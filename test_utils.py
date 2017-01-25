#!/usr/bin/env python3

import unittest

from utils import rank_label


class UtilsTestCase(unittest.TestCase):
    def test_rank_label(self):
        self.assertEqual(rank_label(1), 'a')
        self.assertEqual(rank_label(26), 'z')
        self.assertEqual(rank_label(27), 'aa')
        self.assertEqual(rank_label(52), 'zz')
        self.assertEqual(rank_label(53), 'aaa')


if __name__ == '__main__':
    unittest.main()
