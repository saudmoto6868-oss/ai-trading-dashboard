"""Item 15: SMA 10/40 cross, Donchian 55 (Turtle System 2) and cross-sector momentum, on hand-made candles.
Run: python tests/test_hedge.py"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import momentum, signals as S  # noqa: E402


def frame(close, freq="1D"):
    c = np.asarray(close, dtype=float)
    return pd.DataFrame({"time": pd.date_range("2025-01-01", periods=len(c), freq=freq), "open": c, "high": c * 1.002,
                         "low": c * 0.998, "close": c, "volume": 1000.0})


def keys(df):
    sigs, errs = S.detect_all(df)
    assert not errs, errs
    return {(s["key"], s["direction"]) for s in sigs}


# SMA 10/40: long decline then a sharp turn up -> fresh bullish cross on the last bars
down = list(np.linspace(200, 100, 150))
up = list(np.linspace(100, 101, 30))
c = down + up
for k in range(60):                      # walk forward until the 10-SMA first crosses the 40-SMA
    d = frame(c)
    s10, s40 = d["close"].rolling(10).mean(), d["close"].rolling(40).mean()
    if s10.iloc[-1] > s40.iloc[-1]:
        break
    c.append(c[-1] * 1.03)
d = frame(c)
r = S.sma1040_bull(d)
assert r and r[0]["key"] == "sma1040", r
assert ("sma1040", "bullish") in keys(d)
# bearish twin through the inverted frame
assert ("sma1040", "bearish") in keys(frame([1e4 / x for x in c]))
# not on intraday bars
assert S.sma1040_bull(frame(c, "1h")) == []
# no fresh cross after a long uptrend
assert S.sma1040_bull(frame(np.linspace(100, 300, 200))) == []

# Turtle 55: flat range then one close above the 55-bar high
flat = [100 + (i % 5) * 0.5 for i in range(120)]
d = frame(flat + [104.0])
r = S.turtle55_bull(d)
assert r and r[0]["key"] == "turtle55", r
fin = S._finalize(r[0], False)
assert fin["prices"]["lvl"] < 104 and fin["prices"]["inv"] < 104 and fin["prices"]["x"] < 104, fin["prices"]
assert ("turtle55", "bearish") in keys(frame(flat + [96.0]))
# a breakout that already started earlier is not fresh
assert S.turtle55_bull(frame(flat + [104, 105, 106, 107, 108])) == []
assert S.turtle55_bull(frame(flat + [104.0], "4h")) == []

# Arabic text exists for both keys
from modules import arabic  # noqa: E402
for key in ("sma1040", "turtle55"):
    s = [x for x in S.detect_all(frame(c) if key == "sma1040" else frame(flat + [104.0]))[0] if x["key"] == key][0]
    name, detail = arabic.signal_ar(s)
    assert name and detail and "-" != detail, (name, detail)

# Momentum ranking
n = 300
rng = np.random.default_rng(1)
series = {
    "A": 100 * np.exp(np.cumsum(0.002 + 0.003 * rng.standard_normal(n))),    # strong up
    "B": 100 * np.exp(np.cumsum(0.0005 + 0.003 * rng.standard_normal(n))),   # mild up
    "C": 100 * np.exp(np.cumsum(-0.002 + 0.003 * rng.standard_normal(n))),   # down
    "short": np.linspace(1, 2, 100),                                          # too little history -> left out
}
t = momentum.rank(series)
assert list(t["symbol"]) == ["A", "B", "C"], t
assert t.loc[t.symbol == "A", "call"].item() == "LONG candidate"
assert t.loc[t.symbol == "C", "call"].item() == "AVOID"
st = momentum.stats(series["A"])
c_ = series["A"]
assert abs(st["ret_12_1"] - (c_[-22] / c_[-253] - 1)) < 1e-12
assert momentum.rank({}).empty


def fake_get(sym, tf, limit):
    if sym == "BAD":
        raise RuntimeError("HTTP 403")
    return pd.DataFrame({"close": series["A"]})


cl, errs = momentum.fetch_closes({"X": "x", "BAD": "bad"}, get=fake_get)
assert list(cl) == ["X"] and errs and "403" in errs[0]
print("test_hedge: all passed")
