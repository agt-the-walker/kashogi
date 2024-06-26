#!/usr/bin/env python3

import re

from collections import defaultdict, Counter


class Position:
    MIN_SIZE = 3
    NUM_PLAYERS = 2
    STANDARD_HAND_ORDER = 'RBGSNLP'
    UNPROMOTED_PIECE_REGEX = "[a-zA-Z](?:[a-zA-Z](?=@)|')?"

    def __init__(self, sfen, pieces):
        self._pieces = pieces

        m = re.match(r"(\S+) ([wb]) (\S+)", sfen)
        if not m:
            raise ValueError('Invalid SFEN')

        # the following data structure is indexed by [(file, rank)]
        # rank=1 and file=1 is top-right corner from black's point of view, for
        #  consistency with Japanese notation
        self._board = {}
        self._parse_board(m.group(1))

        self._player_to_move = self._player_from_code(m.group(2))
        self._verify_opponent_not_in_check()

        # the following data structure is indexed by [player][abbrev]
        self._hands = [Counter() for count in range(self.NUM_PLAYERS)]
        self._parse_hands(m.group(3))

        self._update_droppable_pieces()

        self._checking_piece = \
            self._piece_giving_check_to(self._player_to_move)

    @property
    def pieces(self):
        return self._pieces

    @property
    def num_ranks(self):
        return self._num_ranks

    @property
    def num_files(self):
        return self._num_files

    @property
    def droppable_pieces(self):
        return self._droppable_pieces

    @property
    def player_to_move(self):
        return self._player_to_move

    def get(self, square):
        return self._board.get(square)

    def in_hand(self, player):
        return self._hands[player]  # please don't modify me!

    def royal_square(self, player):
        return self._royal_squares[player]

    def __str__(self):
        return ' '.join([self._sfen_board(),
                        self._sfen_player(),
                        self._sfen_hands()])

    def _parse_board(self, sfen_board):
        ranks = sfen_board.split('/')
        self._num_ranks = len(ranks)
        if self._num_ranks < self.MIN_SIZE:
            raise ValueError('Too few ranks: {} < {}'.format(self._num_ranks,
                             self.MIN_SIZE))

        self._all_coordinates = set()
        self._droppable_pieces = set()  # later transformed to a list

        self._num_files = 0
        self._royal_squares = [None] * self.NUM_PLAYERS

        # the following data structure is indexed by [player][abbrev][file]
        self._num_per_file = [defaultdict(lambda: Counter())
                              for count in range(self.NUM_PLAYERS)]

        for rank, sfen_rank in enumerate(ranks, 1):
            self._parse_rank(sfen_rank, rank, False)

        if self._num_files < self.MIN_SIZE:
            raise ValueError('Too few files: {} < {}'.format(self._num_files,
                             self.MIN_SIZE))

        for rank, sfen_rank in enumerate(ranks, 1):
            self._parse_rank(sfen_rank, rank, True)

    def _parse_rank(self, sfen_rank, rank, num_files_known):
        tokens = re.findall(r'\+?' + self.UNPROMOTED_PIECE_REGEX + r'|\d+',
                            sfen_rank)
        file = 0

        for token in tokens:
            if token.isdigit():
                file += int(token)
            else:
                if num_files_known:
                    self._parse_piece(token, rank, self._num_files - file)
                file += 1

        if not (num_files_known) and file > self._num_files:
            self._num_files = file

    def _parse_piece(self, piece, rank, file):
        abbrev = piece.upper()
        if not self._pieces.exist(abbrev):
            raise ValueError('Invalid piece on board: {}'.format(piece))
        player = 0 if abbrev == piece else 1

        if self._pieces.is_royal(abbrev):
            if self._royal_squares[player]:
                raise ValueError('Too many royal pieces for {}'
                                 .format(self.player_name(player)))
            self._royal_squares[player] = file, rank

        max_per_file = self._pieces.max_per_file(abbrev)
        if max_per_file:
            self._num_per_file[player][abbrev][file] += 1
            if self._num_per_file[player][abbrev][file] > max_per_file:
                raise ValueError('Too many {} for {} on file {}'
                                 .format(abbrev, self.player_name(player),
                                         file))

        if not self._is_piece_allowed_on_rank(abbrev, player, rank):
            raise ValueError('{} for {} found on furthest rank(s)'
                             .format(abbrev, self.player_name(player)))
        elif (self._pieces.num_restricted_furthest_ranks(abbrev) >
              self._promotion_zone_height()):
            raise ValueError('Promotion zone too small for {}'.format(abbrev))

        self._remember_piece(abbrev)
        self._board[(file, rank)] = piece

    def _parse_hands(self, sfen_hands):
        for number, piece in re.findall('([1-9][0-9]*)?(' +
                                        self.UNPROMOTED_PIECE_REGEX + ')',
                                        sfen_hands):
            abbrev = piece.upper()
            if not self._pieces.exist(abbrev):
                raise ValueError('Invalid piece in hand: {}'.format(piece))
            if self._pieces.is_royal(abbrev):
                raise ValueError('Royal piece in hand: {}'.format(piece))

            self._remember_piece(abbrev)

            player = 0 if abbrev == piece else 1
            number = int(number) if number.isdigit() else 1
            self._hands[player][abbrev] += number

    def _remember_piece(self, abbrev):
        self._all_coordinates.update(self._pieces.directions(abbrev).keys())
        if not self._pieces.is_royal(abbrev):
            if self._pieces.is_promoted(abbrev):
                abbrev = self._pieces.unpromoted(abbrev)
            self._droppable_pieces.add(abbrev)

    def _update_droppable_pieces(self):
        result = []

        # return non-standard shogi pieces in alphabetical order
        for abbrev in sorted(self._droppable_pieces -
                             set(self.STANDARD_HAND_ORDER)):
            result.append(abbrev)

        # ...then return standard shogi pieces in traditional order
        for abbrev in self.STANDARD_HAND_ORDER:
            if abbrev in self._droppable_pieces:
                result.append(abbrev)

        self._droppable_pieces = result

    def _verify_opponent_not_in_check(self):
        opponent = self.NUM_PLAYERS - self._player_to_move - 1
        piece = self._piece_giving_check_to(opponent)
        if piece:
            raise ValueError('Opponent already in check by {}'.format(piece))

    def _piece_giving_check_to(self, player, royal_square=None):
        if not royal_square:  # argument not provided
            royal_square = self._royal_squares[player]
        if not royal_square:  # player has no royal piece
            return

        for coordinate in self._all_coordinates:
            file, rank = royal_square
            dx, dy = coordinate
            if player == 1:
                dx, dy = -dx, -dy

            range = 0
            while True:
                file -= dx
                rank -= dy
                if file < 1 or file > self._num_files or \
                   rank < 1 or rank > self._num_ranks:
                    break  # outside the board

                range += 1

                piece = self._board.get((file, rank))
                if not piece:
                    continue  # empty square

                abbrev = piece.upper()
                piece_player = 0 if abbrev == piece else 1
                if piece_player == player:
                    break  # found one of his pieces

                piece_directions = self._pieces.directions(abbrev)
                if coordinate not in piece_directions:
                    break  # cannot check him (wrong orientation)

                piece_range = piece_directions[coordinate]
                if piece_range == 0 or piece_range >= range:
                    # my piece has enough range to check him
                    return abbrev
                else:
                    break

    def status(self):
        try:
            next(self._legal_moves_and_drops())
            if self._checking_piece:
                return 'check'
        except StopIteration:
            return 'checkmate' if self._checking_piece else 'stalemate'
        return ''

    def _legal_moves_and_drops(self):
        yield from self._legal_moves(self._player_to_move)

        for abbrev in self._hands[self._player_to_move]:
            yield from self.legal_drops_with_piece(abbrev)

    def _legal_moves(self, player):
        for square in list(self._board):
            piece = self._board[square]

            abbrev = piece.upper()
            piece_player = 0 if abbrev == piece else 1
            if piece_player != player:
                continue  # found one of his pieces

            yield from self.legal_moves_from_square(square, player)

    def move(self, square, dest_square, promotes=False):
        if dest_square not in self.legal_moves_from_square(square):
            raise ValueError('Illegal move')

        possible_promotions = self.promotions(square, dest_square)
        if promotes is None:
            if len(possible_promotions) < 2:
                raise ValueError('Undefined promotion')
        elif promotes not in self.promotions(square, dest_square):
            raise ValueError('Illegal promotion')

        player = self._player_to_move

        # perform the move
        piece = self._board.pop(square)
        captured_piece = self._board.get(dest_square)
        self._board[dest_square] = piece
        if promotes:
            self._promotes(square, dest_square)

        # captured piece goes in hand
        if captured_piece:
            captured_abbrev = captured_piece.upper()

            captured_max_per_file = self._pieces.max_per_file(captured_abbrev)
            if captured_max_per_file:
                file, _ = dest_square
                opponent = self.NUM_PLAYERS - player - 1
                self._num_per_file[opponent][captured_abbrev][file] -= 1

            if self._pieces.is_promoted(captured_abbrev):
                captured_abbrev = self._pieces.unpromoted(captured_abbrev)
            self._hands[player][captured_abbrev] += 1

        # update statistics
        if self._royal_squares[player] == square:
            self._royal_squares[player] = dest_square

        # end turn unless promotion is deferred
        if promotes is None:
            self._movement = [square, dest_square]
        else:
            self._end_turn()

    def legal_moves_from_square(self, square, player=None):
        if player is None:
            player = self._player_to_move

        piece = self._board.get(square)
        if piece:
            abbrev = piece.upper()
            piece_player = 0 if abbrev == piece else 1
            if piece_player != player:
                raise ValueError('Square {} is not ours'.format(square))
        else:
            raise ValueError('Square {} is empty'.format(square))

        for dest_square in \
                self._pseudo_legal_moves_from_square(square, player):
            if self._is_legal_move(square, dest_square, player):
                yield dest_square

    def _pseudo_legal_moves_from_square(self, square, player):
        abbrev = self._board[square].upper()
        for coordinate, range in self._pieces.directions(abbrev).items():
            dx, dy = coordinate
            if player == 0:
                dx, dy = -dx, -dy
            dest_file, dest_rank = square

            while True:
                dest_file += dx
                dest_rank += dy
                if dest_file < 1 or dest_file > self._num_files or \
                   dest_rank < 1 or dest_rank > self._num_ranks:
                    break  # outside the board

                piece = self._board.get((dest_file, dest_rank))
                if piece:
                    abbrev = piece.upper()
                    piece_player = 0 if abbrev == piece else 1
                    if piece_player == player:
                        break  # found one of my pieces
                    else:
                        yield (dest_file, dest_rank)  # found one of his pieces
                        break                         # we cannot go beyond it
                else:
                    yield (dest_file, dest_rank)  # found an empty square
                    if range == 1:
                        break
                    range -= 1

    def _is_legal_move(self, square, dest_square, player):
        royal_square = self._royal_squares[player]
        if not royal_square:  # player has no royal piece
            return True

        if square == royal_square:
            royal_square = dest_square  # we have moved the royal piece

        # perform the move
        captured_piece = self._board.get(dest_square)
        self._board[dest_square] = self._board.pop(square)

        result = True
        if self._piece_giving_check_to(player, royal_square):
            result = False

        # revert the move to restore the board to its initial state
        self._board[square] = self._board.pop(dest_square)
        if captured_piece:
            self._board[dest_square] = captured_piece

        assert (None not in self._board.values())

        return result

    def promotions(self, square, dest_square):
        # No (pseudo) legal check is performed, we consider that the client
        #  calls this on squares returned by legal_moves_from_square()
        piece = self._board[square]
        abbrev = piece.upper()

        if self._pieces.is_promoted(abbrev):
            return [False]
        elif not self._pieces.can_promote(abbrev):
            return [False]

        _, dest_rank = dest_square
        if not self._is_piece_allowed_on_rank(abbrev, self._player_to_move,
                                              dest_rank):
            return [True]  # i.e. mandatory
        elif (self._in_promotion_zone(square) or
              self._in_promotion_zone(dest_square)):
            if self._should_promote(abbrev, dest_rank):
                return [True, False]
            else:
                return [False, True]
        else:
            return [False]

    def _should_promote(self, abbrev, dest_rank):
        if not self._pieces.can_retreat(abbrev):
            directions = self._effective_directions(abbrev, dest_rank)
        else:
            directions = self._pieces.directions(abbrev)

        new_directions = self._pieces.directions(self._pieces.promoted(abbrev))
        if not set(directions).issubset(new_directions):
            return False

        for coordinate, range in directions.items():
            new_range = new_directions[coordinate]
            if new_range != 0 and (range == 0 or new_range < range):
                return False

        return True

    def _effective_directions(self, abbrev, rank):
        result = {}

        nth_furthest_rank = self._nth_furthest_rank(self._player_to_move, rank)
        for coordinate, range in self._pieces.directions(abbrev).items():
            dx, dy = coordinate
            if dy > 0:
                max_new_range = (nth_furthest_rank - 1) // dy
                if max_new_range == 0:
                    continue  # cannot move to this direction anymore

                if range == 0:
                    effective_range = max_new_range
                else:
                    effective_range = min(max_new_range, range)
            else:
                effective_range = range
            result[coordinate] = effective_range

        return result

    def choose_promotion(self, promotes):
        if promotes:
            self._promotes(*self._movement)
        del self._movement

        self._end_turn()

    def _promotes(self, square, dest_square):
        player = self._player_to_move

        piece = self._board.pop(dest_square)
        self._board[dest_square] = self._pieces.promoted(piece)

        # update statistics
        abbrev = piece.upper()
        max_per_file = self._pieces.max_per_file(abbrev)
        if max_per_file:
            file, _ = square
            self._num_per_file[player][abbrev][file] -= 1

    def drop(self, abbrev, dest_square):
        if dest_square not in self.legal_drops_with_piece(abbrev):
            raise ValueError('Illegal drop')

        player = self._player_to_move

        # perform the drop
        self._board[dest_square] = abbrev if player == 0 else abbrev.lower()
        self._hands[player][abbrev] -= 1
        if self._hands[player][abbrev] == 0:
            del self._hands[player][abbrev]

        # update statistics
        max_per_file = self._pieces.max_per_file(abbrev)
        if max_per_file:
            file, _ = dest_square
            self._num_per_file[player][abbrev][file] += 1

        self._end_turn()

    def legal_drops_with_piece(self, abbrev):
        if not self._hands[self._player_to_move].get(abbrev):
            raise ValueError('Piece {} is not in hand'.format(abbrev))

        for rank in range(1, self._num_ranks+1):
            for file in range(1, self._num_files+1):
                square = file, rank
                if self._board.get(square):
                    continue  # not empty

                if self._is_pseudo_legal_drop(abbrev, square) and \
                   self._is_legal_drop(abbrev, square):
                    yield square

    def _is_pseudo_legal_drop(self, abbrev, square):
        file, rank = square
        player = self._player_to_move

        max_per_file = self._pieces.max_per_file(abbrev)
        if max_per_file and \
           max_per_file == self._num_per_file[player][abbrev][file]:
            return False  # Nifu and related restrictions

        if not self._is_piece_allowed_on_rank(abbrev, player, rank):
            return False  # rank restriction

        return True

    def _is_legal_drop(self, abbrev, dest_square):
        player = self._player_to_move

        # perform the drop
        self._board[dest_square] = abbrev if player == 0 else abbrev.lower()

        result = True
        if self._piece_giving_check_to(player):
            result = False  # currently in check and drop didn't block it
        elif (self._pieces.no_drop_mate(abbrev) and
              self._is_opponent_checkmated()):
            result = False  # cannot checkmate opponent with drop

        # revert the drop to restore the board to its initial state
        del self._board[dest_square]

        assert (None not in self._board.values())

        return result

    def _is_opponent_checkmated(self):
        opponent = self.NUM_PLAYERS - self._player_to_move - 1
        if not self._piece_giving_check_to(opponent):
            return False

        try:
            next(self._legal_moves(opponent))
            return False
        except StopIteration:
            return True

    def _end_turn(self):
        self._player_to_move = self.NUM_PLAYERS - self._player_to_move - 1

        self._checking_piece = \
            self._piece_giving_check_to(self._player_to_move)

    def _is_piece_allowed_on_rank(self, abbrev, player, rank):
        num_restricted = self._pieces.num_restricted_furthest_ranks(abbrev)
        if not num_restricted:
            return True

        return num_restricted < self._nth_furthest_rank(player, rank)

    def _in_promotion_zone(self, square):
        _, rank = square
        return (self._promotion_zone_height() >=
                self._nth_furthest_rank(self._player_to_move, rank))

    def _nth_furthest_rank(self, player, rank):
        result = {0: rank, 1: self._num_ranks+1 - rank}[player]
        assert result > 0
        return result

    def _promotion_zone_height(self):
        return self._num_ranks // 3  # ok for Tori, standard, Okisaki, Wa shogi

    @staticmethod
    def player_name(player):
        assert player < Position.NUM_PLAYERS
        return {0: 'black', 1: 'white'}[player]

    def _sfen_board(self):
        ranks = []
        for rank in range(1, self._num_ranks+1):
            buffer = ''
            skipped = 0
            for file in reversed(range(1, self._num_files+1)):
                piece = self._board.get((file, rank))
                if piece:
                    if skipped > 0:
                        buffer += str(skipped)
                        skipped = 0
                    buffer += self._sfen_piece(piece)
                else:
                    skipped += 1
            if skipped > 0:
                buffer += str(skipped)
            ranks.append(buffer)

        return '/'.join(ranks)

    def _sfen_player(self):
        return self.player_name(self._player_to_move)[0]

    def _sfen_hands(self):
        buffer = ''

        for player in range(self.NUM_PLAYERS):
            for abbrev in self.droppable_pieces:
                if abbrev in self._hands[player]:
                    buffer += self._sfen_piece_in_hand(player, abbrev)

        return buffer if buffer else '-'

    def _sfen_piece_in_hand(self, player, abbrev):
        number = self._hands[player][abbrev]

        if number > 1:
            buffer = str(number)
        else:
            buffer = ''

        piece = self._sfen_piece(abbrev)
        if player == 1:
            piece = piece.lower()
        buffer += piece

        return buffer

    @staticmethod
    def _player_from_code(code):
        return {'b': 0, 'w': 1}[code]

    @staticmethod
    def _sfen_piece(piece):
        if re.search('[a-zA-Z]{2}', piece):
            return piece + '@'
        else:
            return piece
