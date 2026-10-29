"""Execution Cycle tab — pipeline tracker + quincunx 7 gates."""
from pathlib import Path
import streamlit.components.v1 as _components

_TEMPLATE = Path(__file__).with_name("execution_app.html")


def render() -> None:
    _html = _TEMPLATE.read_text(encoding="utf-8")
    _components.html(_html, height=900, scrolling=True)
