#!/usr/bin/env python3

import unittest

from game import Game
from pieces import Pieces


class PositionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._pieces = Pieces()

    def test_game_win_by_try_rule(self):
        for try_rule in [False, True]:
            game = Game('1k1/3/1K1 w P', self._pieces, try_rule)
            game.move((2, 1), (1, 1))
            game.move((2, 3), (3, 3))
            game.move((1, 1), (1, 2))
            game.move((3, 3), (3, 2))
            game.move((1, 2), (1, 3))
            game.move((3, 2), (3, 1))
            game.move((1, 3), (2, 3))

            if try_rule:
                self.assertEqual(game.result(), (1, 'try rule'))

                self.assertEqual(set(game.legal_moves_from_square((3, 1))),
                                 set())
                with self.assertRaisesRegex(
                        ValueError, 'Illegal move: game already decided'):
                    game.move((3, 1), (2, 1))

                self.assertEqual(set(game.legal_drops_with_piece('P')), set())
                with self.assertRaisesRegex(
                        ValueError, 'Illegal drop: game already decided'):
                    game.drop('P', (2, 2))
            else:
                self.assertIsNone(game.result()[0])

                self.assertEqual(set(game.legal_moves_from_square((3, 1))),
                                 {(2, 1)})
                self.assertEqual(set(game.legal_drops_with_piece('P')),
                                 {(3, 2), (2, 2), (1, 2),
                                  (3, 3),         (1, 3)})

    def test_game_try_rule_no_kings(self):
        game = Game('1g/3/1G w -', self._pieces, True)
        self.assertIsNone(game.result()[0])

    def test_game_win_by_stalemate(self):
        game = Game('1k1/3/1K1 b BD@', self._pieces, True)
        game.drop('BD', (2, 2))
        self.assertEqual(game.half_moves, 1)
        self.assertEqual(game.result(), (0, 'stalemate'))

    def test_game_draw_by_fourfold(self):
        game = Game('2k/3/K2 b -', self._pieces, True)
        game.move((3, 3), (3, 2))
        game.move((1, 1), (1, 2))
        for _ in range(3):
            self.assertIsNone(game.result()[0])
            game.move((3, 2), (3, 1))
            self.assertIsNone(game.result()[0])
            game.move((1, 2), (1, 3))
            self.assertIsNone(game.result()[0])
            game.move((3, 1), (3, 2))
            self.assertIsNone(game.result()[0])
            game.move((1, 3), (1, 2))
        self.assertEqual(game.half_moves, 14)
        self.assertEqual(game.result(), (game.NUM_PLAYERS,
                                         'fourfold repetition'))

    def test_game_win_due_to_perpetual_check(self):
        game = Game('1k1/2r/K2 w -', self._pieces, True)
        game.move((1, 2), (3, 2))
        for _ in range(3):
            self.assertIsNone(game.result()[0])
            game.move((3, 3), (2, 3))
            self.assertIsNone(game.result()[0])
            game.move((3, 2), (2, 2))
            self.assertIsNone(game.result()[0])
            game.move((2, 3), (3, 3))
            self.assertIsNone(game.result()[0])
            game.move((2, 2), (3, 2))
        self.assertEqual(game.result(), (0, 'perpetual check'))

    def test_game_loss_due_to_perpetual_check(self):
        game = Game('2k/1R1/1K1 b -', self._pieces, True)
        for _ in range(3):
            self.assertIsNone(game.result()[0])
            game.move((2, 2), (1, 2))
            self.assertIsNone(game.result()[0])
            game.move((1, 1), (2, 1))
            self.assertIsNone(game.result()[0])
            game.move((1, 2), (2, 2))
            self.assertIsNone(game.result()[0])
            game.move((2, 1), (1, 1))
        self.assertEqual(game.result(), (1, 'perpetual check'))

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
        self.assertEqual(game.result(), (1, 'perpetual check'))

    def test_game_with_deferred_promotions(self):
        game = Game('2k/SPs/K2 b -', self._pieces, False)
        game.move((3, 2), (3, 1), None)  # can promote
        self.assertEqual(game.half_moves, 0)  # incomplete move
        game.choose_promotion(True)      # yes please
        self.assertEqual(game.half_moves, 1)  # move completed
        self.assertEqual(game.sfen, '+S1k/1Ps/K2 w -')


if __name__ == '__main__':
    unittest.main()
