"""
THE RISK MANAGER
Turns a scored signal into a full trade plan: entry, stop loss, and 3
staged take-profits, using the nearest liquidity/support-resistance levels
and the RR rules from the framework doc (default 0.5% risk, partial-profit-
then-runner approach via staged RR multiples).
"""

from config import RR_TARGETS


def build_trade_plan(score_result: dict) -> dict:
    price = score_result["price"]
    bias = score_result["trend_bias"]
    supports = score_result.get("supports", [])
    resistances = score_result.get("resistances", [])

    if bias == "bullish":
        candidates = [s for s in supports if s < price]
        stop_ref = max(candidates) if candidates else price * 0.995
        risk_distance = price - stop_ref
        entry = price
        stop_loss = stop_ref
        take_profits = [entry + risk_distance * rr for rr in RR_TARGETS]
    else:
        candidates = [r for r in resistances if r > price]
        stop_ref = min(candidates) if candidates else price * 1.005
        risk_distance = stop_ref - price
        entry = price
        stop_loss = stop_ref
        take_profits = [entry - risk_distance * rr for rr in RR_TARGETS]

    return {
        "entry": round(entry, 5),
        "stop_loss": round(stop_loss, 5),
        "take_profits": [round(tp, 5) for tp in take_profits],
        "risk_distance": round(risk_distance, 5),
        "direction": "Long" if bias == "bullish" else "Short",
    }
