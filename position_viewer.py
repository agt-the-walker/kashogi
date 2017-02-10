#!/usr/bin/env python3

import signal
import sys

from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QBrush, QFont, QFontMetrics, QPainter, QPen, QTransform
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, \
                            QGraphicsSimpleTextItem, QGraphicsItemGroup, \
                            QGraphicsItem

from pieces import Pieces
from position import Position
from coordinates import BOARD_STROKE, LINE_OFFSET, LINE_STROKE, SQUARE_SIZE, \
                        Coordinates

PIECE_FONT = 'Sans'
PIECE_SIZE = 32

PIECE_IN_HAND_SIZE = 24
PIECE_IN_HAND_OFFSET = 19
NUM_IN_HAND_SIZE = 12
NUM_IN_HAND_OFFSET = 8

LABEL_FONT = 'Sans'
LABEL_SIZE = 16
LABEL_OFFSET = 6

GHOST_OPACITY = 0.4


class QGraphicsItemParent(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self._data = {}

    def boundingRect(self, *args):
        return QRectF()

    def paint(self, *args):
        pass

    def get(self, key):
        return self._data.get(key)

    def put(self, key, value):
        self._data[key] = value


class QGraphicsPieceItem(QGraphicsSimpleTextItem):
    def __init__(self, text, parent, position, square):
        super().__init__(text, parent)
        self._position = position
        self._coordinates = Coordinates(position.num_files, position.num_ranks)

        self._square = square
        self._ghost = None

    @property
    def square(self):
        return self._square

    def mousePressEvent(self, event):
        if (self.flags() & QGraphicsItem.ItemIsMovable) and \
           event.button() == Qt.LeftButton:
            self._ghost = self.scene().draw_board_piece(self._square, True)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self._ghost:
            self.scene().removeItem(self._ghost)
            self._ghost = None

            position = self._position
            player = self._position.player_to_move
            square = self._square
            dest_square = self._coordinates.pos_to_square(self.pos(), self,
                                                          player)

            if dest_square not in position.legal_moves_from_square(square):
                # restore initial position
                self.setPos(self._coordinates.square_to_pos(square, self,
                                                            player))
            else:
                self.scene().move(square, dest_square)


class QGraphicsDropItem(QGraphicsSimpleTextItem):
    def __init__(self, text, parent, position, index, abbrev, board_pieces):
        super().__init__(text, parent)
        self._position = position
        self._coordinates = Coordinates(position.num_files, position.num_ranks)

        self._index = index
        self._abbrev = abbrev
        self._board_pieces = board_pieces
        self._ghost = None

    @property
    def abbrev(self):
        return self._abbrev

    def mousePressEvent(self, event):
        if (self.flags() & QGraphicsItem.ItemIsMovable) and \
           event.button() == Qt.LeftButton:
            player = self._position.player_to_move
            self._ghost = self.scene().draw_piece_in_hand(player, self._index,
                                                          self._abbrev, True)
            self._old_pos = self.pos()
            self.setScale(PIECE_SIZE / PIECE_IN_HAND_SIZE)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self._ghost:
            self.scene().removeItem(self._ghost)
            self._ghost = None

            player = self._position.player_to_move
            pos = self._board_pieces.mapToScene(self.scenePos())
            if player == 1:
                pos -= QPointF(self.sceneBoundingRect().width(),
                               self.sceneBoundingRect().height())
            dest_square = self._coordinates.pos_to_square(pos, self, player)

            if dest_square not in \
                    position.legal_drops_with_piece(self._abbrev):
                # restore initial position and size
                self.setPos(self._old_pos)
                self.setScale(1)
            else:
                self.scene().drop(self._abbrev, dest_square)


class PositionScene(QGraphicsScene):
    def __init__(self, position):
        super().__init__()
        self._position = position
        self._coordinates = Coordinates(position.num_files, position.num_ranks)
        self.bottom_player = self.player_to_move()

        self._draw_board_grid()
        self._draw_board_pieces()

        self._redraw_board_labels()
        self._has_board_labels = True

        self._hands = [None] * Position.NUM_PLAYERS
        for player in range(Position.NUM_PLAYERS):
            self._draw_hand(player)
        self._update_hands()

        self.prepare_next_move()

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

    def prepare_next_move(self):
        position = self._position

        for piece_item in self._board_pieces.childItems():
            piece = position.get(piece_item.square)
            abbrev = piece.upper()
            player = 0 if abbrev == piece else 1

            self._update_movable(
                player, piece_item,
                lambda: position.legal_moves_from_square(piece_item.square))

        for player in range(Position.NUM_PLAYERS):
            for drop_item in self._hands[player].childItems():
                if type(drop_item) is not QGraphicsDropItem:
                    continue

                self._update_movable(
                    player, drop_item,
                    lambda: position.legal_drops_with_piece(drop_item.abbrev))

        if self.views():
            self.views()[0].update_title()

    def _update_movable(self, player, item, generator):
        if player == self.player_to_move():
            try:
                next(generator())
                item.setFlag(QGraphicsItem.ItemIsMovable)
                return
            except StopIteration:
                pass

        item.setFlag(QGraphicsItem.ItemIsMovable, False)

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
        self._board_pieces = QGraphicsItemParent()
        self._board_pieces.setTransformOriginPoint(
                self._board.boundingRect().center())

        position = self._position

        for file in range(1, position.num_files+1):
            for rank in range(1, position.num_ranks+1):
                square = ((file, rank))
                piece = position.get(square)
                if piece:
                    self._board_pieces.put(square,
                                           self.draw_board_piece(square))

        self._update_board_orientation()
        self.addItem(self._board_pieces)

    def draw_board_piece(self, square, ghost=False):
        position = self._position

        piece = position.get(square)
        abbrev = piece.upper()
        kanji = position.pieces.kanji(abbrev)

        font = QFont(PIECE_FONT)
        font.setPixelSize(PIECE_SIZE)

        text = QGraphicsPieceItem(kanji, self._board_pieces, position, square)
        text.setFont(font)

        if position.pieces.is_promoted(abbrev):
            text.setBrush(QBrush(Qt.red))

        player = 0 if abbrev == piece else 1
        if player == 1:
            text.setTransformOriginPoint(text.boundingRect().center())
            text.setRotation(180)
        if ghost:
            text.setOpacity(GHOST_OPACITY)

        text.setPos(self._coordinates.square_to_pos(square, text, player))

        return text

    def move(self, square, dest_square):
        player = self.player_to_move()

        # XXX: show a dialog box instead of auto-promoting
        promotions = position.promotions(square, dest_square)
        position.move(square, dest_square, promotions[0])

        piece_item = self._board_pieces.get(square)
        self.removeItem(piece_item)
        self._board_pieces.put(square, None)

        captured_piece_item = self._board_pieces.get(dest_square)
        if captured_piece_item:
            self.removeItem(captured_piece_item)
            self._redraw_hand(player)

        self._board_pieces.put(dest_square, self.draw_board_piece(dest_square))

        self.prepare_next_move()

    def drop(self, abbrev, dest_square):
        player = self.player_to_move()
        position.drop(abbrev, dest_square)

        self._redraw_hand(player)
        self._board_pieces.put(dest_square, self.draw_board_piece(dest_square))

        self.prepare_next_move()

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
            text = QGraphicsSimpleTextItem(Coordinates.rank_label(rank))
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
                [fm.width(Coordinates.rank_label(rank)) for rank in
                 range(1, self._position.num_ranks+1)])

    def _redraw_hand(self, player):
        self.removeItem(self._hands[player])
        self._draw_hand(player)
        self._update_hands()

        self.setSceneRect(self.itemsBoundingRect())  # since hand may shrink
        self.views()[0].resize()                     # or grow

    def _draw_hand(self, player):
        self._hands[player] = QGraphicsItemParent()

        position = self._position
        hand = position.in_hand(player)

        index = 0
        for abbrev in reversed(position.droppable_pieces):
            if abbrev in hand:
                self._hands[player].put(
                        abbrev,
                        self.draw_piece_in_hand(player, index, abbrev))
                index += 1

        self.addItem(self._hands[player])

    def draw_piece_in_hand(self, player, index, abbrev, ghost=False):
        position = self._position
        kanji = position.pieces.kanji(abbrev)

        column, row = divmod(index, position.num_ranks - 1)
        row = (position.num_ranks - 1) - row  # 0 is bottom row

        font = QFont(PIECE_FONT)

        text = QGraphicsDropItem(kanji, self._hands[player], position, index,
                                 abbrev, self._board_pieces)
        font.setPixelSize(PIECE_IN_HAND_SIZE)
        text.setFont(font)
        text.setPos(column * SQUARE_SIZE, row * SQUARE_SIZE)
        text.setTransformOriginPoint(text.boundingRect().center())
        if ghost:
            text.setOpacity(GHOST_OPACITY)
            return text

        num = QGraphicsSimpleTextItem(str(position.in_hand(player)[abbrev]),
                                      self._hands[player])
        font.setPixelSize(NUM_IN_HAND_SIZE)
        num.setFont(font)
        num.setPos((column + 1) * SQUARE_SIZE - num.boundingRect().width()
                   - NUM_IN_HAND_OFFSET,
                   (row + 1) * SQUARE_SIZE - num.boundingRect().height())

        return text

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

        self.setFrameStyle(0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.resize(1)

    def resize(self, zoom_level=None):
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
                self.resize(zoom_level)
        elif event.text() == 'f':
            self.scene().flip_view()
        elif event.text() == 'l':
            self.scene().toggle_board_labels()
            self.resize()

    def update_title(self):
        status = self.scene().status()
        title = '{} - '.format(status) if status else ''
        title += '{}'.format(Position.player_name(
                self.scene().player_to_move()))
        self.setWindowTitle(title)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: {} <sfen>'.format(sys.argv[0]))

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    scene = QGraphicsScene()

    position = Position(sys.argv[1], Pieces())
    view = PositionView(PositionScene(position))
    view.update_title()
    view.show()
    sys.exit(app.exec_())
