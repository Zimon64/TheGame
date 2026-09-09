import numpy as np
from settings import FIRST_HAND_POS_X, HAND_UPPER_PLAYER_POS_Y, CARD_WIDTH

class GPU:
    def __init__(self, game):
        self.game = game
        self.matrix = []
        self.opt_moves_calc = False
        self.planed_moves = []

    def simple_move(self):
        pc_cards = self.game.player_2_hand_cards

        if not self.opt_moves_calc:
            self.planed_moves = self.automated_smartest_move_light(pc_cards, self.game.piles.get_all_piles())
            self.opt_moves_calc = True

        if self.planed_moves:
            next_move = self.planed_moves.pop(0)
            card = next_move['card_obj']
            pile_group = next_move['pile_obj']

            # Nimmt die aktuellste Karte des Stapels als Ziel
            top_card = pile_group.sprites()[-1] if len(pile_group.sprites()) > 0 else list(pile_group)[0]

            self.execute_move(card, top_card, pile_group)
            print(f"current laid card: {card.value}")
            return True

        return False

    def automated_smartest_move_light(self, pc_cards, pile_sets):
        final_two_moves = []
        used_card_indices = set()
        cards_list = list(pc_cards)

        # Aktuelle Werte der 4 Stapel ermitteln
        current_pile_values = [p.sprites()[-1].value for p in pile_sets]

        for move_num in range(2): # Maximal 2 Züge planen
            best_move = None
            best_score = float('inf')

            for row, card in enumerate(cards_list):
                if row in used_card_indices:
                    continue

                for col, pile in enumerate(pile_sets):
                    top_val = current_pile_values[col]
                    pos_val = card.value - top_val
                    abs_val = abs(pos_val)

                    is_special = False
                    is_valid = False

                    # Stapel 0 & 1: 100er (Abwärts)
                    if col in (0, 1):
                        if pos_val == 10:
                            is_special = True
                        elif pos_val < 0:
                            is_valid = True

                    # Stapel 2 & 3: 1er (Aufwärts)
                    elif col in (2, 3):
                        if pos_val == -10:
                            is_special = True
                        elif pos_val > 0:
                            is_valid = True

                    if is_special or is_valid:
                        # Priorisiere Sonderzüge extrem hoch (-1000 Abstand)
                        score = -1000 if is_special else abs_val

                        if score < best_score:
                            best_score = score
                            best_move = {
                                'abs_dist': abs_val,
                                'card_idx': row,
                                'pile_idx': col,
                                'card_obj': card,
                                'pile_obj': pile
                            }

            if best_move:
                final_two_moves.append(best_move)
                used_card_indices.add(best_move['card_idx'])
                # Aktualisiere den virtuellen Stapelwert für die 2. Kartenberechnung!
                current_pile_values[best_move['pile_idx']] = best_move['card_obj'].value
            else:
                break

        print(f"Gefundene Züge für den PC: {len(final_two_moves)}")
        for m in final_two_moves:
            print(f"-> Karte Index {m['card_idx']} auf Stapel {m['pile_idx']} (Abstand: {m['abs_dist']}) \nKartenwert: {m['card_obj'].value}")

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