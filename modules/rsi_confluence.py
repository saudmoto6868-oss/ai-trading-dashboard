"""Confluence board for the RSI Heatmap: every school the platform already has votes long / short per symbol.

Nine schools (signal keys from modules/signals.py, grouped once here):
  Structure (SMC/ICT: MSB + order block, CISD, Model 2022, breaker, unicorn, zombie, Judas, Po3, CRT)
  Liquidity (sweeps, liquidity line, OHL, key level, SMT, session AMD, kill zone, ORB)
  Imbalance (fair value gap, OTE)          Elliott (wave 3 / 5 / ABC / C)
  Fib + Harmonic (fib retracement, modules/harmonic.py)   Trend (MA cross / stack, SMA 10/40, Donchian, Turtle, VWAP, trendline, breakout)
  Momentum (RSI phase, RSI / MACD divergence)              Price action (pin / engulf / star / inside, rectangle, double, Wyckoff, chart patterns)
  Order flow (prints, book, funding - modules/rsi_flow.py; only where a prints feed exists)
Numbers are counts of schools, not probabilities. Footprint lives in the Workspace browser feed and is not read here.
"""
from __future__ import annotations

SCHOOLS = ("Structure", "Liquidity", "Imbalance", "Elliott", "Fib/Harmonic", "Trend", "Momentum", "Price action", "Order flow")
SHORT = {"Structure": "SMC", "Liquidity": "LIQ", "Imbalance": "FVG", "Elliott": "EW", "Fib/Harmonic": "FIB",
         "Trend": "TR", "Momentum": "MOM", "Price action": "PA", "Order flow": "OF"}

_KEY_SCHOOL = {}
for _school, _keys in {
    "Structure": ("msb_ob", "cisd", "m2022", "breaker", "ob", "unicorn", "zombie", "judas", "po3", "crt"),
    "Liquidity": ("sweep", "liqline", "ohl_open", "ohl_break", "level", "smt", "sess_amd", "kzs", "orb"),
    "Imbalance": ("fvg", "ote"),
    "Elliott": ("ew3", "ew5", "abc", "wavec"),
    "Fib/Harmonic": ("fib",),
    "Trend": ("ma_cross", "ema_stack", "sma1040", "donch", "turtle55", "vwap", "tlbreak", "breakout"),
    "Momentum": ("rsi_div", "macd_div"),
    "Price action": ("pa_engulf", "pa_pin", "pa_inside", "pa_star", "rect", "dbl", "wyck"),
}.items():
    for _k in _keys:
        _KEY_SCHOOL[_k] = _school
_FAMILY_SCHOOL = {"Elliott": "Elliott", "Fib": "Fib/Harmonic", "MA": "Trend", "VWAP": "Trend", "TL": "Trend",
                  "Liquidity": "Liquidity", "MSB-OB": "Structure", "Unicorn": "Structure", "PA": "Price action"}
BULL_PHASES = {"rev_up", "mom_up", "ext_up"}
BEAR_PHASES = {"rev_down", "mom_dn", "ext_dn"}


def school_of(sig: dict) -> str:
    return _KEY_SCHOOL.get(sig.get("key")) or _FAMILY_SCHOOL.get(sig.get("family"), "Price action")


def _side(direction) -> int:
    d = str(direction).lower()
    return 1 if d in ("bullish", "bull", "buy", "1") else -1 if d in ("bearish", "bear", "sell", "-1") else 0


