"""TIA interactive command cockpit."""
from __future__ import annotations
import streamlit as st


def render_tia():
    st.markdown("""
    <style>
    .tia-top{background:linear-gradient(110deg,#080a0d,#17140e 68%,#2a1e0b);border:1px solid #66502a;border-radius:15px;padding:15px 20px;margin:0 0 10px}
    .tia-k{font-size:10px;letter-spacing:3px;color:#c6a35e;font-weight:700}
    .tia-h{font-size:27px;letter-spacing:5px;color:#f3dfb5;font-weight:800}
    .tia-s{font-size:11px;letter-spacing:1.5px;color:#b9ad96}
    </style>
    <div class="tia-top"><div class="tia-k">TRADE INTELLIGENCE AGENCY · 6868</div>
    <div class="tia-h">TIA COMMAND WORKSPACE</div>
    <div class="tia-s">LIVE CHARTS · ORDER FLOW · LIQUIDITY · OPTIONS · MARKET INTELLIGENCE</div></div>
    """,unsafe_allow_html=True)
    c1,c2=st.columns([1,4])
    universe=c1.segmented_control("Universe",["Crypto","TradFi"],default="Crypto",key="tia_ws_universe")
    c2.caption("Drag widgets to move · resize from edges/corners · double-click title to maximize · chart toolbar controls timeframe, zoom, pan and drawing tools. Layout is saved independently for TIA in this browser.")
    from modules.tia_workspace import render_tia_workspace
    render_tia_workspace(height=1040,universe=universe or "Crypto")
