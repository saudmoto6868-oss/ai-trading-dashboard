"""Shared context feeds (calendar, CMC, macro) reach both the desk and TIA, and a failing feed never breaks TIA. Mock, no network.
Run: PYTHONPATH=. python3 tests/test_context_feeds.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import context_feeds as CF, calendar_feed, cmc, macro_fund  # noqa: E402

calendar_feed.fetch_calendar = lambda: [{"title": "TIA_TEST_EVENT", "time": "x", "impact": "high"}]
cmc.fetch_cmc = lambda: {"mock": True}
macro_fund.fetch_macro_fund = lambda: {"mock": "macro"}
raw = lambda f: getattr(f, "__wrapped__", f)   # bypass st.cache_data for a plain call

assert raw(CF.calendar_rows)()[0]["title"] == "TIA_TEST_EVENT"
assert raw(CF.cmc_data)() == {"mock": True}
assert raw(CF.macro_fund)() == {"mock": "macro"}
print("ok shared feeds return the mocked data")

from modules import tia_workspace as TW  # noqa: E402
assert TW._ctx(lambda: 1 / 0, "fallback") == "fallback"
assert TW._ctx(lambda: [1], []) == [1]
print("ok a failing feed gives the default")

def boom(*a, **k):
    raise RuntimeError("calendar down")
calendar_feed.fetch_calendar = boom
assert TW._ctx(lambda: raw(CF.calendar_rows)(), []) == [], "a failing calendar must give the default, not raise"   # raw() skips the cache
print("ok TIA context wrapper never raises")
print("ALL OK")
