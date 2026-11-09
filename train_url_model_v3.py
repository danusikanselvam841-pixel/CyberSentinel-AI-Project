
from pathlib import Path
from urllib.parse import urlsplit
import ipaddress
import joblib
import numpy as np
import pandas as pd

from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

SPLIT_DIR = Path("url_data/splits")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

FEATURE_NAMES = [
    "url_length",
    "hostname_length",
    "dot_count",
    "hyphen_count",
    "digit_count",
    "at_symbol_count",
    "question_mark_count",
    "equals_count",
    "slash_count",
    "is_ip_address",
    "path_length",
    "query_length",
    "has_username",
    "is_https"
]

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

def build_features(urls, vectorizer, scaler, fit=False):
    urls = pd.Series(urls).astype(str)

    if fit:
        text_features = vectorizer.fit_transform(urls)
    else:
        text_features = vectorizer.transform(urls)

    numeric = np.asarray(
        [get_features(url) for url in urls],
        dtype=np.float32
    )

    if fit:
        numeric = scaler.fit_transform(numeric)
    else:
        numeric = scaler.transform(numeric)

    return hstack(
        [text_features, csr_matrix(numeric)],
        format="csr"
    )

print("Loading datasets...")

train = pd.read_csv(SPLIT_DIR / "train.csv")
val = pd.read_csv(SPLIT_DIR / "validation.csv")

# Keep the test set untouched during model development.
X_train = train["url"].astype(str)
y_train = train["type"]

X_val = val["url"].astype(str)
y_val = val["type"]

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 5),
    min_df=3,
    max_features=100000,
    lowercase=True,
    dtype=np.float32
)

scaler = StandardScaler()

print("Extracting training features...")
X_train_features = build_features(
    X_train, vectorizer, scaler, fit=True
)

print("Extracting validation features...")
X_val_features = build_features(
    X_val, vectorizer, scaler
)

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

print("Training URL model v3...")
model.fit(X_train_features, y_train)

predictions = model.predict(X_val_features)

print("\nV3 VALIDATION RESULTS")
print("Accuracy:", accuracy_score(y_val, predictions))
print(classification_report(
    y_val,
    predictions,
    zero_division=0
))

print("\nEXAMPLE DOMAIN TEST")
for url in [
    "https://example.com",
    "https://example.org",
    "https://example.net"
]:
    features = build_features(
        [url], vectorizer, scaler
    )
    prediction = model.predict(features)[0]
    score = model.predict_proba(features).max() * 100

    print(f"{url} -> {prediction} ({score:.2f}%)")

joblib.dump(
    {
        "model": model,
        "vectorizer": vectorizer,
        "scaler": scaler,
        "feature_names": FEATURE_NAMES,
        "model_version": "url_detector_v3"
    },
    MODEL_DIR / "url_threat_model_v3.pkl"
)

print("\nV3 model saved successfully!")