def school_votes(signals, harmonics=(), patterns=(), phase=None, flow_vote=0):
    """-> {school: {'bull': n, 'bear': n, 'vote': -1/0/1, 'names': [...]}} for all nine schools."""
    out = {s: {"bull": 0, "bear": 0, "vote": 0, "names": [], "ago": None} for s in SCHOOLS}

    def add(school, side, name, ago=None):
        if not side:
            return
        cell = out[school]
        cell["bull" if side > 0 else "bear"] += 1
        if name and name not in cell["names"]:
            cell["names"].append(name)
        if ago is not None and (cell["ago"] is None or ago < cell["ago"]):
            cell["ago"] = int(ago)
    for s in signals or ():
        add(school_of(s), _side(s.get("direction")), s.get("name"), (s.get("vals") or {}).get("ago"))
    for h in harmonics or ():
        add("Fib/Harmonic", _side(h.get("dir")), f"Harmonic {h.get('name', '')}".strip())
    for name, bias in patterns or ():
        add("Price action", _side(bias), name)
    if phase in BULL_PHASES:
        add("Momentum", 1, "RSI " + phase.replace("_", " "))
    elif phase in BEAR_PHASES:
        add("Momentum", -1, "RSI " + phase.replace("_", " "))
    if flow_vote:
        add("Order flow", flow_vote, "prints / book / funding")
    for cell in out.values():
        cell["vote"] = (cell["bull"] > cell["bear"]) - (cell["bull"] < cell["bear"])
    return out


def conviction(votes: dict) -> dict:
    """Counts of schools: bull / bear / quiet, direction, and conviction 0-100 = net agreeing schools / 9."""
    bull = sum(v["vote"] > 0 for v in votes.values())
    bear = sum(v["vote"] < 0 for v in votes.values())
    n = len(SCHOOLS)
    direction = (bull > bear) - (bull < bear)
    return {"bull": bull, "bear": bear, "quiet": n - bull - bear, "dir": direction,
            "conv": round(100 * abs(bull - bear) / n), "bull_pct": round(100 * bull / n), "bear_pct": round(100 * bear / n)}


def verdict(c: dict, phase=None, regime=None) -> str:
    d, k = c["dir"], c["conv"]
    if phase in ("ext_up", "stall_ob") and c["bear"] >= 2:
        return "Topping: overbought, sellers building"
    if phase in ("ext_dn", "stall_os") and c["bull"] >= 2:
        return "Basing: oversold, buyers building"
    if d > 0:
        return "Long setup" if k >= 40 else "Bullish build-up" if k >= 20 else "Leaning up"
    if d < 0:
        return "Short setup" if k >= 40 else "Preparing to drop" if k >= 20 else "Leaning down"
    if regime == "Squeeze":
        return "Coiling: squeeze, wait for break"
    return "No edge"


def trade_plan(df, direction: int, levels=None):
    """Uniform plan from closed candles: entry = last close, stop beyond the nearest swing level (else 1.5 ATR),
    target = next opposite level (else 2R). -> dict or None when there is no side."""
    if not direction or df is None or len(df) < 20:
        return None
    from modules.signals import atr_series, sr_levels
    close = float(df["close"].iloc[-1])
    atr = float(atr_series(df).iloc[-1]) or close * 0.01
    res, sup = levels if levels is not None else sr_levels(df)
    if direction > 0:
        below = [x for x in sup if x < close - 0.2 * atr]
        stop = (max(below) - 0.2 * atr) if below else close - 1.5 * atr
        above = [x for x in res if x > close + 0.2 * atr]
        risk = close - stop
        target = min(above) if above else close + 2 * risk
    else:
        above = [x for x in res if x > close + 0.2 * atr]
        stop = (min(above) + 0.2 * atr) if above else close + 1.5 * atr
        below = [x for x in sup if x < close - 0.2 * atr]
        risk = stop - close
        target = max(below) if below else close - 2 * risk
    if risk <= 0:
        return None
    return {"entry": close, "stop": stop, "target": target, "rr": round(abs(target - close) / risk, 2),
            "risk_pct": round(100 * risk / close, 2), "reward_pct": round(100 * abs(target - close) / close, 2)}


TAGS = ("Urgent", "Fresh", "MTF aligned", "Pullback", "Reversal", "Momentum", "Squeeze", "Divergence", "Fast move", "Volume spike")


