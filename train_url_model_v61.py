
import time
import joblib
import numpy as np
import pandas as pd

from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

TRAIN_PATH = Path("url_data/splits_v6/train.csv")
VAL_PATH = Path("url_data/splits_v6/validation.csv")
MODEL_PATH = Path("models/url_threat_model_v61.pkl")

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

        if parsed.port is not None:
            host += ":" + str(parsed.port)

        path = parsed.path or ""

        result = host + path

        if parsed.query:
            result += "?" + parsed.query

        return result

    except (ValueError, TypeError):
        return ""


def normalize_batch(urls):
    return [normalize_url(url) for url in urls]


print("=" * 55)
print("CYBERSENTINEL AI V6.1 - SCHEME-INVARIANT TRAINING")
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

print("Training rows:", len(train))
print("Validation rows:", len(val))

pipeline = Pipeline([
    (
        "normalize",
        FunctionTransformer(
            normalize_batch,
            validate=False
        )
    ),
    (
        "tfidf",
        TfidfVectorizer(
            analyzer="char",
            ngram_range=(3, 5),
            max_features=80000,
            min_df=3,
            sublinear_tf=True,
            dtype=np.float32
        )
    ),
    (
        "classifier",
        SGDClassifier(
            loss="log_loss",
            penalty="l2",
            alpha=0.00001,
            max_iter=100,
            tol=0.001,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        )
    )
])

print("\nTraining v6.1...")

pipeline.fit(train_urls, y_train)

print("\nEvaluating validation dataset...")

pred = pipeline.predict(val_urls)

print(
    "\nValidation Accuracy:",
    round(accuracy_score(y_val, pred), 4)
)

print("\nClassification Report:")
print(
    classification_report(
        y_val,
        pred,
        zero_division=0
    )
)

benign_mask = y_val == "benign"

fpr = np.mean(
    pred[benign_mask] != "benign"
) * 100

print(
    "\nBenign False Positive Rate:",
    round(fpr, 2),
    "%"
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_val,
        pred,
        labels=pipeline.classes_
    )
)

MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    {
        "pipeline": pipeline,
        "classes": pipeline.classes_.tolist(),
        "model_version": "v6.1_scheme_invariant"
    },
    MODEL_PATH,
    compress=3
)

print("\nSaved:", MODEL_PATH)

print(
    "Training time:",
    round((time.time() - start) / 60, 2),
    "minutes"
)

print("\nSCHEME CONSISTENCY TEST")

examples = [
    "google.com",
    "http://google.com",
    "https://google.com",
    "wikipedia.org",
    "http://wikipedia.org",
    "https://wikipedia.org",
    "github.com",
    "https://github.com",
    "microsoft.com",
    "https://microsoft.com"
]

for url, prediction in zip(
    examples,
    pipeline.predict(examples)
):
    print(url, "=>", prediction)

print("\nTRAINING COMPLETED")
