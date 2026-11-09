
import random
import ipaddress
import joblib
import numpy as np
import pandas as pd

from pathlib import Path
from urllib.parse import urlsplit
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

SEED = 42
rng = random.Random(SEED)

TRAIN_PATH = "url_data/splits/train.csv"
VAL_PATH = "url_data/splits/validation.csv"
MODEL_PATH = "models/url_threat_model_v5.pkl"

print("Loading datasets...")

train = pd.read_csv(
    TRAIN_PATH,
    usecols=["url", "type"]
).dropna()

val = pd.read_csv(
    VAL_PATH,
    usecols=["url", "type"]
).dropna()

train["url"] = train["url"].astype(str)
val["url"] = val["url"].astype(str)

print("Train:", len(train))
print("Validation:", len(val))


def augment_scheme(url):
    url = str(url).strip()

    normalized = (
        url if "://" in url else "http://" + url
    )

    try:
        parsed = urlsplit(normalized)

        if not parsed.hostname:
            return url

        choice = rng.choice(
            ["none", "http", "https"]
        )

        if choice == "none":
            return (
                parsed.netloc
                + parsed.path
                + ("?" + parsed.query if parsed.query else "")
                + ("#" + parsed.fragment if parsed.fragment else "")
            )

        return parsed._replace(
            scheme=choice
        ).geturl()

    except ValueError:
        return url


def extract_features(url):
    url = str(url)

    normalized = (
        url if "://" in url else "http://" + url
    )

    try:
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

    except ValueError:
        return [0] * 14


print("\nApplying training-only augmentation...")

train_urls = [
    augment_scheme(url)
    for url in train["url"]
]

val_urls = val["url"].tolist()

print("Extracting structural features...")

X_train_numeric = np.asarray(
    [extract_features(url) for url in train_urls],
    dtype=np.float32
)

X_val_numeric = np.asarray(
    [extract_features(url) for url in val_urls],
    dtype=np.float32
)

scaler = StandardScaler()

X_train_numeric = scaler.fit_transform(
    X_train_numeric
)

X_val_numeric = scaler.transform(
    X_val_numeric
)

print("Building TF-IDF features...")

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 5),
    max_features=100000,
    min_df=2,
    dtype=np.float32
)

X_train_text = vectorizer.fit_transform(
    train_urls
)

X_val_text = vectorizer.transform(
    val_urls
)

X_train = hstack(
    [
        X_train_text,
        csr_matrix(X_train_numeric)
    ],
    format="csr",
    dtype=np.float32
)

X_val = hstack(
    [
        X_val_text,
        csr_matrix(X_val_numeric)
    ],
    format="csr",
    dtype=np.float32
)

print("Training Model v5...")

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    solver="saga",
    random_state=SEED,
    n_jobs=-1
)

model.fit(
    X_train,
    train["type"]
)

print("\nEvaluating Model v5...")

predictions = model.predict(X_val)

accuracy = accuracy_score(
    val["type"],
    predictions
)

print("\nMODEL V5 RESULTS")
print("Validation Accuracy:", round(accuracy, 4))

print("\nClassification Report:")
print(
    classification_report(
        val["type"],
        predictions,
        zero_division=0
    )
)

benign_mask = val["type"].to_numpy() == "benign"

benign_fpr = np.mean(
    predictions[benign_mask] != "benign"
) * 100

print(
    "Benign False Positive Rate:",
    round(benign_fpr, 2),
    "%"
)

Path("models").mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    {
        "model": model,
        "vectorizer": vectorizer,
        "scaler": scaler,
        "model_version": "v5_scheme_augmented",
        "feature_names": [
            "url_length",
            "hostname_length",
            "hostname_dot_count",
            "hostname_hyphen_count",
            "hostname_digit_count",
            "at_count",
            "question_count",
            "equals_count",
            "slash_count",
            "is_ip",
            "path_length",
            "query_length",
            "has_username",
            "is_https"
        ]
    },
    MODEL_PATH
)

print("\nSaved model:", MODEL_PATH)
