#!/usr/bin/env python3

import signal
import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QShortcut

from pieces import Pieces
from position import Position

BOARD_STROKE = 2
LINE_STROKE = 1
LINE_OFFSET = BOARD_STROKE - LINE_STROKE / 2
SQUARE_SIZE = 40


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
        fragments = []

        fragments.append("""
<svg width="100%" height="100%" viewBox="0 0 {} {}"
     xmlns="http://www.w3.org/2000/svg">
        """.format(self._board_width(), self._board_height()))

        fragments.append("""
  <style text="text/css"><![CDATA[
    body {
      margin: 0;
    }
    #board {
      fill: none;
      stroke: black;
    }
  ]]></style>
  <g id="board">
        """)

        fragments.append(self._board_to_svg())
        fragments.append("""
  </g>
</svg>
        """)

        return ''.join(fragments)

    def _board_to_svg(self):
        position = self._position

        fragments = []

        fragments.append("""
    <rect x="{}" y="{}" width="{}" height="{}" stroke-width="{}"/>
        """.format(BOARD_STROKE / 2,
                   BOARD_STROKE / 2,
                   (SQUARE_SIZE * position.num_files +
                    BOARD_STROKE - LINE_STROKE),
                   (SQUARE_SIZE * position.num_ranks +
                    BOARD_STROKE - LINE_STROKE),
                   BOARD_STROKE))

        for file in range(1, position.num_files):
            fragments.append("""
    <line x1="{}" y1="{}" x2="{}" y2="{}" stroke-width="{}"/>
            """.format(LINE_OFFSET + SQUARE_SIZE * file,
                       LINE_OFFSET,
                       LINE_OFFSET + SQUARE_SIZE * file,
                       LINE_OFFSET + SQUARE_SIZE * position.num_ranks,
                       LINE_STROKE))

        for rank in range(1, position.num_ranks):
            fragments.append("""
    <line x1="{}" y1="{}" x2="{}" y2="{}" stroke-width="{}"/>
            """.format(LINE_OFFSET,
                       LINE_OFFSET + SQUARE_SIZE * rank,
                       LINE_OFFSET + SQUARE_SIZE * position.num_files,
                       LINE_OFFSET + SQUARE_SIZE * rank,
                       LINE_STROKE))

        return '\n'.join(fragments)

    def _board_width(self):
        return SQUARE_SIZE * self._position.num_files + BOARD_STROKE * 2 \
               - LINE_STROKE

    def _board_height(self):
        return SQUARE_SIZE * self._position.num_ranks + BOARD_STROKE * 2 \
               - LINE_STROKE


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: {} <sfen>'.format(sys.argv[0]))

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    position = Position(sys.argv[1], Pieces())
    app = QApplication(sys.argv)
    view = PositionView(position)
    sys.exit(app.exec_())
