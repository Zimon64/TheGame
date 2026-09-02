#!/home/simon/PycharmProjects/GameIdeas/.venv/bin/python

import os
import random
# import pandas as pd

import pygame
from pygame.constants import MOUSEBUTTONDOWN

# Globale Konfigurationen
WIDTH = 1200
HEIGHT = 800
GREEN = (0, 125, 0)
DARK_GREEN = (0, 50, 0)
BRIGHT_GREEN = (0, 175, 0)
RED = (255, 0, 0)
BLACK = (255, 255, 255)
GRAY = (50, 50, 50)

CARD_WIDTH = 100
CARD_HEIGHT = 200

# Pfad zu den Karten
CARDS_DIR = os.path.join(os.getcwd(), 'cards')

remaining_cards = sorted(list(range(2, 100)))

pygame.font.init()
font =  pygame.font.SysFont('Arial', 40)

button_objects = []


class Card(pygame.sprite.Sprite):
    def __init__(self, value, x, y):
        super().__init__()
        self.value = value
        self.x = float(x)
        self.y = float(y)
        self.target_x = float(x)
        self.target_y = float(y)
        self.speed = 15

        # Bild laden und auf die richtige Größe skalieren
        image_path = os.path.join(CARDS_DIR, f'{value}.png')

        # Fallback-Oberfläche, falls das Bild fehlt (Fehlervermeidung)
        try:
            raw_image = pygame.image.load(image_path).convert_alpha()
            self.original_image = pygame.transform.scale(raw_image, (CARD_WIDTH, CARD_HEIGHT))
        except (pygame.error, FileNotFoundError):
            # Erstellt eine weiße Ersatzkarte, falls das Bild nicht geladen werden kann
            self.original_image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            self.original_image.fill((255, 255, 255))

        self.image = self.original_image.copy()
        self.rect = self.original_image.get_rect()
        self.rect.topleft = (int(self.x), int(self.y))
        self.is_selected = False

        self.card_to_destroy = None

    def update(self):
        if self.x != self.target_x or self.y != self.target_y:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = (dx**2 + dy**2) ** 0.5

            if distance <= self.speed:
                self.x = self.target_x
                self.y = self.target_y

                if self.card_to_destroy:
                    self.card_to_destroy.kill()
                    self.card_to_destroy = None
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed

            self.rect.topleft = (int(self.x), int(self.y))

    def move_to(self, target_x, target_y):
        self.target_x = float(target_x)
        self.target_y = float(target_y)

    def _make_grayscale(self, surface):
        gray_surface = surface.copy()
        dark_overlay = pygame.Surface(gray_surface.get_size(), flags=pygame.SRCALPHA)
        dark_overlay.fill((50, 50, 50, 180))

        gray_surface.blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        return gray_surface

    def select(self):
        self.is_selected = True
        self.image = self._make_grayscale(self.original_image)

    def deselect(self):
        self.is_selected = False
        self.image = self.original_image.copy()

class Button():
    def __init__(self, x, y, width, height, buttonText='button pressed', onlickFunction=None, onePress=False):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.buttonText = buttonText
        self.onclickFunction = onlickFunction
        self.onePress = onePress
        self.alreadyPressed = False

        self.fillColors = {
            'normal': GREEN,
            'hover': BRIGHT_GREEN,
            'pressed': '#333333',
            'game_over': GRAY
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        button_objects.append(self)

    def process(self, screen):
        mousePos = pygame.mouse.get_pos()
        if self.buttonText == 'GAME OVER':
            self.buttonSurface.fill(self.fillColors['game_over'])
        else:
            self.buttonSurface.fill(self.fillColors['normal'])

        current_text = self.buttonText() if callable(self.buttonText) else self.buttonText
        text_surf = font.render(str(current_text), True, (20, 20, 20))

        if self.buttonRect.collidepoint(mousePos) and self.onePress:
            self.buttonSurface.fill(self.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    self.onclickFunction()
                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(text_surf, [
            self.buttonRect.width/2 - text_surf.get_rect().width/2,
            self.buttonRect.height/2 - text_surf.get_rect().height/2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)


class Scores():
    def __init__(self):
        self.score = 0


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("THE GAME")
        self.clock = pygame.time.Clock()
        self.running = True

        self.selected_card = None

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
        self.reset_game()

        self.pile_cards_100_left.name = 'pile_cards_100_left'
        self.pile_cards_100_right.name = 'pile_cards_100_right'
        self.pile_cards_1_left.name = 'pile_cards_1_left'
        self.pile_cards_1_right.name = 'pile_cards_1_right'

    def get_buttons(self):
        # Button(30, 30, 400, 100, 'Button One (onePress)', self.my_function)
        Button(
            0, 0, 200, 50,
            'New Game',
            self.reset_game,
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

        self.game_over = False

    def get_remaining_cards(self):
        return len(self.remaining_cards)

    def reset_game(self):
        print('resetting the game...')
        self.game_over = False

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
                    mouse_pos = event.pos
                    print('left click')

                    # select card
                    card_clicked = False
                    self.check_selection(mouse_pos)

                    # draw cards from the deck until hand is full
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
        self.pile_sets = [
            self.pile_cards_100_left,
            self.pile_cards_100_right,
            self.pile_cards_1_left,
            self.pile_cards_1_right,
        ]
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

    def update(self):
        self.all_cards.update()

    def move_card(self, target_pile_card, target_group):
        if not self.selected_card:
            return

        self.cards_in_hand.remove(self.selected_card)
        self.empty_hand_slot.append(self.selected_card.x)

        self.selected_card.deselect()
        self.hand_cards.remove(self.selected_card)

        self.selected_card.move_to(target_pile_card.rect.x, target_pile_card.rect.y)

        self.selected_card.card_to_destroy = target_pile_card

        target_group.remove(target_pile_card)
        target_group.add(self.selected_card)

        self.all_cards.remove(self.selected_card)
        self.all_cards.add(self.selected_card)


        self.selected_card = None

    def draw(self):
        self.screen.fill(GREEN)

        # Alle Karten auf den Bildschirm zeichnen
        self.all_cards.draw(self.screen)

        for button in button_objects:
            button.process(screen=self.screen)

        if self.game_over:# 1. Halbtransparentes Overlay über das gesamte Fenster
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((50, 50, 50, 200))  # Rot mit 200/255 Transparenz

            # 2. Zeile 1: GAME OVER
            text_game_over = font.render('GAME OVER', True, RED)
            rect_game_over = text_game_over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))

            # 3. Zeile 2: Current Score
            score_text = f'Current Score: {self.get_remaining_cards()}'
            text_score = font.render(score_text, True, RED)
            rect_score = text_score.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))

            # 4. Beides auf das Overlay blitten
            overlay.blit(text_game_over, rect_game_over)
            overlay.blit(text_score, rect_score)

            self.screen.blit(overlay, (0, 0))

        pygame.display.flip()

    def run(self):
        # Hauptschleife
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(60)

        # Erst nach Verlassen der Schleife das Spiel sauber beenden!
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()