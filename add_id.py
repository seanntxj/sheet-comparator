import pandas as pd

df = pd.read_csv(f'first_csv.csv', dtype=object)
df.to_csv(f'f', index=True)