
import pandas as pd
from urllib.parse import urlsplit

PATH = "url_data/splits_v6/train.csv"

DOMAINS = [
    "google.com",
    "microsoft.com",
    "wikipedia.org"
]


def parse_url(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlsplit(url)

        hostname = (
            parsed.hostname or ""
        ).lower().rstrip(".")

        return pd.Series({
            "hostname": hostname,
            "path_length": len(parsed.path or ""),
            "query_length": len(parsed.query or ""),
            "has_query": int(bool(parsed.query)),
            "has_path": int(bool(parsed.path))
        })

    except ValueError:
        return pd.Series({
            "hostname": "",
            "path_length": 0,
            "query_length": 0,
            "has_query": 0,
            "has_path": 0
        })


print("Loading training data...")

df = pd.read_csv(
    PATH,
    usecols=["url", "type"]
).dropna()

parsed = df["url"].apply(parse_url)

df = pd.concat(
    [df, parsed],
    axis=1
)

for domain in DOMAINS:
    mask = (
        (df["hostname"] == domain)
        | df["hostname"].str.endswith(
            "." + domain
        )
    )

    subset = df.loc[mask]

    print("\n" + "=" * 65)
    print("DOMAIN:", domain)
    print("TOTAL:", len(subset))

    print("\nLABEL DISTRIBUTION")
    print(subset["type"].value_counts())

    print("\nAVERAGE URL STRUCTURE BY LABEL")

    print(
        subset.groupby("type")[
            [
                "path_length",
                "query_length",
                "has_query",
                "has_path"
            ]
        ].mean().round(2)
    )

    print("\nTOP HOSTNAMES BY LABEL")

    for label in subset["type"].unique():
        print("\nLabel:", label)

        print(
            subset.loc[
                subset["type"] == label,
                "hostname"
            ].value_counts().head(5)
        )

print("\nPATTERN ANALYSIS COMPLETED")
