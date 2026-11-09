
from pathlib import Path
import base64
import streamlit as st


def load_neon_theme():
    styles_dir = Path(__file__).resolve().parent / "styles"

    css = (styles_dir / "neon_circuit.css").read_text(
        encoding="utf-8"
    )

    svg_bytes = (styles_dir / "circuit_pattern.svg").read_bytes()
    encoded = base64.b64encode(svg_bytes).decode("ascii")

    css = css.replace(
        'url("circuit_pattern.svg")',
        f'url("data:image/svg+xml;base64,{encoded}")'
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )
