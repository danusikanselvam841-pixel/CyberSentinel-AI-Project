
from pathlib import Path
from urllib.parse import urlsplit
import pandas as pd

DATA_DIR = Path("url_data/splits")
FILES = ["train.csv", "validation.csv", "test.csv"]

EXPECTED_CLASSES = {
    "benign",
    "phishing",
    "malware",
    "defacement"
}

def hostname(url):
    url = str(url).strip()

    if not url:
        return ""

    if "://" not in url:
        url = "http://" + url

    try:
        return (urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""


def load_split(filename):
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing dataset: {path}"
        )

    df = pd.read_csv(
        path,
        usecols=["url", "type"]
    )

    df = df.dropna(subset=["url", "type"]).copy()

    df["url"] = df["url"].astype(str).str.strip()
    df["type"] = df["type"].astype(str).str.strip()

    df = df[df["url"] != ""].copy()
    df["hostname"] = df["url"].map(hostname)

    return df


print("=" * 55)
print("CYBERSENTINEL AI V6 - DATA QUALITY AUDIT")
print("=" * 55)

datasets = {}

for filename in FILES:
    name = filename.replace(".csv", "")
    df = load_split(filename)
    datasets[name] = df

    print(f"\n{name.upper()}")
    print("-" * 40)
    print("Rows:", len(df))
    print("Duplicate URLs:", df["url"].duplicated().sum())
    print("Missing hostnames:", (df["hostname"] == "").sum())
    print("Unique hostnames:", df["hostname"].nunique())

    print("\nClass distribution:")
    print(df["type"].value_counts().to_string())

    unknown = set(df["type"]) - EXPECTED_CLASSES

    if unknown:
        print("WARNING: Unknown labels:", unknown)
    else:
        print("Labels: OK")

    conflicts = (
        df.groupby("url")["type"]
        .nunique()
        .gt(1)
        .sum()
    )

    print("Conflicting URL labels:", conflicts)


print("\n" + "=" * 55)
print("CROSS-SPLIT CHECKS")
print("=" * 55)

pairs = [
    ("train", "validation"),
    ("train", "test"),
    ("validation", "test")
]

for left, right in pairs:
    a = datasets[left]
    b = datasets[right]

    url_overlap = (
        set(a["url"]) & set(b["url"])
    )

    host_overlap = (
        set(a["hostname"]) - {""}
    ) & (
        set(b["hostname"]) - {""}
    )

    print(f"\n{left} vs {right}")
    print("Overlapping URLs:", len(url_overlap))
    print("Overlapping hostnames:", len(host_overlap))


print("\n" + "=" * 55)
print("AUDIT COMPLETED")
print("=" * 55)
