
import joblib
import numpy as np

from scipy.sparse import hstack, csr_matrix

from train_url_model_v62 import normalize_url
from url_features_v62 import get_url_features, FEATURE_NAMES


MODEL_PATH = "models/url_threat_model_v65.pkl"

saved = joblib.load(MODEL_PATH)

model = saved["model"]
vectorizer = saved["vectorizer"]
scaler = saved["scaler"]

classes = list(model.classes_)

benign_idx = classes.index("benign")
phishing_idx = classes.index("phishing")

feature_names = (
    list(vectorizer.get_feature_names_out())
    + list(FEATURE_NAMES)
)

coefficient_difference = (
    model.coef_[phishing_idx]
    - model.coef_[benign_idx]
)

intercept_difference = (
    model.intercept_[phishing_idx]
    - model.intercept_[benign_idx]
)

urls = [
    "https://google.com",
    "https://github.com",
    "https://microsoft.com",
    "https://wikipedia.org",
    "https://example.com"
]

for url in urls:
    text_features = vectorizer.transform(
        [normalize_url(url)]
    )

    numeric = np.asarray(
        [get_url_features(url)],
        dtype=np.float32
    )

    numeric = scaler.transform(numeric)

    X = hstack(
        [text_features, csr_matrix(numeric)],
        format="csr",
        dtype=np.float32
    )

    contributions = (
        X.multiply(coefficient_difference)
        .toarray()[0]
    )

    margin = (
        contributions.sum()
        + intercept_difference
    )

    print("\n" + "=" * 65)
    print("URL:", url)
    print("Prediction:", model.predict(X)[0])
    print("Phishing - Benign margin:", round(float(margin), 4))

    print("\nTOP FEATURES SUPPORTING PHISHING")

    positive = np.argsort(contributions)[::-1]

    count = 0

    for idx in positive:
        if contributions[idx] <= 0:
            break

        print(
            f"{feature_names[idx]:<30}"
            f"{contributions[idx]:+.4f}"
        )

        count += 1

        if count == 10:
            break

    print("\nTOP FEATURES SUPPORTING BENIGN")

    negative = np.argsort(contributions)

    count = 0

    for idx in negative:
        if contributions[idx] >= 0:
            break

        print(
            f"{feature_names[idx]:<30}"
            f"{contributions[idx]:+.4f}"
        )

        count += 1

        if count == 10:
            break

print("\nANALYSIS COMPLETED")
