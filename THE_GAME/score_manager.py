import os
import pandas as pd
from datetime import datetime

class ScoreManager:
    def __init__(self, filename='stats.csv'):
        self.filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            df = pd.DataFrame(
                columns=[
                    'date',
                    'score',
                    'players',
                    'mode'
                ]
            )
            df.to_csv(self.filename, index=False)

    def save_score(self, score, player, mode):
        df = pd.read_csv(self.filename)
        new_entry = pd.DataFrame([{
            'date': datetime.now().strftime('%Y-%m-%d, %H:%M:%S'),
            'score': score,
            'players': player,
            'mode': mode,
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(self.filename, index=False)
        print(f'Score {score} saved successfully! \n')

    def get_best_score(self):
        df = pd.read_csv(self.filename)
        if df.empty:
            return None

        hsr = df.loc[df['score'] == min(df['score'])]

        date = str(hsr['date'].iloc[0])
        score = int(hsr['score'].iloc[0])
        player = str(hsr['players'].iloc[0])
        mode = str(hsr['mode'].iloc[0])
        return f'{score} ({player} @ {date} - mode: {mode})'