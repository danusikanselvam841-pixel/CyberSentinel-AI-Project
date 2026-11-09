
import pandas as pd
from urllib.parse import urlsplit

df = pd.read_csv(
    "url_data/splits/train.csv",
    usecols=["url", "type"]
)

def create_variants(url):
    url = str(url).strip()

    if not url:
        return []

    # Only change explicit HTTP/HTTPS URLs
    if not url.lower().startswith(
        ("http://", "https://")
    ):
        return []

    try:
        parsed = urlsplit(url)

        if not parsed.hostname:
            return []

        http_url = parsed._replace(
            scheme="http"
        ).geturl()

        https_url = parsed._replace(
            scheme="https"
        ).geturl()

        return [http_url, https_url]

    except ValueError:
        return []


print("Analyzing augmentation opportunities...")

results = []

for label, group in df.groupby("type"):
    count = 0

    for url in group["url"]:
        if create_variants(url):
            count += 1

    results.append({
        "class": label,
        "original_rows": len(group),
        "augmentable_rows": count,
        "possible_variants": count * 2
    })

summary = pd.DataFrame(results)

print("\nAUGMENTATION SUMMARY")
print(summary.to_string(index=False))

print("\nTOTAL AUGMENTABLE ROWS")
print(summary["augmentable_rows"].sum())
