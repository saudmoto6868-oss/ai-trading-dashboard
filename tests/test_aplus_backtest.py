"""A+ setups walk-forward sandbox (owner 2026-11-20). Synthetic candles and a fake OKX reader only; no network.
Run: python3 tests/test_aplus_backtest.py"""
import math
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import aplus_backtest as B  # noqa: E402


def bars(closes, spread=0.5):
    rows, prev = [], closes[0]
    for c in closes:
        o = prev
        rows.append({"t": 0, "o": o, "h": max(o, c) + spread, "l": min(o, c) - spread, "c": c})
        prev = c
    for i, r in enumerate(rows):
        r["t"] = i
    return rows


# 1) trade mechanics: long, stop first in the same bar, target 2R, time stop
rows = bars([100.0] * 70 + [100.0, 100.0])
rows[71] = {"t": 71, "o": 100, "h": 101, "l": 99.0, "c": 100.0}          # stop touched at 99.0 with level 100, atr ~1 -> stop 99.5
rr = B.trade(rows, 70, 1, 100.0, [1.0] * len(rows))
assert rr is not None and rr < -1.0, rr                                    # full stop plus cost
up = bars([100.0] * 70 + [100.0 + 0.1 * k for k in range(1, 60)])
r2 = B.trade(up, 70, 1, 100.0, [1.0] * len(up))
assert r2 is not None and r2 > 1.5, r2                                     # reaches 2R before the hold ends
# 2) statistics + verdict thresholds
assert B.verdict([0.5] * 50)[0] == "not evidence"                          # n < 100
st = B.stats([1.0, -1.0] * 60)
assert st["n"] == 120 and abs(st["meanR"]) < 1e-9
good = [0.5 + (0.2 if k % 2 else -0.2) for k in range(120)]              # mean 0.5, sd ~0.2, both halves positive
v, s_good = B.verdict(good)
assert v.startswith("evidence") and s_good["t"] > 3, (v, s_good)
flip = [0.5] * 84 + [-2.0] * 36                                              # second half negative
assert B.verdict(flip)[0].startswith("not evidence"), B.verdict(flip)
# 3) full run with a fake OKX reader (pages newest first), output written to a temp file
def fake_get(url, params):
    n = 400
    base = 60000.0
    closes = [base + 300 * math.sin(i / 9.0) + 40 * i for i in range(n)]
    rows = bars(closes, spread=40.0)
    rows = [[str(r["t"] * 3600000), str(r["o"]), str(r["h"]), str(r["l"]), str(r["c"]), "1", "0", "0", "1"] for r in rows]
    rows.reverse()
    after = params.get("after")
    if after is None:
        return {"data": rows[:100]}
    idx = [i for i, r in enumerate(rows) if r[0] == after]
    if not idx or idx[0] + 1 >= len(rows):
        return {"data": []}
    return {"data": rows[idx[0] + 1: idx[0] + 101]}
with tempfile.TemporaryDirectory() as d:
    out = os.path.join(d, "aplus.json")
    rep = B.main(get=fake_get, out=out, pages=6)
    import json
    saved = json.load(open(out))
    assert set(saved["results"]) == {f"{s} {t}" for s in B.SYMS for t in B.TFS}, saved["results"].keys()
    one = next(iter(saved["results"].values()))
    assert set(one["setups"]) == {"pullback", "retest", "control"}
    for name, s in one["setups"].items():
        assert s["verdict"].startswith(("evidence", "not evidence")) and "n" in s
print("ok aplus backtest sandbox: mechanics (stop first, 2R, cost), verdict thresholds, full run on fake OKX pages writes JSON; mock only")
