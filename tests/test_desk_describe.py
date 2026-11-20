"""Desk description helper: returns the same labels as the chart rules, never a direction (synthetic candles)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from modules import desk_describe as dd

# too few bars: nothing
assert dd.describe(pd.DataFrame({"high": [1.0] * 5, "low": [0.9] * 5}))["elliott_shape"] is None

# a clear zig-zag path gives pivots and a shape label (or None), never a direction key
pts = [(0, 100), (20, 120), (30, 108), (45, 126), (60, 118), (75, 96), (84, 100)]
xs, ys = zip(*pts)
c = np.interp(np.arange(xs[-1] + 1), xs, ys)
df = pd.DataFrame({"high": c + 0.6, "low": c - 0.6, "close": c})
r = dd.describe(df)
assert set(r) == {"elliott_shape", "elliott_pivots", "harmonic", "harmonic_forming"}
assert r["elliott_pivots"] >= 3
assert "side" not in r and "direction" not in r
print("test_desk_describe: OK", r["elliott_shape"], r["harmonic"])
