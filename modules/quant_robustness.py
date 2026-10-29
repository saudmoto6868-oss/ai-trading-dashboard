"""Robustness Matrix tab — strategy × regime grid + markout decay + who pays us."""
from pathlib import Path
import streamlit.components.v1 as _components

_TEMPLATE = Path(__file__).with_name("robustness_app.html")


def render() -> None:
    from modules.lab_banner import with_demo_banner
    _html = with_demo_banner(_TEMPLATE.read_text(encoding="utf-8"), 'المصفوفة وانحدار الـ markout مولّدة عشوائيًا', 'the matrix and markout decay are randomly generated')
    _components.html(_html, height=900, scrolling=True)
