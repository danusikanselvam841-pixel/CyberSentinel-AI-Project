
from pathlib import Path
import streamlit as st


def load_neon_theme():
    css_path = (
        Path(__file__).resolve().parent
        / "styles"
        / "neon_circuit.css"
    )

    if not css_path.exists():
        st.warning("Neon theme CSS file not found.")
        return

    css = css_path.read_text(encoding="utf-8")

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )
