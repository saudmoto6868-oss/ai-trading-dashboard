"""Macro regime signal (risk-on / neutral / risk-off) from five FRED series, built with NO look-ahead.

Series (direction = +1 when a HIGHER value means more stress):
  BAMLH0A0HYM2  US high-yield credit spread (daily)            +1
  VIXCLS        VIX (daily)                                   +1
  T10Y2Y        10Y - 2Y Treasury curve (daily)               -1   (inverted / falling curve = stress)
  NFCI          Chicago Fed financial conditions (weekly)     +1
  STLFSI4       St. Louis Fed financial stress (weekly)       +1

No look-ahead: a value dated D is only "known" from D + LAG days (publication delay: 1 day for the daily series, 5 for NFCI,
7 for STLFSI4). Each series is scored as a z-score of the last known value against the PREVIOUS 252 known values only.
Score = mean of the direction-adjusted z-scores (clipped to +-3); regime = risk-off above +0.5, risk-on below -0.5, else neutral.

Data: FRED's public CSV (fred.stlouisfed.org/graph/fredgraph.csv?id=..., no key). Not reachable from the build sandbox:
mock-tested only. A description of financial conditions, not a trade signal; it has NOT been backtested as a timing rule.
"""
from __future__ import annotations

import io
import time
from datetime import timedelta

import numpy as np
import pandas as pd
import requests

CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
SERIES = [  # id, label, direction, publication lag in days
    ("BAMLH0A0HYM2", "High-yield credit spread", 1, 1),
    ("VIXCLS", "VIX", 1, 1),
    ("T10Y2Y", "Yield curve 10Y-2Y", -1, 1),
    ("NFCI", "Chicago Fed financial conditions", 1, 5),
    ("STLFSI4", "St. Louis Fed financial stress", 1, 7),
]
WINDOW = 252
TH = 0.5
_cache: dict = {}


def parse_csv(text: str) -> pd.Series:
    """FRED CSV (DATE / observation_date + one value column, '.' = missing) -> float Series indexed by date."""
    df = pd.read_csv(io.StringIO(text))
    if df.shape[1] < 2:
        raise ValueError("FRED: unexpected CSV")
    d = pd.to_datetime(df.iloc[:, 0], errors="coerce")
    v = pd.to_numeric(df.iloc[:, 1], errors="coerce")
    s = pd.Series(v.values, index=d).dropna()
    return s[~s.index.isna()].sort_index()


def fetch(sid: str, years: int = 6, ttl: int = 6 * 3600, get=requests.get) -> pd.Series:
    """One series from FRED's public CSV (cached `ttl` s). Raises on network errors."""
    hit = _cache.get(sid)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    start = (pd.Timestamp.now() - pd.DateOffset(years=years)).strftime("%Y-%m-%d")
    r = get(CSV_URL, params={"id": sid, "cosd": start}, timeout=20)
    r.raise_for_status()
    s = parse_csv(r.text)
    _cache[sid] = (time.time(), s)
    return s


def known(s: pd.Series, lag: int) -> pd.Series:
    """The same values re-dated to the day they became public (date + lag)."""
    return pd.Series(s.values, index=s.index + timedelta(days=lag)).sort_index()


def z_at(s: pd.Series, when: pd.Timestamp, window: int = WINDOW):
    """z-score of the last value known at `when` against the `window` values known BEFORE it (needs >= 30). -> (z, value, date) or None."""
    past = s[s.index <= when]
    if len(past) < 31:
        return None
    ref = past.iloc[-window - 1:-1]
    sd = ref.std(ddof=1)
    if not (sd > 0):
        return None
    return float((past.iloc[-1] - ref.mean()) / sd), float(past.iloc[-1]), past.index[-1]


def regime_at(frames: dict, when, th: float = TH) -> dict:
    """frames = {series id: raw FRED Series}. -> {score, regime, parts:[{id, label, value, z, contrib, known_since}], n}."""
    when = pd.Timestamp(when)
    parts = []
    for sid, label, sign, lag in SERIES:
        s = frames.get(sid)
        if s is None or not len(s):
            continue
        r = z_at(known(s, lag), when)
        if r is None:
            continue
        z, v, d = r
        parts.append({"id": sid, "label": label, "value": v, "z": z, "contrib": float(np.clip(sign * z, -3, 3)), "known_since": d})
    if not parts:
        return {"score": None, "regime": None, "parts": [], "n": 0}
    sc = float(np.mean([p["contrib"] for p in parts]))
    return {"score": sc, "regime": "risk-off" if sc > th else "risk-on" if sc < -th else "neutral", "parts": parts, "n": len(parts)}


def history(frames: dict, start=None, end=None, freq: str = "W-FRI", th: float = TH) -> pd.DataFrame:
    """Walk-forward regime on a date grid (each row only uses what was public on that day). -> DataFrame date, score, regime, n."""
    idx = [s.index for s in frames.values() if s is not None and len(s)]
    if not idx:
        return pd.DataFrame(columns=["date", "score", "regime", "n"])
    lo = min(i.min() for i in idx) + timedelta(days=400)
    hi = max(i.max() for i in idx) + timedelta(days=7)
    start = max(pd.Timestamp(start), lo) if start is not None else lo
    end = min(pd.Timestamp(end), hi) if end is not None else hi
    rows = []
    for d in pd.date_range(start, end, freq=freq):
        r = regime_at(frames, d, th)
        if r["score"] is not None:
            rows.append({"date": d, "score": r["score"], "regime": r["regime"], "n": r["n"]})
    return pd.DataFrame(rows, columns=["date", "score", "regime", "n"])


def load_all(get=requests.get) -> tuple[dict, list]:
    """-> ({id: Series}, [errors]) for every series; a failed one is skipped and reported."""
    out, errs = {}, []
    for sid, label, _s, _l in SERIES:
        try:
            out[sid] = fetch(sid, get=get)
        except Exception as e:
            errs.append(f"{sid}: {type(e).__name__}")
    return out, errs
