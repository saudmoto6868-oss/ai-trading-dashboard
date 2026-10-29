"""SHARED REGIME DEFINITION (pure numpy). One place for how a candle is labelled with a market regime, so every hub tab that slices
results by regime uses the SAME labels and none has to import another tab's code (hub rule). Labels use only information up to
each candle (trailing windows, no look-ahead):
  Crash   5-bar return below -2 sigma of its trailing distribution
  HiVol   ATR(14) above 1.5x its trailing median
  Squeeze Bollinger width in the bottom 20% of its trailing range
  Trend   ADX(14) > 25        Chop  ADX(14) < 20        Mixed  everything else
(first match wins, in that order). '' while warming up (first WARM bars)."""
from __future__ import annotations

import numpy as np

REGIMES = ("Crash", "HiVol", "Squeeze", "Trend", "Chop", "Mixed")
WARM = 220            # bars needed before labels are trusted (longest trailing window + ADX warm-up)


def _wilder(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    out[n - 1] = np.nanmean(x[:n])
    for i in range(n, len(x)):
        out[i] = (out[i - 1] * (n - 1) + x[i]) / n
    return out


def true_range(high, low, close) -> np.ndarray:
    prev = np.concatenate(([close[0]], close[:-1]))
    return np.maximum(high - low, np.maximum(np.abs(high - prev), np.abs(low - prev)))


def adx(high, low, close, n: int = 14) -> np.ndarray:
    up = np.concatenate(([0.0], high[1:] - high[:-1]))
    dn = np.concatenate(([0.0], low[:-1] - low[1:]))
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    atr = _wilder(true_range(high, low, close), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        pdi = 100 * _wilder(pdm, n) / atr
        mdi = 100 * _wilder(mdm, n) / atr
        dx = 100 * np.abs(pdi - mdi) / (pdi + mdi)
    dx = np.nan_to_num(dx, nan=0.0)
    out = _wilder(dx, n)
    out[: 2 * n - 1] = np.nan
    return out


def _trailing(x: np.ndarray, win: int, fn) -> np.ndarray:
    """fn over the PAST win values ending at each bar (bar itself included: it is closed when labelled)."""
    out = np.full(len(x), np.nan)
    for i in range(win - 1, len(x)):
        seg = x[i - win + 1: i + 1]
        seg = seg[~np.isnan(seg)]
        if len(seg):
            out[i] = fn(seg)
    return out


def label(high, low, close) -> list:
    """One regime name per bar ('' while warming up)."""
    high, low, close = (np.asarray(a, dtype=float) for a in (high, low, close))
    n = len(close)
    atr = _wilder(true_range(high, low, close), 14)
    atr_med = _trailing(atr, 100, np.median)
    a = adx(high, low, close)
    r5 = np.full(n, np.nan)
    r5[5:] = close[5:] / close[:-5] - 1.0
    r5_sd = _trailing(r5, 100, lambda s: s.std(ddof=1) if len(s) > 2 else np.nan)
    mid = _trailing(close, 20, np.mean)
    sd = _trailing(close, 20, lambda s: s.std(ddof=0))
    with np.errstate(divide="ignore", invalid="ignore"):
        bbw = 4 * sd / mid
    bbw_p20 = _trailing(bbw, 100, lambda s: np.percentile(s, 20))
    out = [""] * n
    for i in range(WARM, n):
        if np.isnan(a[i]) or np.isnan(atr_med[i]) or np.isnan(r5_sd[i]) or np.isnan(bbw_p20[i]):
            continue
        if r5[i] < -2 * r5_sd[i]:
            out[i] = "Crash"
        elif atr[i] > 1.5 * atr_med[i]:
            out[i] = "HiVol"
        elif bbw[i] <= bbw_p20[i]:
            out[i] = "Squeeze"
        elif a[i] > 25:
            out[i] = "Trend"
        elif a[i] < 20:
            out[i] = "Chop"
        else:
            out[i] = "Mixed"
    return out
