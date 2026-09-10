import pandas as pd

data = {
    'date': [],
    'score': [],
    'players': [],
    'mode': [],
    'time': []
}

df = pd.DataFrame(data)

print(df)

df.to_csv('stats.csv', index=False)




class Engine:
    def __init__(self, game_instance):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dein Spieltitel")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game = game_instance

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.game.handle_event(event)

    def update(self):
        self.game.update()

    def render(self):
        self.screen.fill((30, 30, 30))
        self.game.draw(self.screen)
        pygame.display.flip()


class TurnManager:
    def __init__(self, players):
        self.players = players
        self.current_player_index = 0
        self.turn_count = 1


    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.current_player_index == 0:
            self.turn_count += 1

    def reset(self):
        self.current_player_index = 0
        self.turn_count = 1