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