#!/usr/bin/env python3

import signal
import sys

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QBrush, QFont, QFontMetrics, QPainter, QPen, QTransform
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, \
                            QGraphicsSimpleTextItem, QGraphicsItemGroup, \
                            QGraphicsItem

from pieces import Pieces
from position import Position
from utils import rank_label

BOARD_STROKE = 2
LINE_STROKE = 1
LINE_OFFSET = BOARD_STROKE - LINE_STROKE / 2
SQUARE_SIZE = 39  # preferably odd to center text correctly

PIECE_FONT = 'Sans'
PIECE_SIZE = 32
PIECE_OFFSET = 1

PIECE_IN_HAND_SIZE = 24
PIECE_IN_HAND_OFFSET = 19
NUM_IN_HAND_SIZE = 12
NUM_IN_HAND_OFFSET = 8

LABEL_FONT = 'Sans'
LABEL_SIZE = 16
LABEL_OFFSET = 6


class QGraphicsItemParent(QGraphicsItem):
    def boundingRect(self, *args):
        return QRectF()

    def paint(self, *args):
        pass


class PositionScene(QGraphicsScene):
    def __init__(self, position):
        super().__init__()
        self.bottom_player = position.player_to_move

        self._position = position
        self._draw_board_grid()
        self._draw_board_pieces()

        self._redraw_board_labels()
        self._has_board_labels = True

        self._hands = [None] * Position.NUM_PLAYERS
        for player in range(Position.NUM_PLAYERS):
            self._draw_hand(player)
        self._update_hands()

    def player_to_move(self):
        return self._position.player_to_move

    def status(self):
        return self._position.status()

    def flip_view(self):
        self.bottom_player = Position.NUM_PLAYERS - self.bottom_player - 1
        self._update_board_orientation()

        if self._has_board_labels:
            self.removeItem(self._file_labels)
            self.removeItem(self._rank_labels)
            self._redraw_board_labels()

        self._update_hands()

        self.setSceneRect(self.itemsBoundingRect())

    def _update_board_orientation(self):
        self._board_pieces.setRotation(self.bottom_player * 180)

    def _update_hands(self):
        for player in range(Position.NUM_PLAYERS):
            if player == self.bottom_player:
                x = self._board.boundingRect().width() + PIECE_IN_HAND_OFFSET
                if self._has_board_labels:
                    x += self._rank_label_span()
                self._hands[player].setRotation(0)
            else:
                x = -PIECE_IN_HAND_OFFSET
                self._hands[player].setTransformOriginPoint(
                        0, position.num_ranks / 2 * SQUARE_SIZE)
                self._hands[player].setRotation(180)

            self._hands[player].setPos(x, LINE_OFFSET)

    def toggle_board_labels(self):
        if self._has_board_labels:
            self.removeItem(self._file_labels)
            self.removeItem(self._rank_labels)
            self._hands[self.bottom_player].moveBy(-self._rank_label_span(), 0)
        else:
            self._redraw_board_labels()
            self._hands[self.bottom_player].moveBy(self._rank_label_span(), 0)

        self._has_board_labels = not self._has_board_labels

        self.setSceneRect(self.itemsBoundingRect())

    def _draw_board_grid(self):
        pen = QPen()
        pen.setWidth(BOARD_STROKE)

        position = self._position

        board = self.addRect(
            BOARD_STROKE / 2, BOARD_STROKE / 2,
            SQUARE_SIZE * position.num_files + BOARD_STROKE - LINE_STROKE,
            SQUARE_SIZE * position.num_ranks + BOARD_STROKE - LINE_STROKE,
            pen)

        pen.setWidth(LINE_STROKE)

        for file in range(1, position.num_files):
            self.addLine(
                LINE_OFFSET + SQUARE_SIZE * file, LINE_OFFSET,
                LINE_OFFSET + SQUARE_SIZE * file,
                LINE_OFFSET + SQUARE_SIZE * position.num_ranks,
                pen)

        for rank in range(1, position.num_ranks):
            self.addLine(
                LINE_OFFSET, LINE_OFFSET + SQUARE_SIZE * rank,
                LINE_OFFSET + SQUARE_SIZE * position.num_files,
                LINE_OFFSET + SQUARE_SIZE * rank,
                pen)

        self._board = board

    def _draw_board_pieces(self):
        font = QFont(PIECE_FONT)
        font.setPixelSize(PIECE_SIZE)

        self._board_pieces = QGraphicsItemParent()
        self._board_pieces.setTransformOriginPoint(
                self._board.boundingRect().center())

        position = self._position

        for file in range(1, position.num_files+1):
            for rank in range(1, position.num_ranks+1):
                square = ((file, rank))
                piece = position.get(square)
                if piece:
                    self._draw_board_piece(font, piece, square)

        self._update_board_orientation()
        self.addItem(self._board_pieces)

    def _draw_board_piece(self, font, piece, square):
        position = self._position

        abbrev = piece.upper()
        kanji = position.pieces.kanji(abbrev)

        text = QGraphicsSimpleTextItem(kanji, self._board_pieces)
        text.setFont(font)

        if position.pieces.is_promoted(abbrev):
            text.setBrush(QBrush(Qt.red))

        player = 0 if abbrev == piece else 1
        piece_offset = PIECE_OFFSET
        if player == 1:
            text.setTransformOriginPoint(text.boundingRect().center())
            text.setRotation(180)
            piece_offset = -piece_offset

        file, rank = square

        text.setPos(LINE_OFFSET
                    + (self._position.num_files - file + 0.5) * SQUARE_SIZE
                    - text.boundingRect().width() / 2,
                    LINE_OFFSET + (rank - 0.5) * SQUARE_SIZE
                    + piece_offset - text.boundingRect().height() / 2)

    def _redraw_board_labels(self):
        font = QFont(LABEL_FONT)
        font.setPixelSize(LABEL_SIZE)

        self._compute_max_label_width(font)

        self._file_labels = QGraphicsItemGroup()
        self._rank_labels = QGraphicsItemGroup()

        position = self._position

        for file in range(1, position.num_files+1):
            text = QGraphicsSimpleTextItem(str(file))
            text.setFont(font)
            text.setPos(self._x(file) * SQUARE_SIZE
                        - text.boundingRect().width() / 2, 0)

            self._file_labels.addToGroup(text)

        self._file_labels.setPos(LINE_OFFSET + 0.5 * SQUARE_SIZE,
                                 - LABEL_OFFSET - LABEL_SIZE)

        for rank in range(1, position.num_ranks+1):
            text = QGraphicsSimpleTextItem(rank_label(rank))
            text.setFont(font)
            text.setPos((self._max_label_width
                         - text.boundingRect().width()) / 2,
                        (self._y(rank) * SQUARE_SIZE
                         - text.boundingRect().height() / 2))

            self._rank_labels.addToGroup(text)

        self._rank_labels.setPos(self._board.boundingRect().width()
                                 + LABEL_OFFSET,
                                 LINE_OFFSET + 0.5 * SQUARE_SIZE)

        self.addItem(self._file_labels)
        self.addItem(self._rank_labels)

    def _compute_max_label_width(self, font):
        if hasattr(self, '_max_label_width'):
            return

        fm = QFontMetrics(font)
        self._max_label_width = max(
                [fm.width(rank_label(rank)) for rank in
                 range(1, self._position.num_ranks+1)])

    def _draw_hand(self, player):
        font = QFont(PIECE_FONT)

        self._hands[player] = QGraphicsItemParent()

        position = self._position
        hand = position.in_hand(player)

        index = 0
        for abbrev in reversed(position.droppable_pieces):
            if abbrev in hand:
                self._draw_piece_in_hand(font, player, index, abbrev)
                index += 1

        self.addItem(self._hands[player])

    def _draw_piece_in_hand(self, font, player, index, abbrev):
        position = self._position
        kanji = position.pieces.kanji(abbrev)

        column, row = divmod(index, position.num_ranks - 1)
        row = (position.num_ranks - 1) - row  # 0 is bottom row

        piece = QGraphicsSimpleTextItem(kanji, self._hands[player])
        font.setPixelSize(PIECE_IN_HAND_SIZE)
        piece.setFont(font)
        piece.setPos(column * SQUARE_SIZE, row * SQUARE_SIZE)

        num = QGraphicsSimpleTextItem(str(position.in_hand(player)[abbrev]),
                                      self._hands[player])
        font.setPixelSize(NUM_IN_HAND_SIZE)
        num.setFont(font)
        num.setPos((column + 1) * SQUARE_SIZE - num.boundingRect().width()
                   - NUM_IN_HAND_OFFSET,
                   (row + 1) * SQUARE_SIZE - num.boundingRect().height())

    def _rank_label_span(self):
        return LABEL_OFFSET + self._max_label_width

    def _x(self, file):
        return self._position.num_files - file if self.bottom_player == 0 \
                                               else file-1

    def _y(self, rank):
        return self._position.num_ranks - rank if self.bottom_player == 1 \
                                               else rank-1


class PositionView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)

        status = scene.status()
        title = '{} - '.format(status) if status else ''
        title += '{}'.format(Position.player_name(scene.player_to_move()))
        self.setWindowTitle(title)

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
