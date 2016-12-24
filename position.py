#!/usr/bin/env python3

import math
import re

from collections import defaultdict
from pieces import Pieces
from utils import ordinal

class Position:
    MIN_SIZE = 3
    NUM_PLAYERS = 2
    UNPROMOTED_PIECE_REGEX = "[a-zA-Z](?:[a-zA-Z](?=@)|')?"

    def __init__(self, sfen):
        self._pieces = Pieces()

        m = re.match("(\S+) [wb] (\S+)( [1-9][0-9]*)?$", sfen)
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

        for rank, s in enumerate(ranks):
            self._parse_rank(s, rank)

        if self._num_files < self.MIN_SIZE:
            raise ValueError('Too few files: {} < {}'.format(self._num_files,
                    self.MIN_SIZE))

        self._parse_hands(m.group(2))

    @property
    def num_ranks(self):
        return self._num_ranks

    @property
    def num_files(self):
        return self._num_files

    def _parse_rank(self, s, rank):
        tokens = re.findall('\+?' + self.UNPROMOTED_PIECE_REGEX + '|\d+', s)
        file = 0

        for token in tokens:
            if token.isdigit():
                file += int(token)
            else:
                file += 1
                self._parse_piece(token, rank, file)

        if file > self._num_files:
            self._num_files = file

    def _parse_piece(self, token, rank, file):
        abbrev = token.upper()
        if not self._pieces.exist(abbrev):
            raise ValueError('Invalid piece on board: {}'.format(token))
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

        num_restricted = self._pieces.num_restricted_furthest_ranks(abbrev)
        if num_restricted > 0:
            nth_furthest_rank = {0: rank + 1, 1: self.num_ranks - rank}[player]
            assert nth_furthest_rank > 0

            if num_restricted >= nth_furthest_rank:
                 raise ValueError('{} for {} found on {} furthest rank'
                        .format(abbrev, self._player_name(player),
                                ordinal(nth_furthest_rank)))

    def _parse_hands(self, s):
        for number, token in re.findall('([1-9][0-9]*)?(' +
                self.UNPROMOTED_PIECE_REGEX + ')', s):
            abbrev = token.upper()
            if not self._pieces.exist(abbrev):
                raise ValueError('Invalid piece in hand: {}'.format(token))
            if self._pieces.is_royal(abbrev):
                raise ValueError('Royal piece in hand: {}'.format(token))

    def _player_name(self, player):
        assert player < self.NUM_PLAYERS
        return {0: 'black', 1: 'white'}[player]
