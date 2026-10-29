"""
T1/T2 alerts test: WATCH vs CALL classification.
MEETING_ALERTS_SETUP.md — T1/T2 requirements.
"""
from modules.alerts import (
    classify_alert, WATCH_SCORE_MIN, CALL_SCORE_MIN, CALL_TRIGGER_WHITELIST
)


def _res(score, direction="bullish", signals=None, htf=None, ctx_flags=None):
    return {
        "score": score, "max_score": 7,
        "direction": direction,
        "signals": signals or [],
        "htf": htf or [],
        "context_flags": ctx_flags or [],
        "trade_type": "Day Trade",
        "reasons": [],
        "price": 100.0,
        "trend_bias": direction,
        "supports": [], "resistances": [],
    }


def _sig(key):
    return {"key": key, "family": "Fib", "direction": "bullish",
            "name": key, "icon": "•", "prices": {}}


def test_neutral_returns_none():
    assert classify_alert(_res(5, direction="neutral")) is None
    print("ok test_neutral_returns_none")


def test_below_watch_min_returns_none():
    assert classify_alert(_res(WATCH_SCORE_MIN - 1)) is None
    print("ok test_below_watch_min_returns_none")


def test_call_requires_whitelist_trigger():
    """score >= CALL_SCORE_MIN but no whitelist key → WATCH, not CALL."""
    res = _res(CALL_SCORE_MIN, signals=[_sig("elliott_wave_x")])
    kind = classify_alert(res)
    assert kind == "WATCH", f"Expected WATCH, got {kind}"
    print("ok test_call_requires_whitelist_trigger")


def test_call_fires_with_whitelist_trigger():
    """score >= CALL_SCORE_MIN + whitelist key → CALL."""
    res = _res(CALL_SCORE_MIN, signals=[_sig("fib_ote")])
    kind = classify_alert(res)
    assert kind == "CALL", f"Expected CALL, got {kind}"
    print("ok test_call_fires_with_whitelist_trigger")


def test_watch_fires_with_htf():
    """score == WATCH_SCORE_MIN, no trigger, but HTF confirms → WATCH."""
    res = _res(WATCH_SCORE_MIN, htf=[{"confirms": [{"name": "MA"}]}])
    kind = classify_alert(res)
    assert kind == "WATCH", f"Expected WATCH, got {kind}"
    print("ok test_watch_fires_with_htf")


def test_watch_fires_with_context_flags():
    """score == WATCH_SCORE_MIN, ctx_flags present → WATCH."""
    res = _res(WATCH_SCORE_MIN, ctx_flags=["Elliott"])
    kind = classify_alert(res)
    assert kind == "WATCH", f"Expected WATCH, got {kind}"
    print("ok test_watch_fires_with_context_flags")


def test_msb_ob_in_whitelist():
    assert "msb_ob" in CALL_TRIGGER_WHITELIST
    print("ok test_msb_ob_in_whitelist")


def test_high_score_no_trigger_no_htf_no_ctx_returns_watch():
    """score >= CALL_SCORE_MIN, no trigger, no HTF, no ctx → WATCH (not CALL, not None)."""
    res = _res(CALL_SCORE_MIN)
    kind = classify_alert(res)
    # score >= CALL_SCORE_MIN + no trigger → still WATCH (score condition in WATCH branch)
    assert kind == "WATCH", f"Expected WATCH, got {kind}"
    print("ok test_high_score_no_trigger_no_htf_no_ctx_returns_watch")


test_neutral_returns_none()
test_below_watch_min_returns_none()
test_call_requires_whitelist_trigger()
test_call_fires_with_whitelist_trigger()
test_watch_fires_with_htf()
test_watch_fires_with_context_flags()
test_msb_ob_in_whitelist()
test_high_score_no_trigger_no_htf_no_ctx_returns_watch()
print("T1/T2 alerts tests OK")
