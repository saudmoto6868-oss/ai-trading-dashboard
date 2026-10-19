"""Server-side OKX rubik stats for the Workspace (modules/okx_stats.py). No network: requests.get is replaced."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from modules import okx_stats as ok

calls = []
class Resp:
    def __init__(self, status=200, body=None):
        self.status_code, self._body = status, body or {"code": "0", "msg": "", "data": [["1", "2"]]}
    def json(self):
        return self._body

def reset():
    ok._cache.clear(); ok._down_until = 0.0; calls.clear()

orig_get = requests.get
requests.get = lambda url, **kw: (calls.append(url), Resp())[1]
try:
    reset()
    paths = ok.paths_for("BTC")
    assert "/rubik/stat/contracts/open-interest-volume?ccy=BTC&period=1H" in paths
    assert "/rubik/stat/taker-volume?ccy=BTC&instType=CONTRACTS&period=1H" in paths
    # the server-side map is keyed by the exact paths the page asks for
    got = ok.rubik_for(["BTC-USDT", "ETH-USDT", "BTC-USDT"])
    assert set(got) == set(ok.paths_for("BTC")) | set(ok.paths_for("ETH")), sorted(got)
    assert len(calls) == 14, len(calls)            # 7 paths x 2 bases, BTC listed twice is fetched once
    # cached for TTL: a second call makes no new requests
    ok.rubik_for(["BTC-USDT"])
    assert len(calls) == 14

    # a connection failure pauses further requests (no slow page loads)
    reset()
    def boom(url, **kw):
        calls.append(url); raise requests.ConnectionError("no route")
    requests.get = boom
    assert ok.rubik_for(["BTC-USDT", "ETH-USDT"]) == {}
    assert len(calls) == 1, calls                  # first failure opens the pause; the rest are skipped

    # an OKX error code is not cached and not returned
    reset()
    requests.get = lambda url, **kw: (calls.append(url), Resp(body={"code": "50011", "msg": "rate limit", "data": []}))[1]
    assert ok.rubik_for(["BTC-USDT"]) == {}
finally:
    requests.get = orig_get
    reset()
print("ok okx stats")
