
import pandas as pd
from urllib.parse import urlsplit

PATH = "url_data/splits_v63/train.csv"


def get_homepage_host(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlsplit(url)

        if (
            not parsed.hostname
            or parsed.path not in ("", "/")
            or parsed.query
            or parsed.fragment
            or parsed.username is not None
        ):
            return None

        return parsed.hostname.lower().rstrip(".")

    except (ValueError, TypeError):
        return None


print("Loading training dataset...")

df = pd.read_csv(
    PATH,
    usecols=["url", "type"]
).dropna()

df["homepage_host"] = df["url"].map(
    get_homepage_host
)

homepages = df.dropna(
    subset=["homepage_host"]
).copy()

print("\nTOTAL HOMEPAGE RECORDS:", len(homepages))
print("UNIQUE HOMEPAGE HOSTS:", homepages["homepage_host"].nunique())

print("\nHOMEPAGE LABEL COUNTS")
print(homepages["type"].value_counts())

host_labels = (
    homepages.groupby("homepage_host")["type"]
    .nunique()
)

conflicting_hosts = host_labels[
    host_labels > 1
].index

print("\nHOSTS WITH MULTIPLE LABELS:", len(conflicting_hosts))

conflicts = homepages[
    homepages["homepage_host"].isin(conflicting_hosts)
]

print("\nEXAMPLE HOST LABEL CONFLICTS")

examples = (
    conflicts.groupby(
        ["homepage_host", "type"]
    )
    .size()
    .unstack(fill_value=0)
)

print(examples.head(20).to_string())

print("\nAUDIT COMPLETED")
