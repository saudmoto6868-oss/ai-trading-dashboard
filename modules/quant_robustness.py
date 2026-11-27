"""Robustness Matrix tab — strategy × regime grid + markout decay + who pays us."""
from pathlib import Path
import streamlit as st

_TEMPLATE = Path(__file__).with_name("robustness_app.html")


def render() -> None:
    from modules.lab_banner import with_demo_banner
    _html = with_demo_banner(_TEMPLATE.read_text(encoding="utf-8"), 'المصفوفة وانحدار الـ markout مولّدة عشوائيًا', 'the matrix and markout decay are randomly generated')
    st.iframe(_html, height=900, alt="Quant Robustness Matrix interactive viewer")
