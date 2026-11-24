"""Daily-calls review: the gate (n, Wilson bound vs 40 % break-even), cautious ranking, observations, report file (synthetic)."""
import os, sys, json, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import forecast_review as fr

assert fr.verdict(10, 0.9, 1.0).startswith("not evidence")
assert fr.verdict(50, 0.6, 0.8).startswith("too small")
assert fr.verdict(150, 0.45, 0.6).startswith("beats")
assert fr.verdict(150, 0.2, 0.35) == "below break-even"
assert fr.verdict(150, 0.35, 0.45) == "undecided"

tmp = Path(tempfile.mkdtemp())
res = []
for i in range(120):                       # AAA: 60 % wins over 120 calls
    res.append({"id": f"AAA|{i}", "symbol": "AAA", "class": "Crypto", "side": "long", "outcome": "win" if i % 5 < 3 else "loss", "R": 1.5 if i % 5 < 3 else -1.0})
for i in range(40):                        # BBB: 25 % wins over 40 calls
    res.append({"id": f"BBB|{i}", "symbol": "BBB", "class": "Metals", "side": "short", "outcome": "win" if i % 4 == 0 else "loss", "R": 1.5 if i % 4 == 0 else -1.0})
for i in range(5):                         # CCC: too few
    res.append({"id": f"CCC|{i}", "symbol": "CCC", "class": "Forex", "side": "long", "outcome": "timeout", "R": 0.0})
(tmp / "outcomes.jsonl").write_text("\n".join(json.dumps(r) for r in res), encoding="utf8")
for sym in ("AAA", "BBB", "CCC"):            # the calls behind the outcomes, on daily bars (only those count)
    (tmp / f"{sym}.jsonl").write_text("\n".join(json.dumps({"id": r["id"], "symbol": sym, "tf": "1d"}) for r in res if r["symbol"] == sym), encoding="utf8")

t = {r["key"]: r for r in fr.table(fr.rows(tmp), "symbol")}
assert t["AAA"]["verdict"].startswith("beats") and t["BBB"]["verdict"].startswith("too small") and t["CCC"]["verdict"].startswith("not evidence")
c = fr.candidates(fr.rows(tmp))
assert [r["key"] for r in c] == ["AAA", "BBB"]          # ranked by the lower bound; CCC (n < 30) is not a candidate
txt = fr.write(folder=tmp, out=tmp / "REVIEW.md")
assert "Candidates to study next" in txt and "AAA" in txt and "not trades" in txt.lower() or "not trades" in txt
assert fr.write(folder=Path(tempfile.mkdtemp()), out=tmp / "R2.md").count("no scored calls yet") >= 1
print("test_forecast_review: OK")

# journal trades go through the same gate (never-filled trades are not losses); a missing journal gives no rows
jp = tmp / "trades.json"
jt = {f"t{i}": {"id": f"t{i}", "symbol": "BTC-USDT", "dir": "bullish", "ttype": "swing", "status": "tp" if i % 2 else "sl",
               "exits": [{"level": "tp1" if i % 2 else "sl", "t": 0, "price": 1, "r": 1.5 if i % 2 else -1.0}]} for i in range(6)}
jt["nf1"] = {"id": "nf1", "symbol": "BTC-USDT", "dir": "bullish", "status": "nf"}
jp.write_text(json.dumps(jt), encoding="utf8")
jr = fr.journal_rows(jp)
assert len(jr) == 6 and sum(1 for r in jr if r["outcome"] == "win") == 3
assert fr.journal_rows(tmp / "missing.json") == []
txt2 = fr.write(folder=tmp, out=tmp / "R3.md", journal_path=jp)
assert "Journal trades" in txt2 and "BTC-USDT" in txt2 and "not evidence" in txt2
print("test_forecast_review journal: OK")
