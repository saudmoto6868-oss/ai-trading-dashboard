"""Wyckoff accumulation phases (modules/wyckoff_phases.py). Synthetic candles only; no network. Context labels, not signals."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from modules import wyckoff_phases as W


def frame(path, vol=None):
    c = np.asarray(path, float)
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + 0.4
    l = np.minimum(o, c) - 0.4
    d = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=len(c), freq="h"), "open": o, "high": h, "low": l, "close": c,
                      "volume": vol if vol is not None else np.full(len(c), 100.0)})
    return d


def build(stage):
    """stage: 'A' (SC+AR only) ... 'E'. The climax bar is wide, so the ATR is a few points; the range is about 88-100."""
    rng = np.random.default_rng(3)
    pre = np.linspace(125, 100, 50) + rng.normal(0, 0.2, 50)           # long decline into the climax
    sc = [96.0, 90.0, 93.0]                                              # SC: big drop bar then a bounce
    ar = [97.0, 99.0, 100.0, 99.0, 97.0]                                 # AR to ~100 then back in the range
    rangeA = [96, 94, 92.5, 93, 95, 96.5, 95, 93.5, 92.2, 93.5, 95, 97, 96, 94.5, 93, 92.4, 94, 96, 98, 97]   # range, tests near 90-92
    sp = [91.5, 87.0, 91.0, 93.0]                                        # spring: dips below the SC low and closes back
    mid = [95, 97, 98, 99, 98.5, 99.5]
    sos = [101.5, 103.0, 104.5]                                          # close above R
    lps = [102.0, 101.0, 102.5, 103.5, 105, 107, 108.5]                  # LPS holds above R then trend
    parts = {"A": [pre, sc, ar], "B": [pre, sc, ar, rangeA], "C": [pre, sc, ar, rangeA, sp], "D": [pre, sc, ar, rangeA, sp, mid, sos],
             "E": [pre, sc, ar, rangeA, sp, mid, sos, lps]}[stage]
    path = np.concatenate([np.asarray(p, float) for p in parts])
    lead = np.linspace(path[0] + 25, path[0], 100)
    full = np.concatenate([lead, path])
    vol = np.full(len(full), 100.0)
    vol[100 + 50 + 1] = 400.0                                              # climax volume on the SC bar
    d = frame(full, vol)
    i_sc = 100 + 50 + 1
    d.loc[i_sc, "low"] = 88.0                                             # wide climax range
    return d


# 1) too short / flat noise: nothing
assert W.analyze(frame(np.linspace(100, 101, 50))) is None
flat = frame(100 + np.random.default_rng(1).normal(0, 0.3, 300))
assert W.analyze(flat) is None, W.analyze(flat)

# 2) a full accumulation reaches a later phase than a partial one, and phases never go backwards
order = "ABCDE"
got = {}
for s in "ABCDE":
    r = W.analyze(build(s))
    got[s] = r["phase"] if r else None
print("phases found:", got)
assert got["A"] is not None, got
ranks = [order.index(got[s]) for s in "ABCDE" if got[s]]
assert ranks == sorted(ranks), got
assert order.index(got["E"] or "A") > order.index(got["A"]), got

# 3) events are named and the range is sensible
r = W.analyze(build("D"))
names = {e[0] for e in r["events"]}
assert {"SC", "AR"} <= names and r["R"] > r["S"] and r["bias"] == "bullish", r
t = W.tag(build("D"))
assert t and t[0]["family"] == "PA" and t[0]["context"] is True and "phase" in t[0]["name"]

# 4) a range that breaks down is void
bad = build("B")
bad.loc[bad.index[-3:], ["open", "high", "low", "close"]] = [[88, 88.4, 70, 70]] * 3
assert W.analyze(bad) is None
print("ok wyckoff phases")
