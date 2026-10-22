"""Checks for modules/lab_holdout.py: the holdout cut, the judge's gate, and that run() uses only candles older than the lab window."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import lab_holdout as H  # noqa: E402


def _df(n):
    t = pd.date_range("2018-01-01", periods=n, freq="D")
    c = 100 + np.cumsum(np.random.default_rng(1).normal(0, 1, n))
    return pd.DataFrame({"time": t, "open": c, "high": c + 1, "low": c - 1, "close": c, "volume": 1.0})


def test_cut_excludes_the_lab_window_and_splits_in_time():
    df = _df(2000)
    a, b = H.holdout_halves(df)
    assert len(a) + len(b) == 2000 - 900 and a["time"].iloc[-1] < b["time"].iloc[0]
    assert b["time"].iloc[-1] < df["time"].iloc[-900]            # nothing from the lab's newest 900 candles
    assert H.holdout_halves(_df(1200)) is None and H.holdout_halves(_df(800)) is None   # holdout shorter than the minimum


def test_judge_gate():
    rng = np.random.default_rng(2)
    good = [(float(x), 0.0) for x in rng.choice([1.5, -1.0], 400, p=[0.6, 0.4])]   # avg +0.5R vs a flat baseline
    j = H.judge({"h1": good[:200], "h2": good[200:]})
    assert j["n"] == 400 and j["pass"] and j["t_vs_random"] > 3 and j["h1"]["net_avgR"] > 0 and j["h2"]["net_avgR"] > 0
    bad = [(float(x), 0.0) for x in rng.choice([1.5, -1.0], 400, p=[0.4, 0.6])]    # exactly the random-walk break-even win rate
    assert not H.judge({"h1": bad[:200], "h2": bad[200:]})["pass"]
    one_half = {"h1": good[:200], "h2": [(-1.0, 0.0)] * 200}                        # good first half, losing second half
    assert not H.judge(one_half)["pass"]
    assert not H.judge({"h1": good[:30], "h2": good[30:60]})["pass"]                # n < 100


def test_run_reads_only_old_candles():
    seen = []
    def fake_fetch(sym, tf, bars):
        return _df(2200)
    import modules.strategy_lab as SL
    orig = SL.walk
    def spy(df, tf, stride=4, seed=0, peers=()):
        seen.append(df["time"].iloc[-1]); return [], []
    SL.walk = spy
    try:
        out = H.run(["A-USDT"], fetch=fake_fetch, log=lambda *_: None)
    finally:
        SL.walk = orig
    cut = _df(2200)["time"].iloc[-900]
    assert seen and all(t < cut for t in seen), (seen, cut)
    assert out["result"]["n"] == 0 and not out["result"]["pass"]


if __name__ == "__main__":
    test_cut_excludes_the_lab_window_and_splits_in_time(); test_judge_gate(); test_run_reads_only_old_candles(); print("ok lab_holdout")
