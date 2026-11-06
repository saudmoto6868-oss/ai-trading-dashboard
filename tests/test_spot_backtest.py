"""scripts/spot_backtest.py on synthetic candles: no look-ahead in the monthly frame, tables + Arabic summary. No network."""
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import numpy as np
import pandas as pd

import spot_backtest as SB

rng = np.random.default_rng(2)


def frame(n=1500):
    c = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, n)))
    o = np.r_[c[0], c[:-1]]
    return pd.DataFrame({"time": pd.date_range("2021-01-04", periods=n, freq="D"), "open": o, "high": np.maximum(o, c) * 1.01,
                         "low": np.minimum(o, c) * 0.99, "close": c, "volume": 1.0})


cache = {}


def get(sym, tf, limit=300):
    d = cache.setdefault(sym, frame()).set_index("time")
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    if tf == "1w":
        return d.resample("W-SUN", label="left", closed="left").agg(agg).dropna().reset_index().tail(limit).reset_index(drop=True)
    return d.resample("MS").agg(agg).dropna().reset_index()


# a month is used only once it has closed
m = get("X", "1mo")
cm = SB.closed_months(m, pd.Timestamp("2022-03-15"))
assert str(cm["time"].iloc[-1])[:7] == "2022-02" and len(SB.closed_months(m, pd.Timestamp("2022-03-01"))) == len(cm)
SB.CRYPTO, SB.METALS = ["BTC", "ETH"], {"GOLD": "Y:GC=F", "BAD": "Y:NOPE"}
real_get = get
res = SB.main(lambda s, tf, limit=300: (_ for _ in ()).throw(ValueError("x")) if "NOPE" in s else real_get(s, tf, limit))
assert res["symbols_ok"] == ["BTC", "ETH", "GOLD"] and res["symbols_failed"] == ["BAD (ValueError)"] and res["rows"] > 200
g = res["groups"]["crypto"]
assert [s["step"] for s in g] == [1, 4, 12] and sum(b["n"] for b in g[0]["buckets"]) == g[0]["n"]
assert g[1]["n"] < g[0]["n"]   # non-overlapping keeps fewer rows
md, ar = SB.fmt(res), SB.summary_ar(res)
assert "| >= 35 |" in md and "non-overlapping" in md and "الكريبتو" in ar and "المعادن" in ar and "ناقص: BAD" in ar
print("test_spot_backtest OK")
