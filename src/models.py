import os
import pygame
from settings import CARDS_DIR, CARD_WIDTH, CARD_HEIGHT

class Card(pygame.sprite.Sprite):
    def __init__(self, value, x, y):
        super().__init__()
        self.value = value
        self.x = float(x)
        self.y = float(y)
        self.target_x = float(x)
        self.target_y = float(y)
        self.speed = 15

        image_path = os.path.join(CARDS_DIR, f'{value}.png')

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
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance <= self.speed:
                self.x = self.target_x
                self.y = self.target_y
                self.rect.topleft = (int(self.x), int(self.y))

                if hasattr(self, 'target_pile_card') and self.target_pile_card:
                    self.target_pile_card.value = self.value

                    image_path = os.path.join(CARDS_DIR, f'{self.value}.png')
                    try:
                        raw_image = pygame.image.load(image_path).convert_alpha()
                        self.target_pile_card.original_image = pygame.transform.scale(raw_image,
                                                                                      (CARD_WIDTH, CARD_HEIGHT))
                        self.target_pile_card.image = self.target_pile_card.original_image.copy()
                    except (pygame.error, FileNotFoundError):
                        pass

                self.kill()
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