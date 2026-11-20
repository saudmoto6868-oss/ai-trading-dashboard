"""'6868 brain' - a READ-ONLY MCP server (stdio) so any AI client (Claude Code / Desktop, ChatGPT via a bridge, OpenClaw's
Jarvis / Hermes, Cursor) reads the same numbers: the trade-review database, the weekly strategy lab, and the meeting room.

It is not a hosted server: the client starts this script on this computer when it needs it and talks over stdin/stdout.
Standard library only. Nothing here writes, trades, or calls the network.

Tools
  trade_review_schema()                 tables / views of research/trade_db/trade_review.sqlite
  query_trade_review(sql, limit=200)    one SELECT / WITH statement, read-only connection, row cap, 5 s time cap
  lab_card(keys, tf)                    weekly-lab row per detector (n, net R, t, IS / OOS, verdict) - same as the Setup Card
  lab_rows(key="", school="", tf="")    rows of data/strategy_lab.json filtered (max 100)
  meeting_room(sections=3)              the last N sections of docs/MEETING_ROOM.md
  owner_pending()                       the latest "waiting on the owner" list from the meeting room
Rule for clients: numbers in an answer must come from these tools (the ai-desk Auditor rule)."""
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
DB = ROOT / "research" / "trade_db" / "trade_review.sqlite"
LAB = ROOT / "data" / "strategy_lab.json"
ROOM = ROOT / "docs" / "MEETING_ROOM.md"
PROTO = "2025-06-18"
MAX_ROWS = 1000


def _text(obj):
    return {"content": [{"type": "text", "text": obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, indent=1, default=str)}]}


def _ro():
    if not DB.exists():
        raise ValueError(f"no trade-review database yet: build it with `python -m research.trade_db.build_db` ({DB.name} missing)")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.execute("PRAGMA query_only = ON")
    return con


def trade_review_schema():
    con = _ro()
    rows = con.execute("SELECT type, name, sql FROM sqlite_master WHERE type IN ('table','view') ORDER BY type, name").fetchall()
    con.close()
    return [{"type": t, "name": n, "sql": s} for t, n, s in rows]


def query_trade_review(sql, limit=200):
    q = (sql or "").strip().rstrip(";").strip()
    if not re.match(r"(?is)^(select|with)\b", q) or ";" in q:
        raise ValueError("only one SELECT / WITH statement is allowed")
    limit = max(1, min(int(limit or 200), MAX_ROWS))
    con = _ro(); t0 = time.time()
    con.set_progress_handler(lambda: 1 if time.time() - t0 > 5 else 0, 10000)   # abort queries longer than 5 s
    cur = con.execute(q)
    cols = [d[0] for d in cur.description or []]
    rows = cur.fetchmany(limit + 1)
    con.close()
    return {"columns": cols, "rows": [list(r) for r in rows[:limit]], "truncated": len(rows) > limit}


def lab_card(keys, tf):
    from modules.lab_tiers import card
    return card(list(keys or []), str(tf or ""))


def lab_rows(key="", school="", tf=""):
    if not LAB.exists():
        raise ValueError("data/strategy_lab.json missing")
    rows = json.loads(LAB.read_text()).get("rows", [])
    out = [r for r in rows if (not key or r.get("key") == key) and (not school or school.lower() in str(r.get("school", "")).lower())
           and (not tf or r.get("tf") == tf)]
    return {"n_rows": len(out), "rows": out[:100]}


def _sections():
    return re.split(r"(?m)^(?=## )", ROOM.read_text(encoding="utf-8"))


def meeting_room(sections=3):
    n = max(1, min(int(sections or 3), 20))
    return "".join(_sections()[-n:])


def owner_pending():
    hits = [s for s in _sections() if "مستني المالك" in s.split("\n", 1)[0] or "waiting on the owner" in s.split("\n", 1)[0].lower()]
    return hits[-1] if hits else "no owner-pending list found in the meeting room"


TOOLS = {
    "trade_review_schema": (trade_review_schema, "Tables and views of the trade-review database (ideas, context, votes, outcomes).", {}),
    "query_trade_review": (query_trade_review, "Run ONE read-only SELECT/WITH on the trade-review database. Max 1000 rows, 5 s.",
                           {"sql": {"type": "string"}, "limit": {"type": "integer", "default": 200}}),
    "lab_card": (lab_card, "Weekly-lab evidence per detector key on a timeframe (n, net R after cost, t, IS/OOS, verdict).",
                 {"keys": {"type": "array", "items": {"type": "string"}}, "tf": {"type": "string"}}),
    "lab_rows": (lab_rows, "Rows of the weekly strategy lab filtered by detector key, school and timeframe (max 100).",
                 {"key": {"type": "string"}, "school": {"type": "string"}, "tf": {"type": "string"}}),
    "meeting_room": (meeting_room, "The last N sections of the project meeting room (docs/MEETING_ROOM.md).",
                     {"sections": {"type": "integer", "default": 3}}),
    "owner_pending": (owner_pending, "The latest list of items waiting on the owner (keys, approvals, decisions).", {}),
}
REQUIRED = {"query_trade_review": ["sql"], "lab_card": ["keys", "tf"]}


def handle(msg):
    """One JSON-RPC message -> response dict, or None for notifications."""
    mid, method, params = msg.get("id"), msg.get("method", ""), msg.get("params") or {}
    if mid is None:   # notification (e.g. notifications/initialized)
        return None
    if method == "initialize":
        res = {"protocolVersion": params.get("protocolVersion") or PROTO, "capabilities": {"tools": {"listChanged": False}},
               "serverInfo": {"name": "6868-brain", "version": "0.1.0"},
               "instructions": "Read-only access to the 6868 trading research. Numbers in answers must come from these tools. Never place trades."}
    elif method == "ping":
        res = {}
    elif method == "tools/list":
        res = {"tools": [{"name": n, "description": d, "inputSchema": {"type": "object", "properties": p, "required": REQUIRED.get(n, [])}}
                         for n, (_, d, p) in TOOLS.items()]}
    elif method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        if name not in TOOLS:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"unknown tool {name}"}}
        try:
            res = _text(TOOLS[name][0](**args))
        except Exception as e:   # tool errors go back to the model as text, not as a protocol error
            res = {"content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}], "isError": True}
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": res}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            out = handle(json.loads(line))
        except json.JSONDecodeError:
            out = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        if out is not None:
            sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n"); sys.stdout.flush()


if __name__ == "__main__":
    main()
