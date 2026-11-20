"""tools/mcp_6868/server.py over real stdio: initialize, tools/list, read-only SQL guard, lab_card, meeting room. Plain script."""
import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import tools.mcp_6868.server as S   # noqa: E402

# a tiny database in place of the real one, so the test does not depend on a built DB
tmp = Path(tempfile.mkdtemp()) / "t.sqlite"
con = sqlite3.connect(tmp); con.execute("CREATE TABLE ideas (id INTEGER, key TEXT)"); con.executemany("INSERT INTO ideas VALUES (?,?)", [(i, "k%d" % i) for i in range(5)]); con.commit(); con.close()
S.DB = tmp
assert S.query_trade_review("SELECT COUNT(*) FROM ideas")["rows"] == [[5]]
assert S.query_trade_review("select * from ideas", limit=2)["truncated"] is True
for bad in ("DELETE FROM ideas", "SELECT 1; DROP TABLE ideas", "PRAGMA writable_schema=1", "ATTACH 'x' AS y"):
    try:
        S.query_trade_review(bad); raise AssertionError("allowed: " + bad)
    except ValueError:
        pass
try:   # even a sneaky write through WITH is refused by the read-only connection
    S.query_trade_review("WITH x AS (SELECT 1) INSERT INTO ideas VALUES (9,'z')"); raise AssertionError("write allowed")
except (sqlite3.OperationalError, ValueError):
    pass
assert any(t["name"] == "ideas" for t in S.trade_review_schema())

# the real process over stdio
p = subprocess.Popen([sys.executable, str(ROOT / "tools/mcp_6868/server.py")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "lab_card", "arguments": {"keys": ["fvg"], "tf": "1h"}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "meeting_room", "arguments": {"sections": 1}}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "nope"}}]
out, _ = p.communicate("\n".join(json.dumps(m) for m in msgs) + "\n", timeout=30)
res = {r["id"]: r for r in map(json.loads, out.strip().splitlines())}
assert set(res) == {1, 2, 3, 4, 5}, res.keys()   # no reply to the notification
assert res[1]["result"]["serverInfo"]["name"] == "6868-brain"
assert {t["name"] for t in res[2]["result"]["tools"]} >= {"query_trade_review", "lab_card", "meeting_room", "owner_pending"}
assert "isError" not in res[3]["result"] and "fvg" in res[3]["result"]["content"][0]["text"]
assert res[4]["result"]["content"][0]["text"].startswith("## ")
assert res[5]["error"]["code"] == -32602
print("ok mcp_6868")
