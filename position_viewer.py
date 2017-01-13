#!/usr/bin/env python3

import signal
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics, QPen
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

        if position.num_ranks > len(ascii_lowercase):
            raise ValueError('Too many ranks in position for GUI')

        self._draw_board(position)
        self._draw_board_labels(position)

    def _draw_board_labels(self, pos):
        font = QFont(LABEL_FONT)
        font.setPointSize(LABEL_SIZE)

        self._compute_lowercase_max_width(font)

        file_labels = QGraphicsItemGroup()
        rank_labels = QGraphicsItemGroup()

        for i in range(pos.num_files):
            file = pos.num_files - i if pos.player_to_move == 0 else i+1

            text = QGraphicsSimpleTextItem(str(file))
            text.setFont(font)
            text.setPos(i * SQUARE_SIZE - text.boundingRect().width() / 2, 0)

            file_labels.addToGroup(text)

        file_labels.setPos(LINE_OFFSET + 0.5 * SQUARE_SIZE,
                           - FILE_LABEL_OFFSET - LABEL_SIZE)

        for i in range(pos.num_ranks):
            rank = pos.num_ranks - i if pos.player_to_move == 1 else i+1

            text = QGraphicsSimpleTextItem(chr(ord('a') + rank - 1))
            text.setFont(font)
            text.setPos((self._max_width - text.boundingRect().width()) / 2,
                        i * SQUARE_SIZE - text.boundingRect().height() / 2)

            rank_labels.addToGroup(text)

        rank_labels.setPos(self._board.boundingRect().width()
                           + RANK_LABEL_OFFSET,
                           LINE_OFFSET + 0.5 * SQUARE_SIZE)

        self.addItem(file_labels)
        self.addItem(rank_labels)

    def _compute_lowercase_max_width(self, font):
        fm = QFontMetrics(font)
        self._max_width = max([fm.width(letter) for letter in ascii_lowercase])

    def _draw_board(self, pos):
        board = QGraphicsItemGroup()

        pen = QPen()
        pen.setWidth(BOARD_STROKE)

        board.addToGroup(self.addRect(
            BOARD_STROKE / 2, BOARD_STROKE / 2,
            SQUARE_SIZE * pos.num_files + BOARD_STROKE - LINE_STROKE,
            SQUARE_SIZE * pos.num_ranks + BOARD_STROKE - LINE_STROKE,
            pen))

        pen.setWidth(LINE_STROKE)

        for file in range(1, pos.num_files):
            board.addToGroup(self.addLine(
                LINE_OFFSET + SQUARE_SIZE * file, LINE_OFFSET,
                LINE_OFFSET + SQUARE_SIZE * file,
                LINE_OFFSET + SQUARE_SIZE * pos.num_ranks,
                pen))

        for rank in range(1, pos.num_ranks):
            board.addToGroup(self.addLine(
                LINE_OFFSET, LINE_OFFSET + SQUARE_SIZE * rank,
                LINE_OFFSET + SQUARE_SIZE * pos.num_files,
                LINE_OFFSET + SQUARE_SIZE * rank,
                pen))

        self.addItem(board)
        self._board = board


class PositionView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setFrameStyle(0)

    def keyPressEvent(self, event):
        if event.text().isdigit():
            zoom_level = int(event.text())
            if zoom_level > 0:
                self.resize(self.scene().width() * zoom_level,
                            self.scene().height() * zoom_level)

    def resizeEvent(self, event):
        self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)


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
