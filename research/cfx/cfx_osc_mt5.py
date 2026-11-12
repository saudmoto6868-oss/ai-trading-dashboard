#!/usr/bin/env python3
"""Faithful MT5 oscillator reconstruction for the CFX pane.

Parameter order follows MT5 iStochastic(Kperiod, Dperiod, slowing) and the
Amirulss screenshot label Stoch(1,9,8) = K=1, D=9, slowing=8.

Signals use each indicator's own rule. No adaptive zones, no pipeline-fill
dots, no extra AND-merge that hides a valid individual signal.
Research only — no edge claimed.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# MT5 (K, D, slowing) — same numbers as the Amirulss pane title
STOCH_SETS = ((1, 9, 8), (1, 6, 3), (1, 5, 7), (1, 8, 8))
STOCH_COLS = ("#c6ff00", "#76ff03", "#f9a825", "#e91e63")  # lime/green/gold/magenta like the shot
AMIR_OS, AMIR_OB = 10.0, 90.0

# ScalpKing RSI(1) MACD: 0–100 line = EMA8(RSI1) so 82/18 can fire.
# rsi1 is 100/0/50 on up/down/flat close. Hollow signal = EMA5 of that line; hist = line−signal.
# (A 50+macd/2 remap of EMA8−EMA17 only spanned ~41–59 on this GC=F 15m window.)
SK_FAST, SK_SLOW, SK_SIG = 8, 17, 5
SK_BUY_LV, SK_SELL_LV = 18.0, 82.0

# RSI(1) Stochastic: stoch of smoothed RSI(1), blue %K / red %D.
# Levels from the owner's notes: Waiting 90 / sell 83 / sell 75 / S.B 50 / buy 25 / buy 18 / Waiting 7.
# Signal the owner specified: crossing back from the waiting levels 7 (BUY) and 90 (SELL).
RSI1_STOCH_K, RSI1_STOCH_D, RSI1_STOCH_SLOW = 8, 3, 5
RSI1_WAIT_LO, RSI1_WAIT_HI = 7.0, 90.0
RSI1_LEVELS = (90, 83, 75, 50, 25, 18, 7)


def _ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def stoch_kd(high, low, close, k_period: int, d_period: int, slowing: int):
    """MT5 Stochastic: %K period, %D period, slowing (both SMA)."""
    ll = low.rolling(k_period, min_periods=k_period).min()
    hh = high.rolling(k_period, min_periods=k_period).max()
    raw = 100.0 * (close - ll) / (hh - ll).replace(0, np.nan)
    k_line = raw.rolling(int(slowing), min_periods=int(slowing)).mean()
    d_line = k_line.rolling(int(d_period), min_periods=int(d_period)).mean()
    return k_line, d_line


def rsi1_raw(close: pd.Series) -> pd.Series:
    chg = close.diff()
    out = pd.Series(np.where(chg > 0, 100.0, np.where(chg < 0, 0.0, 50.0)), index=close.index)
    out.iloc[0] = np.nan
    return out


def add_mt5_oscillators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    h, l, c = out["high"], out["low"], out["close"]
    ks = []
    for i, (k_per, d_per, slowing) in enumerate(STOCH_SETS):
        k_line, d_line = stoch_kd(h, l, c, k_per, d_per, slowing)
        out[f"amir_k{i}"] = k_line
        out[f"amir_d{i}"] = d_line
        ks.append(k_line)
    stacked = pd.concat(ks, axis=1)
    out["amir_med"] = stacked.median(axis=1)
    in_os = pd.concat([(out[f"amir_k{i}"] <= AMIR_OS) for i in range(4)], axis=1)
    in_ob = pd.concat([(out[f"amir_k{i}"] >= AMIR_OB) for i in range(4)], axis=1)
    out["amir_n_os"] = in_os.sum(axis=1)
    out["amir_n_ob"] = in_ob.sum(axis=1)
    # all 4 were in the 10 (90) zone last bar, and all 4 have now left it, median turning
    was_all_os = (out["amir_n_os"].shift(1) == 4)
    was_all_ob = (out["amir_n_ob"].shift(1) == 4)
    now_all_above10 = (out["amir_n_os"] == 0)
    now_all_below90 = (out["amir_n_ob"] == 0)
    rising = out["amir_med"] > out["amir_med"].shift(1)
    falling = out["amir_med"] < out["amir_med"].shift(1)
    out["amir_buy"] = (was_all_os & now_all_above10 & rising).fillna(False)
    out["amir_sell"] = (was_all_ob & now_all_below90 & falling).fillna(False)

    r1 = rsi1_raw(c)
    out["rsi1"] = r1
    # MACD-style of RSI(1): the 0–100 line is EMA_fast(RSI1), the hollow signal is
    # EMA_sig of that line, histogram = line − signal. 82/18 sit on the 0–100 line.
    # (A raw EMA-difference mapped by 50+macd/2 only spanned ~41–59 on GC=F 15m
    # and would hide every 18/82 cross the owner asked for.)
    out["sk_macd_raw"] = _ema(r1, SK_FAST) - _ema(r1, SK_SLOW)
    out["sk_line"] = _ema(r1, SK_FAST).clip(0, 100)
    out["sk_signal"] = _ema(out["sk_line"], SK_SIG)
    out["sk_hist"] = out["sk_line"] - out["sk_signal"]
    prev, now = out["sk_line"].shift(1), out["sk_line"]
    out["sk_buy"] = ((prev <= SK_BUY_LV) & (now > SK_BUY_LV)).fillna(False)
    out["sk_sell"] = ((prev >= SK_SELL_LV) & (now < SK_SELL_LV)).fillna(False)

    r_smooth = _ema(r1, 8)
    out["rsi1_smooth"] = r_smooth
    sk, sd = stoch_kd(r_smooth, r_smooth, r_smooth, RSI1_STOCH_K, RSI1_STOCH_D, RSI1_STOCH_SLOW)
    # stoch of a 1-D series: high=low=close makes raw undefined (span 0). Use range of the series:
    lo = r_smooth.rolling(RSI1_STOCH_K, min_periods=RSI1_STOCH_K).min()
    hi = r_smooth.rolling(RSI1_STOCH_K, min_periods=RSI1_STOCH_K).max()
    raw = 100.0 * (r_smooth - lo) / (hi - lo).replace(0, np.nan)
    out["rs_k"] = raw.rolling(RSI1_STOCH_SLOW, min_periods=RSI1_STOCH_SLOW).mean()
    out["rs_d"] = out["rs_k"].rolling(RSI1_STOCH_D, min_periods=RSI1_STOCH_D).mean()
    pk, nk = out["rs_k"].shift(1), out["rs_k"]
    out["rs_buy"] = ((pk <= RSI1_WAIT_LO) & (nk > RSI1_WAIT_LO)).fillna(False)
    out["rs_sell"] = ((pk >= RSI1_WAIT_HI) & (nk < RSI1_WAIT_HI)).fillna(False)
    return out


def collect_mt5_dots(df: pd.DataFrame, vis_start: int, vis_end: int) -> list[dict]:
    """One row per bar where any of the three indicators fires. No pipeline fill."""
    rows = []
    c = df["close"].to_numpy(float)
    n = len(df)
    for i in range(vis_start, min(vis_end, n - 1) + 1):
        fired_buy, fired_sell = [], []
        if bool(df["amir_buy"].iloc[i]):
            fired_buy.append("Amirulss: all 4 stochs left the 10 zone upward")
        if bool(df["amir_sell"].iloc[i]):
            fired_sell.append("Amirulss: all 4 stochs left the 90 zone downward")
        if bool(df["sk_buy"].iloc[i]):
            fired_buy.append("ScalpKing: RSI(1) MACD crossed up through 18")
        if bool(df["sk_sell"].iloc[i]):
            fired_sell.append("ScalpKing: RSI(1) MACD crossed down through 82")
        if bool(df["rs_buy"].iloc[i]):
            fired_buy.append("RSI(1) Stoch: crossed back up from waiting 7")
        if bool(df["rs_sell"].iloc[i]):
            fired_sell.append("RSI(1) Stoch: crossed back down from waiting 90")
        nxt = c[i + 1: i + 9]
        hi = float(df["high"].iloc[i + 1: i + 9].max()) if i + 1 < n else np.nan
        lo = float(df["low"].iloc[i + 1: i + 9].min()) if i + 1 < n else np.nan
        px = float(c[i])
        after = None
        if np.isfinite(hi) and np.isfinite(lo):
            after = f"next8 high {hi - px:+.1f} / low {lo - px:+.1f}"
        ts = df.index[i]
        for side, fired in (("buy", fired_buy), ("sell", fired_sell)):
            if not fired:
                continue
            rows.append({
                "i": int(i),
                "side": side,
                "time": ts,
                "price": px,
                "fired": fired,
                "amir_med": float(df["amir_med"].iloc[i]) if np.isfinite(df["amir_med"].iloc[i]) else None,
                "sk_line": float(df["sk_line"].iloc[i]) if np.isfinite(df["sk_line"].iloc[i]) else None,
                "rs_k": float(df["rs_k"].iloc[i]) if np.isfinite(df["rs_k"].iloc[i]) else None,
                "after": after,
            })
    return rows


def sanity_report(df: pd.DataFrame, vis_start: int, vis_end: int) -> dict:
    sl = df.iloc[vis_start: vis_end + 1]
    info = {"bars": len(sl)}
    for i in range(4):
        s = sl[f"amir_k{i}"]
        info[f"amir_k{i}_minmax"] = (float(np.nanmin(s)), float(np.nanmax(s)))
    info["amir_n_os_max"] = int(sl["amir_n_os"].max())
    info["amir_n_ob_max"] = int(sl["amir_n_ob"].max())
    info["n_all4_os"] = int((sl["amir_n_os"] == 4).sum())
    info["n_all4_ob"] = int((sl["amir_n_ob"] == 4).sum())
    info["sk_minmax"] = (float(np.nanmin(sl["sk_line"])), float(np.nanmax(sl["sk_line"])))
    info["rs_minmax"] = (float(np.nanmin(sl["rs_k"])), float(np.nanmax(sl["rs_k"])))
    info["n_amir_buy"] = int(sl["amir_buy"].sum())
    info["n_amir_sell"] = int(sl["amir_sell"].sum())
    info["n_sk_buy"] = int(sl["sk_buy"].sum())
    info["n_sk_sell"] = int(sl["sk_sell"].sum())
    info["n_rs_buy"] = int(sl["rs_buy"].sum())
    info["n_rs_sell"] = int(sl["rs_sell"].sum())
    return info
