#!/usr/bin/env python3

import re
import yaml

from betza import Betza
from collections import defaultdict


class PiecesException(Exception):
    pass


class Pieces:
    def __init__(self, filename='pieces.yaml'):
        with open(filename, 'r', encoding='utf-8') as stream:
            doc = yaml.safe_load(stream)

        self._betza = {}
        self._kanji = {}
        self._royal = set()
        self._no_drop_mate = set()
        self._max_per_file = {}

        for abbrev, info in doc.items():
            if not re.match(r"\+?[A-Z]['A-Z]?$", abbrev):
                raise PiecesException('Invalid piece abbreviation: {}'
                                      .format(abbrev))

            self._betza[abbrev] = Betza(info['betza'])
            self._kanji[abbrev] = info['kanji']

            if 'flags' in info:
                if self.is_promoted(abbrev):
                    raise PiecesException('Promoted piece {} cannot have flags'
                                          .format(abbrev))
                for flag in info['flags']:
                    if flag == 'royal':
                        self._royal.add(abbrev)
                    elif flag == 'no_drop_mate':
                        self._no_drop_mate.add(abbrev)
                    m = re.match("max_([1-9][0-9]*)_per_file$", flag)
                    if m:
                        self._max_per_file[abbrev] = int(m.group(1))

        self._check_consistency()
        self._check_kanjis()

    def _check_consistency(self):
        for abbrev, betza in self._betza.items():
            if not betza.can_advance():
                raise PiecesException('Piece {} cannot advance'.format(abbrev))

            elif self.is_promoted(abbrev):
                if not betza.can_retreat():
                    raise PiecesException('Promoted piece {} cannot retreat'
                                          .format(abbrev))
                elif self.unpromoted(abbrev) not in self._betza:
                    raise PiecesException('Unpromoted version of {} missing'
                                          .format(abbrev))

            elif self.can_promote(abbrev) and self.is_royal(abbrev):
                raise PiecesException('Promotable piece {} cannot be royal'
                                      .format(abbrev))

            elif not self.can_promote(abbrev) and not betza.can_retreat():
                raise PiecesException('Unpromotable piece {} cannot retreat'
                                      .format(abbrev))

            elif betza.can_change_file() and abbrev in self._max_per_file:
                raise PiecesException('Piece {} can change files'
                                      .format(abbrev))

            elif betza.is_rider and self.no_drop_mate(abbrev):
                raise PiecesException('Piece {} is a rider'.format(abbrev))

    def _check_kanjis(self):
        abbrevs = defaultdict(list)

        for abbrev, kanji in self._kanji.items():
            abbrevs[kanji].append(abbrev)

        for kanji, abbrevs in abbrevs.items():
            if len(abbrevs) > 2:
                raise PiecesException('Too many pieces with kanji {}'
                                      .format(kanji))
            elif len(abbrevs) == 2:
                if self.is_promoted(abbrevs[0]) == \
                   self.is_promoted(abbrevs[1]):
                    raise PiecesException('Two promoted or unpromoted pieces '
                                          'with kanji {}'.format(kanji))
                if self.directions(abbrevs[0]) != \
                   self.directions(abbrevs[1]):
                    raise PiecesException('Two different betza for kanji {}'
                                          .format(kanji))

    def exist(self, abbrev):
        return abbrev in self._betza

    def kanji(self, abbrev):
        return self._kanji[abbrev]

    def can_promote(self, abbrev):
        return self.promoted(abbrev) in self._betza

    def is_royal(self, abbrev):
        return abbrev in self._royal

    def no_drop_mate(self, abbrev):
        return abbrev in self._no_drop_mate

    def max_per_file(self, abbrev):
        return self._max_per_file.get(abbrev)

    def can_retreat(self, abbrev):
        return self._betza[abbrev].can_retreat()

    def directions(self, abbrev):
        return self._betza[abbrev].directions

    def num_restricted_furthest_ranks(self, abbrev):
        return self._betza[abbrev].num_restricted_furthest_ranks()

    @staticmethod
    def is_promoted(abbrev):
        return abbrev[0] == '+'

    @staticmethod
    def promoted(abbrev):
        assert not Pieces.is_promoted(abbrev)
        return '+' + abbrev

    @staticmethod
    def unpromoted(abbrev):
        assert Pieces.is_promoted(abbrev)
        return abbrev[1:]
