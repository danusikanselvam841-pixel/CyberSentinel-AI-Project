
import joblib
import numpy as np
import pandas as pd

from url_features_v67 import prepare_features


MODEL_PATH = "models/url_threat_model_v67.pkl"
VAL_PATH = "url_data/splits_v6/validation.csv"

print("Loading v6.7 model...")

saved = joblib.load(MODEL_PATH)

model = saved["model"]
host_vectorizer = saved["hostname_vectorizer"]
path_vectorizer = saved["path_vectorizer"]

print("Loading validation dataset...")

val = pd.read_csv(
    VAL_PATH,
    usecols=["url", "type"]
).dropna()

urls = val["url"].astype(str).tolist()
labels = val["type"].to_numpy()

print("Preparing features...")

X = prepare_features(
    urls,
    host_vectorizer,
    path_vectorizer,
    fit=False
)

print("Calculating threat scores...")

probabilities = model.predict_proba(X)

benign_idx = list(model.classes_).index("benign")

threat_scores = 1 - probabilities[:, benign_idx]

benign_mask = labels == "benign"
threat_mask = labels != "benign"

print("\nTHRESHOLD ANALYSIS")
print("=" * 65)

for threshold in [
    0.50,
    0.60,
    0.70,
    0.80,
    0.90,
    0.95
]:
    predicted_threat = threat_scores >= threshold

    benign_fpr = (
        predicted_threat[benign_mask].mean() * 100
    )

    threat_recall = (
        predicted_threat[threat_mask].mean() * 100
    )

    print(
        f"Threshold {threshold:.2f} | "
        f"Benign FPR: {benign_fpr:.2f}% | "
        f"Threat Recall: {threat_recall:.2f}%"
    )

print("\nANALYSIS COMPLETED")
