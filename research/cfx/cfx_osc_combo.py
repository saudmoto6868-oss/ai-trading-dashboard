#!/usr/bin/env python3
"""One working oscillator from the owner's MT5 settings screenshots (v7).

Settings read from the five MT5 dialogs (paths named in the v7 brief;
JPEGs were not on disk at write time, so values follow the extracted dialogs):

  SMA 144, method Simple, apply to Close, red dashed   — price pane
  SMA  77, method Simple, apply to Close, orange dashed — price pane
  MACD fast EMA 12, slow EMA 26, signal SMA 1, apply to Close
      main style grey dash-dot, signal yellow
  RSI period 14, apply to Close, levels 10 / 90 / 50
  Stochastic %K 5, %D 3, slowing 3, price field Low/High, method Simple,
      levels 15 / 85 / 50

MT5 iStochastic(Kperiod, Dperiod, slowing) + Low/High = HH/LL of high/low.
MACD signal period 1 ⇒ SMA(1) of the MACD line equals the line itself, so the
histogram is ~0; confirmation therefore uses the MACD *main* slope
(macd[i] > macd[i-1]), as the brief allowed ("histogram/main rising").

Research only — no edge claimed.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from cfx_osc_mt5 import stoch_kd


STOCH_K, STOCH_D, STOCH_SLOW = 5, 3, 3
STOCH_OS, STOCH_OB, STOCH_MID = 15.0, 85.0, 50.0
RSI_LEN = 14
RSI_OS, RSI_OB, RSI_MID = 10.0, 90.0, 50.0
MACD_FAST, MACD_SLOW, MACD_SIG = 12, 26, 1
SMA_FAST, SMA_SLOW = 77, 144


def _ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def _sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(int(n), min_periods=int(n)).mean()


def rsi_wilder(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_g = gain.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    avg_l = loss.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    rs = avg_g / avg_l.replace(0, np.nan)
    out = 100.0 - (100.0 / (1.0 + rs))
    out = out.where(avg_l != 0, 100.0)
    out = out.where(avg_g != 0, 0.0)
    return out


def add_combo_oscillators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    h, l, c = out["high"], out["low"], out["close"]
    k, d = stoch_kd(h, l, c, STOCH_K, STOCH_D, STOCH_SLOW)
    out["st_k"] = k
    out["st_d"] = d
    out["rsi14"] = rsi_wilder(c, RSI_LEN)
    macd = _ema(c, MACD_FAST) - _ema(c, MACD_SLOW)
    out["macd"] = macd
    out["macd_sig"] = _sma(macd, MACD_SIG)  # period 1 == macd
    out["macd_hist"] = out["macd"] - out["macd_sig"]
    out["sma77"] = _sma(c, SMA_FAST)
    out["sma144"] = _sma(c, SMA_SLOW)
    return out


def _cross_up(k, d, i):
    return k[i - 1] <= d[i - 1] and k[i] > d[i]


def _cross_dn(k, d, i):
    return k[i - 1] >= d[i - 1] and k[i] < d[i]


def _from_os(k, i, look=0):
    a = max(0, i - look)
    return any(np.isfinite(k[j]) and k[j] <= STOCH_OS for j in range(a, i + 1))


def _from_ob(k, i, look=0):
    a = max(0, i - look)
    return any(np.isfinite(k[j]) and k[j] >= STOCH_OB for j in range(a, i + 1))


def collect_combo_dots(df: pd.DataFrame, vis_start: int, vis_end: int, variant: str = "A") -> list[dict]:
    """variant A = Stoch K/D cross from 15/85 + RSI turning + MACD main rising.
    B = same with a 3-bar zone memory (K touched 15/85 in the last 3 bars).
    C = A plus SMA144 trend context (buy only above SMA144, sell only below).
    """
    k = df["st_k"].to_numpy(float)
    d = df["st_d"].to_numpy(float)
    rsi = df["rsi14"].to_numpy(float)
    macd = df["macd"].to_numpy(float)
    sma144 = df["sma144"].to_numpy(float)
    close = df["close"].to_numpy(float)
    high = df["high"].to_numpy(float)
    low = df["low"].to_numpy(float)
    n = len(df)
    look = 3 if variant == "B" else 0
    rows = []
    start = max(int(vis_start), 2)
    end = min(int(vis_end), n - 1)
    for i in range(start, end + 1):
        if not all(np.isfinite(x) for x in (k[i], k[i - 1], d[i], d[i - 1], rsi[i], rsi[i - 1], macd[i], macd[i - 1])):
            continue
        rsi_up = rsi[i] > rsi[i - 1]
        rsi_dn = rsi[i] < rsi[i - 1]
        macd_up = macd[i] > macd[i - 1]
        macd_dn = macd[i] < macd[i - 1]
        buy = _cross_up(k, d, i) and _from_os(k, i, look) and rsi_up and macd_up
        sell = _cross_dn(k, d, i) and _from_ob(k, i, look) and rsi_dn and macd_dn
        if variant == "C":
            if np.isfinite(sma144[i]):
                buy = buy and close[i] > sma144[i]
                sell = sell and close[i] < sma144[i]
            else:
                buy = sell = False
        if not buy and not sell:
            continue
        hi = float(np.nanmax(high[i + 1:i + 9])) if i + 1 < n else np.nan
        lo = float(np.nanmin(low[i + 1:i + 9])) if i + 1 < n else np.nan
        px = float(close[i])
        after = None
        side = "buy" if buy else "sell"
        if np.isfinite(hi) and np.isfinite(lo):
            after = f"next8 high {hi - px:+.1f} / low {lo - px:+.1f}"
            if side == "buy":
                mfe, mae = hi - px, px - lo
            else:
                mfe, mae = px - lo, hi - px
        else:
            mfe = mae = np.nan
        fired = []
        if side == "buy":
            fired.append(f"Stoch(5,3,3) %K crossed above %D from ≤15"
                         + (" (3-bar memory)" if variant == "B" else ""))
            fired.append("RSI(14) turning up")
            fired.append("MACD(12,26,1) main rising")
            if variant == "C":
                fired.append("close above SMA144")
        else:
            fired.append(f"Stoch(5,3,3) %K crossed below %D from ≥85"
                         + (" (3-bar memory)" if variant == "B" else ""))
            fired.append("RSI(14) turning down")
            fired.append("MACD(12,26,1) main falling")
            if variant == "C":
                fired.append("close below SMA144")
        rows.append({
            "i": int(i), "side": side, "time": df.index[i], "price": px,
            "fired": fired, "st_k": float(k[i]), "st_d": float(d[i]),
            "rsi14": float(rsi[i]), "macd": float(macd[i]),
            "after": after, "mfe": None if not np.isfinite(mfe) else float(mfe),
            "mae": None if not np.isfinite(mae) else float(mae),
            "variant": variant,
        })
    return rows


def score_dots(dots: list[dict]) -> dict:
    n = len(dots)
    n_buy = sum(1 for d in dots if d["side"] == "buy")
    n_sell = n - n_buy
    decided = [d for d in dots if d.get("mfe") is not None and d.get("mae") is not None]
    n_with = sum(1 for d in decided if d["mfe"] > d["mae"])
    n_against = sum(1 for d in decided if d["mae"] > d["mfe"])
    n_flat = len(decided) - n_with - n_against
    rate = (n_against / len(decided)) if decided else None
    return {
        "n": n, "n_buy": n_buy, "n_sell": n_sell,
        "n_with": n_with, "n_against": n_against, "n_flat": n_flat,
        "against_rate": rate, "n_decided": len(decided),
    }


def compare_variants(df: pd.DataFrame, windows: dict) -> dict:
    """windows: name -> (start_i, end_i). Returns per-variant scores per window."""
    out = {}
    for var in ("A", "B", "C"):
        out[var] = {}
        for wname, (a, b) in windows.items():
            dots = collect_combo_dots(df, a, b, variant=var)
            out[var][wname] = {"score": score_dots(dots), "n_dots": len(dots)}
    return out


def pick_variant(cmp: dict, long_key: str = "long") -> str:
    """Fewest against-move signals on the longer window, with enough samples.
    Ties go to the simpler rule (A, then B, then C). Not an edge claim.
    """
    ranked = []
    for var in ("A", "B", "C"):
        sc = cmp[var][long_key]["score"]
        n = sc["n_decided"]
        rate = sc["against_rate"] if sc["against_rate"] is not None else 1.0
        ranked.append((rate, -n, var, sc))
    ranked.sort()
    # prefer a variant with at least 8 decided signals if any qualifies
    enough = [r for r in ranked if r[3]["n_decided"] >= 8]
    pool = enough if enough else ranked
    return pool[0][2]
