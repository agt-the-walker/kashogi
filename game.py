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

        result = self.result()
        if result is not None:
            raise ValueError('Game is already won by {}'.format(result))

    def __getattr__(self, name):
        return getattr(self._position, name)

    def result(self):
        opponent = self.NUM_PLAYERS - self.player_to_move - 1

        if self._status.endswith('mate'):
            return opponent
        elif (hasattr(self, '_try_squares') and
              self.royal_square(opponent) == self._try_squares[opponent]):
            return opponent
        return self._fourfold_repetition_result()

    def move(self, square, dest_square, promotes=False):
        self._position.move(square, dest_square, promotes)
        self._update_history()

    def drop(self, abbrev, dest_square):
        self._position.drop(abbrev, dest_square)
        self._update_history()

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

    def _fourfold_repetition_result(self):
        if len(self._sfens[self._sfen]) < 4:
            return  # no four-fold repetition

        # receiving perpetual check
        if self._is_perpetual_check(0):
            return self.player_to_move

        # giving perpetual_check
        if self._is_perpetual_check(1):
            opponent = self.NUM_PLAYERS - self.player_to_move - 1
            return opponent

        return self.NUM_PLAYERS  # draw

    def _is_perpetual_check(self, offset):
        assert self._sfens[self._sfen][3] == self._half_moves

        return all(self._in_check[half_moves] for half_moves in
                   range(self._sfens[self._sfen][2] - offset
                                                    + self.NUM_PLAYERS,  # noqa
                         self._sfens[self._sfen][3] - offset
                                                    + self.NUM_PLAYERS,  # noqa
                         self.NUM_PLAYERS))
