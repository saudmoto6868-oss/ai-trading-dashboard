"""Stock fundamentals from Finnhub (free plan: 60 calls/min; some endpoints, e.g. price targets, are premium -> shown as n/a).
Key: FINNHUB_API_KEY (config.py / env / Streamlit secrets); stays on the server. Endpoint/field names are from documentation memory."""
from __future__ import annotations

import os
import time
from datetime import date, timedelta

import requests

from config import FINNHUB_API_KEY

BASE = "https://finnhub.io/api/v1"
DEFAULT_TICKERS = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "SPY"]


def api_key() -> str:
    key = FINNHUB_API_KEY or os.environ.get("FINNHUB_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("FINNHUB_API_KEY", "")
        except Exception:
            key = ""
    return key


def _num(v):
    try:
        return None if v is None else float(v)
    except Exception:
        return None


def parse_stock(sym: str, quote, profile, metric, reco, earn_hist, earn_cal) -> dict:
    m = (metric or {}).get("metric") or {}
    q = quote or {}
    p = profile or {}
    r = (reco or [None])[0] if isinstance(reco, list) and reco else None
    out = {"sym": sym, "ok": bool(q.get("c") or p.get("name")), "name": p.get("name"), "industry": p.get("finnhubIndustry"),
           "price": _num(q.get("c")), "chg": _num(q.get("dp")), "mcap": (_num(p.get("marketCapitalization")) or 0) * 1e6 or None,
           "pe": _num(m.get("peTTM")), "eps": _num(m.get("epsTTM")), "ps": _num(m.get("psTTM")), "pb": _num(m.get("pbQuarterly")),
           "div": _num(m.get("dividendYieldIndicatedAnnual")), "beta": _num(m.get("beta")), "roe": _num(m.get("roeTTM")),
           "margin": _num(m.get("netProfitMarginTTM")), "rev_g": _num(m.get("revenueGrowthTTMYoy")), "debt_eq": _num(m.get("totalDebt/totalEquityQuarterly")),
           "hi52": _num(m.get("52WeekHigh")), "lo52": _num(m.get("52WeekLow")), "reco": None, "surprises": [], "next_earn": None}
    if r:
        out["reco"] = {"sb": r.get("strongBuy", 0), "b": r.get("buy", 0), "h": r.get("hold", 0), "s": r.get("sell", 0), "ss": r.get("strongSell", 0), "period": r.get("period")}
    for e in (earn_hist or [])[:4]:
        if e.get("actual") is not None and e.get("estimate") is not None:
            out["surprises"].append({"period": e.get("period"), "actual": _num(e["actual"]), "est": _num(e["estimate"]), "pct": _num(e.get("surprisePercent"))})
    cal = ((earn_cal or {}).get("earningsCalendar") or [])
    if cal:
        c0 = sorted(cal, key=lambda x: x.get("date", ""))[0]
        out["next_earn"] = {"date": c0.get("date"), "eps_est": _num(c0.get("epsEstimate"))}
    return out


def _get(path, key, **params):
    r = requests.get(BASE + path, params=dict(params, token=key), timeout=10)
    if r.status_code in (401, 403):
        return None
    if r.status_code == 429:
        time.sleep(2)
        r = requests.get(BASE + path, params=dict(params, token=key), timeout=10)
    r.raise_for_status()
    return r.json()


def _one(key, sym):
    def g(path, **kw):
        try:
            return _get(path, key, **kw)
        except Exception:
            return None
    today = date.today()
    return parse_stock(sym, g("/quote", symbol=sym), g("/stock/profile2", symbol=sym), g("/stock/metric", symbol=sym, metric="all"),
                       g("/stock/recommendation", symbol=sym), g("/stock/earnings", symbol=sym, limit=4),
                       g("/calendar/earnings", symbol=sym, **{"from": today.isoformat(), "to": (today + timedelta(days=120)).isoformat()}))


def fetch_stock_fund(tickers: tuple | list | None = None) -> dict:
    key = api_key()
    if not key:
        return {"ok": False, "err": "nokey", "stocks": []}
    from concurrent.futures import ThreadPoolExecutor
    t = list(dict.fromkeys(tickers or DEFAULT_TICKERS))[:10]
    try:
        with ThreadPoolExecutor(max_workers=3) as ex:
            res = list(ex.map(lambda s: _one(key, s), t))
    except Exception:
        return {"ok": False, "err": "net", "stocks": []}
    if not any(s["ok"] for s in res):
        return {"ok": False, "err": "badkey", "stocks": []}   # nothing came back for any ticker: most likely a rejected key or unreachable
    return {"ok": True, "stocks": res}
