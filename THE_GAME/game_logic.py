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

    def draw_card(self):
        if not self.remaining_cards:
            return None
        taken_card = random.choice(self.remaining_cards)
        self.remaining_cards.remove(taken_card)
        return taken_card

    def __len__(self):
        return len(self.remaining_cards)

class PileGroup:
    def __init__(self):
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