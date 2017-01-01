#!/usr/bin/env python3

from position import Position


class Game:
    def __init__(self, sfen, pieces, try_rule):
        self._position = Position(sfen, pieces)

        position = self._position
        if try_rule:
            self._try_squares = [
                position.royal_square(player)
                for player in reversed(range(position.NUM_PLAYERS))]

        winner = self.winner()
        if winner is not None:
            raise ValueError('Game is already won by {}'.format(winner))

    def __getattr__(self, name):
        return getattr(self._position, name)

    def winner(self):
        pos = self._position
        opponent = pos.NUM_PLAYERS - pos.player_to_move - 1

        if pos.status().endswith('mate'):
            return opponent
        elif (hasattr(self, '_try_squares') and
              pos.royal_square(opponent) == self._try_squares[opponent]):
            return opponent
