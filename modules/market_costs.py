"""Per-market transaction cost model in R-multiples (fees, funding, spread)."""
from __future__ import annotations

from typing import Dict, Iterable, Optional

FALLBACK_COST_R = 0.10

MARKET_COSTS: Dict[str, Dict[str, float]] = {
    "BTC": {"15m": 0.08, "1h": 0.06, "4h": 0.05},
    "ETH": {"15m": 0.09, "1h": 0.07, "4h": 0.05},
    "SOL": {"15m": 0.11, "1h": 0.08, "4h": 0.06},
    "HL:GOLD": {"15m": 0.30, "1h": 0.20, "4h": 0.15},
    "HL:EURUSD": {"15m": 0.12, "1h": 0.09, "4h": 0.07},
    "HL:SP500": {"15m": 0.14, "1h": 0.10, "4h": 0.08},
    "HL:OIL": {"15m": 0.22, "1h": 0.16, "4h": 0.12},
}


def _normalize_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    aliases = {
        "BTCUSDT": "BTC",
        "BTC-USDT": "BTC",
        "ETHUSDT": "ETH",
        "ETH-USDT": "ETH",
        "SOLUSDT": "SOL",
        "SOL-USDT": "SOL",
        "XAUUSD": "HL:GOLD",
        "GOLD": "HL:GOLD",
        "EURUSD": "HL:EURUSD",
        "SP500": "HL:SP500",
    }
    return aliases.get(s, s)


def get_cost(symbol: str, tf: str, fallback: float = FALLBACK_COST_R) -> float:
    """Return estimated round-trip transaction cost in R for (symbol, tf)."""
    norm = _normalize_symbol(symbol)
    tf_key = tf.strip().lower()
    return MARKET_COSTS.get(norm, {}).get(tf_key, fallback)


def estimate_okx_fee_r(
    stop_pct: float,
    taker_fee: float = 0.0005,
    maker_fee: float = 0.0002,
    use_taker: bool = True,
) -> float:
    """Estimate round-trip OKX fee as a fraction of 1R stop distance."""
    if stop_pct <= 0:
        return FALLBACK_COST_R
    one_way = taker_fee if use_taker else maker_fee
    return round((2.0 * one_way) / stop_pct, 4)


def estimate_hl_funding_r(
    stop_pct: float,
    hourly_funding_rate: float = 0.0000125,
    avg_hold_hours: float = 8.0,
) -> float:
    """Estimate Hyperliquid funding cost in R over average holding duration."""
    if stop_pct <= 0:
        return 0.0
    return round((abs(hourly_funding_rate) * avg_hold_hours) / stop_pct, 4)


def estimate_spread_r_from_candles(
    candles: Iterable[dict],
    stop_points: float,
    spread_fraction_of_range: float = 0.05,
) -> float:
    """Estimate spread cost in R from minimum candle high-low range."""
    ranges = [float(c["high"]) - float(c["low"]) for c in candles if "high" in c and "low" in c]
    if not ranges or stop_points <= 0:
        return FALLBACK_COST_R
    min_range = min(r for r in ranges if r > 0) if any(r > 0 for r in ranges) else 0.0
    est_spread = min_range * spread_fraction_of_range
    return round(est_spread / stop_points, 4)


def build_cost_comparison(
    symbol: str,
    tf: str,
    actual_cost_r: Optional[float] = None,
) -> Dict[str, float]:
    """Return report columns comparing cost_actual vs cost_estimate."""
    est = get_cost(symbol, tf)
    act = est if actual_cost_r is None else float(actual_cost_r)
    return {
        "cost_estimate": round(est, 4),
        "cost_actual": round(act, 4),
    }
