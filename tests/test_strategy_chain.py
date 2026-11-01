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
md = sl.report(rows, conf, cfl, {"built": 0, "symbols": ["X"], "tfs": ["1h"]})
assert "## Chain grades" in md and "*CHAIN*" not in md.split("## Chain grades")[0], "chain rows leaked into detector tables"
print("ok strategy chain", len(ev), "events")
