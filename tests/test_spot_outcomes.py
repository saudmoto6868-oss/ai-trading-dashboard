"""Spot ideas outcome measurement (owner 2026-11-25). Synthetic daily bars and a fake OKX reader; no network.
Run: python3 tests/test_spot_outcomes.py"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import spot_outcomes as O  # noqa: E402

idea = {"day": "2026-11-21", "asset": "BTC", "kind": "discount", "entry": [100.0, 102.0], "stop": 96.0, "targets": [108.0]}   # mid 101, risk 5
bar = lambda l, h: {"t": 0, "l": l, "h": h, "c": (l + h) / 2}
# 1) no fill ever -> open
assert O.measure(idea, [bar(110, 112)] * 5)["status"] == "open"
# 2) fill then target -> win, R = (108-101)/5 - cost
r = O.measure(idea, [bar(101, 103), bar(101, 109)])
assert r["status"] == "closed" and r["result"] == "win" and abs(r["R"] - (7 / 5 - 0.001 * 101 / 5)) < 1e-3, r
# 3) fill then stop -> loss -1R minus cost
r = O.measure(idea, [bar(101, 103), bar(95, 101)])
assert r["result"] == "loss" and r["R"] < -1.0, r
# 4) same bar touches stop and target after fill -> stop first
r = O.measure(idea, [bar(95, 110)])
assert r["result"] == "loss", r
# 5) skipped: not a long, no entry
assert O.measure({**idea, "targets": [90.0]}, [bar(1, 2)])["status"] == "skipped"
assert O.measure({"kind": "avoid", "entry": None, "stop": None, "targets": []}, [])["status"] == "skipped"
# 6) run on a log file with a fake OKX reader: BTC measured, GOLD marked no feed, summary n < 30 is "not evidence"
def fake(url, params):
    # 40 daily bars after 2026-11-21: fill at once and a target on day 3
    import datetime as dt
    base = int(dt.datetime(2026, 11, 21, tzinfo=dt.timezone.utc).timestamp() * 1000)
    rows = []
    for k in range(40, -1, -1):
        t = base + (k + 1) * 86_400_000
        l, h = (101.0, 104.0) if k != 2 else (101.0, 109.0)
        rows.append([str(t), "101", str(h), str(l), "102", "1", "0", "0", "1"])
    return {"data": rows[:100]}
with tempfile.TemporaryDirectory() as d:
    lp, op = os.path.join(d, "log.jsonl"), os.path.join(d, "out.json")
    with open(lp, "w", encoding="utf-8") as f:
        f.write(json.dumps(idea) + "\n")
        f.write(json.dumps({**idea, "asset": "GOLD", "day": "2026-11-21"}) + "\n")
    rep = O.run(log_path=lp, out_path=op, fetch=fake, pages=1)
    by = {(r["asset"]): r for r in rep["rows"]}
    assert by["BTC"]["status"] == "closed" and by["BTC"]["result"] == "win", by["BTC"]
    assert by["GOLD"]["status"] == "no feed"
    assert rep["summary"]["discount"]["verdict"].startswith("not evidence"), rep["summary"]
    assert json.load(open(op, encoding="utf-8"))["rows"]
print("ok spot outcomes: win / loss / stop-first / open / skipped rules; no-feed assets not measured; n<30 = not evidence")
