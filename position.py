#!/usr/bin/env python3

import re

from collections import defaultdict
from pieces import Pieces

class Position:
    MIN_SIZE = 3
    NUM_PLAYERS = 2

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
        self._num_royals = [0] * self.NUM_PLAYERS

        # the following data structure is indexed by [player][abbrev][file]
        self._num_per_file = [defaultdict(lambda: defaultdict(int))
                for count in range(self.NUM_PLAYERS)]

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
        file = 0

        for token in tokens:
            if token.isdigit():
                file += int(token)
            else:
                file += 1
                self._parse_piece(token, file)

        if file > self._num_files:
            self._num_files = file

    def _parse_piece(self, token, file):
        abbrev = token.upper()
        if not self._pieces.exist(abbrev):
            raise ValueError('Invalid piece in SFEN: {}'.format(token))
        player = 0 if abbrev == token else 1

        if self._pieces.is_royal(abbrev):
            self._num_royals[player] += 1
            if self._num_royals[player] > 1:
                raise ValueError('Too many royal pieces for {}'
                        .format(self._player_name(player)))

        max_per_file = self._pieces.max_per_file(abbrev)
        if max_per_file:
            self._num_per_file[player][abbrev][file] += 1
            if self._num_per_file[player][abbrev][file] > max_per_file:
                raise ValueError('Too many {} for {} on file {}'
                        .format(abbrev, self._player_name(player), file))

    def _player_name(self, player):
        assert player < self.NUM_PLAYERS
        return {0: 'black', 1: 'white'}[player]
