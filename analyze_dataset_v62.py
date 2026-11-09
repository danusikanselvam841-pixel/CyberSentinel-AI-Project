
import pandas as pd
from urllib.parse import urlsplit

PATH = "url_data/splits_v6/train.csv"

df = pd.read_csv(
    PATH,
    usecols=["url", "type"]
)

def get_features(url):
    url = str(url).strip()

    if url.startswith("https://"):
        scheme = "HTTPS"
    elif url.startswith("http://"):
        scheme = "HTTP"
    else:
        scheme = "NO_SCHEME"

    parsed_url = (
        url if "://" in url
        else "http://" + url
    )

    try:
        parsed = urlsplit(parsed_url)
        hostname = parsed.hostname or ""
    except ValueError:
        hostname = ""

    return pd.Series({
        "scheme": scheme,
        "url_length": len(url),
        "hostname_length": len(hostname),
        "dot_count": hostname.count("."),
        "digit_count": sum(
            c.isdigit() for c in url
        )
    })


print("Analyzing training dataset...")

features = df["url"].apply(get_features)

df = pd.concat(
    [df, features],
    axis=1
)

print("\nSCHEME DISTRIBUTION BY CLASS")
print(
    pd.crosstab(
        df["type"],
        df["scheme"],
        normalize="index"
    ).mul(100).round(2)
)

print("\nAVERAGE URL FEATURES BY CLASS")
print(
    df.groupby("type")[
        [
            "url_length",
            "hostname_length",
            "dot_count",
            "digit_count"
        ]
    ].mean().round(2)
)

print("\nANALYSIS COMPLETED")
