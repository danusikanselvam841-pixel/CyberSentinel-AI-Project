
import joblib
import pandas as pd
from urllib.parse import urlsplit
import ipaddress
import numpy as np
from scipy.sparse import hstack, csr_matrix

saved = joblib.load("models/url_threat_model_v3.pkl")

model = saved["model"]
vectorizer = saved["vectorizer"]
scaler = saved["scaler"]

def get_features(url):
    normalized = url if "://" in url else "http://" + url
    parsed = urlsplit(normalized)
    host = parsed.hostname or ""

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

def predict(url):
    text = vectorizer.transform([url])

    numeric = np.array(
        [get_features(url)],
        dtype=np.float32
    )
    numeric = scaler.transform(numeric)

    combined = hstack(
        [text, csr_matrix(numeric)],
        format="csr"
    )

    probabilities = model.predict_proba(combined)[0]
    prediction = model.classes_[np.argmax(probabilities)]

    return prediction, dict(zip(
        model.classes_,
        np.round(probabilities * 100, 2)
    ))

domains = [
    "example.com",
    "example.org",
    "example.net",
    "google.com",
    "wikipedia.org"
]

for domain in domains:
    print(f"\nDOMAIN: {domain}")

    for scheme in ["http", "https"]:
        url = f"{scheme}://{domain}"
        prediction, scores = predict(url)

        print(f"{url}")
        print("Prediction:", prediction)
        print("Scores:", scores)
