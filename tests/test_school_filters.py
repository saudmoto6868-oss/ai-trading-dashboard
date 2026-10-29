"""
Tests for SCHOOL_FILTERS in modules/chart_scan.py  (Item 25 / priority 4)
mock-tested only — no network.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

EXPECTED_SCHOOLS = {
    "sch_ict":      "SMC / ICT",
    "sch_elliott":  "Elliott wave",
    "sch_harmonic": "Harmonic",
    "sch_trend":    "Trend",
    "sch_liq":      "Liquidity",
    "sch_session":  "Time (sessions)",
    "sch_fib":      "Fibonacci",
    "sch_mom":      "Momentum / divergence",
    "sch_level":    "Levels / breakouts",
    "sch_smt":      "Intermarket (SMT)",
}


def test_school_filters_present():
    """All 10 school filter IDs exist in STRATEGY_FILTERS."""
    import importlib, modules.chart_scan as cs
    importlib.reload(cs)
    for fid in EXPECTED_SCHOOLS:
        assert fid in cs.STRATEGY_FILTERS, f"Missing {fid} in STRATEGY_FILTERS"
    print("PASS test_school_filters_present")


def test_school_filters_in_all_filters():
    """All school filter labels appear in ALL_FILTERS."""
    import importlib, modules.chart_scan as cs
    importlib.reload(cs)
    for fid in EXPECTED_SCHOOLS:
        assert fid in cs.ALL_FILTERS, f"Missing {fid} in ALL_FILTERS"
    print("PASS test_school_filters_in_all_filters")


def test_school_matcher_kind():
    """Each school filter uses matcher kind == 'school'."""
    import importlib, modules.chart_scan as cs
    importlib.reload(cs)
    for fid in EXPECTED_SCHOOLS:
        label, matcher = cs.STRATEGY_FILTERS[fid]
        kind, school_name = matcher
        assert kind == "school", f"{fid}: expected kind='school', got {kind!r}"
    print("PASS test_school_matcher_kind")


def test_school_name_values():
    """Each school filter's school_name contains the expected substring."""
    import importlib, modules.chart_scan as cs
    importlib.reload(cs)
    for fid, expected_substr in EXPECTED_SCHOOLS.items():
        label, matcher = cs.STRATEGY_FILTERS[fid]
        kind, school_name = matcher
        assert expected_substr in school_name, (
            f"{fid}: school_name={school_name!r} doesn't contain {expected_substr!r}"
        )
    print("PASS test_school_name_values")


def test_school_count():
    """Exactly 10 school filters registered."""
    import importlib, modules.chart_scan as cs
    importlib.reload(cs)
    sch_keys = [k for k in cs.STRATEGY_FILTERS if k.startswith("sch_")]
    assert len(sch_keys) == 10, f"Expected 10 school filters, got {len(sch_keys)}: {sch_keys}"
    print("PASS test_school_count")


if __name__ == "__main__":
    test_school_filters_present()
    test_school_filters_in_all_filters()
    test_school_matcher_kind()
    test_school_name_values()
    test_school_count()
    print("\nAll 5 tests passed.")
