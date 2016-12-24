#!/usr/bin/env python3

import unittest

from position import Position

class PositionTestCase(unittest.TestCase):
    def test_standard_shogi(self):
        # thanks http://shogi.typepad.jp/brainstorm/2007/01/post_11a0.html
        self.check('8l/1l+R2P3/p2pBG1pp/kps1p4/Nn1P2G2/P1P1P2PP/1PS6/1KSG3+r1/LN2+p3L w Sbgn3p 124', 9, 9)

    def test_tiny_board(self):
        with self.assertRaisesRegex(ValueError, 'Too few ranks: 2 <'):
            Position('k2/2K b -')
        with self.assertRaisesRegex(ValueError, 'Too few files: 2 <'):
            Position('k1/2/1K b -')

    def test_invalid_piece(self):
        with self.assertRaisesRegex(ValueError, 'Invalid piece in SFEN: Z'):
            Position('k1Z/3/2K b -')

    def test_too_many_royals(self):
        with self.assertRaisesRegex(ValueError,
                'Too many royal pieces for white'):
            Position('k1k/3/2K b -')
        with self.assertRaisesRegex(ValueError,
                'Too many royal pieces for black'):
            Position('r2/3/K1K b -')

    def test_too_many_pawns_or_swallows_on_file(self):
        with self.assertRaisesRegex(ValueError,
                'Too many P for white on file 3'):
            Position('3/2p/2p/P1P b -')
        with self.assertRaisesRegex(ValueError,
                "Too many S' for black on file 2"):
            Position("s'2/s'S'1/1S'1/1S'1 b -")
        # pawns and swallows don't share constraints though
        self.check("2p/2s'/2s'/K2 b -", 4, 3)

    def test_no_legal_moves_on_subsequent_turns(self):
        with self.assertRaisesRegex(ValueError,
                'L for black found on 1st furthest rank'):
            Position('k1L/3/1K1 b -')
        with self.assertRaisesRegex(ValueError,
                'N for white found on 1st furthest rank'):
            Position('k2/3/3/1Kn b -')
        with self.assertRaisesRegex(ValueError,
                'N for black found on 2nd furthest rank'):
            Position('k2/1N1/3/1K1 b -')

    def test_missing_plies_on_minishogi(self):
        self.check('rbsgk/4p/5/P4/KGSBR b -', 5, 5)

    def test_wrong_plies(self):
        with self.assertRaisesRegex(ValueError, 'Invalid SFEN'):
            Position('rbsgk/4p/5/P4/KGSBR w - 0')

    def test_tori_wa_pieces_on_narrow_board(self):
        self.check("k/p'p'sc@/p'1P'/P'P'SC@/K b -", 5, 3)

    def check(self, sfen, expected_num_ranks, expected_num_files):
        position = Position(sfen)
        self.assertEqual(position.num_ranks, expected_num_ranks)
        self.assertEqual(position.num_files, expected_num_files)


if __name__ == '__main__':
    unittest.main()
