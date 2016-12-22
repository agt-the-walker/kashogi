#!/usr/bin/env python3

import unittest

from pieces import PiecesException, Pieces

class PiecesTestCase(unittest.TestCase):
    def test_normal_path(self):
        Pieces()

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
            Pieces('support/cannot_retreat.yaml')

    def test_cannot_unpromote(self):
        with self.assertRaisesRegex(PiecesException,
                'Unpromoted version of \+P missing'):
            Pieces('support/cannot_unpromote.yaml')


if __name__ == '__main__':
    unittest.main()
