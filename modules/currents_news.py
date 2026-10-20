"""Currents API headlines (https://api.currentsapi.services/v1/search, key as apiKey param) as one more news fallback.
Key -> Streamlit Secrets / env CURRENTS_API_KEY. Free-plan quota is stated inconsistently (100/day vs 100/month), so
results are cached 30 min by the caller and this is only used after Finnhub and Alpha Vantage fail. Mock-tested only."""
from __future__ import annotations

import os

import requests

URL = "https://api.currentsapi.services/v1/search"


def api_key() -> str:
    key = os.environ.get("CURRENTS_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("CURRENTS_API_KEY", "")
        except Exception:
            key = ""
    return key


def parse(d: dict, limit: int = 15) -> list[dict]:
    out = []
    for a in (d or {}).get("news") or []:
        t = (a.get("title") or "").strip()
        if t:
            out.append({"title": t, "url": a.get("url") or "", "source": a.get("author") or "Currents", "time": str(a.get("published") or "")[:16]})
    return out[:limit]


def fetch(limit: int = 15, keywords: str = "markets OR forex OR gold OR bitcoin", key: str | None = None, get=requests.get) -> list[dict]:
    key = key if key is not None else api_key()
    if not key:
        raise RuntimeError("no CURRENTS_API_KEY")
    r = get(URL, params={"apiKey": key, "keywords": keywords, "language": "en"}, timeout=10)
    if r.status_code != 200:
        raise RuntimeError(f"Currents HTTP {r.status_code}")
    rows = parse(r.json(), limit)
    if not rows:
        raise RuntimeError("Currents: no articles")
    return rows
