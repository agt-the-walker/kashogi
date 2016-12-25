#!/usr/bin/env python3

import re

from collections import defaultdict, Counter
from pieces import Pieces
from utils import ordinal


class Position:
    MIN_SIZE = 3
    NUM_PLAYERS = 2
    STANDARD_HAND_ORDER = 'RBGSNLP'
    UNPROMOTED_PIECE_REGEX = "[a-zA-Z](?:[a-zA-Z](?=@)|')?"

    def __init__(self, sfen):
        self._pieces = Pieces()

        m = re.match("(\S+) ([wb]) (\S+)( [1-9][0-9]*)?$", sfen)
        if not m:
            raise ValueError('Invalid SFEN')

        # the following data structure is indexed by [(file, rank)]
        # by convention, rank=0 and file=0 is bottom-left corner from black's
        #  point of view
        self._board = {}
        self._parse_board(m.group(1))

        # the following data structure is indexed by [player][abbrev]
        self._hands = [Counter() for count in range(self.NUM_PLAYERS)]
        self._parse_hands(m.group(3))

        self._player_to_move = self._player_from_code(m.group(2))
        self._verify_opponent_not_in_check()

        self._half_moves = int(m.group(4)) if m.group(4) else None

    @property
    def num_ranks(self):
        return self._num_ranks

    @property
    def num_files(self):
        return self._num_files

    def status(self):
        checking_piece = self._piece_giving_check_to(self._player_to_move)
        try:
            next(self._legal_moves())
            if checking_piece:
                return 'check'
        except StopIteration:
            return 'checkmate' if checking_piece else 'stalemate'

    def __str__(self):
        sfen = ' '.join([self._sfen_board(),
                        self._sfen_player(),
                        self._sfen_hands()])
        if self._half_moves:
            sfen += ' {}'.format(self._half_moves)
        return sfen

    def _parse_board(self, s):
        ranks = s.split('/')
        self._num_ranks = len(ranks)
        if self._num_ranks < self.MIN_SIZE:
            raise ValueError('Too few ranks: {} < {}'.format(self._num_ranks,
                             self.MIN_SIZE))

        self._all_coordinates = set()
        self._num_files = 0
        self._royal_squares = [None] * self.NUM_PLAYERS

        # the following data structure is indexed by [player][abbrev][file]
        self._num_per_file = [defaultdict(lambda: Counter())
                              for count in range(self.NUM_PLAYERS)]

        for rank, s in enumerate(ranks):
            self._parse_rank(s, rank)

        if self._num_files < self.MIN_SIZE:
            raise ValueError('Too few files: {} < {}'.format(self._num_files,
                             self.MIN_SIZE))

    def _parse_rank(self, s, rank):
        tokens = re.findall('\+?' + self.UNPROMOTED_PIECE_REGEX + '|\d+', s)
        file = 0

        for token in tokens:
            if token.isdigit():
                file += int(token)
            else:
                self._parse_piece(token, rank, file)
                file += 1

        if file > self._num_files:
            self._num_files = file

    def _parse_piece(self, token, rank, file):
        abbrev = token.upper()
        if not self._pieces.exist(abbrev):
            raise ValueError('Invalid piece on board: {}'.format(token))
        player = 0 if abbrev == token else 1

        if self._pieces.is_royal(abbrev):
            if self._royal_squares[player]:
                raise ValueError('Too many royal pieces for {}'
                                 .format(self._player_name(player)))
            self._royal_squares[player] = (file, self._num_ranks - rank - 1)

        max_per_file = self._pieces.max_per_file(abbrev)
        if max_per_file:
            self._num_per_file[player][abbrev][file] += 1
            if self._num_per_file[player][abbrev][file] > max_per_file:
                raise ValueError('Too many {} for {} on file {}'
                                 .format(abbrev, self._player_name(player),
                                         file + 1))

        num_restricted = self._pieces.num_restricted_furthest_ranks(abbrev)
        if num_restricted > 0:
            nth_furthest_rank = {0: rank + 1, 1: self.num_ranks - rank}[player]
            assert nth_furthest_rank > 0

            if num_restricted >= nth_furthest_rank:
                raise ValueError('{} for {} found on {} furthest rank'
                                 .format(abbrev, self._player_name(player),
                                         ordinal(nth_furthest_rank)))

        self._all_coordinates.update(self._pieces.directions(abbrev).keys())
        self._board[(file, self._num_ranks - rank - 1)] = token

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
            if player == 0:
                dx, dy = -dx, -dy

            range = 0
            while True:
                file -= dx
                rank -= dy
                if file < 0 or file >= self._num_files or \
                   rank < 0 or rank >= self._num_ranks:
                    break  # outside the board

                range += 1

                token = self._board.get((file, rank))
                if not token:
                    continue  # empty square

                abbrev = token.upper()
                piece_player = 0 if abbrev == token else 1
                if piece_player == player:
                    break  # found one of his pieces

                piece_directions = self._pieces.directions(abbrev)
                if coordinate not in piece_directions:
                    break  # cannot check him (wrong orientation)

                piece_range = piece_directions[coordinate]
                if piece_range == 0 or piece_range >= range:
                    # my piece has enough range to check him
                    return abbrev

    def _legal_moves(self):
        # XXX: we don't handle drops for now
        for square in list(self._board):
            token = self._board[square]

            abbrev = token.upper()
            piece_player = 0 if abbrev == token else 1
            if piece_player != self._player_to_move:
                continue  # found one of his pieces

            for dest_square in self._pseudo_legal_moves_from_square(square):
                if self._is_legal_move(square, dest_square):
                    yield dest_square

    def _pseudo_legal_moves_from_square(self, square):
        abbrev = self._board[square].upper()
        for coordinate, range in self._pieces.directions(abbrev).items():
            dx, dy = coordinate
            if self._player_to_move == 1:
                dx, dy = -dx, -dy
            dest_file, dest_rank = square

            while True:
                dest_file += dx
                dest_rank += dy
                if dest_file < 0 or dest_file >= self._num_files or \
                   dest_rank < 0 or dest_rank >= self._num_ranks:
                    break  # outside the board

                token = self._board.get((dest_file, dest_rank))
                if token:
                    abbrev = token.upper()
                    piece_player = 0 if abbrev == token else 1
                    if piece_player == self._player_to_move:
                        break  # found one of my pieces
                    else:
                        yield (dest_file, dest_rank)  # found one of his pieces
                        break                         # we cannot go beyond it
                else:
                    yield (dest_file, dest_rank)  # found an empty square
                    if range == 1:
                        break
                    range -= 1

    def _is_legal_move(self, square, dest_square):
        royal_square = self._royal_squares[self._player_to_move]
        if not royal_square:  # player has no royal piece
            return True

        if square == royal_square:
            royal_square = dest_square  # we have moved the royal piece

        # perform the move
        saved_token = self._board.get(dest_square)
        self._board[dest_square] = self._board[square]
        del self._board[square]

        result = True
        if self._piece_giving_check_to(self._player_to_move, royal_square):
            result = False

        # revert the move to restore the board to its initial state
        self._board[square] = self._board[dest_square]
        self._board[dest_square] = saved_token

        return result

    def _parse_hands(self, s):
        for number, token in re.findall('([1-9][0-9]*)?(' +
                                        self.UNPROMOTED_PIECE_REGEX + ')', s):
            abbrev = token.upper()
            if not self._pieces.exist(abbrev):
                raise ValueError('Invalid piece in hand: {}'.format(token))
            if self._pieces.is_royal(abbrev):
                raise ValueError('Royal piece in hand: {}'.format(token))

            player = 0 if abbrev == token else 1
            number = int(number) if number.isdigit() else 1
            self._hands[player][abbrev] += number

    def _player_name(self, player):
        assert player < self.NUM_PLAYERS
        return {0: 'black', 1: 'white'}[player]

    def _sfen_board(self):
        ranks = []
        for rank in reversed(range(self._num_ranks)):
            buffer = ''
            skipped = 0
            for file in range(self._num_files):
                token = self._board.get((file, rank))
                if token:
                    if skipped > 0:
                        buffer += str(skipped)
                        skipped = 0
                    buffer += self._sfen_piece(token)
                else:
                    skipped += 1
            if skipped > 0:
                buffer += str(skipped)
            ranks.append(buffer)

        return '/'.join(ranks)

    def _sfen_player(self):
        return self._player_name(self._player_to_move)[0]

    def _sfen_hands(self):
        buffer = ''

        for player in range(self.NUM_PLAYERS):
            # output standard shogi pieces in traditional order
            for abbrev in self.STANDARD_HAND_ORDER:
                buffer += self._sfen_piece_in_hand(player, abbrev)

            # ...then output remaining pieces in alphabetical order
            for abbrev in sorted(self._hands[player].keys() -
                                 self.STANDARD_HAND_ORDER):
                buffer += self._sfen_piece_in_hand(player, abbrev)

        return buffer if buffer else '-'

    def _sfen_piece_in_hand(self, player, abbrev):
        number = self._hands[player][abbrev]

        if number > 1:
            buffer = str(number)
        else:
            buffer = ''
        if number > 0:
            piece = self._sfen_piece(abbrev)
            if player == 1:
                piece = piece.lower()
            buffer += piece

        return buffer

    @staticmethod
    def _player_from_code(code):
        return {'b': 0, 'w': 1}[code]

    @staticmethod
    def _sfen_piece(token):
        if re.search('[a-zA-Z]{2}', token):
            return token + '@'
        else:
            return token
