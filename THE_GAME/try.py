import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 1. Aussehen festlegen
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))  # Grünes Quadrat

        # 2. Position & Kollisionsbox festlegen
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # 3. Eigene Eigenschaften
        self.speed = 5

    def handle_input(self):
        """Reagiert auf Tastatureingaben."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

    def update(self):
        """Wird in jedem Frame aufgerufen, um den Zustand zu aktualisieren."""
        self.handle_input()


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True

        # Sprite-Gruppen verwalten alle Objekte zentral
        self.all_sprites = pygame.sprite.Group()

        # Objekt instanziieren und zur Gruppe hinzufügen
        self.player = Player(400, 300)
        self.all_sprites.add(self.player)

    def run(self):
        """Die Hauptschleife des Spiels."""
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS

        pygame.quit()

    def events(self):
        """Verarbeitet System-Events (z. B. Fenster schließen)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """Aktualisiert alle Objekte automatisch."""
        self.all_sprites.update()  # Ruft update() bei allen Sprites auf

    def draw(self):
        """Zeichnet das Spiel."""
        self.screen.fill((30, 30, 30))  # Hintergrund leeren
        self.all_sprites.draw(self.screen)  # Alle Sprites zeichnen
        pygame.display.flip()


# Spiel starten
if __name__ == "__main__":
    game = Game()
    game.run()