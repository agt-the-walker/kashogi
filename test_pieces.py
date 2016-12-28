#!/usr/bin/env python3

import unittest

from pieces import PiecesException, Pieces


class PiecesTestCase(unittest.TestCase):
    def test_normal_path(self):
        pieces = Pieces()

        self.assertTrue(pieces.exist('K'))
        self.assertTrue(pieces.exist("FF"))
        self.assertTrue(pieces.exist("+A'"))
        self.assertFalse(pieces.exist("FF@"))

        self.assertTrue(pieces.is_royal('K'))
        self.assertFalse(pieces.is_royal('N'))

        self.assertTrue(pieces.no_drop_mate("S'"))
        self.assertFalse(pieces.no_drop_mate('L'))

        self.assertIsNone(pieces.max_per_file('K'))
        self.assertEqual(pieces.max_per_file('P'), 1)
        self.assertEqual(pieces.max_per_file("S'"), 2)

        self.assertEqual(pieces.directions('P'), {(0, 1): 1})
        self.assertEqual(pieces.num_restricted_furthest_ranks('N'), 2)

    def test_invalid_abbreviation(self):
        with self.assertRaisesRegex(PiecesException,
                                    'Invalid piece abbreviation: Ph'):
            Pieces('support/invalid_abbreviation.yaml')

    def test_cannot_advance(self):
        with self.assertRaisesRegex(PiecesException, 'Piece P cannot advance'):
            Pieces('support/cannot_advance.yaml')

    def test_cannot_retreat(self):
        with self.assertRaisesRegex(PiecesException,
                                    'Promoted piece \+P cannot retreat'):
            Pieces('support/cannot_retreat_promoted.yaml')
        with self.assertRaisesRegex(PiecesException,
                                    'Unpromotable piece L cannot retreat'):
            Pieces('support/cannot_retreat_unpromotable.yaml')

    def test_cannot_be_royal(self):
        with self.assertRaisesRegex(PiecesException,
                                    'Promoted piece \+K cannot be royal'):
            Pieces('support/cannot_be_royal_promoted.yaml')
        with self.assertRaisesRegex(PiecesException,
                                    'Promotable piece K cannot be royal'):
            Pieces('support/cannot_be_royal_promotable.yaml')

    def test_cannot_unpromote(self):
        with self.assertRaisesRegex(PiecesException,
                                    'Unpromoted version of \+P missing'):
            Pieces('support/cannot_unpromote.yaml')

    def test_can_change_file(self):
        with self.assertRaisesRegex(PiecesException,
                                    'Piece P can change files'):
            Pieces('support/can_change_files.yaml')

    def test_is_rider(self):
        with self.assertRaisesRegex(PiecesException, 'Piece SR is a rider'):
            Pieces('support/is_rider.yaml')


if __name__ == '__main__':
    unittest.main()
