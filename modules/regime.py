"""Market regime of the latest candle, from the candles only (no invented data). One label per symbol / timeframe, shown and filterable in the Radar.

Definitions (first match wins, so the rarer / stronger states come first; thresholds are the ones agreed in the room 2026-10-30, change them there):
  Crash    the last 5-candle return is below -2 standard deviations of the 5-candle returns of the last 100 candles
  Hi-Vol   ATR(14) is above 1.5 x the median ATR(14) of the last 100 candles
  Squeeze  Bollinger(20, 2) width is in the lowest 20 % of the last 100 candles
  Thin     the last candle's volume is in the lowest 20 % of the last 100 candles (skipped when the feed has no volume)
  Trend    ADX(14) above 25
  Chop     ADX(14) below 20 and ATR(14) below its median
  Mixed    anything else (ADX between 20 and 25)
A description of the market NOW, not a signal and not a forecast; what each regime did for each detector is a separate question for the weekly lab.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

REGIMES = ["Trend", "Chop", "Hi-Vol", "Crash", "Squeeze", "Thin", "Mixed"]
LOOK = 100


def _wilder(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) <= n:
        return out
    out[n] = np.nanmean(x[1:n + 1])
    for i in range(n + 1, len(x)):
        out[i] = (out[i - 1] * (n - 1) + x[i]) / n
    return out


def _atr_adx(df: pd.DataFrame, n: int = 14):
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    pc = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)])
    up, dn = np.concatenate([[0], np.diff(h)]), np.concatenate([[0], -np.diff(l)])
    pdm, mdm = np.where((up > dn) & (up > 0), up, 0.0), np.where((dn > up) & (dn > 0), dn, 0.0)
    atr = _wilder(tr, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        pdi, mdi = 100 * _wilder(pdm, n) / atr, 100 * _wilder(mdm, n) / atr
        dx = 100 * np.abs(pdi - mdi) / (pdi + mdi)
    dx = np.where(np.isfinite(dx), dx, np.nan)
    first = np.where(~np.isnan(dx))[0]
    adx = np.full(len(dx), np.nan)
    if len(first) and first[0] + n < len(dx):
        s = first[0]
        adx[s + n - 1] = np.nanmean(dx[s:s + n])
        for i in range(s + n, len(dx)):
            adx[i] = (adx[i - 1] * (n - 1) + dx[i]) / n
    return atr, adx


def classify(df: pd.DataFrame) -> dict:
    """-> {'regime': label or None, 'adx', 'atr_ratio', 'bb_pct', 'vol_pct', 'ret_z'} (None when there are fewer than 60 candles)."""
    if df is None or len(df) < 60:
        return {"regime": None}
    d = df.reset_index(drop=True)
    c = d["close"].to_numpy(float)
    atr, adx = _atr_adx(d)
    a, x = atr[-LOOK:], adx[-1]
    a = a[~np.isnan(a)]
    atr_ratio = float(atr[-1] / np.median(a)) if len(a) and np.median(a) > 0 else None
    s = pd.Series(c)
    mid, sd = s.rolling(20).mean(), s.rolling(20).std(ddof=0)
    bbw = ((4 * sd) / mid).to_numpy(float)
    w = bbw[-LOOK:][~np.isnan(bbw[-LOOK:])]
    bb_pct = float((w < bbw[-1]).mean() * 100) if len(w) > 10 and not np.isnan(bbw[-1]) else None
    r5 = (s / s.shift(5) - 1).to_numpy(float)
    z = r5[-LOOK:][~np.isnan(r5[-LOOK:])]
    ret_z = float((r5[-1] - z.mean()) / z.std()) if len(z) > 10 and z.std() > 0 and not np.isnan(r5[-1]) else None
    vol_pct = None
    if "volume" in d.columns:
        v = d["volume"].to_numpy(float)[-LOOK:]
        if np.nansum(v) > 0 and np.count_nonzero(v) > len(v) * 0.5:
            vol_pct = float(((v < v[-1]).mean() + (v <= v[-1]).mean()) / 2 * 100)   # mid-rank: equal volumes do not read as the lowest
    if ret_z is not None and ret_z < -2:
        reg = "Crash"
    elif atr_ratio is not None and atr_ratio > 1.5:
        reg = "Hi-Vol"
    elif bb_pct is not None and bb_pct < 20:
        reg = "Squeeze"
    elif vol_pct is not None and vol_pct < 20:
        reg = "Thin"
    elif x == x and x > 25:
        reg = "Trend"
    elif x == x and x < 20 and atr_ratio is not None and atr_ratio < 1:
        reg = "Chop"
    else:
        reg = "Mixed"
    return {"regime": reg, "adx": None if x != x else round(float(x), 1), "atr_ratio": None if atr_ratio is None else round(atr_ratio, 2),
            "bb_pct": None if bb_pct is None else round(bb_pct), "vol_pct": None if vol_pct is None else round(vol_pct), "ret_z": None if ret_z is None else round(ret_z, 2)}
