import numpy as np

from settings import FIRST_HAND_POS_X, HAND_UPPER_PLAYER_POS_Y, CARD_WIDTH

class GPU:
    def __init__(self, game):
        self.game = game
        self.matrix = []
        self.opt_moves_calc = False

    def simple_move(self):
        pc_cards = self.game.player_2_hand_cards
        print(len(pc_cards))

        if not self.opt_moves_calc:
            self.planed_moves = self.automated_smartest_move_light(pc_cards, self.game.piles.get_all_piles())
            self.opt_moves_calc = True

        if self.planed_moves:
            next_move = self.planed_moves.pop(0)

            card = next_move['card_obj']
            pile = next_move['pile_obj']
            top_card = pile.sprites()[0]

            self.execute_move(card, top_card, pile)
            return True

        return False

    def automated_smartest_move_light(self, pc_cards, pile_sets):
        valid_moves = []
        special_moves = []
        final_two_moves = []

        used_card_indices = set()

        num_cards = len(pc_cards)
        num_piles = len(pile_sets)

        self.matrix = np.zeros((num_cards, num_piles))
        matrix_abs = self.matrix.copy()

        for row, card in enumerate(pc_cards):
            for col, pile in enumerate(pile_sets):
                pile_card_value = pile.sprites()[0].value
                distance = card.value - pile_card_value

                self.matrix[row, col] = distance
                matrix_abs[row, col] = abs(distance)

        print(self.matrix.shape)

        for row in range(num_cards):
            for col in range(num_piles):
                pos_val = self.matrix[row, col]
                abs_val = matrix_abs[row, col]

                if (col in (0, 1) and pos_val == +10) or (col in (2, 3) and pos_val == -10):
                    special_moves.append({
                        'abs_dist': abs_val,
                        'card_idx': row,
                        'pile_idx': col,
                        'card_obj': list(pc_cards)[row],
                        'pile_obj': pile_sets[col]
                    })
                if (col in (0, 1) and pos_val < 0) or (col in (2, 3) and pos_val > 0):
                    valid_moves.append({
                        'abs_dist': abs_val,
                        'card_idx': row,
                        'pile_idx': col,
                        'card_obj': list(pc_cards)[row],
                        'pile_obj': pile_sets[col]
                    })

        # special_moves.sort(key=lambda move: move['abs_dist'])
        valid_moves.sort(key=lambda move: move['abs_dist'])

        for move in valid_moves:
            for special_move in special_moves:
                if special_move['card_idx'] not in used_card_indices:
                    final_two_moves.append(special_move)
                    used_card_indices.add(special_move['card_idx'])
            if move['card_idx'] not in used_card_indices:
                final_two_moves.append(move)
                used_card_indices.add(move['card_idx'])

            if len(final_two_moves) == 2:
                break

        print(f"Gefundene Züge für den PC: {len(final_two_moves)}")
        for m in final_two_moves:
            print(f"-> Karte Index {m['card_idx']} auf Stapel {m['pile_idx']} (Abstand: {m['abs_dist']})")

        self.opt_moves_calc = True

        return final_two_moves

    def execute_move(self, card_to_play, target_pile_card, target_group):
        self.game.selected_card = card_to_play
        self.game.piles.move_card_to_pile(target_pile_card, target_group)

    def move_remaining_cards(self, cards_to_sort, y_pos=HAND_UPPER_PLAYER_POS_Y):
        x_pos = FIRST_HAND_POS_X

        for card in cards_to_sort:
            card.x = x_pos
            card.move_to(x_pos, y_pos)
            x_pos += CARD_WIDTH
