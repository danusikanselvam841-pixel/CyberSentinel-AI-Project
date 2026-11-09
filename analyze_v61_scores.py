
import sys
import joblib
import numpy as np
import pandas as pd

from urllib.parse import urlsplit


# Original normalization function used in v6.1 training
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

        result = host + (parsed.path or "")

        if parsed.query:
            result += "?" + parsed.query

        return result

    except (ValueError, TypeError):
        return ""


def normalize_batch(urls):
    return [normalize_url(url) for url in urls]


# Allow joblib to resolve the original saved function
sys.modules["__main__"].normalize_batch = normalize_batch


MODEL_PATH = "models/url_threat_model_v61.pkl"
VAL_PATH = "url_data/splits_v6/validation.csv"

print("Loading saved v6.1 model...")

saved = joblib.load(MODEL_PATH)

if hasattr(saved, "predict_proba"):
    model = saved
elif isinstance(saved, dict):
    model = saved.get("pipeline")
else:
    model = None

if model is None:
    raise ValueError("Trained pipeline not found.")

df = pd.read_csv(
    VAL_PATH,
    usecols=["url", "type"]
).dropna()

# Pipeline automatically normalizes URLs
urls = df["url"].astype(str).tolist()
labels = df["type"].to_numpy()

print("Validation URLs:", len(urls))
print("Evaluating prediction scores...")

probs = model.predict_proba(urls)

classes = list(model.classes_)
benign_index = classes.index("benign")

threat_score = 1 - probs[:, benign_index]
is_malicious = labels != "benign"

print("\nTHRESHOLD ANALYSIS")
print("=" * 65)

for threshold in [0.50, 0.70, 0.80, 0.90, 0.95]:

    flagged = threat_score >= threshold

    benign_mask = ~is_malicious
    malicious_mask = is_malicious

    fpr = np.mean(flagged[benign_mask]) * 100
    recall = np.mean(flagged[malicious_mask]) * 100

    print(
        f"Threshold {threshold:.2f} | "
        f"Benign FPR: {fpr:.2f}% | "
        f"Threat Recall: {recall:.2f}%"
    )


print("\nKNOWN DOMAIN SCORE CHECK")
print("=" * 65)

examples = [
    "https://google.com",
    "https://github.com",
    "https://microsoft.com",
    "https://wikipedia.org",
    "https://example.com"
]

example_probs = model.predict_proba(examples)

for url, row in zip(examples, example_probs):

    score = 1 - row[benign_index]

    print(
        f"{url}: "
        f"Threat Score = {score * 100:.2f}%"
    )


print("\nANALYSIS COMPLETED")
