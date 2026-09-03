import numpy as np

class GPU:
    def __init__(self, game):
        self.game = game
        self.opt_moves_calc = False

    def simple_move(self):
        pc_cards = self.game.player_2_hand_cards

        if not self.opt_moves_calc:
            self.planed_moves = self.automated_smartest_move_light(pc_cards, self.game.pile_sets)
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
        num_cards = len(pc_cards)
        num_piles = len(pile_sets)

        matrix = np.zeros((num_cards, num_piles))
        matrix_abs = np.zeros((num_cards, num_piles))

        for row, card in enumerate(pc_cards):
            for col, pile in enumerate(pile_sets):
                pile_card_value = pile.sprites()[0].value
                distance = card.value - pile_card_value

                matrix[row, col] = distance
                matrix_abs[row, col] = abs(distance)

        valid_moves = []

        for row in range(num_cards):
            for col in range(num_piles):
                pos_val = matrix[row, col]
                abs_val = matrix_abs[row, col]

                if (col in (0, 1) and pos_val < 0) or (col in (2, 3) and pos_val > 0):
                    valid_moves.append({
                        'abs_dist': abs_val,
                        'card_idx': row,
                        'pile_idx': col,
                        'card_obj': list(pc_cards)[row],
                        'pile_obj': pile_sets[col]
                    })

        valid_moves.sort(key=lambda move: move['abs_dist'])

        final_two_moves = []
        used_card_indices = set()

        for move in valid_moves:
            if move['card_idx'] not in used_card_indices:
                final_two_moves.append(move)
                used_card_indices.add(move['card_idx'])

            if len(final_two_moves) == 2:
                break

        print(f"Gefundene Züge für den PC: {len(final_two_moves)}")
        for m in final_two_moves:
            print(f"-> Karte Index {m['card_idx']} auf Stapel {m['pile_idx']} (Abstand: {m['abs_dist']})")

        self.opt_moves_clac = True

        return final_two_moves

    def execute_move(self, card_to_play, target_pile_card, target_group):
        self.game.selected_card = card_to_play
        self.game.move_card(target_pile_card, target_group)