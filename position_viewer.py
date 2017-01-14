#!/usr/bin/env python3

import signal
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QPen, QTransform
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, \
                            QGraphicsSimpleTextItem, QGraphicsItemGroup

from pieces import Pieces
from position import Position
from string import ascii_lowercase

BOARD_STROKE = 2
LINE_STROKE = 1
LINE_OFFSET = BOARD_STROKE - LINE_STROKE / 2
SQUARE_SIZE = 39  # preferably odd to center text correctly

LABEL_FONT = 'Sans'
LABEL_SIZE = 12
FILE_LABEL_OFFSET = 8
RANK_LABEL_OFFSET = 4


class PositionScene(QGraphicsScene):
    def __init__(self, position):
        super().__init__()
        self.bottom_player = position.player_to_move

        if position.num_ranks > len(ascii_lowercase):
            raise ValueError('Too many ranks in position for GUI')

        self._position = position
        self._draw_board()
        self._redraw_board_labels()

        self._has_board_labels = True

    def toggle_board_labels(self):
        if self._has_board_labels:
            self.removeItem(self._file_labels)
            self.removeItem(self._rank_labels)
        else:
            self._redraw_board_labels()

        self._has_board_labels = not self._has_board_labels
        self.setSceneRect(self.itemsBoundingRect())

    def flip_view(self):
        self.bottom_player = Position.NUM_PLAYERS - self.bottom_player - 1

        if not self._has_board_labels:
            return

        self.removeItem(self._file_labels)
        self.removeItem(self._rank_labels)

        self._redraw_board_labels()

    def _redraw_board_labels(self):
        font = QFont(LABEL_FONT)
        font.setPointSize(LABEL_SIZE)

        self._compute_lowercase_max_width(font)

        self._file_labels = QGraphicsItemGroup()
        self._rank_labels = QGraphicsItemGroup()

        position = self._position

        for i in range(position.num_files):
            file = position.num_files - i if self.bottom_player == 0 else i+1

            text = QGraphicsSimpleTextItem(str(file))
            text.setFont(font)
            text.setPos(i * SQUARE_SIZE - text.boundingRect().width() / 2, 0)

            self._file_labels.addToGroup(text)

        self._file_labels.setPos(LINE_OFFSET + 0.5 * SQUARE_SIZE,
                                 - FILE_LABEL_OFFSET - LABEL_SIZE)

        for i in range(position.num_ranks):
            rank = position.num_ranks - i if self.bottom_player == 1 else i+1

            text = QGraphicsSimpleTextItem(chr(ord('a') + rank - 1))
            text.setFont(font)
            text.setPos((self._max_width - text.boundingRect().width()) / 2,
                        i * SQUARE_SIZE - text.boundingRect().height() / 2)

            self._rank_labels.addToGroup(text)

        self._rank_labels.setPos(self._board.boundingRect().width()
                                 + RANK_LABEL_OFFSET,
                                 LINE_OFFSET + 0.5 * SQUARE_SIZE)

        self.addItem(self._file_labels)
        self.addItem(self._rank_labels)

    def _compute_lowercase_max_width(self, font):
        if hasattr(self, '_max_width'):
            return

        fm = QFontMetrics(font)
        self._max_width = max([fm.width(letter) for letter in ascii_lowercase])

    def _draw_board(self):
        board = QGraphicsItemGroup()

        pen = QPen()
        pen.setWidth(BOARD_STROKE)

        position = self._position

        board.addToGroup(self.addRect(
            BOARD_STROKE / 2, BOARD_STROKE / 2,
            SQUARE_SIZE * position.num_files + BOARD_STROKE - LINE_STROKE,
            SQUARE_SIZE * position.num_ranks + BOARD_STROKE - LINE_STROKE,
            pen))

        pen.setWidth(LINE_STROKE)

        for file in range(1, position.num_files):
            board.addToGroup(self.addLine(
                LINE_OFFSET + SQUARE_SIZE * file, LINE_OFFSET,
                LINE_OFFSET + SQUARE_SIZE * file,
                LINE_OFFSET + SQUARE_SIZE * position.num_ranks,
                pen))

        for rank in range(1, position.num_ranks):
            board.addToGroup(self.addLine(
                LINE_OFFSET, LINE_OFFSET + SQUARE_SIZE * rank,
                LINE_OFFSET + SQUARE_SIZE * position.num_files,
                LINE_OFFSET + SQUARE_SIZE * rank,
                pen))

        self.addItem(board)
        self._board = board


class PositionView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)

        self.setFrameStyle(0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self._resize(1)

    def _resize(self, zoom_level=None):
        if zoom_level:
            self._zoom_level = zoom_level
        self.setFixedSize(self._zoom_level * self.scene().width(),
                          self._zoom_level * self.scene().height())

    def keyPressEvent(self, event):
        if event.text().isdigit():
            zoom_level = int(event.text())
            if zoom_level > 0:
                t = QTransform.fromScale(zoom_level, zoom_level)
                self.setTransform(t)
                self._resize(zoom_level)
        elif event.text() == 'f':
            self.scene().flip_view()
        elif event.text() == 'l':
            self.scene().toggle_board_labels()
            self._resize()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: {} <sfen>'.format(sys.argv[0]))

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    scene = QGraphicsScene()

    position = Position(sys.argv[1], Pieces())
    view = PositionView(PositionScene(position))

    view.show()
    sys.exit(app.exec_())
