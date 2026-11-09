
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

urls = [
    "https://google.com",
    "https://github.com",
    "https://microsoft.com",
    "https://wikipedia.org",
    "https://example.com"
]

feature_names = (
    list(vectorizer.get_feature_names_out())
    + list(FEATURE_NAMES)
)

print("MODEL CLASSES:", model.classes_)

for url in urls:
    normalized = normalize_url(url)

    text_features = vectorizer.transform([normalized])

    numeric_features = np.asarray(
        [get_url_features(url)],
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

    prediction = model.predict(X)[0]

    print("\n" + "=" * 65)
    print("URL:", url)
    print("PREDICTION:", prediction)

    predicted_index = list(model.classes_).index(
        prediction
    )

    coefficients = model.coef_[predicted_index]

    contributions = X.multiply(coefficients).toarray()[0]

    top_indices = np.argsort(
        np.abs(contributions)
    )[::-1][:15]

    print("\nTOP FEATURE CONTRIBUTIONS")

    for idx in top_indices:
        if contributions[idx] != 0:
            print(
                f"{feature_names[idx]:<30} "
                f"{contributions[idx]:+.4f}"
            )

print("\nANALYSIS COMPLETED")
