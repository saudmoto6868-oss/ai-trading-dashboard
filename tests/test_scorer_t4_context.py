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
print("T4 scorer context tests OK")
