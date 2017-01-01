#!/usr/bin/env python3

import unittest

from game import Game
from pieces import Pieces


class PositionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._pieces = Pieces()

    def test_game_already_won_by_normal_means(self):
        for try_rule in [False, True]:
            with self.assertRaisesRegex(ValueError,
                                        'Game is already won by 0'):
                Game('1k1/1G1/1K1 w -', self._pieces, try_rule)

    def test_game_win_by_try_rule(self):
        for try_rule in [False, True]:
            game = Game('1k1/3/1K1 w -', self._pieces, try_rule)
            game.move((2, 1), (1, 1))
            game.move((2, 3), (3, 3))
            game.move((1, 1), (1, 2))
            game.move((3, 3), (3, 2))
            game.move((1, 2), (1, 3))
            game.move((3, 2), (3, 1))
            game.move((1, 3), (2, 3))

            if try_rule:
                self.assertEqual(game.winner(), 1)
            else:
                self.assertIsNone(game.winner())

    def test_game_win_by_stalemate(self):
        game = Game('1k1/3/1K1 b BD@', self._pieces, True)
        game.drop('BD', (2, 2))
        self.assertEqual(game.status(), 'stalemate')
        self.assertEqual(game.winner(), 0)
