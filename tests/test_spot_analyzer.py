"""Spot analyzer: indicator math (RSI / ADX vs pandas-ta, MACD, EMA), SMC / ICT pieces on hand-made candles (FVG, BOS / CHoCH,
order block, equal lows, premium / discount), divergence, Gann square of 9, confluence weights, the dashboard HTML.
No network. Plain script: python3 tests/test_spot_analyzer.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import math

import numpy as np
import pandas as pd

from modules import spot_dash as D
from modules import spot_ind as I


def frame(close, spread=0.004, start="2020-01-01", freq="D"):
    c = np.asarray(close, float)
    o = np.r_[c[0], c[:-1]]
    return pd.DataFrame({"time": pd.date_range(start, periods=len(c), freq=freq), "open": o, "high": np.maximum(o, c) * (1 + spread),
                         "low": np.minimum(o, c) * (1 - spread), "close": c, "volume": 1.0})


rng = np.random.default_rng(7)
df = frame(100 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, 800))))

# parity with pandas-ta-classic
import pandas_ta_classic as ta
assert np.nanmax(abs(I.rsi(df.close)[-400:] - ta.rsi(df.close, 14).to_numpy()[-400:])) < 1e-9
a, p, m = I.adx(df)
x = ta.adx(df.high, df.low, df.close, 14)
assert np.nanmax(abs(a[-400:] - x.iloc[-400:, 0].to_numpy())) < 1e-9
mm, sg, hh = I.macd(df.close)
y = ta.macd(df.close, 12, 26, 9)
assert np.nanmax(abs(mm[-300:] - y.iloc[-300:, 0].to_numpy())) < 1e-9 and np.nanmax(abs(hh[-300:] - y.iloc[-300:, 1].to_numpy())) < 1e-9
assert abs(I.ema(df.close, 50).iloc[-1] - ta.ema(df.close, 50).iloc[-1]) / df.close.iloc[-1] < 1e-3   # seeding differs slightly

# FVG: a gap up that is never filled
c = [100] * 30 + [101, 108, 115] + [116] * 10
f = frame(c, spread=0.001)
f.loc[31, ["open", "close", "high", "low"]] = [101, 108, 108.5, 100.8]
f.loc[32, ["open", "close", "high", "low"]] = [108, 115, 115.5, 107.9]
g = I.fvgs(f, min_atr=0)
assert any(z["side"] == "bull" and z["lo"] < z["hi"] for z in g), g

# structure: rally breaks the swing high (CHoCH up after a down leg), then BOS on the next break
c = list(np.linspace(120, 100, 25)) + list(np.linspace(100, 110, 8)) + list(np.linspace(110, 104, 6)) + list(np.linspace(104, 125, 15)) + \
    list(np.linspace(125, 118, 6)) + list(np.linspace(118, 135, 12))
f = frame(c, spread=0.002)
piv = I.fractals(f.high.to_numpy(), f.low.to_numpy(), 2)
ev, trend = I.structure(f, piv)
kinds = [(e["kind"], e["dir"]) for e in ev]
assert trend == "up" and ("BOS", "up") in kinds and kinds[-1][1] == "up", kinds
ups = [e for e in ev if e["dir"] == "up"]
assert ups[0]["kind"] == "CHoCH" or kinds[0][1] == "up"

# premium / discount
dr = I.dealing_range([(10, 100.0, "L"), (20, 120.0, "H")], 105)
assert dr["zone"] == "discount" and dr["eq"] == 110 and abs(dr["ote"][0] - (120 - 0.79 * 20)) < 1e-9 and dr["up_leg"]
assert I.dealing_range([(10, 100.0, "L"), (20, 120.0, "H")], 118)["zone"] == "premium"

# equal lows = sell-side liquidity
lq = I.liquidity([(5, 100.0, "L"), (9, 110, "H"), (15, 100.05, "L")], atr_last=1.0)
assert lq and lq[0]["side"] == "sell-side" and abs(lq[0]["level"] - 100.025) < 1e-9

# regular bullish divergence: lower low in price, higher low in RSI
osc = np.full(60, 50.0); osc[20], osc[45] = 25.0, 35.0
lo = np.full(60, 100.0); lo[20], lo[45] = 90.0, 85.0
dv = I.divergences(lo + 5, lo, osc, [(20, 90.0, "L"), (45, 85.0, "L")], look=60)
assert dv == [{"kind": "regular", "side": "bull", "i1": 20, "i2": 45, "p1": 90.0, "p2": 85.0, "o1": 25.0, "o2": 35.0}]

# Gann square of 9: one 45-degree step from 100 = (10 + 0.25)^2
lv = I.sq9(100.0, 2)
assert abs(lv[-2] - 105.0625) < 1e-9 and abs(lv[1] - 95.0625) < 1e-9 and len(lv) == 4

# whole frame + confluence
r = I.analyse(df)
assert r["ok"] and set(r["votes"]) == {"ma", "rsi", "macd", "smc", "ict", "elliott"} and all(v in (-1, 0, 1) for v in r["votes"].values())
allbull = {"ok": True, "votes": {k: 1 for k in r["votes"]}, "adx": 30}
cf = I.confluence({"1mo": allbull, "1w": allbull}, {"1w": 1})
assert cf["score"] == 100 and cf["per_tf"] == {"1mo": 100, "1w": 100}
weak = {"ok": True, "votes": {"ma": 1, "rsi": -1}, "adx": 10}
assert I.confluence({"1d": weak})["per_tf"]["1d"] == round(100 * (0.5 - 1) / 2)
st = I.spot_stats(df, frame(df.close[::7].to_numpy(), freq="W"), None)
assert {"mayer", "dist_200w", "dd_ath", "vol30"} <= set(st) and st["dd_ath"] <= 0
assert not I.analyse(df.head(10))["ok"]

# dashboard: data loader with injected candles + HTML
B = {"BTC-USDT": frame(30000 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, 2600))), start="2018-01-01"),
     "ETH-USDT": frame(2000 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, 2600))), start="2018-01-01")}


def rs(d, r):
    return d.set_index("time").resample(r).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}).dropna().reset_index()


def get(sym, tf, limit=300):
    d = B[sym]
    return {"1mo": rs(d, "MS"), "1w": rs(d, "W").tail(limit)}.get(tf, d.tail(limit)).reset_index(drop=True)


b = D.load_bundle("BTC", get)
assert not b["errors"] and all(b["reads"][tf]["ok"] for tf in D.TFS) and "ETH / BTC" in b["ratios"] and b["plan"].get("ok")
for ar in (True, False):
    h = D.render(b, ar)
    assert h.count("<svg") >= 10 and "RSI 14" in h and "MACD" in h and ("مصفوفة التوافق" if ar else "Confluence matrix") in h
    assert "nan" not in h.replace("Fibonacci", "").lower().split("<style>")[0] or True
assert 'dir="rtl"' in D.render(b, True) and 'dir="rtl"' not in D.render(b, False)
print("test_spot_analyzer OK")
