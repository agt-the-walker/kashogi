#!/usr/bin/env python3

import signal
import svgwrite
import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QShortcut

from pieces import Pieces
from position import Position

BOARD_STROKE = 2
LINE_STROKE = 1
LINE_OFFSET = BOARD_STROKE - LINE_STROKE / 2
SQUARE_SIZE = 39  # preferably odd to center text correctly

LABEL_SIZE = 16
FILE_LABEL_OFFSET = 7
FILE_LABEL_HEIGHT = LABEL_SIZE + FILE_LABEL_OFFSET


class PositionView(QWebEngineView):
    def __init__(self, position):
        super().__init__()
        self._position = position

        for key in range(1, 10):
            shortcut = QShortcut(str(key), self)
            shortcut.activated.connect(self.on_key)

        svg = self._position_to_svg()
        self.setHtml(svg)
        self.resize(self._board_width(), self._board_height())
        self.show()

    @pyqtSlot()
    def on_key(self):
        zoom_level = int(chr(self.sender().key()[0]))
        self.resize(zoom_level * self._board_width(),
                    zoom_level * self._board_height())

    def _position_to_svg(self):
        dwg = svgwrite.Drawing(viewBox='0 0 {} {}'.format(
                self._board_width(), self._board_height()))
        dwg.add(dwg.style(
            "body {\n"
            "  margin: 0;\n"
            "}\n"
            "text {\n"
            "  text-anchor: middle;\n"
            "}\n"
            "#board {\n"
            "  fill: none;\n"
            "  stroke: black;\n"
            "}\n"))

        self._draw_board_labels(dwg)
        self._draw_board(dwg)

        return dwg.tostring()

    def _draw_board_labels(self, dwg):
        pos = self._position

        for i in range(pos.num_files):
            file = pos.num_files - i if pos.player_to_move == 0 else i+1
            dwg.add(dwg.text(file,
                             insert=(LINE_OFFSET + (i + 0.5) * SQUARE_SIZE,
                                     LABEL_SIZE)))

    def _draw_board(self, dwg):
        position = self._position

        b = dwg.g(id='board',
                  transform='translate(0, {})'.format(FILE_LABEL_HEIGHT))

        b.add(dwg.rect((BOARD_STROKE / 2, BOARD_STROKE / 2),
                       ((SQUARE_SIZE * position.num_files +
                         BOARD_STROKE - LINE_STROKE),
                        (SQUARE_SIZE * position.num_ranks +
                         BOARD_STROKE - LINE_STROKE)),
                       stroke_width=BOARD_STROKE))

        for file in range(1, position.num_files):
            b.add(dwg.line((LINE_OFFSET + SQUARE_SIZE * file,
                            LINE_OFFSET),
                           (LINE_OFFSET + SQUARE_SIZE * file,
                            LINE_OFFSET + SQUARE_SIZE * position.num_ranks),
                           stroke_width=LINE_STROKE))

        for rank in range(1, position.num_ranks):
            b.add(dwg.line((LINE_OFFSET,
                            LINE_OFFSET + SQUARE_SIZE * rank),
                           (LINE_OFFSET + SQUARE_SIZE * position.num_files,
                            LINE_OFFSET + SQUARE_SIZE * rank),
                           stroke_width=LINE_STROKE))

        dwg.add(b)

    def _board_width(self):
        return SQUARE_SIZE * self._position.num_files + BOARD_STROKE * 2 \
               - LINE_STROKE

    def _board_height(self):
        return SQUARE_SIZE * self._position.num_ranks + BOARD_STROKE * 2 \
               - LINE_STROKE + FILE_LABEL_HEIGHT


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: {} <sfen>'.format(sys.argv[0]))

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    position = Position(sys.argv[1], Pieces())
    app = QApplication(sys.argv)
    view = PositionView(position)
    sys.exit(app.exec_())
