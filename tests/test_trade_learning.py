"""Journal learning: factor table, evidence gate (n >= 30), lesson candidates, trade table. Synthetic trades only.
Plain script: python3 tests/test_trade_learning.py"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules import trade_learning as L  # noqa: E402
from modules import trade_journal as TJ  # noqa: E402

tmp = Path(tempfile.mkdtemp())


def mk(i, win, against):
    tr = {"id": f"t{i}", "symbol": "XAUUSD", "dir": "bullish", "tfk": "1h", "ttype": "bounce", "entry": 100.0, "sl": 99.0,
          "tp1": 101.0, "score": 8, "max": 10, "t0": 1_800_000_000_000 + i * 3600_000, "fill": True,
          "ctx": {"of": "against" if against else "agree", "news": False, "fund": None, "oi": None, "ses": "NY AM KZ"},
          "tags": ["bounce"], "exits": []}
    if win:
        tr["exits"] = [{"level": "tp1", "t": tr["t0"] + 1000, "price": 101.0, "r": 1.0}]
        tr["status"] = "tp"
    else:
        tr["exits"] = [{"level": "sl", "t": tr["t0"] + 1000, "price": 99.0, "r": -1.0}]
        tr["status"] = "sl"
    return tr


# 60 closed trades (30 per side of the order-flow factor): "against" loses, "agree" wins 3 of 4
trades = []
for i in range(60):
    against = i % 2 == 0
    win = (not against) and (i % 4 != 1)  # agree: 3 of 4 win ; against: all lose
    trades.append(mk(i, win, against))
res = L.learn(trades)
assert res["evidence"] is True and res["n_closed"] == 60, res
row = {r["factor"]: r for r in res["table"]}
assert row["of:against"]["verdict"] == "avoid" and row["of:agree"]["verdict"] == "prefer", row
assert any("require confirmation" in c["rule"] and "of:against" in c["rule"] for c in res["candidates"]), res["candidates"]
assert all(c["status"] == "candidate" for c in res["candidates"])
print("ok learn avoid/prefer:", row["of:against"]["win_pct"], "vs", row["of:agree"]["win_pct"])

# school readings: pros/cons labels normalised (numbers stripped), level distance in ATR
tr = mk(999, True, False)
tr["ctx"]["schools"] = {"verdict": "TAKE", "pros": [[3, "Limit order at 1234.5 near VWAP"]], "cons": [[2, "Price 12 pts from HTF level"]], "vetoes": []}
tr["ctx"]["snap"] = {"regime": "trend", "atr": 10.0, "lv": [{"p": 100.5, "k": "S"}, {"p": 120, "k": "R"}]}
fs = L.factors(tr)
assert "pro:Limit order at near VWAP" in fs and "con:Price pts from HTF level" in fs, fs
assert "level:at" in fs and "regime:trend" in fs and "verdict:TAKE" in fs, fs
print("ok school factors:", [f for f in fs if f.startswith(("pro", "con", "level"))])

# under 30 trades: everything is "not evidence", no candidates
small = L.learn(trades[:10])
assert small["evidence"] is False and all(r["verdict"] == "not evidence" for r in small["table"]) and small["candidates"] == []
print("ok evidence gate")

# save and read lessons file
p = tmp / "lessons.json"
L.save_lessons(res, p)
assert p.exists() and "table" in __import__("json").loads(p.read_text(encoding="utf-8"))
print("ok lessons saved")

# trade table: one row per closed trade plus header
tbl = L.trade_table(trades[:3])
assert tbl.count("\n") == 4 and "| UTC set |" in tbl, tbl
print("ok trade table rows:", tbl.count("\n") - 1)
print("ALL OK")

# brain suggestions: read-only, only when evidence, capped; review text shows them
from modules import brain as B  # noqa: E402
sp = tmp / "lessons_s.json"
assert L.suggestions(tmp / "missing.json") == []
L.save_lessons(res, sp)
sug = L.suggestions(sp, k=2)
assert 0 < len(sug) <= 2 and all(s.endswith("[candidate]") for s in sug), sug
L.save_lessons(L.learn(trades[:10]), sp)
assert L.suggestions(sp) == [], "under n=30 must give no suggestions"
rv = B.review_text([], {}, lessons=["take this setup when of:agree [candidate]"])
assert "take this setup" in rv and "غير مطبّقة" in rv, rv
print("ok brain suggestions:", len(sug))
print("ALL OK 2")
