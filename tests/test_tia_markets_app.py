"""TIA page (PAGE 12) in the real app with AppTest and the network blocked: Terminal view and the Markets view (the desk's market map).
Run: PYTHONPATH=. python3 tests/test_tia_markets_app.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import requests  # noqa: E402


def _fail(*a, **k):
    raise requests.exceptions.ConnectionError("blocked in test")


requests.get = _fail
requests.post = _fail
requests.Session.request = _fail
from streamlit.testing.v1 import AppTest  # noqa: E402

for view in ("Markets", "Terminal"):
    at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=300)
    at.session_state["page"] = 12
    at.session_state["ws_lang"] = "en"
    at.session_state["tia_view"] = view
    at.run()
    assert not at.exception, (view, [str(e.value)[:300] for e in at.exception])
    text = " ".join([m.value for m in at.markdown] + [w.value for w in at.warning] + [c.value for c in at.caption])
    if view == "Markets":
        assert "Market map" in text or "Hyperliquid did not answer" in text or "no markets" in text.lower(), text[:400]
    print("ok TIA", view, "view renders with network blocked")
print("ALL OK")
