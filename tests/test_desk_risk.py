"""Order Flow Desk risk manager (modules/desk_risk.py). Plain script: python3 tests/test_desk_risk.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.desk_risk import DeskDay, DeskRules, position_size, reward_risk


def test_size_base_quarter_percent_default():
    s = position_size(10_000, entry=100, stop=99)
    assert abs(s["qty"] - 25) < 1e-9 and abs(s["risk_amount"] - 25) < 1e-9
    print("ok test_size_base_quarter_percent_default")


def test_a_plus_step_up_requires_validated_30_trade_sample():
    base = position_size(10000, 100, 99, grade="A+", validation_n=29, validation_passed=True)
    tier = position_size(10000, 100, 99, grade="A+", validation_n=30, validation_passed=True)
    bad = position_size(10000, 100, 99, grade="A+", validation_n=50, validation_passed=False)
    other = position_size(10000, 100, 99, grade="A", validation_n=50, validation_passed=True)
    assert base["risk_pct"] == 0.25 and base["risk_amount"] == 25
    assert tier["risk_pct"] == 0.5 and tier["risk_amount"] == 50
    assert bad["risk_pct"] == other["risk_pct"] == 0.25
    # Integer-valued numeric counts (including 30.0) match JavaScript; strings/fractions/bools fail closed.
    numeric_float = position_size(10000, 100, 99, grade="A+", validation_n=30.0, validation_passed=True)
    assert numeric_float["risk_pct"] == 0.5 and numeric_float["risk_amount"] == 50
    for invalid_n in ("30", 30.9, True, float("nan"), float("inf")):
        rejected = position_size(10000, 100, 99, grade="A+", validation_n=invalid_n, validation_passed=True)
        assert rejected["risk_pct"] == 0.25, (invalid_n, rejected)
    print("ok test_a_plus_step_up_requires_validated_30_trade_sample")


def test_day_guard_uses_same_automatic_tier():
    base_day = DeskDay(10_000)
    ok, why = base_day.check("BTC", "long", 100, 99, 102, 50)
    assert not ok and any("0.25%" in reason for reason in why), why

    qualified_day = DeskDay(10_000)
    ok, why = qualified_day.check("BTC", "long", 100, 99, 102, 50,
                                  grade="A+", validation_n=30, validation_passed=True)
    assert ok, why
    print("ok test_day_guard_uses_same_automatic_tier")


def test_size_point_value_and_step_rounds_down():
    s = position_size(50_000, entry=5000, stop=4990, point_value=50, qty_step=1)   # 125 base budget / 500 per contract
    assert s["qty"] == 0, s                                   # never rounds up past the cap
    s = position_size(250_000, entry=5000, stop=4990, point_value=50, qty_step=1)  # 625 base budget / 500 = 1.25 -> 1
    assert s["qty"] == 1 and s["actual_risk_pct"] <= 0.25
    print("ok test_size_point_value_and_step_rounds_down")


def test_reward_risk_both_sides():
    assert reward_risk(100, 99, 102) == 2.0
    assert reward_risk(100, 101, 97) == 3.0
    assert reward_risk(100, 99, 98) < 0
    print("ok test_reward_risk_both_sides")


def test_three_stops_lock_the_day():
    d = DeskDay(10_000)
    for _ in range(3):
        d.record(-10)
    ok, why = d.check("BTC", "long", 100, 99, 103, 50)
    assert not ok and any("3 stops" in w for w in why), why
    print("ok test_three_stops_lock_the_day")


def test_daily_cap_locks_and_limits_last_trade():
    d = DeskDay(10_000)                       # cap 200
    d.record(-90, stopped=True)
    d.record(-90, stopped=True)               # 180 lost, 20 left
    ok, why = d.check("ETH", "short", 100, 101, 97, 25)
    assert not ok and any("left of today's cap" in w for w in why), why
    ok, _ = d.check("ETH", "short", 100, 101, 97, 20)
    assert ok
    d.record(-20)
    assert d.lock_reason() is not None
    print("ok test_daily_cap_locks_and_limits_last_trade")


def test_wins_do_not_count_as_stops_and_refill_budget():
    d = DeskDay(10_000)
    d.record(-150)
    d.record(+100)
    assert d.stops == 1 and abs(d.remaining_budget() - 150) < 1e-9
    print("ok test_wins_do_not_count_as_stops_and_refill_budget")


def test_duplicate_rr_and_per_trade_cap():
    d = DeskDay(10_000)
    d.open("XAU", "long")
    ok, why = d.check("xau", "LONG", 100, 99, 101.5, 60)
    assert not ok
    assert any("already open" in w for w in why)
    assert any("reward:risk" in w for w in why)
    assert any("per-trade cap" in w for w in why)
    d.record(+5, "XAU", "long")
    ok, why = d.check("XAU", "long", 100, 99, 102, 50,
                     grade="A+", validation_n=30, validation_passed=True)
    assert ok, why
    print("ok test_duplicate_rr_and_per_trade_cap")


def test_default_rules_are_fixed_quarter_percent():
    r = DeskRules()
    s = position_size(10_000, 100, 99)
    assert abs(s["qty"] - 25) < 1e-9
    ok, _ = DeskDay(10_000, rules=r).check("BTC", "long", 100, 99, 102, 25)
    assert ok
    ok, _ = DeskDay(10_000, rules=r).check("BTC", "long", 100, 99, 102, 50)
    assert not ok
    print("ok test_default_rules_are_fixed_quarter_percent")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
