#!/usr/bin/env python3

from collections import defaultdict
from position import Position


class Game:
    def __init__(self, sfen, pieces, try_rule):
        self._position = Position(sfen, pieces)

        if try_rule:
            self._try_squares = [
                self.royal_square(player)
                for player in reversed(range(self.NUM_PLAYERS))]

        self._update_history()

    def __getattr__(self, name):
        return getattr(self._position, name)

    @property
    def half_moves(self):
        return self._half_moves

    @property
    def sfen(self):
        return self._sfen

    def result(self):
        return self._winner, self._result_reason

    def _update_result(self):
        opponent = self.NUM_PLAYERS - self.player_to_move - 1

        if hasattr(self, '_try_squares'):
            try_square = self._try_squares[opponent]
        else:
            try_square = None

        if self._status.endswith('mate'):
            self._winner, self._result_reason = opponent, self._status
        elif try_square and self.royal_square(opponent) == try_square:
            self._winner, self._result_reason = opponent, 'try rule'
        else:
            self._winner, self._result_reason = \
                    self._fourfold_repetition_result()

    def move(self, square, dest_square, promotes=False):
        if self._winner is not None:
            raise ValueError('Illegal move: game already decided')

        self._position.move(square, dest_square, promotes)
        if promotes is not None:
            self._update_history()

    def legal_moves_from_square(self, square, player=None):
        if self._winner is not None:
            return
        yield from self._position.legal_moves_from_square(square, player)

    def choose_promotion(self, promotes):
        self._position.choose_promotion(promotes)
        self._update_history()

    def drop(self, abbrev, dest_square):
        if self._winner is not None:
            raise ValueError('Illegal drop: game already decided')

        self._position.drop(abbrev, dest_square)
        self._update_history()

    def legal_drops_with_piece(self, abbrev):
        if self._winner is not None:
            return
        yield from self._position.legal_drops_with_piece(abbrev)

    def _update_history(self):
        self._status = self.status()

        if not hasattr(self, '_half_moves'):
            self._half_moves = 0
            self._sfens = defaultdict(list)
            self._in_check = []
        else:
            self._half_moves += 1

        self._sfen = str(self._position)
        self._sfens[self._sfen].append(self._half_moves)
        self._in_check.append(self._status.startswith('check'))

        self._update_result()

    def _fourfold_repetition_result(self):
        if len(self._sfens[self._sfen]) < 4:
            return None, 'in progress'  # no four-fold repetition

        # receiving perpetual check
        if self._is_perpetual_check(0):
            return self.player_to_move, 'perpetual check'

        # giving perpetual_check
        if self._is_perpetual_check(1):
            opponent = self.NUM_PLAYERS - self.player_to_move - 1
            return opponent, 'perpetual check'

        return self.NUM_PLAYERS, 'fourfold repetition'  # draw

    def _is_perpetual_check(self, offset):
        assert self._sfens[self._sfen][3] == self._half_moves

        return all(self._in_check[half_moves] for half_moves in
                   range(self._sfens[self._sfen][2] - offset
                                                    + self.NUM_PLAYERS,  # noqa
                         self._sfens[self._sfen][3] - offset
                                                    + self.NUM_PLAYERS,  # noqa
                         self.NUM_PLAYERS))
