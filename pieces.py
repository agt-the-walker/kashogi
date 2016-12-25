#!/usr/bin/env python3

import re
import yaml

from betza import Betza


class PiecesException(Exception):
    pass


class Pieces:
    def __init__(self, filename='pieces.yaml'):
        with open(filename, 'r') as stream:
            doc = yaml.load(stream)

        self._betza = {}
        self._royal = set()
        self._max_per_file = {}

        for abbrev, info in doc.items():
            if not re.match("\+?[A-Z]['A-Z]?$", abbrev):
                raise PiecesException('Invalid piece abbreviation: {}'
                                      .format(abbrev))

            self._betza[abbrev] = Betza(info['betza'])
            if 'flags' in info:
                for flag in info['flags']:
                    if flag == 'royal':
                        self._royal.add(abbrev)
                    m = re.match("max_([1-9][0-9]*)_per_file$", flag)
                    if m:
                        self._max_per_file[abbrev] = int(m.group(1))

        self._check_consistency()

    def _check_consistency(self):
        for abbrev, betza in self._betza.items():
            if not betza.can_advance():
                raise PiecesException('Piece {} cannot advance'.format(abbrev))
            if self._promoted(abbrev) and not betza.can_retreat():
                raise PiecesException('Promoted piece {} cannot retreat'
                                      .format(abbrev))

            if self._promoted(abbrev):
                if abbrev[1:] not in self._betza:
                    raise PiecesException('Unpromoted version of {} missing'
                                          .format(abbrev))
            elif "+{}".format(abbrev) not in self._betza and \
                    not betza.can_retreat():
                raise PiecesException('Unpromotable piece {} cannot retreat'
                                      .format(abbrev))

            if betza.can_change_file() and abbrev in self._max_per_file:
                raise PiecesException('Piece {} can change files'
                                      .format(abbrev))

    def exist(self, abbrev):
        return abbrev in self._betza

    def is_royal(self, abbrev):
        return abbrev in self._royal

    def max_per_file(self, abbrev):
        return self._max_per_file.get(abbrev)

    def directions(self, abbrev):
        return self._betza[abbrev].directions

    def num_restricted_furthest_ranks(self, abbrev):
        return self._betza[abbrev].num_restricted_furthest_ranks()

    @staticmethod
    def _promoted(abbrev):
        return abbrev[0] == '+'
