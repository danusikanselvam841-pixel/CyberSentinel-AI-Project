
import joblib
import pandas as pd
import numpy as np

MODEL_PATH = "models/url_threat_model_v6.pkl"
DATA_PATH = "url_data/splits_v6/validation.csv"

saved = joblib.load(MODEL_PATH)
model = saved["pipeline"]

df = pd.read_csv(DATA_PATH)

benign = df[df["type"] == "benign"].copy()

print("Analyzing benign validation URLs...")

predictions = model.predict(
    benign["url"].astype(str).tolist()
)

benign["prediction"] = predictions

false_positives = benign[
    benign["prediction"] != "benign"
].copy()

print("\nV6 FALSE POSITIVE ANALYSIS")
print("=" * 55)

print("Total benign URLs:", len(benign))
print("False positives:", len(false_positives))

print(
    "False positive rate:",
    round(
        len(false_positives) / len(benign) * 100,
        2
    ),
    "%"
)

print("\nFalse positives by predicted class:")
print(
    false_positives["prediction"]
    .value_counts()
    .to_string()
)

urls = benign["url"].astype(str).str.lower()

benign["scheme"] = np.select(
    [
        urls.str.startswith("https://"),
        urls.str.startswith("http://")
    ],
    [
        "HTTPS",
        "HTTP"
    ],
    default="NO SCHEME"
)

print("\nFALSE POSITIVE RATE BY URL FORMAT")

for scheme, group in benign.groupby("scheme"):
    rate = (
        (group["prediction"] != "benign").mean()
        * 100
    )

    print(
        scheme,
        "- URLs:",
        len(group),
        "- False positive rate:",
        round(rate, 2),
        "%"
    )

print("\nSAMPLE FALSE POSITIVES")

print(
    false_positives[
        ["url", "prediction"]
    ].head(15).to_string(index=False)
)

print("\nANALYSIS COMPLETED")
