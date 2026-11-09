
import joblib
import pandas as pd
import numpy as np

saved = joblib.load(
    "models/url_threat_model_v6.pkl"
)

model = saved["pipeline"]

urls = [
    "google.com",
    "http://google.com",
    "https://google.com",
    "wikipedia.org",
    "http://wikipedia.org",
    "https://wikipedia.org",
    "example.com",
    "http://example.com",
    "https://example.com",
    "github.com",
    "https://github.com",
    "microsoft.com",
    "https://microsoft.com"
]

predictions = model.predict(urls)
scores = model.predict_proba(urls)

print("\nCYBERSENTINEL AI V6 - URL TEST")
print("=" * 65)

for url, prediction, score in zip(
    urls,
    predictions,
    scores
):
    confidence = np.max(score) * 100

    print("\nURL:", url)
    print("Prediction:", prediction)
    print(
        "Model score:",
        round(confidence, 2),
        "%"
    )

print("\nTEST COMPLETED")
