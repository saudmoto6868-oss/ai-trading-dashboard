"""journal_sync routes chart-strategy plans (kind "sig") to the signal ledger and trade snapshots to the trade journal. AppTest, mock data only.
Run: python3 tests/test_journal_sync_ledger.py"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
tmp = tempfile.mkdtemp()
os.environ["SIGNAL_LEDGER_PATH"] = os.path.join(tmp, "signals.json")
os.environ["TRADE_JOURNAL_PATH"] = os.path.join(tmp, "trades.json")
from streamlit.testing.v1 import AppTest  # noqa: E402

T0 = 1_700_000_000_000
APP = """
import sys; sys.path.insert(0, %r)
from modules import journal_sync as J
ev = [{"seq": 1, "rec": {"id": "sig:a", "kind": "sig", "src": "kzs", "sub": "London", "symbol": "BTC-USDT", "tf": "15m", "dir": "long", "entry": 100, "sl": 99, "tps": [102], "t0": %d}},
      {"seq": 2, "rec": {"id": "t1", "symbol": "BTC-USDT", "dir": "bullish", "tfk": "1h", "ttype": "day", "entry": 100, "sl": 99, "tp1": 101, "t0": %d, "status": "open"}},
      {"seq": 3, "rec": {"id": "sig:b", "kind": "sig", "src": "kzs", "symbol": "BTC-USDT", "tf": "15m", "dir": "long", "entry": 100, "sl": 101, "tps": [102], "t0": %d}}]
J._bridge = lambda **k: {"uid": "u1", "events": ev}
import streamlit as st
st.session_state["saved"] = J.sync()
""" % (ROOT, T0, T0, T0)
at = AppTest.from_string(APP, default_timeout=60).run()
assert not at.exception, at.exception
from modules import signal_ledger as SL  # noqa: E402
sigs = SL.all_signals()
assert len(sigs) == 1 and sigs[0]["src"] == "kzs" and sigs[0]["sub"] == "London", sigs   # the wrong-side stop (sig:b) is dropped
tj = json.load(open(os.environ["TRADE_JOURNAL_PATH"]))
assert "t1" in tj and not any(k.startswith("sig:") for k in tj), list(tj)
assert at.session_state["saved"] == 2, at.session_state["saved"]
print("ok journal sync -> ledger")
