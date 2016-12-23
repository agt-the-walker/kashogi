#!/usr/bin/env python3

import re
import yaml

from betza import Betza

class PiecesException(Exception):
    pass

class Pieces:
    def __init__(self, filename='pieces.yaml'):
        with open(filename, 'r') as stream:
            self._doc = yaml.load(stream)

        abbrevs = set()
        for abbrev, info in self._doc.items():
            if not re.match("\+?[A-Z]['A-Z]?$", abbrev):
                raise PiecesException('Invalid piece abbreviation: {}'
                        .format(abbrev))

            betza = Betza(info['betza'])
            if not betza.can_advance():
                raise PiecesException('Piece {} cannot advance'.format(abbrev))
            if self._promoted(abbrev) and not betza.can_retreat():
                raise PiecesException('Promoted piece {} cannot retreat'
                        .format(abbrev))

            abbrevs.add(abbrev)

        for abbrev in self._doc:
            if self._promoted(abbrev) and abbrev[1:] not in abbrevs:
                raise PiecesException('Unpromoted version of {} missing'
                        .format(abbrev))

    def exist(self, abbrev):
        return abbrev in self._doc

    @staticmethod
    def _promoted(abbrev):
        return abbrev[0] == '+'
