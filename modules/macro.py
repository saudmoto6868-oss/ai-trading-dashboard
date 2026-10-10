"""Macro watchlist (gold, oil, EUR/USD, DXY ...) from TwelveData. Needs TWELVEDATA_API_KEY
(config.py, env var or Streamlit secrets); without it the widget shows how to enable it."""
from __future__ import annotations

import os

import requests

from config import TWELVEDATA_API_KEY

MACRO = [("Gold", "XAU/USD"), ("Oil WTI", "WTI/USD"), ("EUR/USD", "EUR/USD"), ("DXY", "DXY"),
         ("USD/JPY", "USD/JPY"), ("GBP/USD", "GBP/USD")]
URL = "https://api.twelvedata.com/quote"


def api_key() -> str:
    key = TWELVEDATA_API_KEY or os.environ.get("TWELVEDATA_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("TWELVEDATA_API_KEY", "")
        except Exception:
            key = ""
    return key


def parse_quotes(payload: dict) -> list[dict]:
    """TwelveData batch /quote -> [{'name','symbol','price','pct','ok'}]; one bad symbol never hides the rest."""
    out = []
    for name, sym in MACRO:
        d = payload.get(sym) if isinstance(payload.get(sym), dict) else (payload if payload.get("symbol") == sym else {})
        try:
            if not d or d.get("status") == "error" or d.get("code"):
                raise ValueError
            out.append({"name": name, "symbol": sym, "price": float(d["close"]), "pct": float(d.get("percent_change", 0)), "ok": True})
        except Exception:
            out.append({"name": name, "symbol": sym, "price": None, "pct": None, "ok": False})
    return out


def fetch_macro(key: str | None = None) -> list[dict]:
    key = key or api_key()
    if not key:
        return []
    r = requests.get(URL, params={"symbol": ",".join(s for _, s in MACRO), "apikey": key}, timeout=10)
    r.raise_for_status()
    return parse_quotes(r.json())
