"""
T4 scorer test: context families (Elliott) are flags, not trigger stars.
MEETING_ALERTS_SETUP.md — T4 requirement.
"""
from modules.signals import BULL, BEAR
from modules.scorer import aggregate, CONTEXT_FAMILIES, TRIGGER_FAMILIES


def _sig(family, direction, key=None):
    return {"family": family, "direction": direction, "key": key or family.lower()}


def test_context_family_alone_gives_zero_stars():
    """Elliott alone: 0 stars, but ctx_flags populated."""
    sigs = [_sig("Elliott", BULL)]
    r = aggregate(sigs)
    assert r["stars"] == 0, f"Expected 0 stars for Elliott alone, got {r['stars']}"
    assert r["direction"] == "neutral", f"Expected neutral, got {r['direction']}"
    assert "Elliott" in r["ctx_flags"][BULL]


def test_context_family_does_not_add_star_to_trigger():
    """Elliott + 1 trigger family = 1 star (not 2)."""
    sigs = [_sig("Elliott", BULL), _sig("MA", BULL)]
    r = aggregate(sigs)
    assert r["stars"] == 1, f"Expected 1 star (MA), got {r['stars']}"
    assert r["direction"] == BULL
    assert "Elliott" in r["ctx_flags"][BULL]


def test_trigger_families_count_normally():
    """Fib + Liquidity = 2 stars."""
    sigs = [_sig("Fib", BULL, "ote"), _sig("Liquidity", BULL, "sweep")]
    r = aggregate(sigs)
    assert r["stars"] == 2, f"Expected 2 stars, got {r['stars']}"


def test_context_families_in_correct_set():
    """Elliott should be in CONTEXT_FAMILIES, not TRIGGER_FAMILIES."""
    assert "Elliott" in CONTEXT_FAMILIES
    assert "Elliott" not in TRIGGER_FAMILIES


def test_trigger_families_still_include_fib_liquidity_ma():
    """Core trigger families are present."""
    for f in ("Fib", "Liquidity", "MA", "Unicorn", "MSB-OB"):
        assert f in TRIGGER_FAMILIES, f"{f} missing from TRIGGER_FAMILIES"


def test_scan_symbol_with_context_family_signal():
    """A context-family (PA) signal on the trade's side must not crash scan_symbol (KeyError 'PA' in the Telegram cron)."""
    import numpy as np
    import pandas as pd
    import modules.scorer as S
    n = 120
    c = 100 + np.cumsum(np.random.default_rng(1).normal(0, 1, n))
    df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="h"), "open": c, "high": c + 1, "low": c - 1,
                       "close": c, "volume": 1000.0})
    fake = [{"family": "PA", "direction": BULL, "key": "pa_x", "name": "PA x", "icon": "P"},
            {"family": "MA", "direction": BULL, "key": "ma_x", "name": "MA x", "icon": "M"},
            {"family": "Fib", "direction": BULL, "key": "ote", "name": "Fib", "icon": "F"}]
    orig = S.cached_detect
    S.cached_detect = lambda d: (fake, [])
    try:
        r = S.scan_symbol("TEST", {"1h": df}, "1h")
    finally:
        S.cached_detect = orig
    assert r["direction"] == BULL
    assert [s["family"] for s in r["signals"]][-1] == "PA"   # star families first, context last


print("ok test_context_family_alone_gives_zero_stars")
test_context_family_alone_gives_zero_stars()
print("ok test_context_family_does_not_add_star_to_trigger")
test_context_family_does_not_add_star_to_trigger()
print("ok test_trigger_families_count_normally")
test_trigger_families_count_normally()
print("ok test_context_families_in_correct_set")
test_context_families_in_correct_set()
print("ok test_trigger_families_still_include_fib_liquidity_ma")
test_trigger_families_still_include_fib_liquidity_ma()
print("ok test_scan_symbol_with_context_family_signal")
test_scan_symbol_with_context_family_signal()
print("T4 scorer context tests OK")
