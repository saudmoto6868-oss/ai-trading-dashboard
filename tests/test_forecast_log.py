"""Forecast log: record checks, scoring order, timeout, Wilson interval, verdict (synthetic candles)."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import forecast_log as fl

fc = {"id": "t1", "symbol": "BTC-USDT", "tf": "1h", "side": "long", "entry": 100, "stop": 98, "target": 104,
      "made_at": "2026-11-20T08:00:00Z", "horizon_bars": 3}
d = tempfile.mkdtemp()
fl.record(fc, folder=d)
bad = dict(fc, stop=101)
try:
    fl.record(bad, folder=d); raise SystemExit("bad long accepted")
except ValueError:
    pass

bars = lambda *hl: [{"h": h, "l": l} for h, l in hl]
assert fl.score(fc, bars((101, 99), (105, 100)))[0] == "win"
assert fl.score(fc, bars((101, 97), (105, 100)))[0] == "loss"
assert fl.score(fc, bars((105, 97)))[0] == "loss"            # same bar: stop counted first
assert fl.score(fc, bars((101, 99), (102, 99), (103, 99)))[0] == "timeout"
out, r = fl.score(fc, bars((105, 100)))
assert out == "win" and abs(r - 2.0) < 1e-9                  # reward 4 / risk 2

lo, hi = fl.wilson(10, 20)
assert 0.27 < lo < 0.30 and 0.70 < hi < 0.74, (lo, hi)
s = fl.summarise([("win", 2.0), ("loss", -1.0), ("timeout", 0.0)])
assert s["n"] == 3 and s["wins"] == 1 and s["timeouts"] == 1 and "not evidence" in s["verdict"]
assert "sample is big" in fl.verdict(150)
print("test_forecast_log: OK")
