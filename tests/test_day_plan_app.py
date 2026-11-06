"""Radar > Day plan (real app, AppTest, network blocked, day_plan.scan replaced by a canned plan). Run: PYTHONPATH=. python tests/test_day_plan_app.py"""
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
from modules import day_plan as D  # noqa: E402

PLAN = {"id": "plan|HL:xyz:GOLD|bullish|15m|conf", "symbol": "HL:xyz:GOLD", "mode": "conf", "tf": "15m", "direction": "bullish", "stars": 3, "price": 4100.0, "entry": 4100.0, "stop": 4088.0,
        "tps": [4118.0, 4135.0, 4160.0], "book": "levels", "risk_points": 120, "move_points": 600, "rr1": 1.5, "point": 0.1,
        "confluence": {"bias": "bullish", "bias_strength": 2, "agree": ["1d", "4h", "1h", "15m"], "n": 4, "of": 5, "views": {"1d": "bullish", "4h": "bullish", "1h": "bullish", "15m": "bullish", "5m": "neutral"}},
        "schools": ["Fibonacci", "SMC / ICT"], "reasons": ["📐 OTE entry", "🧱 Order block"], "keys": ["ote", "ob"],
        "exit": D.exit_plan({"entry": 4100.0, "stop_loss": 4088.0, "take_profits": [4118.0, 4135.0, 4160.0]}, "conf", 6.0, 0.1), "session": D.session_clock("2026-11-06T08:00:00Z"), "t": "2026-11-06 08:00"}
calls = []
D.scan = lambda symbols, fetch, mode="conf", **kw: calls.append((list(symbols), mode, kw)) or [PLAN]

for lang in ("en", "ar"):
    at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=250)
    at.session_state["page"] = 1
    at.session_state["ws_lang"] = lang
    at.session_state["radar_view"] = "Day plan"
    at.run()
    assert not at.exception, (lang, [str(e.value)[:300] for e in at.exception])
    body = " ".join(m.value for m in at.markdown)
    assert "HL:xyz:GOLD" in body and "4118.0" in body and "1D" in body and ("Entry" in body or "دخول" in body) and "London Open KZ" in body, body[:500]
    assert calls and calls[-1][1] == "conf", calls
    print("ok day plan app", lang)
