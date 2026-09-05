import pygame

from settings import (
    WIDTH, HEIGHT, GREEN, RED, WHITE,
    FONT,
    FIRST_HAND_POS_X, MAX_CARDS_IN_HAND, HAND_UPPER_PLAYER_POS_Y,
    BOT_TIMER,
)
from card import Card
from card_setup import CardSetup
from button import button_objects
from score_manager import ScoreManager
from gpu import GPU
from online import Online
from ui_manager import UIManager, MenuManager
from game_logic import Rules, Deck, PileGroup
from input_handler import InputHandler

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("THE GAME")

        self.clock = pygame.time.Clock()
        self.running = True

        # Ausgelagerte Manager & Module
        self.card_setup = CardSetup(self)
        self.deck = Deck()
        self.piles = PileGroup()
        self.score_manager = ScoreManager()
        self.ui_manager = UIManager(self, self.screen, self.score_manager)
        self.menu_manager = MenuManager(self)
        self.gpu = GPU(self)
        self.online = Online(self)
        self.input_handler = InputHandler(self)

        # Zustände
        self.selected_card = None
        self.new_game = False
        self.selected_mode = None
        self.with_pc = False
        self.sub_menu = False
        self.menu_state = 'main_menu'
        self.current_turn = 'player1'
        self.pc_timer = 0
        self.game_over = False
        self.score_saved = False

        # Sprite-Gruppen
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
                        self.move_card_to_pile(top_pile_card, target_group)
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

    def stapels_logic(self, card, pile_card, mouse_pos):
        if card.rect.collidepoint(mouse_pos):
            if not isinstance(self.selected_card.value, int):
                return

            sel_val = self.selected_card.value
            top_val = card.value

            # Verwendung des ausgelagerten Rules-Moduls
            if Rules.is_valid_move(pile_card.name, top_val, sel_val):
                print(f'card {sel_val} laid down on stapel')
                self.move_card_to_pile(card, pile_card)
            else:
                print(f'wrong move on pile {pile_card.name}. \ncurrent card {top_val}')
                self.check_possible_moves()

    def check_possible_moves(self):
        valid = False
        for card in self.hand_cards:
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
                self.score_manager.save_score(self.get_remaining_cards(), 'Simon', self.selected_mode)
                self.score_saved = True

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
                    self.refill_pc_hand()
                    self.gpu.opt_moves_calc = False
                    self.current_turn = 'player1'
                else:
                    # check if player has no more moves left
                    return

    def move_card_to_pile(self, target_pile_card, target_group):
        if not self.selected_card:
            return

        # delete from hand
        if self.current_turn == 'player1' or not self.with_pc:
            hand_list = self.cards_in_hand
            hand_group = self.hand_cards
        else:
            hand_list = self.player_2_cards_in_hand
            hand_group = self.player_2_hand_cards

        if self.selected_card in hand_list:
            hand_list.remove(self.selected_card)
            # if self.current_turn == 'pc':
            self.empty_hand_slot.append(self.selected_card.x)

        # save card value for network thingy, before selections is reset
        played_value = self.selected_card.value

        # delete from hand group - no double selection possible
        hand_group.remove(self.selected_card)
        self.selected_card.deselect()

        # set final coordinates & start animation
        self.selected_card.target_pile_card = target_pile_card
        self.selected_card.move_to(target_pile_card.rect.x, target_pile_card.rect.y)

        # if online: move send to other player
        if self.selected_mode == 'online':
            self.online.send_action('MOVED_CARD', {
                'card_value': played_value,
                'target_pile': target_group.name
            })

        # reset selection
        self.selected_card = None

    def game_over_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((50, 50, 50, 200))

        text_game_over = FONT.render('GAME OVER', True, RED)
        rect_game_over = text_game_over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))

        score_text = f'Current Score: {self.get_remaining_cards()}'
        text_score = FONT.render(score_text, True, WHITE)
        rect_score = text_score.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))

        score_text = f'Highscore: {self.score_manager.get_best_score()}'
        text_highscore = FONT.render(score_text, True, WHITE)
        rect_highscore = text_score.get_rect(center=(WIDTH // 5, HEIGHT // 2 + 90))

        overlay.blit(text_game_over, rect_game_over)
        overlay.blit(text_score, rect_score)
        overlay.blit(text_highscore, rect_highscore)

        self.screen.blit(overlay, (0, 0))

    def draw(self):
        if self.new_game or self.sub_menu:
            self.ui_manager.draw_menu(self.menu_state)
        else:
            self.screen.fill(GREEN)

            for button in button_objects:
                button.visible = button.buttonText not in ['online', 'play with PC', 'Host Game', 'Join Game', 'Back']
                button.draw(self.screen)

            self.all_cards.draw(self.screen)

        if self.game_over:
            self.ui_manager.draw_game_over(self.get_remaining_cards())

        pygame.display.flip()

    def run(self):
        while self.running:
            self.input_handler.events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()