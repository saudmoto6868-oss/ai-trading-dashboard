"""Volatility-scaled swings in the lab (harm_vol_*, ew_*_v) keep the old fixed-swing behaviour unchanged."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np, pandas as pd
from modules.harmonic import vol_dev, find_harmonics, zigzag
from modules.elliott_lab import DEGREES, elliott_signals
from modules import strategy_lab as SL

def walk(p0, sg, n, seed):
    r = np.random.default_rng(seed); c = p0 * np.exp(np.cumsum(sg * r.standard_normal(n)))
    o = np.r_[p0, c[:-1]]; w = np.abs(sg * r.standard_normal(n)) * c * 0.5
    return pd.DataFrame({"open": o, "high": np.maximum(o, c) + w, "low": np.minimum(o, c) - w, "close": c, "volume": 1.0})

# 1. clamps: flat candles -> lower bound, huge candles -> upper bound, and a calm 5m gold walk is far below the old 1.2 %
flat = pd.DataFrame({"high": [1.0]*50, "low": [1.0]*50, "close": [1.0]*50})
assert vol_dev(flat, 4, .002, .04) == .002
wide = pd.DataFrame({"high": [2.0]*50, "low": [1.0]*50, "close": [1.0]*50})
assert vol_dev(wide, 4, .002, .04) == .04
gold5m = walk(4180, 0.0004, 500, 1)
assert 0.002 <= vol_dev(gold5m, 4, .002, .04) < 0.012

# 2. the old fixed-swing call is unchanged (default vol=False)
d = walk(82000, 0.004, 400, 2)
assert [p["name"] for p in find_harmonics(d, max_age=2)] == [p["name"] for p in find_harmonics(d, max_age=2, dev=0.012)]

# 3. volatility-scaled harmonic and Elliott run on the same window without errors, and give pivots on the calm walk
vz = zigzag(gold5m["high"].values, gold5m["low"].values, vol_dev(gold5m, 4, .002, .04), 3)
assert len(vz) > len(zigzag(gold5m["high"].values, gold5m["low"].values, 0.012, 3))
for k in range(5):
    find_harmonics(walk(100, 0.002, 300, 10 + k), max_age=2, vol=True)
    elliott_signals(walk(100, 0.002, 300, 20 + k))

# 4. registration: the new keys are in the lab's school map and the Elliott degree "v" is registered
assert "v" in DEGREES and DEGREES["v"] is None
assert "ew_r3_v" in SL.SCHOOL and "ew_r2_v" in SL.SCHOOL
assert "harm_vol_gartley" in SL.SCHOOL and "harm_vol_cypher_tight" in SL.SCHOOL
assert "harm_gartley" in SL.SCHOOL   # old keys still there
print("ok lab vol")
