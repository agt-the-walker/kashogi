#!/usr/bin/env python3

import unittest

from position import Position


class PositionTestCase(unittest.TestCase):
    def test_standard_shogi(self):
        # thanks http://shogi.typepad.jp/brainstorm/2007/01/post_11a0.html
        self.check('8l/1l+R2P3/p2pBG1pp/kps1p4/Nn1P2G2/P1P1P2PP/1PS6/1KSG3+r1'
                   '/LN2+p3L w Sbgn3p 124', 9, 9)

    def test_tiny_board(self):
        with self.assertRaisesRegex(ValueError, 'Too few ranks: 2 <'):
            Position('k2/2K b -')
        with self.assertRaisesRegex(ValueError, 'Too few files: 2 <'):
            Position('k1/2/1K b -')

    def test_invalid_piece(self):
        with self.assertRaisesRegex(ValueError, 'Invalid piece on board: Z'):
            Position('k1Z/3/2K b -')

    def test_too_many_royals(self):
        with self.assertRaisesRegex(ValueError,
                                    'Too many royal pieces for white'):
            Position('k1k/3/2K b -')
        with self.assertRaisesRegex(ValueError,
                                    'Too many royal pieces for black'):
            Position('r2/3/K1K b -')

    def test_too_many_pawns_or_swallows_on_file(self):
        with self.assertRaisesRegex(ValueError,
                                    'Too many P for white on file 3'):
            Position('3/2p/2p/P1P b -')
        with self.assertRaisesRegex(ValueError,
                                    "Too many S' for black on file 2"):
            Position("s'2/s'S'1/1S'1/1S'1 b -")
        # pawns and swallows don't share constraints though
        self.check("2p/2s'/2s'/K2 b -", 4, 3)

    def test_no_legal_moves_on_subsequent_turns(self):
        with self.assertRaisesRegex(ValueError,
                                    'L for black found on 1st furthest rank'):
            Position('k1L/3/1K1 b -')
        with self.assertRaisesRegex(ValueError,
                                    'N for white found on 1st furthest rank'):
            Position('k2/3/3/1Kn b -')
        with self.assertRaisesRegex(ValueError,
                                    'N for black found on 2nd furthest rank'):
            Position('k2/1N1/3/1K1 b -')

    def test_missing_plies_on_minishogi(self):
        self.check('rbsgk/4p/5/P4/KGSBR b -', 5, 5)

    def test_wrong_plies(self):
        with self.assertRaisesRegex(ValueError, 'Invalid SFEN'):
            Position('rbsgk/4p/5/P4/KGSBR w - 0')

    def test_invalid_piece_in_hand(self):
        with self.assertRaisesRegex(ValueError, 'Invalid piece in hand: Z'):
            Position('k2/3/2K b PZ')
        with self.assertRaisesRegex(ValueError, 'Invalid piece in hand: z'):
            Position('k2/3/2K b Pp2z')

    def test_royal_piece_in_hand(self):
        with self.assertRaisesRegex(ValueError, 'Royal piece in hand: K'):
            Position('k2/3/2K b PK')
        with self.assertRaisesRegex(ValueError, 'Royal piece in hand: k'):
            Position('k2/3/2K b Pp2k')

    def test_in_check(self):
        self.check('k2/1p1/L2 w -', expected_status='check')

    def test_in_double_check(self):
        self.check('k2/1B1/3/L2 w -', 4, 3, expected_status='check')

    def test_elementary_checkmate(self):
        self.check('R1k/3/b1K w -', expected_status='checkmate')  # with rook
        self.check('2k/1g1/2K b -', expected_status='checkmate')  # with gold

    def test_real_checkmate(self):
        # thanks http://brainking.com/en/ArchivedGame?g=3748461
        self.check('1bb2/sG1R1/KP2G/P2S1/1r1k1 b -', 5, 5,
                   expected_status='checkmate')
        # thanks http://brainking.com/en/ArchivedGame?g=3748125
        self.check('2rkB/BG3/2gs1/Pg3/K2PR b -', 5, 5,
                   expected_status='checkmate')
        # thanks http://brainking.com/en/ArchivedGame?g=3739393
        self.check('2r1k/B3p/P1gb1/G2s1/2K1R b S', 5, 5,
                   expected_status='checkmate')

    def test_block_check_by_cloud_eagle(self):
        # since it has a limited range (3) diagonally forward
        self.check('ce@5/6/5K/6/1R3k w -', 5, 6, expected_status='checkmate')
        self.check('6/1ce@4/5K/6/1R3k w -', 5, 6, expected_status='check')

    def test_elementary_stalemate(self):
        self.check("2k/3/KQ'1 w -", expected_status='stalemate')  # with queen
        self.check('2k/1r1/K2 b -', expected_status='stalemate')  # with rook
        self.check('3/kbK/3 b -', expected_status='stalemate')    # with bishop

    def test_simple_stalemate(self):
        # thanks https://en.wikipedia.org/wiki/Stalemate#Simple_examples
        self.check('KB1r/4/1k2 b -', 3, 4, expected_status='stalemate')
        self.check("2K/1Q'1/p2/k2 w -", 4, 3, expected_status='stalemate')

    def test_adjacent_kings(self):
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by K'):
            Position('k2/1K1/3 b -')

    def test_opponent_in_check(self):
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by L'):
            Position('k2/1p1/L2 b -')
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by R'):
            Position('k2/1p1/R2 b -')
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by S'):
            Position('k2/sp1/K2 w -')

    def test_opponent_not_in_check(self):
        self.check('k2/p2/R2 b -')    # found one of his pieces
        self.check('k2/FC@2/R2 b -')  # wrong orientation of closest piece
        self.check('k2/1p1/B2 b -')   # wrong orientation
        self.check('k2/1p1/G2 b -')   # out of range

    def test_opponent_in_double_check(self):
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by [BL]'):
            Position('k2/1B1/3/L2 b -')

    def test_opponent_in_check_by_jumping_pieces(self):
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by N'):
            Position('n2/PPP/1K1 w -')
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by TF'):
            Position('tf@2/PPP/2K w -')

    def test_opponent_in_check_by_cloud_eagle(self):
        # since it has a limited range (3) diagonally forward
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by CE'):
            Position('k4/5/5/3CE@1/5 b -')     # just in range
        self.check('k4/5/5/5/4CE@ b -', 5, 5)  # just out of range

    def test_opponent_in_check_by_quails(self):
        # since they are L-R asymmetrical
        with self.assertRaisesRegex(ValueError,
                                    "Opponent already in check by L'"):
            Position("L'2/3/2k b -")
        self.check("2L'/3/k2 b -")   # L-R swapped
        with self.assertRaisesRegex(ValueError,
                                    "Opponent already in check by R'"):
            Position("2R'/3/k2 b -")
        self.check("R'2/3/2k b -")   # L-R swapped

    def test_tori_wa_pieces_on_narrow_board(self):
        self.check("k/p'p'sc@/p'1P'/P'P'SC@/K b RFF@11SC@p1n'p'2rr@", 5, 3,
                   "k2/p'p'sc@/p'1P'/P'P'SC@/K2 b RFF@11SC@pn'p'2rr@",
                   expected_status='check')

    def check(self, sfen, expected_num_ranks=3, expected_num_files=3,
              expected_sfen=None, expected_status=None):
        position = Position(sfen)
        self.assertEqual(position.num_ranks, expected_num_ranks)
        self.assertEqual(position.num_files, expected_num_files)
        if not expected_sfen:
            expected_sfen = sfen
        self.assertEqual(str(position), expected_sfen)
        self.assertEqual(position.status(), expected_status)


if __name__ == '__main__':
    unittest.main()
