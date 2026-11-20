"""
Micro · Foundations — standalone page
Embeds modules/micro_foundations.html (self-contained JS microstructure viewer).
Resolution Grid, Inventory Plane, Side Chain, Order Flow Hierarchy.
Based on docs/INSTITUTIONAL_FOUNDATIONS.md content.
"""
from __future__ import annotations
from pathlib import Path

import streamlit as st

_TEMPLATE = Path(__file__).with_name("micro_foundations.html")


def render() -> None:
    """Called from main.py to display the Micro Foundations page."""
    from modules.lab_banner import with_demo_banner
    _html = with_demo_banner(_TEMPLATE.read_text(encoding="utf-8"), 'الشبكة والرسوم عشوائية (النص المرجعي فقط حقيقي)', 'grids and charts are random (only the reference text is real)')
    st.iframe(_html, height=900, alt="Micro Foundations interactive viewer")
