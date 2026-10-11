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


BARS_PER_YEAR = {"1m": 525600, "5m": 105120, "15m": 35040, "30m": 17520, "1h": 8760, "4h": 2190, "1d": 365, "1w": 52}


def vol_target_weight(df, tf: str, target: float = 0.25, lookback: int = 60) -> dict | None:
    """Volatility-based position size: the share of the capital set aside for this trade so that the position's
    annualised volatility equals `target` (default 25%, this dashboard's choice). Capped at 100% (no leverage)."""
    import numpy as np
    try:
        c = df["close"].astype(float).values
        r = np.diff(np.log(c[-(lookback + 1):]))
        if len(r) < 20:
            return None
        bpy = BARS_PER_YEAR.get(tf)
        if not bpy:
            step = (df["time"].iloc[-1] - df["time"].iloc[-2]).total_seconds()
            bpy = 31_536_000 / step if step > 0 else 8760
        vol = float(np.std(r, ddof=1) * np.sqrt(bpy))
        if vol <= 0 or not np.isfinite(vol):
            return None
        return {"ann_vol": round(vol, 4), "target": target, "weight": round(min(1.0, target / vol), 4)}
    except Exception:
        return None
