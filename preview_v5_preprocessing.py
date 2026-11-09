
import random
from urllib.parse import urlsplit
import pandas as pd

random.seed(42)

def change_url_format(url):
    url = str(url).strip()

    if not url:
        return url

    normalized = (
        url if "://" in url else "http://" + url
    )

    try:
        parsed = urlsplit(normalized)

        if not parsed.hostname:
            return url

        formats = ["none", "http", "https"]
        selected = random.choice(formats)

        if selected == "none":
            return (
                parsed.netloc
                + parsed.path
                + ("?" + parsed.query if parsed.query else "")
                + ("#" + parsed.fragment if parsed.fragment else "")
            )

        return parsed._replace(
            scheme=selected
        ).geturl()

    except ValueError:
        return url


df = pd.read_csv(
    "url_data/splits/train.csv",
    usecols=["url", "type"]
)

sample = df.sample(
    n=10,
    random_state=42
)

print("\nMODEL V5 PREPROCESSING PREVIEW")

for _, row in sample.iterrows():
    original = row["url"]
    modified = change_url_format(original)

    print("\nLabel:", row["type"])
    print("Original:", original)
    print("Modified:", modified)
    print("-" * 50)
