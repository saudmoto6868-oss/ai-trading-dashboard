"""
THE CHART ANALYST
Department 1 signals: support/resistance clustering, VWAP, EMA trend bias,
and simple breakout detection. Pure price-action logic - own calculations,
not copying any paid indicator.
"""

import pandas as pd
import numpy as np


def find_support_resistance(df: pd.DataFrame, lookback: int = 50, tolerance: float = 0.0015):
    recent = df.tail(lookback).reset_index(drop=True)
    highs, lows = [], []

    for i in range(2, len(recent) - 2):
        window_h = recent["high"].iloc[i - 2:i + 3]
        window_l = recent["low"].iloc[i - 2:i + 3]
        if recent["high"].iloc[i] == window_h.max():
            highs.append(recent["high"].iloc[i])
        if recent["low"].iloc[i] == window_l.min():
            lows.append(recent["low"].iloc[i])

    def cluster(levels):
        levels = sorted(levels)
        clusters = []
        for lvl in levels:
            if clusters and abs(lvl - clusters[-1][-1]) / lvl < tolerance:
                clusters[-1].append(lvl)
            else:
                clusters.append([lvl])
        return [float(np.mean(c)) for c in clusters]

    return cluster(highs), cluster(lows)


def calc_vwap(df: pd.DataFrame):
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    cum_vol = df["volume"].cumsum().replace(0, np.nan)
    cum_vol_price = (typical_price * df["volume"]).cumsum()
    return cum_vol_price / cum_vol


def calc_ema(df: pd.DataFrame, period: int = 21):
    return df["close"].ewm(span=period, adjust=False).mean()


def detect_breakout(df: pd.DataFrame, lookback: int = 20):
    if len(df) < lookback + 2:
        return {"breakout": False, "direction": None}

    prior_window = df.iloc[-(lookback + 1):-1]
    recent_high = prior_window["high"].max()
    recent_low = prior_window["low"].min()
    price = df["close"].iloc[-1]

    if price > recent_high:
        return {"breakout": True, "direction": "bullish", "level": float(recent_high)}
    if price < recent_low:
        return {"breakout": True, "direction": "bearish", "level": float(recent_low)}
    return {"breakout": False, "direction": None}


def price_action_signals(df: pd.DataFrame) -> dict:
    signals = {}
    price = df["close"].iloc[-1]

    resistances, supports = find_support_resistance(df)
    near_resistance = any(abs(price - r) / price < 0.002 for r in resistances)
    near_support = any(abs(price - s) / price < 0.002 for s in supports)
    signals["near_key_level"] = near_resistance or near_support
    signals["level_type"] = "resistance" if near_resistance else ("support" if near_support else None)
    signals["resistances"] = resistances
    signals["supports"] = supports

    vwap = calc_vwap(df)
    signals["vwap"] = float(vwap.iloc[-1]) if pd.notna(vwap.iloc[-1]) else None
    signals["above_vwap"] = (signals["vwap"] is not None) and (price > signals["vwap"])

    ema9 = calc_ema(df, 9)
    ema21 = calc_ema(df, 21)
    signals["ema9"] = float(ema9.iloc[-1])
    signals["ema21"] = float(ema21.iloc[-1])
    signals["ema_bullish_cross"] = ema9.iloc[-1] > ema21.iloc[-1] and ema9.iloc[-2] <= ema21.iloc[-2]
    signals["ema_bearish_cross"] = ema9.iloc[-1] < ema21.iloc[-1] and ema9.iloc[-2] >= ema21.iloc[-2]
    signals["trend_bias"] = "bullish" if ema9.iloc[-1] > ema21.iloc[-1] else "bearish"

    signals["breakout"] = detect_breakout(df)
    signals["price"] = float(price)

    return signals
