
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd
import tldextract

from sklearn.model_selection import GroupShuffleSplit

SOURCE = Path("url_data/malicious_phish.csv")
OUTPUT = Path("url_data/splits_v6")
SEED = 42

OUTPUT.mkdir(parents=True, exist_ok=True)

extractor = tldextract.TLDExtract(
    suffix_list_urls=()
)

print("Loading original dataset...")

df = pd.read_csv(
    SOURCE,
    usecols=["url", "type"]
)

df = df.dropna(subset=["url", "type"]).copy()

df["url"] = df["url"].astype(str).str.strip()
df["type"] = df["type"].astype(str).str.strip()

df = df[df["url"] != ""].copy()

# Remove exact duplicates
df = df.drop_duplicates(subset=["url"])

print("Total unique URLs:", len(df))


def get_registrable_domain(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    try:
        host = urlsplit(url).hostname or ""
    except ValueError:
        return ""

    host = host.lower().rstrip(".")

    if not host:
        return ""

    result = extractor(host)

    if result.domain and result.suffix:
        return result.domain + "." + result.suffix

    return host


print("Extracting registrable domains...")

df["domain"] = df["url"].map(
    get_registrable_domain
)

# Invalid URLs are excluded from this experiment
invalid_count = (df["domain"] == "").sum()

df = df[df["domain"] != ""].copy()

print("Invalid domains excluded:", invalid_count)

# Group-aware train / temporary split
splitter1 = GroupShuffleSplit(
    n_splits=1,
    train_size=0.70,
    random_state=SEED
)

train_idx, temp_idx = next(
    splitter1.split(
        df,
        groups=df["domain"]
    )
)

train = df.iloc[train_idx].copy()
temp = df.iloc[temp_idx].copy()

# Split temporary set into validation and test
splitter2 = GroupShuffleSplit(
    n_splits=1,
    train_size=0.50,
    random_state=SEED
)

val_idx, test_idx = next(
    splitter2.split(
        temp,
        groups=temp["domain"]
    )
)

validation = temp.iloc[val_idx].copy()
test = temp.iloc[test_idx].copy()

datasets = {
    "train": train,
    "validation": validation,
    "test": test
}

print("\nV6 DATASET SUMMARY")

for name, data in datasets.items():
    print(f"\n{name.upper()}")
    print("Rows:", len(data))
    print("Unique domains:", data["domain"].nunique())
    print(data["type"].value_counts().to_string())

    data[["url", "type"]].to_csv(
        OUTPUT / f"{name}.csv",
        index=False
    )


print("\nDOMAIN OVERLAP CHECK")

pairs = [
    ("train", "validation"),
    ("train", "test"),
    ("validation", "test")
]

for a, b in pairs:
    overlap = (
        set(datasets[a]["domain"])
        & set(datasets[b]["domain"])
    )

    print(f"{a} vs {b}: {len(overlap)}")

    assert len(overlap) == 0, (
        f"Domain leakage found: {a} vs {b}"
    )

print("\nV6 SPLIT CREATED SUCCESSFULLY")
