"""The background scan worker (modules/page_bg._scan_worker) feeds the signal ledger: every scanner plan is recorded (t0 = next candle),
the brain's setup detectors run at most every 15 min, and pending signals are graded at the end of the pass. Stubbed data, no network.
Run: PYTHONPATH=. python3 tests/test_ledger_scan_worker.py"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["SIGNAL_LEDGER_PATH"] = os.path.join(tempfile.mkdtemp(), "signals.json")
import pandas as pd  # noqa: E402

from modules import page_bg as PB  # noqa: E402
from modules import signal_ledger as SL  # noqa: E402

H = 3_600_000
T_LAST = 1_700_000_000_000 // H * H
df = pd.DataFrame({"time": pd.to_datetime([T_LAST - H, T_LAST], unit="ms"), "open": [1.0, 1.0], "high": [1.0, 1.0], "low": [1.0, 1.0], "close": [100.0, 100.0]})
calls = {"setups": 0, "grade": 0}
PB.SCAN_TFS = ["1h"]
PB.get_klines = lambda *a, **k: df
PB.seed_from_df = lambda *a, **k: None
PB.scan_crypto_group = lambda syms, tf: ([{"symbol": "BTC-USDT", "direction": "bullish", "score": 1, "signals": [], "against": False}], "")
PB.scan_entry = lambda r, d: {"symbol": "BTC-USDT", "direction": "bullish", "tfk": "1h", "tfc": "1H", "ttype": "day", "trade": "", "tags": [], "tags_en": [],
                              "zones": [], "score": 6, "max": 10, "tv": "", "ew": None, "keys": ["bos", "fvg"],
                              "plan": {"entry": 100.0, "stop": 98.0, "tps": [102.0, 104.0]}}
SL.record_setups = lambda syms, fetch, path=None: calls.__setitem__("setups", calls["setups"] + 1) or 0
SL.grade_pending = lambda fetch, path=None, limit=40, **k: calls.__setitem__("grade", calls["grade"] + 1) or 0

store = {"t0": 0}
PB._scan_worker(store, "1h", ("k", "x", ("BTC-USDT",)))
assert store["payload"]["mini"], store.get("payload")   # the scan itself still works
sigs = SL.all_signals()
assert len(sigs) == 1, sigs
s = sigs[0]
assert s["src"] == "scanner" and s["sub"] == "day" and s["tf"] == "1h" and s["dir"] == "long" and s["why"] == ["bos", "fvg"], s
assert s["t0"] == T_LAST + H, (s["t0"], T_LAST)   # the next candle's open: no look-ahead
assert calls == {"setups": 1, "grade": 1}, calls
PB._scan_worker(store, "1h", ("k", "x", ("BTC-USDT",)))   # second pass right away: detectors wait 15 min, grading runs again, the plan is not duplicated
assert calls == {"setups": 1, "grade": 2}, calls and len(SL.all_signals()) == 1
assert len(SL.all_signals()) == 1
print("ok ledger scan worker")
