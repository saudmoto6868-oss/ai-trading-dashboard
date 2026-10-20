"""Macro fundamentals: FRED (rates, inflation, jobs, dollar, VIX) + CFTC Commitments of Traders (speculator positioning).
FRED needs FRED_API_KEY (secrets/env, server-side only). CFTC public reporting needs no key.
Endpoint/field names are written from documentation memory: any series/market that fails shows 'n/a' instead of breaking the panel."""
from __future__ import annotations

import os

import requests

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
CFTC_URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"   # legacy futures-only COT

# (id, label, kind) kind: lvl = show level + change vs previous obs; yoy = year-over-year % of an index; diff = monthly change in thousands
FRED_SERIES = [("FEDFUNDS", "Fed funds rate %", "lvl"), ("DGS2", "US 2Y yield %", "lvl"), ("DGS10", "US 10Y yield %", "lvl"),
               ("T10Y2Y", "10Y-2Y curve %", "lvl"), ("CPIAUCSL", "CPI inflation YoY %", "yoy"), ("UNRATE", "Unemployment %", "lvl"),
               ("PAYEMS", "Nonfarm payrolls (monthly chg, K)", "diff"), ("DTWEXBGS", "Dollar index (broad)", "lvl"), ("VIXCLS", "VIX", "lvl")]
COT_MARKETS = [("Gold", "GOLD - COMMODITY%"), ("Euro FX", "EURO FX - CHICAGO%"), ("Yen", "JAPANESE YEN - CHICAGO%"), ("Pound", "BRITISH POUND%"),
               ("Crude oil", "CRUDE OIL, LIGHT SWEET%NEW YORK%"), ("Bitcoin", "BITCOIN - CHICAGO%"), ("S&P 500 e-mini", "E-MINI S&P 500%")]


def fred_key() -> str:
    key = os.environ.get("FRED_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("FRED_API_KEY", "")
        except Exception:
            key = ""
    return key


def parse_fred(sid: str, label: str, kind: str, payload: dict) -> dict:
    obs = []
    for o in (payload or {}).get("observations", []):   # requested newest first
        try:
            obs.append((o["date"], float(o["value"])))   # "." (no data) raises -> skipped
        except Exception:
            continue
    try:
        if kind == "yoy":
            val, prev = (obs[0][1] / obs[12][1] - 1) * 100, (obs[1][1] / obs[13][1] - 1) * 100
        elif kind == "diff":
            val, prev = obs[0][1] - obs[1][1], obs[1][1] - obs[2][1]
        else:
            val, prev = obs[0][1], obs[1][1]
        return {"id": sid, "label": label, "val": val, "prev": prev, "date": obs[0][0], "ok": True}
    except Exception:
        return {"id": sid, "label": label, "val": None, "prev": None, "date": None, "ok": False}


def parse_cot(label: str, rows: list) -> dict:
    """rows newest first -> net speculative (non-commercial) position, weekly change, 52-week percentile (0 = most short, 100 = most long)."""
    try:
        nets = [(r["report_date_as_yyyy_mm_dd"][:10], int(float(r["noncomm_positions_long_all"])) - int(float(r["noncomm_positions_short_all"])),
                 int(float(r.get("open_interest_all") or 0))) for r in rows]
        cur = nets[0][1]; vals = [n[1] for n in nets]; lo, hi = min(vals), max(vals)
        return {"name": label, "net": cur, "chg": cur - nets[1][1] if len(nets) > 1 else None, "pct": round((cur - lo) / (hi - lo) * 100) if hi > lo else 50,
                "weeks": len(nets), "date": nets[0][0], "oi": nets[0][2], "ok": True}
    except Exception:
        return {"name": label, "ok": False}


def _fred_one(key, spec):
    sid, label, kind = spec
    try:
        r = requests.get(FRED_URL, params={"series_id": sid, "api_key": key, "file_type": "json", "sort_order": "desc", "limit": 16}, timeout=10)
        if r.status_code in (400, 401, 403):
            return "badkey"
        r.raise_for_status()
        return parse_fred(sid, label, kind, r.json())
    except Exception:
        return {"id": sid, "label": label, "val": None, "ok": False}


def _cot_one(spec):
    label, like = spec
    try:
        r = requests.get(CFTC_URL, params={"$where": "market_and_exchange_names like '%s'" % like, "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": 52}, timeout=12)
        r.raise_for_status()
        return parse_cot(label, r.json())
    except Exception:
        return {"name": label, "ok": False}


def fetch_macro_fund() -> dict:
    from concurrent.futures import ThreadPoolExecutor
    out = {"fred": [], "cot": [], "fred_err": None}
    key = fred_key()
    with ThreadPoolExecutor(max_workers=8) as ex:
        cf = [ex.submit(_cot_one, m) for m in COT_MARKETS]
        ff = [ex.submit(_fred_one, key, f) for f in FRED_SERIES] if key else []
        res = [f.result() for f in ff]
        out["cot"] = [f.result() for f in cf]
    if not key:
        out["fred_err"] = "nokey"
    elif "badkey" in res:
        out["fred_err"] = "badkey"
    else:
        out["fred"] = res
    return out
