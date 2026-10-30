"""
T3 risk_engine test: setup-type aware trade plan (levels / trend / reversal / fallback).
MEETING_ALERTS_SETUP.md — T3 requirement.
"""
from modules.risk_engine import build_trade_plan, _detect_book


def _res(signals, price=1000.0, bias="bullish", supports=None, resistances=None):
    return {
        "price": price, "trend_bias": bias,
        "signals": signals,
        "supports": supports or [980.0, 960.0, 940.0],
        "resistances": resistances or [1020.0, 1040.0, 1060.0],
    }


def _sig(key, family="Fib", prices=None):
    return {"key": key, "family": family, "direction": "bullish",
            "name": key, "icon": "•", "prices": prices or {}}


# ── book detection ─────────────────────────────────────────────────────────────

def test_detect_reversal_book():
    assert _detect_book([_sig("msb_ob")]) == "reversal"
    print("ok test_detect_reversal_book")


def test_detect_levels_book():
    assert _detect_book([_sig("ote")]) == "levels"
    print("ok test_detect_levels_book")


def test_detect_trend_book():
    assert _detect_book([_sig("ma_cross")]) == "trend"
    print("ok test_detect_trend_book")


def test_detect_fallback():
    assert _detect_book([_sig("unknown_key")]) == "fallback"
    print("ok test_detect_fallback")


def test_reversal_priority_over_levels():
    """Reversal key beats levels key when both present."""
    assert _detect_book([_sig("ote"), _sig("unicorn")]) == "reversal"
    print("ok test_reversal_priority_over_levels")


# ── plan sanity ────────────────────────────────────────────────────────────────

def _check_plan(plan, long):
    entry = plan["entry"]
    sl    = plan["stop_loss"]
    tps   = plan["take_profits"]
    assert len(tps) == 3, f"Expected 3 TPs, got {len(tps)}"
    if long:
        assert sl < entry,  f"Long: SL {sl} must be below entry {entry}"
        assert tps[0] > entry, f"Long: TP1 {tps[0]} must be above entry {entry}"
    else:
        assert sl > entry,  f"Short: SL {sl} must be above entry {entry}"
        assert tps[0] < entry, f"Short: TP1 {tps[0]} must be below entry {entry}"
    assert plan["risk_distance"] > 0, "risk_distance must be positive"


def test_levels_plan_long():
    res = _res([_sig("ote", prices={"lo": 995.0, "hi": 1000.0})], bias="bullish")
    plan = build_trade_plan(res)
    assert plan["book"] == "levels"
    _check_plan(plan, long=True)
    print("ok test_levels_plan_long")


def test_trend_plan_long():
    res = _res([_sig("ma_cross")], bias="bullish")
    plan = build_trade_plan(res)
    assert plan["book"] == "trend"
    _check_plan(plan, long=True)
    print("ok test_trend_plan_long")


def test_reversal_plan_short():
    res = _res([_sig("sweep")], bias="bearish",
               supports=[960.0, 940.0], resistances=[1020.0, 1040.0])
    plan = build_trade_plan(res)
    assert plan["book"] == "reversal"
    _check_plan(plan, long=False)
    print("ok test_reversal_plan_short")


def test_fallback_plan_no_signals():
    res = _res([], bias="bullish")
    plan = build_trade_plan(res)
    assert plan["book"] == "fallback"
    _check_plan(plan, long=True)
    print("ok test_fallback_plan_no_signals")


def test_plan_always_has_book_field():
    for key, bias in [("msb_ob", "bullish"), ("ote", "bearish"),
                       ("ma_cross", "bullish"), ("????", "bullish")]:
        res = _res([_sig(key)], bias=bias)
        plan = build_trade_plan(res)
        assert "book" in plan, f"book missing for key={key}"
    print("ok test_plan_always_has_book_field")


test_detect_reversal_book()
test_detect_levels_book()
test_detect_trend_book()
test_detect_fallback()
test_reversal_priority_over_levels()
test_levels_plan_long()
test_trend_plan_long()
test_reversal_plan_short()
test_fallback_plan_no_signals()
test_plan_always_has_book_field()
print("T3 risk_engine tests OK")
