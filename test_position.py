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
