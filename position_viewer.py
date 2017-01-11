#!/usr/bin/env python3

import signal
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPen
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, \
                            QGraphicsSimpleTextItem

from pieces import Pieces
from position import Position
from string import ascii_lowercase

BOARD_STROKE = 2
LINE_STROKE = 1
LINE_OFFSET = BOARD_STROKE - LINE_STROKE / 2
SQUARE_SIZE = 39  # preferably odd to center text correctly

LABEL_SIZE = 12
FILE_LABEL_OFFSET = 8
RANK_LABEL_OFFSET = 6


class PositionScene(QGraphicsScene):
    def __init__(self, position):
        super().__init__()

        if position.num_ranks > len(ascii_lowercase):
            raise ValueError('Too many ranks in position for GUI')

        self._draw_board(position)
        self._draw_board_labels(position)

    def _draw_board_labels(self, pos):
        font = QFont()
        font.setPointSize(LABEL_SIZE)

        for i in range(pos.num_files):
            file = pos.num_files - i if pos.player_to_move == 0 else i+1

            text = QGraphicsSimpleTextItem(str(file))
            text.setFont(font)
            text.setPos(LINE_OFFSET + (i + 0.5) * SQUARE_SIZE
                        - text.boundingRect().width() / 2,
                        - FILE_LABEL_OFFSET - LABEL_SIZE)

            self.addItem(text)

        for i in range(pos.num_ranks):
            rank = pos.num_ranks - i if pos.player_to_move == 1 else i+1

            text = QGraphicsSimpleTextItem(chr(ord('a') + rank - 1))
            text.setFont(font)
            text.setPos(SQUARE_SIZE * pos.num_files + 2 * LINE_OFFSET +
                        RANK_LABEL_OFFSET,
                        LINE_OFFSET + (i + 0.5) * SQUARE_SIZE
                        - text.boundingRect().height() / 2)

            self.addItem(text)

    def _draw_board(self, pos):
        pen = QPen()
        pen.setWidth(BOARD_STROKE)

        self.addRect(BOARD_STROKE / 2, BOARD_STROKE / 2,
                     SQUARE_SIZE * pos.num_files + BOARD_STROKE - LINE_STROKE,
                     SQUARE_SIZE * pos.num_ranks + BOARD_STROKE - LINE_STROKE,
                     pen)

        pen.setWidth(LINE_STROKE)

        for file in range(1, pos.num_files):
            self.addLine(LINE_OFFSET + SQUARE_SIZE * file, LINE_OFFSET,
                         LINE_OFFSET + SQUARE_SIZE * file,
                         LINE_OFFSET + SQUARE_SIZE * pos.num_ranks,
                         pen)

        for rank in range(1, pos.num_ranks):
            self.addLine(LINE_OFFSET,
                         LINE_OFFSET + SQUARE_SIZE * rank,
                         LINE_OFFSET + SQUARE_SIZE * pos.num_files,
                         LINE_OFFSET + SQUARE_SIZE * rank,
                         pen)


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
