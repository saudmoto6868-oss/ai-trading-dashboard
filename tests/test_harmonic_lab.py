"""The strategy lab must find completed harmonic patterns. The lab used max_age=2, but a zig-zag pivot is only confirmed 3 bars after it (harmonic.zigzag n=3),
so a completed pattern (D pivot) is first visible 3 bars after D: with max_age=2 the lab produced ZERO harmonic rows on 61,000 real signals (2026-11-01 run).
Run: PYTHONPATH=. python tests/test_harmonic_lab.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from modules import strategy_lab as sl  # noqa: E402
from modules.harmonic import find_harmonics  # noqa: E402

X, A = 100.0, 110.0
B = A - 0.618 * (A - X); C = B + 0.5 * (A - B); D = A - 0.786 * (A - X)      # an exact bullish Gartley
leg = lambda pts, k=20: [v for a, b in zip(pts[:-1], pts[1:]) for v in np.linspace(a, b, k, endpoint=False)]
one = list(np.linspace(108, X, 20, endpoint=False)) + leg([X, A, B, C, D]) + [D + 0.3 * k for k in range(0, 9)]
c = np.array(one)
df = pd.DataFrame({"open": c, "high": c + 0.05, "low": c - 0.05, "close": c, "volume": 1.0})
dpos = 100   # index of the D pivot
rows = {}
for age in (2, sl.HARM_AGE):
    for after in range(0, 9):
        w = df.iloc[:dpos + after + 1].reset_index(drop=True)
        rows[(age, after)] = [p["name"] for p in find_harmonics(w, max_age=age) if not p["forming"]]
assert all(not rows[(2, a)] for a in range(9)), "max_age=2 can never see a completed pattern (the bug)"
assert rows[(sl.HARM_AGE, 3)] == ["Gartley"] and rows[(sl.HARM_AGE, 5)] == ["Gartley"], rows
assert not rows[(sl.HARM_AGE, 2)] and not rows[(sl.HARM_AGE, 6)], "visible 3..5 bars after D only"
assert sl.HARM_AGE >= 5
# the real lab walk emits harm_* events on candles that contain such patterns (8 cycles of the same shape, 1h)
cyc = np.concatenate([c + 3 * i for i in range(10)]) * 1.0
big = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=len(cyc), freq="1h"), "open": cyc, "high": cyc + 0.1, "low": cyc - 0.1, "close": cyc, "volume": 10.0})
ev, _ = sl.walk(big, "1h", stride=1)
keys = {e["key"] for e in ev}
assert "harm_gartley" in keys, sorted(k for k in keys if k.startswith("harm"))
print("ok harmonic lab: found", sorted(k for k in keys if k.startswith("harm")))
