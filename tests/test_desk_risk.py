"""Order Flow Desk risk manager (modules/desk_risk.py). Plain script: python3 tests/test_desk_risk.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.desk_risk import DeskDay, DeskRules, position_size, reward_risk


def test_size_quarter_percent():
    s = position_size(10_000, entry=100, stop=99)          # 0.25 % of 10k = 25, 1.0 per unit
    assert abs(s["qty"] - 25) < 1e-9 and abs(s["risk_amount"] - 25) < 1e-9
    print("ok test_size_quarter_percent")


def test_size_point_value_and_step_rounds_down():
    s = position_size(50_000, entry=5000, stop=4990, point_value=50, qty_step=1)   # 125 budget / 500 per contract
    assert s["qty"] == 0, s                                   # never rounds up past the cap
    s = position_size(500_000, entry=5000, stop=4990, point_value=50, qty_step=1)  # 1250 / 500 = 2.5 -> 2
    assert s["qty"] == 2 and s["actual_risk_pct"] <= 0.25
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
    ok, why = d.check("BTC", "long", 100, 99, 103, 25)
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
    ok, why = d.check("xau", "LONG", 100, 99, 101.5, 30)
    assert not ok
    assert any("already open" in w for w in why)
    assert any("reward:risk" in w for w in why)
    assert any("per-trade cap" in w for w in why)
    d.record(+5, "XAU", "long")
    ok, why = d.check("XAU", "long", 100, 99, 102, 25)
    assert ok, why
    print("ok test_duplicate_rr_and_per_trade_cap")


def test_custom_rules_half_percent():
    r = DeskRules(risk_pct=0.5)
    s = position_size(10_000, 100, 99, risk_pct=r.risk_pct)
    assert abs(s["qty"] - 50) < 1e-9
    ok, _ = DeskDay(10_000, rules=r).check("BTC", "long", 100, 99, 102, 50)
    assert ok
    print("ok test_custom_rules_half_percent")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
