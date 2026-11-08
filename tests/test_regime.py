"""Market regime classifier on synthetic candles with a known shape (no market data). Run: PYTHONPATH=. python tests/test_regime.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from modules.regime import classify, REGIMES  # noqa: E402


def frame(close, spread=None, vol=None):
    vol = np.random.default_rng(9).uniform(80, 120, len(close)) if vol is None else vol
    close = np.asarray(close, float)
    sp = np.full(len(close), 0.4) if spread is None else np.asarray(spread, float)
    o = np.concatenate([[close[0]], close[:-1]])
    return pd.DataFrame({"open": o, "high": np.maximum(o, close) + sp, "low": np.minimum(o, close) - sp, "close": close,
                         "volume": np.asarray(vol, float)})


g = np.random.default_rng(3)
n = 200
trend = frame(100 * np.exp(np.cumsum(0.004 + g.normal(0, 0.003, n))), spread=np.full(n, 0.2), vol=g.uniform(80, 120, n))
assert classify(trend)["regime"] == "Trend", classify(trend)
chop = frame(100 + 0.6 * np.sin(np.arange(n) / 2.0) + g.normal(0, 0.05, n))
assert classify(chop)["regime"] in ("Chop", "Mixed", "Squeeze"), classify(chop)   # tiny ranges: never Trend
assert classify(chop)["regime"] != "Trend"
cl = 100 + np.cumsum(g.normal(0, 0.3, n)); cl[-5:] = cl[-6] * np.array([.99, .975, .96, .945, .93])
crash = classify(frame(cl)); assert crash["regime"] == "Crash" and crash["ret_z"] < -2, crash
sp = np.full(n, 0.3); sp[-5:] = 6.0
hv = classify(frame(100 + np.cumsum(g.normal(0, 0.3, n)), spread=sp)); assert hv["regime"] == "Hi-Vol" and hv["atr_ratio"] > 1.5, hv
sq = 100 + np.cumsum(g.normal(0, 1.0, n)); sq[-30:] = sq[-31] + g.normal(0, 0.02, 30)
sqz = classify(frame(sq, spread=np.concatenate([np.full(n - 30, 0.3), np.full(30, 0.05)]))); assert sqz["regime"] == "Squeeze" and sqz["bb_pct"] < 20, sqz
vol = np.full(n, 100.0); vol[-1] = 5.0
th = classify(frame(100 + np.cumsum(g.normal(0, 0.3, n)), vol=vol)); assert th["regime"] in ("Thin", "Crash", "Hi-Vol", "Squeeze") and th["vol_pct"] is not None and th["vol_pct"] < 20, th
nv = classify(frame(100 + np.cumsum(g.normal(0, 0.3, n)), vol=np.zeros(n))); assert nv["vol_pct"] is None   # a feed without volume never says Thin
assert classify(frame(100 + np.arange(30) * 1.0))["regime"] is None and classify(None)["regime"] is None
assert all(classify(frame(100 + np.cumsum(g.normal(0, 0.5, n))))["regime"] in REGIMES for _ in range(3))
print("ok regime:", {k: classify(x)["regime"] for k, x in {"trend": trend, "chop": chop, "crash": frame(cl), "hivol": frame(100 + np.cumsum(g.normal(0, 0.3, n)), spread=sp), "squeeze": frame(sq)}.items()})
