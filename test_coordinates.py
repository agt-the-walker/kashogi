#!/usr/bin/env python3

import unittest

from PyQt5.QtCore import QRectF

from coordinates import Coordinates
from position import Position


class Item:
    def sceneBoundingRect(self):
        return QRectF(0, 0, 17, 21)


class CoordinatesTestCase(unittest.TestCase):
    NUM_FILES = 3
    NUM_RANKS = 4

    @classmethod
    def setUpClass(cls):
        cls._coordinates = Coordinates(cls.NUM_FILES, cls.NUM_RANKS)
        cls._item = Item()

    def test_identity(self):
        for file in range(1, self.NUM_FILES+1):
            for rank in range(1, self.NUM_RANKS+1):
                for player in range(Position.NUM_PLAYERS):
                    square = file, rank
                    pos = self._coordinates.square_to_pos(square,
                            self._item, player)                         # noqa
                    actual_square = self._coordinates.pos_to_square(pos,
                            self._item, player)                         # noqa
                    self.assertEqual(square, actual_square)

    def test_rank_label(self):
        self.assertEqual(self._coordinates.rank_label(1), 'a')
        self.assertEqual(self._coordinates.rank_label(26), 'z')
        self.assertEqual(self._coordinates.rank_label(27), 'aa')
        self.assertEqual(self._coordinates.rank_label(52), 'zz')
        self.assertEqual(self._coordinates.rank_label(53), 'aaa')


if __name__ == '__main__':
    unittest.main()
