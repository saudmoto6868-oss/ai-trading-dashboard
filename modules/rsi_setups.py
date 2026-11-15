"""RSI Heatmap setup reader: what is each symbol doing NOW on one timeframe.

Combines what the platform already computes from closed candles, no new maths invented:
  - RSI phase + speed (CoinGlass-style speed dots): leaving overbought / oversold, crossing 60 / 40, extended
  - market regime (modules/regime.py): Trend, Squeeze (stand-by before expansion), Hi-Vol / Crash (fast move) ...
  - Radar strategies (modules/scorer.py cached_detect + aggregate): stars, direction, strategy icons
  - chart patterns (modules/patterns.py)
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
GROUPS = ("Reversal", "Momentum", "Stand-by", "Extended", "Radar signal", "Flow confirms", "Neutral")


def rsi_path(closes, period: int = 14, back: int = SPEED_LOOKBACK):
    """RSI now and `back` candles ago (same Wilder maths as the map)."""
    values = [float(x) for x in closes]
    now = rsi_wilder(values, period)
    before = rsi_wilder(values[:-back], period) if len(values) > back else None
    return now, before


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


def _radar(df):
    try:
        from modules.scorer import aggregate, cached_detect, MAX_STARS
        sigs, _ = cached_detect(df)
        agg = aggregate(sigs)
    except Exception:
        return None
    direction = agg.get("direction", "neutral")
    if direction == "neutral":
        return {"stars": 0, "max": MAX_STARS, "direction": "neutral", "icons": ""}
    mine = [s for s in sigs if s.get("direction") == direction]
    return {"stars": int(agg.get("stars") or 0), "max": MAX_STARS, "direction": direction,
            "icons": "".join(dict.fromkeys(s.get("icon", "") for s in mine))}


def _patterns(df):
    try:
        from modules.patterns import PATTERNS, find
        return [PATTERNS[k][0] for k in find(df) if k in PATTERNS]
    except Exception:
        return []


def read_setup(df, deep: bool = True) -> dict | None:
    """df = closed candles of one symbol on the map timeframe. deep=False skips Radar + patterns (fast)."""
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
           "regime": regime or "—", "radar": None, "patterns": []}
    if regime in ("Hi-Vol", "Crash") and not out["speed"]:
        out["speed"] = "●"   # volatility expansion counts as a fast move even when RSI is pinned
    if deep and len(df) >= 60:
        out["radar"] = _radar(df)
        out["patterns"] = _patterns(df)
    return out


def setup_rank(s: dict | None) -> float:
    """Sort key, higher = look first: Radar stars, then fresh reversals / momentum / stand-by, then speed."""
    if not s:
        return -1.0
    stars = (s.get("radar") or {}).get("stars", 0)
    bonus = {"Reversal": 3, "Momentum": 2.5, "Stand-by": 2, "Extended": 1}.get(s["group"], 0)
    return stars * 2 + bonus + len(s.get("speed", "")) * 0.5 + (0.5 if s.get("patterns") else 0)


def groups_of(s: dict | None) -> set:
    if not s:
        return set()
    g = {s["group"]}
    if (s.get("radar") or {}).get("stars", 0) > 0:
        g.add("Radar signal")
    return g
