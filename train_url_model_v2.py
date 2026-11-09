
from pathlib import Path

import joblib
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report
)

SPLIT_DIR = Path("url_data/splits")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

print("Loading hostname-separated datasets...")

train = pd.read_csv(SPLIT_DIR / "train.csv")
validation = pd.read_csv(SPLIT_DIR / "validation.csv")
test = pd.read_csv(SPLIT_DIR / "test.csv")

X_train = train["url"].astype(str)
y_train = train["type"]

X_val = validation["url"].astype(str)
y_val = validation["type"]

X_test = test["url"].astype(str)
y_test = test["type"]

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

print("Training URL model v2...")
pipeline.fit(X_train, y_train)

print("\nVALIDATION RESULTS")
val_predictions = pipeline.predict(X_val)

print(
    "Validation Accuracy:",
    accuracy_score(y_val, val_predictions)
)
print(classification_report(
    y_val,
    val_predictions,
    zero_division=0
))

print("\nTEST RESULTS")
test_predictions = pipeline.predict(X_test)

print(
    "Test Accuracy:",
    accuracy_score(y_test, test_predictions)
)
print(classification_report(
    y_test,
    test_predictions,
    zero_division=0
))

print("\nEXAMPLE DOMAIN TEST")

examples = [
    "https://example.com",
    "https://example.org",
    "https://example.net"
]

for url in examples:
    prediction = pipeline.predict([url])[0]
    scores = pipeline.predict_proba([url])[0]
    score = max(scores) * 100

    print(
        f"{url} -> {prediction} ({score:.2f}%)"
    )

model_path = MODEL_DIR / "url_threat_model_v2.pkl"

joblib.dump({
    "pipeline": pipeline,
    "classes": pipeline.classes_.tolist(),
    "model_version": "url_detector_v2"
}, model_path)

print("\nModel saved:", model_path)
