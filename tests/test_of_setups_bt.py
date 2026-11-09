"""Order Flow Desk setups backtest engine (modules/of_setups_bt.py) on synthetic trades. Plain script.
Mock data only: it checks the mechanics (bars, footprint, no look-ahead, stop-first, costs), not whether a setup works."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from modules import of_setups_bt as B

T0 = 1793577600000   # 2026-11-02 00:00 UTC


def trades(n_bars=600, sec=300, seed=7):
    r = np.random.default_rng(seed); rows = []; p = 100.0
    for b in range(n_bars):
        for k in range(20):
            p = max(1.0, p + r.normal(0, 0.05))
            rows.append({"t": T0 + b * sec * 1000 + k * 1000, "p": round(p, 2), "q": float(r.integers(1, 5)), "buyer_maker": bool(r.random() < 0.5)})
    return pd.DataFrame(rows)


def test_bars_delta_and_footprint():
    tr = pd.DataFrame([{"t": T0, "p": 100.0, "q": 2, "buyer_maker": False}, {"t": T0 + 1000, "p": 100.0, "q": 1, "buyer_maker": True},
                       {"t": T0 + 2000, "p": 100.5, "q": 3, "buyer_maker": False}, {"t": T0 + 300_000, "p": 99.0, "q": 4, "buyer_maker": True}])
    b = B.bars(tr, 300, tick=0.5)
    assert len(b) == 2 and b.delta.iloc[0] == 2 - 1 + 3 and b.delta.iloc[1] == -4
    assert b.fp.iloc[0] == {100.0: [1.0, 2.0], 100.5: [0.0, 3.0]} and (b.o.iloc[0], b.h.iloc[0], b.c.iloc[0]) == (100.0, 100.5, 100.5)
    print("ok test_bars_delta_and_footprint")


def test_signals_do_not_look_ahead():
    df = B.bars(trades(), 300)
    s_all = B.signals(df)
    cut = 400
    s_cut = B.signals(df.iloc[:cut].copy())
    a = s_all[s_all.i < cut - 1].reset_index(drop=True)
    b = s_cut[s_cut.i < cut - 1].reset_index(drop=True)
    pd.testing.assert_frame_equal(a, b)              # adding future bars never changes a past signal
    print("ok test_signals_do_not_look_ahead", len(s_all), dict(s_all.setup.value_counts()))


def test_stacked_imbalance_detected():
    df = B.bars(trades(200), 300)
    fp = {100.0 + 0.01 * k: [1.0, 5.0] for k in range(4)}   # 4 rows of 5:1 buying
    df.at[150, "fp"] = fp
    s = B.signals(df, level=False)
    assert ((s.i == 150) & (s.setup == "stacked") & (s.dir == 1)).any()
    print("ok test_stacked_imbalance_detected")


def test_simulate_stop_first_and_costs():
    df = pd.DataFrame({"t": [T0 + i * 300_000 for i in range(40)], "o": [100.0] * 40, "h": [100.5] * 40, "l": [99.5] * 40, "c": [100.0] * 40,
                       "v": 1.0, "delta": 0.0, "fp": [{}] * 40})
    df.loc[31, ["h", "l"]] = [104.0, 96.0]               # touches both: the stop counts
    sig = pd.DataFrame([{"i": 30, "setup": "absorption", "dir": 1}])
    t = B.simulate(df, sig, stop_atr=1.0, rr=2.0, cost_r=0.1)
    assert len(t) == 1 and abs(t.R.iloc[0] - (-1.1)) < 1e-9, t
    df.loc[31, ["h", "l"]] = [104.0, 99.9]               # only the target
    t = B.simulate(df, sig, stop_atr=1.0, rr=2.0, cost_r=0.1)
    assert abs(t.R.iloc[0] - 1.9) < 1e-9
    print("ok test_simulate_stop_first_and_costs")


def test_report_says_not_evidence_and_dom_untestable():
    tr = pd.DataFrame([{"setup": "absorption", "dir": 1, "i": 1, "t": 0, "entry": 1, "R": 1.9}] * 5)
    rep = B.report(tr).set_index("setup")
    assert rep.loc["absorption", "n"] == 5 and rep.loc["absorption", "verdict"] == "not evidence (n < 30)"
    assert rep.loc["dom_reject", "verdict"].startswith("not testable")
    print("ok test_report_says_not_evidence_and_dom_untestable")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
