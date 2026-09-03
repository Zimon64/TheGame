import pygame
from settings import GREEN, BRIGHT_GREEN, GRAY, FONT

button_objects = []

class Button():
    def __init__(self, x, y, width, height, buttonText='button pressed', onlickFunction=None, onePress=False):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.buttonText = buttonText
        self.onclickFunction = onlickFunction
        self.onePress = onePress
        self.visible = True

        self.fillColors = {
            'normal': GREEN,
            'hover': BRIGHT_GREEN,
            'pressed': '#333333',
            'game_over': GRAY
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        button_objects.append(self)

    def draw(self, screen):
        """Reines Zeichnen des Buttons - KEINE Klick-Logik hier!"""
        if not self.visible:
            return

        mousePos = pygame.mouse.get_pos()
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
        else:
            self.buttonSurface.fill(self.fillColors['normal'])

        current_text = self.buttonText() if callable(self.buttonText) else self.buttonText
        text_surf = FONT.render(str(current_text), True, (20, 20, 20))

        self.buttonSurface.blit(text_surf, [
            self.buttonRect.width/2 - text_surf.get_rect().width/2,
            self.buttonRect.height/2 - text_surf.get_rect().height/2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)

    def check_event(self, event):
        """Wird NUR bei einem echten MOUSEBUTTONDOWN Event aufgerufen"""
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.buttonRect.collidepoint(event.pos):
                if callable(self.onclickFunction):
                    self.onclickFunction()
                    return True
        return False