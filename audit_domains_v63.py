
import pandas as pd
from urllib.parse import urlsplit

TRAIN_PATH = "url_data/splits_v6/train.csv"
VAL_PATH = "url_data/splits_v6/validation.csv"

DOMAINS = [
    "google.com",
    "github.com",
    "microsoft.com",
    "wikipedia.org",
    "example.com"
]


def get_hostname(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    try:
        return (
            urlsplit(url).hostname or ""
        ).lower().rstrip(".")
    except ValueError:
        return ""


def audit_dataset(path, name):
    print(f"\n{name}")
    print("=" * 60)

    df = pd.read_csv(
        path,
        usecols=["url", "type"]
    ).dropna()

    df["hostname"] = df["url"].map(get_hostname)

    for domain in DOMAINS:
        mask = (
            (df["hostname"] == domain)
            | df["hostname"].str.endswith(
                "." + domain
            )
        )

        matches = df.loc[mask]

        print(f"\nDomain: {domain}")
        print("Matching URLs:", len(matches))

        if len(matches):
            print(
                matches["type"]
                .value_counts()
                .to_string()
            )
        else:
            print("No matching URLs")


print("CYBERSENTINEL AI - DOMAIN COVERAGE AUDIT")

audit_dataset(TRAIN_PATH, "TRAINING DATA")
audit_dataset(VAL_PATH, "VALIDATION DATA")

print("\nAUDIT COMPLETED")
