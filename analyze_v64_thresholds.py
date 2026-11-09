
import joblib
import numpy as np
import pandas as pd

from scipy.sparse import hstack, csr_matrix

from train_url_model_v62 import normalize_url
from url_features_v62 import get_url_features


MODEL_PATH = "models/url_threat_model_v64.pkl"
VAL_PATH = "url_data/splits_v6/validation.csv"

print("Loading v6.4 model...")

saved = joblib.load(MODEL_PATH)

model = saved["model"]
vectorizer = saved["vectorizer"]
scaler = saved["scaler"]

print("Loading validation dataset...")

df = pd.read_csv(
    VAL_PATH,
    usecols=["url", "type"]
).dropna()

urls = df["url"].astype(str).tolist()
labels = df["type"].to_numpy()

print("Validation URLs:", len(urls))

print("Preparing features...")

normalized = [normalize_url(url) for url in urls]

text_features = vectorizer.transform(normalized)

numeric_features = np.asarray(
    [get_url_features(url) for url in urls],
    dtype=np.float32
)

numeric_features = scaler.transform(numeric_features)

X = hstack(
    [
        text_features,
        csr_matrix(numeric_features)
    ],
    format="csr",
    dtype=np.float32
)

print("Calculating threat scores...")

probabilities = model.predict_proba(X)

benign_index = list(model.classes_).index("benign")

threat_scores = 1 - probabilities[:, benign_index]

is_malicious = labels != "benign"

print("\nTHRESHOLD ANALYSIS")
print("=" * 70)

for threshold in [0.50, 0.60, 0.70, 0.80, 0.90, 0.95]:
    flagged = threat_scores >= threshold

    benign_fpr = (
        np.mean(flagged[~is_malicious]) * 100
    )

    threat_recall = (
        np.mean(flagged[is_malicious]) * 100
    )

    print(
        f"Threshold {threshold:.2f} | "
        f"Benign FPR: {benign_fpr:.2f}% | "
        f"Threat Recall: {threat_recall:.2f}%"
    )

print("\nANALYSIS COMPLETED")
