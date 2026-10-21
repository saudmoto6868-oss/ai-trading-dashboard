"""KPI strip numbers on hand-made trades (plain script, like the other tests)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import pandas as pd
from modules.kpi import breakdown, kpis

d = pd.DataFrame({"r": [2, -1, 2, -1, -1, 2, -1]})
k = kpis(d)
assert k["n"] == 7 and abs(k["win_rate"] - 3 / 7) < 1e-9
assert abs(k["profit_factor"] - 1.5) < 1e-9          # gross win 6 / gross loss 4
assert k["max_dd_r"] == -2.0                          # 3R peak, then 1R
assert k["evidence"]["badge"] == "not evidence"       # n < 100

rng = np.random.default_rng(1)
big = pd.DataFrame({"r": rng.normal(0.3, 1, 400), "symbol": ["BTC"] * 200 + ["ETH"] * 200})
assert kpis(big)["evidence"]["badge"] == "passes gate"
b = breakdown(big, "symbol")
assert list(b["symbol"]) and set(b["n"]) == {200}
assert kpis(pd.DataFrame({"r": []}))["n"] == 0
print("test_kpi: all passed")
