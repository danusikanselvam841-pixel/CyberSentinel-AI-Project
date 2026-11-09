
import joblib

from train_url_model_v62 import normalize_url


MODEL_PATH = "models/url_threat_model_v66.pkl"

saved = joblib.load(MODEL_PATH)

model = saved["model"]
vectorizer = saved["vectorizer"]

print("Loading CyberSentinel AI v6.6...")

urls = [
    "https://google.com",
    "https://github.com",
    "https://microsoft.com",
    "https://wikipedia.org",
    "https://example.com"
]

print("\nKNOWN DOMAIN TEST")
print("=" * 70)

for url in urls:
    normalized = normalize_url(url)

    X = vectorizer.transform([normalized])

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    benign_index = list(model.classes_).index("benign")

    threat_score = (
        1 - probabilities[benign_index]
    ) * 100

    print(
        f"{url:<40} "
        f"{prediction:<12} "
        f"Threat score: {threat_score:.2f}%"
    )

print("\nSCHEME CONSISTENCY TEST")
print("=" * 70)

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

    predictions = []

    for url in variants:
        X = vectorizer.transform(
            [normalize_url(url)]
        )

        prediction = model.predict(X)[0]
        predictions.append(prediction)

        print(f"{url:<40} {prediction}")

    if len(set(predictions)) == 1:
        print("Consistency: PASS")
    else:
        print("Consistency: FAIL")

    print("-" * 70)

print("\nTEST COMPLETED")
