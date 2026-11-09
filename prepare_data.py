
from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path("data")
OUTPUT_DIR = Path("processed")
OUTPUT_DIR.mkdir(exist_ok=True)

CHUNK_SIZE = 10000
SAMPLES_PER_CLASS = 3000
RANDOM_SEED = 42

rng = np.random.default_rng(RANDOM_SEED)
reservoirs = {}
seen = {}

csv_files = sorted(DATA_DIR.rglob("*.csv"))

if not csv_files:
    raise FileNotFoundError("No CSV files found!")

print(f"Found {len(csv_files)} CSV files")

for file in csv_files:
    print(f"\nProcessing: {file.name}")

    for chunk in pd.read_csv(
        file,
        chunksize=CHUNK_SIZE,
        encoding="latin1",
        low_memory=False
    ):
        chunk.columns = chunk.columns.str.strip()

        if "Label" not in chunk.columns:
            raise ValueError(f"Label missing: {file.name}")

        chunk["Label"] = (
            chunk["Label"]
            .astype(str)
            .str.strip()
            .str.replace("\ufffd", "-", regex=False)
        )

        for label, group in chunk.groupby("Label", sort=False):
            if label not in reservoirs:
                reservoirs[label] = []
                seen[label] = 0

            for row in group.itertuples(index=False, name=None):
                seen[label] += 1
                count = seen[label]
                bucket = reservoirs[label]

                if len(bucket) < SAMPLES_PER_CLASS:
                    bucket.append(row)
                else:
                    j = int(rng.integers(0, count))
                    if j < SAMPLES_PER_CLASS:
                        bucket[j] = row

    print("Completed")

columns = pd.read_csv(
    csv_files[0],
    nrows=0,
    encoding="latin1"
).columns.str.strip().tolist()

frames = []

for label, rows in reservoirs.items():
    frame = pd.DataFrame(rows, columns=columns)
    frames.append(frame)

combined = pd.concat(frames, ignore_index=True)
combined = combined.replace([np.inf, -np.inf], np.nan)

combined = combined.sample(
    frac=1,
    random_state=RANDOM_SEED
).reset_index(drop=True)

output_file = OUTPUT_DIR / "sampled_dataset.csv"
combined.to_csv(output_file, index=False)

print("\nDataset prepared successfully!")
print("Total records:", len(combined))
print("\nClass distribution:")
print(combined["Label"].value_counts())
print("\nSaved to:", output_file)
