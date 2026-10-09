"""
THE LIQUIDITY READER
Department 2 signals: own liquidity-line approximation (stop-cluster zones
from above-average-volume swing points) plus OHL bias. Independent logic -
not a copy of any paid indicator's code.
"""

import pandas as pd


def liquidity_line_breaks(df: pd.DataFrame, lookback: int = 50):
    recent = df.tail(lookback)
    avg_vol = recent["volume"].mean()
    high_vol_bars = recent[recent["volume"] > avg_vol * 1.5]

    liquidity_levels = sorted(set(
        list(high_vol_bars["high"]) + list(high_vol_bars["low"])
    ))

    price = df["close"].iloc[-1]
    prev_price = df["close"].iloc[-2]
    broke_level = any(
        (prev_price < lvl <= price) or (prev_price > lvl >= price)
        for lvl in liquidity_levels
    )
    return {"liquidity_levels": liquidity_levels, "just_broke_level": broke_level}


def ohl_bias(df: pd.DataFrame):
    prev = df.iloc[-2]
    price = df["close"].iloc[-1]
    return {
        "above_prior_high": price > prev["high"],
        "below_prior_low": price < prev["low"],
        "above_prior_open": price > prev["open"],
    }
