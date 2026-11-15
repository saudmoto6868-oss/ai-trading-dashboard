"""RSI Heatmap setup reader: what is each symbol doing NOW on one timeframe.

Combines what the platform already computes from closed candles, no new maths invented:
  - RSI phase + speed (CoinGlass-style speed dots): leaving overbought / oversold, crossing 60 / 40, extended
  - market regime (modules/regime.py): Trend, Squeeze (stand-by before expansion), Hi-Vol / Crash (fast move) ...
A description to guide attention, not a trade instruction. Order flow lives in the browser (Workspace WebSocket)
and is NOT read here.
"""
from __future__ import annotations

from modules.rsi_heatmap import rsi_wilder

SPEED_LOOKBACK = 3   # candles used for the RSI speed (CoinGlass dots)

# phase id -> (label, group used by the "Show" filter)
PHASES = {
    "rev_down": ("↘ Leaving overbought", "Reversal"),
    "rev_up": ("↗ Leaving oversold", "Reversal"),
    "ext_up": ("⚡ Overbought, still rising", "Extended"),
    "ext_dn": ("⚡ Oversold, still falling", "Extended"),
    "stall_ob": ("Overbought, stalling", "Extended"),
    "stall_os": ("Oversold, stalling", "Extended"),
    "mom_up": ("🚀 Momentum up (crossed 60)", "Momentum"),
    "mom_dn": ("🔻 Momentum down (crossed 40)", "Momentum"),
    "squeeze": ("⏳ Stand-by: squeeze", "Stand-by"),
    "drift": ("· Neutral drift", "Neutral"),
}


def rsi_path(closes, period: int = 14, back: int = SPEED_LOOKBACK):
    """RSI now and `back` candles ago (same Wilder maths as the map)."""
    values = [float(x) for x in closes]
    now = rsi_wilder(values, period)
    before = rsi_wilder(values[:-back], period) if len(values) > back else None
    return now, before


def rsi_trail(closes, n: int = 6, period: int = 14):
    """RSI of the last n closed candles, oldest first (the comet tail on the map)."""
    values = [float(x) for x in closes]
    out = [rsi_wilder(values[:len(values) - k] if k else values, period) for k in range(n - 1, -1, -1)]
    return [x for x in out if x is not None]


def speed_dots(now, before) -> str:
    """CoinGlass-style speed marker: ●● very fast, ● fast, '' calm (RSI points moved in SPEED_LOOKBACK candles)."""
    if now is None or before is None:
        return ""
    move = abs(now - before)
    return "●●" if move >= 15 else "●" if move >= 8 else ""


def rsi_phase(now, before, regime=None) -> str:
    """First match wins: reversals, then extended, then momentum crosses, then squeeze stand-by."""
    if now is None:
        return "drift"
    b = now if before is None else before
    if b >= 70 > now:
        return "rev_down"
    if b <= 30 < now:
        return "rev_up"
    if now >= 70:
        return "ext_up" if now > b else "stall_ob"
    if now <= 30:
        return "ext_dn" if now < b else "stall_os"
    if b < 60 <= now:
        return "mom_up"
    if b > 40 >= now:
        return "mom_dn"
    if regime == "Squeeze":
        return "squeeze"
    return "drift"


def read_setup(df) -> dict | None:
    """df = closed candles of one symbol on the map timeframe. Strategy schools are read in modules/rsi_confluence.py."""
    if df is None or len(df) < 20 or "close" not in df:
        return None
    now, before = rsi_path(df["close"].tolist())
    regime = None
    try:
        from modules.regime import classify
        regime = classify(df.reset_index(drop=True)).get("regime")
    except Exception:
        regime = None
    phase = rsi_phase(now, before, regime)
    out = {"phase": phase, "state": PHASES[phase][0], "group": PHASES[phase][1],
           "speed": speed_dots(now, before), "rsi_move": None if now is None or before is None else round(now - before, 2),
           "regime": regime or "—"}
    if regime in ("Hi-Vol", "Crash") and not out["speed"]:
        out["speed"] = "●"   # volatility expansion counts as a fast move even when RSI is pinned
    return out
