"""Trade-by-trade review of the ai-desk journal (SQLite `ideas` table, read-only).

For every idea: what it was, why it was taken (reasons / components), what the desk itself doubted, how it ended, and
simple flags a reviewer should look at:
  repeat_after_loss  same symbol + direction re-entered within 48 h after a stop-out
  choch_against      the desk's own doubts said the last CHoCH was against the idea
  room_lt_2r         the desk's own doubts said a structural obstacle sat < 2R away
  tight_stop         stop distance < 0.15 % of price (an approximation; no ATR in the table)
Then counts per flag / stars / confidence. n is tiny, so every table says so.

Usage: python -m research.trade_review.review_desk <journal.sqlite> [out.md]"""
import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path


def load(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM ideas ORDER BY id")]
    con.close()
    return rows


def _ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")[:19]) if s else None


def flags(rows):
    for i, r in enumerate(rows):
        doubts = " ".join(json.loads(r.get("doubts") or "[]"))
        f = []
        prev = [p for p in rows[:i] if p["symbol"] == r["symbol"] and p["direction"] == r["direction"] and p["status"] == "loss"
                and p.get("closed") and _ts(r["created"]) - _ts(p["closed"]) < timedelta(hours=48) and _ts(p["closed"]) <= _ts(r["created"])]
        if prev:
            f.append("repeat_after_loss")
        if "CHoCH" in doubts:
            f.append("choch_against")
        if "المساحة" in doubts or "room" in doubts.lower():
            f.append("room_lt_2r")
        if r["entry"] and r["stop"] and abs(r["entry"] - r["stop"]) / r["entry"] < 0.0015:
            f.append("tight_stop")
        r["flags"] = f
    return rows


def summary(rows, key):
    out = {}
    for r in rows:
        if r["status"] not in ("win", "loss"):
            continue
        ks = r[key] if isinstance(r[key], list) else [r[key]]
        for k in ks or ["(none)"]:
            s = out.setdefault(str(k), {"n": 0, "wins": 0, "sum_r": 0.0})
            s["n"] += 1; s["wins"] += r["status"] == "win"; s["sum_r"] += r["result_r"] or 0.0
    return out


def report(rows):
    closed = [r for r in rows if r["status"] in ("win", "loss")]
    tot = sum(r["result_r"] or 0 for r in closed)
    L = [f"# ai-desk trade review ({len(rows)} ideas, {len(closed)} closed)", "",
         f"Closed: {sum(r['status'] == 'win' for r in closed)} wins / {sum(r['status'] == 'loss' for r in closed)} losses, "
         f"total {tot:+.2f}R, mean {tot / len(closed):+.2f}R per closed idea. **n < 30: not evidence.**" if closed else "No closed ideas.", ""]
    for key, title in (("flags", "Flag"), ("stars", "Stars"), ("confidence", "Confidence"), ("symbol", "Symbol")):
        L += [f"## By {title.lower()}", "", f"| {title} | n | wins | sum R |", "|---|---|---|---|"]
        for k, s in sorted(summary(rows, key).items(), key=lambda kv: -kv[1]["n"]):
            L.append(f"| {k} | {s['n']} | {s['wins']} | {s['sum_r']:+.2f} |")
        L.append("")
    L += ["## Trade by trade", "", "| # | time | symbol | side | status | R | stars | conf | why (desk reasons, first 3) | desk doubts | flags |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        why = "؛ ".join(json.loads(r.get("reasons") or "[]")[:3])
        dbt = "؛ ".join(json.loads(r.get("doubts") or "[]"))
        res = "" if r["result_r"] is None else f"{r['result_r']:+.2f}"
        side = "long" if r["direction"] > 0 else "short"
        L.append(f"| {r['id']} | {(r['created'] or '')[:16]} | {r['symbol']} | {side} | {r['status']} | {res} | "
                 f"{r['stars']} | {r['confidence']} | {why} | {dbt} | {', '.join(r['flags'])} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    rows = flags(load(sys.argv[1]))
    md = report(rows)
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(md, encoding="utf-8")
    print(md)
