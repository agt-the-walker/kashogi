#!/usr/bin/env python3

import re

from pieces import Pieces

class Position:
    MIN_SIZE = 3

    def __init__(self, sfen):
        self._pieces = Pieces()

        m = re.match("(\S+) [wb] \S+( [1-9][0-9]*)?$", sfen)
        if not m:
            raise ValueError('Invalid SFEN')

        ranks = m.group(1).split('/')
        self._num_ranks = len(ranks)
        if self._num_ranks < self.MIN_SIZE:
            raise ValueError('Too few ranks: {} < {}'.format(self._num_ranks,
                self.MIN_SIZE))

        self._num_files = 0
        for rank in ranks:
            self._parse_rank(rank)

        if self._num_files < self.MIN_SIZE:
            raise ValueError('Too few files: {} < {}'.format(self._num_files,
                self.MIN_SIZE))

    @property
    def num_ranks(self):
        return self._num_ranks

    @property
    def num_files(self):
        return self._num_files

    def _parse_rank(self, rank):
        tokens = re.findall("\+?[a-zA-Z](?:[a-zA-Z](?=@)|')?|\d+", rank)
        num_files = 0

        for token in tokens:
            if token.isdigit():
                num_files += int(token)
            else:
                if not self._pieces.exist(token.upper()):
                    raise ValueError('Invalid piece in SFEN: {}'.format(token))
                num_files += 1

        if num_files > self._num_files:
            self._num_files = num_files
