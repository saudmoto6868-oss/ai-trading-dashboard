"""SMT on synthetic shapes: same-direction pair, INVERSE pair (e.g. EURUSD vs the dollar index), no-correlation guard, daily alignment."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from modules import smt

n = 125
rng = np.random.RandomState(3)
def frame(path, start="2026-03-02", freq="1h", noise=.05):
    c = np.interp(np.arange(n), *zip(*path)) + rng.randn(n) * noise
    o = np.r_[c[0], c[:-1]]; h = np.maximum(o, c) + .25 + abs(rng.randn(n)) * .02; l = np.minimum(o, c) - .25 - abs(rng.randn(n)) * .02
    return pd.DataFrame({"time": pd.date_range(start, periods=n, freq=freq), "open": o, "high": h, "low": l, "close": c, "volume": 0.0})

A_path = [(0, 120), (35, 110), (70, 100), (95, 112), (115, 95), (124, 106)]     # A: 2nd low (95) is LOWER than the 1st (100)
B_path = [(0, 120), (35, 110), (70, 100), (95, 112), (115, 101), (124, 108)]    # peer: 2nd low HOLDS above the 1st (refuses to confirm)
A, B = frame(A_path), frame(B_path)

# 1) same-direction pair
s1 = smt.smt_signals(A, B, "PEER")
assert any(x["direction"] == "bullish" and x["key"] == "smt" for x in s1), s1

# 2) inverse pair: the peer is the mirror image (200 - price) -> after mirroring it is the same story
Bi = B.copy()
for c in ("open", "close"): Bi[c] = 200 - B[c]
Bi["high"], Bi["low"] = 200 - B["low"], 200 - B["high"]
s2 = smt.smt_signals(A, Bi, "DXY", inverse=True)
assert any(x["direction"] == "bullish" and x["key"] == "smt" for x in s2), s2
# ...and the same mirrored peer WITHOUT inverse=True is correctly ignored (negative correlation)
assert smt.smt_signals(A, Bi, "DXY", inverse=False) == []

# 3) decoupled peer (random walk) -> no signal
R = frame([(0, 100), (124, 100)], noise=1.5)
assert smt.smt_signals(A, R, "RND") == []

# 4) daily bars that start at different hours (forex 00:00 vs futures 22:00 the day before) are matched by calendar day
Ad = frame(A_path, freq="1D"); Bd = frame(B_path, freq="1D"); Bd["time"] = Bd["time"] - pd.Timedelta(hours=2)
assert len(smt._align(Ad, Bd)) >= 100
assert any(x["key"] == "smt" for x in smt.smt_signals(Ad, Bd, "PEER"))

# 5) pairs table: forex pairs reachable
assert ("Y:DX-Y.NYB", True) in smt.peers_of("Y:EURUSD=X") and ("Y:EURUSD=X", True) in smt.peers_of("Y:DX-Y.NYB")
print("smt inverse tests OK")
