
import joblib
import pandas as pd

model = joblib.load(
    "models/url_threat_model.pkl"
)["pipeline"]

test_urls = [
    "https://example.com",
    "http://example.com",
    "example.com",
    "https://example.org",
    "https://example.net"
]

print("\nURL PREDICTION TEST\n")

for url in test_urls:
    prediction = model.predict([url])[0]
    probabilities = model.predict_proba([url])[0]

    print("URL:", url)
    print("Prediction:", prediction)

    for category, score in zip(
        model.classes_,
        probabilities
    ):
        print(f"  {category}: {score * 100:.2f}%")

    print("-" * 45)

df = pd.read_csv(
    "url_data/malicious_phish.csv",
    usecols=["url", "type"]
)

matches = df[
    df["url"].str.contains(
        "example.com",
        case=False,
        regex=False,
        na=False
    )
]

print("\nDATASET MATCHES:")
print(matches["type"].value_counts())
print(matches.head(10).to_string(index=False))
