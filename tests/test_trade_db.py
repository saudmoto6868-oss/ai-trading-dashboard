"""research/trade_db: swing levels use only confirmed pivots on the right side of price; trade walk exit types, MFE/MAE. Plain script."""
import numpy as np

import json
import sqlite3
import tempfile
from pathlib import Path

import pandas as pd

from research.trade_db.build_db import SCHEMA, _args, insert, lab_votes, swings, telegram_records, walk_trade

# swings: a pivot high at bar 5 (above close) and a pivot low at bar 10 (below close); bar 15 = now
hi = np.array([10, 11, 12, 13, 14, 20, 14, 13, 12, 11, 10, 11, 12, 13, 14, 15, 16], float)
lo = hi - 1; lo[10] = 5
sup, res = swings(hi, lo, c=15.0, i=15, n=3)
assert res == 20 and sup == 5, (sup, res)
# an unconfirmed pivot (fewer than n bars after it) must not count
hi2 = hi.copy(); hi2[14] = 30
sup2, res2 = swings(hi2, lo, c=15.0, i=15, n=3)
assert res2 == 20, res2

# walk_trade: long, stop 1, target 1.5R
cl = np.array([100, 100.5, 101, 101.6, 101.0])
h = cl + .2; l = cl - .2
ex, r, b, mfe, mae = walk_trade(h, l, cl, 0, 1, 1.0, 10)
assert ex == "tp" and r == 1.5 and b == 3 and mfe >= 1.5 and mae < .5, (ex, r, b, mfe, mae)
ex, r, *_ = walk_trade(h, l, cl, 0, -1, 1.0, 10)
assert ex == "sl" and r == -1.0
ex, r, b, *_ = walk_trade(np.array([100, 100.1, 100.2]), np.array([100, 99.9, 99.95]), np.array([100, 100.05, 100.1]), 0, 1, 1.0, 2)
assert ex == "time" and abs(r - 0.1) < 1e-9 and b == 2

# the "studied trade" filter (v_studied): lab-rated confirmation, nothing against, no losing detector
con = sqlite3.connect(":memory:"); con.executescript(SCHEMA)
con.executemany("INSERT INTO lab_evidence VALUES (?,?,?,?,?,?)", [("good", "SMC", "1h", 400, .05, "positive, not proven"),
                ("bad", "MA", "1h", 900, -.08, "loses"), ("few", "Gann", "all", 12, .3, "too few")])
ctx, out = {}, ("tp", 1.5, 1.4, 3, 180, 1.6, .2, "sl", -1.0)
def idea(src, key="telegram"):
    return {"source": src, "symbol": "BTC-USDT", "tf": "1h", "ts": 0, "time": "", "side": 1, "entry": 1, "stop": 0, "target": 2,
            "key": key, "school": "", "taken": 1, "status": "signal", "oos": None, "ext_id": None}
cases = {1: ([("good", "SMC", 1)], 1), 2: ([("good", "SMC", 1), ("x", "desk doubt", -1)], 0), 3: ([("good", "SMC", 1), ("bad", "MA", 1)], 0),
         4: ([("few", "Gann", 1)], 0), 5: ([], 0)}
for k, (votes, _) in cases.items():
    insert(con, idea("telegram"), ctx, out, votes)
insert(con, idea("lab", "bad"), ctx, out, [("good", "SMC", 1)])   # its own detector loses -> not studied
got = dict(con.execute("SELECT idea_id, studied FROM v_studied_flag").fetchall())
assert got == {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}, got
assert [r[0] for r in con.execute("SELECT id FROM v_studied")] == [1]
edge = {(s_, st): n for s_, st, n, *_ in con.execute("SELECT * FROM v_studied_edge")}
assert edge == {("lab", 0): 1, ("telegram", 0): 4, ("telegram", 1): 1}, edge

# lab votes for a desk / Telegram idea: detectors on the same symbol + bar, signed by side
ev = pd.DataFrame({"sym": ["BTC-USDT"] * 3, "ts": [1000, 1000, 2000], "key": ["good", "bad", "good"], "d": [1, -1, 1]})
evg = {(s_, int(t)): g for (s_, t), g in ev.groupby(["sym", "ts"])}
assert sorted(v[0::2] for v in lab_votes(evg, "BTC-USDT", 1000, 1)) == [("bad", -1), ("good", 1)]
assert lab_votes(evg, "BTC-USDT", 3000, 1) == [] and lab_votes({}, "X", 1, 1) == []

# Telegram log lines: damaged or plan-less lines are skipped
f = Path(tempfile.mkdtemp()) / "log.jsonl"
f.write_text(json.dumps({"t": 1, "symbol": "BTC-USDT", "dir": "bullish", "entry": 1, "stop": .9, "tp1": 1.2}) + "\n{broken\n"
             + json.dumps({"t": 2, "symbol": "ETH-USDT", "dir": "bullish", "entry": 1}) + "\n")
assert [r["symbol"] for r in telegram_records(f)] == ["BTC-USDT"]
assert _args(["j.sqlite"]) == {"desk": "j.sqlite", "telegram": None}
assert _args(["--telegram", "l.jsonl", "--desk", "j"]) == {"desk": "j", "telegram": "l.jsonl"}
print("ok trade_db")
