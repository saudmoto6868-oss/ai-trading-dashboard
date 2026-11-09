"""GEX levels (modules/gex.py) on a synthetic chain. Plain script: python3 tests/test_gex.py
Mock data only - not checked against a live Cboe chain."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from modules import gex

TODAY = pd.Timestamp("2026-11-09")
EXP = pd.Timestamp("2026-11-20")


def _chain(rows):
    return pd.DataFrame([{"expiry": EXP, "type": t, "strike": k, "oi": oi, "iv": iv, "gamma": None}
                         for t, k, oi, iv in rows])


def test_bs_gamma_peaks_at_the_money():
    g = gex.bs_gamma(100, np.array([80, 100, 120]), 30 / 365, 0.2)
    assert g[1] > g[0] and g[1] > g[2] and (g > 0).all()
    print("ok test_bs_gamma_peaks_at_the_money")


def test_walls():
    ch = _chain([("C", 105, 5000, 0.2), ("C", 110, 20000, 0.2), ("C", 100, 1000, 0.2),
                 ("P", 95, 3000, 0.2), ("P", 90, 15000, 0.25), ("P", 100, 500, 0.2)])
    lv = gex.levels(ch, 100, TODAY)
    assert lv["call_wall"] in (105.0, 110.0)
    assert lv["put_wall"] in (90.0, 95.0)
    tbl = gex.by_strike(ch, 100, TODAY)
    assert (tbl.call_gex >= 0).all() and (tbl.put_gex <= 0).all()
    print("ok test_walls", lv["call_wall"], lv["put_wall"])


def test_gamma_flip_between_put_and_call_mass():
    # heavy puts below, heavy calls above -> total GEX negative low, positive high; flip in between
    ch = _chain([("P", 90, 30000, 0.2), ("P", 95, 20000, 0.2), ("C", 105, 20000, 0.2), ("C", 110, 30000, 0.2)])
    f = gex.gamma_flip(ch, 100, TODAY, width=0.2)
    assert f is not None and 92 < f < 108, f
    print("ok test_gamma_flip_between_put_and_call_mass", round(f, 2))


def test_no_flip_when_only_calls():
    ch = _chain([("C", 100, 1000, 0.2), ("C", 105, 1000, 0.2)])
    assert gex.gamma_flip(ch, 100, TODAY) is None
    lv = gex.levels(ch, 100, TODAY)
    assert lv["regime"] == "positive" and lv["put_wall"] is None
    print("ok test_no_flip_when_only_calls")


def test_expired_and_zero_oi_dropped_iv_percent_fixed():
    ch = pd.DataFrame([
        {"expiry": pd.Timestamp("2026-11-01"), "type": "C", "strike": 100, "oi": 9e9, "iv": 0.2, "gamma": None},
        {"expiry": EXP, "type": "P", "strike": 100, "oi": 0, "iv": 0.2, "gamma": None},
        {"expiry": EXP, "type": "C", "strike": 100, "oi": 10, "iv": 20.0, "gamma": None},   # 20 = 20 %
    ])
    lv = gex.levels(ch, 100, TODAY)
    assert lv["n_contracts"] == 1 and lv["call_wall"] == 100.0
    a = gex.by_strike(ch, 100, TODAY).net_gex.sum()
    ch.loc[2, "iv"] = 0.2
    b = gex.by_strike(ch, 100, TODAY).net_gex.sum()
    assert abs(a - b) < 1e-6 * abs(b)
    print("ok test_expired_and_zero_oi_dropped_iv_percent_fixed")


def test_feed_gamma_used_when_present():
    ch = _chain([("C", 100, 100, 0.2)])
    ch["gamma"] = 0.05
    tbl = gex.by_strike(ch, 100, TODAY)
    assert abs(tbl.call_gex.iloc[0] - 0.05 * 100 * 100 * 100 * 100 * 0.01) < 1e-6
    print("ok test_feed_gamma_used_when_present")


def test_empty_chain():
    lv = gex.levels(_chain([("C", 100, 0, 0.2)]), 100, TODAY)
    assert lv["call_wall"] is None and lv["n_contracts"] == 0
    print("ok test_empty_chain")


def test_mult_scales_linearly():
    ch = _chain([("C", 100, 100, 0.2), ("P", 95, 50, 0.2)])
    a, b = gex.by_strike(ch, 100, TODAY).net_gex.sum(), gex.by_strike(ch, 100, TODAY, mult=1).net_gex.sum()
    assert abs(a - 100 * b) < 1e-6 * abs(a)
    assert gex.levels(ch, 100, TODAY, mult=1)["call_wall"] == gex.levels(ch, 100, TODAY)["call_wall"]
    print("ok test_mult_scales_linearly")


def test_whole_number_iv_percent():
    ch = _chain([("C", 105, 100, 50), ("P", 95, 100, 50)])   # Deribit sends mark_iv as 50 (percent, int)
    lv = gex.levels(ch, 100, TODAY, mult=1)
    assert lv["call_wall"] == 105.0 and lv["put_wall"] == 95.0
    print("ok test_whole_number_iv_percent")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
