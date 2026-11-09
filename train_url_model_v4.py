
from pathlib import Path
from urllib.parse import urlsplit

import joblib
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

SPLIT_DIR = Path("url_data/splits")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)


def normalize_url(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlsplit(url)
        hostname = (parsed.hostname or "").lower()

        if not hostname:
            return ""

        port = (
            f":{parsed.port}"
            if parsed.port is not None
            else ""
        )

        path = parsed.path or ""
        query = (
            f"?{parsed.query}"
            if parsed.query
            else ""
        )

        return hostname + port + path + query

    except ValueError:
        return ""


print("Loading hostname-separated datasets...")

train = pd.read_csv(SPLIT_DIR / "train.csv")
validation = pd.read_csv(SPLIT_DIR / "validation.csv")

print("Normalizing URLs...")

X_train = train["url"].map(normalize_url)
y_train = train["type"]

X_val = validation["url"].map(normalize_url)
y_val = validation["type"]

# Exclude invalid normalized URLs
train_valid = X_train != ""
val_valid = X_val != ""

X_train = X_train[train_valid]
y_train = y_train[train_valid]

X_val = X_val[val_valid]
y_val = y_val[val_valid]

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        min_df=3,
        max_features=100000,
        lowercase=True
    )),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ))
])

print("Training URL Model v4...")
pipeline.fit(X_train, y_train)

print("\nVALIDATION RESULTS")

predictions = pipeline.predict(X_val)

print(
    "Accuracy:",
    accuracy_score(y_val, predictions)
)

print(classification_report(
    y_val,
    predictions,
    zero_division=0
))

benign_mask = y_val == "benign"

false_positive_rate = (
    (predictions[benign_mask] != "benign").mean()
    * 100
)

print(
    "Benign False Positive Rate:",
    round(false_positive_rate, 2),
    "%"
)

print("\nEXAMPLE DOMAIN TEST")

examples = [
    "https://example.com",
    "http://example.com",
    "https://example.org",
    "https://example.net",
    "https://google.com",
    "https://wikipedia.org"
]

for url in examples:
    normalized = normalize_url(url)
    prediction = pipeline.predict([normalized])[0]

    probabilities = pipeline.predict_proba(
        [normalized]
    )[0]

    score = max(probabilities) * 100

    print(
        f"{url} -> {prediction} ({score:.2f}%)"
    )

model_path = MODEL_DIR / "url_threat_model_v4.pkl"

joblib.dump({
    "pipeline": pipeline,
    "normalization": "scheme_removed_v1",
    "classes": pipeline.classes_.tolist(),
    "model_version": "url_detector_v4"
}, model_path)

print("\nModel saved:", model_path)
