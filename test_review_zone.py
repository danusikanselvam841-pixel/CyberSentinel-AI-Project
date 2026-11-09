
import joblib
import numpy as np
import pandas as pd

model = joblib.load(
    "models/url_threat_model_v2.pkl"
)["pipeline"]

df = pd.read_csv("url_data/splits/validation.csv")

probabilities = model.predict_proba(
    df["url"].astype(str)
)

classes = np.asarray(model.classes_)
y = df["type"].astype(str).to_numpy()

malicious_indices = np.where(classes != "benign")[0]

malicious_probs = probabilities[:, malicious_indices]
max_malicious = malicious_probs.max(axis=1)

# Experimental review thresholds
low_threshold = 0.50
high_threshold = 0.80

status = np.full(len(df), "Likely Benign", dtype=object)

status[
    max_malicious >= low_threshold
] = "Needs Review"

status[
    max_malicious >= high_threshold
] = "High-Risk Pattern"

print("\nREVIEW ZONE RESULTS")
print(pd.Series(status).value_counts())

print("\nACTUAL CLASS vs STATUS")
print(pd.crosstab(
    pd.Series(y, name="Actual"),
    pd.Series(status, name="Status")
))

print("\nMISSED THREAT ANALYSIS")

actual_malicious = y != "benign"

for category in [
    "Likely Benign",
    "Needs Review",
    "High-Risk Pattern"
]:
    count = np.sum(
        actual_malicious & (status == category)
    )
    print(f"{category}: {count} actual malicious URLs")

print("\nBENIGN FALSE ALARMS")

benign = y == "benign"

for category in [
    "Needs Review",
    "High-Risk Pattern"
]:
    count = np.sum(benign & (status == category))
    print(f"{category}: {count} benign URLs")
