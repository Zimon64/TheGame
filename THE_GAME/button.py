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
        text_surf = FONT.render(str(current_text), True, (20, 20, 20))

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