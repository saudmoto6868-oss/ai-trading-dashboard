"""
THE HEAD ANALYST
Turns raw signals (modules/signals.py) into one scanner result per symbol:
direction, 0-7 stars, reasons, multi-timeframe context and trade type.

Scoring (T4 redesign — MEETING_ALERTS_SETUP.md):
  * Two tiers of families:
    - TRIGGER families (count toward stars): MA, VWAP, TL (trend/confirmation),
      Unicorn, MSB-OB, Fib, Liquidity — these are the «where» and «whether to act».
    - CONTEXT families (flag only, shown in UI but do NOT add a star): Elliott.
      (Gann, Harmonic, SMC added here when their detectors land.)
      A CONTEXT signal alone is a WATCH, never enough to drive a CALL.
  * stars = number of DISTINCT TRIGGER families agreeing on the dominant direction.
    Context families are surfaced in result["context_flags"] for display.
  * confirmation-only families (MA/VWAP/TL) are worth at most 1 star unless at
    least one non-confirmation TRIGGER family agrees.
  * each opposing primary TRIGGER family takes one star away (conflicting evidence).

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

# T4 (MEETING_ALERTS_SETUP.md): context families shown as flags, not counted as stars.
# These add a WATCH signal but cannot drive a CALL on their own.
# Elliott is context because the lab shows low t-stat and it is primarily a «map» tool.
# Add "Gann", "Harmonic", "SMC" here as their detectors are built.
CONTEXT_FAMILIES: tuple = ("Elliott",)

# Trigger families = ALL_FAMILIES minus context families
TRIGGER_FAMILIES: tuple = tuple(f for f in ALL_FAMILIES if f not in CONTEXT_FAMILIES)

MAX_STARS = len(TRIGGER_FAMILIES)  # updated from ALL_FAMILIES

import os as _os
# horizons scanned in the background (alerts + journal). 1m is OFF by default: in the owner's journal (Oct 2026, 1110 trades)
# 735 one-minute trades lost about -147R of the -150R total. Set SCAN_1M=1 in env / Secrets to bring it back.
SCAN_TFS = ["1h", "1d", "1w"] + (["1m"] if _os.environ.get("SCAN_1M") == "1" else [])
MAX_SAME_SIDE = 3   # per scan timeframe: at most this many alerts in the same direction (they are mostly one market-wide bet)
# every timeframe the user can pick for a scan (13m/3h/7h/8h are built from 1m/1h candles, the rest are OKX bar sizes)
ALL_SCAN_TFS = ["1m", "13m", "1h", "2h", "3h", "6h", "7h", "8h", "12h", "1d", "3d", "1w", "1mo"]
CONTEXT_TFS = {"1m": ["1h", "1d", "1w"], "13m": ["1h", "1d", "1w"], "1h": ["1d", "1w"], "2h": ["1d", "1w"], "3h": ["1d", "1w"],
               "6h": ["1d", "1w"], "7h": ["1d", "1w"], "8h": ["1d", "1w"], "12h": ["1d", "1w"], "1d": ["1w"], "3d": ["1w"], "1w": [], "1mo": []}
BASE_TRADE_TYPE = {"1m": "Scalp", "13m": "Scalp", "1h": "Day Trade", "2h": "Day Trade", "3h": "Day Trade", "6h": "Swing", "7h": "Swing", "8h": "Swing",
                   "12h": "Swing", "1d": "Swing", "3d": "Swing", "1w": "Position", "1mo": "Position"}
CONFIRM_TRADE_TYPE = {"1h": "Day Trade", "1d": "Swing", "1w": "Position"}
TF_LABEL = {"1m": "1 minute", "13m": "13 minutes", "1h": "1 hour", "2h": "2 hours", "3h": "3 hours", "6h": "6 hours", "7h": "7 hours", "8h": "8 hours",
            "12h": "12 hours", "1d": "1 day", "3d": "3 days", "1w": "1 week", "1mo": "1 month"}

# legacy labels used by the MT5 (forex/metals/stocks) path
LEGACY_TF = {"M1": "1m", "M5": "1m", "M15": "1m", "H1": "1h", "H4": "1h", "D1": "1d", "W1": "1w", "MN1": "1w"}


# Direct buy/sell indicators (MSB-OB: "structure break + order block retest") are CONFIRMATION only: they never start a
# trade, they add their family's star only when another primary family already backs the same side.
CONFIRM_ONLY_KEYS = ("msb_ob",)


def aggregate(signals: list) -> dict:
    fams = {BULL: set(), BEAR: set()}               # trigger families only (count as stars)
    ctx_flags = {BULL: set(), BEAR: set()}          # context families (Elliott etc) — displayed, not counted
    held = {BULL: set(), BEAR: set()}               # families that only a confirm-only signal supports
    try:
        from modules.lab_tiers import off_keys
        off = off_keys()          # detectors the weekly lab found clearly negative: shown, but they do not decide a trade
    except Exception:
        off = frozenset()
    for s in signals:
        if s.get("key") in off:
            continue
        fam = s["family"]
        side = s["direction"]
        if fam in CONTEXT_FAMILIES:
            # T4: context families are a WATCH flag — never a trigger star
            ctx_flags[side].add(fam)
            continue
        if s.get("key") in CONFIRM_ONLY_KEYS:
            held[side].add(fam)
        else:
            fams[side].add(fam)
    for d in (BULL, BEAR):
        others = fams[d] & set(PRIMARY_FAMILIES)
        for f in held[d]:
            if f in fams[d] or others:                  # a primary family (other than the held one) already agrees
                fams[d].add(f)

    # TRIGGER families only (context excluded above)
    TRIGGER_PRIMARY = tuple(f for f in PRIMARY_FAMILIES if f not in CONTEXT_FAMILIES)

    def effective(d):
        f = fams[d]
        if not f:
            return 0
        prim = f & set(TRIGGER_PRIMARY)
        return len(f) if prim else 1  # confirmation alone = 1 star max

    def opposing_primary(d):
        return len(fams[BEAR if d == BULL else BULL] & set(TRIGGER_PRIMARY))

    sb, sr = effective(BULL), effective(BEAR)
    if sb == sr:
        return {"direction": "neutral", "stars": 0, "aligned": set(), "mixed": sb > 0,
                "fams": fams, "ctx_flags": ctx_flags}
    d = BULL if sb > sr else BEAR
    eff = max(sb, sr)
    stars = max(1, eff - opposing_primary(d))
    return {"direction": d, "stars": min(stars, MAX_STARS), "aligned": fams[d], "mixed": False,
            "fams": fams, "ctx_flags": ctx_flags}


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
    if s.get("key") in CONFIRM_ONLY_KEYS:
        return False                                      # confirmation only: cannot be what upgrades a trade's horizon
    if s["family"] in ("Elliott", "Unicorn", "MSB-OB", "Fib"):
        return True
    return s["family"] == "Liquidity" and ("sweep" in s["name"].lower() or s["name"].startswith("At "))


SWING_FETCH = {"6h", "7h", "8h", "12h", "1d", "3d"}   # swing triggers also pull the 4H candles for the weekly/daily/4H framework (modules/mtf.py)


def fetch_tfs(trigger_tf: str) -> list:
    """Timeframes to fetch for one scan: the trigger, its higher-timeframe context, and 4H for swing triggers."""
    out = [trigger_tf] + list(CONTEXT_TFS.get(trigger_tf, []))
    if trigger_tf in SWING_FETCH and "4h" not in out:
        out.append("4h")
    return out


def htf_view(df, tf: str, direction: str) -> dict:
    """Does this higher timeframe back the trigger? (meaningful primary signal on the same side)"""
    if df is None or len(df) < 60 or direction == "neutral":
        return {"tf": tf, "confirms": [], "available": df is not None and len(df) >= 60}
    sigs, _ = cached_detect(df)
    ok = [s for s in sigs if s["direction"] == direction and _meaningful_for_htf(s)]
    trend = [s for s in sigs if s["direction"] == direction and s["family"] == "MA"]
    return {"tf": tf, "available": True, "confirms": ok, "trend_aligned": bool(trend)}


def scan_symbol(symbol: str, frames: dict, trigger_tf: str, peers: dict | None = None) -> dict:
    """peers = {peer_symbol: (inverse, df_on_trigger_tf)} enables SMT divergence against correlated markets."""
    df = frames.get(trigger_tf)
    if df is None or len(df) < 60:
        raise ValueError(f"not enough {trigger_tf} candles for {symbol}")
    sigs, errs = cached_detect(df)
    if peers:
        from modules.smt import smt_signals
        sigs, errs = list(sigs), list(errs)
        for psym, (inv, pdf) in peers.items():
            try:
                sigs += smt_signals(df, pdf, psym, inv)
            except Exception as e:
                errs.append(f"smt {psym}: {e}")
    agg = aggregate(sigs)
    direction = agg["direction"]
    mine = [s for s in sigs if s["direction"] == direction] if direction != "neutral" else []
    against = [s for s in sigs if direction != "neutral" and s["direction"] != direction]

    htf = [htf_view(frames.get(tf), tf, direction) for tf in CONTEXT_TFS.get(trigger_tf, [])]
    # the type follows the TRIGGER timeframe (its stop / target / holding time); a higher timeframe that agrees is shown as
    # htf_type, it no longer relabels a 1-minute trade as "Position" (the journal showed those still behave like scalps)
    trade_type, htf_type = BASE_TRADE_TYPE[trigger_tf], None
    for h in reversed(htf):  # highest timeframe first
        if h["confirms"]:
            htf_type = CONFIRM_TRADE_TYPE[h["tf"]]
            break

    mtf = None
    try:   # weekly / daily / 4H framework + coherence; shown and used for ranking, never counted in the stars
        from modules.mtf import analyse as _mtf
        if direction != "neutral":
            mtf = _mtf(frames, direction, trigger_tf, df)
    except Exception:
        mtf = None
    res, sup = sr_levels(df)
    from modules.risk_engine import vol_target_weight
    volsz = vol_target_weight(df, trigger_tf)
    price = float(df["close"].iloc[-1])
    order = {f: i for i, f in enumerate(ALL_FAMILIES)}
    mine.sort(key=lambda s: order[s["family"]])
    try:
        from modules.context import market_context
        ctx = market_context(df, direction if direction != "neutral" else None)
    except Exception:
        ctx = {}
    # T4: context flags (Elliott etc.) shown separately — WATCH only, not CALL drivers
    ctx_fams = sorted(agg["ctx_flags"].get(direction, set())) if direction != "neutral" else []
    return {
        "context": ctx,   # where / when / which side (daily bias, premium/discount, NY killzone) - shown, never counted in the stars
        "context_flags": ctx_fams,   # T4: context families (Elliott/Gann/Harmonic/SMC) — display as WATCH badge, not stars
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
        "mtf": mtf,
        "trade_type": trade_type,
        "htf_type": htf_type,
        "timeframe": trigger_tf,
        "price": price,
        "supports": sup, "resistances": res,
        "liquidity_levels": [],
        "errors": errs,
        "vol": volsz,
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
