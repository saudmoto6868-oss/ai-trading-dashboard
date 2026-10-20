"""Elliott school in the strategy lab: rule count on a clean impulse, the mirror, a broken wave 2, and the walk wiring (synthetic)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from modules import elliott_lab as el
from modules import strategy_lab as sl


def frame(path, n=None):
    """path = [(bar, price)] turning points; linear legs with small noise."""
    n = n or path[-1][0] + 1
    rng = np.random.default_rng(1)
    c = np.interp(np.arange(n), *zip(*path)) + rng.normal(0, .08, n)
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + .15; l = np.minimum(o, c) - .15
    return pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="1h"), "open": o, "high": h, "low": l, "close": c, "volume": 1.0})

# clean bull: 100 -> 120 (w1) -> 110 (w2) -> 150 (w3) -> 140 (w4); the window ends 4 bars after the wave-4 low (zig-zag confirms late)
bull = frame([(0, 105), (5, 100), (30, 120), (50, 110), (80, 150), (100, 140), (104, 141)])
s = el.elliott_signals(bull)
assert any(x["key"] == "ew_r3_d1" and x["direction"] == "bullish" for x in s), s

# mirror (bear): same shape flipped around 200
bear = bull.copy()
for c_ in ("open", "close"): bear[c_] = 200 - bull[c_]
bear["high"], bear["low"] = 200 - bull["low"], 200 - bull["high"]
s2 = el.elliott_signals(bear)
assert any(x["key"] == "ew_r3_d1" and x["direction"] == "bearish" for x in s2), s2

# wave 2 below the wave-1 start (100 -> 95): rule R1 fails -> at most 2 rules
broken = frame([(0, 105), (5, 100), (30, 120), (50, 95), (80, 150), (100, 140), (104, 141)])
s3 = el.elliott_signals(broken)
assert not any(x["key"] == "ew_r3_d1" for x in s3), s3
assert el.impulse_rules([100, 120, 95, 150, 140], True) == 2   # R1 fails; R2 and R3 hold

# walk wiring: Elliott keys reach the lab events and carry a school
assert sl.SCHOOL["ew_r3_d1"] == "Elliott wave" and sl.SCHOOL["ew_r2_d2"] == "Elliott wave"
rng = np.random.default_rng(4); n = 900
c = 100 + np.cumsum(np.sign(np.sin(np.arange(n) / 17.0)) * 1.1 + rng.normal(0, .4, n))
df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="1h"), "open": c, "high": c + .6, "low": c - .6, "close": c, "volume": rng.uniform(10, 30, n)})
ev, _ = sl.walk(df, "1h", stride=4)
assert any(e["key"].startswith("ew_r") for e in ev), "no Elliott events in the walk"
print("ok elliott lab", sum(e["key"].startswith("ew_r") for e in ev), "events")
