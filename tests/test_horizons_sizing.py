"""Brain plans use the shared deterministic risk policy."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import horizons as H

PLAN = {"symbol": "BTC-USDT", "horizon": "swing", "tf": "4h", "direction": "bullish", "grade": "A+",
        "entry": 100.0, "stop": 98.0, "tps": [104.0, 106.0], "move_points": 600, "rr1": 2.0,
        "schools": ["SMC", "ICT", "Elliott", "Classic"], "confluence": {"n": 3, "of": 3},
        "exit": {"text_ar": "x", "text_en": "y"}}


def test_sizing_base_quarter_percent():
    s = H.sizing(PLAN, equity=10000)
    assert s["qty"] == 12.5 and s["risk_amount"] == 25 and s["risk_pct"] == 0.25
    os.environ["DESK_EQUITY"] = "20000"
    try:
        assert H.sizing(PLAN)["qty"] == 25
    finally:
        del os.environ["DESK_EQUITY"]
    assert H.sizing(dict(PLAN, stop=100.0)) is None and H.sizing({"entry": 1}) is None
    print("ok test_sizing_base_quarter_percent")


def test_sizing_a_plus_validated_tier():
    s = H.sizing(dict(PLAN, validation_n=30, validation_passed=True), equity=10000)
    assert s["qty"] == 25 and s["risk_amount"] == 50 and s["risk_pct"] == 0.5
    print("ok test_sizing_a_plus_validated_tier")


def test_format_plan_shows_base_size():
    ar, en = H.format_plan(PLAN), H.format_plan(PLAN, ar=False)
    assert "الحجم 12.5" in ar and "0.25% من 10,000$" in ar
    assert "Size 12.5" in en and "risk 25$ = 0.25% of 10,000$" in en
    assert "Size" not in H.format_plan(dict(PLAN, stop=100.0), ar=False)
    print("ok test_format_plan_shows_base_size")


if __name__ == "__main__":
    test_sizing_base_quarter_percent()
    test_sizing_a_plus_validated_tier()
    test_format_plan_shows_base_size()
