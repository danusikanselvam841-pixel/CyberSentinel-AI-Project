
import joblib
import pandas as pd
import numpy as np
from urllib.parse import urlsplit

MODEL_PATH = "models/url_threat_model_v6.pkl"
VAL_PATH = "url_data/splits_v6/validation.csv"

model = joblib.load(MODEL_PATH)["pipeline"]

df = pd.read_csv(VAL_PATH, usecols=["url", "type"])

benign = df[df["type"] == "benign"].sample(
    n=2000,
    random_state=42
)

def remove_scheme(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlsplit(url)

        if not parsed.netloc:
            return None

        result = parsed.netloc + (parsed.path or "")

        if parsed.query:
            result += "?" + parsed.query

        if parsed.fragment:
            result += "#" + parsed.fragment

        return result

    except ValueError:
        return None


base_urls = [
    remove_scheme(url)
    for url in benign["url"]
]

base_urls = [
    url for url in base_urls
    if url is not None
]

variants = {
    "No scheme": base_urls,
    "HTTP": ["http://" + url for url in base_urls],
    "HTTPS": ["https://" + url for url in base_urls]
}

results = {}

print("CYBERSENTINEL V6 - SCHEME BIAS AUDIT")
print("=" * 50)
print("Benign URLs tested:", len(base_urls))

for name, urls in variants.items():
    predictions = model.predict(urls)
    results[name] = predictions

    false_positive_rate = np.mean(
        predictions != "benign"
    ) * 100

    print(
        f"{name} false positive rate: "
        f"{false_positive_rate:.2f}%"
    )

print("\nPREDICTION CHANGES")

pairs = [
    ("No scheme", "HTTP"),
    ("HTTP", "HTTPS"),
    ("No scheme", "HTTPS")
]

for a, b in pairs:
    changes = np.sum(results[a] != results[b])
    print(f"{a} vs {b}: {changes}")

print("\nAUDIT COMPLETED")
