
import pandas as pd
from urllib.parse import urlsplit

df = pd.read_csv(
    "url_data/splits/train.csv",
    usecols=["url", "type"]
)

def analyze_url(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlsplit(url)
        host = parsed.hostname or ""

        return pd.Series({
            "hostname_length": len(host),
            "path_length": len(parsed.path),
            "query_length": len(parsed.query),
            "is_https": parsed.scheme == "https",
            "is_simple": (
                len(parsed.path) <= 1
                and len(parsed.query) == 0
            )
        })
    except ValueError:
        return pd.Series({
            "hostname_length": 0,
            "path_length": 0,
            "query_length": 0,
            "is_https": False,
            "is_simple": False
        })

print("Analyzing URL patterns...")

features = df["url"].apply(analyze_url)
df = pd.concat([df, features], axis=1)

print("\nSIMPLE URL DISTRIBUTION")
print(pd.crosstab(
    df["type"],
    df["is_simple"]
))

print("\nHTTPS DISTRIBUTION")
print(pd.crosstab(
    df["type"],
    df["is_https"]
))

print("\nAVERAGE HOSTNAME LENGTH")
print(df.groupby("type")["hostname_length"].mean())

print("\nAVERAGE PATH LENGTH")
print(df.groupby("type")["path_length"].mean())
