
from pathlib import Path
from theme import load_neon_theme
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="CyberSentinel AI | Security Operations",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)
load_neon_theme()
st.markdown("""
<style>
.stApp {
    background: #0B1120;
    color: #E2E8F0;
}
[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #263449;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    color: #F8FAFC !important;
}
[data-testid="stMetric"] {
    background: #151F32;
    border: 1px solid #29374D;
    border-radius: 14px;
    padding: 18px;
}
[data-testid="stMetricValue"] {
    color: #38BDF8;
}
div[data-testid="stFileUploader"] {
    border-radius: 12px;
}
.stButton > button,
.stDownloadButton > button {
    background: #0284C7;
    color: white;
    border: none;
    border-radius: 9px;
}
</style>
""", unsafe_allow_html=True)

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "cybersentinel_validated.pkl"
)

@st.cache_resource
def load_model(path):
    return joblib.load(path)

SEVERITY = {
    "BENIGN": "Normal",
    "Bot": "High",
    "DDoS": "Critical",
    "DoS GoldenEye": "High",
    "DoS Hulk": "High",
    "DoS Slowhttptest": "High",
    "DoS slowloris": "High",
    "FTP-Patator": "Medium",
    "PortScan": "Medium",
    "SSH-Patator": "Medium",
    "Web Attack - Brute Force": "High",
    "Web Attack - XSS": "High"
}

COLORS = {
    "Normal": "#22C55E",
    "Medium": "#FACC15",
    "High": "#F97316",
    "Critical": "#EF4444",
    "Unknown": "#94A3B8"
}

st.sidebar.markdown("## 🛡️ CyberSentinel AI")
st.sidebar.caption("SECURITY OPERATIONS CENTER")
st.sidebar.divider()

st.title("🛡️ CyberSentinel AI")
st.caption(
    "AI-Powered Network Intrusion Detection | "
    "Security Analytics Dashboard"
)

if not MODEL_PATH.exists():
    st.error(
        "Validated model not found. "
        "Run python validate_model.py first."
    )
    st.stop()

try:
    saved = load_model(str(MODEL_PATH))
    pipeline = saved["pipeline"]
    features = saved["features"]
except Exception as error:
    st.error(f"Unable to load model: {error}")
    st.stop()

st.sidebar.success("● AI ENGINE ONLINE")
st.sidebar.write(
    "Model:",
    saved.get("model_version", "Unknown")
)
st.sidebar.write("Features:", len(features))
st.sidebar.info("Offline CSV analysis only")
st.sidebar.warning(
    "Research prototype — not a live security monitor."
)

st.markdown("### Network Traffic Intelligence")

uploaded_file = st.file_uploader(
    "Upload CIC-IDS2017 compatible network flow CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.info(
        "Upload a compatible CSV file to start "
        "AI-powered traffic classification."
    )
    st.markdown("#### Supported Analysis")
    a, b, c = st.columns(3)
    a.info("📊 Traffic Classification")
    b.info("🚨 Threat Severity Analytics")
    c.info("📁 Downloadable Reports")
    st.stop()

try:
    df = pd.read_csv(
        uploaded_file,
        low_memory=False
    )
except Exception as error:
    st.error(f"CSV reading failed: {error}")
    st.stop()

df.columns = df.columns.str.strip()

if df.empty:
    st.error("Uploaded CSV contains no records.")
    st.stop()

missing = [
    feature for feature in features
    if feature not in df.columns
]

if missing:
    st.error(
        f"Missing {len(missing)} required features."
    )
    st.write(missing)
    st.stop()

X = df[features].copy()

for column in features:
    X[column] = pd.to_numeric(
        X[column],
        errors="coerce"
    )

X = X.replace(
    [np.inf, -np.inf],
    np.nan
)

if X.isna().all(axis=1).any():
    st.error(
        "Some rows have no valid numerical "
        "feature values."
    )
    st.stop()

