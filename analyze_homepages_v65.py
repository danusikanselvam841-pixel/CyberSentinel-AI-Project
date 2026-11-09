
import pandas as pd
from urllib.parse import urlsplit

PATH = "url_data/splits_v63/train.csv"


def get_homepage_info(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlsplit(url)

        hostname = parsed.hostname or ""

        is_homepage = (
            hostname != ""
            and parsed.path in ("", "/")
            and not parsed.query
            and not parsed.fragment
            and parsed.username is None
        )

        return is_homepage

    except (ValueError, TypeError):
        return False


print("Loading cleaned training dataset...")

df = pd.read_csv(
    PATH,
    usecols=["url", "type"]
).dropna()

df["is_homepage"] = (
    df["url"].map(get_homepage_info)
)

print("\nTOTAL TRAINING RECORDS:", len(df))

print("\nHOMEPAGE DISTRIBUTION")
print("=" * 60)

print(
    pd.crosstab(
        df["type"],
        df["is_homepage"]
    )
)

print("\nHOMEPAGE PERCENTAGE BY CLASS")
print("=" * 60)

print(
    pd.crosstab(
        df["type"],
        df["is_homepage"],
        normalize="index"
    ).mul(100).round(2)
)

print("\nANALYSIS COMPLETED")
