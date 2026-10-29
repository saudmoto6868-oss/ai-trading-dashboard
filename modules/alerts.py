"""
THE ALERT OFFICER
Watches scored signals; when one crosses the alert threshold, fires a
sound, colored banner, and full trade plan (entry, stop loss, 3 staged
take profits). This is also the hook point for a future Telegram bot.

T1/T2 (MEETING_ALERTS_SETUP.md):
  Two alert kinds — WATCH and CALL — replace the flat score >= 4 threshold.

  WATCH: score >= WATCH_SCORE_MIN AND (HTF confirms OR context_flags present)
         → shows a banner but does NOT trigger sound by default.
         Meaning: «the story is forming, keep eyes on this».

  CALL:  score >= CALL_SCORE_MIN AND at least one trigger from CALL_TRIGGER_WHITELIST
         AND direction != neutral.
         → shows banner + optional sound + full trade plan.
         Meaning: «actionable — a real trigger with location backing».

  The optional OF/session gate is surfaced as a confidence flag in the result
  dict (call_gated=True) but is NOT a hard requirement — the owner can enable
  hard gating later with CALL_REQUIRE_GATE=True.
"""

import streamlit as st
from modules.risk_engine import build_trade_plan

# ── thresholds (T2) ────────────────────────────────────────────────────────────
WATCH_SCORE_MIN = 3   # min stars to show a WATCH banner
CALL_SCORE_MIN  = 4   # min stars to show a CALL banner (with whitelist check)

# Kept for backward compatibility with any caller that uses the old constant.
ALERT_SCORE_THRESHOLD = CALL_SCORE_MIN

# ── CALL whitelist (T1) ────────────────────────────────────────────────────────
# A CALL requires at least one signal key from this set.
# These are «real» triggers: structure, zone retests, sweeps, MA crossovers.
# Context-only signals (Elliott waves, Gann, Harmonic PRZ alone) are excluded
# until the lab shows n>=100 + t>3 for them.
CALL_TRIGGER_WHITELIST: frozenset = frozenset({
    # Structure / OB / FVG
    "msb_ob",
    # Fib / OTE
    "fib_ote", "fib_ext",
    # Liquidity sweeps
    "sweep_high", "sweep_low", "kzs", "liq_sweep",
    # MA / trend
    "ma_cross", "ma_slope", "sma200_cross", "ema_stack",
    # Elliott impulse wave (only when confirmed by another trigger)
    "ew_r3_v",
    # Unicorn (SMC confluent setup)
    "unicorn",
    # VWAP reclaim / reject
    "vwap_reclaim", "vwap_reject",
    # Support/resistance bounce
    "sr_bounce", "sr_break",
})


STRENGTH_COLORS = {
    "strong": "#1f9d55",
    "medium": "#d4a72c",
    "weak":   "#9aa0a6",
}

ALERT_KIND_COLORS = {
    "CALL":  "#1f9d55",   # green  — actionable
    "WATCH": "#d4a72c",   # amber  — context / forming
}


def classify_strength(score: int, max_score: int) -> str:
    ratio = score / max_score
    if ratio >= 0.75:
        return "strong"
    if ratio >= 0.5:
        return "medium"
    return "weak"


def classify_alert(score_result: dict) -> str:
    """
    T1/T2: decide CALL vs WATCH vs None.

    Returns one of: "CALL", "WATCH", None.
    None means the signal does not reach any alert threshold.
    """
    score     = score_result.get("score", 0)
    direction = score_result.get("direction", "neutral")
    signals   = score_result.get("signals", [])
    htf       = score_result.get("htf", [])
    ctx_flags = score_result.get("context_flags", [])

    if direction == "neutral" or score < WATCH_SCORE_MIN:
        return None

    # Check for a whitelisted trigger key in the current signals
    has_trigger = any(
        s.get("key") in CALL_TRIGGER_WHITELIST for s in signals
    )

    # HTF confirmation: at least one higher timeframe confirms
    htf_ok = any(h.get("confirms") for h in htf)

    if score >= CALL_SCORE_MIN and has_trigger:
        return "CALL"

    # WATCH: score in [WATCH_SCORE_MIN, CALL_SCORE_MIN) OR no whitelist trigger
    if score >= WATCH_SCORE_MIN and (htf_ok or ctx_flags or score >= CALL_SCORE_MIN):
        return "WATCH"

    return None


