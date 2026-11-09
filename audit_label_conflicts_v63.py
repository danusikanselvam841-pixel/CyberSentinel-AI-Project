
import pandas as pd
from urllib.parse import urlsplit

PATH = "url_data/splits_v6/train.csv"

DOMAINS = [
    "google.com",
    "github.com",
    "microsoft.com",
    "wikipedia.org",
    "example.com"
]


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

        path = parsed.path or ""
        query = parsed.query or ""

        result = hostname + path

        if query:
            result += "?" + query

        return result

    except (ValueError, TypeError):
        return ""


print("Loading training dataset...")

df = pd.read_csv(
    PATH,
    usecols=["url", "type"]
).dropna()

df["normalized_url"] = df["url"].map(normalize_url)

df = df[df["normalized_url"] != ""]

print("Training records:", len(df))

print("\nEXACT URL LABEL CONFLICTS")
print("=" * 65)

label_counts = df.groupby(
    "normalized_url"
)["type"].nunique()

conflicting_urls = label_counts[
    label_counts > 1
].index

print(
    "Normalized URLs with conflicting labels:",
    len(conflicting_urls)
)

conflicts = df[
    df["normalized_url"].isin(conflicting_urls)
]

print(
    "Records affected:",
    len(conflicts)
)

print("\nCONFLICT LABEL COMBINATIONS")

if len(conflicts):
    combinations = (
        conflicts.groupby("normalized_url")["type"]
        .apply(lambda x: " + ".join(sorted(set(x))))
        .value_counts()
    )

    print(combinations.head(10))
else:
    print("No exact normalized URL conflicts found.")


print("\nHOMEPAGE LABEL AUDIT")
print("=" * 65)

for domain in DOMAINS:
    matches = df[
        df["normalized_url"].isin(
            [domain, domain + "/"]
        )
    ]

    print("\nDomain:", domain)
    print("Homepage records:", len(matches))

    if len(matches):
        print(matches["type"].value_counts())
    else:
        print("No homepage examples")


print("\nAUDIT COMPLETED")
