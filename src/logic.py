import pygame
import random

from settings import (
    WIDTH, HEIGHT,
    FIRST_HAND_POS_X, MAX_CARDS_IN_HAND, HAND_UPPER_PLAYER_POS_Y, MAX_CARDS_IN_HAND_FOR_REFILL_EASY,
    BOT_TIMER,
    FPS
)
from score_manager import ScoreManager
from .bot import BOT
from online import Online

from src.ui import UIManager, MenuManager, InputHandler
from src.models import Card

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("THE GAME")

        self.clock = pygame.time.Clock()
        self.running = True

        self.card_setup = CardSetup(self)
        self.deck = Deck()
        self.piles = PileGroup(self)
        self.score_manager = ScoreManager()
        self.ui_manager = UIManager(self, self.screen, self.score_manager)
        self.menu_manager = MenuManager(self)
        self.gpu = BOT(self)
        self.online = Online(self)
        self.input_handler = InputHandler(self)

        self.selected_card = None
        self.new_game = False
        self.selected_mode = None
        self.with_pc = False
        self.sub_menu = False
        self.menu_state = 'main_menu'
        self.current_turn = 'player1'
        self.player_name = 'PLAYER1'
        self.pc_timer = 0
        self.game_over = False
        self.score_saved = False

        self.all_cards = pygame.sprite.Group()
        self.hand_cards = pygame.sprite.Group()
        self.deck_cards = pygame.sprite.Group()
        self.player_2_hand_cards = pygame.sprite.Group()
        self.player_2_hand_cards_back = pygame.sprite.Group()

        self.menu_manager.get_buttons()
        self.new_game_mode()

    def get_remaining_cards(self):
        return len(self.deck)

    def handle_network_action(self, packet):
        action = packet.get('action')
        data = packet.get('data')

        if action == 'MOVE_CARD':
            card_val = data['card_val']
            pile_name = data['target_pile']
            print(f'Network received: {data}')

            target_group = None
            for pile in self.pile_sets:
                if pile.name == pile_name:
                    target_group = pile
                    break

            if target_group and len(target_group) > 0:
                top_pile_card = target_group.sprites()[0]

                for card in list(self.player_2_hand_cards):
                    if card.value == card_val:
                        self.selected_card = card
                        self.piles.move_card_to_pile(top_pile_card, target_group)
                        break

    def new_game_mode(self):
        self.new_game = True

    def reset_game(self):
        print('resetting the game...')
        self.game_over = False
        self.score_saved = False

        if self.selected_card:
            self.selected_card.deselect()
            self.selected_card = None

        self.all_cards.empty()
        self.hand_cards.empty()
        self.deck_cards.empty()
        self.piles.empty_all()

        self.deck.reset()

        self.card_setup.load_starting_cards()
        self.card_setup.load_starting_hand()
        self.load_other_game_players()

    def fill_up_hand(self, empty_hand_pos):
        self.selected_card.move_to(*empty_hand_pos)

    def card_generator(self, hand_list, card_pos, number, y):
        hand_list.append(
            Card(
                value=number,
                x=card_pos,
                y=y
            )
        )
        return

    def load_other_game_players(self):
        self.player_2_cards_in_hand = []
        self.player_2_back_cards_in_hand = []
        left_card_pos = FIRST_HAND_POS_X
        distance_to_previous = 100

        while len(self.player_2_cards_in_hand) < MAX_CARDS_IN_HAND:
            self.card_generator(
                self.player_2_cards_in_hand,
                left_card_pos,
                self.deck.draw_card(),
                -100
            )
            self.card_generator(
                self.player_2_back_cards_in_hand,
                left_card_pos,
                'back',
                -100
            )

            left_card_pos += distance_to_previous

        self.empty_hand_slot = []

        self.player_2_hand_cards.add(self.player_2_cards_in_hand)
        self.player_2_hand_cards_back.add(self.player_2_back_cards_in_hand)

        self.all_cards.add(self.player_2_cards_in_hand)
        self.all_cards.add(self.player_2_back_cards_in_hand)

    def staples_logic(self, card, pile_card, mouse_pos):
        if card.rect.collidepoint(mouse_pos):
            if not isinstance(self.selected_card.value, int):
                return

            sel_val = self.selected_card.value
            top_val = card.value

            # Verwendung des ausgelagerten Rules-Moduls
            if Rules.is_valid_move(pile_card.name, top_val, sel_val):
                print(f'card {sel_val} laid down on stapel')
                self.piles.move_card_to_pile(card, pile_card)
            else:
                print(f'wrong move on pile {pile_card.name}. \ncurrent card {top_val}')
                self.check_possible_moves()

    def check_possible_moves(self, hand=None):
        if hand is None:
            hand = self.hand_cards

        if len(hand) == 0 or self.menu_state == 'main_menu':
            return True

        valid = False
        for card in hand:
            for pile in self.piles.get_all_piles():
                if len(pile) == 0:
                    continue
                top_card = pile.sprites()[0]
                if Rules.is_valid_move(pile.name, top_card.value, card.value):
                    valid = True
                    break
            if valid:
                break

        if not valid:
            print('no more moves allowed')
            self.game_over = True
            if not self.score_saved:
                time_str = self.menu_manager.end_timer()
                self.score_manager.save_score(self.get_remaining_cards(), self.player_name, self.selected_mode, time_str)
                self.score_saved = True
            return False

        return True

    def refill_pc_hand(self): # maybe change for can just draw a card if already put 2 on piles
        while len(self.player_2_cards_in_hand) < MAX_CARDS_IN_HAND and len(self.deck) > 0:
            if not self.empty_hand_slot:
                break

            pos_x = self.empty_hand_slot.pop(0)
            new_card_val = self.deck.draw_card()
            if new_card_val is None:
                break

            # logic card
            new_card = Card(value=new_card_val, x=pos_x, y=HAND_UPPER_PLAYER_POS_Y)
            # visuell card
            back_card = Card(value='back', x=pos_x, y=HAND_UPPER_PLAYER_POS_Y)

            # lists & sprite groups filling
            # logic cards
            self.player_2_cards_in_hand.append(new_card)
            self.player_2_hand_cards.add(new_card)
            self.all_cards.add(new_card)
            # # visuel cards
            self.player_2_back_cards_in_hand.append(back_card)
            self.player_2_hand_cards_back.add(back_card)
            self.all_cards.add(back_card)

    def update(self):
        self.all_cards.update()

        if self.with_pc and self.current_turn == 'pc' and not self.game_over:
            current_time = pygame.time.get_ticks()

            if current_time - self.pc_timer > BOT_TIMER:
                move_made = self.gpu.simple_move()

                if not move_made:
                    print('pc is done with his moves...')

                    has_moves = self.check_possible_moves(self.player_2_hand_cards)
                    hand_too_full = len(self.player_2_cards_in_hand) > MAX_CARDS_IN_HAND_FOR_REFILL_EASY

                    if not has_moves or hand_too_full:
                        print('PC has no valid moves left or did not lay out enough cards...')
                        self.game_over = True
                        return

                    self.refill_pc_hand()
                    self.gpu.opt_moves_calc = False

                    if not self.check_possible_moves(self.hand_cards):
                        print('Player has no valid moves left. \n\n ---GAME OVER--- \n\n')
                        return

                    self.current_turn = 'player1'

    def run(self):
        while self.running:
            self.input_handler.events()
            self.update()
            self.ui_manager.draw()
            self.clock.tick(60)

        pygame.quit()


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

        target_group.add(self.game.selected_card)

        self.game.selected_card.target_pile_card = target_pile_card
        self.game.selected_card.move_to(target_pile_card.rect.x, target_pile_card.rect.y)

        if self.game.selected_mode == 'online':
            self.game.online.send_action('MOVED_CARD', {
                'card_value': played_value,
                'target_pile': target_group.name
            })

        self.game.selected_card = None


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