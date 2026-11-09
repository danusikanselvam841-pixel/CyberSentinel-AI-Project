
import joblib
import numpy as np
import pandas as pd

saved = joblib.load("models/url_threat_model_v2.pkl")
model = saved["pipeline"]

df = pd.read_csv("url_data/splits/validation.csv")

X = df["url"].astype(str)
y = df["type"].astype(str).to_numpy()

print("Calculating probabilities...")
probabilities = model.predict_proba(X)
classes = model.classes_

benign_idx = list(classes).index("benign")
malicious_classes = [
    c for c in classes if c != "benign"
]
malicious_indices = [
    list(classes).index(c)
    for c in malicious_classes
]

benign_mask = y == "benign"
phishing_mask = y == "phishing"

print("\nTHRESHOLD EXPERIMENT")
print(
    f"{'Threshold':<12}"
    f"{'False Positive %':<20}"
    f"{'Phishing Recall %':<20}"
)

for threshold in [0.50, 0.60, 0.70, 0.80, 0.90]:
    malicious_probs = probabilities[:, malicious_indices]
    max_malicious = malicious_probs.max(axis=1)

    predicted_malicious_idx = malicious_probs.argmax(axis=1)

    predictions = np.array(
        malicious_classes,
        dtype=object
    )[predicted_malicious_idx]

    predictions[max_malicious < threshold] = "benign"

    false_positive_rate = (
        np.mean(predictions[benign_mask] != "benign") * 100
    )

    phishing_recall = (
        np.mean(predictions[phishing_mask] == "phishing") * 100
    )

    print(
        f"{threshold:<12.2f}"
        f"{false_positive_rate:<20.2f}"
        f"{phishing_recall:<20.2f}"
    )
