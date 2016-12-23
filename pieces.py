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

        self._abbrevs = set()
        self._flags = defaultdict(lambda: set())

        for abbrev, info in doc.items():
            if not re.match("\+?[A-Z]['A-Z]?$", abbrev):
                raise PiecesException('Invalid piece abbreviation: {}'
                        .format(abbrev))

            betza = Betza(info['betza'])
            if not betza.can_advance():
                raise PiecesException('Piece {} cannot advance'.format(abbrev))
            if self._promoted(abbrev) and not betza.can_retreat():
                raise PiecesException('Promoted piece {} cannot retreat'
                        .format(abbrev))

            self._abbrevs.add(abbrev)
            if 'flags' in info:
                self._flags[abbrev] = set(info['flags'])

        for abbrev in self._abbrevs:
            if self._promoted(abbrev) and abbrev[1:] not in self._abbrevs:
                raise PiecesException('Unpromoted version of {} missing'
                        .format(abbrev))

    def exist(self, abbrev):
        return abbrev in self._abbrevs

    def is_royal(self, abbrev):
        return 'royal' in self._flags[abbrev]

    @staticmethod
    def _promoted(abbrev):
        return abbrev[0] == '+'
