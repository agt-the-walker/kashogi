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
            self.check(notation, expected)

    def test_double_digit_range_on_queen(self):
        self.check('Q12',
                {(-1, 1): 12, (0, 1): 12, (1, 1): 12,
                 (-1, 0): 12,             (1, 0): 12,
                 (-1,-1): 12, (0,-1): 12, (1,-1): 12})


    def test_blind_dog(self):
        self.check('fFrlbW',
                {(-1, 1): 1,            (1, 1): 1,
                 (-1, 0): 1,            (1, 0): 1,
                             (0,-1): 1           })

    def test_charging_knight(self):
        self.check('fNrrllbK',
                {            (-1, 2): 1,            (1, 2): 1,
                 (-2, 1): 1,                                   (2, 1): 1,
                             (-1, 0): 1,            (1, 0): 1,
                             (-1,-1): 1, (0,-1): 1, (1,-1): 1           })

    def test_charging_rook(self):
        self.check('frlRrrllbK',
                {            (0, 1): 0,
                 (-1, 0): 0,            (1, 0): 0,
                 (-1,-1): 1, (0,-1): 1, (1,-1): 1})

    def test_cloud_eagle(self):
        self.check('fbRfB3K',
                {(-1, 1): 3, (0, 1): 0, (1, 1): 3,
                 (-1, 0): 1,            (1, 0): 1,
                 (-1,-1): 1, (0,-1): 0, (1,-1): 1})

    def test_colonel(self):
        self.check('fNfrlRK',
                {            (-1, 2): 1,            (1, 2): 1,
                 (-2, 1): 1, (-1, 1): 1, (0, 1): 0, (1, 1): 1, (2, 1): 1,
                             (-1, 0): 0,            (1, 0): 0,
                             (-1,-1): 1, (0,-1): 1, (1,-1): 1           })

    def test_eagle(self):
        self.check('fBbRWbB2',
                {(-1, 1): 0, (0, 1): 1, (1, 1): 0,
                 (-1, 0): 1,            (1, 0): 1,
                 (-1,-1): 2, (0,-1): 0, (1,-1): 2})

    def test_falcon(self):
        self.check('FfrlW',
                {(-1, 1): 1, (0, 1): 1, (1, 1): 1,
                 (-1, 0): 1,            (1, 0): 1,
                 (-1,-1): 1,            (1,-1): 1})

    def test_fibnif(self):
        self.check('ffbbNF',
                {(-1, 2): 1, (1, 2): 1,
                 (-1, 1): 1, (1, 1): 1,
                 (-1,-1): 1, (1,-1): 1,
                 (-1,-2): 1, (1,-2): 1})

    def test_heavenly_horse(self):
        self.check('ffbbN',
                {(-1, 2): 1, (1, 2): 1,
                 (-1,-2): 1, (1,-2): 1})

    def test_inverted_pawn(self):
        self.check('bW',
                {(0, -1): 1},
                0, False, True)

    def test_lance(self):
        self.check('fR',
                {(0, 1): 0},
                1, True, False)

    def test_left_quail(self):
        self.check('fRbrBblF',
                {            (0, 1): 0,
                 (-1,-1): 1,            (1,-1): 0})

    def test_left_inverted_quail(self):
        self.check('bRfrBflF',
                {(-1, 1): 1,            (1, 1): 0,
                             (0,-1): 0           })

    def test_pawn(self):
        self.check('fW',
                {(0, 1): 1},
                1, True, False)

    def test_right_quail(self):
        self.check('fRblBbrF',
                {            (0, 1): 0,
                 (-1,-1): 0,            (1,-1): 1})

    def test_right_inverted_quail(self):
        self.check('bRflBfrF',
                {(-1, 1): 0,            (1, 1): 1,
                             (0,-1): 0           })

    def test_shogi_knight(self):
        self.check('ffN',
                {(-1, 2): 1, (1, 2): 1},
                2, True, False)

    def test_treacherous_fox(self):
        self.check('fbWFfbDA',
                {(-2, 2): 1,             (0, 2): 1,            (2, 2): 1,
                             (-1, 1): 1, (0, 1): 1, (1, 1): 1,

                             (-1,-1): 1, (0,-1): 1, (1,-1): 1,
                 (-2,-2): 1,             (0,-2): 1,            (2,-2): 1})

    def test_wide_knight(self):
        self.check('llrrN',
                {(-2, 1): 1, (2, 1): 1,
                 (-2,-1): 1, (2,-1): 1})

    def check(self, notation, expected_directions, expected_num_restricted=0,
              expected_can_advance=True, expected_can_retreat=True):
        betza = Betza(notation)
        self.assertEqual(betza.directions, expected_directions)
        self.assertEqual(betza.num_restricted_furthest_ranks(),
                expected_num_restricted)
        self.assertEqual(betza.can_advance(), expected_can_advance)
        self.assertEqual(betza.can_retreat(), expected_can_retreat)


if __name__ == '__main__':
    unittest.main()