def derive_tags(item: dict, chart_tf: str, timeframes) -> tuple[list, str]:
    """Setup tags from numbers already on the record (no new detectors) + the urgent reason ('' when calm).
    Pullback = bigger timeframes trend one way while the map TF RSI is stretched the other way (buy the dip / sell the rip)."""
    tags, d, conv = [], item.get("dir") or 0, item.get("conv") or 0
    rsi, plan, fresh = item.get("rsi_map"), item.get("plan") or {}, item.get("fresh")
    higher = [tf for tf in timeframes if timeframes.index(tf) > timeframes.index(chart_tf)] if chart_tf in timeframes else []
    htf = [item.get("htf", {}).get(tf, 0) for tf in higher]
    htf_side = (all(x > 0 for x in htf) - all(x < 0 for x in htf)) if htf and all(htf) else 0
    trends = [v for v in item.get("htf", {}).values() if v]
    if trends and len(trends) == len(timeframes) and abs(sum(trends)) == len(trends):
        tags.append("MTF aligned")
    if rsi is not None and htf_side > 0 and rsi <= 40:
        tags.append("Pullback")
    if rsi is not None and htf_side < 0 and rsi >= 60:
        tags.append("Pullback")
    phase = item.get("phase", "")
    if phase in ("rev_up", "rev_down") or item.get("verdict", "").startswith(("Topping", "Basing")):
        tags.append("Reversal")
    if phase in ("mom_up", "mom_dn"):
        tags.append("Momentum")
    if item.get("regime") == "Squeeze":
        tags.append("Squeeze")
    if any("divergence" in n.lower() for v in (item.get("votes") or {}).values() for n in v.get("n", [])):
        tags.append("Divergence")
    if item.get("speed") == "●●":
        tags.append("Fast move")
    if (item.get("vol_x") or 0) >= 2:
        tags.append("Volume spike")
    if fresh is not None and fresh <= 2:
        tags.append("Fresh")
    urgent = ""
    if d and conv >= 33 and plan.get("rr", 0) >= 1.5 and fresh is not None and fresh <= 1:
        urgent = "fresh signal with conviction and R:R"
    elif d and conv >= 44 and ("Pullback" in tags or "Reversal" in tags):
        urgent = "high conviction at a turning point"
    elif "Fast move" in tags and ("Momentum" in tags or "Reversal" in tags):
        urgent = "fast RSI move through a band"
    if urgent:
        tags.insert(0, "Urgent")
    return tags, urgent


def read_symbol(df, setup: dict | None, flow_vote: int = 0, deep: bool = True) -> dict | None:
    """Full board record for one symbol on the map timeframe (df = closed candles)."""
    if df is None or len(df) < 20 or not setup:
        return None
    signals, harmonics, pats = [], [], []
    if deep and len(df) >= 60:
        try:
            from modules.scorer import cached_detect
            signals, _ = cached_detect(df)
        except Exception:
            signals = []
        try:
            from modules.harmonic import find_harmonics
            harmonics = find_harmonics(df.reset_index(drop=True))
        except Exception:
            harmonics = []
        try:
            from modules.patterns import PATTERNS, find
            pats = [PATTERNS[k] for k in find(df) if k in PATTERNS]
        except Exception:
            pats = []
    votes = school_votes(signals, harmonics, pats, setup.get("phase"), flow_vote)
    c = conviction(votes)
    agos = [v["ago"] for v in votes.values() if v["vote"] == c["dir"] and c["dir"] and v["ago"] is not None]
    try:
        plan = trade_plan(df, c["dir"])
    except Exception:
        plan = None
    return {"votes": votes, **c, "verdict": verdict(c, setup.get("phase"), setup.get("regime")),
            "fresh": min(agos) if agos else None, "plan": plan, "signals": signals,
            "harm": [h.get("name", "") for h in harmonics or []], "pats": [p[0] for p in pats]}
