"""
THE HEAD ANALYST
Combines Department 1 (price action) and Department 2 (liquidity/OHL)
signals into one strength score plus reasons list, and classifies the
signal into a trade type (scalp/day/swing/position) based on which
timeframe it fired on, per the framework doc's multi-timeframe process.
"""

from modules.price_action import price_action_signals
from modules.liquidity_ohl import liquidity_line_breaks, ohl_bias
from config import TRADE_TYPE_BY_TIMEFRAME


def score_symbol(df, timeframe_label: str = "H1") -> dict:
    pa = price_action_signals(df)
    liq = liquidity_line_breaks(df)
    ohl = ohl_bias(df)

    score = 0
    reasons = []

    if pa["near_key_level"]:
        score += 1
        reasons.append(f"Near {pa['level_type']}")
    if pa["ema_bullish_cross"] or pa["ema_bearish_cross"]:
        score += 1
        reasons.append("EMA cross")
    if pa["above_vwap"]:
        score += 1
        reasons.append("Above VWAP")
    if liq["just_broke_level"]:
        score += 1
        reasons.append("Liquidity level break")
    if ohl["above_prior_high"] or ohl["below_prior_low"]:
        score += 1
        reasons.append("OHL breakout")
    if pa["breakout"]["breakout"]:
        score += 1
        reasons.append(f"{pa['breakout']['direction'].capitalize()} breakout")

    trade_type = TRADE_TYPE_BY_TIMEFRAME.get(timeframe_label, "Day Trade")

    return {
        "score": score,
        "max_score": 6,
        "reasons": reasons,
        "trend_bias": pa["trend_bias"],
        "price": pa["price"],
        "trade_type": trade_type,
        "timeframe": timeframe_label,
        "supports": pa["supports"],
        "resistances": pa["resistances"],
        "liquidity_levels": liq["liquidity_levels"],
    }
