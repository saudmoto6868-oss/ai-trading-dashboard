"""FRED (St. Louis Fed) macro snapshot: CPI year-on-year, Fed funds rate, 10Y yield, unemployment.
Free key -> Streamlit Secrets / env FRED_API_KEY (never in code). Monthly/daily economic data, NOT live prices.
Endpoint: https://api.stlouisfed.org/fred/series/observations (series_id, api_key, file_type=json, sort_order=desc, limit).
Mock-tested only - the build sandbox cannot reach the API."""
from __future__ import annotations

import os

import requests

URL = "https://api.stlouisfed.org/fred/series/observations"
# label, series id, mode: "yoy" = % change vs 12 months earlier, "level" = value as published
SERIES = [("CPI (YoY %)", "CPIAUCSL", "yoy"), ("Fed funds %", "FEDFUNDS", "level"),
          ("US 10Y yield %", "DGS10", "level"), ("Unemployment %", "UNRATE", "level")]


def api_key() -> str:
    key = os.environ.get("FRED_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("FRED_API_KEY", "")
        except Exception:
            key = ""
    return key


def parse_obs(d: dict) -> list[tuple[str, float]]:
    """-> [(date, value)] newest first, FRED's '.' (missing) rows dropped."""
    out = []
    for o in (d or {}).get("observations") or []:
        try:
            out.append((o["date"], float(o["value"])))
        except (KeyError, ValueError, TypeError):
            continue
    return out


def row_from(label: str, mode: str, obs: list[tuple[str, float]]) -> dict:
    if not obs:
        return {"label": label, "value": None, "date": "", "note": "no data"}
    date, v = obs[0]
    if mode == "yoy":
        if len(obs) < 13 or obs[12][1] == 0:
            return {"label": label, "value": None, "date": date, "note": "need 13 months"}
        v = (v / obs[12][1] - 1) * 100
    return {"label": label, "value": round(v, 2), "date": date, "note": ""}


def snapshot(key: str | None = None, get=requests.get) -> list[dict]:
    key = key if key is not None else api_key()
    if not key:
        return [{"label": "FRED", "value": None, "date": "", "note": "add FRED_API_KEY in Streamlit Secrets"}]
    rows = []
    for label, sid, mode in SERIES:
        try:
            r = get(URL, params={"series_id": sid, "api_key": key, "file_type": "json", "sort_order": "desc",
                                 "limit": 14 if mode == "yoy" else 3}, timeout=10)
            if r.status_code in (400, 401, 403):
                rows.append({"label": label, "value": None, "date": "", "note": f"key rejected (HTTP {r.status_code})"})
                continue
            if r.status_code == 429:
                rows.append({"label": label, "value": None, "date": "", "note": "rate limit"})
                continue
            r.raise_for_status()
            rows.append(row_from(label, mode, parse_obs(r.json())))
        except Exception as e:   # type name only: the message can contain the URL with the key
            rows.append({"label": label, "value": None, "date": "", "note": f"failed ({type(e).__name__})"})
    return rows
