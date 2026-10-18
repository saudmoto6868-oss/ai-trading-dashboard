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


def _smt_pairs():
    try:
        from modules.smt import SMT_PAIRS
        return SMT_PAIRS
    except Exception:
        return []


def _gann_oos() -> dict:
    """Out-of-sample Gann zone result per timeframe from the weekly lab (data/strategy_lab.json); {} if missing."""
    import numpy as np
    path = Path(__file__).resolve().parent.parent / "data" / "strategy_lab.json"
    try:
        mt = path.stat().st_mtime
        if _OOS_CACHE.get("mt") == mt:
            return _OOS_CACHE["v"]
        gz = json.loads(path.read_text()).get("gzone") or {}
    except Exception:
        return {}
    out = {}
    for tf, rs in gz.items():
        a = np.asarray(rs, float)
        if a.ndim != 2 or len(a) < 2:
            continue
        d = a[:, 0] - a[:, 1]; sd = d.std(ddof=1)
        out[str(tf).lower()] = {"n": int(len(a)), "win": round(100 * float((a[:, 0] > 0).mean()), 1), "avg": round(float(a[:, 0].mean()), 3),
                                "rnd": round(float(a[:, 1].mean()), 3), "t": round(float(d.mean() / (sd / np.sqrt(len(d)))), 2) if sd > 0 else 0.0}
    _OOS_CACHE.update(mt=mt, v=out)
    return out


_OOS_CACHE: dict = {}

UI_THEMES = [("classic", "Classic"), ("lux", "1 · Less is More"), ("hud", "2 · Orbit HUD"), ("ember", "3 · Ember"), ("sunset", "4 · Sunset"),
             ("emerald", "5 · Emerald"), ("neon", "6 · Neon"), ("mono", "7 · Mono Data"), ("grafana", "8 · Grafana"), ("blueprint", "9 · Blueprint")]
# themes 3-9 (owner pictures 2026-10-18) share one engine: a palette -> CSS variables for the page, the top bar and the Workspace (+ chart colours).
# keys: bg page, panel/panel2 cards (see-through over the blurred picture), solid = card in front, line, txt, mut, acc accent, ink text on accent,
# up/dn candles, rad corner radius px, font, tt text-transform of titles, ls letter-spacing, glow card shadow
UI_PALETTES = {
    "ember":     dict(bg="#0f0f10", panel="rgba(28,28,30,.84)", panel2="rgba(44,44,47,.88)", solid="rgba(24,24,26,.97)", line="rgba(255,255,255,.08)", txt="#ececec", mut="#8e8e93",
                      acc="#ff5a36", ink="#1a0b06", up="#d9d9d9", dn="#ff5a36", rad=16, font="", tt="none", ls="0", glow="0 10px 30px rgba(0,0,0,.45)"),
    "sunset":    dict(bg="#22252b", panel="rgba(36,39,46,.84)", panel2="rgba(48,52,61,.88)", solid="rgba(32,35,41,.97)", line="rgba(255,255,255,.07)", txt="#ece8e2", mut="#9a958e",
                      acc="#f08a4b", ink="#1d0f06", up="#3fd0c9", dn="#f0784b", rad=14, font="", tt="none", ls="0", glow="0 12px 32px rgba(0,0,0,.4)"),
    "emerald":   dict(bg="#131516", panel="rgba(24,27,28,.82)", panel2="rgba(34,38,39,.86)", solid="rgba(20,22,23,.97)", line="rgba(45,224,185,.16)", txt="#dfe7e5", mut="#7d8a87",
                      acc="#2de0b9", ink="#03201a", up="#2de0b9", dn="#ff5c6c", rad=4, font="", tt="uppercase", ls=".08em", glow="0 0 18px rgba(45,224,185,.10)"),
    "neon":      dict(bg="#050505", panel="rgba(9,9,9,.9)", panel2="rgba(18,18,18,.92)", solid="rgba(6,6,6,.98)", line="rgba(255,255,255,.06)", txt="#f2f2f2", mut="#8a8a8a",
                      acc="#39ff7a", ink="#022b10", up="#39ff7a", dn="#ff3b3b", rad=18, font="", tt="none", ls="0", glow="0 0 24px rgba(57,255,122,.10)"),
    "mono":      dict(bg="#0a0a0a", panel="rgba(10,10,10,.9)", panel2="rgba(18,18,18,.92)", solid="rgba(8,8,8,.98)", line="rgba(255,255,255,.26)", txt="#e6e6e6", mut="#8c8c8c",
                      acc="#ffffff", ink="#000000", up="#e6e6e6", dn="#6f6f6f", rad=0, font="ui-monospace,Menlo,Consolas,monospace", tt="uppercase", ls=".1em", glow="none"),
    "grafana":   dict(bg="#111217", panel="rgba(24,27,31,.96)", panel2="rgba(32,36,41,.98)", solid="#181b1f", line="#2c3235", txt="#d8d9da", mut="#8e8e8e",
                      acc="#5794f2", ink="#ffffff", up="#73bf69", dn="#f2495c", rad=3, font="Inter,Roboto,'Segoe UI',sans-serif", tt="none", ls="0", glow="none"),
    "blueprint": dict(bg="#000000", panel="rgba(3,4,8,.86)", panel2="rgba(10,12,20,.9)", solid="rgba(2,3,6,.98)", line="rgba(150,175,255,.20)", txt="#e8ecff", mut="#8790b0",
                      acc="#9db8ff", ink="#05081a", up="#8fd3ff", dn="#c08fff", rad=2, font="", tt="uppercase", ls=".12em", glow="none"),
}


