"""Price action + range detectors (modules/pa_patterns.py): each bullish pattern is found on a hand-built series, its bearish twin is found on the mirrored series through detect_all,
random noise gives few signals, and the family is CONTEXT (never a star). No network."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from modules import pa_patterns as P
from modules import signals as S
from modules import scorer


def frame(closes, spread=0.5, opens=None, highs=None, lows=None):
    c = np.asarray(closes, float)
    o = np.r_[c[0], c[:-1]] if opens is None else np.asarray(opens, float)
    h = np.maximum(o, c) + spread if highs is None else np.asarray(highs, float)
    l = np.minimum(o, c) - spread if lows is None else np.asarray(lows, float)
    return pd.DataFrame({"time": pd.date_range("2026-01-01", periods=len(c), freq="1h"), "open": o, "high": h, "low": l, "close": c, "volume": 10.0})


def decline_to_support():
    """100 bars of chop, a decline to a swing low at 100 (bar ~60), a bounce, a second dip back to the level: the setting for engulf / pin / star."""
    rng = np.random.default_rng(1)
    c = list(120 + np.cumsum(rng.normal(0, .4, 40)))
    c += list(np.linspace(c[-1], 100.5, 20))      # decline into the low
    c += [99.8, 100.8, 102.0, 103.0, 103.8, 104.2, 104.0, 103.4, 102.6, 101.8, 101.2, 100.7]   # bounce, then back down to the level
    return c


def run(fn, df):
    return fn(df.reset_index(drop=True))


# 1) engulfing at support
c = decline_to_support()
o = np.r_[c[0], c[:-1]]
c2 = c + [100.6, 103.0]; o2 = list(o) + [101.0, 100.4]   # prev bearish (101.0 -> 100.6), last bullish engulfing it (100.4 -> 103.0)
d = frame(c2, opens=o2)
r = run(P.pa_engulf_bull, d)
assert r and r[0]["key"] == "pa_engulf" and r[0]["family"] == "PA", r

# 2) hammer at support
c3 = c + [100.2]; o3 = list(o) + [100.8]
d3 = frame(c3, opens=o3, highs=list(frame(c).high) + [100.95], lows=list(frame(c).low) + [98.0])
r = run(P.pa_pin_bull, d3)
assert r and r[0]["key"] == "pa_pin", r

# 3) rectangle breakout + retest, and wyckoff spring on the same box
rng = np.random.default_rng(4)
box = []
for k in range(50):                                   # a box 100 .. 106, touching both edges every ~8 bars
    box.append(103 + 3 * np.sin(k * 2 * np.pi / 8.0) + rng.normal(0, .15))
pre = list(np.linspace(90, 103, 40))
brk = [107.9, 108.3, 108.0]                           # closes above the top, then back down to the broken edge
rect = frame(pre + box + brk + [107.5])
atr = float(S.atr_series(rect).iloc[-1])
rr = run(P.rect_bull, rect)
print("rect", [x["name"] for x in rr], "atr", round(atr, 2))
assert rr and rr[0]["key"] == "rect", rr
base = frame(pre + box)
spring = pd.concat([base, pd.DataFrame({"time": pd.date_range(base.time.iloc[-1] + pd.Timedelta(hours=1), periods=3, freq="1h"), "open": [101.0, 100.6, 98.6], "high": [101.5, 100.9, 100.9],
                                         "low": [100.1, 99.9, 97.6], "close": [100.6, 100.2, 100.5], "volume": 10.0})], ignore_index=True)
rw = run(P.wyck_bull, spring)
print("wyck", [x["name"] for x in rw])
assert rw and rw[0]["key"] == "wyck", rw

# 3b) inside-bar breakout in an uptrend
up = list(np.linspace(80, 108, 100))
ib_o = list(np.r_[up[0], up[:-1]]) + [107.0, 108.6, 108.8]
ib_c = up + [109.0, 108.9, 111.0]
ib_h = list(frame(up).high) + [110.0, 109.5, 111.3]
ib_l = list(frame(up).low) + [106.8, 108.2, 108.7]
ib = frame(ib_c, opens=ib_o, highs=ib_h, lows=ib_l)
ri = run(P.pa_inside_bull, ib)
assert ri and ri[0]["key"] == "pa_inside", ri

# 3c) morning star at a swing low
st_o = list(o) + [102.2, 100.1, 100.4]
st_c = list(c) + [100.4, 100.25, 101.9]
star = frame(st_c, opens=st_o)
rs = run(P.pa_star_bull, star)
assert rs and rs[0]["key"] == "pa_star", rs

# 4) double bottom neckline break
db = list(np.linspace(120, 100, 30)) + list(np.linspace(100, 110, 15)) + list(np.linspace(110, 100.2, 15)) + list(np.linspace(100.2, 109, 10)) + [112.0, 112.5, 113.0]
dbl = frame(db)
rd = run(P.dbl_bull, dbl)
print("dbl", [x["name"] for x in rd])
assert rd and rd[0]["key"] == "dbl", rd

# 5) bearish twins come out of detect_all on the mirrored frame, with flipped text
mir = frame([300 - x for x in c2], opens=[300 - x for x in o2])
sigs, errs = S.detect_all(mir)
assert any(s["key"] == "pa_engulf" and s["direction"] == "bearish" and "Bearish engulfing at resistance" in s["name"] for s in sigs), [s["name"] for s in sigs if s["family"] == "PA"]
assert not errs, errs

# 6) PA is a CONTEXT family: flags, never stars
assert "PA" in scorer.CONTEXT_FAMILIES and "PA" not in scorer.TRIGGER_FAMILIES

# 7) noise: the detectors must stay quiet most of the time (no pattern factory)
rng = np.random.default_rng(11)
hits = 0
for _ in range(40):
    z = frame(100 + np.cumsum(rng.normal(0, 1, 160)), spread=.6)
    for fn in P.PA_DETECTORS:
        hits += len(fn(z))
assert hits <= 30, hits   # 40 random series x 7 detectors: a handful of accidental hits is fine, hundreds is not
print("ok pa patterns; noise hits", hits)
