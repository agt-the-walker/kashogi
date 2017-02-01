#!/usr/bin/env python3

from string import ascii_lowercase

from PyQt5.QtCore import QPointF

BOARD_STROKE = 2
LINE_STROKE = 1
LINE_OFFSET = BOARD_STROKE - LINE_STROKE / 2
SQUARE_SIZE = 39

PIECE_OFFSET = 1


class Coordinates:
    def __init__(self, num_files, num_ranks):
        self._num_files = num_files
        self._num_ranks = num_ranks

    def square_to_pos(self, square, item, player):
        file, rank = square
        piece_offset = PIECE_OFFSET if player == 0 else -PIECE_OFFSET
        return QPointF(LINE_OFFSET + (self._num_files - file + 0.5) *
                       SQUARE_SIZE - item.boundingRect().width() / 2,
                       LINE_OFFSET + (rank - 0.5) * SQUARE_SIZE
                       + piece_offset - item.boundingRect().height() / 2)

    def pos_to_square(self, pos, item, player):
        piece_offset = PIECE_OFFSET if player == 0 else -PIECE_OFFSET
        return (round(- (pos.x() - LINE_OFFSET
                      + item.boundingRect().width() / 2) / SQUARE_SIZE
                      + self._num_files + 0.5),
                round((pos.y() - LINE_OFFSET + item.boundingRect().height() / 2
                      - piece_offset) / SQUARE_SIZE + 0.5))

    @staticmethod
    def rank_label(rank):
        assert rank > 0
        rank -= 1
        quotient, remainder = divmod(rank, len(ascii_lowercase))
        return chr(ord('a') + remainder) * (quotient + 1)
