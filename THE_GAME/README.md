# THE GAME
## Structure
```text
GameIdeas/
├── .github/
│   └── workflows/
│       └── build.yml
│
├── cards/                   # Directory for image files
├── stats.csv                # Highscore file
│
├── main.py                  # Entry point: initializes and runs the game
├── game.py                  # Main game class: game loop, event routing, state management
├── game_logic.py            # Game domain logic (Deck, PileGroup, move rules)
├── ui_manager.py            # HUD, rendering overlays, layout management
├── gpu.py                   # BOT decision-making logic
├── score_manager.py         # ScoreManager class (CSV file access)
├── card.py                  # Card sprite class (visuals & card attributes)
├── button.py                # Interactive UI button class
├── settings.py              # global constants (color, window sizes, paths)
```
## Playing Rules

Players in The Game try to `discard all 98 cards` in the deck onto four discard piles in order to win, but they need to do so in the right ways.

Each player `starts with 6` cards in their hand depending on the number of players, and four discard pile prompt cards are on the table: `two showing 1` and an up arrow and `two showing 100` and a down arrow. `On a turn`, a player must `discard at least two cards from their hand` onto one or more discard piles, with cards `on the 1 piles being placed in ascending` order and cards `on the 100 piles being placed in descending` order. One tricky aspect of the game is that you `can play a card exactly 10 higher/lower than the top card` of a discard pile even when you would normally have to play in a descending/ascending order, e.g., if a 100 discard pile is topped with an 87, you can play any card lower than 87 or you can play the 97.

After a player finishes their turn, they refill their hand from the deck. During play, `players cannot reveal exact numbers` in their hands, `but` they can `warn others not to play on certain discard piles or otherwise make play suggestions`.

Once the `deck is emptied`, players are required `only to play at least one card on a turn`. 

If you play all 98 cards, you win!

If `you get good`, the rules suggest that you `play at least three cards a turn` to increase the challenge.

