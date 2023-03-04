#!/usr/bin/env python3

import argparse
import signal
import sys

from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QBrush, QColor, QFont, QFontMetrics, QPainter, QPen, \
                        QTransform
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, \
                            QGraphicsSimpleTextItem, QGraphicsItemGroup, \
                            QGraphicsItem, QGraphicsRectItem, QMessageBox

from game import Game
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
    def __init__(self, text, parent, game, square):
        super().__init__(text, parent)
        self._game = game
        self._coordinates = Coordinates(game.num_files, game.num_ranks)

        self._square = square
        self._ghost = None

    @property
    def square(self):
        return self._square

    def mousePressEvent(self, event):
        if (self.flags() & QGraphicsItem.ItemIsMovable) and \
           event.button() == Qt.LeftButton:
            game = self._game

            self._ghost = self.scene().draw_board_piece(self._square, True)
            self._legal_moves = \
                list(game.legal_moves_from_square(self._square))
            self.scene().highlight(self._legal_moves, True)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self._ghost:
            self.scene().removeItem(self._ghost)
            self._ghost = None
            self.scene().highlight(self._legal_moves, False)

            player = self._game.player_to_move
            square = self._square
            dest_square = self._coordinates.pos_to_square(self.pos(), self,
                                                          player)

            if dest_square not in self._legal_moves:
                # restore initial position
                self.setPos(self._coordinates.square_to_pos(square, self,
                                                            player))
                self.scene().refresh()
            else:
                self.scene().move(square, dest_square)


class QGraphicsDropItem(QGraphicsSimpleTextItem):
    def __init__(self, text, parent, game, index, abbrev, board_pieces):
        super().__init__(text, parent)
        self._game = game
        self._coordinates = Coordinates(game.num_files, game.num_ranks)

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
            player = self._game.player_to_move
            game = self._game

            self._ghost = self.scene().draw_piece_in_hand(player, self._index,
                                                          self._abbrev, True)
            self._legal_drops = \
                list(game.legal_drops_with_piece(self._abbrev))
            self.scene().highlight(self._legal_drops, True)
            self._old_pos = self.pos()
            self.setScale(PIECE_SIZE / PIECE_IN_HAND_SIZE)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self._ghost:
            self.scene().removeItem(self._ghost)
            self._ghost = None
            self.scene().highlight(self._legal_drops, False)

            player = self._game.player_to_move
            pos = self._board_pieces.mapToScene(self.scenePos())
            if player == 1:
                pos -= QPointF(self.sceneBoundingRect().width(),
                               self.sceneBoundingRect().height())
            dest_square = self._coordinates.pos_to_square(pos, self, player)

            if dest_square not in self._legal_drops:
                # restore initial position and size
                self.setPos(self._old_pos)
                self.setScale(1)
                self.scene().refresh()
            else:
                self.scene().drop(self._abbrev, dest_square)


