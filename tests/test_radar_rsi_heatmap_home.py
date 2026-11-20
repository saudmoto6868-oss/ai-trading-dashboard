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

# 2026-11-20: Trade Intelligence Center (17) merged into TIA (12); old ?page=17 links open it inside TIA
hubs = eval(re.search(r"_HUBS = (\{[^}]*\})", src).group(1))
assert all(17 not in v for v in hubs.values()), hubs
assert 'if i == 17:' in src and 'st.session_state["tia_view"] = "Intelligence Center"' in src
assert '["TIA", "Intelligence Center"]' in src
import requests
from unittest import mock
from streamlit.testing.v1 import AppTest


def boom(*a, **k):
    raise requests.ConnectionError("blocked in test")


with mock.patch("requests.get", boom), mock.patch("requests.post", boom):
    at = AppTest.from_file(os.path.join(os.path.dirname(__file__), "..", "main.py"), default_timeout=300)
    at.query_params["page"] = "17"
    at.run()
    assert not at.exception, at.exception
    assert at.session_state["page"] == 12 and at.session_state["tia_view"] == "Intelligence Center"
    assert any("Meeting Room" in t.label for t in at.tabs), [t.label for t in at.tabs]
print("TIA + Intelligence Center merge: OK")
