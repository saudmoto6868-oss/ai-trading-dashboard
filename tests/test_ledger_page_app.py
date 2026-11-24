"""Strategy Ledger page (modules/ledger_page.py) in Streamlit AppTest with a seeded ledger (synthetic trades, no network). Mock data only.
Run: python3 tests/test_ledger_page_app.py"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
tmp = tempfile.mkdtemp()
os.environ["SIGNAL_LEDGER_PATH"] = os.path.join(tmp, "signals.json")

import pandas as pd  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

from modules import signal_ledger as L  # noqa: E402

H = 3_600_000
T0 = 1_700_000_000_000 // H * H
RUN = [(100.5, 100.6, 99.9, 100.2), (100.2, 102.1, 100.1, 102), (102, 104.2, 101.8, 104), (104, 106.5, 103.9, 106)]
HUNT = [(100.5, 100.6, 99.9, 100), (100, 100.2, 97.5, 98.5), (98.5, 102.5, 98.4, 102.2)]


def df(rows):
    b = [(T0 + i * H, *r) for i, r in enumerate(rows)] + [(T0 + (len(rows) + i) * H, rows[-1][3], rows[-1][3], rows[-1][3], rows[-1][3]) for i in range(200)]
    return pd.DataFrame({"time": pd.to_datetime([x[0] for x in b], unit="ms"), "open": [x[1] for x in b], "high": [x[2] for x in b], "low": [x[3] for x in b], "close": [x[4] for x in b]})


for i in range(14):
    L.record(dict(src="scanner" if i % 2 else "kzs", sub="day", symbol="S%d" % i, tf="1h", dir="long", entry=100, sl=98, tps=[102, 104, 106], t0=T0,
                  why=["bos", "fvg"], ctx={"of": "with", "delta_pct": 61, "of_real": True, "htf": "against", "regime": "Trend"}))
assert L.grade_pending(lambda sym, tf, n: df(HUNT if int(sym[1:]) % 2 else RUN), now_ms=T0 + 1000 * H) == 14

APP = """
import sys; sys.path.insert(0, %r)
from modules.ledger_page import render
render()
""" % ROOT
for lg in ("en", "ar"):
    at = AppTest.from_string(APP, default_timeout=60)
    at.session_state["ws_lang"] = lg
    at.run()
    assert not at.exception, at.exception
    md = " ".join(m.value for m in at.markdown)
    tabs = at.dataframe
    assert len(tabs) >= 3, len(tabs)   # ranking + trades + one-trade grid
    rank = tabs[0].value
    assert len(rank) == 2 and set(rank.iloc[:, 2]) == {7}, rank   # 7 filled each
    if lg == "en":
        assert "Stops too tight" in md and "Server scanner" in rank.to_string() and "Kill Zone Sniper" in rank.to_string(), md[:400]
        assert "Best chance that existed" in md, md[:600]
        at.radio(key="sl_by").set_value("why").run()
        assert not at.exception and "bos" in at.dataframe[0].value.to_string()
    else:
        assert "الستوب ضيق" in md, md[:300]
print("ok ledger page app")
