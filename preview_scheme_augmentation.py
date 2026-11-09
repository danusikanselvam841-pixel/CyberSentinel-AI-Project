
from urllib.parse import urlsplit
import pandas as pd

def create_scheme_variants(url):
    url = str(url).strip()

    if not url.lower().startswith(
        ("http://", "https://")
    ):
        return []

    try:
        parsed = urlsplit(url)

        if not parsed.hostname:
            return []

        return [
            parsed._replace(scheme="http").geturl(),
            parsed._replace(scheme="https").geturl()
        ]

    except ValueError:
        return []


df = pd.read_csv(
    "url_data/splits/train.csv",
    usecols=["url", "type"]
)

print("Original training rows:", len(df))

sample = df.sample(
    n=min(5, len(df)),
    random_state=42
)

print("\nAUGMENTATION PREVIEW")

for _, row in sample.iterrows():
    print("\nOriginal:", row["url"])
    print("Label:", row["type"])

    variants = create_scheme_variants(row["url"])

    for variant in variants:
        print("Variant:", variant)


explicit_scheme = df["url"].astype(str).str.lower().str.startswith(
    ("http://", "https://")
)

print("\nURLs with explicit HTTP/HTTPS:", explicit_scheme.sum())
print("URLs without explicit scheme:", (~explicit_scheme).sum())
