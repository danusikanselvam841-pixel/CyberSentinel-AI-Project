
from pathlib import Path
from urllib.parse import urlsplit

import joblib
import streamlit as st

st.set_page_config(
    page_title="URL Threat Scanner | CyberSentinel AI",
    page_icon="🔗",
    layout="wide"
)

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "url_threat_model.pkl"
)

@st.cache_resource
def load_url_model():
    return joblib.load(MODEL_PATH)

st.title("🔗 URL Threat Scanner")
st.caption("CyberSentinel AI | Machine Learning URL Analysis")

st.info(
    "This scanner analyzes URL text patterns. "
    "It does not visit or execute the website."
)

if not MODEL_PATH.exists():
    st.error("URL model not found. Run train_url_model.py.")
    st.stop()

saved = load_url_model()
pipeline = saved["pipeline"]

url = st.text_input(
    "Enter website URL",
    placeholder="https://example.com"
)

if st.button("🔍 Analyze URL", type="primary"):
    url = url.strip()

    if not url:
        st.warning("Please enter a URL.")
        st.stop()

    if len(url) > 4096:
        st.error("URL is too long.")
        st.stop()

    # Validate input without visiting the website
    parsed = urlsplit(
        url if "://" in url else "http://" + url
    )

    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or " " in parsed.hostname
    ):
        st.error("Please enter a valid HTTP/HTTPS URL.")
        st.stop()

    prediction = pipeline.predict([url])[0]
    probabilities = pipeline.predict_proba([url])[0]

    scores = dict(
        zip(pipeline.classes_, probabilities)
    )

    confidence = max(scores.values()) * 100

    st.divider()
    st.subheader("Analysis Result")

    if prediction == "benign":
        st.success("🟢 Likely Legitimate URL")
    elif prediction == "phishing":
        st.error("🔴 Potential Phishing URL")
    elif prediction == "malware":
        st.error("🔴 Potential Malware URL")
    elif prediction == "defacement":
        st.warning("🟠 Defacement-Related URL Pattern")
    else:
        st.warning("Unknown prediction")

    col1, col2 = st.columns(2)

    col1.metric("Predicted Category", prediction.upper())
    col2.metric("Model Score", f"{confidence:.2f}%")

    st.subheader("Prediction Scores")

    for category, score in sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        st.write(
            f"{category.title()}: {score * 100:.2f}%"
        )
        st.progress(float(score))

    st.warning(
        "This is an experimental ML prediction, "
        "not a verified website safety assessment. "
        "A benign result does not guarantee safety, "
        "and model scores are not calibrated probabilities."
    )
