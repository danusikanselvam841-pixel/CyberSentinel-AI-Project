
import pandas as pd
from pathlib import Path

folder = Path("url_data")
files = list(folder.glob("*.csv"))

if not files:
    print("ERROR: No CSV file found in url_data folder.")
    raise SystemExit

file = files[0]

print("Dataset:", file.name)

df = pd.read_csv(file, nrows=5)

print("\nCOLUMN NAMES:")
print(df.columns.tolist())

print("\nFIRST 5 RECORDS:")
print(df.head().to_string(index=False))