def is_gate_confirmed(score_result: dict) -> bool:
    """
    Optional OF/session gate (T1 note 5).
    Returns True when order-flow direction or a kill-zone marker agrees with
    the signal direction. Currently read from score_result["context"] if present.
    This is advisory — surfaced as call_gated in the result, not a hard block.
    """
    ctx = score_result.get("context", {})
    direction = score_result.get("direction", "neutral")
    of_dir = ctx.get("of_direction")   # "bullish" / "bearish" / None
    in_kz  = ctx.get("in_killzone", False)
    if of_dir and of_dir == direction:
        return True
    if in_kz:
        return True
    return False


_BEEP_HTML = """
<audio autoplay>
  <source src="data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQQAAAAAAAAA" type="audio/wav">
</audio>
"""


def fire_alert(symbol: str, score_result: dict, play_sound: bool = True,
               alert_kind: str | None = None):
    """
    Render an alert banner.  alert_kind must be "CALL" or "WATCH".
    For CALL: full trade plan + optional sound.
    For WATCH: summary banner only, no sound.
    """
    if alert_kind is None:
        alert_kind = classify_alert(score_result)
    if alert_kind is None:
        return None

    strength = classify_strength(score_result["score"], score_result["max_score"])
    color    = ALERT_KIND_COLORS.get(alert_kind, STRENGTH_COLORS[strength])
    gated    = is_gate_confirmed(score_result)
    ctx_flags = score_result.get("context_flags", [])

    plan = None
    plan_html = ""
    if alert_kind == "CALL":
        plan = build_trade_plan(score_result)
        plan_html = (
            f"Entry: {plan['entry']} | SL: {plan['stop_loss']}<br>"
            f"TP1: {plan['take_profits'][0]} | "
            f"TP2: {plan['take_profits'][1]} | "
            f"TP3: {plan['take_profits'][2]}<br>"
        )

    ctx_line = ""
    if ctx_flags:
        ctx_line = f"<span style='color:#aaa; font-size:11px;'>Context: {', '.join(ctx_flags)}</span><br>"

    gate_line = ""
    if gated:
        gate_line = "<span style='color:#6fcf97; font-size:11px;'>✓ OF/Session gate confirmed</span><br>"

    st.markdown(
        f"""
        <div style="border-left: 6px solid {color}; background-color: #1a1a1a;
                    padding: 12px 16px; border-radius: 6px; margin-bottom: 8px;">
            <span style="color:{color}; font-weight:bold; font-size:16px;">
                [{alert_kind}] {symbol} — {strength.upper()} ({score_result['trade_type']})
            </span><br>
            <span style="color:#ddd;">
                Direction: {score_result['direction']} |
                Stars: {score_result['score']}/{score_result['max_score']}<br>
                {plan_html}
                {ctx_line}
                {gate_line}
                Triggers: {', '.join(score_result['reasons'])}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if play_sound and alert_kind == "CALL":
        st.markdown(_BEEP_HTML, unsafe_allow_html=True)

    return {**(plan or {}), "alert_kind": alert_kind, "gate_confirmed": gated}


def check_and_fire_alerts(results: list, play_sound: bool = True):
    fired = []
    for res in results:
        kind = classify_alert(res)
        if kind is None:
            continue
        plan = fire_alert(res["symbol"], res, play_sound=play_sound, alert_kind=kind)
        if plan is not None:
            fired.append({**res, "plan": plan, "alert_kind": kind})
    return fired
