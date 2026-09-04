import pygame
from settings import WIDTH, HEIGHT, GREEN, RED, WHITE, FONT
from button import button_objects

class UIManager(object):
    def __init__(self, screen, score_manager):
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
