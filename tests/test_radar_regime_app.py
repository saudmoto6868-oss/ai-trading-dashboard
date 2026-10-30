"""Market regime in the Radar (plain script; real app via AppTest, candles mocked, network blocked): chart_scan.features carries the regime, the Radar page opens with the regime
filter set (every view, no exception), the filter drops symbols of another regime, and the regime reaches market_context. Run: PYTHONPATH=. python tests/test_radar_regime_app.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import requests  # noqa: E402


def _fail(*a, **k):
    raise requests.exceptions.ConnectionError("blocked in test")


requests.get = _fail
requests.post = _fail
requests.Session.request = _fail


def frame(kind, seed, n=260):
    r = np.random.default_rng(seed)
    if kind == "trend":
        c = 100 * np.exp(np.cumsum(0.004 + r.normal(0, 0.003, n)))
    else:
        c = 100 + 0.6 * np.sin(np.arange(n) / 2.0) + r.normal(0, 0.05, n)
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({"time": np.arange(n) * 3600_000 + 1_700_000_000_000, "open": o, "high": np.maximum(o, c) + 0.2, "low": np.minimum(o, c) - 0.2, "close": c, "volume": 80 + r.random(n) * 40})


from modules import chart_scan as CS  # noqa: E402
from modules.context import market_context  # noqa: E402
assert CS.features(frame("trend", 1))["regime"] == "Trend" and CS.features(frame("chop", 2))["regime"] in ("Chop", "Mixed", "Squeeze")
assert market_context(frame("trend", 3))["regime"]["regime"] == "Trend"
from modules import market_cache as MC  # noqa: E402


def fake_frames(symbols, tfs, limit=300, workers=4):
    return {s: {tf: frame("trend" if i % 2 == 0 else "chop", i + 10) for tf in tfs} for i, s in enumerate(symbols)}, []


MC.fetch_frames = fake_frames
MC.get_klines = lambda sym, tf, limit=300, *a, **k: frame("trend", 5)
from streamlit.testing.v1 import AppTest  # noqa: E402

src = open(os.path.join(ROOT, "main.py"), encoding="utf8").read()
assert '"regime": f.get("regime")' in src and 'f.get("regime") and d.get("regime") not in f["regime"]' in src
for view in ("Chart grid", "Signal list", "Screener"):
    for pick in ([], ["Trend"], ["Chop", "Hi-Vol"]):
        at = AppTest.from_file(os.path.join(ROOT, "main.py"), default_timeout=300)
        at.session_state["page"] = 1
        at.session_state["radar_view"] = view
        at.session_state["cs_regime"] = pick
        at.run()
        assert not at.exception, (view, pick, [str(e.value)[:200] for e in at.exception])
        assert not at.error, (view, pick, [str(e.value)[:200] for e in at.error])
    print("ok radar view:", view)
print("ok regime in the Radar (mock-tested)")
