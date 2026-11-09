
import joblib
import pandas as pd
from sklearn.metrics import confusion_matrix

print("Loading model and validation dataset...")

saved = joblib.load("models/url_threat_model_v2.pkl")
model = saved["pipeline"]

df = pd.read_csv("url_data/splits/validation.csv")

X = df["url"].astype(str)
y = df["type"].astype(str)

print("Predicting validation URLs...")
predictions = model.predict(X)

labels = ["benign", "defacement", "malware", "phishing"]

cm = confusion_matrix(y, predictions, labels=labels)

print("\nCONFUSION MATRIX")
print(pd.DataFrame(
    cm,
    index=[f"Actual {x}" for x in labels],
    columns=[f"Predicted {x}" for x in labels]
))

benign_mask = (y == "benign")
false_positive_mask = benign_mask & (predictions != "benign")

benign_count = int(benign_mask.sum())
false_positive_count = int(false_positive_mask.sum())

print("\nBENIGN FALSE POSITIVE ANALYSIS")
print("Total benign URLs:", benign_count)
print("Incorrectly flagged:", false_positive_count)

print(
    "False Positive Rate:",
    round(false_positive_count / benign_count * 100, 2),
    "%"
)

print("\nFALSE POSITIVE CATEGORIES")
print(
    pd.Series(
        predictions[false_positive_mask.to_numpy()]
    ).value_counts()
)

print("\nEXAMPLE FALSE POSITIVES")

examples = df.loc[
    false_positive_mask,
    ["url", "type"]
].copy()

examples["prediction"] = predictions[
    false_positive_mask.to_numpy()
]

# Print only the URL patterns, not full URLs,
# to avoid exposing potentially sensitive query data.
from urllib.parse import urlsplit

def summarize_url(url):
    url = str(url)
    normalized = url if "://" in url else "http://" + url

    try:
        parsed = urlsplit(normalized)
        return {
            "scheme": parsed.scheme,
            "hostname_length": len(parsed.hostname or ""),
            "path_length": len(parsed.path),
            "has_query": bool(parsed.query)
        }
    except ValueError:
        return {
            "scheme": "invalid",
            "hostname_length": 0,
            "path_length": 0,
            "has_query": False
        }

print(
    examples["url"]
    .head(10)
    .apply(summarize_url)
    .to_string(index=False)
)
