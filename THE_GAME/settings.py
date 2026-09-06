import os
import pygame

# colors
WIDTH = 1200
HEIGHT = 800
GREEN = (0, 125, 0)
DARK_GREEN = (0, 50, 0)
BRIGHT_GREEN = (0, 175, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)

# cards
CARD_WIDTH = 100
CARD_HEIGHT = 200
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(BASE_DIR, 'cards')
MAX_CARDS_IN_HAND = 6
MAX_CARDS_IN_HAND_FOR_REFILL_EASY = MAX_CARDS_IN_HAND - 2
FIRST_HAND_POS_X = 300
HAND_UPPER_PLAYER_POS_Y = -100

remaining_cards = sorted(list(range(2, 100)))
# remaining_cards = sorted(list(range(2,8)))

# fonts
pygame.font.init()
FONT =  pygame.font.SysFont('Cambria', 40)

# bot
BOT_TIMER = 600

# scoring table
SCORING_TABLE_X = 100