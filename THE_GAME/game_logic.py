import random
import pygame

class Rules:
    @staticmethod
    def is_valid_move(pile_name: str, top_val: int, sel_val: int) -> bool:
        if '100' in pile_name:
            return (sel_val < top_val) or (sel_val == top_val + 10)
        return (sel_val > top_val) or (sel_val == top_val - 10)

class Deck:
    def __init__(self):
        self.remaining_cards = []
        self.reset()

    def reset(self):
        self.remaining_cards = sorted(list(range(2, 100)))
        # # check for game ending behavior
        # self.remaining_cards = sorted(list(range(2,16)))

    def draw_card(self):
        if not self.remaining_cards:
            return None
        taken_card = random.choice(self.remaining_cards)
        self.remaining_cards.remove(taken_card)
        return taken_card

    def __len__(self):
        return len(self.remaining_cards)

class PileGroup:
    def __init__(self, game):
        self.game = game
        self.pile_100_left = pygame.sprite.Group()
        self.pile_100_right = pygame.sprite.Group()
        self.pile_1_left = pygame.sprite.Group()
        self.pile_1_right = pygame.sprite.Group()

        self.pile_100_left.name = 'pile_card_100_left'
        self.pile_100_right.name = 'pile_card_100_right'
        self.pile_1_left.name = 'pile_card_1_left'
        self.pile_1_right.name = 'pile_card_1_right'

    def get_all_piles(self):
        return [
            self.pile_100_left,
            self.pile_100_right,
            self.pile_1_left,
            self.pile_1_right
        ]

    def empty_all(self):
        for pile in self.get_all_piles():
            pile.empty()

    def move_card_to_pile(self, target_pile_card, target_group):
        if not self.game.selected_card:
            return

        # Aus der Hand entfernen
        if self.game.current_turn == 'player1' or not self.game.with_pc:
            hand_list = self.game.cards_in_hand
            hand_group = self.game.hand_cards
        else:
            hand_list = self.game.player_2_cards_in_hand
            hand_group = self.game.player_2_hand_cards

        if self.game.selected_card in hand_list:
            hand_list.remove(self.game.selected_card)
            self.game.empty_hand_slot.append(self.game.selected_card.x)

        played_value = self.game.selected_card.value

        hand_group.remove(self.game.selected_card)
        self.game.selected_card.deselect()

        # WICHTIG: Die neue Karte hinten an die Gruppe anhängen!
        target_group.add(self.game.selected_card)

        # Positionierung und Animation
        self.game.selected_card.target_pile_card = target_pile_card
        self.game.selected_card.move_to(target_pile_card.rect.x, target_pile_card.rect.y)

        if self.game.selected_mode == 'online':
            self.game.online.send_action('MOVED_CARD', {
                'card_value': played_value,
                'target_pile': target_group.name
            })

        self.game.selected_card = None