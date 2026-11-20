"""2.6 journal: every 2.6 setup becomes one journal record, with a rule-based review.

Pure logic (no Streamlit, no network). Input = the plays from modules/two_six_chart.setups().
Output = JSON-lines records in data/two_six/journal.jsonl (git-ignored, like data/spot/).

Each record:
  id            symbol|tf|kind|side|known-bar time  (one setup = one row, updated in place when its status changes)
  status        waiting / expired / open / open (TP1 hit) / TP2 / stopped / TP1 then stop
  outcome_r     +2 (TP2), -1 (stopped), None while open / waiting / expired / TP1 then stop (that rule is not confirmed)
  why_taken     the rule-based reasons the setup was (or could be) taken
  why_rejected  the reasons it was not taken (expired, not filled yet, ...)
  best_now      True for the ONE live (waiting / open) setup nearest to the last price: "best opportunity now"
  review        one-line review from the rules above
  followup      what to check next
  note          free text the owner writes; kept when the record is updated

Honest limits: stop / TP rules are PROVISIONAL (see two_six_chart), the sample is small, costs are not included.
Nothing here is a win rate. The summary prints n and says "not evidence" below 30 closed trades.
"""
from __future__ import annotations

import json
from pathlib import Path

PATH = Path("data/two_six/journal.jsonl")
MIN_EVIDENCE_N = 30
LIVE = ("waiting", "open", "open (TP1 hit)")
CLOSED_CLEAN = {"TP2": 2.0, "stopped": -1.0}


def _rec_id(symbol, tf, play, time_key):
    return f"{symbol}|{tf}|{play['kind']}|{play['side']}|{time_key}"


def _outcome(status):
    return CLOSED_CLEAN.get(status)


def _reasons(play, wait):
    """Why it was taken / rejected, from the play itself (no hindsight: only what was known at the time)."""
    taken, rejected = [], []
    kind, side = play["kind"], play["side"]
    taken.append(f"{kind} {side}: leg measured, entry = leg / ratio from the pool or pivot")
    if kind == "H2":
        taken.append("liquidity pool swept before the entry (sweep bar known)")
    if play.get("fill") is not None:
        taken.append(f"filled at {play['entry']:.2f}")
    else:
        if play["status"] == "expired":
            rejected.append(f"no fill within {wait} bars: expired")
        elif play["status"] == "waiting":
            rejected.append("not filled yet (waiting)")
    if play["status"] == "stopped":
        rejected.append("stop hit before TP1")
    if play["status"] == "TP1 then stop":
        rejected.append("TP1 reached, then stop: partial-exit rule not confirmed")
    return taken, rejected


def _review(play):
    s = play["status"]
    if s == "TP2":
        return "won: TP2 reached (+2R on the provisional plan)"
    if s == "stopped":
        return "lost: stop hit before TP1 (-1R on the provisional plan)"
    if s == "TP1 then stop":
        return "unresolved: TP1 hit, then stop. The rule for this case is not confirmed"
    if s == "expired":
        return "not taken: the entry never filled inside the wait window"
    if s == "waiting":
        return "live: waiting for the entry"
    return "live: filled, still open"


def _followup(play, wait):
    s = play["status"]
    if s == "waiting":
        return f"watch the entry {play['entry']:.2f} for up to {wait} bars"
    if s in ("open", "open (TP1 hit)"):
        return f"manage to stop {play['stop']:.2f} / TP1 {play['tp1']:.2f} / TP2 {play['tp2']:.2f}"
    if s == "stopped":
        return "check: was the leg or the pool the wrong one? (log it, do not change the rule on one trade)"
    if s == "expired":
        return "check: did the price come back to the entry after the window? (log it)"
    return "record the rule question for the owner: how to handle TP1 then stop"


def _nearest_live(plays, last_price):
    live = [p for p in plays if p["status"] in LIVE]
    if not live or last_price is None:
        return None
    return min(live, key=lambda p: abs(p["entry"] - last_price))


def build_records(plays, times, symbol, tf, last_price=None, wait=80):
    """One record per play. times[i] = timestamp (string) of bar i. last_price = latest close (for best_now)."""
    best = _nearest_live(plays, last_price)
    out = []
    for p in plays:
        t = str(times[p["known"]])
        taken, rejected = _reasons(p, wait)
        out.append({
            "id": _rec_id(symbol, tf, p, t), "symbol": symbol, "tf": tf, "time": t,
            "kind": p["kind"], "side": p["side"], "status": p["status"],
            "entry": round(p["entry"], 4), "stop": round(p["stop"], 4),
            "tp1": round(p["tp1"], 4), "tp2": round(p["tp2"], 4),
            "outcome_r": _outcome(p["status"]),
            "why_taken": taken, "why_rejected": rejected,
            "best_now": best is p,
            "review": _review(p), "followup": _followup(p, wait),
            "strategy": f"2.6 {p['kind']} · ratio leg/u · provisional stop 1u, TP1 1R, TP2 2R",
            "note": "",
        })
    return out


def load(path: Path = PATH) -> list[dict]:
    if not Path(path).exists():
        return []
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def upsert(records: list[dict], path: Path = PATH) -> int:
    """Insert new records; update existing ones by id but keep the owner's note. Returns the number of rows that changed."""
    path = Path(path)
    current = {r["id"]: r for r in load(path)}
    changed = 0
    for rec in records:
        old = current.get(rec["id"])
        if old is not None:
            rec["note"] = old.get("note", "")
            if old == rec:
                continue
        current[rec["id"]] = rec
        changed += 1
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in sorted(current.values(), key=lambda r: r["time"]):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return changed


def summary(rows: list[dict]) -> dict:
    closed = [r["outcome_r"] for r in rows if r.get("outcome_r") is not None]
    n = len(closed)
    wins = sum(1 for r in closed if r > 0)
    return {
        "rows": len(rows), "closed": n, "wins": wins,
        "avg_r": round(sum(closed) / n, 3) if n else None,
        "live": sum(1 for r in rows if r["status"] in LIVE),
        "expired": sum(1 for r in rows if r["status"] == "expired"),
        "evidence": n >= MIN_EVIDENCE_N,
        "text": (f"n={n} closed · wins {wins} · avg {round(sum(closed) / n, 2) if n else '–'} R (provisional plan, no costs)"
                 + ("" if n >= MIN_EVIDENCE_N else f" · NOT EVIDENCE below n={MIN_EVIDENCE_N}")),
    }
