
import joblib
import numpy as np
import pandas as pd
import ipaddress

from urllib.parse import urlsplit
from scipy.sparse import hstack, csr_matrix

saved = joblib.load("models/url_threat_model_v3.pkl")

model = saved["model"]
vectorizer = saved["vectorizer"]
scaler = saved["scaler"]

df = pd.read_csv("url_data/splits/validation.csv")
benign = df[df["type"] == "benign"].copy()

# Only explicitly HTTP or HTTPS URLs
urls = benign["url"].astype(str)

mask = urls.str.match(
    r"^https?://",
    case=False
)

urls = urls[mask]

# Use a reproducible sample for faster analysis
urls = urls.sample(
    n=min(5000, len(urls)),
    random_state=42
)

def features(url):
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()

    try:
        ipaddress.ip_address(host)
        is_ip = 1
    except ValueError:
        is_ip = 0

    return [
        len(url),
        len(host),
        host.count("."),
        host.count("-"),
        sum(c.isdigit() for c in host),
        url.count("@"),
        url.count("?"),
        url.count("="),
        url.count("/"),
        is_ip,
        len(parsed.path),
        len(parsed.query),
        int(parsed.username is not None),
        int(parsed.scheme.lower() == "https")
    ]

def predict_batch(url_list):
    text = vectorizer.transform(url_list)

    numeric = np.asarray(
        [features(url) for url in url_list],
        dtype=np.float32
    )

    numeric = scaler.transform(numeric)

    X = hstack(
        [text, csr_matrix(numeric)],
        format="csr"
    )

    return model.predict(X)

http_urls = []
https_urls = []

for url in urls:
    parsed = urlsplit(url)

    http_urls.append(
        parsed._replace(scheme="http").geturl()
    )

    https_urls.append(
        parsed._replace(scheme="https").geturl()
    )

print("Predicting HTTP variants...")
http_predictions = predict_batch(http_urls)

print("Predicting HTTPS variants...")
https_predictions = predict_batch(https_urls)

http_false_positive = np.mean(
    http_predictions != "benign"
) * 100

https_false_positive = np.mean(
    https_predictions != "benign"
) * 100

print("\nSCHEME SENSITIVITY RESULTS")
print("URLs tested:", len(urls))

print(
    "HTTP variant false positive rate:",
    round(http_false_positive, 2),
    "%"
)

print(
    "HTTPS variant false positive rate:",
    round(https_false_positive, 2),
    "%"
)

changed = np.sum(
    http_predictions != https_predictions
)

print("Predictions changed:", changed)

print(
    "HTTP benign -> HTTPS malicious:",
    np.sum(
        (http_predictions == "benign")
        & (https_predictions != "benign")
    )
)

print(
    "HTTP malicious -> HTTPS benign:",
    np.sum(
        (http_predictions != "benign")
        & (https_predictions == "benign")
    )
)
