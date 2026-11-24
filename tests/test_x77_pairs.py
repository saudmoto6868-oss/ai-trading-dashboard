"""X77 pair rule on hand-made per-bar keys (no detectors, no network). Run: python3 tests/test_x77_pairs.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research import x77_pairs as X  # noqa: E402

n = 300
c = 100 + np.linspace(0, 30, n)   # steady rise: long trades hit target
df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC"), "open": c, "high": c + 1, "low": c - 1,
                   "close": c, "volume": 1.0})
kb = {i: set() for i in range(150, n - 1)}
kb[160] = {("sweep", 1)}; kb[162] = {("ote", 1)}            # P1 within the 3-bar window -> fires at 162
kb[170] = {("sweep", 1)}; kb[174] = {("ote", 1)}            # too far apart -> no trade
kb[180] = {("sweep", 1), ("ote", -1)}                        # opposite directions -> no P1
kb[182] = {("sweep", 1), ("ote", 1)}; kb[184] = {("ote", 1)}  # fires at 182; 184 inside the 6-bar cooldown
kb[200] = {("level", -1), ("pa_pin", -1)}                    # P3 short
tr = X.pair_trades(df, kb)
p1 = [t for t in tr if t["pair"].startswith("P1")]
assert [t["i"] for t in p1] == [162, 182], p1
assert all(t["d"] == 1 for t in p1)
p3 = [t for t in tr if t["pair"].startswith("P3")]
assert [(t["i"], t["d"]) for t in p3] == [(200, -1)], p3
assert abs(p1[0]["r"] - (1.5 - X.L.COST_R)) < 1e-9, p1[0]   # rising market: long hits 1.5R, minus cost
s = X.stats(tr)
assert s["n"] == len(tr) and "t_day" in s
assert X.verdict_history({"n": 10}).startswith("KILLED")
assert X.verdict_history({"n": 50, "net_mean": 0.1, "half1": 0.1, "half2": -0.01}).startswith("KILLED")
assert X.verdict_history({"n": 50, "net_mean": 0.1, "half1": 0.1, "half2": 0.1}).startswith("SURVIVES")
print("x77_pairs: rule checks passed")
