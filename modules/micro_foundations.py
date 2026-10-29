"""
Micro · Foundations — standalone page
Embeds modules/micro_foundations.html (self-contained JS microstructure viewer).
Resolution Grid, Inventory Plane, Side Chain, Order Flow Hierarchy.
Based on docs/INSTITUTIONAL_FOUNDATIONS.md content.
"""
from __future__ import annotations
from pathlib import Path

import streamlit.components.v1 as _components

_TEMPLATE = Path(__file__).with_name("micro_foundations.html")


def render() -> None:
    """Called from main.py to display the Micro Foundations page."""
    _html = _TEMPLATE.read_text(encoding="utf-8")
    _components.html(_html, height=900, scrolling=True)
