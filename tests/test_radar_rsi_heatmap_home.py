"""Owner 2026-11-20: radar things live in the Radar. RSI Heatmap is no longer a top tab; it opens in Radar > Heat map,
and old links (?page=20) still reach it. Plain script: python3 tests/test_radar_rsi_heatmap_home.py"""
import os
import re

src = open(os.path.join(os.path.dirname(__file__), "..", "main.py"), encoding="utf8").read()
order = eval(re.search(r"_PAGE_ORDER = (\[[^\]]*\])", src).group(1))
assert 20 not in order and 1 in order, order
assert '"Heat map", "RSI heatmap"' in src and 'key="radar_sub_h"' in src
assert 'if i == 20:' in src and 'st.session_state["radar_sub_h"] = "RSI heatmap"' in src
print("radar rsi heatmap home: OK")
