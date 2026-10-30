"""MARKET CONTEXT LAYER (ICT 'where / when / which side' filters).
These do not create signals and never change the star count. They describe the setting a signal appears in, so the
scorer / UI can show whether the setup agrees with it:
  daily bias   : the previous COMPLETED New-York day closed above the high / below the low of the day before = that side only;
                 a close back inside the range = no bias; two inside days in a row = accumulation, stand aside.
  premium/disc : position of price inside the dealing range (latest major swing low -> swing high). Longs live in discount (<50%),
                 shorts in premium (>50%). Context, not a signal - trends can stay on the 'wrong' side for long.
  time window  : New York killzones (London 02-05, NY AM 07-10) and the Silver Bullet hours (03-04, 10-11, 14-15), DST-correct.
Intraday frames only (the day logic needs several days of candles and a 'time' column)."""
from __future__ import annotations

import pandas as pd

from modules.signals import fractal_pivots

NY = "America/New_York"
KILLZONES = (("London", 2, 5), ("NY AM", 7, 10))
SILVER = ((3, 4), (10, 11), (14, 15))


def _ny_time(df):
    t = pd.to_datetime(df["time"])
    return t.dt.tz_localize("UTC").dt.tz_convert(NY) if t.dt.tz is None else t.dt.tz_convert(NY)


def _step_s(df):
    t = pd.to_datetime(df["time"])
    return (t.iloc[-1] - t.iloc[-2]).total_seconds() if len(t) > 1 else 0


def time_window(df):
    """-> {'kz': 'London'|'NY AM'|None, 'silver': bool, 'ny_hour': float} for the last candle."""
    if "time" not in df.columns or len(df) < 2 or _step_s(df) > 4 * 3600:
        return {"kz": None, "silver": False, "ny_hour": None}
    ts = _ny_time(df).iloc[-1]; hr = ts.hour + ts.minute / 60
    kz = next((n for n, a, b in KILLZONES if a <= hr < b), None)
    return {"kz": kz, "silver": any(a <= hr < b for a, b in SILVER), "ny_hour": round(hr, 2)}


def daily_bias(df):
    """-> {'bias': 'bullish'|'bearish'|'inside'|'neutral'|None, 'accumulation': bool, 'why': str}"""
    if "time" not in df.columns or len(df) < 30 or _step_s(df) > 4 * 3600:
        return {"bias": None, "accumulation": False, "why": ""}
    ny = _ny_time(df); day = ny.dt.date
    g = df.assign(_d=day.values).groupby("_d").agg(o=("open", "first"), h=("high", "max"), l=("low", "min"), c=("close", "last"))
    if len(g) < 4:
        return {"bias": None, "accumulation": False, "why": ""}
    d1, d2, d3 = g.iloc[-2], g.iloc[-3], g.iloc[-4]          # last row = today (still forming)
    inside = lambda a, b: a.h <= b.h and a.l >= b.l
    acc = bool(inside(d1, d2) and inside(d2, d3))
    if d1.c > d2.h: b, why = "bullish", "yesterday closed above the previous day's high"
    elif d1.c < d2.l: b, why = "bearish", "yesterday closed below the previous day's low"
    elif inside(d1, d2): b, why = "inside", "yesterday stayed inside the previous day's range"
    else: b, why = "neutral", "yesterday closed back inside the previous day's range"
    return {"bias": b, "accumulation": acc, "why": why}


def premium_discount(df, look: int = 150):
    """-> {'zone': 'discount'|'premium'|'equilibrium'|None, 'pos': 0-100, 'lo', 'hi', 'eq'} (dealing range = latest major swing pair)."""
    seg = df.tail(look).reset_index(drop=True)
    if len(seg) < 40: return {"zone": None}
    piv = fractal_pivots(seg, 5); hs = [p for p in piv if p[2] == "H"]; ls = [p for p in piv if p[2] == "L"]
    if not hs or not ls: return {"zone": None}
    hi = float(seg['high'].iloc[hs[-1][0]:].max()); lo = float(seg['low'].iloc[ls[-1][0]:].min())   # the range always contains the current price (a new extreme extends it)
    if hi <= lo: return {"zone": None}
    px = float(seg["close"].iloc[-1]); pos = (px - lo) / (hi - lo)
    zone = "equilibrium" if 0.45 <= pos <= 0.55 else "discount" if pos < 0.5 else "premium"
    return {"zone": zone, "pos": round(100 * pos, 1), "lo": float(lo), "hi": float(hi), "eq": float((hi + lo) / 2)}


def market_context(df, direction: str | None = None):
    """Everything above in one dict; with a direction ('bullish'/'bearish') it also says which parts AGREE with it."""
    d = df.reset_index(drop=True)
    try: tw = time_window(d)
    except Exception: tw = {"kz": None, "silver": False, "ny_hour": None}
    try: db = daily_bias(d)
    except Exception: db = {"bias": None, "accumulation": False, "why": ""}
    try: pd_ = premium_discount(d)
    except Exception: pd_ = {"zone": None}
    try:
        from modules.regime import classify as _regime
        rg = _regime(d)
    except Exception:
        rg = {"regime": None}
    ctx = {"window": tw, "daily": db, "pd": pd_, "regime": rg, "agree": {}}   # regime = market state NOW (shown, never counted in the stars)
    if direction in ("bullish", "bearish"):
        up = direction == "bullish"
        ctx["agree"] = {
            "bias": None if db["bias"] in (None, "neutral", "inside") else db["bias"] == direction,
            "pd": None if pd_["zone"] in (None, "equilibrium") else (pd_["zone"] == "discount") == up,
            "window": bool(tw["kz"] or tw["silver"]) if tw["ny_hour"] is not None else None,
            "stand_aside": bool(db["accumulation"]),
        }
    return ctx
