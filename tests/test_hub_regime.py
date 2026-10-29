"""Regime Radar on synthetic candles (plain script). MOCK DATA ONLY: proves the labelling logic, says nothing about real markets."""
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import pandas as pd
from modules import hub_core, hub_regime as hr

def ohlc(close, wick=0.002):
    c = np.asarray(close, dtype=float)
    return pd.DataFrame({"open": c, "high": c * (1 + wick), "low": c * (1 - wick), "close": c})

def walk(seed, n, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    return 100 * np.exp(np.cumsum(drift + vol * rng.standard_normal(n)))

# --- ADX: strong steady trend is high, a flat oscillation is low ---
up = ohlc(100 * np.exp(0.004 * np.arange(400)))
a = hr.adx(up["high"].to_numpy(), up["low"].to_numpy(), up["close"].to_numpy())
assert a[-1] > 40, a[-1]
t = np.arange(400); osc = ohlc(100 + 3 * np.sin(t / 3.0), wick=0.004)
a2 = hr.adx(osc["high"].to_numpy(), osc["low"].to_numpy(), osc["close"].to_numpy())
assert a2[-1] < 25, a2[-1]
assert np.isnan(a[5])

# --- labels: warm-up blank, valid names after, trend series ends in Trend ---
lab = hr.label(up["high"], up["low"], up["close"])
assert all(l == "" for l in lab[:hr.WARM]) and set(lab[hr.WARM:]) <= set(hr.REGIMES)
assert lab[-1] == "Trend"

# --- NO LOOK-AHEAD: changing the last candle cannot change any earlier label ---
base = walk(3, 600)
d1, d2 = ohlc(base), ohlc(np.concatenate((base[:-1], [base[-1] * 0.6])))
l1 = hr.label(d1["high"], d1["low"], d1["close"]); l2 = hr.label(d2["high"], d2["low"], d2["close"])
assert l1[:-1] == l2[:-1]

# --- a sudden drop is a Crash on that very bar ---
c = walk(4, 500, vol=0.003).copy(); c[400:] *= 0.85
lc = hr.label(*(ohlc(c)[k] for k in ("high", "low", "close")))
assert "Crash" in lc[400:406], lc[398:410]

# --- stats: counts add up, persistence in [0,1], small regimes flagged ---
df = ohlc(walk(5, 1200))
res = hr.analyse(df, "synthetic", publish=False)
labs = res["labels"]
assert sum(s["bars"] for s in res["stats"].values()) == sum(1 for l in labs if l)
for g, s in res["stats"].items():
    assert s["persistence"] is None or 0 <= s["persistence"] <= 1
    assert s["evidence"] == (s["bars"] >= hr.MIN_N)
cur = hr.current(["", "Chop", "Trend", "Trend"])
assert cur == {"regime": "Trend", "bars_in": 2, "stale_bars": 0}
assert hr.current(["", ""])["regime"] is None

# --- correlation: identical symbols are 'one bet', independent ones are not ---
x = walk(6, 300)
hi = hr.avg_pair_corr({"a": x, "b": x * 2, "c": x * 0.5})
assert hi["high"] and hi["mean_corr"] > 0.99
lo = hr.avg_pair_corr({"a": walk(7, 300), "b": walk(8, 300), "c": walk(9, 300)})
assert not lo["high"]
assert hr.avg_pair_corr({"a": x})["mean_corr"] is None

# --- publish merges per key and counts one test per regime per series ---
tmp = Path(tempfile.mkdtemp())
hr.analyse(df, "s1", root=tmp); hr.analyse(df, "s2", root=tmp); hr.analyse(df, "s1", root=tmp)
snap = hub_core.read("regime", tmp)
assert sorted(f["key"] for f in snap["findings"]) == ["s1", "s2"] and snap["n_trials"] == 2 * len(hr.REGIMES)

# --- funding / OI context (fake Hyperliquid API, no network) ---
hist = [0.00001 + 0.000001 * (i % 5) for i in range(100)]
assert hr.funding_z(hist[:10], 0.0001) is None and hr.funding_z([0.0001] * 50, 0.0002) is None
assert hr.funding_z(hist, 0.00001) is not None and hr.funding_z(hist, 0.0005) > 2
assert hr.quadrant(1, 1).startswith("new longs") and hr.quadrant(-1, 1).startswith("new shorts")
assert hr.quadrant(1, -1).startswith("short covering") and hr.quadrant(-1, -1).startswith("long liquidation") and hr.quadrant(0, 5) == "flat"

def fake_post(payload, oi=1000.0, px=100.0, fund=0.0005):
    if payload["type"] == "metaAndAssetCtxs":
        return [{"universe": [{"name": "BTC"}, {"name": "ETH"}]},
                [{"funding": str(fund), "openInterest": str(oi), "markPx": str(px), "premium": "0.0002"},
                 {"funding": "0.00001", "openInterest": "10", "markPx": "5", "premium": "0"}]]
    return [{"fundingRate": str(h)} for h in hist]

raw = hr.fetch_funding(coins=("BTC", "SOL"), now_ms=10**12, post=fake_post)
assert list(raw) == ["BTC"] and raw["BTC"]["oi_usd"] == 100000.0           # unknown coin skipped, OI in dollars
ctx = hr.funding_context(raw, now=1000)
assert ctx["BTC"]["stretched"] and ctx["BTC"]["funding_apr_pct"] == round(0.0005 * 24 * 365 * 100, 2) and ctx["BTC"]["quadrant"] is None
raw2 = hr.fetch_funding(coins=("BTC",), now_ms=10**12, post=lambda q: fake_post(q, oi=1200.0, px=105.0))
ctx2 = hr.funding_context(raw2, prev=ctx, now=1000 + hr.MIN_GAP_S)
assert ctx2["BTC"]["quadrant"].startswith("new longs") and ctx2["BTC"]["since"] == hr.MIN_GAP_S and ctx2["BTC"]["oi_change_pct"] > 20
assert hr.funding_context(raw2, prev=ctx, now=1600)["BTC"]["quadrant"].startswith("too soon")   # 10 min: noise
assert hr.funding_context(raw2, prev=ctx, now=1000)["BTC"]["quadrant"] is None      # no time passed: no reading

# --- update_funding keeps the regime findings; analyse keeps the funding block ---
tmp2 = Path(tempfile.mkdtemp())
hr.analyse(df, "keep", root=tmp2)
hr.update_funding(root=tmp2, post=fake_post, now=2000)
s2 = hub_core.read("regime", tmp2)
assert [f["key"] for f in s2["findings"]] == ["keep"] and "BTC" in s2["funding"]
hr.analyse(df, "keep2", root=tmp2)
s3 = hub_core.read("regime", tmp2)
assert "BTC" in s3["funding"] and len(s3["findings"]) == 2
hr.update_funding(root=tmp2, post=lambda q: fake_post(q, oi=2000.0, px=90.0), now=2000 + hr.MIN_GAP_S)
assert hub_core.read("regime", tmp2)["funding"]["BTC"]["quadrant"].startswith("new shorts")
print("test_hub_regime: all passed")
