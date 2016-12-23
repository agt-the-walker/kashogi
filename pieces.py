#!/usr/bin/env python3

import re
import yaml

from betza import Betza
from collections import defaultdict

class PiecesException(Exception):
    pass

class Pieces:
    def __init__(self, filename='pieces.yaml'):
        with open(filename, 'r') as stream:
            doc = yaml.load(stream)

        self._betza = {}
        self._flags = defaultdict(lambda: set())

        for abbrev, info in doc.items():
            if not re.match("\+?[A-Z]['A-Z]?$", abbrev):
                raise PiecesException('Invalid piece abbreviation: {}'
                        .format(abbrev))

            self._betza[abbrev] = Betza(info['betza'])
            if 'flags' in info:
                self._flags[abbrev] = set(info['flags'])

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

    def exist(self, abbrev):
        return abbrev in self._betza

    def is_royal(self, abbrev):
        return 'royal' in self._flags[abbrev]

    @staticmethod
    def _promoted(abbrev):
        return abbrev[0] == '+'
