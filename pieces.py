#!/usr/bin/env python3

import yaml

from betza import Betza

class PiecesException(Exception):
    pass

class Pieces:
    def __init__(self, filename='pieces.yaml'):
        with open(filename, 'r') as stream:
            doc = yaml.load(stream)

        abbrevs = set()
        for abbrev, info in doc.items():
            betza = Betza(info['betza'])
            if not betza.can_advance():
                raise PiecesException('Piece %s cannot advance' % abbrev)
            if self._promoted(abbrev) and not betza.can_retreat():
                raise PiecesException('Promoted piece %s cannot retreat' %
                        abbrev)
            abbrevs.add(abbrev)

        for abbrev in doc:
            if self._promoted(abbrev) and abbrev[1:] not in abbrevs:
                raise PiecesException('Unpromoted version of %s missing' %
                        abbrev)

    @staticmethod
    def _promoted(abbrev):
        return abbrev[0] == '+'
