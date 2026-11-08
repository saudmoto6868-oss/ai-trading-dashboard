"""Radar filter block (plain script, Streamlit AppTest, network blocked): the preset dropdown exists, choosing a preset sets the grouped filters, no exception."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import requests
def _fail(*a, **k): raise requests.exceptions.ConnectionError("blocked in test")
requests.get = _fail; requests.post = _fail; requests.Session.request = _fail
from streamlit.testing.v1 import AppTest
at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=200); at.session_state["page"] = 1; at.run()
assert not at.exception, [str(e.value)[:200] for e in at.exception]
box = [s for s in at.selectbox if s.key == "cs_preset"]; assert box and "Oversold bounce" in box[0].options
box[0].set_value("Oversold bounce").run()
ss = at.session_state
assert ss["cs_rsi"] == ["rsi_lt30"] and ss["cs_mom_v"] == ["vol_2x"] and ss["cs_side"] == "Buy only" and not at.exception
box = [s for s in at.selectbox if s.key == "cs_preset"][0]; box.set_value("Elliott waves").run()
assert at.session_state["cs_rsi"] == [] and at.session_state["cs_strat"] == ["st_elliott"] and at.session_state["cs_side"] == "Both", "old choices must be cleared"
# the new candle-only lists exist as dropdowns and can be chosen without breaking the page
for k in ("adx", "sar", "dist20", "macd", "stoch", "cci", "willr", "turnover", "obv", "range", "bb", "price", "ichi", "beta", "corr"):
    assert [b for b in at.selectbox if b.key == "fv_f_" + k], k
b = [b for b in at.selectbox if b.key == "fv_f_adx"][0]; b.set_value("o25").run(); assert not at.exception, [str(e.value)[:200] for e in at.exception]
print("PASS: radar filter block + presets")
