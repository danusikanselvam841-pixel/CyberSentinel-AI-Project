
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from url_features import extract_hostname

DATA_PATH = Path("url_data/malicious_phish.csv")
OUTPUT_DIR = Path("url_data/splits")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading dataset...")

df = pd.read_csv(
    DATA_PATH,
    usecols=["url", "type"]
)

df = df.dropna(subset=["url", "type"]).copy()
df["url"] = df["url"].astype(str).str.strip()
df["type"] = df["type"].astype(str).str.strip().str.lower()

df = df[df["url"] != ""]
df = df.drop_duplicates(subset=["url"]).reset_index(drop=True)

print("Extracting hostnames...")

df["hostname"] = df["url"].map(extract_hostname)

# Invalid hostnames are excluded
df = df[df["hostname"] != ""].reset_index(drop=True)

# Group by exact hostname
groups = df["hostname"]

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.30,
    random_state=42
)

train_idx, temp_idx = next(
    splitter.split(df, df["type"], groups)
)

train = df.iloc[train_idx].copy()
temp = df.iloc[temp_idx].copy()

second_splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.50,
    random_state=42
)

val_idx, test_idx = next(
    second_splitter.split(
        temp,
        temp["type"],
        temp["hostname"]
    )
)

validation = temp.iloc[val_idx].copy()
test = temp.iloc[test_idx].copy()

train.to_csv(OUTPUT_DIR / "train.csv", index=False)
validation.to_csv(OUTPUT_DIR / "validation.csv", index=False)
test.to_csv(OUTPUT_DIR / "test.csv", index=False)

print("\nDOMAIN-GROUPED SPLIT RESULTS")
print("Training:", len(train))
print("Validation:", len(validation))
print("Testing:", len(test))

print("\nTrain class distribution:")
print(train["type"].value_counts())

print("\nValidation class distribution:")
print(validation["type"].value_counts())

print("\nTest class distribution:")
print(test["type"].value_counts())

train_hosts = set(train["hostname"])
val_hosts = set(validation["hostname"])
test_hosts = set(test["hostname"])

print("\nHostname overlap:")
print("Train / Validation:", len(train_hosts & val_hosts))
print("Train / Test:", len(train_hosts & test_hosts))
print("Validation / Test:", len(val_hosts & test_hosts))
