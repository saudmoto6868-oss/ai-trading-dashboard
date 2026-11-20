"""Voice control of the chart (owner 2026-11-20): the Gemini Live tool list declares the chart tools, every one is routed to the
XCMD command layer in the workspace page, and there is no order tool. Plain script: python3 tests/test_guide_voice_tools.py"""
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
from modules.guide_ai import LIVE_TOOLS

names = [f["name"] for f in LIVE_TOOLS[0]["function_declarations"]]
want = ["point_at", "open_page", "read_chart", "set_symbol", "set_timeframe", "toggle_indicator", "add_widget", "draw_level", "chart_layout"]
assert names == want, names
assert not any(w in n for n in names for w in ("order", "trade", "buy", "sell")), names
js = open(os.path.join(ROOT, "modules", "ws", "25_guide.js"), encoding="utf8").read()
for n in want[2:]:
    assert f'fc.name === "{n}"' in js, n
assert "X.setSymbol(" in js and "X.setTf(" in js and "X.toggle(" in js and "X.addPanel(" in js and "X.draw(" in js and "X.layout(" in js
print("guide voice tools: OK")
