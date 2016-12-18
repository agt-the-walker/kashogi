#!/usr/bin/env python3

import unittest

from betza import Betza

class BetzaTestCase(unittest.TestCase):
    def test_invalid_notation(self):
        with self.assertRaisesRegex(ValueError, 'No token found'):
            Betza('')
        with self.assertRaisesRegex(ValueError, 'No token found'):
            Betza('#!')

    def test_invalid_piece(self):
        with self.assertRaisesRegex(ValueError, 'Unknown piece: C'):
            Betza('C')


    def test_notation_order_on_dragon(self):
        expected = {(-1, 1): 1, (0, 1): 0, (1, 1): 1,
                    (-1, 0): 0,            (1, 0): 0,
                    (-1,-1): 1, (0,-1): 0, (1,-1): 1}
        for notation in ['FR', 'RF', 'KR', 'RK']:
            self.assertEqual(Betza(notation).directions, expected)

    def test_double_digit_range_on_queen(self):
        self.assertEqual(Betza('Q12').directions,
                {(-1, 1): 12, (0, 1): 12, (1, 1): 12,
                 (-1, 0): 12,             (1, 0): 12,
                 (-1,-1): 12, (0,-1): 12, (1,-1): 12})


    def test_blind_dog(self):
        self.assertEqual(Betza('fFrlbW').directions,
                {(-1, 1): 1,            (1, 1): 1,
                 (-1, 0): 1,            (1, 0): 1,
                             (0,-1): 1           })

    def test_charging_knight(self):
        self.assertEqual(Betza('fNrrllbK').directions,
                {            (-1, 2): 1,            (1, 2): 1,
                 (-2, 1): 1,                                   (2, 1): 1,
                             (-1, 0): 1,            (1, 0): 1,
                             (-1,-1): 1, (0,-1): 1, (1,-1): 1           })

    def test_charging_rook(self):
        self.assertEqual(Betza('frlRrrllbK').directions,
                {            (0, 1): 0,
                 (-1, 0): 0,            (1, 0): 0,
                 (-1,-1): 1, (0,-1): 1, (1,-1): 1})

    def test_cloud_eagle(self):
        self.assertEqual(Betza('fbRfB3K').directions,
                {(-1, 1): 3, (0, 1): 0, (1, 1): 3,
                 (-1, 0): 1,            (1, 0): 1,
                 (-1,-1): 1, (0,-1): 0, (1,-1): 1})

    def test_colonel(self):
        self.assertEqual(Betza('fNfrlRK').directions,
                {            (-1, 2): 1,            (1, 2): 1,
                 (-2, 1): 1, (-1, 1): 1, (0, 1): 0, (1, 1): 1, (2, 1): 1,
                             (-1, 0): 0,            (1, 0): 0,
                             (-1,-1): 1, (0,-1): 1, (1,-1): 1           })

    def test_eagle(self):
        self.assertEqual(Betza('fBbRWbB2').directions,
                {(-1, 1): 0, (0, 1): 1, (1, 1): 0,
                 (-1, 0): 1,            (1, 0): 1,
                 (-1,-1): 2, (0,-1): 0, (1,-1): 2})

    def test_falcon(self):
        self.assertEqual(Betza('FfrlW').directions,
                {(-1, 1): 1, (0, 1): 1, (1, 1): 1,
                 (-1, 0): 1,            (1, 0): 1,
                 (-1,-1): 1,            (1,-1): 1})

    def test_fibnif(self):
        self.assertEqual(Betza('ffbbNF').directions,
                {(-1, 2): 1, (1, 2): 1,
                 (-1, 1): 1, (1, 1): 1,
                 (-1,-1): 1, (1,-1): 1,
                 (-1,-2): 1, (1,-2): 1})

    def test_heavenly_horse(self):
        self.assertEqual(Betza('ffbbN').directions,
                {(-1, 2): 1, (1, 2): 1,
                 (-1,-2): 1, (1,-2): 1})

    def test_left_quail(self):
        self.assertEqual(Betza('fRbrBblF').directions,
                {            (0, 1): 0,
                 (-1,-1): 1,            (1,-1): 0})

    def test_left_inverted_quail(self):
        self.assertEqual(Betza('fRfrBflF').directions,
                {(-1, 1): 1,            (1, 1): 0,
                             (0, 1): 0           })

    def test_right_quail(self):
        self.assertEqual(Betza('fRblBbrF').directions,
                {            (0, 1): 0,
                 (-1,-1): 0,            (1,-1): 1})

    def test_right_inverted_quail(self):
        self.assertEqual(Betza('fRflBfrF').directions,
                {(-1, 1): 0,            (1, 1): 1,
                             (0, 1): 0           })

    def test_shogi_knight(self):
        self.assertEqual(Betza('ffN').directions,
                {(-1, 2): 1, (1, 2): 1})

    def test_treacherous_fox(self):
        self.assertEqual(Betza('fbWFfbDA').directions,
                {(-2, 2): 1,             (0, 2): 1,            (2, 2): 1,
                             (-1, 1): 1, (0, 1): 1, (1, 1): 1,

                             (-1,-1): 1, (0,-1): 1, (1,-1): 1,
                 (-2,-2): 1,             (0,-2): 1,            (2,-2): 1})

    def test_wide_knight(self):
        self.assertEqual(Betza('llrrN').directions,
                {(-2, 1): 1, (2, 1): 1,
                 (-2,-1): 1, (2,-1): 1})


if __name__ == '__main__':
    unittest.main()
