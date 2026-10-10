"""
FREE-FORM WORKSPACE (Streamlit tab)
Embeds modules/workspace_app.html - a self-contained, client-side trading
workspace: draggable / resizable / minimisable / maximisable widgets (chart,
DOM, Time & Sales, Limit Tracking, watchlist, news, video, notes), our own
canvas candlestick chart with working zoom / pan / timeframes, and an
English / Arabic switch.

It talks to OKX's public REST API straight from the viewer's browser, so it
updates by itself without Streamlit reruns. No API key, no login, nothing
stored on a server (layout is kept in the browser's localStorage).
"""

from __future__ import annotations

import json
from pathlib import Path

_TEMPLATE = Path(__file__).with_name("workspace_app.html")


def build_workspace_html(symbols: list, news: list | None = None, lang: str = "en",
                         api_base: str = "https://www.okx.com") -> str:
    cfg = {
        "symbols": list(symbols),
        "news": [
            {
                "headline": str(n.get("headline", "")),
                "source": str(n.get("source", "")),
                "url": str(n.get("url", "")),
                "summary": str(n.get("summary", "")),
                "datetime": str(n.get("datetime", "")),
            }
            for n in (news or [])
        ],
        "lang": lang if lang in ("en", "ar") else "en",
        "apiBase": api_base,
    }
    # "</" inside a <script> block would end it early
    payload = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    return _TEMPLATE.read_text(encoding="utf-8").replace("__CONFIG__", payload, 1)


def render_workspace(symbols: list, news: list | None = None, lang: str = "en", height: int = 860):
    import streamlit.components.v1 as components

    components.html(build_workspace_html(symbols, news, lang), height=height, scrolling=False)
