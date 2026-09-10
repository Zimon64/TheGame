import pygame

from time import time

from settings import (
    WIDTH, HEIGHT, GREEN, RED, WHITE, GRAY, BRIGHT_GREEN,
    FONT,
    SCORING_TABLE_X, MAX_CARDS_IN_HAND, MAX_CARDS_IN_HAND_FOR_REFILL_EASY
)


class UIManager(object):
    def __init__(self, game, screen, score_manager):
        self.game = game
        self.screen = screen
        self.score_manager = score_manager
        self.scroll_y = 0

    def draw_game_over(self, score: int):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((50, 50, 50, 200))

        text_game_over = FONT.render('GAME OVER', True, RED)
        rect_game_over = text_game_over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))

        text_score = FONT.render(f'Current Score: {score}', True, WHITE)
        rect_score = text_score.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))

        text_highscore = FONT.render(f'Highscore: {self.score_manager.get_best_score()}', True, WHITE)
        rect_highscore = text_score.get_rect(center=(WIDTH // 3 + 100, HEIGHT // 2 + 90))

        overlay.blit(text_game_over, rect_game_over)
        overlay.blit(text_score, rect_score)
        overlay.blit(text_highscore, rect_highscore)

        self.screen.blit(overlay, (0, 0))

    def draw_menu(self, menu_state: str):
        self.screen.fill(GREEN)
        if menu_state == 'main_menu':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((50, 50, 50, 200))
            self.screen.blit(overlay, (0, 0))

            for button in self.game.menu_manager.buttons:
                button.visible = button.buttonText in ['online', 'play with PC', 'Change Name', 'Scoring List']
                button.draw(self.screen)

        elif menu_state == 'online_menu':
            for button in self.game.menu_manager.buttons:
                button.visible = button.buttonText in ['Host Game', 'Join Game', 'Back']
                button.draw(self.screen)

    def mode_select_screen(self):
        if self.game.menu_state == 'main_menu':
            self.screen.fill(GREEN)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((50, 50, 50, 200))
            self.screen.blit(overlay, (0, 0))

            for button in self.game.menu_manager.buttons:
                button.visible = button.buttonText in ['play with PC', 'Change Name', 'Scoring List']
                button.draw(self.screen)

        elif self.game.menu_state == 'online_menu':
            self.screen.fill(GREEN)

            for button in self.game.menu_manager.buttons:
                button.visible = button.buttonText in ['Host Game', 'Join Game', 'Back']
                button.draw(self.screen)

    def closing_overlay(self, overlay, button_name):
        close_surf = FONT.render(f'Click "{button_name}" or press ESC to close', True, GRAY)
        overlay.blit(close_surf, close_surf.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

    def draw_change_name_overlay(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))

        title_surf = FONT.render('Change Name', True, WHITE)
        overlay.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 120)))

        input_rect = pygame.Rect(0, 0, 300, 50)
        input_rect.center = (WIDTH // 2, HEIGHT // 2 - 20)
        pygame.draw.rect(overlay, GRAY, input_rect, 2, border_radius=5)

        display_text = self.game.player_name + "|"
        name_surf = FONT.render(display_text, True, WHITE)
        overlay.blit(name_surf, name_surf.get_rect(center=input_rect.center))

        hint_surf = FONT.render('Press ENTER to save', True, GRAY)
        overlay.blit(hint_surf, hint_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

        self.closing_overlay(overlay, 'Change Name')

        self.screen.blit(overlay, (0, 0))

    def draw_scoring_list_overlay(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))

        title_surf = FONT.render('ALL SCORES', True, WHITE)
        overlay.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 80)))

        header_surf = FONT.render('Player       Mode       Score     Time                      Date', True, RED)
        overlay.blit(header_surf, (SCORING_TABLE_X, 100))

        all_scores = self.score_manager.get_all_scores() if hasattr(self.score_manager, 'get_all_scores') else []

        list_rect = pygame.Rect(0, 120, WIDTH, HEIGHT - 180)
        overlay.set_clip(list_rect)

        y_offset = 150 + self.scroll_y
        for entry in all_scores:
            if 150 <= y_offset <= HEIGHT - 95:
                name = entry.get('players', 'P1')
                mode = entry.get('mode', '-')
                score = entry.get('score', 0)
                time_str = entry.get('time', '--:--')
                date_str = entry.get('date', 'aaaa:mm:dd, hh:mm:ss')

                overlay.blit(FONT.render(name, True, WHITE), (SCORING_TABLE_X - 50, y_offset))
                overlay.blit(FONT.render(mode, True, WHITE), (SCORING_TABLE_X + 160, y_offset))
                overlay.blit(FONT.render(score, True, WHITE), (SCORING_TABLE_X + 360, y_offset))
                overlay.blit(FONT.render(time_str, True, WHITE), (SCORING_TABLE_X + 440, y_offset))
                overlay.blit(FONT.render(date_str, True, WHITE), (SCORING_TABLE_X + 640, y_offset))

            y_offset += 35

        overlay.set_clip(None)

        self.closing_overlay(overlay, 'Scoring List')

        self.screen.blit(overlay, (0, 0))

    def draw(self):
        is_in_menu = self.game.sub_menu or self.game.menu_state in ['main_menu', 'online_menu']

        if is_in_menu:
            scoring_btn_x = 450
            scoring_btn_y = 525
        else:
            scoring_btn_x = WIDTH - 300
            scoring_btn_y = 0

        self.game.menu_manager.set_button_pos('Scoring List', scoring_btn_x, scoring_btn_y)

        if is_in_menu:
            self.draw_menu(self.game.menu_state)
        else:
            self.game.screen.fill(GREEN)

            for button in self.game.menu_manager.buttons:
                btn_text = button.buttonText() if callable(button.buttonText) else button.buttonText

                button.visible = btn_text not in [
                    'online', 'play with PC', 'Change Name', 'Host Game', 'Join Game', 'Back'
                ]
                button.draw(self.game.screen)

            self.game.all_cards.draw(self.game.screen)

        if self.game.game_over:
            self.draw_game_over(self.game.get_remaining_cards())

        if getattr(self.game, 'show_scoring_list', False):
            self.draw_scoring_list_overlay()

        elif getattr(self.game, 'show_change_name_interface', False):
            self.draw_change_name_overlay()

        pygame.display.flip()


