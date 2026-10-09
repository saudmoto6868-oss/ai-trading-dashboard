"""
THE HEAD ANALYST
Turns raw signals (modules/signals.py) into one scanner result per symbol:
direction, 0-7 stars, reasons, multi-timeframe context and trade type.

Scoring (doc: "a setup confirmed by two or three indicators carries more weight
than a single weaker signal" and "technical indicators are confirmation only"):
  * 7 signal families: Elliott, Unicorn, MSB-OB, Fib, Liquidity (primary) and
    MA, VWAP (confirmation only).
  * stars = number of DISTINCT families agreeing on the dominant direction.
  * confirmation-only families are worth at most 1 star unless at least one
    primary family agrees.
  * each opposing primary family takes one star away (conflicting evidence).

Trade type (doc: multi-timeframe top-down process): comes from which
timeframe actually CONFIRMS the trigger, not from the tab it was fetched on.
  - the trigger timeframe sets the base type (1m scalp, 1h day, 1d swing, 1w position)
  - if a HIGHER timeframe shows an aligned primary signal (structure / zone /
    wave / sweep on the same side), the trade is upgraded to that timeframe's
    horizon, e.g. a 1-minute trigger at a weekly zone = Position.
"""

from modules.signals import (
    BULL, BEAR, PRIMARY_FAMILIES, CONFIRM_FAMILIES, ALL_FAMILIES, detect_all, sr_levels, fp,
)

MAX_STARS = len(ALL_FAMILIES)  # 7

SCAN_TFS = ["1m", "1h", "1d", "1w"]
CONTEXT_TFS = {"1m": ["1h", "1d", "1w"], "1h": ["1d", "1w"], "1d": ["1w"], "1w": []}
BASE_TRADE_TYPE = {"1m": "Scalp", "1h": "Day Trade", "1d": "Swing", "1w": "Position"}
CONFIRM_TRADE_TYPE = {"1h": "Day Trade", "1d": "Swing", "1w": "Position"}
TF_LABEL = {"1m": "1 minute", "1h": "1 hour", "1d": "1 day", "1w": "1 week"}

# legacy labels used by the MT5 (forex/metals/stocks) path
LEGACY_TF = {"M1": "1m", "M5": "1m", "M15": "1m", "H1": "1h", "H4": "1h", "D1": "1d", "W1": "1w", "MN1": "1w"}


def aggregate(signals: list) -> dict:
    fams = {BULL: set(), BEAR: set()}
    for s in signals:
        fams[s["direction"]].add(s["family"])

    def effective(d):
        f = fams[d]
        if not f:
            return 0
        prim = f & set(PRIMARY_FAMILIES)
        return len(f) if prim else 1  # confirmation alone = 1 star max

    def opposing_primary(d):
        return len(fams[BEAR if d == BULL else BULL] & set(PRIMARY_FAMILIES))

    sb, sr = effective(BULL), effective(BEAR)
    if sb == sr:
        return {"direction": "neutral", "stars": 0, "aligned": set(), "mixed": sb > 0,
                "fams": fams}
    d = BULL if sb > sr else BEAR
    eff = max(sb, sr)
    stars = max(1, eff - opposing_primary(d))
    return {"direction": d, "stars": min(stars, MAX_STARS), "aligned": fams[d], "mixed": False, "fams": fams}


_memo: dict = {}


def cached_detect(df):
    """detect_all() memoised on the last candles, so the 10-20s auto-refresh does
    not re-scan frames whose latest candle has not changed."""
    tail = df.tail(3)
    key = (len(df), str(df["time"].iloc[-1]), round(float(tail["close"].sum()), 8),
           round(float(tail["high"].sum()), 8), round(float(tail["low"].sum()), 8))
    hit = _memo.get(key)
    if hit is None:
        if len(_memo) > 200:
            _memo.clear()
        hit = _memo[key] = detect_all(df)
    return hit


def _meaningful_for_htf(s: dict) -> bool:
    """Which signals may confirm a trade from a HIGHER timeframe: structure, zones,
    waves, sweeps and key levels - not one-bar noise like OHL or a 20-bar breakout."""
    if s["family"] in ("Elliott", "Unicorn", "MSB-OB", "Fib"):
        return True
    return s["family"] == "Liquidity" and ("sweep" in s["name"].lower() or s["name"].startswith("At "))