with st.spinner("Analyzing network traffic..."):
    predictions = pipeline.predict(X)
    probabilities = pipeline.predict_proba(X)
    confidence = probabilities.max(axis=1)

results = df.copy()
results["Predicted Attack"] = predictions
results["Confidence"] = np.round(
    confidence * 100, 2
)
results["Severity"] = [
    SEVERITY.get(label, "Unknown")
    for label in predictions
]

total = len(results)
threats = int(
    (results["Predicted Attack"] != "BENIGN").sum()
)
benign = total - threats
critical = int(
    (results["Severity"] == "Critical").sum()
)
threat_rate = threats / total * 100

st.markdown("### Security Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Network Flows", f"{total:,}")
c2.metric("Threat Predictions", f"{threats:,}")
c3.metric("Benign Predictions", f"{benign:,}")
c4.metric("Critical Predictions", f"{critical:,}")

st.progress(
    min(max(threat_rate / 100, 0.0), 1.0),
    text=f"Predicted Threat Rate: {threat_rate:.1f}%"
)

st.caption(
    "Threat rate is the proportion of uploaded "
    "records predicted as non-BENIGN. "
    "It is not a measure of confirmed attacks."
)

st.divider()

left, right = st.columns([1.5, 1])

with left:
    st.subheader("Attack Distribution")

    attack_counts = (
        results["Predicted Attack"]
        .value_counts()
        .reset_index()
    )
    attack_counts.columns = [
        "Attack Category", "Count"
    ]

    fig = px.bar(
        attack_counts,
        x="Attack Category",
        y="Count",
        color="Attack Category",
        template="plotly_dark"
    )
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="#0B1120",
        plot_bgcolor="#111827",
        xaxis_tickangle=-35,
        height=420
    )
    st.plotly_chart(
        fig,
        width="stretch"
    )

with right:
    st.subheader("Threat Severity")

    severity_counts = (
        results["Severity"]
        .value_counts()
        .reset_index()
    )
    severity_counts.columns = [
        "Severity", "Count"
    ]

    fig2 = px.pie(
        severity_counts,
        names="Severity",
        values="Count",
        hole=0.6,
        color="Severity",
        color_discrete_map=COLORS,
        template="plotly_dark"
    )
    fig2.update_layout(
        paper_bgcolor="#0B1120",
        height=420
    )
    st.plotly_chart(
        fig2,
        width="stretch"
    )

st.divider()

st.subheader("Detection Explorer")

attack_options = sorted(
    results["Predicted Attack"].unique().tolist()
)

selected_attacks = st.multiselect(
    "Filter by attack category",
    options=attack_options,
    default=attack_options
)

severity_options = [
    "Normal", "Medium", "High",
    "Critical", "Unknown"
]

selected_severity = st.multiselect(
    "Filter by severity",
    options=severity_options,
    default=severity_options
)

filtered = results[
    results["Predicted Attack"].isin(
        selected_attacks
    )
    & results["Severity"].isin(
        selected_severity
    )
]

st.caption(
    f"Showing {len(filtered):,} "
    f"of {total:,} records"
)

display_columns = [
    "Predicted Attack",
    "Severity",
    "Confidence"
]

if "Destination Port" in results.columns:
    display_columns.append("Destination Port")

if "Flow Duration" in results.columns:
    display_columns.append("Flow Duration")

st.dataframe(
    filtered[display_columns],
    width="stretch",
    height=380
)

st.subheader("Export Security Report")

report_csv = filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered CSV Report",
    data=report_csv,
    file_name="cybersentinel_security_report.csv",
    mime="text/csv"
)

st.divider()

st.caption(
    "CyberSentinel AI | Research Prototype | "
    "CIC-IDS2017 | Random Forest"
)

st.warning(
    "Severity is a predefined category label, "
    "not a verified risk assessment. "
    "Confidence represents the model's estimated "
    "class probability, not guaranteed correctness. "
    "This prototype may miss attacks or produce "
    "false alarms and should not be used as a "
    "standalone security control."
)
