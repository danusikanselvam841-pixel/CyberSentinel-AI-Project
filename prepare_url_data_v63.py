
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd


SOURCE = Path("url_data/splits_v6/train.csv")
OUTPUT = Path("url_data/splits_v63/train.csv")


def normalize_url(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlsplit(url)

        hostname = (
            parsed.hostname or ""
        ).lower().rstrip(".")

        if not hostname:
            return ""

        result = hostname + (parsed.path or "")

        if parsed.query:
            result += "?" + parsed.query

        return result

    except (ValueError, TypeError):
        return ""


def main():
    print("CYBERSENTINEL AI V6.3 - DATA CLEANING")
    print("=" * 55)

    df = pd.read_csv(
        SOURCE,
        usecols=["url", "type"]
    ).dropna()

    print("Original training records:", len(df))

    df["normalized_url"] = (
        df["url"].map(normalize_url)
    )

    df = df[df["normalized_url"] != ""].copy()

    label_counts = (
        df.groupby("normalized_url")["type"]
        .nunique()
    )

    conflicting_urls = label_counts[
        label_counts > 1
    ].index

    print(
        "Conflicting normalized URLs:",
        len(conflicting_urls)
    )

    conflict_mask = df["normalized_url"].isin(
        conflicting_urls
    )

    print(
        "Records excluded:",
        int(conflict_mask.sum())
    )

    clean = df.loc[
        ~conflict_mask,
        ["url", "type"]
    ].copy()

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    clean.to_csv(
        OUTPUT,
        index=False
    )

    print("\nClean training records:", len(clean))

    print("\nCLASS DISTRIBUTION")
    print(clean["type"].value_counts())

    print("\nSaved:", OUTPUT)
    print("\nDATA PREPARATION COMPLETED")


if __name__ == "__main__":
    main()
