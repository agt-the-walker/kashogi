#!/usr/bin/env python3

import unittest

from position import Position

class PositionTestCase(unittest.TestCase):
    def test_standard_shogi(self):
        # thanks http://shogi.typepad.jp/brainstorm/2007/01/post_11a0.html
        Position('8l/1l+R2P3/p2pBG1pp/kps1p4/Nn1P2G2/P1P1P2PP/1PS6/1KSG3+r1/LN2+p3L w Sbgn3p 124')

    def test_missing_plies_on_minishogi(self):
        Position('rbsgk/4p/5/P4/KGSBR b -')

    def test_wrong_plies(self):
        with self.assertRaisesRegex(ValueError, 'Invalid SFEN'):
            Position('rbsgk/4p/5/P4/KGSBR w - 0')

    def test_tiny_board(self):
        with self.assertRaisesRegex(ValueError, 'Too few ranks: 2 <'):
            Position('k2/2K b -')

if __name__ == '__main__':
    unittest.main()
