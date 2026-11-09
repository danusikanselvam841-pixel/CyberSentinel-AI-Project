
import joblib
import pandas as pd
import numpy as np
import ipaddress

from urllib.parse import urlsplit
from scipy.sparse import hstack, csr_matrix
saved = joblib.load("models/url_threat_model_v5.pkl")

model = saved["model"]
vectorizer = saved["vectorizer"]
scaler = saved["scaler"]

df = pd.read_csv("url_data/splits/validation.csv")
benign = df[df["type"] == "benign"]

sample = benign.sample(
    n=min(2000, len(benign)),
    random_state=42
)

def get_features(url):
    normalized = url if "://" in url else "http://" + url
    parsed = urlsplit(normalized)
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
        int(parsed.scheme == "https")
    ]

def predict(urls):
    text = vectorizer.transform(urls)

    numeric = np.asarray(
        [get_features(url) for url in urls],
        dtype=np.float32
    )

    numeric = scaler.transform(numeric)

    X = hstack(
        [text, csr_matrix(numeric)],
        format="csr"
    )

    return model.predict(X)

no_scheme = []
http_urls = []
https_urls = []

for url in sample["url"].astype(str):
    normalized = (
        url if "://" in url else "http://" + url
    )

    parsed = urlsplit(normalized)

    no_scheme.append(
        parsed.netloc + parsed.path +
        ("?" + parsed.query if parsed.query else "")
    )

    http_urls.append(
        parsed._replace(scheme="http").geturl()
    )

    https_urls.append(
        parsed._replace(scheme="https").geturl()
    )

print("Predicting three formats...")

pred_no_scheme = predict(no_scheme)
pred_http = predict(http_urls)
pred_https = predict(https_urls)

print("\nTHREE FORMAT COMPARISON")

for name, predictions in [
    ("No Scheme", pred_no_scheme),
    ("HTTP", pred_http),
    ("HTTPS", pred_https)
]:
    flagged = np.mean(predictions != "benign") * 100
    print(f"{name}: {flagged:.2f}% flagged malicious")

print("\nPREDICTION CHANGES")

print(
    "No Scheme vs HTTP:",
    np.sum(pred_no_scheme != pred_http)
)

print(
    "HTTP vs HTTPS:",
    np.sum(pred_http != pred_https)
)

print(
    "No Scheme vs HTTPS:",
    np.sum(pred_no_scheme != pred_https)
)
