from card import Card
from settings import FIRST_HAND_POS_X, MAX_CARDS_IN_HAND

class CardSetup:
    def __init__(self, game):
        self.game = game

    def load_starting_cards(self):
        card_1_right = Card(value=1, x=1000, y=500)
        card_1_left = Card(value=1, x=100, y=500)
        card_100_right = Card(value=100, x=1000, y=100)
        card_100_left = Card(value=100, x=100, y=100)
        card_deck = Card(value='back', x=550, y=300)

        self.game.piles.pile_100_left.add(card_100_left)
        self.game.piles.pile_100_right.add(card_100_right)
        self.game.piles.pile_1_left.add(card_1_left)
        self.game.piles.pile_1_right.add(card_1_right)
        self.game.deck_cards.add(card_deck)

        self.game.all_cards.add(card_1_left, card_1_right, card_100_left, card_100_right, card_deck)

    def load_starting_hand(self):
        self.game.cards_in_hand = []
        left_card_pos = FIRST_HAND_POS_X
        distance_to_previous = 100

        while len(self.game.cards_in_hand) < MAX_CARDS_IN_HAND:
            self.game.card_generator(
                self.game.cards_in_hand,
                left_card_pos,
                self.game.deck.draw_card(),
                600,
            )
            left_card_pos += distance_to_previous

        self.game.empty_hand_slot = []

        self.game.hand_cards.add(self.game.cards_in_hand)

        self.game.all_cards.add(self.game.cards_in_hand)