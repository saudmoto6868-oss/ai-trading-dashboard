"""Tests for modules/pipeline_report.py — synthetic data only."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.pipeline_report import (
    tier_distribution, gate_passed, top_by_avgr,
    chain_breakdown, fmt_r, _gap_flag, TIER_ORDER
)

ROWS = [
    # edge candidate: n>=100, t>3, avgR>0, IS>0, OOS>0
    {"key": "level", "tf": "1h", "side": "all", "n": 500, "win": 0.6,
     "avgR": 0.08, "t": 4.5, "is_avgR": 0.09, "oos_avgR": 0.07, "edge": "edge"},
    # positive, overfit (IS-OOS gap > 0.05)
    {"key": "macd_div", "tf": "1d", "side": "all", "n": 67, "win": 0.55,
     "avgR": 0.41, "t": 2.1, "is_avgR": 0.50, "oos_avgR": 0.30, "edge": ""},
    # negative
    {"key": "bad_signal", "tf": "15m", "side": "all", "n": 200, "win": 0.35,
     "avgR": -0.08, "t": -2.0, "is_avgR": -0.07, "oos_avgR": -0.09, "edge": ""},
    # off (n>=300, avgR<=-0.06)
    {"key": "useless", "tf": "all", "side": "all", "n": 350, "win": 0.30,
     "avgR": -0.10, "t": -3.0, "is_avgR": -0.09, "oos_avgR": -0.11, "edge": "off"},
    # weak (n<30)
    {"key": "rare", "tf": "4h", "side": "all", "n": 10, "win": 0.70,
     "avgR": 0.50, "t": 1.0, "is_avgR": None, "oos_avgR": None, "edge": ""},
    # neutral
    {"key": "neutral_key", "tf": "1h", "side": "all", "n": 80, "win": 0.48,
     "avgR": 0.01, "t": 0.5, "is_avgR": 0.02, "oos_avgR": 0.00, "edge": ""},
]


def test_tier_distribution():
    dist = tier_distribution(ROWS)
    assert dist["edge"] == 1, f"expected 1 edge, got {dist['edge']}"
    assert dist["off"] == 1, f"expected 1 off, got {dist['off']}"
    assert dist["weak"] == 1, f"expected 1 weak, got {dist['weak']}"
    assert dist["negative"] == 1, f"expected 1 negative"
    assert sum(dist.values()) == len(ROWS), "tier counts must sum to total rows"
    print("✅ tier_distribution OK")


def test_gate_passed():
    passed = gate_passed(ROWS)
    assert len(passed) == 1, f"only 'level' should pass strict gate, got {[r['key'] for r in passed]}"
    assert passed[0]["key"] == "level"
    print("✅ gate_passed OK")


def test_top_by_avgr():
    top = top_by_avgr(ROWS, n_top=5)
    # 'rare' excluded (n<30), 'level' should be top
    keys = [r["key"] for r in top]
    assert "rare" not in keys, "rare (n<30) must be excluded"
    # macd_div has higher avgR (0.41) than level (0.08) even though level passes the gate
    assert top[0]["key"] == "macd_div", f"macd_div has highest avgR, got {top[0]['key']}"
    assert "level" in keys, "level must be in top list"
    print("✅ top_by_avgr OK")


def test_gap_flag():
    overfit_row = {"is_avgR": 0.50, "oos_avgR": 0.30}  # gap = 0.20 > 0.05
    ok_row = {"is_avgR": 0.08, "oos_avgR": 0.07}        # gap = 0.01
    none_row = {"is_avgR": None, "oos_avgR": None}
    assert "overfit" in _gap_flag(overfit_row)
    assert _gap_flag(ok_row) == ""
    assert _gap_flag(none_row) == ""
    print("✅ gap_flag OK")


def test_fmt_r():
    assert fmt_r(0.082) == "+0.082R"
    assert fmt_r(-0.05) == "-0.050R"
    assert fmt_r(None) == "—"
    print("✅ fmt_r OK")


def test_chain_breakdown_empty():
    # no grade/layer fields → empty breakdown
    result = chain_breakdown(ROWS)
    assert result["grades"] == {}, "no grade fields → empty grades"
    assert result["layers"] == {}, "no layer fields → empty layers"
    print("✅ chain_breakdown (empty) OK")


def test_chain_breakdown_with_data():
    rows_with_chain = [
        {"key": "a", "grade": "A+++", "avgR": 0.10, "reg": True, "htf": True},
        {"key": "b", "grade": "A+",   "avgR": 0.05, "reg": False, "htf": True},
        {"key": "c", "grade": "A+++", "avgR": 0.08, "reg": True, "htf": False},
    ]
    result = chain_breakdown(rows_with_chain)
    assert "A+++" in result["grades"]
    assert result["grades"]["A+++"]["n"] == 2
    assert "reg" in result["layers"]
    assert result["layers"]["reg"]["with"] == 2
    assert result["layers"]["reg"]["without"] == 1
    print("✅ chain_breakdown (with data) OK")


if __name__ == "__main__":
    test_tier_distribution()
    test_gate_passed()
    test_top_by_avgr()
    test_gap_flag()
    test_fmt_r()
    test_chain_breakdown_empty()
    test_chain_breakdown_with_data()
    print("\nAll pipeline_report tests passed ✅")
