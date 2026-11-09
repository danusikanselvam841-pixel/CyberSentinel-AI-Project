
import joblib
from url_features_v67 import prepare_features

MODEL_PATH = "models/url_threat_model_v67.pkl"

saved = joblib.load(MODEL_PATH)

model = saved["model"]
host_vectorizer = saved["hostname_vectorizer"]
path_vectorizer = saved["path_vectorizer"]

urls = [
    "https://google.com",
    "https://github.com",
    "https://microsoft.com",
    "https://wikipedia.org",
    "https://example.com"
]

print("CYBERSENTINEL AI V6.7 - HOMEPAGE TEST")
print("=" * 70)

for url in urls:
    X = prepare_features(
        [url],
        host_vectorizer,
        path_vectorizer,
        fit=False
    )

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    benign_idx = list(model.classes_).index("benign")

    threat_score = (
        1 - probabilities[benign_idx]
    ) * 100

    print(
        f"{url:<35}"
        f"{prediction:<12}"
        f"Threat score: {threat_score:.2f}%"
    )

print("\nTEST COMPLETED")
