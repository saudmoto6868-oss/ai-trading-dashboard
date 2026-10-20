"""Alpha Vantage widgets: news sentiment, top gainers/losers, put/call ratio.
Key: ALPHAVANTAGE_API_KEY (env var or Streamlit secrets, never committed). Free tier is ~25 calls/day,
so callers cache for minutes. Responses with 'Note'/'Information' mean rate-limited / premium-only."""
from __future__ import annotations

import os

import requests

URL = "https://www.alphavantage.co/query"


def api_key() -> str:
    key = os.environ.get("ALPHAVANTAGE_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("ALPHAVANTAGE_API_KEY", "")
        except Exception:
            key = ""
    return key


def call(function: str, **params) -> dict:
    """-> {'data': dict|None, 'error': str|None}. Never raises."""
    key = api_key()
    if not key:
        return {"data": None, "error": "no key: set ALPHAVANTAGE_API_KEY in Streamlit Secrets"}
    try:
        r = requests.get(URL, params={"function": function, "apikey": key, **params}, timeout=20)
        d = r.json()
    except Exception as e:
        return {"data": None, "error": f"network/JSON: {e.__class__.__name__}"}
    if not isinstance(d, dict):
        return {"data": None, "error": "unexpected response"}
    msg = d.get("Note") or d.get("Information") or d.get("Error Message")
    if msg:
        return {"data": None, "error": str(msg)[:200]}
    return {"data": d, "error": None}


def parse_news(d: dict, limit: int = 20) -> list[dict]:
    out = []
    for a in (d or {}).get("feed", [])[:limit]:
        try:
            out.append({"title": a["title"], "url": a.get("url"), "source": a.get("source"),
                        "time": a.get("time_published"), "score": float(a.get("overall_sentiment_score", 0)),
                        "label": a.get("overall_sentiment_label", ""),
                        "tickers": ", ".join(t["ticker"] for t in a.get("ticker_sentiment", [])[:4])})
        except (KeyError, TypeError, ValueError):
            continue
    return out


def parse_movers(d: dict) -> dict:
    return {k: (d or {}).get(k, [])[:10] for k in ("top_gainers", "top_losers", "most_actively_traded")}


def news(tickers: str = "", topics: str = "") -> dict:
    p = {k: v for k, v in (("tickers", tickers), ("topics", topics)) if v}
    r = call("NEWS_SENTIMENT", sort="LATEST", limit=50, **p)
    return {"rows": parse_news(r["data"]) if r["data"] else [], "error": r["error"]}


def movers() -> dict:
    r = call("TOP_GAINERS_LOSERS")
    return {"data": parse_movers(r["data"]) if r["data"] else {}, "error": r["error"]}