class MenuManager:
    def __init__(self, game):
        self.game = game
        self.buttons = []

    def set_button_pos(self, text, x, y):
        for button in self.game.menu_manager.buttons:
            btn_text = button.buttonText() if callable(button.buttonText) else button.buttonText
            if btn_text == text:
                button.x = x
                button.y = y
                if hasattr(button, 'rect'):
                    button.rect.x = x
                    button.rect.y = y
                    button.rect.topleft = (x, y)

    def scoring_list(self):
        current_state = getattr(self.game, 'show_scoring_list', False)
        self.game.show_scoring_list = not current_state

    def change_name(self):
        current_state = getattr(self.game, 'show_change_name_interface', False)
        self.game.show_change_name_interface = not current_state

    def get_buttons(self):
        # table
        Button(
            self.buttons,
            0, 0, 200, 50,
            'New Game',
            self.reset_button,
            True)
        Button(
            self.buttons,
            500, 250, 200, 50,
            buttonText= lambda: f'DECK: {self.game.get_remaining_cards()}',
            onlickFunction=self.game.get_remaining_cards,
            static_color=True
        )
        Button(
            self.buttons,225, 175, 200, 50,
               '100 pile', static_color=True
        )
        Button(
            self.buttons,
            775, 175, 200, 50,
            '100 pile', static_color=True
        )
        Button(
            self.buttons,
            225, 525, 150, 50,
            '1 pile', static_color=True
        )
        Button(
            self.buttons,
            825, 525, 150, 50,
            '1 pile', static_color=True
        )

        # main menu
        Button(
            self.buttons,
            500, 150, 200, 50,
            'online',
            self.open_online_menu,
            True
        )
        Button(
            self.buttons,
            450, 275, 300, 50,
            'play with PC',
            self.start_with_pc,
            True
        )
        Button(
            self.buttons,
            450, 400, 300, 50,
            'Change Name',
            self.change_name,
            True
        )
        Button(
            self.buttons,
            450, 525, 300, 50,
            'Scoring List',
            self.scoring_list,
            True
        )

        # under menu - online buttons
        Button(
            self.buttons,
            450, 250, 300, 50,
            'Host Game',
            self.start_host_game,
            True
        )
        Button(
            self.buttons,
            450, 375, 300, 50,
            'Join Game',
            self.start_join_game,
            True
        )
        Button(
            self.buttons,
            450, 500, 300, 50,
            'Back',
            self.back_to_main_menu,
            True
        )

        self.game.game_over = False

    def reset_button(self):
        self.game.reset_game()
        self.game.menu_state ='main_menu'
        self.game.with_pc = False
        self.game.game_over = False
        self.game.new_game_mode()

    def back_to_main_menu(self):
        self.game.menu_state = 'main_menu'
        self.game.selected_mode = None
        self.game.sub_menu = False
        self.game.new_game = True

    def open_online_menu(self):
        self.game.menu_state = 'online_menu'
        self.game.sub_menu = True

    def start_host_game(self):
        self.game.reset_game()
        self.game.selected_mode = 'online'
        self.game.menu_state = 'in_game'
        self.game.new_game = False

        print(f'Starting new game as HOST...')
        self.game.online.start_host()

    def start_join_game(self):
        self.game.selected_mode = 'online'
        self.game.new_game = False
        self.game.sub_menu = False

        print(f'Connecting with HOST...')
        self.game.online._connect_to_host("127.0.0.1")

    def start_with_pc(self):
        self.game.reset_game()
        self.game.selected_mode = 'with_pc'
        self.game.new_game = False
        self.game.sub_menu = False
        self.game.menu_state = 'in_game'
        self.game.with_pc = True
        self.start_timer()
        self.game.current_turn = 'player1'

    def start_timer(self):
        self.starting_time = time()

    def end_timer(self):
        ending_time = time()
        delta = ending_time - self.starting_time
        print(delta)

        minutes = int(delta // 60)
        seconds = int(delta % 60)
        milliseconds = int((delta - int(delta)) * 1000)
        return f'{minutes:02d}:{seconds:02d}:{milliseconds:03d}'


class InputHandler:
    def __init__(self, game):
        self.game = game

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if getattr(self.game, 'show_scoring_list', False):
                    if event.button == 4:
                        self.game.ui_manager.scroll_y = min(0, self.game.ui_manager.scroll_y + 35)
                    elif event.button == 5:
                        all_scores = self.game.score_manager.get_all_scores()
                        max_scroll = -max(0, len(all_scores) * 35 - (HEIGHT - 200))
                        self.game.ui_manager.scroll_y = max(max_scroll, self.game.ui_manager.scroll_y - 35)
                    elif event.button == 1:
                        self.check_menu_buttons(self.game.menu_manager.buttons, event)

                elif getattr(self.game, 'show_change_name_interface', False):
                    if event.button == 1:
                        self.check_menu_buttons(self.game.menu_manager.buttons, event)

                else:
                    self.mouse_events(event)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.game.menu_manager.scoring_list()

                if getattr(self.game, 'show_scoring_list', False):
                    if event.key == pygame.K_ESCAPE:
                        self.game.show_scoring_list = False

                elif getattr(self.game, 'show_change_name_interface', False):
                    self.handle_name_input_keys(event)

    def handle_name_input_keys(self, event):
        if event.key == pygame.K_ESCAPE:
            self.game.show_change_name_interface = False

        elif event.key == pygame.K_RETURN:
            if not self.game.player_name.strip():
                self.game.player_name = "PLAYER1"  # Fallback falls leer
            print(f"Neuer Name gespeichert: {self.game.player_name}")
            self.game.show_change_name_interface = False

        elif event.key == pygame.K_BACKSPACE:
            # Letzten Buchstaben löschen
            self.game.player_name = self.game.player_name[:-1]

        else:
            if len(self.game.player_name) < 10 and event.unicode.isprintable():
                self.game.player_name += event.unicode

    def mouse_events(self, event):
        if event.button == 1:
            button_clicked = self.check_menu_buttons(self.game.menu_manager.buttons, event)
            if not button_clicked and not (self.game.new_game or self.game.sub_menu):
                self.carry_out_cards_logic(event)

    def check_menu_buttons(self, button_objects, event):
        for button in button_objects:
            if button.visible and button.check_event(event):
                return True
        return False

    def carry_out_cards_logic(self, event):
        mouse_pos = event.pos
        card_clicked = self.check_selection(mouse_pos)

        if len(self.game.cards_in_hand) == 0 and self.game.get_remaining_cards() == 0 and len(
                self.game.player_2_cards_in_hand) == 0:
            print('no cards left\n\n ---GAME WON!!!--- \n\n')
            return

        if not card_clicked:
            is_deck_clicked = any(card.rect.collidepoint(mouse_pos) for card in self.game.deck_cards)
            if is_deck_clicked:
                if ((len(self.game.cards_in_hand) < MAX_CARDS_IN_HAND and self.game.get_remaining_cards() == 0) or
                        len(self.game.cards_in_hand) <= MAX_CARDS_IN_HAND_FOR_REFILL_EASY):
                    self.card_drawing(self.game.cards_in_hand, mouse_pos)
                else:
                    print('not enough cards laid out yet...')

            elif self.game.selected_card:
                for pile in self.game.piles.get_all_piles():
                    if len(pile) > 0:
                        top_card = pile.sprites()[-1]

                        if top_card.rect.collidepoint(mouse_pos):
                            self.game.staples_logic(top_card, pile, mouse_pos)
                            break

    def card_drawing(self, cards_in_hand,  mouse_pos,
                     max_cards_hand=MAX_CARDS_IN_HAND, max_cards_hand_easy=MAX_CARDS_IN_HAND_FOR_REFILL_EASY):
        deck_clicked = any(card.rect.collidepoint(mouse_pos) for card in self.game.deck_cards)
        if not deck_clicked or len(self.game.empty_hand_slot)==0:
            return

        for card in self.game.deck_cards:
            card_col_n_empty_hand_slot = card.rect.collidepoint(mouse_pos) and (len(self.game.empty_hand_slot) > 0)
            if len(cards_in_hand) < max_cards_hand and self.game.get_remaining_cards() == 0:
                print('no cards left to draw from the Deck pile... \nnext players turn...')
                self._finish_turn()

            elif len(cards_in_hand) <= max_cards_hand_easy:
                self._refill_player_hand()
                self._finish_turn()

    def _finish_turn(self):
        if self.game.with_pc:
            self.game.current_turn = 'pc'
            self.game.pc_timer = pygame.time.get_ticks()
        else:
            # logic for drawing online
            pass

    def _refill_player_hand(self):
        print('draw cards...')
        for x in range(len(self.game.empty_hand_slot)):
            if self.game.get_remaining_cards() == 0:
                break
            pos_x = self.game.empty_hand_slot[x]
            self.game.card_generator(
                self.game.cards_in_hand,
                pos_x,
                self.game.deck.draw_card(),
                600,
            )

        self.game.hand_cards.add(self.game.cards_in_hand)
        self.game.all_cards.add(self.game.cards_in_hand)
        self.game.empty_hand_slot.clear()

    def check_selection(self, mouse_pos):
        card_clicked = False
        for card in self.game.hand_cards:
            if card.rect.collidepoint(mouse_pos):
                if self.game.selected_card:
                    self.game.selected_card.deselect()

                self.game.selected_card = card
                self.game.selected_card_value = card.value
                self.game.selected_card.select()

                print(f'card {card.value} from hand selected...')
                card_clicked = True
                break
        return card_clicked

class Button:
    def __init__(self, button_list, x, y, width, height, buttonText='button pressed', onlickFunction=None, onePress=False, static_color=False):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.buttonText = buttonText
        self.onclickFunction = onlickFunction
        self.onePress = onePress
        self.visible = True
        self.static_color = static_color

        self.fillColors = {
            'normal': GREEN,
            'hover': BRIGHT_GREEN,
            'pressed': '#333333',
            'game_over': GRAY
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        button_list.append(self)

    def draw(self, screen):
        if not self.visible:
            return

        self.buttonRect.x = int(self.x)
        self.buttonRect.y = int(self.y)

        mousePos = pygame.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])

        if not self.static_color:
            if self.buttonRect.collidepoint(mousePos):
                self.buttonSurface.fill(self.fillColors['hover'])

        current_text = self.buttonText() if callable(self.buttonText) else self.buttonText
        text_surf = FONT.render(str(current_text), True, (20, 20, 20))

        self.buttonSurface.blit(text_surf, [
            self.buttonRect.width/2 - text_surf.get_rect().width/2,
            self.buttonRect.height/2 - text_surf.get_rect().height/2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)

    def check_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.buttonRect.collidepoint(event.pos):
                if callable(self.onclickFunction):
                    self.onclickFunction()
                    return True
        return False