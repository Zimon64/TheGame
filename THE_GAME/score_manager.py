import os
import csv
import numpy as np
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
        best_time_ms = float('inf')

        with open(self.filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    score_val = int(row['score'])
                    time_ms = self.time_to_ms(row['time'])
                    
                    if (score_val < best_score) or (score_val == best_score and time_ms < best_time_ms):
                        best_score = score_val
                        best_time_ms = time_ms
                        best_row = row
                except (ValueError, KeyError):
                    continue

        if best_row:
            return f"{best_row['score']} [{best_row['players']} - time: {best_row['time']} - mode: {best_row['mode']}]"

        return None

    def time_to_ms(self, time_str: str) -> int:
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds = int(parts[1])
        milliseconds = int(parts[2])
        return (minutes * 60 * 1000) + (seconds * 1000) + milliseconds