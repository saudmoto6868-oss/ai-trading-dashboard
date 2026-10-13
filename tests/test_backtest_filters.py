"""Plumbing test on SYNTHETIC candles (random walk): proves the on/off switch restores env and the table renders.
It says nothing about real performance - that needs OKX data (python -m modules.backtest_filters)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from modules import backtest_filters as bf

rng = np.random.RandomState(1); n = 420
c = 100 * np.exp(np.cumsum(rng.randn(n) * .004)); o = np.r_[c[0], c[:-1]]
h = np.maximum(o, c) * (1 + abs(rng.randn(n)) * .002); l = np.minimum(o, c) * (1 - abs(rng.randn(n)) * .002)
df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="1h"), "open": o, "high": h, "low": l, "close": c, "volume": rng.rand(n) * 100 + 10})
os.environ["SIGF_OB_VOL"] = "1"
res = bf.compare(df, keys=("donch", "ob"), stride=6)
assert os.environ["SIGF_OB_VOL"] == "1" and "SIGF_STRICT_SMC" not in os.environ
assert set(res["ob"]) == {"on", "off"} and res["ob"]["on"]["n"] <= res["ob"]["off"]["n"], res["ob"]
t = bf.table({"SYNTH|1h": res}); assert "| donch | off |" in t and "| ob | on |" in t
print(t); print("backtest_filters plumbing OK")
