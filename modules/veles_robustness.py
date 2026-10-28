"""
Veles · Robustness Lab — standalone page
Embeds modules/veles_robustness.html (self-contained JS robustness matrix).
Regime classification via ADX/ATR/BB, Markout Decay, Plateau Surface heatmap.
"""
from __future__ import annotations
from pathlib import Path

import streamlit.components.v1 as _components

_TEMPLATE = Path(__file__).with_name("veles_robustness.html")


def render() -> None:
    """Called from main.py to display the Robustness Lab page."""
    _html = _TEMPLATE.read_text(encoding="utf-8")
    _components.html(_html, height=900, scrolling=True)
