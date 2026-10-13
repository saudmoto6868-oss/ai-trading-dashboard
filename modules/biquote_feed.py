"""Biquote (biquote.io) candles as a FALLBACK for forex pairs and gold/silver when Yahoo fails.
Keyless, community MT5 CFD feed, package `biquote` (Beta). It has NO volume, and its docs only show interval "1h"
and limit 500, so the code asks for the interval it needs and, if that is rejected, derives it from 1h or fails
with a clear message (the next layer then shows the error instead of fake data). The row field names of ohlc()
are not documented on PyPI, so parsing accepts the usual spellings and raises if it finds none.
NOT verified against the live service from the build sandbox - tested with a mock only."""
from __future__ import annotations

import re
import threading
import time

import pandas as pd

from modules.data_fetcher import aggregate_frame

_TTL = {"1m": 20, "5m": 40, "15m": 60, "30m": 90, "1h": 90, "4h": 240, "1d": 600, "1w": 1800}
_cache: dict = {}
_lock = threading.Lock()
_PAIR = re.compile(r"^([A-Z]{3})([A-Z]{3})=X$")
_FUT = {"GC=F": "XAUUSD", "SI=F": "XAGUSD"}
_KEYS = {"time": ("time", "t", "timestamp", "ts", "date", "openTime"), "open": ("open", "o"), "high": ("high", "h"),
         "low": ("low", "l"), "close": ("close", "c", "mid")}


def symbol_for(sym: str) -> str | None:
    """"Y:EURUSD=X" -> "EURUSD", "Y:GC=F" -> "XAUUSD", anything Biquote cannot serve -> None."""
    s = sym[2:] if sym.startswith("Y:") else sym
    if s in _FUT:
        return _FUT[s]
    m = _PAIR.match(s)
    return m.group(1) + m.group(2) if m else None


def _pick(row: dict, names):
    for n in names:
        if n in row and row[n] is not None:
            return row[n]
    return None


def parse_ohlc(rows) -> pd.DataFrame:
    recs = []
    for r in rows or []:
        if not isinstance(r, dict):
            continue
        v = {k: _pick(r, n) for k, n in _KEYS.items()}
        if any(v[k] is None for k in _KEYS):
            continue
        recs.append(v)
    if not recs:
        raise ValueError("Biquote: no candles in the response (unknown format?)")
    df = pd.DataFrame(recs)
    t = df["time"]
    if pd.api.types.is_numeric_dtype(t):
        unit = "ms" if float(t.iloc[0]) > 1e11 else "s"
        df["time"] = pd.to_datetime(t, unit=unit)
    else:
        df["time"] = pd.to_datetime(t, utc=True).dt.tz_localize(None)
    for c in ("open", "high", "low", "close"):
        df[c] = df[c].astype(float)
    df["volume"] = 0.0
    return df.sort_values("time").reset_index(drop=True)


def _client():
    from biquote import Biquote   # imported lazily: the app must start even if the package is missing
    return Biquote()


def get_klines(sym: str, tf: str, limit: int = 300, client=None) -> pd.DataFrame:
    bq_sym = symbol_for(sym)
    if not bq_sym:
        raise ValueError("Biquote fallback: forex pairs and gold/silver only")
    key = (bq_sym, tf)
    with _lock:
        hit = _cache.get(key)
    if hit and time.time() - hit[0] < _TTL.get(tf, 60):
        return hit[1].tail(limit).reset_index(drop=True)
    bq = client or _client()
    n = 1
    try:
        df = parse_ohlc(bq.ohlc(bq_sym, interval=tf, limit=500))
    except Exception as e:
        if tf != "4h":
            raise RuntimeError(f"Biquote {tf}: {e}")
        try:
            df = aggregate_frame(parse_ohlc(bq.ohlc(bq_sym, interval="1h", limit=500)), 4, 60)
        except Exception as e2:
            raise RuntimeError(f"Biquote 4h: {e2}")
    with _lock:
        _cache[key] = (time.time(), df)
    return df.tail(limit).reset_index(drop=True)
