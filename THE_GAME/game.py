import random
import pygame
from pygame.constants import MOUSEBUTTONDOWN

from settings import WIDTH, HEIGHT, GREEN, RED, WHITE, FONT
from card import Card
from button import Button, button_objects
from score_manager import ScoreManager
from gpu import GPU
from online import Online

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("THE GAME")
        self.clock = pygame.time.Clock()
        self.running = True

        self.selected_card = None
        self.new_game = False
        self.selected_mode = None
        self.with_pc = False
        self.sub_menu = False
        self.menu_state = 'main_menu'

        self.current_turn = 'player1'
        self.pc_timer = 0

        self.gpu = GPU(self)
        self.online = Online(self)
        self.score_manager = ScoreManager()

        self.get_buttons()

        # Sprite-Gruppe zum Verwalten aller Karten
        self.all_cards = pygame.sprite.Group()
        self.hand_cards = pygame.sprite.Group()
        self.deck_cards = pygame.sprite.Group()
        self.pile_cards_100_left : pygame.sprite.Group = pygame.sprite.Group()
        self.pile_cards_100_right: pygame.sprite.Group = pygame.sprite.Group()
        self.pile_cards_1_left: pygame.sprite.Group = pygame.sprite.Group()
        self.pile_cards_1_right: pygame.sprite.Group = pygame.sprite.Group()
        self.player_2_hand_cards = pygame.sprite.Group()
        self.player_2_hand_cards_back = pygame.sprite.Group()
        # self.reset_game()

        self.new_game_mode()

        self.pile_cards_100_left.name = 'pile_cards_100_left'
        self.pile_cards_100_right.name = 'pile_cards_100_right'
        self.pile_cards_1_left.name = 'pile_cards_1_left'
        self.pile_cards_1_right.name = 'pile_cards_1_right'

        self.score_saved = False

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
            onlickFunction=self.get_remaining_cards
        )
        Button(225, 175, 200, 50,
               '100 pile'
        )
        Button(
            775, 175, 200, 50,
            '100 pile'
        )
        Button(
            225, 525, 150, 50,
            '1 pile'
        )
        Button(
            825, 525, 150, 50,
            '1 pile'
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
        return len(self.remaining_cards)

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
                        self.move_card(top_pile_card, target_group)
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

        # 1. Ausgewählte Karte zurücksetzen
        if self.selected_card:
            self.selected_card.deselect()
            self.selected_card = None

        # 2. Alle bestehenden Sprite-Gruppen komplett leeren
        self.all_cards.empty()
        self.hand_cards.empty()
        self.deck_cards.empty()
        self.pile_cards_100_left.empty()
        self.pile_cards_100_right.empty()
        self.pile_cards_1_left.empty()
        self.pile_cards_1_right.empty()

        # 3. Kartenstapel als Instanzvariable neu aufbauen
        self.remaining_cards = sorted(list(range(2, 100)))

        # 4. Karten neu laden
        self.load_starting_cards()
        self.load_starting_hand()
        self.load_other_game_players()

        self.pile_sets = [
            self.pile_cards_100_left,
            self.pile_cards_100_right,
            self.pile_cards_1_left,
            self.pile_cards_1_right,
        ]

    def load_starting_cards(self):
        # Karten instanziieren und zur Sprite-Gruppe hinzufügen
        card_1_right = Card(value=1, x=1000, y=500)
        card_1_left = Card(value=1, x=100, y=500)
        card_100_right = Card(value=100, x=1000, y=100)
        card_100_left = Card(value=100, x=100, y=100)

        card_deck = Card(value='back', x=550, y=300)

        self.pile_cards_100_left.add(card_100_left)
        self.pile_cards_100_right.add(card_100_right)
        self.pile_cards_1_left.add(card_1_left)
        self.pile_cards_1_right.add(card_1_right)
        self.deck_cards.add(card_deck)

        self.all_cards.add(
            card_1_left,
            card_1_right,
            card_100_left,
            card_100_right,
            card_deck
        )

    def random_card_generator(self):
        len_remaining_cards = len(self.remaining_cards) - 1
        if len_remaining_cards < 0:
            print('no remaining cards!')
            return None

        taken_card_idx = random.randint(0, len_remaining_cards)
        taken_card = self.remaining_cards[taken_card_idx]
        self.remaining_cards.remove(taken_card)
        return taken_card


    def load_starting_hand(self):
        self.cards_in_hand = []
        left_card_pos = 350
        distance_to_previous = 100

        while len(self.cards_in_hand) < 5:
            self.card_generator(
                self.cards_in_hand,
                left_card_pos,
                self.random_card_generator(),
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
        left_card_pos = 350
        distance_to_previous = 100

        while len(self.player_2_cards_in_hand) < 5:
            self.card_generator(
                self.player_2_cards_in_hand,
                left_card_pos,
                self.random_card_generator(),
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

                        if len(self.cards_in_hand) < 4:
                            for card in self.deck_cards:
                                if card.rect.collidepoint(mouse_pos) and (len(self.empty_hand_slot) > 0):
                                    print('drew cards...')
                                    for x in range(len(self.empty_hand_slot)):
                                        pos_x = self.empty_hand_slot[x]
                                        self.card_generator(
                                            self.cards_in_hand,
                                            pos_x,
                                            self.random_card_generator(),
                                            600,
                                        )

                                    self.hand_cards.add(self.cards_in_hand)
                                    self.all_cards.add(self.cards_in_hand)
                                    self.empty_hand_slot.clear()

                                    if self.with_pc:
                                        self.current_turn = 'pc'
                                        self.pc_timer = pygame.time.get_ticks()

                        if not card_clicked and self.selected_card:
                            for card in self.pile_cards_100_left:
                                self.stapels_logic(card, self.pile_cards_100_left, mouse_pos)

                            for card in self.pile_cards_100_right:
                                self.stapels_logic(card, self.pile_cards_100_right, mouse_pos)

                            for card in self.pile_cards_1_left:
                                self.stapels_logic(card, self.pile_cards_1_left, mouse_pos)

                            for card in self.pile_cards_1_right:
                                self.stapels_logic(card, self.pile_cards_1_right, mouse_pos=mouse_pos)

    def stapels_logic(self, card, pile_card, mouse_pos):
        if card.rect.collidepoint(mouse_pos):
            if not isinstance(self.selected_card.value, int):
                return

            sel_val = self.selected_card.value
            top_val = card.value
            current_pile_name = pile_card.name

            is_valid = self.valid_move(
                current_pile_name,
                top_val,
                sel_val,
            )

            if is_valid:
                print(f'card {sel_val} laid down on stapel')
                self.move_card(card, pile_card)
            else:
                print(f'wrong move on pile {pile_card.name}. \ncurrent card {top_val}')
                self.check_possible_moves()

    def valid_move(self, pile_card_name, top_val, sel_val):
            if '100' in pile_card_name:
                is_valid = (sel_val < top_val) or (sel_val == top_val + 10)
            else:
                is_valid = (sel_val > top_val) or (sel_val == top_val - 10)

            return is_valid

    def check_possible_moves(self):
        valid = False

        for card in self.hand_cards:
            for pile in self.pile_sets:
                if len(pile) == 0:
                    continue

                top_card = pile.sprites()[0]
                pile_name = pile.name
                pile_val = top_card.value
                card_val = card.value

                if self.valid_move(pile_name, pile_val, card_val):
                    valid = True
                    break

            if valid:
                break

        if valid:
            print('moves still allowed')
        else:
            print('no more moves allowed')
            self.game_over = True

            if not self.score_saved:
                current_score = self.get_remaining_cards()
                self.score_manager.save_score(current_score, 'Simon', self.selected_mode)
                self.score_saved = True

    def refill_pc_hand(self):
        while len(self.player_2_cards_in_hand) < 5 and len(self.remaining_cards) > 0:
            pos_x = 350 + (len(self.player_2_cards_in_hand) * 100)

            new_card_val = self.random_card_generator()
            if new_card_val is None:
                break

            # 1. Echte Logikkarte erstellen (unsichtbar im Hintergrund)
            new_card = Card(value=new_card_val, x=pos_x, y=-100)

            # 2. Visuelle Kartenrücken-Sprite erstellen
            back_card = Card(value='back', x=pos_x, y=-100)

            # 3. Listen und Sprite-Gruppen für die Hand auffüllen
            self.player_2_cards_in_hand.append(new_card)
            self.player_2_back_cards_in_hand.append(back_card)

            self.player_2_hand_cards.add(new_card)
            self.player_2_hand_cards_back.add(back_card)

            self.all_cards.add(new_card)
            self.all_cards.add(back_card)

    def update(self):
        self.all_cards.update()

        if self.with_pc and self.current_turn == 'pc' and not self.game_over:
            current_time = pygame.time.get_ticks()

            if current_time - self.pc_timer > 600:
                move_made = self.gpu.simple_move()

                if not move_made:
                    print('pc is done with his moves...')
                    self.refill_pc_hand()
                    self.gpu.opt_moves_calc = False
                    self.current_turn = 'player1'
                else:
                    # check if player has no more moves left
                    return

    def move_card(self, target_pile_card, target_group):
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
            if self.current_turn == 'player1':
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
            self.mode_select_screen()
        else:
            self.screen.fill(GREEN)
            self.all_cards.draw(self.screen)

            for button in button_objects:
                button.visible = button.buttonText not in ['online', 'play with PC', 'Host Game', 'Join Game', 'Back']
                button.draw(self.screen)

        if self.game_over:
            self.game_over_screen()

        pygame.display.flip()

    def run(self):
        # Hauptschleife
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()