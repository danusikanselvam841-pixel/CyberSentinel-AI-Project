
import joblib
import pandas as pd
import numpy as np
import ipaddress

from urllib.parse import urlsplit
from scipy.sparse import hstack, csr_matrix
from sklearn.metrics import classification_report

saved = joblib.load("models/url_threat_model_v3.pkl")

model = saved["model"]
vectorizer = saved["vectorizer"]
scaler = saved["scaler"]

df = pd.read_csv("url_data/splits/validation.csv")

def get_features(url):
    url = str(url).strip()
    normalized = url if "://" in url else "http://" + url

    try:
        parsed = urlsplit(normalized)
        host = (parsed.hostname or "").lower()
    except ValueError:
        parsed = urlsplit("http://invalid.local")
        host = ""

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

print("Extracting validation features...")

X_text = vectorizer.transform(
    df["url"].astype(str)
)

X_numeric = np.asarray(
    [get_features(url) for url in df["url"]],
    dtype=np.float32
)

X_numeric = scaler.transform(X_numeric)

X = hstack(
    [X_text, csr_matrix(X_numeric)],
    format="csr"
)

print("Predicting...")
predictions = model.predict(X)

actual = df["type"].to_numpy()
benign = actual == "benign"

false_positives = np.sum(
    benign & (predictions != "benign")
)

false_positive_rate = (
    false_positives / np.sum(benign) * 100
)

print("\nV3 FALSE POSITIVE RESULTS")
print("Total benign URLs:", np.sum(benign))
print("False positives:", false_positives)
print("False positive rate:", round(false_positive_rate, 2), "%")

print("\nFALSE POSITIVE CATEGORIES")
print(
    pd.Series(predictions[benign & (predictions != "benign")])
    .value_counts()
)

print("\nCLASSIFICATION REPORT")
print(classification_report(
    actual,
    predictions,
    zero_division=0
))

