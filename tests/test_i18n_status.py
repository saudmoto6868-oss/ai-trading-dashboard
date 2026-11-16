"""Feed status wording: a dead data source must read 'واقف' (offline), a falling market 'هابط' (down).
Before 2026-11-16 both used the key "down", so a dead OKX / Hyperliquid feed showed as 'هابط' (falling)."""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.i18n import AR

assert AR["offline"] == "واقف", AR.get("offline")
assert AR["down"] == "هابط", AR.get("down")
src = open(os.path.join(os.path.dirname(__file__), "..", "main.py"), encoding="utf-8").read()
for line in src.split("\n"):
    if re.search(r"""L\(["']live["']\)\s+if\s+src\.get""", line):
        assert 'L("offline")' in line and 'L("down")' not in line and "L('down')" not in line, line[:160]
print("ok test_i18n_status")
