
import pandas as pd
import tldextract
from pathlib import Path
from urllib.parse import urlsplit

DATA_DIR = Path("url_data/splits")

extractor = tldextract.TLDExtract(
    suffix_list_urls=()
)

def get_domain(url):
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


domains = {}

for split in ["train", "validation", "test"]:
    path = DATA_DIR / f"{split}.csv"

    df = pd.read_csv(
        path,
        usecols=["url"]
    )

    values = {
        get_domain(url)
        for url in df["url"].dropna()
    }

    domains[split] = values - {""}

    print(
        f"{split}: {len(domains[split])} "
        "unique registrable domains"
    )


print("\nREGISTRABLE DOMAIN OVERLAP")

pairs = [
    ("train", "validation"),
    ("train", "test"),
    ("validation", "test")
]

for a, b in pairs:
    overlap = domains[a] & domains[b]

    print(f"\n{a} vs {b}")
    print("Overlapping domains:", len(overlap))

    if overlap:
        print("Examples:", sorted(overlap)[:10])


print("\nAUDIT COMPLETED")
