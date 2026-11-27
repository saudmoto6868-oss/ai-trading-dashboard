"""Trade journal store: upsert validation, tp1 -> runner -> tp2 flow, stop, never-filled, atomic save, stats, post-mortem.
Plain script: python3 tests/test_trade_journal.py"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import trade_journal as J  # noqa: E402

tmp = Path(tempfile.mkdtemp()) / "trades.json"


def rec(i, d="bullish", **kw):
    base = {"id": i, "symbol": "XAUUSD", "dir": d, "tfk": "1h", "ttype": "bounce", "entry": 100.0, "sl": 99.0,
            "tp1": 101.0, "tp2": 102.0, "tp3": 103.0, "score": 8, "max": 10, "fill": True}
    base.update(kw)
    return base


# 1. validation at the boundary
for bad in ({"id": "", "dir": "bullish", "entry": 1, "sl": 0, "tp1": 2},
            {"id": "x", "dir": "sideways", "entry": 1, "sl": 0, "tp1": 2},
            {"id": "x", "dir": "bullish", "entry": "1", "sl": 0, "tp1": 2},
            {"id": "x", "dir": "bullish", "entry": float("nan"), "sl": 0, "tp1": 2}):
    try:
        J.upsert(bad, tmp)
        raise SystemExit(f"FAIL accepted bad record {bad}")
    except ValueError:
        pass
print("ok validation")

# 2. winner: tp1 -> part, then tp2 -> tp (runner exits at tp2)
J.upsert(rec("w1"), tmp)
J.add_exit("w1", "tp1", 1000, 101.0, 1.0, tmp)
assert J._load(tmp)["w1"]["status"] == "part"
J.add_exit("w1", "tp2", 2000, 102.0, 2.0, tmp)
assert J._load(tmp)["w1"]["status"] == "part"  # tp3 still open: the runner keeps going
J.add_exit("w1", "tp3", 3000, 103.0, 3.0, tmp)
w = J._load(tmp)["w1"]
assert w["status"] == "tp" and round(J.r_total(w), 3) == 6.0, w
# repeated exit after final is ignored
J.add_exit("w1", "sl", 4000, 99.0, -1.0, tmp)
assert J.r_total(J._load(tmp)["w1"]) == 6.0
print("ok tp1 -> tp2 -> tp3")

# 3. loser: tp1 then stop on the runner (the case the owner asked about)
J.upsert(rec("l1"), tmp)
J.add_exit("l1", "tp1", 1000, 101.0, 0.5, tmp)
J.add_exit("l1", "sl", 1500, 100.0, 0.0, tmp)  # runner stopped at break-even
l = J._load(tmp)["l1"]
assert l["status"] == "sl"
pm = J.postmortem(l)
assert any("runner" in x for x in pm["why"]), pm
print("ok postmortem tp1 then stop:", pm["next"])

# 4. plain stop with warnings at entry
J.upsert(rec("l2", ctx={"of": "against", "news": True, "oi": "shorts"}, score=5), tmp)
J.add_exit("l2", "sl", 2000, 99.0, -1.0, tmp)
pm2 = J.postmortem(J._load(tmp)["l2"])
assert pm2["warnings"] == 4 and pm2["next"].startswith("skip or wait"), pm2
print("ok postmortem warnings:", pm2["warnings"])

# 5. never filled is not a loss
J.upsert(rec("n1", fill=False), tmp)
J.finish("n1", "nf", 5000, 0.0, "", tmp)
assert J._load(tmp)["n1"]["status"] == "nf"
st = J.stats(tmp)
assert st["n"] == 3  # w1, l1, l2 closed; n1 excluded, n1 is not a trade
assert st["evidence"] is False
print("ok never-filled excluded from stats")

# 6. reason text saved and capped
J.finish("l2", "sl", 2000, -1.0, "x" * 5000, tmp)
assert len(J._load(tmp)["l2"]["reason"]) <= 2000
print("ok reason cap")

# 7. browser snapshots: idempotent, status only moves forward, final not overwritten
snap = {"id": "s1", "symbol": "BTC", "dir": "bearish", "entry": 50.0, "sl": 51.0, "tp1": 49.0, "tfk": "1h", "ttype": "bounce", "status": "open", "fill": True, "t0": 7000}
J.apply_snapshot(snap, tmp)
J.apply_snapshot(snap, tmp)  # same snapshot twice: still one record
assert len([k for k in J._load(tmp) if k == "s1"]) == 1 and J._load(tmp)["s1"]["status"] == "open"
J.apply_snapshot({"id": "s1", "status": "sl", "r": -1.0, "t1": 8000}, tmp)
J.apply_snapshot({"id": "s1", "status": "tp", "r": 2.0, "t1": 9000}, tmp)  # later "tp" must not overwrite the stop
s1 = J._load(tmp)["s1"]
assert s1["status"] == "sl" and J.r_total(s1) == -1.0 and len(s1["exits"]) == 1, s1
# add_exit same level twice books once
J.upsert(rec("d1"), tmp)
J.add_exit("d1", "tp1", 1, 101.0, 1.0, tmp)
J.add_exit("d1", "tp1", 1, 101.0, 1.0, tmp)
assert len(J._load(tmp)["d1"]["exits"]) == 1
print("ok snapshots")

# 8. batch merge: one write, bad items skipped, re-run idempotent
n = J.apply_snapshots([{"id": "b1", "dir": "bullish", "entry": 1.0, "sl": 0.9, "tp1": 1.1, "t0": 1},
                       {"id": "b2", "dir": "sideways", "entry": 1, "sl": 0, "tp1": 2},
                       {"id": "b1", "status": "tp", "r": 1.5, "t1": 5}], tmp)
assert n == 2 and J._load(tmp)["b1"]["status"] == "tp" and "b2" not in J._load(tmp)
assert J.apply_snapshots([{"id": "b1", "status": "tp", "r": 1.5, "t1": 5}], tmp) == 1
assert J._load(tmp)["b1"]["r_total"] == 1.5
print("ok batch merge")

# 9. analyze: times in UTC, missed targets, post-mortem for a stop
a = J.analyze(J._load(tmp)["l1"])
assert a["side"] == "long" and a["exits"][0]["level"] == "tp1" and a["set_utc"] and a["postmortem"] is not None
assert "tp2" in a["missed"] and "tp1" not in a["missed"], a
print("ok analyze")

# 10. atomic save leaves no tmp file behind
assert not tmp.with_suffix(".tmp").exists()
print("ALL OK")

# partial exits from the browser: tp1 books 1/3, runner stays "part", tp2/tp3 finish it; stop after tp1 books the rest at -1R
pe = Path(tempfile.mkdtemp()) / "pe.json"
J.apply_snapshot(rec("pe1", tp1=101.0, tp2=102.0, tp3=103.0, status="open", fill=True, t0=1_800_000_000_000, r=0.33,
                     exits=[{"level": "tp1", "t": 1, "price": 101.0, "r": 1 / 3}]), pe)
t = J._load(pe)["pe1"]
assert t["status"] == "part" and abs(J.r_total(t) - 1 / 3) < 1e-9, t
J.apply_snapshot(rec("pe1", status="sl", r=-0.67, t1=5, exits=[{"level": "tp1", "t": 1, "price": 101.0, "r": 1 / 3},
                                                             {"level": "sl", "t": 5, "price": 99.0, "r": -2 / 3}]), pe)
t = J._load(pe)["pe1"]
assert t["status"] == "sl" and abs(J.r_total(t) - (-1 / 3)) < 1e-9, t
J.apply_snapshot(rec("pe2", tp1=101.0, tp2=102.0, tp3=103.0, status="open", t0=1_800_000_000_000, r=0.0,
                     exits=[{"level": "tp1", "t": 1, "price": 101.0, "r": 1 / 3}, {"level": "tp2", "t": 2, "price": 102.0, "r": 2 / 3}]), pe)
J.apply_snapshot(rec("pe2", status="tp", r=2.0, t1=9, exits=[{"level": "tp1", "t": 1, "price": 101.0, "r": 1 / 3},
                                                             {"level": "tp2", "t": 2, "price": 102.0, "r": 2 / 3},
                                                             {"level": "tp3", "t": 9, "price": 103.0, "r": 1.0}]), pe)
t = J._load(pe)["pe2"]
assert t["status"] == "tp" and abs(J.r_total(t) - 2.0) < 1e-9 and len(t["exits"]) == 3, t
print("ok partial exits merge")
