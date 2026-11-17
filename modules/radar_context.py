"""Chart context for the Radar explanations (owner 2026-11-16): the numbers of THIS chart, so the text changes with
price, swings, trend, RSI and direction instead of repeating one template. Pure pandas, read only."""
from __future__ import annotations

import pandas as pd


def _pivots(df: pd.DataFrame, n: int = 3, lookback: int = 90):
    """Confirmed swing highs / lows (n bars each side) in the last `lookback` candles: lists of (index, price)."""
    tail = df.tail(lookback).reset_index(drop=True)
    hi, lo = [], []
    for i in range(n, len(tail) - n):
        h = tail["high"].iloc[i]
        l_ = tail["low"].iloc[i]
        if h == tail["high"].iloc[i - n:i + n + 1].max():
            hi.append((i, float(h)))
        if l_ == tail["low"].iloc[i - n:i + n + 1].min():
            lo.append((i, float(l_)))
    return hi, lo, len(tail)


def context(df: pd.DataFrame) -> dict:
    """Numbers for one chart: price, ATR, last swing high / low, nearest levels, EMA trend, bars since the last swing."""
    if df is None or len(df) < 60:
        return {}
    close = float(df["close"].iloc[-1])
    prev = df["close"].iloc[-2] if len(df) > 1 else close
    tr = pd.concat([df["high"] - df["low"], (df["high"] - df["close"].shift()).abs(), (df["low"] - df["close"].shift()).abs()], axis=1).max(axis=1)
    atr = float(tr.tail(14).mean())
    ema20 = float(df["close"].ewm(span=20, adjust=False).mean().iloc[-1])
    ema50 = float(df["close"].ewm(span=50, adjust=False).mean().iloc[-1])
    hi, lo, n = _pivots(df)
    last_hi = hi[-1] if hi else None
    last_lo = lo[-1] if lo else None
    above = [p for _i, p in hi if p > close]
    below = [p for _i, p in lo if p < close]
    res = min(above) if above else None           # nearest swing high above price
    sup = max(below) if below else None           # nearest swing low below price
    return {
        "close": close,
        "change_1": (close / float(prev) - 1) * 100 if prev else 0.0,
        "atr": atr,
        "atr_pct": atr / close * 100 if close else 0.0,
        "ema20": ema20, "ema50": ema50,
        "trend": "up" if ema20 > ema50 and close > ema20 else "down" if ema20 < ema50 and close < ema20 else "mixed",
        "swing_high": last_hi[1] if last_hi else None,
        "swing_high_age": (n - 1 - last_hi[0]) if last_hi else None,
        "swing_low": last_lo[1] if last_lo else None,
        "swing_low_age": (n - 1 - last_lo[0]) if last_lo else None,
        "resistance": res,
        "support": sup,
    }


def pct(a: float, b: float) -> float:
    """Distance from b to a in percent of b."""
    return (a / b - 1) * 100 if b else 0.0
