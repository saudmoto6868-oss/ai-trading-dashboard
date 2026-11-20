"""Tests for modules/signal_compare.py (plain script). The last check reads the committed real-candle lab file."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import signal_compare as sc  # noqa: E402


def _row(**kw):
    base = {"key": "x", "school": "SMC / ICT", "tf": "all", "side": "all", "n": 200, "win": 40.0, "avgR": 0.3,
            "t": 3.5, "is_avgR": 0.2, "oos_avgR": 0.4, "edge": True}
    base.update(kw)
    return base


def test_net_uses_lab_cost_when_missing():
    assert sc.net_r(_row(avgR=0.3)) == 0.2
    assert sc.net_r(_row(avgR=0.3, net=0.05)) == 0.05, "an explicit net field wins"
    assert sc.net_r(_row(avgR=None)) is None
    print("ok net = avgR - 0.1 unless a net field is given")


def test_owner_bar_needs_all_conditions():
    assert sc.verdict(_row()) is True
    assert sc.verdict(_row(n=99)) is False, "n must be >= 100"
    assert sc.verdict(_row(t=3.0)) is False, "t must be > 3"
    assert sc.verdict(_row(oos_avgR=-0.01)) is False, "OOS must be positive"
    assert sc.verdict(_row(avgR=0.1)) is False, "net must be positive after cost"
    assert sc.verdict(_row(t=None)) is False, "missing numbers never pass"
    print("ok owner bar: n, t, both halves and net after cost")


def test_compare_keeps_pooled_rows_only_and_sorts_by_net():
    rows = [_row(key="a", avgR=0.1), _row(key="b", avgR=0.5), _row(key="c", tf="1h", avgR=0.9),
            _row(key="d", side="rr1.5", avgR=0.9)]
    out = sc.compare(rows)
    assert [r["key"] for r in out] == ["b", "a"]
    print("ok compare: pooled rows only, sorted by net R")


def test_committed_lab_every_lab_yes_still_checked_against_cost():
    """The lab's YES does not imply the owner bar: any row the lab flags but with net <= 0 must fail here.
    (Holds for whatever the committed lab file says today, so this test does not hard-code one run.)"""
    rows = sc.compare(sc.load())
    assert rows, "lab file has pooled rows"
    for r in rows:
        if r["lab_edge"] and (r["net"] is None or r["net"] <= 0):
            assert r["owner_pass"] is False, r
    print("ok committed lab: no row passes the owner bar unless net is positive after cost")


if __name__ == "__main__":
    test_net_uses_lab_cost_when_missing()
    test_owner_bar_needs_all_conditions()
    test_compare_keeps_pooled_rows_only_and_sorts_by_net()
    test_committed_lab_every_lab_yes_still_checked_against_cost()
    print("signal_compare: all ok")
