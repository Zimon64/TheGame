import random
import pygame
from pygame.constants import MOUSEBUTTONDOWN

from settings import (
    WIDTH, HEIGHT, GREEN, RED, WHITE,
    FONT,
    FIRST_HAND_POS_X, MAX_CARDS_IN_HAND, MAX_CARDS_IN_HAND_FOR_REFILL_EASY, HAND_UPPER_PLAYER_POS_Y,
    BOT_TIMER,
)
from card import Card
from button import Button, button_objects
from score_manager import ScoreManager
from gpu import GPU
from online import Online
from ui_manager import UIManager
from game_logic import Rules, Deck, PileGroup

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("THE GAME")

        self.clock = pygame.time.Clock()
        self.running = True

        # Ausgelagerte Manager & Module
        self.deck = Deck()
        self.piles = PileGroup()
        self.score_manager = ScoreManager()
        self.ui_manager = UIManager(self.screen, self.score_manager)
        self.gpu = GPU(self)
        self.online = Online(self)

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

        self.get_buttons()
        self.new_game_mode()

    def reset_button(self):
        self.reset_game()
        self.new_game_mode()

    def get_buttons(self):
        # table
        Button(
            0, 0, 200, 50,
            'New Game',
            self.reset_button,
            True)
        Button(
            500, 250, 200, 50,
            buttonText= lambda: f'DECK: {self.get_remaining_cards()}',
            onlickFunction=self.get_remaining_cards,
            static_color=True
        )
        Button(225, 175, 200, 50,
               '100 pile', static_color=True
        )
        Button(
            775, 175, 200, 50,
            '100 pile', static_color=True
        )
        Button(
            225, 525, 150, 50,
            '1 pile', static_color=True
        )
        Button(
            825, 525, 150, 50,
            '1 pile', static_color=True
        )

        # main menu
        Button(
            500, 250, 200, 50,
            'online',
            self.open_online_menu,
            True
        )

        Button(
            450, 500, 300, 50,
            'play with PC',
            self.start_with_pc,
            True
        )

        # under menu - online buttons
        Button(
            450, 250, 300, 50,
            'Host Game',
            self.start_host_game,
            True
        )
        Button(
            450, 375, 300, 50,
            'Join Game',
            self.start_join_game,
            True
        )
        Button(
            450, 500, 300, 50,
            'Back',
            self.back_to_main_menu,
            True
        )

        self.game_over = False

    def get_remaining_cards(self):
        return len(self.deck)

    def back_to_main_menu(self):
        self.menu_state = 'main_menu'
        self.selected_mode = None
        self.sub_menu = False
        self.new_game = True

    def open_online_menu(self):
        self.menu_state = 'online_menu'
        self.sub_menu = True

    def start_host_game(self):
        self.reset_game()

        self.selected_mode = 'online'
        self.menu_state = 'in_game'

        self.new_game = False

        print(f'Starting new game as HOST...')
        self.online.start_host()

    def start_join_game(self):
        self.selected_mode = 'online'

        self.new_game = False
        self.sub_menu = False

        print(f'Connecting with HOST...')
        self.online._connect_to_host("127.0.0.1")

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


    def start_with_pc(self):
        self.reset_game()
        self.selected_mode = 'with_pc'
        self.new_game = False
        self.with_pc = True
        self.current_turn = 'player1'

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

        self.load_starting_cards()
        self.load_starting_hand()
        self.load_other_game_players()

    def load_starting_cards(self):
        card_1_right = Card(value=1, x=1000, y=500)
        card_1_left = Card(value=1, x=100, y=500)
        card_100_right = Card(value=100, x=1000, y=100)
        card_100_left = Card(value=100, x=100, y=100)
        card_deck = Card(value='back', x=550, y=300)

        self.piles.pile_100_left.add(card_100_left)
        self.piles.pile_100_right.add(card_100_right)
        self.piles.pile_1_left.add(card_1_left)
        self.piles.pile_1_right.add(card_1_right)
        self.deck_cards.add(card_deck)

        self.all_cards.add(card_1_left, card_1_right, card_100_left, card_100_right, card_deck)

    def load_starting_hand(self):
        self.cards_in_hand = []
        left_card_pos = FIRST_HAND_POS_X
        distance_to_previous = 100

        while len(self.cards_in_hand) < MAX_CARDS_IN_HAND:
            self.card_generator(
                self.cards_in_hand,
                left_card_pos,
                self.deck.draw_card(),
                600,
            )
            left_card_pos += distance_to_previous

        self.empty_hand_slot = []

        self.hand_cards.add(self.cards_in_hand)

        self.all_cards.add(self.cards_in_hand)

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

    def check_selection(self, mouse_pos):
        for card in self.hand_cards:
            if card.rect.collidepoint(mouse_pos):
                if self.selected_card:
                    self.selected_card.deselect()

                self.selected_card = card
                self.selected_card_value = card.value
                print(card)
                self.selected_card.select()

                print(f'card {card.value} from hand selected...')
                card_clicked = True
                break

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    # 1. Menü-Buttons prüfen
                    button_clicked = False
                    for button in button_objects:
                        if button.visible and button.check_event(event):
                            button_clicked = True
                            break

                    # 2. Wenn kein Button geklickt wurde, Karten-Logik ausführen
                    if not button_clicked and not (self.new_game or self.sub_menu):
                        mouse_pos = event.pos
                        card_clicked = False
                        self.check_selection(mouse_pos)

                        if len(self.cards_in_hand) == 0 and self.get_remaining_cards() == 0 and len(self.player_2_cards_in_hand) == 0:
                            print('no cards left\n\n ---GAME WON!!!--- \n\n')

                        elif ((len(self.cards_in_hand) < MAX_CARDS_IN_HAND and self.get_remaining_cards() == 0) or
                              len(self.cards_in_hand) <= MAX_CARDS_IN_HAND_FOR_REFILL_EASY):
                            self.card_drawing(self.cards_in_hand, mouse_pos)

                        else:
                            print('not enough cards laid out yet...')

                        if not card_clicked and self.selected_card and not card_clicked and self.selected_card:
                            for pile in self.piles.get_all_piles():
                                for card in pile:
                                    self.stapels_logic(card, pile, mouse_pos)

    def card_drawing(self, cards_in_hand, mouse_pos,
                     max_cards_hand=MAX_CARDS_IN_HAND, max_cards_hand_easy=MAX_CARDS_IN_HAND_FOR_REFILL_EASY):
        for card in self.deck_cards:
            card_col_n_empty_hand_slot = card.rect.collidepoint(mouse_pos) and (len(self.empty_hand_slot) > 0)
            if len(cards_in_hand) < max_cards_hand and self.get_remaining_cards() == 0:
                print('no cards left to draw from the Deck pile... \nnext players turn...')
                if card_col_n_empty_hand_slot and self.with_pc:
                    print('no cards drawn...')
                    self.current_turn = 'pc'
                    self.pc_timer = pygame.time.get_ticks()
                elif card_col_n_empty_hand_slot and not self.with_pc:
                    # logic for drawing online
                    return

            elif len(cards_in_hand) <= max_cards_hand_easy:
                print('draw cards...')
                for x in range(len(self.empty_hand_slot)):
                    if self.get_remaining_cards() == 0:
                        break
                    pos_x = self.empty_hand_slot[x]
                    self.card_generator(
                        self.cards_in_hand,
                        pos_x,
                        self.deck.draw_card(),
                        600,
                    )

                self.hand_cards.add(self.cards_in_hand)
                self.all_cards.add(self.cards_in_hand)
                self.empty_hand_slot.clear()

                if self.with_pc:
                    self.current_turn = 'pc'
                    self.pc_timer = pygame.time.get_ticks()
                else:
                    # logic for drawing online
                    return

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

    def mode_select_screen(self):
        if self.menu_state == 'main_menu':
            self.screen.fill(GREEN)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((50, 50, 50, 200))
            self.screen.blit(overlay, (0, 0))

            for button in button_objects:
                button.visible = button.buttonText in ['online', 'play with PC']
                button.draw(self.screen)

        elif self.menu_state == 'online_menu':
            self.screen.fill(GREEN)

            for button in button_objects:
                button.visible = button.buttonText in ['Host Game', 'Join Game', 'Back']
                button.draw(self.screen)

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
        # Hauptschleife
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()