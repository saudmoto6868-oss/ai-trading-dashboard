"""Day plan exits in the weekly lab (strategy_lab VARIANTS pt_*): same entries, partial + trailing walk shared with day_plan.simulate_arrays. Synthetic, no network."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from modules import strategy_lab as sl
from modules import day_plan as D

pt = [n for n, v in sl.VARIANTS.items() if len(v) > 3]
assert set(pt) == {"pt_1.5_3", "pt_1.0_3", "pt_1.5_5", "trail_only"}, pt

# the lab's walk and the Day plan's simulate_exit agree on the same path (entry bar 0 = 100, stop 98, atr 1): path A of tests/test_day_plan.py
hi = np.array([100.2, 101, 103.2, 106.5, 108.0, 107.0]); lo = np.array([99.8, 99.5, 100.5, 103.0, 105.5, 105.0]); cl = np.array([100.0, 100.8, 103.0, 106.2, 107.0, 105.2])
r_lab = sl._outcome_pt(hi, lo, cl, 0, 1, 2.0, 1.0, 10, sl.VARIANTS["pt_1.5_5"])
ex = {"targets": [103.0, 110.0], "partial": {"at": 103.0, "fraction": 0.5}, "be_at": 2.0, "trail_atr": 1.5}
r_day = D.simulate_arrays(hi[1:], lo[1:], cl[1:], "bullish", 100.0, 98.0, ex, 1.0)["r"]
assert abs(r_lab - r_day) < 1e-9 and r_lab > 1.5, (r_lab, r_day)
# short mirror = the long on negated prices
assert abs(sl._outcome_pt(-lo, -hi, -cl, 0, -1, 2.0, 1.0, 10, sl.VARIANTS["pt_1.5_5"]) - r_lab) < 1e-9
# a straight loser is -1R in every variant
hl = np.array([100.1, 100.0, 97.0]); ll = np.array([99.9, 97.5, 96.0]); cc = np.array([100.0, 98.0, 96.5])
assert all(sl._outcome_pt(hl, ll, cc, 0, 1, 2.0, 1.0, 10, sl.VARIANTS[n]) == -1.0 for n in pt)
# trail_only (no partial): a run that fades gives back less than the fixed target would have given... but never below the stop (-1R) and never above tp3
rr = sl._outcome_pt(hi, lo, cl, 0, 1, 2.0, 1.0, 10, sl.VARIANTS["trail_only"])
assert -1.0 <= rr <= 5.0

# the lab walk on a random series produces every pt_* variant for every event, and the report rows exist
rng = np.random.default_rng(7)
n = 700
c = 100 + np.cumsum(rng.normal(0, 1, n))
df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="1h"), "open": c, "high": c + .6, "low": c - .6, "close": c, "volume": rng.uniform(10, 30, n)})
ev, _ = sl.walk(df, "1h", stride=4)
assert ev and all(set(pt) <= set(e["var"]) for e in ev), "pt_* variants missing from the events"
assert all(-1.0 <= e["var"][n] <= 5.0 for e in ev for n in pt)
print("ok exit lab:", len(ev), "events; pt_1.5_3 mean R", round(float(np.mean([e["var"]["pt_1.5_3"] for e in ev])), 3), "vs rr1.5", round(float(np.mean([e["var"]["rr1.5"] for e in ev])), 3), "(random walk, not evidence)")