def ui_vars(theme: str) -> dict:
    """Palette of an engine theme (themes 3-9), {} for Classic / 1 / 2 (they have their own hand-made CSS)."""
    return dict(UI_PALETTES.get(theme, {}))


_UI_BG = {"lux": "lux_bg.jpg", "hud": "hud_bg.jpg", **{k: k + "_bg.jpg" for k in ("ember", "sunset", "emerald", "neon", "mono", "grafana", "blueprint")}}


def ui_theme_bg(theme: str) -> str:
    """Pre-blurred background picture of a dashboard theme as a data URI ('' if none)."""
    import base64
    f = _UI_BG.get(theme)
    if not f:
        return ""
    try:
        return "data:image/jpeg;base64," + base64.b64encode((Path(__file__).resolve().parent / "themes" / f).read_bytes()).decode()
    except Exception:
        return ""


def build_workspace_html(symbols: list, news: list | None = None, lang: str = "en",
                         api_base: str = "https://www.okx.com", alerts: list | None = None,
                         ws_base: str = "wss://ws.okx.com:8443/ws/v5", seed: dict | None = None, scan: dict | None = None, links: list | None = None,
                         filters: dict | None = None, ready: list | None = None, scanning: bool = False,
                         asset_cls: str = "Crypto", meme: list | None = None, world: list | None = None, tfstats: dict | None = None, cmc: dict | None = None, macrof: dict | None = None, stockf: dict | None = None, world_errs: list | None = None, yf: dict | None = None,
                         fh_token: str = "", cal: list | None = None, ui_theme: str = "", ui_bg: str = "") -> str:
    news = list(news or [])
    status = [str(n.get("headline", "")) for n in news if n.get("status")]   # placeholder rows from the news fetcher = status lines, not headlines
    if world_errs:
        status.append("World feeds failed: " + ", ".join(str(e) for e in world_errs[:6]))
    cfg = {
        "symbols": list(symbols),
        "feedStatus": status,
        "news": [
            {
                "headline": str(n.get("headline", "")),
                "source": str(n.get("source", "")),
                "url": str(n.get("url", "")),
                "summary": str(n.get("summary", "")),
                "datetime": str(n.get("datetime", "")),
            }
            for n in news if not n.get("status")
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
        "cls": asset_cls,
        "tfstats": tfstats or {},
        "smt": [list(x) for x in _smt_pairs()],
        "world": [{k: v for k, v in n.items() if k in ("headline", "source", "url", "summary", "datetime", "ts", "topic", "lang")} for n in (world or [])],
        "meme": list(meme or []),
        "cmc": cmc or {},
        "macrof": macrof or {},
        "stockf": stockf or {},
        "yf": yf or {},
        "fhToken": str(fh_token or ""),
        "gannoos": _gann_oos(),
        "ui": ui_theme or "", "uiBg": ui_bg or "", "uiVars": ui_vars(ui_theme or ""),   # dashboard theme from the top bar (+ its blurred background image as a data URI)
        "cal": [{k: e.get(k) for k in ("title", "country", "ts", "impact")} for e in (cal or [])][:120],   # economic calendar for the news check   # browser-visible on purpose (websocket from the viewer); empty = feature off
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


def _fh_token() -> str:
    """FINNHUB_WS_TOKEN (env or Streamlit Secrets): a key the BROWSER uses for the live CFD websocket, so it is visible in the
    page source. Kept separate from FINNHUB_API_KEY on purpose - the server key is never sent to the browser."""
    import os
    v = os.environ.get("FINNHUB_WS_TOKEN", "")
    if not v:
        try:
            import streamlit as st
            v = str(st.secrets.get("FINNHUB_WS_TOKEN", "") or "")
        except Exception:
            v = ""
    return v.strip()


def render_workspace(symbols: list, news: list | None = None, lang: str = "en", height: int = 860,
                     alerts: list | None = None, seed: dict | None = None, scan: dict | None = None, links: list | None = None,
                     filters: dict | None = None, ready: list | None = None, scanning: bool = False,
                     asset_cls: str = "Crypto", meme: list | None = None, world: list | None = None, tfstats: dict | None = None, cmc: dict | None = None, macrof: dict | None = None, stockf: dict | None = None, world_errs: list | None = None, yf: dict | None = None, cal: list | None = None, ui_theme: str = "", ui_bg: str = ""):
    import streamlit.components.v1 as components

    components.html(build_workspace_html(symbols, news, lang, alerts=alerts, seed=seed, scan=scan, links=links, filters=filters, ready=ready, scanning=scanning, asset_cls=asset_cls, meme=meme, world=world, tfstats=tfstats, cmc=cmc, macrof=macrof, stockf=stockf, world_errs=world_errs, yf=yf, fh_token=_fh_token(), cal=cal, ui_theme=ui_theme, ui_bg=ui_bg), height=height, scrolling=False)
