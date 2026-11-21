"""Status strip input: market_cache.recent_ok(src) = a real request to that source worked in the last 180 s.
Run: python tests/test_source_status.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import market_cache as mc

clock = [1000.0]
mc._now = lambda: clock[0]
mc._ok_at.clear()

assert not mc.recent_ok("OKX")                 # nothing seen yet = unknown, not "up"
mc._note("OKX", True)
assert mc.recent_ok("OKX") and not mc.recent_ok("HL")
clock[0] += 100
assert mc.recent_ok("OKX")
clock[0] += 100                                # 200 s after the last success
assert not mc.recent_ok("OKX") and mc.recent_ok("OKX", within=300)
mc._note("HL", False, mc.requests.exceptions.ConnectionError("x"))   # a failure never counts as seen-OK
assert not mc.recent_ok("HL")
mc._note("HL", True)
assert mc.recent_ok("HL")
print("source status tests ok")
