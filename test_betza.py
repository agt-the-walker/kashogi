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
        with self.assertRaisesRegex(ValueError, 'Unknown piece: S'):
            Betza('S')

    def test_notation_order_on_dragon(self):
        expected = {(-1,  1): 1, (0,  1): 0, (1,  1): 1,
                    (-1,  0): 0,             (1,  0): 0,
                    (-1, -1): 1, (0, -1): 0, (1, -1): 1}
        for notation in ['FR', 'RF', 'KR', 'RK']:
            self.check(notation, expected, True)

    def test_double_digit_range_on_queen(self):
        self.check('Q12',
                   {(-1,  1): 12, (0,  1): 12, (1,  1): 12,
                    (-1,  0): 12,              (1,  0): 12,
                    (-1, -1): 12, (0, -1): 12, (1, -1): 12},
                   True)

    def test_blind_dog(self):
        self.check('fFrlbW',
                   {(-1, 1): 1,             (1, 1): 1,
                    (-1, 0): 1,             (1, 0): 1,
                                (0, -1): 1},                            # noqa
                   False)

    def test_charging_knight(self):
        self.check('fNrrllbK',
                   {            (-1,  2): 1,             (1,  2): 1,    # noqa
                    (-2, 1): 1,                                      (2, 1): 1,
                                (-1,  0): 1,             (1,  0): 1,
                                (-1, -1): 1, (0, -1): 1, (1, -1): 1},
                   False)

    def test_charging_rook(self):
        self.check('frlRbK',
                   {             (0,  1): 0,                            # noqa
                    (-1,  0): 0,             (1,  0): 0,
                    (-1, -1): 1, (0, -1): 1, (1, -1): 1},
                   True)

    def test_cloud_eagle(self):
        self.check('fbRfB3K',
                   {(-1,  1): 3, (0,  1): 0, (1,  1): 3,
                    (-1,  0): 1,             (1,  0): 1,
                    (-1, -1): 1, (0, -1): 0, (1, -1): 1},
                   True)

    def test_colonel(self):
        self.check('fNfrlRK',
                   {            (-1,  2): 1,             (1,  2): 1,    # noqa
                    (-2, 1): 1, (-1,  1): 1, (0,  1): 0, (1,  1): 1, (2, 1): 1,
                                (-1,  0): 0,             (1,  0): 0,
                                (-1, -1): 1, (0, -1): 1, (1, -1): 1},
                   True)

    def test_eagle(self):
        self.check('fBbRWbB2',
                   {(-1,  1): 0, (0,  1): 1, (1,  1): 0,
                    (-1,  0): 1,             (1,  0): 1,
                    (-1, -1): 2, (0, -1): 0, (1, -1): 2},
                   True)

    def test_falcon(self):
        self.check('FfrlW',
                   {(-1,  1): 1, (0, 1): 1, (1,  1): 1,
                    (-1,  0): 1,            (1,  0): 1,
                    (-1, -1): 1,            (1, -1): 1},
                   False)

    def test_fibnif(self):
        self.check('ffbbNF',
                   {(-1,  2): 1, (1,  2): 1,
                    (-1,  1): 1, (1,  1): 1,
                    (-1, -1): 1, (1, -1): 1,
                    (-1, -2): 1, (1, -2): 1},
                   False)

    def test_flying_cock(self):
        self.check('fFrlW',
                   {(-1,  1): 1, (1, 1): 1,
                    (-1,  0): 1, (1, 0): 1},
                   False, 0, True, False)

    def test_heavenly_horse(self):
        self.check('ffbbN',
                   {(-1,  2): 1, (1,  2): 1,
                    (-1, -2): 1, (1, -2): 1},
                   False)

    def test_inverted_pawn(self):
        self.check('bW',
                   {(0, -1): 1},
                   False, 0, False, True, False)

    def test_lance(self):
        self.check('fR',
                   {(0, 1): 0},
                   True, 1, True, False, False)

    def test_leopard(self):
        self.check('B2N',
                   {             (-1,  2): 1, (1,  2): 1,               # noqa
                    (-2,  1): 1, (-1,  1): 2, (1,  1): 2, (2,  1): 1,
                    (-2, -1): 1, (-1, -1): 2, (1, -1): 2, (2, -1): 1,
                                 (-1, -2): 1, (1, -2): 1},              # noqa
                   True)

    def test_left_quail(self):
        self.check('fRbrBblF',
                   {             (0, 1): 0,                             # noqa
                    (-1, -1): 1,            (1, -1): 0},
                   True)

    def test_left_inverted_quail(self):
        self.check('bRfrBflF',
                   {(-1, 1): 1,             (1, 1): 0,
                                (0, -1): 0},                            # noqa
                   True)

    def test_left_rook(self):
        self.check('flbR',
                   {            (0,  1): 0,                             # noqa
                    (-1, 0): 0,
                                (0, -1): 0},
                   True)

    def test_nightrider(self):
        self.check('N0',
                   {(-1,  2): 0,  (1,  2): 0,
                    (-2,  1): 0,  (2,  1): 0,
                    (-2, -1): 0,  (2, -1): 0,
                    (-1, -2): 0,  (1, -2): 0},
                   True)

    def test_pawn(self):
        self.check('fW',
                   {(0, 1): 1},
                   False, 1, True, False, False)

    def test_right_quail(self):
        self.check('fRblBbrF',
                   {             (0, 1): 0,                             # noqa
                    (-1, -1): 0,            (1, -1): 1},
                   True)

    def test_right_inverted_quail(self):
        self.check('bRflBfrF',
                   {(-1, 1): 0,             (1, 1): 1,
                                (0, -1): 0},                            # noqa
                   True)

    def test_right_rook(self):
        self.check('frbR',
                   {(0,  1): 0,
                                (1, 0): 0,                              # noqa
                    (0, -1): 0},
                   True)

    def test_shogi_knight(self):
        self.check('ffN',
                   {(-1, 2): 1, (1, 2): 1},
                   False, 2, True, False)

    def test_spanish_lion(self):
        self.check('CH',
                {             (-1,  3): 1, (0,  3): 1, (1,  3): 1,     # noqa
                 (-3,  1): 1,                                      (3,  1): 1,
                 (-3,  0): 1,                                      (3,  0): 1,
                 (-3, -1): 1,                                      (3, -1): 1,
                              (-1, -3): 1, (0, -3): 1, (1, -3): 1},
                False)

    def test_treacherous_fox(self):
        self.check('fbWFfbDA',
                {(-2,  2): 1,              (0,  2): 1,             (2,  2): 1,
                              (-1,  1): 1, (0,  1): 1, (1,  1): 1,      # noqa

                              (-1, -1): 1, (0, -1): 1, (1, -1): 1,
                 (-2, -2): 1,              (0, -2): 1,             (2, -2): 1},
                False)

    def test_tripper(self):
        self.check('G',
                   {(-3,  3): 1, (3,  3): 1,
                    (-3, -3): 1, (3, -3): 1},
                   False)

    def test_wide_knight(self):
        self.check('llrrN',
                   {(-2,  1): 1, (2,  1): 1,
                    (-2, -1): 1, (2, -1): 1},
                   False)

    def test_zebrarider(self):
        self.check('Z0',
                   {(-2,  3): 0,  (2,  3): 0,
                    (-3,  2): 0,  (3,  2): 0,
                    (-3, -2): 0,  (3, -2): 0,
                    (-2, -3): 0,  (2, -3): 0},
                   True)

    def check(self, notation, expected_directions, expected_is_rider,
              expected_num_restricted=0,
              expected_can_advance=True, expected_can_retreat=True,
              expected_can_change_file=True):
        betza = Betza(notation)
        self.assertEqual(betza.directions, expected_directions)
        self.assertEqual(betza.is_rider, expected_is_rider)
        self.assertEqual(betza.num_restricted_furthest_ranks(),
                         expected_num_restricted)
        self.assertEqual(betza.can_advance(), expected_can_advance)
        self.assertEqual(betza.can_retreat(), expected_can_retreat)
        self.assertEqual(betza.can_change_file(), expected_can_change_file)


if __name__ == '__main__':
    unittest.main()
