import gymnasium as gym
from gymnasium import spaces
import numpy as np
import torch

from game import Game
from game_logic import Rules


class TheGameEnv(gym.Env):
    """
    RL Environment für 'The Game', das als Brücke zwischen Pygame/Game-Logik
    und dem PyTorch Modell dient.
    """
    metadata = {'render_modes': ['human']}

    def __init__(self, with_gui=False):
        super(TheGameEnv, self).__init__()

        # Initialisiere die Spiel-Instanz
        self.game = Game()
        self.game.with_pc = True
        self.with_gui = with_gui

        # -------------------------------------------------------------
        # 1. ACTION SPACE (Welche Aktionen kann die KI ausführen?)
        # -------------------------------------------------------------
        # Aktionen sind eine Auswahl aus: (Handkarten-Index x Stapel-Index) + Spezial-Aktionen (z.B. Zug beenden)
        # Max Handkarten: 6, Stapel: 4 -> 6 * 4 = 24 Legemöglichkeiten + 1 "Zug beenden/Nachziehen"
        self.action_space = spaces.Discrete(25)

        # -------------------------------------------------------------
        # 2. OBSERVATION SPACE (Was "sieht" die KI als Input?)
        # -------------------------------------------------------------
        # Wir übergeben dem Netz einen Vektor mit normierten Werten (0.0 bis 1.0):
        # - 4 Stapelwerte (normiert auf 1-100)
        # - 6 Handkarten der KI (normiert auf 0-100, 0 = leeres Slot)
        # - Verbleibende Deck-Karten (normiert auf 0-98)
        # - Bereits gelegte Karten in diesem Zug (0 bis 6)
        # Insgesamt 12 Zahlenwerte
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(12,), dtype=np.float32
        )

        self.cards_played_this_turn = 0

    def reset(self, seed=None, options=None):
        """Setzt das Spiel für eine neue Episode zurück."""
        super().reset(seed=seed)

        self.game.reset_game()
        self.game.current_turn = 'player1'
        self.cards_played_this_turn = 0

        observation = self._get_observation()
        info = {}
        return observation, info

    def _get_observation(self):
        """Wandelt den aktuellen Game-State in ein Float-Array für PyTorch um."""
        piles = self.game.piles.get_all_piles()
        pile_vals = [p.sprites()[-1].value / 100.0 for p in piles]

        # KI Handkarten (Player 1 oder Player 2 je nach Perspektive)
        hand = self.game.player_2_cards_in_hand
        hand_vals = [(c.value / 100.0) if c else 0.0 for c in hand]

        # Ergänze auf 6 Slots, falls weniger Karten auf der Hand sind
        while len(hand_vals) < 6:
            hand_vals.append(0.0)

        deck_left = self.game.get_remaining_cards() / 98.0
        turn_progress = self.cards_played_this_turn / 6.0

        obs = np.array(pile_vals + hand_vals + [deck_left, turn_progress], dtype=np.float32)
        return obs

    def step(self, action):
        """
        Führt eine Aktion der KI aus und berechnet Reward, Done-Status & neuen State.
        """
        reward = 0.0
        terminated = False
        truncated = False

        # Action 24: Zug beenden / Nachziehen
        if action == 24:
            if self.cards_played_this_turn >= 2 or self.game.get_remaining_cards() == 0:
                reward += 2.0  # Belohnung für regelkonformes Beenden
                self._finish_turn()
            else:
                reward -= 10.0  # Bestrafung: Versucht Zug zu beenden ohne mindestens 2 Karten zu legen
        else:
            # Karte und Stapel dekodieren
            card_idx = action // 4
            pile_idx = action % 4

            pc_hand = self.game.player_2_cards_in_hand
            piles = self.game.piles.get_all_piles()

            if card_idx < len(pc_hand):
                selected_card = pc_hand[card_idx]
                target_pile = piles[pile_idx]
                top_card = target_pile.sprites()[-1]

                # Regelprüfung via deine Rules-Klasse
                if Rules.is_valid_move(target_pile.name, top_card.value, selected_card.value):
                    diff = abs(selected_card.value - top_card.value)

                    # 1. Belohnungs-Logik
                    if diff == 10:  # Rücksprung-Bonus (+10/-10)
                        reward += 20.0
                    else:
                        # Je kleiner der Abstand zum Stapel, desto höher die Belohnung
                        reward += max(1.0, (15.0 - diff))

                    # Zug ausführen
                    self.game.selected_card = selected_card
                    self.game.piles.move_card_to_pile(top_card, target_pile)
                    self.cards_played_this_turn += 1

                else:
                    reward -= 5.0  # Bestrafung für ungültigen Zug
            else:
                reward -= 5.0  # Bestrafung: Ungültiger Karten-Index gewählt

        # 2. Prüfen ob Spiel gewonnen oder verloren
        if self.game.game_over:
            terminated = True
            reward -= 50.0  # Game Over Bestrafung
        elif len(self.game.cards_in_hand) == 0 and len(
                self.game.player_2_cards_in_hand) == 0 and self.game.get_remaining_cards() == 0:
            terminated = True
            reward += 200.0  # Sieges-Bonus!

        observation = self._get_observation()
        return observation, reward, terminated, truncated, {}

    def _finish_turn(self):
        """Simuliert den Zug des Mitspielers oder füllt die Hand wieder auf."""
        self.game.refill_pc_hand()
        self.cards_played_this_turn = 0
        # Hier kann optional die Mitspieler-Aktion (Mensch oder 2. KI) aufgerufen werden

    def render(self):
        """Optional: Rendert Pygame, wenn man dem KI-Training zuschauen möchte."""
        if self.with_gui:
            self.game.ui_manager.draw()
            self.game.clock.tick(60)