class GameScene(QGraphicsScene):
    def __init__(self, game, verbose):
        super().__init__()
        self._game = game
        self._verbose = verbose

        self._coordinates = Coordinates(game.num_files, game.num_ranks)
        self.bottom_player = self.player_to_move()

        self._draw_board_grid()
        self._draw_board_squares()
        self._draw_board_pieces()

        self._redraw_board_labels()
        self._has_board_labels = True

        self._hands = [None] * game.NUM_PLAYERS
        for player in range(game.NUM_PLAYERS):
            self._draw_hand(player)
        self._update_hands()

        self._prepare_next_move()

    def player_to_move(self):
        return self._game.player_to_move

    def status(self):
        return self._game.status()

    def flip_view(self):
        self.bottom_player = self._game.NUM_PLAYERS - self.bottom_player - 1
        self._update_board_orientation()

        if self._has_board_labels:
            self.removeItem(self._file_labels)
            self.removeItem(self._rank_labels)
            self._redraw_board_labels()

        self._update_hands()

        self.setSceneRect(self.itemsBoundingRect())

    def _update_board_orientation(self):
        self._board_pieces.setRotation(self.bottom_player * 180)
        self._board_squares.setRotation(self.bottom_player * 180)

    def _update_hands(self):
        for player in range(self._game.NUM_PLAYERS):
            if player == self.bottom_player:
                x = self._board.boundingRect().width() + PIECE_IN_HAND_OFFSET
                if self._has_board_labels:
                    x += self._rank_label_span()
                self._hands[player].setRotation(0)
            else:
                x = -PIECE_IN_HAND_OFFSET
                self._hands[player].setTransformOriginPoint(
                        0, game.num_ranks / 2 * SQUARE_SIZE)
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

        self.refresh()

    def _prepare_next_move(self):
        game = self._game

        for piece_item in self._board_pieces.childItems():
            if type(piece_item) is not QGraphicsPieceItem:
                continue

            piece = game.get(piece_item.square)
            abbrev = piece.upper()
            player = 0 if abbrev == piece else 1

            self._update_movable(
                player, piece_item,
                lambda: game.legal_moves_from_square(piece_item.square))

        for player in range(game.NUM_PLAYERS):
            for drop_item in self._hands[player].childItems():
                if type(drop_item) is not QGraphicsDropItem:
                    continue

                self._update_movable(
                    player, drop_item,
                    lambda: game.legal_drops_with_piece(drop_item.abbrev))

        if self.views():
            self.show_status_and_result()
        if self._verbose:
            print(game.sfen)

    def show_status_and_result(self):
        status = self.status()
        title = '{} - '.format(status) if status else ''
        title += '{}'.format(Position.player_name(self.player_to_move()))
        self.views()[0].setWindowTitle(title)

        winner, result_reason = game.result()
        if winner is None:
            return

        if winner == game.NUM_PLAYERS:
            message = 'Draw'
        else:
            message = '{} won'.format(game.player_name(winner).capitalize())
        message += ' ({})'.format(result_reason)

        QMessageBox.information(None, 'Game result', message)

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

        game = self._game

        self._board = self.addRect(
            BOARD_STROKE / 2, BOARD_STROKE / 2,
            SQUARE_SIZE * game.num_files + BOARD_STROKE - LINE_STROKE,
            SQUARE_SIZE * game.num_ranks + BOARD_STROKE - LINE_STROKE,
            pen)

        pen.setWidth(LINE_STROKE)

        for file in range(1, game.num_files):
            self.addLine(
                LINE_OFFSET + SQUARE_SIZE * file, LINE_OFFSET,
                LINE_OFFSET + SQUARE_SIZE * file,
                LINE_OFFSET + SQUARE_SIZE * game.num_ranks,
                pen)

        for rank in range(1, game.num_ranks):
            self.addLine(
                LINE_OFFSET, LINE_OFFSET + SQUARE_SIZE * rank,
                LINE_OFFSET + SQUARE_SIZE * game.num_files,
                LINE_OFFSET + SQUARE_SIZE * rank,
                pen)

    def _draw_board_squares(self):
        self._board_squares = QGraphicsItemParent()
        self._board_squares.setTransformOriginPoint(
                self._board.boundingRect().center())

        highlight_color = QColor(Qt.yellow).lighter()
        for file in range(1, game.num_files+1):
            for rank in range(1, game.num_ranks+1):
                square = file, rank
                rect = QGraphicsRectItem(
                        self._coordinates.square_to_rect(square),
                        self._board_squares)
                rect.setPen(QPen(Qt.NoPen))
                rect.setBrush(QBrush(highlight_color))
                rect.hide()
                self._board_squares.put(square, rect)

        self.addItem(self._board_squares)

    def highlight(self, squares, visible):
        for square in squares:
            self._board_squares.get(square).setVisible(visible)

    def _draw_board_pieces(self):
        self._board_pieces = QGraphicsItemParent()
        self._board_pieces.setTransformOriginPoint(
                self._board.boundingRect().center())

        game = self._game

        for file in range(1, game.num_files+1):
            for rank in range(1, game.num_ranks+1):
                square = file, rank
                piece = game.get(square)
                if piece:
                    self._board_pieces.put(square,
                                           self.draw_board_piece(square))

        self._update_board_orientation()
        self.addItem(self._board_pieces)

    def draw_board_piece(self, square, ghost=False):
        game = self._game

        piece = game.get(square)
        abbrev = piece.upper()
        kanji = game.pieces.kanji(abbrev)

        font = QFont(PIECE_FONT)
        font.setPixelSize(PIECE_SIZE)

        text = QGraphicsPieceItem(kanji, self._board_pieces, game, square)
        text.setFont(font)

        if game.pieces.is_promoted(abbrev):
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

        promotions = game.promotions(square, dest_square)
        if promotions == [False, True]:
            promotes = None
        else:
            promotes = promotions[0]
        game.move(square, dest_square, promotes)

        piece_item = self._board_pieces.get(square)
        self.removeItem(piece_item)
        self._board_pieces.put(square, None)

        captured_piece_item = self._board_pieces.get(dest_square)
        if captured_piece_item:
            self.removeItem(captured_piece_item)
            self._redraw_hand(player)

        self.refresh()
        self._board_pieces.put(dest_square, self.draw_board_piece(dest_square))

        if promotes is None:
            promotes = QMessageBox.question(None, 'Optional promotion',
                                            'Promotes?') == QMessageBox.Yes
            game.choose_promotion(promotes)
            if promotes:
                self.removeItem(self._board_pieces.get(dest_square))
                self._board_pieces.put(dest_square,
                                       self.draw_board_piece(dest_square))

        self._prepare_next_move()

    def drop(self, abbrev, dest_square):
        player = self.player_to_move()
        game.drop(abbrev, dest_square)

        self._redraw_hand(player)

        self.refresh()
        self._board_pieces.put(dest_square, self.draw_board_piece(dest_square))

        self._prepare_next_move()

    def refresh(self):
        self.setSceneRect(self.itemsBoundingRect())
        self.views()[0].resize()

    def _redraw_board_labels(self):
        font = QFont(LABEL_FONT)
        font.setPixelSize(LABEL_SIZE)

        self._compute_max_label_width(font)

        self._file_labels = QGraphicsItemGroup()
        self._rank_labels = QGraphicsItemGroup()

        game = self._game

        for file in range(1, game.num_files+1):
            text = QGraphicsSimpleTextItem(str(file))
            text.setFont(font)
            text.setPos(self._x(file) * SQUARE_SIZE
                        - text.boundingRect().width() / 2, 0)

            self._file_labels.addToGroup(text)

        self._file_labels.setPos(LINE_OFFSET + 0.5 * SQUARE_SIZE,
                                 - LABEL_OFFSET - LABEL_SIZE)

        for rank in range(1, game.num_ranks+1):
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
                 range(1, self._game.num_ranks+1)])

    def _redraw_hand(self, player):
        self.removeItem(self._hands[player])
        self._draw_hand(player)
        self._update_hands()

    def _draw_hand(self, player):
        self._hands[player] = QGraphicsItemParent()

        game = self._game
        hand = game.in_hand(player)

        index = 0
        for abbrev in reversed(game.droppable_pieces):
            if abbrev in hand:
                self._hands[player].put(
                        abbrev,
                        self.draw_piece_in_hand(player, index, abbrev))
                index += 1

        self.addItem(self._hands[player])

    def draw_piece_in_hand(self, player, index, abbrev, ghost=False):
        game = self._game
        kanji = game.pieces.kanji(abbrev)

        column, row = divmod(index, game.num_ranks - 1)
        row = (game.num_ranks - 1) - row  # 0 is bottom row

        font = QFont(PIECE_FONT)

        text = QGraphicsDropItem(kanji, self._hands[player], game, index,
                                 abbrev, self._board_pieces)
        font.setPixelSize(PIECE_IN_HAND_SIZE)
        text.setFont(font)
        text.setPos(column * SQUARE_SIZE, row * SQUARE_SIZE)
        text.setTransformOriginPoint(text.boundingRect().center())
        if ghost:
            text.setOpacity(GHOST_OPACITY)
            return text

        num = QGraphicsSimpleTextItem(str(game.in_hand(player)[abbrev]),
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
        return self._game.num_files - file if self.bottom_player == 0 \
                                           else file-1

    def _y(self, rank):
        return self._game.num_ranks - rank if self.bottom_player == 1 \
                                           else rank-1


class GameView(QGraphicsView):
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
        self.setFixedSize(self._zoom_level * int(self.scene().width()),
                          self._zoom_level * int(self.scene().height()))

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
        elif event.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('sfen', help='SFEN position')
    parser.add_argument('--no-try', action='store_true',
                        help='do not apply the Try Rule')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='show SFEN position after each move/drop')
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)

    game = Game(args.sfen, Pieces(), not (args.no_try))
    scene = GameScene(game, args.verbose)
    view = GameView(scene)

    view.show()
    scene.show_status_and_result()
    sys.exit(app.exec_())
