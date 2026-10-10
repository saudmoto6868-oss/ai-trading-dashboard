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
                         api_base: str = "https://www.okx.com", alerts: list | None = None,
                         ws_base: str = "wss://ws.okx.com:8443/ws/v5", seed: dict | None = None, scan: dict | None = None, links: list | None = None,
                         filters: dict | None = None, ready: list | None = None, scanning: bool = False) -> str:
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
        "alerts": list(alerts or []),
        "lang": lang if lang in ("en", "ar") else "en",
        "apiBase": api_base,
        "wsBase": ws_base,
        "seed": seed,
        "scan": scan or {},
        "links": links or [],
        "filters": filters or {},
        "ready": list(ready or []),
        "scanning": bool(scanning),
    }
    # "</" inside a <script> block would end it early
    payload = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    return _TEMPLATE.read_text(encoding="utf-8").replace("__CONFIG__", payload, 1)


def seed_from_df(symbol: str, tf: str, df, bars: int = 200) -> dict | None:
    """Snapshot of recent candles (from the server side) shown only if the
    browser cannot reach OKX directly, so the chart is never blank."""
    try:
        d = df.iloc[:-1].tail(bars)  # drop the forming candle so the page HTML stays stable between refreshes
        rows = [[int(t.timestamp() * 1000), float(o), float(h), float(l), float(c), float(v)]
                for t, o, h, l, c, v in zip(d["time"], d["open"], d["high"], d["low"], d["close"], d["volume"])]
        return {"sym": symbol, "tf": {"1h": "1H", "1d": "1D", "1w": "1W"}.get(tf, tf), "rows": rows}
    except Exception:
        return None


def render_workspace(symbols: list, news: list | None = None, lang: str = "en", height: int = 860,
                     alerts: list | None = None, seed: dict | None = None, scan: dict | None = None, links: list | None = None,
                     filters: dict | None = None, ready: list | None = None, scanning: bool = False):
    import streamlit.components.v1 as components

    components.html(build_workspace_html(symbols, news, lang, alerts=alerts, seed=seed, scan=scan, links=links, filters=filters, ready=ready, scanning=scanning), height=height, scrolling=False)
