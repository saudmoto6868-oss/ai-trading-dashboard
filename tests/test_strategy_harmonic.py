"""Harmonic school in the strategy lab: the walk asks the harmonic finder on every step (synthetic candles, no network)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from modules import strategy_lab as sl

rng = np.random.default_rng(5)
n = 900
steps = np.sign(np.sin(np.arange(n) / 23.0)) * 1.2 + rng.normal(0, .5, n)
c = 100 + np.cumsum(steps)
df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="1h"), "open": c, "high": c + .6, "low": c - .6, "close": c, "volume": rng.uniform(10, 30, n)})

calls = {"n": 0}
orig = sl.find_harmonics
def counting(*a, **k):
    calls["n"] += 1
    return orig(*a, **k)
sl.find_harmonics = counting
try:
    ev, br = sl.walk(df, "1h", stride=4)
finally:
    sl.find_harmonics = orig
assert calls["n"] > 100, calls          # the harmonic finder runs on the walk
assert sl.SCHOOL["harmonic"].startswith("Harmonic")
assert all(e["key"] != "harmonic" or e["fam"] == "Harmonic" for e in ev)
print("ok strategy harmonic", len(ev), "events, finder calls", calls["n"])
