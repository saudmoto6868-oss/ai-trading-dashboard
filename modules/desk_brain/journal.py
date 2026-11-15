"""Paper journal: every idea the desk proposes is stored and later graded against real
price movement. Nothing here talks to a broker."""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone

import pandas as pd

from .config import DATA_DIR, UNIVERSE
from .data import sources

DB = DATA_DIR / "journal.sqlite"
_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS ideas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TEXT, symbol TEXT, direction INTEGER, status TEXT,
  entry REAL, stop REAL, t1 REAL, t2 REAL, rr REAL,
  bias REAL, confidence INTEGER, components TEXT, rationale TEXT, doubts TEXT,
  data_source TEXT, filled TEXT, closed TEXT, result_r REAL, note TEXT
);
"""
# Columns added for the framework (reasons that fired, stars, scenarios, eligible accounts).
EXTRA = {"stars": "INTEGER", "reasons": "TEXT", "scenarios": "TEXT", "accounts": "TEXT",
         "current_stop": "REAL", "managed_at": "TEXT", "events": "TEXT", "partial": "INTEGER", "r_t1": "REAL"}
# status: pending (waiting for limit fill) -> open -> win | loss | expired


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute(SCHEMA)
    have = {r[1] for r in c.execute("PRAGMA table_info(ideas)")}
    for k, t in EXTRA.items():
        if k not in have:
            c.execute(f"ALTER TABLE ideas ADD COLUMN {k} {t}")
    return c


def _accounts_text(acc) -> str:
    """Risk agent gives {"acc2": lots, ...}; older rows give a list of ids. None / junk -> ""."""
    if isinstance(acc, dict):
        return ",".join(str(k) for k, v in acc.items() if isinstance(v, (int, float)) and v > 0)
    if isinstance(acc, (list, tuple)):
        return ",".join(str(x) for x in acc)
    return ""


def add(idea: dict) -> int | None:
    """Store an idea unless the same symbol/direction is already live."""
    with _lock, _conn() as c:
        dup = c.execute("SELECT id FROM ideas WHERE symbol=? AND direction=? AND status IN ('pending','open')",
                        (idea["symbol"], idea["direction"])).fetchone()
        if dup:
            return None
        now = datetime.now(timezone.utc).isoformat()
        status = "open" if idea["order"] == "market" else "pending"
        cur = c.execute(
            "INSERT INTO ideas (created,symbol,direction,status,entry,stop,t1,t2,rr,bias,confidence,components,"
            "rationale,doubts,data_source,filled,stars,reasons,scenarios,accounts) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (now, idea["symbol"], idea["direction"], status, idea["entry"], idea["stop"], idea["t1"], idea["t2"],
             idea["rr"], idea["bias"], idea["confidence"], json.dumps(idea["components"]),
             idea["rationale"], json.dumps(idea["doubts"], ensure_ascii=False), ",".join(idea["source"]),
             now if status == "open" else None, idea.get("stars", 0),
             json.dumps(idea.get("reasons", []), ensure_ascii=False),
             json.dumps(idea.get("scenarios", []), ensure_ascii=False), _accounts_text(idea.get("accounts"))))
        return cur.lastrowid


def rows(limit: int = 200) -> list[dict]:
    with _lock, _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM ideas ORDER BY id DESC LIMIT ?", (limit,))]


def update_outcomes() -> int:
    """Walk hourly bars after each live idea and mark fills, stops and targets.
    Conservative: if stop and target fall inside the same bar, count the stop."""
    changed = 0
    for r in [x for x in rows(500) if x["status"] in ("pending", "open")
              and not x.get("managed_at")]:  # 5m manager owns rows it has touched
        df, _ = sources.prices(UNIVERSE[r["symbol"]]["yf"], "1h")
        d = r["direction"]
        start = pd.Timestamp(r["filled"] or r["created"])
        bars = df[df.index > start]
        status, filled, closed, res = r["status"], r["filled"], None, None
        for ts, b in bars.iterrows():
            if status == "pending":
                if ts > pd.Timestamp(r["created"]) + timedelta(hours=24):
                    status, closed = "expired", ts.isoformat()
                    break
                if b["Low"] <= r["entry"] <= b["High"]:
                    status, filled = "open", ts.isoformat()
                continue
            hit_stop = b["Low"] <= r["stop"] if d > 0 else b["High"] >= r["stop"]
            hit_t1 = b["High"] >= r["t1"] if d > 0 else b["Low"] <= r["t1"]
            if hit_stop:
                status, closed, res = "loss", ts.isoformat(), -1.0
                break
            if hit_t1:
                status, closed, res = "win", ts.isoformat(), r["rr"]
                break
        if status != r["status"] or filled != r["filled"]:
            with _lock, _conn() as c:
                c.execute("UPDATE ideas SET status=?, filled=?, closed=?, result_r=? WHERE id=?",
                          (status, filled, closed, res, r["id"]))
            changed += 1
    return changed


def stats() -> dict:
    done = [r for r in rows(1000) if r["status"] in ("win", "loss")]
    if not done:
        return {"closed": 0}
    wins = [r for r in done if r["status"] == "win"]
    out = {"closed": len(done), "win_rate": round(100 * len(wins) / len(done)),
           "avg_r": round(sum(r["result_r"] for r in done) / len(done), 2),
           "total_r": round(sum(r["result_r"] for r in done), 2)}
    # Which bias component tends to agree with winners? First step of the learning loop.
    agree = {}
    for r in done:
        comp = json.loads(r["components"])
        for k, v in comp.items():
            a = agree.setdefault(k, {"agree_win": 0, "agree": 0})
            if v * r["direction"] > 0.1:
                a["agree"] += 1
                a["agree_win"] += r["status"] == "win"
    out["component_hit_rate"] = {k: round(100 * v["agree_win"] / v["agree"]) if v["agree"] else None
                                 for k, v in agree.items()}
    # Do more stars really mean better trades? (framework: "score should reflect quality")
    by_star = {}
    for r in done:
        b = by_star.setdefault(r.get("stars") or 0, [0, 0])
        b[0] += 1
        b[1] += r["status"] == "win"
    out["win_rate_by_stars"] = {k: round(100 * w / n) for k, (n, w) in sorted(by_star.items())}
    return out


def save_managed(trade_id: int, st: dict) -> None:
    """Persist the state returned by manage.manage (paper only)."""
    with _lock, _conn() as c:
        c.execute("UPDATE ideas SET status=?, filled=?, closed=?, result_r=?, current_stop=?, managed_at=?, "
                  "events=?, partial=?, r_t1=? WHERE id=?",
                  (st["status"], st["filled"], st["closed"], st["result_r"], st["current_stop"], st["managed_at"],
                   json.dumps(st["events"]), int(st["partial"]), st["r_t1"], trade_id))
