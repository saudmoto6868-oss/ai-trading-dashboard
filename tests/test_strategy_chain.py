"""Chain layers + grades in the strategy lab, on synthetic candles (no network)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from modules import strategy_lab as sl

# layers / grades
ctx = {"pos": .1, "rv": 1.5, "reg": 1.0}
L = sl.chain_layers(ctx, 1, 1, "London 07-12")
assert all(L.values()) and sl.grade(L) == "A+++", L
L = sl.chain_layers(ctx, -1, 1, "Asia 00-07")       # short in discount, against trend, Asia
assert not L["htf"] and not L["loc"] and not L["time"] and sl.grade(L) == "B", L
assert sl.chain_layers({"pos": .9, "rv": 0, "reg": .5}, -1, -1, None)["loc"]

# chain_ctx uses only bars up to i
rng = np.random.default_rng(1); n = 400
cl = 100 + np.cumsum(rng.normal(0, 1, n)); hi = cl + 1; lo = cl - 1; vol = rng.uniform(1, 2, n); natr = np.full(n, .01)
c1 = sl.chain_ctx(hi, lo, cl, vol, natr, 200)
hi2 = hi.copy(); hi2[201:] += 50
assert sl.chain_ctx(hi2, lo, cl, vol, natr, 200) == c1, "look-ahead"
assert 0 <= c1["pos"] <= 1

# full walk + summarize + report on synthetic candles
t = pd.date_range("2026-01-01", periods=900, freq="1h")
c = 100 + np.cumsum(rng.normal(0, .8, 900))
df = pd.DataFrame({"time": t, "open": c + rng.normal(0, .2, 900), "high": c + abs(rng.normal(0, .8, 900)) + .3,
                   "low": c - abs(rng.normal(0, .8, 900)) - .3, "close": c, "volume": rng.uniform(10, 30, 900)})
ev, br = sl.walk(df, "1h", stride=6)
assert ev and all("chain" in e and "oos" in e for e in ev)
rows, conf, cfl = sl.summarize([("1h", "X", ev)], [("1h", "X", br)])
ch = [r for r in rows if r["key"] == "*CHAIN*"]
assert any(r["side"] == "all signals" for r in ch) and all("t" in r and "oos_n" in r for r in ch)
assert next(r for r in ch if r["side"] == "all signals")["n"] == len(ev)
assert all(r["net"] == round(r["avgR"] - sl.COST_R, 3) for r in ch if r.get("avgR") is not None), "chain rows carry net of cost"
lk = [r for r in ch if r["side"].startswith(("loc / ", "no loc / "))]
assert lk and sum(r["n"] for r in lk) == len(ev), "every event lands in exactly one loc / no loc row"
pr = [r for r in rows if r["key"] == "*PREREG*"]
assert len(pr) == 2 and all(r["n"] == 0 and not r["edge"] for r in pr), "before the freeze date nothing counts"
assert all(e["ts"] > 0 for e in ev)
# fabricated events: 150 winners with loc after the freeze, 50 before it (must not count), 20 without loc (must not count)
mk = lambda ts, loc, r: {"key": "sess_amd", "ts": ts, "r": r, "base": -1.0, "ses": "London 07-12", "chain": {"loc": loc, "htf": True, "vol": True, "reg": True, "time": True}}
fab = [mk(sl.PREREG_CUTOFF_MS + 1000 + i, True, 1.5 if i % 2 else -1.0) for i in range(150)] + [mk(sl.PREREG_CUTOFF_MS - 1000 - i, True, 1.5) for i in range(50)] + [mk(sl.PREREG_CUTOFF_MS + 5 + i, False, 1.5) for i in range(20)]
h1 = {r["side"]: r for r in sl.prereg_rows([("1h", "X", fab)])}["H1 sess_amd + loc"]
assert h1["n"] == 150 and h1["since"] == sl.PREREG_CUTOFF_MS, h1
assert h1["avgR"] == 0.25 and h1["net"] == 0.15, h1
assert h1["edge"] is True, h1                      # n 150, t vs random > 3, net > 0 in both halves
assert {r["side"]: r for r in sl.prereg_rows([("1h", "X", fab[:60])])}["H1 sess_amd + loc"]["edge"] is False, "n < 100 never passes"
# stop study: hand-made candles (entry 100, ATR 1, target 2.25 ATR)
_n = 60; _cl = np.full(_n, 100.0); _hi = _cl + 0.2; _lo = _cl - 0.2
_lo[12] = 98.3; _hi[20] = 102.3                       # dips 1.7 ATR (through the 1.5 stop, inside 2.0) and THEN reaches the target
_r = sl.stop_study(_hi, _lo, _cl, 10, 1, 1.0, 40)
assert _r["stp"][1.0] == -1.0 and _r["stp"][1.5] == -1.5 and _r["stp"][2.0] == 2.25 and _r["stp"][3.0] == 2.25, _r
assert _r["rec"] == 1 and abs(_r["mae"] - 1.7) < 1e-9, _r
_lo2 = np.full(_n, 99.8); _hi2 = _cl + 0.2; _hi2[15] = 102.3   # straight to the target, never against us
_r2 = sl.stop_study(_hi2, _lo2, _cl, 10, 1, 1.0, 40); assert _r2["rec"] is None and all(v == 2.25 for v in _r2["stp"].values()) and _r2["mae"] < 0.3, _r2
_lo3 = np.full(_n, 99.8); _hi3 = _cl + 0.2; _lo3[12] = 98.3                            # stopped, target never comes
_r3 = sl.stop_study(_hi3, _lo3, _cl, 10, 1, 1.0, 40); assert _r3["rec"] == 0 and _r3["mae"] is None and _r3["stp"][1.5] == -1.5 and -1.5 < _r3["stp"][3.0] <= 0.5, _r3
_lo4 = np.full(_n, 99.8); _hi4 = _cl + 0.2; _lo4[12] = 98.3; _hi4[12] = 102.5          # one bar touches both: counted as the stop (conservative)
_r4 = sl.stop_study(_hi4, _lo4, _cl, 10, 1, 1.0, 40); assert _r4["stp"][1.5] == -1.5 and _r4["stp"][2.0] == 2.25, _r4
_ev = [("1h", "X", [{"stop": _r, "mirror": _r3, "key": "a"}, {"stop": _r2, "mirror": _r2, "key": "a"}])]
_sr = sl.stop_rows(_ev); _all = {r["side"]: r for r in _sr if r["tf"] == "all"}
assert _all["stop 2.0 ATR"]["win"] == 100.0 and _all["stop 1.5 ATR"]["win"] == 50.0 and _all["stopped at 1.5 ATR, target reached later"]["win"] == 100.0, _all
assert "stopped_share" in _all["stopped at 1.5 ATR, target reached later"] and all(e["stop"]["stp"] for e in ev if "stop" in e)
assert all("stop" in e and "mirror" in e for e in ev), "real walk events carry the stop study"
md0 = sl.report(rows, conf, cfl, {"built": 0, "symbols": ["X"], "tfs": ["1h"]}); assert "## Stop study" in md0 and "*STOP*" not in md0.split("## Stop study")[0], "stop rows leaked into detector tables"
md = sl.report(rows, conf, cfl, {"built": 0, "symbols": ["X"], "tfs": ["1h"]})
assert "## Chain grades" in md and "*CHAIN*" not in md.split("## Chain grades")[0], "chain rows leaked into detector tables"
print("ok strategy chain", len(ev), "events")
