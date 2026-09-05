import os
import csv
from datetime import datetime

from ui_manager import MenuManager

class ScoreManager:
    def __init__(self, filename='stats.csv'):
        self.filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['date', 'score', 'players', 'mode', 'time'])

    def save_score(self, score, player, mode, elapsed_time):
        date_str = datetime.now().strftime('%Y-%m-%d, %H:%M:%S')
        with open(self.filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([date_str, score, player, mode, elapsed_time])
        print(f'Score {score} saved successfully! \n')

    def get_best_score(self):
        if not os.path.exists(self.filename):
            return None

        best_row = None
        best_score = float('inf')

        with open(self.filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    score_val = int(row['score'])
                    if score_val < best_score:
                        best_score = score_val
                        best_row = row
                except (ValueError, KeyError):
                    continue

        if best_row:
            date = str(best_row['date'])
            score = int(best_row['score'])
            player = str(best_row['players'])
            mode = str(best_row['mode'])
            time = str(best_row['time'])
            return f'{score} [{player} - time: {time} - mode: {mode}]'

        return None