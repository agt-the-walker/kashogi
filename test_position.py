#!/usr/bin/env python3

import unittest

from pieces import Pieces
from position import Position


class PositionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._pieces = Pieces()

    def test_standard_shogi_random_position(self):
        # thanks http://shogi.typepad.jp/brainstorm/2007/01/post_11a0.html
        sfen = '8l/1l+R2P3/p2pBG1pp/kps1p4/Nn1P2G2/P1P1P2PP/1PS6/1KSG3+r1/'\
               'LN2+p3L w Sbgn3p'
        # we ignore move count, etc.
        position = self.check(sfen + ' 124', 9, 9, sfen)
        self.assertEqual(position.pieces, self._pieces)
        self.assertEqual(position.droppable_pieces,
                         list(position.STANDARD_HAND_ORDER))
        self.assertEqual(position.player_to_move, 1)
        self.assertEqual(position.get((2, 8)), '+r')
        self.assertEqual(position.in_hand(1), {'B': 1, 'G': 1, 'N': 1, 'P': 3})
        self.assertEqual(position.royal_square(1), (9, 4))

        with self.assertRaisesRegex(ValueError, r'Square \(9, 2\) is empty'):
            next(position.legal_moves_from_square((9, 2)))
        with self.assertRaisesRegex(ValueError,
                                    r'Square \(7, 2\) is not ours'):
            next(position.legal_moves_from_square((7, 2)))

        with self.assertRaisesRegex(ValueError, 'Piece S is not in hand'):
            next(position.legal_drops_with_piece('S'))

        self.assertEqual(set(position.legal_moves_from_square((7, 4))),  # S7d
                         {(8, 3),
                                  (7, 5), (6, 5)})                       # noqa

        self.assertEqual(set(position.legal_moves_from_square((5, 9))),  # +P5i
                         {        (5, 8),                                # noqa
                          (6, 9),         (4, 9)})

        self.assertEqual(set(position.legal_drops_with_piece('P')),      # P*
                         {(7, 1), (4, 1), (3, 1),
                                          (3, 2),
                          (7, 3),         (3, 3),
                                  (4, 4), (3, 4),                        # noqa
                          (7, 5), (4, 5),
                                  (4, 6), (3, 6),
                                  (4, 7), (3, 7),
                                  (4, 8), (3, 8)})

    def test_standard_shogi_shortest_game(self):
        # thanks http://userpages.monmouth.com/~colonel/shortshogi.html
        sfen = 'lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -'
        position = self.check(sfen + ' 1', 9, 9, sfen)

        position.move((7, 7), (7, 6), False)  # 1. P-7f
        position.move((6, 1), (7, 2), False)  # 2. G-7b
        position.move((8, 8), (3, 3), True)   # 3. Bx3c+
        position.move((4, 1), (4, 2), False)  # 4. G-4b
        position.move((3, 3), (4, 2), False)  # 5. +Bx4b
        position.move((5, 1), (6, 1), False)  # 6. K-6a
        position.drop('G', (5, 2))            # 7. G*5b

        final_sfen = 'lnsk2snl/1rg1G+B1b1/pppppp1pp/9/9/2P6/PP1PPPPPP/7R1/'\
                     'LNSGKGSNL w P'
        self.assertEqual(str(position), final_sfen)
        self.assertEqual(position.royal_square(1), (6, 1))
        self.assertEqual(position.status(), 'checkmate')

    def test_tsumeshogi(self):
        # thanks https://en.wikipedia.org/wiki/Tsumeshogi
        position = self.check('3sks3/9/4+P4/9/7+B1/9/9/9/9 b S2rb4g4n17p',
                              9, 9)
        position.move((2, 5), (5, 2), False)  # 1. +B-5b
        position.move((4, 1), (5, 2), False)  # 2. Sx5b
        position.drop('S', (4, 2))            # 3. S*4b

        final_sfen = '3sk4/4sS3/4+P4/9/9/9/9/9/9 w 2r2b4g4n17p'
        self.assertEqual(str(position), final_sfen)
        self.assertEqual(position.status(), 'checkmate')

    def test_tiny_board(self):
        with self.assertRaisesRegex(ValueError, 'Too few ranks: 2 <'):
            self.check('k2/2K b -')
        with self.assertRaisesRegex(ValueError, 'Too few files: 2 <'):
            self.check('k1/2/1K b -')

    def test_invalid_piece(self):
        with self.assertRaisesRegex(ValueError, 'Invalid piece on board: Z'):
            self.check('k1Z/3/2K b -')

    def test_too_many_royals(self):
        with self.assertRaisesRegex(ValueError,
                                    'Too many royal pieces for white'):
            self.check('k1k/3/2K b -')
        with self.assertRaisesRegex(ValueError,
                                    'Too many royal pieces for black'):
            self.check('r2/3/K1K b -')

    def test_too_many_pawns_or_swallows_on_file(self):
        with self.assertRaisesRegex(ValueError,
                                    'Too many P for white on file 1'):
            self.check('3/2p/2p/P1P b -')
        with self.assertRaisesRegex(ValueError,
                                    "Too many S' for black on file 2"):
            self.check("s'2/s'S'1/1S'1/1S'1 b -")
        # pawns and swallows don't share constraints though
        self.check("2p/2s'/2s'/K2 b -", 3, 4)

    def test_no_legal_moves_on_subsequent_turns(self):
        with self.assertRaisesRegex(ValueError,
                                    'L for black found on furthest rank'):
            self.check('k1L/3/1K1 b -')
        with self.assertRaisesRegex(ValueError,
                                    'N for white found on furthest rank'):
            self.check('k2/3/3/1Kn b -')
        with self.assertRaisesRegex(ValueError,
                                    'N for black found on furthest rank'):
            self.check('k2/1N1/3/1K1 b -')

    def test_promotion_zone_too_small(self):
        with self.assertRaisesRegex(ValueError,
                                    'Promotion zone too small for N'):
            self.check('rbsgk/3np/5/P4/KGSBR b -')

    def test_minishogi_starting_position(self):
        self.check('rbsgk/4p/5/P4/KGSBR b -', 5, 5)

    def test_invalid_sfen(self):
        with self.assertRaisesRegex(ValueError, 'Invalid SFEN'):
            self.check('3/3/3 b')    # missing "pieces in hand"
        with self.assertRaisesRegex(ValueError, 'Invalid SFEN'):
            self.check('3/3/3 s -')  # unknown player to move

    def test_invalid_piece_in_hand(self):
        with self.assertRaisesRegex(ValueError, 'Invalid piece in hand: Z'):
            self.check('k2/3/2K b PZ')
        with self.assertRaisesRegex(ValueError, 'Invalid piece in hand: z'):
            self.check('k2/3/2K b Pp2z')

    def test_royal_piece_in_hand(self):
        with self.assertRaisesRegex(ValueError, 'Royal piece in hand: K'):
            self.check('k2/3/2K b PK')
        with self.assertRaisesRegex(ValueError, 'Royal piece in hand: k'):
            self.check('k2/3/2K b Pp2k')

    def test_in_check(self):
        self.check('k2/1p1/L2 w -', expected_status='check')

    def test_in_double_check(self):
        self.check('k2/1B1/3/L2 w -', 3, 4, expected_status='check')

    def test_check_blocked_by_enemy_piece(self):
        self.check('4/+R+P1k/4 w -', 4, 3)

    def test_elementary_checkmate(self):
        self.check('R1k/3/b1K w -', expected_status='checkmate')  # with rook
        self.check('2k/1g1/2K b -', expected_status='checkmate')  # with gold

    def test_elementary_checkmate_with_pawn_drops(self):
        self.check('R1k/3/b1K w p', expected_status='check')        # drop ok
        self.check('R1k/1p1/b1K w p', expected_status='checkmate')  # nifu
        self.check('b1K/3/R1k w 12p', expected_status='checkmate')  # last rank

    def test_elementary_checkmate_with_knight_drops(self):
        # we cannot drop a shogi knight on our last two further ranks
        position = self.check("3/GN'1/K1r/3/1k1 b N", 3, 5,
                              expected_status='check')
        self.assertEqual(set(position.legal_drops_with_piece('N')), {(2, 3)})
        self.check("GN'1/K1r/3/1k1 b N", 3, 4, expected_status='checkmate')

    def test_elementary_checkmate_with_sparrow_drops(self):
        # we can have two sparrows per file at most
        self.check("R1k/1s'1/b1K/3 w s'", 3, 4, expected_status='check')
        self.check("R1k/1s'1/bs'K/3 w s'", 3, 4, expected_status='checkmate')

    def test_pawn_drop_cannot_checkmate_but_other_drops_can_checkmate(self):
        position = self.check("2s/3/1N'K w lp")
        self.assertEqual(set(position.legal_drops_with_piece('P')),
                         {(3, 1), (2, 1),
                          (3, 2), (2, 2)})  # (1, 2) would give checkmate
        self.assertEqual(set(position.legal_drops_with_piece('L')),
                         {(3, 1), (2, 1),
                          (3, 2), (2, 2), (1, 2)})  # (1, 2) checkmates

    def test_pawn_drop_cannot_checkmate_even_when_in_check(self):
        position = self.check('lkb+R/b3/K3 b P', 4, 3, expected_status='check')
        self.assertEqual(set(position.legal_drops_with_piece('P')),
                         set())  # (3, 2) would give checkmate

    def test_pawn_drop_can_check_with_protected_drop(self):
        position = self.check('1k1/3/K2 b P2s')
        self.assertEqual(set(position.legal_drops_with_piece('P')),
                         {(3, 2), (2, 2), (1, 2),
                                  (2, 3), (1, 3)})

    def test_pawn_drop_can_check_with_unprotected_drop(self):
        position = self.check('k2/1p1/2K w p')
        self.assertEqual(set(position.legal_drops_with_piece('P')),
                         {        (1, 1),                                # noqa
                          (3, 2), (1, 2)})  # (1, 2) drop not protected

    def test_pawn_drop_can_check_even_when_in_check(self):
        # similar to test_pawn_drop_cannot_checkmate_even_when_in_check
        #  except that opponent king has a flight square
        position = self.check('1kb+R/b3/K3 b P', 4, 3, expected_status='check')
        self.assertEqual(set(position.legal_drops_with_piece('P')), {(3, 2)})

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
        self.check('ce@5/6/5K/6/1R3k w -', 6, 5, expected_status='checkmate')

        position = self.check('6/1ce@4/5K/6/2R2k w -', 6, 5,
                              expected_status='check')
        self.assertEqual(set(position.legal_moves_from_square((5, 2))),  # CE
                         {(2, 5)})

    def test_elementary_stalemate(self):
        self.check("2k/3/KQ'1 w R", expected_status='stalemate')  # with queen
        self.check('2k/1r1/K2 b -', expected_status='stalemate')  # with rook
        self.check('3/kbK/3 b snp', expected_status='stalemate')  # with bishop

    def test_simple_stalemate(self):
        # thanks https://en.wikipedia.org/wiki/Stalemate#Simple_examples
        self.check('KB1r/4/1k2 b -', 4, 3, expected_status='stalemate')
        self.check("2K/1Q'1/p2/k2 w -", 3, 4, expected_status='stalemate')

    def test_empty_board(self):
        self.check('3/3/3 b -', expected_status='stalemate')
        self.check('3/3/3 b p', expected_status='stalemate')
        self.check('3/3/3 b P')
        self.check('3/3/3 w p')
        self.check('3/3/3 w P', expected_status='stalemate')

    def test_blocked_board(self):
        self.check("SSS/PPP/KN'N' b P", expected_status='stalemate')
        self.check("SSS/PPP/KN'N' w p", expected_status='stalemate')

    def test_adjacent_kings(self):
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by K'):
            self.check('k2/1K1/3 b -')

    def test_opponent_in_check(self):
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by L'):
            self.check('k2/1p1/L2 b -')
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by R'):
            self.check('k2/1p1/R2 b -')
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by S'):
            self.check('k2/sp1/K2 w -')

    def test_opponent_not_in_check(self):
        self.check('k2/p2/R2 b -')    # found one of his pieces
        self.check('k2/FC@2/R2 b -')  # wrong orientation of closest piece
        self.check('k2/1p1/B2 b -')   # wrong orientation
        self.check('k2/1p1/G2 b -')   # out of range

    def test_opponent_in_double_check(self):
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by [BL]'):
            self.check('k2/1B1/3/L2 b -')

    def test_opponent_in_check_by_jumping_pieces(self):
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by N'):
            self.check("n'2/PPP/1K1 w -")
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by TF'):
            self.check('tf@2/PPP/2K w -')

    def test_opponent_in_check_by_cloud_eagle(self):
        # since it has a limited range (3) diagonally forward
        with self.assertRaisesRegex(ValueError,
                                    'Opponent already in check by CE'):
            self.check('k4/5/5/3CE@1/5 b -')     # just in range
        self.check('k4/5/5/5/4CE@ b -', 5, 5)  # just out of range

    def test_opponent_in_check_by_quails(self):
        # since they are L-R asymmetrical
        with self.assertRaisesRegex(ValueError,
                                    "Opponent already in check by L'"):
            self.check("L'2/3/2k b -")
        self.check("2L'/3/k2 b -")   # L-R swapped
        with self.assertRaisesRegex(ValueError,
                                    "Opponent already in check by R'"):
            self.check("2R'/3/k2 b -")
        self.check("R'2/3/2k b -")   # L-R swapped

    def test_tori_wa_pieces_on_narrow_board(self):
        position = self.check(
                "k/p'p'sc@/p'1P'/P'P'SC@/K b FF@11SC@Rn'p'2rr@p1", 3, 5,
                "k2/p'p'sc@/p'1P'/P'P'SC@/K2 b FF@11SC@Rn'p'2rr@p",
                expected_status='check')
        self.assertEqual(position.droppable_pieces,
                         ['FF', "N'", "P'", 'RR', 'SC', 'R', 'P'])

    def test_promotion_choices_for_black(self):
        position = self.check('2k/P2/S1P/NP+B/2N/1N1/G2/3/1K1 b -', 3, 9)

        # already promoted (+B)
        self.assertEqual(position.promotions((1, 4), (2, 3)), [False])

        # no promoted version (G)
        self.assertEqual(position.promotions((3, 7), (3, 6)), [False])

        # should promote (P)
        self.assertEqual(position.promotions((2, 4), (2, 3)), [True, False])
        self.assertEqual(position.promotions((1, 3), (1, 2)), [True, False])
        # must promote (P)
        self.assertEqual(position.promotions((3, 2), (3, 1)), [True])

        # cannot promote (N)
        self.assertEqual(position.promotions((2, 6), (1, 4)), [False])
        # can promote (N)
        self.assertEqual(position.promotions((1, 5), (2, 3)), [False, True])
        # must promote (N)
        self.assertEqual(position.promotions((3, 4), (2, 2)), [True])

        # moves wholly within promotion zone (S)
        self.assertEqual(position.promotions((3, 3), (2, 2)), [False, True])

    def test_promotion_choices_for_white(self):
        position = self.check('2k/3/3/1n1/n2/1n1/r1n/3/2K w -', 3, 9)

        # cannot promote (N)
        self.assertEqual(position.promotions((2, 4), (1, 6)), [False])
        # can promote (N)
        self.assertEqual(position.promotions((3, 5), (2, 7)), [False, True])
        # must promote (N)
        self.assertEqual(position.promotions((2, 6), (3, 8)), [True])
        self.assertEqual(position.promotions((1, 7), (2, 9)), [True])

        # moves out of promotion zone (R)
        self.assertEqual(position.promotions((3, 7), (3, 6)), [True, False])

    def test_promotion_choices_for_lance(self):
        position = self.check('3/3/2L/1L1/L2/3/3/3/K2 b -', 3, 9)

        # can promote
        self.assertEqual(position.promotions((3, 5), (3, 3)), [False, True])
        # should promote
        self.assertEqual(position.promotions((2, 4), (2, 2)), [True, False])
        self.assertEqual(position.promotions((1, 3), (1, 2)), [True, False])
        # must promote
        self.assertEqual(position.promotions((1, 3), (1, 1)), [True])

    def test_promotion_choices_for_flying_cock(self):
        position = self.check('2k/FC@2/2FC@/1FC@1/3/3/3/3/3 b -', 3, 9)

        # should promote
        self.assertEqual(position.promotions((2, 4), (2, 3)), [True, False])
        self.assertEqual(position.promotions((1, 3), (1, 2)), [True, False])
        self.assertEqual(position.promotions((3, 2), (3, 1)), [True, False])

    def test_pawn_drops(self):
        position = self.check('2k/3/K2 b 2Pp')
        position.drop('P', (1, 3))
        self.assertEqual(str(position), '2k/3/K1P w Pp')
        position.drop('P', (2, 2))
        self.assertEqual(str(position), '2k/1p1/K1P b P')

        with self.assertRaisesRegex(ValueError, 'Illegal drop'):
            position.drop('P', (1, 2))  # nifu (due to previous drop)
        position.drop('P', (2, 3))
        self.assertEqual(str(position), '2k/1p1/KPP w -')

    def test_other_drop(self):
        position = self.check('2k/3/K2 w 3s')
        position.drop('S', (2, 2))
        self.assertEqual(str(position), '2k/1s1/K2 b 2s')
        self.assertEqual(position.status(), 'check')

    def test_drop_with_new_directions(self):
        position = self.check('1k1/3/3/3/K2 b N', 3, 5)
        self.assertEqual(position.droppable_pieces, ['N'])
        position.drop('N', (1, 3))
        self.assertEqual(str(position), '1k1/3/2N/3/K2 w -')
        self.assertEqual(position.status(), 'check')

    def test_king_move(self):
        position = self.check('1k1/2P/1K1 b P')

        position.move((2, 3), (3, 3), False)  # simple move
        self.assertEqual(str(position), '1k1/2P/K2 w P')
        self.assertEqual(position.royal_square(0), (3, 3))

        position.move((2, 1), (1, 2), False)  # king captures pawn
        self.assertEqual(str(position), '3/2k/K2 b Pp')
        self.assertEqual(position.royal_square(1), (1, 2))

        position.drop('P', (1, 3))  # no nifu (due to previous capture)
        self.assertEqual(str(position), '3/2k/K1P w p')
        self.assertEqual(position.status(), 'check')

        with self.assertRaisesRegex(ValueError, 'Illegal move'):
            position.move((1, 2), (2, 2), False)  # adjacent kings
        with self.assertRaisesRegex(ValueError, 'Illegal promotion'):
            position.move((1, 2), (1, 3), True)  # king cannot promote

    def test_pawn_move(self):
        position = self.check('2k/1p1/K2 w p')

        position.move((2, 2), (2, 3), True)  # promotes
        self.assertEqual(str(position), '2k/3/K+p1 b p')
        self.assertEqual(position.status(), 'check')

        position.move((3, 3), (3, 2), False)  # king moves
        self.assertEqual(str(position), '2k/K2/1+p1 w p')

        position.drop('P', (2, 2))  # no nifu (since pawn has promoted)

    def test_capture_promoted_piece_while_promoting(self):
        position = self.check('1+rk/3/KL1 b -')

        position.move((2, 3), (2, 1), True)  # promotes and capture promoted
        self.assertEqual(str(position), '1+Lk/3/K2 w R')
        self.assertEqual(position.status(), 'check')

    def test_capture_promoted_pawn(self):
        position = self.check('1k1/p2/+p1K/P2 b -', expected_num_ranks=4)

        position.move((3, 4), (3, 3))  # capture promoted
        self.assertEqual(str(position), '1k1/p2/P1K/3 w P')
        position.move((3, 2), (3, 3))  # capture back
        self.assertEqual(str(position), '1k1/3/p1K/3 b Pp')
        position.drop('P', (3, 2))
        self.assertEqual(str(position), '1k1/P2/p1K/3 w p')

        with self.assertRaisesRegex(ValueError, 'Illegal drop'):
            position.drop('P', (3, 1))  # nifu

    def test_deferred_promotion(self):
        sfen = '2k/SPs/K2 b -'
        position = self.check(sfen)

        with self.assertRaisesRegex(ValueError, 'Undefined promotion'):
            position.move((2, 2), (2, 1), None)  # must promote

        position.move((3, 2), (3, 1), None)  # can promote
        position.choose_promotion(True)      # yes please
        self.assertEqual(str(position), '+S1k/1Ps/K2 w -')

        position.move((1, 2), (1, 3), None)  # can promote
        position.choose_promotion(False)     # no thanks
        self.assertEqual(str(position), '+S1k/1P1/K1s b -')

    def check(self, sfen, expected_num_files=3, expected_num_ranks=3,
              expected_sfen=None, expected_status=''):
        position = Position(sfen, self._pieces)
        self.assertEqual(position.num_files, expected_num_files)
        self.assertEqual(position.num_ranks, expected_num_ranks)
        if not expected_sfen:
            expected_sfen = sfen
        self.assertEqual(str(position), expected_sfen)
        self.assertEqual(position.status(), expected_status)
        return position


if __name__ == '__main__':
    unittest.main()
