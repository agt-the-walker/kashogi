#!/usr/bin/env python3

import re


class Betza:
    def __init__(self, notation):
        tokens = re.findall(r"([a-z]*)([A-Z])(\d+)?", notation)
        if not tokens:
            raise ValueError('No token found')

        self._directions = {}  # coordinate => best range
        self._is_rider = False

        for token in tokens:
            self._parse(*token)

    @property
    def directions(self):
        return self._directions

    @property
    def is_rider(self):
        return self._is_rider

    def can_advance(self):
        return self._max_dy > 0

    def can_retreat(self):
        return self._min_dy < 0

    def can_change_file(self):
        return self._min_dx < 0 or 0 < self._max_dx

    # i.e. no legal moves on subsequent turns if dropped or not promoted
    def num_restricted_furthest_ranks(self):
        return max(self._min_dy, 0)

    def _parse(self, modifiers, piece, range):  # noqa: C901
        if not range:
            if piece in ['B', 'Q', 'R']:
                range = 0  # i.e. unlimited rider
            else:
                range = 1  # i.e. leaper
        else:
            range = int(range)

        if piece == 'A':
            self._add_movement(2, 2, modifiers, range)
        elif piece in ['B', 'F']:
            self._add_movement(1, 1, modifiers, range)
        elif piece == 'C':
            self._add_movement(1, 3, modifiers, range)
        elif piece == 'D':
            self._add_movement(0, 2, modifiers, range)
        elif piece == 'G':
            self._add_movement(3, 3, modifiers, range)
        elif piece == 'H':
            self._add_movement(0, 3, modifiers, range)
        elif piece in ['K', 'Q']:
            self._add_movement(0, 1, modifiers, range)
            self._add_movement(1, 1, modifiers, range)
        elif piece == 'N':
            self._add_movement(1, 2, modifiers, range)
        elif piece in ['R', 'W']:
            self._add_movement(0, 1, modifiers, range)
        elif piece == 'Z':
            self._add_movement(2, 3, modifiers, range)
        else:
            raise ValueError('Unknown piece: ' + piece)

        if range != 1:
            self._is_rider = True

    def _add_movement(self, m, n, modifiers, range):
        assert m <= n

        if modifiers:
            if m == 0:  # orthogonal
                list_modifiers = re.findall("[bflr]", modifiers)
            else:       # diagonal/oblique
                list_modifiers = [
                        x[0] for x in
                        re.findall(r"(bl|br|fl|fr|([bflr])\2?)", modifiers)]

        for coordinate in self._coordinates(m, n):
            dx, dy = coordinate
            if not modifiers:
                self._add_direction(dx, dy, range)
                continue

            for modifier in list_modifiers:
                if len(modifier) == 2 and modifier[0] == modifier[1]:
                    modifier = modifier[0]
                    repeated = True
                else:
                    repeated = False

                if self._allowed_direction(dx, dy, modifier, repeated):
                    self._add_direction(dx, dy, range)

    def _allowed_direction(self, dx, dy, modifier, repeated):
        # diagonal/oblique
        if modifier == 'bl' and dx < 0 and dy < 0:
            return True
        elif modifier == 'br' and dx > 0 and dy < 0:
            return True
        elif modifier == 'fl' and dx < 0 and dy > 0:
            return True
        elif modifier == 'fr' and dx > 0 and dy > 0:
            return True

        # all
        if not (repeated) or abs(dx) < abs(dy):
            if modifier == 'b' and dy < 0:
                return True
            elif modifier == 'f' and dy > 0:
                return True
        if not (repeated) or abs(dx) > abs(dy):
            if modifier == 'l' and dx < 0:
                return True
            elif modifier == 'r' and dx > 0:
                return True

        return False

    def _add_direction(self, dx, dy, range):
        if (dx, dy) in self._directions:
            # only upgrade range for the better
            old_range = self._directions[(dx, dy)]
            if old_range != 0 and (range > old_range or range == 0):
                self._directions[(dx, dy)] = range
        else:
            self._directions[(dx, dy)] = range

        if not hasattr(self, '_min_dx') or dx < self._min_dx:
            self._min_dx = dx
        if not hasattr(self, '_min_dy') or dy < self._min_dy:
            self._min_dy = dy

        if not hasattr(self, '_max_dx') or dx > self._max_dx:
            self._max_dx = dx
        if not hasattr(self, '_max_dy') or dy > self._max_dy:
            self._max_dy = dy

    @staticmethod
    def _coordinates(m, n):
        assert m <= n

        if m == n:  # diagonal
            for coordinate in [(-m, -n), (-m, n), (m, -n), (m, n)]:
                yield coordinate
        else:       # oblique/orthogonal
            if m != 0:  # oblique
                for coordinate in [(-m, n), (m, -n), (n, -m), (-n, m)]:
                    yield coordinate
            for coordinate in [(-m, -n), (m, n), (-n, -m), (n, m)]:
                yield coordinate
