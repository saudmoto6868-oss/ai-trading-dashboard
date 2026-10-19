"""The Workspace page carries server-fetched rubik stats in CFG (empty when the server cannot reach OKX)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import workspace, okx_stats

orig = okx_stats.rubik_for
okx_stats.rubik_for = lambda symbols: {"/rubik/stat/contracts/open-interest-volume?ccy=BTC&period=1H": [["1", "2"]]}
try:
    html = workspace.build_workspace_html(["BTC-USDT"])
finally:
    okx_stats.rubik_for = orig
m = re.search(r'"rubik":\s*(\{.*?\})\s*,\s*"mrxOn"', html)
assert m, "CFG has no rubik key"
assert any("open-interest-volume?ccy=BTC" in k for k in json.loads(m.group(1)))
assert "CFG.rubik && Object.prototype.hasOwnProperty.call(CFG.rubik, path)" in html
print("ok workspace rubik")
