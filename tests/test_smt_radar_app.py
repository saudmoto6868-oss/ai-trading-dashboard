"""Radar > SMT pairs + the SMT banner (real app, AppTest, network blocked, scan_pairs replaced by canned events).
Run: PYTHONPATH=. python tests/test_smt_radar_app.py"""
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
from modules import intermarket as IM  # noqa: E402

EV = [{"id": "smt|HL:xyz:GOLD|HL:xyz:SILVER|1h|bullish|1", "a": "HL:xyz:GOLD", "b": "HL:xyz:SILVER", "inverse": False, "tf": "1h", "direction": "bullish", "bars_ago": 3, "t": "2026-11-06T10:00:00+00:00",
       "session": "London", "p1": 4000.0, "p2": 3990.0, "a_name": "Gold", "b_name": "Silver", "a_color": "#f0b90b", "b_color": "#c0c7d0",
       "text_en": "SMT up on 1H between Gold and Silver: one made a new low and the other refused.", "text_ar": "SMT صاعد على فريم 1H بين الذهب والفضة",
       "series_a": [4000 + (i % 9) for i in range(60)], "series_b": [50 + (i % 7) * .1 for i in range(60)]}]
IM.scan_pairs = lambda fetch, tfs=IM.DEFAULT_TFS, pairs=None, **k: list(EV)

for lang in ("en", "ar"):
    at2 = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=250)
    at2.session_state["page"] = 1
    at2.session_state["ws_lang"] = lang
    at2.session_state["radar_view"] = "SMT pairs"
    at2.run()
    assert not at2.exception, (lang, [str(e.value)[:300] for e in at2.exception])
    body = " ".join(m.value for m in at2.markdown)
    assert "Gold" in body and "Silver" in body and "SMT" in body and "<svg" in body, body[:400]
    print("ok smt radar", lang)
