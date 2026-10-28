"""The four lab tabs in REAL Streamlit (AppTest, network blocked, no mocked app functions): one Lab Summary page (Validation Lab / Calibration / Class rotation / Evidence summary,
once through main.py (the scan payload is not built yet -> the 'not ready' message, no error) and once with a real-shaped scan payload fed to the render functions.
Also: class_of maps the real symbols (gold, oil, FX, EGX ...) to their classes. Run: python tests/test_lab_tabs_app.py"""
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
from modules import lab_shared as LS  # noqa: E402

for sym, cls in [("HL:xyz:GOLD", "Metals"), ("HL:xyz:CL", "Oil & Gas"), ("HL:xyz:SP500", "Indices"), ("HL:xyz:TSLA", "Stocks"), ("HL:xyz:EUR", "Forex"), ("Y:EURUSD=X", "Forex"),
                 ("Y:COMI.CA", "Egypt (EGX)"), ("Y:2222.SR", "Saudi (Tadawul)"), ("BTC-USDT", "Crypto"), ("FH:EUR_USD", "Forex")]:
    assert LS.class_of(sym) == cls, (sym, LS.class_of(sym), cls)

# 1) through main.py: the one Lab Summary page (page 8) renders all four sections (payload empty at this point -> the two payload sections show 'not ready')
for lang in ("en", "ar"):
    at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=250)
    at.session_state["page"] = 8
    at.session_state["ws_lang"] = lang
    at.run()
    assert not at.exception, (lang, [str(e.value)[:200] for e in at.exception])
    assert not at.error, (lang, [str(e.value)[:200] for e in at.error])
    assert len(at.metric) == 4 and len(at.expander) >= 4 and len(at.dataframe) >= 2, (lang, len(at.metric), len(at.expander), len(at.dataframe))
    print("ok main.py Lab Summary:", lang)

# 2) the payload tabs with a real-shaped payload (scan = symbol -> timeframe -> setup, mini = ready setups with the detector keys)
PAYLOAD = {
    "scan": {"BTC-USDT": {"1h": {"tf": "1h", "dir": "bullish", "score": 5, "max": 8}}, "HL:xyz:GOLD": {"1h": {"tf": "1h", "dir": "bearish", "score": 3, "max": 8}, "1d": {"tf": "1d", "dir": "bearish", "score": 4, "max": 8}},
             "HL:xyz:CL": {"1h": {"tf": "1h", "dir": "bullish", "score": 2, "max": 8}}},
    "mini": [{"symbol": "BTC-USDT", "direction": "bullish", "tfk": "1H", "ttype": "Day Trade", "trade": "Long", "tags": ["اختراق"], "tags_en": ["Breakout"], "score": 5, "max": 8,
              "plan": {"entry": 60000.0, "stop": 59000.0}, "keys": ["level", "vwap", "ob"], "against": False},
             {"symbol": "HL:xyz:GOLD", "direction": "bearish", "tfk": "1D", "ttype": "Swing", "trade": "Short", "tags": [], "tags_en": [], "score": 4, "max": 8, "plan": {}, "keys": [], "against": True}],
}
SCRIPT = f"""
import sys
sys.path.insert(0, {ROOT!r})
from modules.rotation_scan import render_rotation_scan
from modules.decision_desk import render_decision_desk
P = {PAYLOAD!r}
render_rotation_scan(P)
render_decision_desk(P)
render_rotation_scan({{}})
render_decision_desk({{"mini": []}})
"""
for lang in ("en", "ar"):
    at = AppTest.from_string(SCRIPT, default_timeout=60)
    at.session_state["ws_lang"] = lang
    at.run()
    assert not at.exception, (lang, [str(e.value)[:200] for e in at.exception])
    assert not at.error, (lang, [str(e.value)[:200] for e in at.error])
    assert len(at.info) == 2, ("both empty states", len(at.info))
    md = " ".join(m.value for m in at.markdown if isinstance(m.value, str)) + " ".join(str(c.value) for c in at.caption)
    assert "Decision" not in md and "يمرّ البوابة" not in md and "Passes gate" not in md, "no pass / block gate wording"
    assert len(at.dataframe) >= 2, lang
    print("ok payload tabs:", lang, "| dataframes:", len(at.dataframe))
print("ok lab tabs in the real app")