def htf_view(df, tf: str, direction: str) -> dict:
    """Does this higher timeframe back the trigger? (meaningful primary signal on the same side)"""
    if df is None or len(df) < 60 or direction == "neutral":
        return {"tf": tf, "confirms": [], "available": df is not None and len(df) >= 60}
    sigs, _ = cached_detect(df)
    ok = [s for s in sigs if s["direction"] == direction and _meaningful_for_htf(s)]
    trend = [s for s in sigs if s["direction"] == direction and s["family"] == "MA"]
    return {"tf": tf, "available": True, "confirms": ok, "trend_aligned": bool(trend)}


def scan_symbol(symbol: str, frames: dict, trigger_tf: str) -> dict:
    df = frames.get(trigger_tf)
    if df is None or len(df) < 60:
        raise ValueError(f"not enough {trigger_tf} candles for {symbol}")
    sigs, errs = cached_detect(df)
    agg = aggregate(sigs)
    direction = agg["direction"]
    mine = [s for s in sigs if s["direction"] == direction] if direction != "neutral" else []
    against = [s for s in sigs if direction != "neutral" and s["direction"] != direction]

    htf = [htf_view(frames.get(tf), tf, direction) for tf in CONTEXT_TFS.get(trigger_tf, [])]
    trade_type = BASE_TRADE_TYPE[trigger_tf]
    for h in reversed(htf):  # highest timeframe first
        if h["confirms"]:
            trade_type = CONFIRM_TRADE_TYPE[h["tf"]]
            break

    res, sup = sr_levels(df)
    price = float(df["close"].iloc[-1])
    order = {f: i for i, f in enumerate(ALL_FAMILIES)}
    mine.sort(key=lambda s: order[s["family"]])
    return {
        "symbol": symbol,
        "score": agg["stars"], "max_score": MAX_STARS,
        "direction": direction,
        "trend_bias": direction,
        "mixed": agg["mixed"],
        "signals": mine, "against": against,
        "families": sorted(agg["aligned"], key=order.get) if direction != "neutral" else [],
        "reasons": [f"{s['icon']} {s['name']}" for s in mine],
        "icons": "".join(dict.fromkeys(s["icon"] for s in mine)),
        "htf": htf,
        "trade_type": trade_type,
        "timeframe": trigger_tf,
        "price": price,
        "supports": sup, "resistances": res,
        "liquidity_levels": [],
        "errors": errs,
    }


def score_symbol(df, timeframe_label: str = "H1") -> dict:
    """Legacy entry point (MT5 forex/metals/stocks path): single timeframe, no HTF context."""
    tf = LEGACY_TF.get(timeframe_label, "1h")
    return scan_symbol("", {tf: df}, tf)


def htf_lines(res: dict) -> list:
    """Human-readable multi-timeframe lines for the detail panel."""
    out = []
    for h in res["htf"]:
        label = TF_LABEL[h["tf"]]
        if not h["available"]:
            out.append(f"{label}: no data")
        elif h["confirms"]:
            names = ", ".join(f"{s['icon']} {s['name']}" for s in h["confirms"][:3])
            out.append(f"{label}: CONFIRMS - {names}")
        else:
            trend = "trend agrees, " if h.get("trend_aligned") else ""
            out.append(f"{label}: {trend}no structure/zone signal on this side")
    return out


def scenarios(res: dict) -> list:
    """2-3 pre-planned scenarios (doc: always picture them before entry)."""
    d = res["direction"]
    if d == "neutral" or not res["signals"]:
        return ["No dominant direction - nothing to plan. Wait for confluence."]
    long = d == BULL
    prices = {}
    for s in res["signals"]:
        prices.update(s["prices"])
    zones = [s["zone"] for s in res["signals"] if s.get("zone")]
    inv = prices.get("inv") or prices.get("start")
    if zones:
        lo, hi = zones[0]
        inv = lo if long else hi
    tgt = prices.get("t") or prices.get("x1") or prices.get("t1") or prices.get("m3")
    verb, opp = ("hold and bounce", "breaks below") if long else ("hold and reject", "breaks above")
    out = [f"1) Level/zone holds: wait for a candle to {verb}, then enter in the {d} direction"
           + (f"; first objective around {fp(tgt)}." if tgt else ".")]
    if inv:
        out.append(f"2) Level fails: a close that {opp} {fp(inv)} cancels the idea - stand aside or look the other way.")
    out.append("3) Trap: price spikes through, then closes back - fade the spike only after the order book / time & sales "
               "confirm (wall absorbed, no follow-through).")
    return out
