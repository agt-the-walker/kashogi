#!/usr/bin/env python3

import re

from pieces import Pieces

class Position:
    MIN_SIZE = 3

    def __init__(self, sfen):
        pieces = Pieces()

        m = re.match("(\S+) [wb] \S+( [1-9][0-9]*)?$", sfen)
        if not m:
            raise ValueError('Invalid SFEN')

        ranks = m.group(1).split('/')
        if len(ranks) < self.MIN_SIZE:
            raise ValueError('Too few ranks: {} < {}'.format(len(ranks),
                self.MIN_SIZE))
