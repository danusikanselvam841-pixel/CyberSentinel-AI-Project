
import streamlit as st
import pandas as pd
from pdf_report_generator import generate_pdf_report

from datetime import datetime
from url_scanner_v67 import scan_url


st.set_page_config(
    page_title="CyberSentinel AI | URL Scanner",
    page_icon="🛡️",
    layout="wide"
)

# Initialize scan history
if "url_scan_history" not in st.session_state:
    st.session_state.url_scan_history = []


st.title("🛡️ CyberSentinel AI")
st.subheader("Advanced URL Threat Scanner")

st.caption(
    "AI-powered URL classification using "
    "hostname and path features."
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
        "Prediction": result["prediction"].upper(),
        "Threat Score": f'{result["threat_score"]:.2f}%',
        "Risk Level": result["risk_level"],
        "Model Version": "v6.7"
    }
)

            st.divider()

            col1, col2, col3 = st.columns([1, 1, 1.5])

            col1.metric(
                "Prediction",
                result["prediction"].upper()
            )

            col2.metric(
                "Model Threat Score",
                f'{result["threat_score"]:.2f}%'
            )

            col3.write("**Risk Level**")

            if result["risk_level"] == "HIGH MODEL SCORE":
                col3.error("HIGH MODEL SCORE")

            elif result["risk_level"] == "NEEDS REVIEW":
                col3.warning("NEEDS REVIEW")

            else:
                col3.info("LOWER MODEL SCORE")

            if result["risk_level"] == "HIGH MODEL SCORE":
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

            st.subheader("AI Class Scores")

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
            pdf_bytes = generate_pdf_report(result)

            st.download_button(
                label="📄 Download PDF Security Report",
                data=pdf_bytes,
                file_name="CyberSentinel_URL_Security_Report.pdf",
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
