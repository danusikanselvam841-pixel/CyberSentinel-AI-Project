
import joblib
import numpy as np

from scipy.sparse import hstack, csr_matrix

from train_url_model_v62 import normalize_url
from url_features_v62 import get_url_features


MODEL_PATH = "models/url_threat_model_v65.pkl"

print("Loading CyberSentinel AI v6.5...")

saved = joblib.load(MODEL_PATH)

model = saved["model"]
vectorizer = saved["vectorizer"]
scaler = saved["scaler"]


def predict_urls(urls):
    normalized = [
        normalize_url(url)
        for url in urls
    ]

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

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)

    benign_index = list(model.classes_).index("benign")

    for url, prediction, probs in zip(
        urls, predictions, probabilities
    ):
        threat_score = (1 - probs[benign_index]) * 100

        print(
            f"{url:<42} "
            f"{prediction:<12} "
            f"Threat score: {threat_score:.2f}%"
        )

    return predictions


print("\nKNOWN DOMAIN TEST")
print("=" * 75)

known_urls = [
    "https://google.com",
    "https://github.com",
    "https://microsoft.com",
    "https://wikipedia.org",
    "https://example.com"
]

predict_urls(known_urls)


print("\nSCHEME CONSISTENCY TEST")
print("=" * 75)

domains = [
    "google.com",
    "github.com",
    "microsoft.com",
    "wikipedia.org",
    "example.com"
]

for domain in domains:
    variants = [
        domain,
        "http://" + domain,
        "https://" + domain
    ]

    predictions = predict_urls(variants)

    consistent = len(set(predictions)) == 1

    print(
        "Consistency:",
        "PASS" if consistent else "FAIL"
    )
    print("-" * 75)

print("\nTEST COMPLETED")
