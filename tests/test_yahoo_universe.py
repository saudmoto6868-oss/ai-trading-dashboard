"""EGX / Tadawul full universe + the shared 60m download (1h and 4h = one request). No network: requests.get is faked.
Run: python tests/test_yahoo_universe.py"""
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import yahoo_feed as yf

egx, ksa = yf.universe("Egypt (EGX)"), yf.universe("Saudi (Tadawul)")
assert len(egx) >= 100 and len(ksa) >= 100, (len(egx), len(ksa))
assert egx[0] == "Y:^CASE30" and ksa[0] == "Y:^TASI.SR" and "Y:COMI.CA" in egx and "Y:2222.SR" in ksa
assert len(set(egx)) == len(egx) and len(set(ksa)) == len(ksa)
assert all(s.endswith(".CA") or s == "Y:^CASE30" for s in egx) and all(s.endswith(".SR") for s in ksa)
assert yf.universe("Forex") == yf.symbols("Forex")   # other classes unchanged
yf.mark_dead("Y:COMI.CA")
assert "Y:COMI.CA" not in yf.universe("Egypt (EGX)")

calls = []


class FakeResp:
    status_code = 200

    def __init__(self, n):
        self.n = n

    def json(self):
        ts = [1700000000 + 3600 * i for i in range(self.n)]
        c = [100 + (i % 7) for i in range(self.n)]
        return {"chart": {"result": [{"timestamp": ts, "indicators": {"quote": [{"open": c, "high": c, "low": c, "close": c, "volume": [1] * self.n}]}}]}}


def fake_get(url, params=None, headers=None, timeout=0):
    calls.append(params["interval"])
    time.sleep(0.2)
    return FakeResp(400)


yf.requests.get = fake_get
out = {}
threads = [threading.Thread(target=lambda tf=tf: out.__setitem__(tf, yf.get_yahoo_klines("Y:TEST.CA", tf, 250))) for tf in ("1h", "4h")]
[t.start() for t in threads]
[t.join() for t in threads]
assert calls.count("60m") == 1, calls   # one download for both timeframes
assert len(out["1h"]) == 250 and 0 < len(out["4h"]) <= 100 and list(out["1h"].columns) == list(out["4h"].columns)
print("yahoo universe tests ok")
