"""Exit variants (RR target + break-even stop) in the strategy lab, on synthetic candles (no network)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from modules import strategy_lab as sl

# long, entry 100, stop 1 (stop_d=1)
hi = np.array([100, 101, 102.5, 103, 104]); lo = np.array([100, 100, 101, 102, 103]); cl = np.array([100, 101, 102, 103, 104])
assert sl._outcome(hi, lo, cl, 0, 1, 1.0, 4, rr=1.5) == 1.5          # target hit (102.5 >= 101.5)
# break-even: price reaches +1R (101) then falls back to entry (100) -> 0R instead of -1R
hi2 = np.array([100, 101.2, 100.6, 100.0]); lo2 = np.array([100, 100.5, 99.9, 98.5]); cl2 = np.array([100, 101, 100, 99.8])
assert sl._outcome(hi2, lo2, cl2, 0, 1, 1.0, 3, rr=2.0) == -1.0
assert sl._outcome(hi2, lo2, cl2, 0, 1, 1.0, 3, rr=2.0, be=True) == 0.0
# short side mirror
hi3 = np.array([100, 100.5, 101]); lo3 = np.array([100, 98.8, 98.7]); cl3 = np.array([100, 99, 98.8])
assert sl._outcome(hi3, lo3, cl3, 0, -1, 1.0, 2, rr=1.0) == 1.0
# variants are all present on a real walk
rng = np.random.default_rng(3)
import pandas as pd
n = 700; c = 100 + np.cumsum(rng.normal(0, .8, n))
df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="1h"), "open": c, "high": c + abs(rng.normal(0, .7, n)) + .2,
                   "low": c - abs(rng.normal(0, .7, n)) - .2, "close": c, "volume": rng.uniform(10, 30, n)})
ev, br = sl.walk(df, "1h", stride=8)
withv = [e for e in ev if e.get("var")]
assert withv and set(withv[0]["var"]) == set(sl.VARIANTS)
rows, conf, cfl = sl.summarize([("1h", "X", ev)], [("1h", "X", br)])
vr = [r for r in rows if r["school"] == "exit" and r["key"] == "*VAR*"]
assert len(vr) == len(sl.VARIANTS) and all(r["n"] == len(ev) for r in vr)
md = sl.report(rows, conf, cfl, {"built": 0, "symbols": ["X"], "tfs": ["1h"]})
assert "## Exit variants" in md
print("ok strategy exits", len(ev), "events")
