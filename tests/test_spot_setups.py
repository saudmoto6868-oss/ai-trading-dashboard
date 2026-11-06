"""Spot setup library + setup lab: Radar detectors on spot timeframes (buy + exit), spot-only setups fire on hand-made shapes
(Elliott wave 3 go, golden cross, 52-week breakout, Mayer value, COT extreme), evidence labels (t >= 3 rule), the library list,
and the walk-forward lab on synthetic candles (no look-ahead in months). No network. Plain script."""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import numpy as np
import pandas as pd

from modules import spot_dash, spot_ind as I, spot_setups as SS

rng = np.random.default_rng(3)


def frame(c, start="2018-01-01", freq="D", vol=None):
    c = np.asarray(c, float)
    o = np.r_[c[0], c[:-1]]
    return pd.DataFrame({"time": pd.date_range(start, periods=len(c), freq=freq), "open": o, "high": np.maximum(o, c) * 1.006,
                         "low": np.minimum(o, c) * 0.994, "close": c, "volume": vol if vol is not None else rng.uniform(1, 3, len(c))})


day = frame(1900 * np.exp(np.cumsum(rng.normal(0.0005, 0.013, 2600))))
agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}


def get(sym, tf, limit=300):
    d = day.set_index("time")
    if tf == "1mo":
        return d.resample("MS").agg(agg).dropna().reset_index()
    if tf == "1w":
        return d.resample("W").agg(agg).dropna().reset_index().tail(limit).reset_index(drop=True)
    return day.tail(limit).reset_index(drop=True)


b = spot_dash.load_bundle("GOLD", get)
assert set(b["frames"]) >= {"1mo", "1w", "1d"}
live = SS.scan(b, {"deriv": {"ok": True, "funding": 0.08}}, {"ok": True, "comm_idx": 95, "spec_idx": 97, "date": "2026-10-27"})
ids = {x["id"] for x in live}
assert any(i.startswith("radar:") for i in ids) and {"inst_comm_long", "inst_spec_crowd", "flow_funding_hot"} <= ids
assert {x["side"] for x in live} <= {"buy", "exit"} and all(x["school_ar"] and x["name"] and x["ev_label"] for x in live)
assert all(x["entry"] is None for x in live if x["side"] == "exit")
assert any("؀" <= ch <= "ۿ" for x in live if x["id"].startswith("radar:") for ch in x["name"])   # Arabic names for Radar setups

# hand-made shapes for the spot-only rules
up = np.r_[np.linspace(100, 60, 220), np.linspace(60, 61, 40)]           # long fall then flat: 50 under 200
golden = np.r_[up, np.linspace(61, 95, 60)]                               # rally: 50 crosses 200 near the end
for k in range(len(golden) - 260, len(golden)):
    d = frame(golden[:k + 1])
    rd = I.analyse(d)
    s = SS.spot_only({"reads": {"1d": rd}, "frames": {"1d": d}, "price": float(d.close.iloc[-1]), "stats": {}})
    if any(x["id"] == "cl_golden" for x in s):
        break
else:
    raise AssertionError("golden cross never fired")
wk = np.r_[np.linspace(50, 40, 60), np.linspace(40, 45, 20), [44, 46, 52]]   # weekly close above the 52-week high
dw = frame(wk, freq="W")
s = SS.spot_only({"reads": {"1w": I.analyse(dw)}, "frames": {"1w": dw}, "price": 52.0, "stats": {"mayer": 0.7, "dist_200w": -5}})
got = {x["id"] for x in s}
assert "cl_52w_break" in got and "val_mayer" in got and "val_200w" in got, got
s2 = SS.spot_only({"reads": {}, "frames": {}, "price": 100.0, "stats": {"mayer": 2.6}})
assert [x["id"] for x in s2] == ["val_hot"] and s2[0]["side"] == "exit"
# Elliott wave 3 'go': L H L(higher) then a close through the wave-1 high
fake = {"ok": True, "px": 112.0, "atr": 2.0, "c": np.r_[np.full(50, 100.0), [104, 112]], "h": np.full(52, 113.0), "l": np.full(52, 99.0), "dr": {}, "piv": [],
        "rsi": np.full(52, 50.0), "hist": np.zeros(52), "trend": "up", "elliott": {"kind": None, "pivots": [(10, 90.0, "L"), (20, 110.0, "H"), (30, 98.0, "L"), (51, 112.0, "H")]}, "gann": {}}
fake["c"][-2] = 109.0
s3 = SS.spot_only({"reads": {"1w": fake}, "frames": {}, "price": 112.0, "stats": {}})
assert any(x["id"] == "ew_w3_go" and x["target"] > 112 for x in s3), [x["id"] for x in s3]

# evidence labels: luck guard
assert SS.ev_label(None) == "لسه ماتقاسش" and "مش دليل" in SS.ev_label({"n": 12, "t": 4})
assert SS.ev_label({"n": 40, "t": 3.2}).startswith("اشتغل") and SS.ev_label({"n": 40, "t": 2.4}).startswith("مشجع")
assert SS.ev_label({"n": 40, "t": -3.5}).startswith("كان أسوأ") and SS.ev_label({"n": 40, "t": 0.5}).startswith("مفيش فرق")
tmp = Path(tempfile.mkdtemp()) / "ev.json"
tmp.write_text(json.dumps({"setups": {"inst_comm_long|1w": {"n": 50, "t": 3.4}}}))
SS.EVIDENCE = tmp
lab = SS.library()
assert len(lab) >= 90 and any(r["id"] == "inst_comm_long" and "اشتغل" in " ".join(r["evidence"].values()) for r in lab)
assert {"اليوت", "جان", "الزخم / الدايفرجنس", "كلاسيك", "SMC / ICT", "المؤسسات"} <= {r["school"] for r in lab}

# the lab on synthetic candles
import spot_setups_lab as L
cache = {}


def get2(sym, tf, limit=300):
    d0 = cache.setdefault(sym, frame(100 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, 1600))), start="2021-01-04")).set_index("time")
    if tf == "1w":
        return d0.resample("W-SUN", label="left", closed="left").agg(agg).dropna().reset_index().tail(limit).reset_index(drop=True)
    if tf == "1mo":
        return d0.resample("MS").agg(agg).dropna().reset_index()
    return cache[sym].tail(limit).reset_index(drop=True)


m = get2("BTC", "1mo")
assert str(L._closed_months(m, pd.Timestamp("2022-03-15"))["time"].iloc[-1])[:7] == "2022-02"
res = L.main(get2, crypto=["BTC"], other={})
assert res["markets_ok"] == ["BTC"] and res["setups"] and all(v["n"] >= 1 and v["side"] in ("buy", "exit") for v in res["setups"].values())
md, ar = L.report(res), L.summary_ar(res)
assert "| setup |" in md and "t ≥ 3" in ar
print("test_spot_setups OK")
