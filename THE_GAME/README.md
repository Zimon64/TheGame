# THE GAME
## Structure
```text
GameIdeas/
├── .github/
│   └── workflows/
│       └── build.yml
│
├── cards/                   # directory for image files
├── stats.csv                # highscore file
│
├── main.py                  # starting the game
├── settings.py              # global constants (color, window sizes, paths)
├── card.py                  # Card class
├── button.py                # Button class
├── score_manager.py         # ScoreManager class (CSV file access)
├── gpu.py                   # GPU / bot-logic
└── game.py                  # Game class (main-game-loop & state)
```
## Playing Rules

