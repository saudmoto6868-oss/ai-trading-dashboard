"""Write the journal review for the meeting room: stats, lesson candidates, and one row per closed trade.
Usage: python3 scripts/journal_report.py   -> data/journal/report.md (git-ignored: data/)"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from modules import trade_journal as TJ, trade_learning as TL  # noqa: E402

out = Path("data/journal/report.md")
res = TL.learn()
st = TJ.stats()
lines = [f"# Journal review ({time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC)", "",
         f"Closed trades: {st['n']} · evidence: {'yes' if st['evidence'] else 'NO (under 30 = not evidence)'} · baseline win {res['baseline_win_pct']}%", "",
         "## Lesson candidates (not applied; a person promotes them)"]
lines += [f"- {c['rule']} — {c['evidence']}" for c in res["candidates"]] or ["- none yet"]
lines += ["", "## Closed trades", TL.trade_table()]
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {out} ({st['n']} closed)")
