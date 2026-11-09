
import time
from pathlib import Path
from urllib.parse import urlsplit

import joblib
import numpy as np
import pandas as pd

from scipy.sparse import hstack, csr_matrix

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from url_features_v62 import (
    get_url_features,
    FEATURE_NAMES
)


TRAIN_PATH = Path("url_data/splits_v63/train.csv")
VAL_PATH = Path("url_data/splits_v6/validation.csv")
MODEL_PATH = Path("models/url_threat_model_v64.pkl")

start = time.time()


def normalize_url(url):
    url = str(url).strip()

    if "://" not in url:
        url = "http://" + url

    try:
        parsed = urlsplit(url)

        if not parsed.hostname:
            return ""

        host = parsed.hostname.lower().rstrip(".")

        if ":" in host:
            host = "[" + host + "]"

        result = host + (parsed.path or "")

        if parsed.query:
            result += "?" + parsed.query

        return result

    except (ValueError, TypeError):
        return ""


def prepare_features(urls, vectorizer, scaler, fit=False):
    normalized = [
        normalize_url(url)
        for url in urls
    ]

    if fit:
        text_features = vectorizer.fit_transform(normalized)
    else:
        text_features = vectorizer.transform(normalized)

    numeric_features = np.asarray(
        [get_url_features(url) for url in urls],
        dtype=np.float32
    )

    if fit:
        numeric_features = scaler.fit_transform(
            numeric_features
        )
    else:
        numeric_features = scaler.transform(
            numeric_features
        )

    combined = hstack(
        [
            text_features,
            csr_matrix(numeric_features)
        ],
        format="csr",
        dtype=np.float32
    )

    return combined


def main():
    print("=" * 55)
    print("CYBERSENTINEL AI V6.4 - HYBRID TRAINING")
    print("=" * 55)

    print("\nLoading datasets...")

    train = pd.read_csv(
        TRAIN_PATH,
        usecols=["url", "type"]
    ).dropna()

    val = pd.read_csv(
        VAL_PATH,
        usecols=["url", "type"]
    ).dropna()

    train_urls = train["url"].astype(str).tolist()
    val_urls = val["url"].astype(str).tolist()

    y_train = train["type"].to_numpy()
    y_val = val["type"].to_numpy()

    print("Train:", len(train_urls))
    print("Validation:", len(val_urls))

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        max_features=50000,
        min_df=3,
        sublinear_tf=True,
        dtype=np.float32
    )

    scaler = StandardScaler()

    print("\nPreparing training features...")

    X_train = prepare_features(
        train_urls,
        vectorizer,
        scaler,
        fit=True
    )

    print("Training feature shape:", X_train.shape)

    model = SGDClassifier(
        loss="log_loss",
        alpha=0.00001,
        max_iter=100,
        tol=0.001,
       class_weight=None,
        random_state=42,
        n_jobs=-1
    )

    print("\nTraining classifier...")
    model.fit(X_train, y_train)

    del X_train

    print("\nPreparing validation features...")

    X_val = prepare_features(
        val_urls,
        vectorizer,
        scaler,
        fit=False
    )

    print("\nEvaluating...")

    predictions = model.predict(X_val)

    accuracy = accuracy_score(
        y_val,
        predictions
    )

    print("\nVALIDATION ACCURACY:", round(accuracy, 4))

    print("\nCLASSIFICATION REPORT")
    print(
        classification_report(
            y_val,
            predictions,
            zero_division=0
        )
    )

    benign_mask = y_val == "benign"

    benign_fpr = np.mean(
        predictions[benign_mask] != "benign"
    ) * 100

    print(
        "\nBENIGN FALSE POSITIVE RATE:",
        round(benign_fpr, 2),
        "%"
    )

    print("\nCONFUSION MATRIX")
    print(
        confusion_matrix(
            y_val,
            predictions,
            labels=model.classes_
        )
    )

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        {
            "model": model,
            "vectorizer": vectorizer,
            "scaler": scaler,
            "feature_names": FEATURE_NAMES,
            "model_version": "v6.4"
        },
        MODEL_PATH,
        compress=3
    )

    print("\nSaved:", MODEL_PATH)

    elapsed = time.time() - start

    print(
        "Training time:",
        round(elapsed / 60, 2),
        "minutes"
    )

    print("\nTRAINING COMPLETED")


if __name__ == "__main__":
    main()
