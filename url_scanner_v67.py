
import joblib
from pathlib import Path

from url_validator_v68 import validate_url
from url_parser_v67 import split_url


# Load trained URL detection pipeline
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "url_threat_model.pkl"

saved = joblib.load(MODEL_PATH)
model = saved["pipeline"]


def scan_url(url):
    # Validate URL
    url = validate_url(url)

    # Extract URL information
    hostname, path = split_url(url)

    if not hostname:
        raise ValueError("Invalid URL.")

    # Pipeline handles TF-IDF automatically
    prediction = model.predict([url])[0]
    probabilities = model.predict_proba([url])[0]

    classes = list(model.classes_)

    benign_index = classes.index("benign")

    threat_score = float(
        1.0 - probabilities[benign_index]
    )

    if threat_score >= 0.80:
        risk_level = "HIGH MODEL SCORE"
    elif threat_score >= 0.50:
        risk_level = "NEEDS REVIEW"
    else:
        risk_level = "LOWER MODEL SCORE"

    return {
        "url": url,
        "hostname": hostname,
        "path": path,
        "prediction": str(prediction),
        "threat_score": round(threat_score * 100, 2),
        "risk_level": risk_level,
        "class_scores": {
            str(label): round(float(score) * 100, 2)
            for label, score in zip(classes, probabilities)
        }
    }


if __name__ == "__main__":
    test_url = "https://example.com"

    result = scan_url(test_url)

    print("URL:", result["url"])
    print("Prediction:", result["prediction"])
    print("Threat Score:", result["threat_score"])
    print("Risk Level:", result["risk_level"])
    print("Class Scores:", result["class_scores"])
