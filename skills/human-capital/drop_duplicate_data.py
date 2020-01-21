# drop_duplicate_data.py
# -------
# Drops duplicate rows from CSV
import pandas as pd

df = pd.read_csv("crsp.csv")
# 'subset' specifies what row data is considered for duplicates
df = df.drop_duplicates(subset=['date', 'TICKER'], keep=False)
df.to_csv("crsp.csv", index=False)  # Optional line to overwrite CSV



