"""Options-flow filter on the Unusual Whales API (https://api.unusualwhales.com, Bearer auth).

Rules (all must hold): ask-side dominant, stock/ETF/ADR underlying, premium >= $45k,
volume > open interest, OTM, single-leg. Filtering is done client-side so it never depends on
server parameter names; a few well-known params are sent only to shrink the payload.

Key: UNUSUALWHALES_API_KEY (env var or Streamlit secrets - never commit it).
UNVERIFIED against the live API (sandbox cannot reach it): field names are read defensively and
`diagnose()` shows exactly what came back. Empty 200 = no data, not an error (per UW conventions).
"""
from __future__ import annotations

import os

import requests

BASE = "https://api.unusualwhales.com"
FLOW_PATH = "/api/option-trades/flow-alerts"
MIN_PREMIUM = 45_000
ASK_SHARE = 0.60                       # share of premium traded at the ask
ISSUE_OK = ("common stock", "etf", "adr")


def api_key() -> str:
    key = os.environ.get("UNUSUALWHALES_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("UNUSUALWHALES_API_KEY", "")
        except Exception:
            key = ""
    return key


def _f(d: dict, *names, default=None):
    for n in names:
        v = d.get(n)
        if v not in (None, ""):
            return v
    return default


def _num(v, default=0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _truthy(v) -> bool:
    return v is True or str(v).lower() in ("true", "1", "yes")


def check(a: dict, min_premium: float = MIN_PREMIUM, ask_share: float = ASK_SHARE) -> tuple[bool, str]:
    """-> (passes, reason-if-rejected)."""
    prem = _num(_f(a, "total_premium", "premium"))
    if prem < min_premium:
        return False, "premium"
    ask = _num(_f(a, "total_ask_side_prem", "ask_side_premium", "ask_premium"))
    if prem <= 0 or ask / prem < ask_share:
        return False, "not ask-side"
    it = str(_f(a, "issue_type", "underlying_type", default="")).lower()
    if it and it not in ISSUE_OK:
        return False, "not stock/ETF/ADR"
    if _num(_f(a, "volume", "total_size")) <= _num(_f(a, "open_interest")):
        return False, "vol<=OI"
    multi = _f(a, "has_multileg")
    single = _f(a, "has_singleleg")
    if (multi is not None and _truthy(multi)) or (single is not None and not _truthy(single)):
        return False, "multi-leg"
    strike, und = _num(a.get("strike")), _num(_f(a, "underlying_price", "stock_price"))
    typ = str(_f(a, "type", "option_type", default="")).lower()
    if not strike or not und or typ not in ("call", "put"):
        return False, "no strike/underlying"
    if (typ == "call" and strike <= und) or (typ == "put" and strike >= und):
        return False, "ITM"
    return True, ""


def filter_alerts(rows: list[dict], **kw) -> tuple[list[dict], dict]:
    """-> (kept rows sorted by premium desc, {reason: count} rejected)."""
    kept, why = [], {}
    for a in rows or []:
        if not isinstance(a, dict):
            continue
        ok, r = check(a, **kw)
        if ok:
            kept.append(a)
        else:
            why[r] = why.get(r, 0) + 1
    kept.sort(key=lambda a: -_num(_f(a, "total_premium", "premium")))
    return kept, why


def fetch(key: str | None = None, limit: int = 200, timeout: int = 20) -> dict:
    """-> {'rows', 'error', 'used', 'cap'}. Never raises."""
    key = key or api_key()
    if not key:
        return {"rows": [], "error": "no key: set UNUSUALWHALES_API_KEY in Streamlit Secrets", "used": None, "cap": None}
    hdr = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    tries = [{"min_premium": MIN_PREMIUM, "is_ask_side": "true", "is_otm": "true", "limit": limit}, {"limit": limit}]
    r = None
    for params in tries:                   # retry bare if the server rejects a filter name
        try:
            r = requests.get(BASE + FLOW_PATH, headers=hdr, params=params, timeout=timeout)
        except requests.RequestException as e:
            return {"rows": [], "error": f"network: {e.__class__.__name__}", "used": None, "cap": None}
        if r.status_code != 422:
            break
    used, cap = r.headers.get("x-uw-daily-req-count"), r.headers.get("x-uw-token-req-limit")
    if r.status_code in (401, 403):
        return {"rows": [], "error": f"HTTP {r.status_code}: key invalid or plan has no API access", "used": used, "cap": cap}
    if r.status_code == 429:
        return {"rows": [], "error": "HTTP 429: daily/rate limit reached", "used": used, "cap": cap}
    if r.status_code != 200:
        return {"rows": [], "error": f"HTTP {r.status_code}: {r.text[:160]}", "used": used, "cap": cap}
    try:
        data = r.json().get("data", [])
    except Exception:
        return {"rows": [], "error": "bad JSON", "used": used, "cap": cap}
    return {"rows": data if isinstance(data, list) else [], "error": None, "used": used, "cap": cap}


def diagnose(rows: list[dict]) -> str:
    """Field names of the first row - to spot a schema mismatch immediately."""
    return ", ".join(sorted(rows[0].keys())) if rows and isinstance(rows[0], dict) else "(no rows)"
