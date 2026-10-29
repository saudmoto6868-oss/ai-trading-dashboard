"""
Quant · Monte Carlo — standalone page
Embeds modules/montecarlo_app.html (self-contained JS Monte Carlo simulator).
Bootstrap resampling of trade returns: 7000 paths, ruin probability,
Quincunx 7 gates, p-value vs random baseline.
"""
from __future__ import annotations
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as _components

_TEMPLATE = Path(__file__).with_name("montecarlo_app.html")


def render() -> None:
    """Called from main.py to display the Monte Carlo page."""
    _html = _TEMPLATE.read_text(encoding="utf-8")
    _components.html(_html, height=900, scrolling=True)
