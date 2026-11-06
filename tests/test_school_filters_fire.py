"""The Radar 'School ·' filters must actually FIRE (found 2026-11-06: they matched sg['school'], a field no signal carried, so they never did). Synthetic series, no network."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from modules import chart_scan as C

rng = np.random.default_rng(5)
n = 400
c = 100 + np.cumsum(rng.normal(0, 1, n))
df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="1h"), "open": c, "high": c + .7, "low": c - .7, "close": c, "volume": rng.uniform(10, 30, n)})
seen = set()
for k in range(150, n, 10):
    fl, _ = C.strategy_flags(df.iloc[:k].reset_index(drop=True))
    seen |= {f for f in fl if f.startswith("sch_")}
assert {"sch_ict", "sch_trend", "sch_liq", "sch_fib", "sch_elliott"} <= seen, sorted(seen)
print("ok school filters fire:", sorted(seen))
