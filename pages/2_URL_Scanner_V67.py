
import streamlit as st
import pandas as pd
from pdf_report_generator import generate_pdf_report
from theme import load_neon_theme

from datetime import datetime
from url_scanner_v67 import scan_url, MODEL_VERSION


st.set_page_config(
    page_title="CyberSentinel AI | URL Scanner",
    page_icon="🛡️",
    layout="wide"
)
load_neon_theme()

# Initialize scan history
if "url_scan_history" not in st.session_state:
    st.session_state.url_scan_history = []


st.title("🛡️ CyberSentinel AI")
st.subheader("Experimental URL Text Classifier")

st.caption(
    "Experimental URL classification based on text features. "
    "This is not an independently verified security scan."
)

url = st.text_input(
    "Enter a URL",
    placeholder="https://example.com"
)


if st.button("🔍 Scan URL", type="primary"):

    if not url.strip():
        st.warning("Please enter a URL.")

    else:
        try:
            with st.spinner("Analyzing URL..."):
                result = scan_url(url)

            # Save scan result once
            st.session_state.url_scan_history.insert(
    0,
    {
        "Scan Time": datetime.now().astimezone().strftime(
            "%Y-%m-%d %H:%M:%S %z"
        ),
        "URL": result["url"],
        "Prediction": result["display_prediction"],
        "Threat Score": f'{result["threat_score"]:.2f}%',
        "Risk Level": result["risk_level"],
        "Model Version": MODEL_VERSION
    }
)

            st.divider()

            st.warning(
                "MODEL-ONLY RESULT - NOT A VERIFIED SECURITY VERDICT. "
                "PHISHING predictions may be false positives. "
                "BENIGN predictions may miss actual threats. "
                "Verify URLs using independent security sources."
            )

            col1, col2, col3 = st.columns([1, 1, 1.5])

            col1.metric(
                "Unverified Model Label",
                result["display_prediction"]
            )

            col2.metric(
                "Uncalibrated Model Score",
                f'{result["threat_score"]:.2f}%'
            )

            col3.write("**Model Flag Level (Unverified)**")

            if result["review_required"]:
                col3.warning("MODEL RESULT UNVERIFIED")
            elif result["risk_level"] in ("HIGH MODEL SCORE", "MODEL FLAG - VERIFY"):
                col3.error(result["risk_level"])

            elif result["risk_level"] == "NEEDS REVIEW":
                col3.warning("NEEDS REVIEW")

            else:
                col3.info("LOWER MODEL SCORE")

            if result["review_required"]:
                st.warning(
                    "Possible model false positive on an official homepage. "
                    "The raw AI prediction is "
                    f"{result['prediction'].upper()}. "
                    "Website safety has NOT been independently verified."
                )
            elif result["risk_level"] in ("HIGH MODEL SCORE", "MODEL FLAG - VERIFY"):
                st.error(
                    "High model threat score. "
                    "Avoid trusting this URL without verification."
                )

            elif result["risk_level"] == "NEEDS REVIEW":
                st.warning(
                    "This URL needs additional verification."
                )

            else:
                st.info(
                    "Lower model threat score. "
                    "This does not guarantee the URL is safe."
                )

            st.subheader("URL Validation")
            st.success("URL Format: VALID")

            st.info(
                "Input security checks passed. "
                "This does not guarantee the website is safe."
            )

            st.subheader("URL Information")

            st.write("**Hostname:**", result["hostname"])
            st.write("**Path:**", result["path"])

            st.subheader("Uncalibrated AI Class Scores")

            for label, score in result["class_scores"].items():
                st.write(f"{label.title()}: {score:.2f}%")
                st.progress(
                    min(max(score / 100, 0.0), 1.0)
                )

            st.caption(
                "Scores are uncalibrated model estimates. "
                "This scanner does not visit the URL or "
                "inspect live website content."
            )
            
            
            # Generate PDF report for the current URL
            pdf_result = dict(result)
            if result["review_required"]:
                pdf_result["prediction"] = "unverified"
            pdf_bytes = generate_pdf_report(pdf_result)

            st.download_button(
                label="📄 Download PDF (UNVERIFIED model output)",
                data=pdf_bytes,
                file_name="CyberSentinel_Unverified_Model_Report.pdf",
                mime="application/pdf",
                width="stretch"
            )


        except ValueError as error:
            st.error(str(error))


# Scan History
st.divider()
st.subheader("Scan History")

if st.session_state.url_scan_history:

    history_df = pd.DataFrame(
        st.session_state.url_scan_history
    )

    st.dataframe(
        history_df,
        width="stretch",
        hide_index=True
    )

    # CSV report
    csv_data = history_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="📥 Download CSV Report",
        data=csv_data,
        file_name="CyberSentinel_URL_Scan_Report.csv",
        mime="text/csv",
        width="stretch"
    )

    if st.button("Clear Scan History"):
        st.session_state.url_scan_history = []
        st.rerun()

else:
    st.info("No URLs scanned in this session yet.")
