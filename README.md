
# 🛡️ CyberSentinel AI

### Advanced AI-Powered URL Threat Detection System

CyberSentinel AI is a Python-based cybersecurity project
that uses machine learning to classify URLs and generate
security analysis reports.

## 🚀 Features

- AI-powered URL threat classification
- Four categories: Benign, Phishing, Malware, Defacement
- URL format validation
- Model threat scoring
- Interactive Streamlit dashboard
- URL scan history
- CSV report export
- Premium single-page PDF security reports
- Dark futuristic cybersecurity interface

## 🧠 Machine Learning

Current deployed URL detection model: url_detector_v1

The classifier uses character-level TF-IDF features
from URL hostnames and paths.

The system analyzes URL text without visiting
the website or executing its content.

## 🛠️ Technologies

- Python
- Scikit-learn
- Streamlit
- Pandas
- ReportLab
- TF-IDF
- Machine Learning

## ⚠️ Security Disclaimer

CyberSentinel AI provides machine-learning estimates,
not verified website safety probabilities.

A low threat score does not guarantee safety.
A high threat score does not confirm malicious activity.
Known limitation: The current experimental model can
incorrectly classify legitimate websites as phishing
or other threats (false positives).

Model scores are not calibrated probabilities and
should not be used as the sole basis for security decisions.

## 📌 Project Status

Live demo deployed on Streamlit Community Cloud.
The URL detection model remains experimental.

## 📄 License

License not yet selected.

## Quick Start

### Windows Installation

1. Clone the repository:

    git clone https://github.com/danusikanselvam841-pixel/CyberSentinel-AI-Project.git

2. Open the project folder:

    cd CyberSentinel-AI-Project

3. Create a virtual environment:

    python -m venv .venv

4. Activate the environment:

    .venv\Scripts\Activate.ps1

5. Install dependencies:

    python -m pip install -r requirements.txt

6. Start the application:

    python -m streamlit run app.py

### Usage

- Scan URLs for potential security threats.
- Review threat predictions and scores.
- Export scan history as CSV.
- Download PDF security reports.

Note: AI predictions do not guarantee website safety.

## Live Demo

[Open CyberSentinel AI Web Application](https://cybersentinel-ai-project-z2dkbiovppvvyduqlkyrra.streamlit.app/)

