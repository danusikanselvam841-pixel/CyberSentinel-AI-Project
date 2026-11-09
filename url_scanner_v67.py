
import joblib
import numpy as np

from urllib.parse import urlsplit
from url_validator_v68 import validate_url

from url_features_v67 import prepare_features
from url_parser_v67 import split_url


MODEL_PATH = "models/url_threat_model_v67.pkl"

saved = joblib.load(MODEL_PATH)

model = saved["model"]
host_vectorizer = saved["hostname_vectorizer"]
path_vectorizer = saved["path_vectorizer"]


def scan_url(url):
    url = validate_url(url)

    hostname, path = split_url(url)
   

    if not hostname:
        raise ValueError("Invalid URL.")

    X = prepare_features(
        [url],
        host_vectorizer,
        path_vectorizer,
        fit=False
    )

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    benign_index = list(model.classes_).index("benign")

    threat_score = float(
        1 - probabilities[benign_index]
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
            for label, score in zip(model.classes_, probabilities)
        }
    }


if __name__ == "__main__":

    print("=" * 55)
    print("CYBERSENTINEL AI V6.7 - URL THREAT SCANNER")
    print("=" * 55)

    while True:
        url = input("\nEnter URL (or 'exit'): ").strip()

        if url.lower() == "exit":
            break

        try:
            result = scan_url(url)

            print("\n" + "-" * 55)
            print("URL:", result["url"])
            print("Hostname:", result["hostname"])
            print("Path:", result["path"])
            print("Prediction:", result["prediction"])
            print("Threat score:", result["threat_score"], "%")
            print("Risk level:", result["risk_level"])

            print("\nCLASS SCORES")

            for label, score in result["class_scores"].items():
                print(f"{label:<15}: {score:.2f}%")

            print(
                "\nNote: Scores are uncalibrated model estimates, "
                "not verified safety probabilities."
            )

            print("-" * 55)

        except ValueError as error:
            print("Error:", error)
