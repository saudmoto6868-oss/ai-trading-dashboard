"""Alpha Vantage FX candles (daily + weekly) as a FALLBACK when Yahoo fails for a forex pair ("Y:EURUSD=X").
Tested on the free key: FX_DAILY works; FX_INTRADAY and INDEX_DATA are premium-only, so no small frames and no indices here.
Free tier is ~25 calls/day shared with the news widgets, so one FX_DAILY call per pair is cached for 12 h and weekly bars
are derived from it."""
from __future__ import annotations

import re
import threading
import time

import pandas as pd

from modules import alphavantage

_TTL = 12 * 3600
_cache: dict = {}
_lock = threading.Lock()
_PAIR = re.compile(r"^([A-Z]{3})([A-Z]{3})=X$")


def pair(sym: str):
    """"Y:EURUSD=X" -> ("EUR", "USD"), anything else -> None."""
    m = _PAIR.match(sym[2:] if sym.startswith("Y:") else sym)
    return (m.group(1), m.group(2)) if m else None


def parse_fx_daily(d: dict) -> pd.DataFrame:
    ts = (d or {}).get("Time Series FX (Daily)")
    if not ts:
        raise ValueError("Alpha Vantage: no FX series")
    rows = [(pd.Timestamp(k), float(v["1. open"]), float(v["2. high"]), float(v["3. low"]), float(v["4. close"])) for k, v in ts.items()]
    df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close"]).sort_values("time")
    df["volume"] = 0.0
    return df.reset_index(drop=True)


def weekly(df: pd.DataFrame) -> pd.DataFrame:
    w = df.set_index("time").resample("W-SUN", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}).dropna(subset=["open"])
    w.index = w.index + pd.Timedelta(days=1)   # week starts Monday
    return w.reset_index()


def get_fx_klines(sym: str, tf: str, limit: int = 300) -> pd.DataFrame:
    p = pair(sym)
    if not p:
        raise ValueError("Alpha Vantage fallback: forex pairs only")
    if tf not in ("1d", "1w"):
        raise ValueError(f"Alpha Vantage free tier has no {tf} forex candles (daily/weekly only)")
    key = p
    with _lock:
        hit = _cache.get(key)
    if hit and time.time() - hit[0] < _TTL:
        df = hit[1]
    else:
        r = alphavantage.call("FX_DAILY", from_symbol=p[0], to_symbol=p[1], outputsize="full")
        if r["error"]:
            if hit:   # stale copy beats nothing
                df = hit[1]
            else:
                raise RuntimeError("Alpha Vantage: " + r["error"])
        else:
            df = parse_fx_daily(r["data"])
            with _lock:
                _cache[key] = (time.time(), df)
    out = df if tf == "1d" else weekly(df)
    return out.tail(limit).reset_index(drop=True)
