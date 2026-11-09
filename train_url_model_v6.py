
import time
import joblib
import numpy as np
import pandas as pd

from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

SEED = 42

TRAIN_PATH = Path("url_data/splits_v6/train.csv")
VAL_PATH = Path("url_data/splits_v6/validation.csv")
MODEL_PATH = Path("models/url_threat_model_v6.pkl")

start = time.time()

print("=" * 55)
print("CYBERSENTINEL AI V6 - TRAINING")
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
            random_state=SEED,
            n_jobs=-1
        )
    )
])

print("\nTraining Model v6...")
pipeline.fit(train_urls, y_train)

print("\nEvaluating validation dataset...")

predictions = pipeline.predict(val_urls)

accuracy = accuracy_score(
    y_val,
    predictions
)

print("\nMODEL V6 RESULTS")
print("Validation Accuracy:", round(accuracy, 4))

print("\nClassification Report:")
print(
    classification_report(
        y_val,
        predictions,
        zero_division=0
    )
)

benign_mask = y_val == "benign"

benign_fpr = (
    np.mean(
        predictions[benign_mask] != "benign"
    ) * 100
)

print(
    "\nBenign False Positive Rate:",
    round(benign_fpr, 2),
    "%"
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_val,
        predictions,
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
        "model_version": "v6_domain_separated",
        "training_split": str(TRAIN_PATH)
    },
    MODEL_PATH,
    compress=3
)

elapsed = time.time() - start

print("\nSaved model:", MODEL_PATH)
print(
    "Total elapsed time:",
    round(elapsed / 60, 2),
    "minutes"
)
