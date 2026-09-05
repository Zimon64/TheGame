import pygame

from settings import WIDTH, HEIGHT, GREEN, RED, WHITE, FONT
from button import button_objects, Button

class UIManager(object):
    def __init__(self, game, screen, score_manager):
        self.game = game
        self.screen = screen
        self.score_manager = score_manager

    def draw_game_over(self, score: int):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((50, 50, 50, 200))

        text_game_over = FONT.render('GAME OVER', True, RED)
        rect_game_over = text_game_over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))

        text_score = FONT.render(f'Current Score: {score}', True, WHITE)
        rect_score = text_score.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))

        text_highscore = FONT.render(f'Highscore: {self.score_manager.get_best_score()}', True, WHITE)
        rect_highscore = text_score.get_rect(center=(WIDTH // 5, HEIGHT // 2 + 90))

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

            for button in button_objects:
                button.visible = button.buttonText in ['online', 'play with PC']
                button.draw(self.screen)

        elif menu_state == 'online_menu':
            for button in button_objects:
                button.visible = button.buttonText in ['Host Game', 'Join Game', 'Back']
                button.draw(self.screen)

    def mode_select_screen(self):
        if self.game.menu_state == 'main_menu':
            self.screen.fill(GREEN)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((50, 50, 50, 200))
            self.screen.blit(overlay, (0, 0))

            for button in button_objects:
                button.visible = button.buttonText in ['online', 'play with PC']
                button.draw(self.screen)

        elif self.game.menu_state == 'online_menu':
            self.screen.fill(GREEN)

            for button in button_objects:
                button.visible = button.buttonText in ['Host Game', 'Join Game', 'Back']
                button.draw(self.screen)

    def draw(self):
        if self.game.new_game or self.game.sub_menu:
            self.game.ui_manager.draw_menu(self.game.menu_state)
        else:
            self.game.screen.fill(GREEN)

            for button in button_objects:
                button.visible = button.buttonText not in ['online', 'play with PC', 'Host Game', 'Join Game', 'Back']
                button.draw(self.game.screen)

            self.game.all_cards.draw(self.game.screen)

        if self.game.game_over:
            self.game.ui_manager.draw_game_over(self.game.get_remaining_cards())

        pygame.display.flip()


class MenuManager:
    def __init__(self, game):
        self.game = game

    def get_buttons(self):
        # table
        Button(
            0, 0, 200, 50,
            'New Game',
            self.reset_button,
            True)
        Button(
            500, 250, 200, 50,
            buttonText= lambda: f'DECK: {self.game.get_remaining_cards()}',
            onlickFunction=self.game.get_remaining_cards,
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

        self.game.game_over = False

    def reset_button(self):
        self.game.reset_game()
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
        self.game.with_pc = True
        self.game.current_turn = 'player1'
