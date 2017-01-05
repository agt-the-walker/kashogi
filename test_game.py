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
                self.assertEqual(game.result(), 1)
            else:
                self.assertIsNone(game.result())

    def test_game_win_by_stalemate(self):
        game = Game('1k1/3/1K1 b BD@', self._pieces, True)
        game.drop('BD', (2, 2))
        self.assertEqual(game.status(), 'stalemate')
        self.assertEqual(game.result(), 0)

    def test_game_draw_by_fourfold(self):
        game = Game('2k/3/K2 b -', self._pieces, True)
        game.move((3, 3), (3, 2))
        game.move((1, 1), (1, 2))
        for _ in range(3):
            self.assertIsNone(game.result())
            game.move((3, 2), (3, 1))
            self.assertIsNone(game.result())
            game.move((1, 2), (1, 3))
            self.assertIsNone(game.result())
            game.move((3, 1), (3, 2))
            self.assertIsNone(game.result())
            game.move((1, 3), (1, 2))
        self.assertEqual(game.result(), game.NUM_PLAYERS)

    def test_game_win_due_to_perpetual_check(self):
        game = Game('1k1/2r/K2 w -', self._pieces, True)
        game.move((1, 2), (3, 2))
        for _ in range(3):
            self.assertIsNone(game.result())
            game.move((3, 3), (2, 3))
            self.assertIsNone(game.result())
            game.move((3, 2), (2, 2))
            self.assertIsNone(game.result())
            game.move((2, 3), (3, 3))
            self.assertIsNone(game.result())
            game.move((2, 2), (3, 2))
        self.assertEqual(game.result(), 0)

    def test_game_loss_due_to_perpetual_check(self):
        game = Game('2k/1R1/1K1 b -', self._pieces, True)
        for _ in range(3):
            self.assertIsNone(game.result())
            game.move((2, 2), (1, 2))
            self.assertIsNone(game.result())
            game.move((1, 1), (2, 1))
            self.assertIsNone(game.result())
            game.move((1, 2), (2, 2))
            self.assertIsNone(game.result())
            game.move((2, 1), (1, 1))
        self.assertEqual(game.result(), 1)

    def test_game_loss_due_to_perpetual_check_during_last_repetition(self):
        game = Game('2k1/1R2/2K1 b -', self._pieces, True)
        for _ in range(2):
            game.move((3, 2), (4, 2))
            game.move((2, 1), (1, 1))
            game.move((4, 2), (3, 2))
            game.move((1, 1), (2, 1))
        # no checks so far, let's give perpetual check now
        game.move((3, 2), (2, 2))
        game.move((2, 1), (3, 1))
        game.move((2, 2), (3, 2))
        game.move((3, 1), (2, 1))
        self.assertEqual(game.result(), 1)


if __name__ == '__main__':
    unittest.main()
