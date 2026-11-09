"""TIA's isolated interactive workspace shell.

Uses the existing browser-side chart/widget engine with a TIA-only storage namespace.
Original Workspace layouts, drawings and preferences remain untouched.
"""
from __future__ import annotations
import streamlit.components.v1 as components
from modules.workspace import build_workspace_html


def render_tia_workspace(height: int = 980, universe: str = "Crypto"):
    if universe == "Crypto":
        symbols = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT"]
        asset_class = "Crypto"
    else:
        symbols = ["HL:xyz:GOLD", "HL:xyz:SILVER", "HL:xyz:SP500",
                   "HL:xyz:XYZ100", "HL:xyz:EUR", "HL:xyz:GBP",
                   "HL:xyz:CL", "HL:xyz:BRENTOIL", "HL:xyz:JP225"]
        asset_class = "TradFi"
    doc = build_workspace_html(symbols=symbols, news=[], lang="en", asset_cls=asset_class,
                               ui_theme="gold", ui_mat="steel")
    # Isolate all localStorage/sessionStorage keys from the original Workspace.
    doc = doc.replace("ai_ws_v5", "tia_ws_v1")
    doc = doc.replace("<title>6868 X</title>", "<title>TIA Command Workspace</title>")
    doc = doc.replace(
        ":root{--panel0:#0e1114;--dot:#1b2027;--bg:#0b0e11;--panel:#161a1e;--panel2:#1e2329;--line:#2b3139;--txt:#eaecef;--mut:#848e9c;--grn:#0ecb81;--red:#f6465d;--gold:#f0b90b;--blue:#4aa3ff;--vio:#b57cff}",
        ":root{--panel0:#0d0c0a;--dot:#282117;--bg:#090a0c;--panel:#141311;--panel2:#201d18;--line:#51432c;--txt:#eee6d7;--mut:#a99d89;--grn:#31c48d;--red:#e66a67;--gold:#d6ad62;--blue:#78a9d1;--vio:#b59acb}"
    )
    components.html(doc, height=height, scrolling=False)
