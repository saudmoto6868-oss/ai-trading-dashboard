"""Footprint recorder (recorder/footprint_recorder.py), offline: aggregation per minute x price, duplicate ids ignored, coverage runs (a reconnect leaves a HOLE), the HTTP endpoint (JSON, CORS,
symbol whitelist, 72 h cap, gzip), and the WebSocket loop against a fake socket. Run: PYTHONPATH=. python tests/test_footprint_recorder.py"""
import asyncio
import gzip
import json
import os
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recorder"))
import footprint_recorder as R  # noqa: E402

S = R.Store()
T0 = 1_800_000_000_000 // R.MIN * R.MIN
run = S.begin("BTC-USDT", T0)
assert S.add("BTC-USDT", "1", T0 + 1000, 100.0, 2.0, "buy") and S.add("BTC-USDT", "2", T0 + 2000, 100.0, 3.0, "sell") and S.add("BTC-USDT", "3", T0 + 61000, 100.5, 1.0, "buy")
assert not S.add("BTC-USDT", "1", T0 + 1000, 100.0, 2.0, "buy"), "a resent id must not count twice"
S.beat("BTC-USDT", run, T0 + 120000); S.commit()
q = S.query("BTC-USDT", T0, T0 + 120000)
assert q["mins"][str(T0)] == [100.0, 2.0, 3.0] and q["mins"][str(T0 + R.MIN)] == [100.5, 1.0, 0.0], q
assert q["cov"] == [[T0, T0 + 120000]], q["cov"]
# a drop: a second run starts later; the time in between is a hole, not "no trades"
run2 = S.begin("BTC-USDT", T0 + 300000); S.beat("BTC-USDT", run2, T0 + 360000)
q = S.query("BTC-USDT", T0, T0 + 400000)
assert q["cov"] == [[T0, T0 + 120000], [T0 + 300000, T0 + 360000]], q["cov"]
assert S.query("BTC-USDT", T0 + 130000, T0 + 290000)["cov"] == [], "inside the hole nothing is known"
assert S.query("BTC-USDT", T0, T0 + 10 * 86_400_000)["cov"][-1][1] <= T0 + R.MAX_SPAN + 360000   # the span is capped
assert S.since("BTC-USDT") == T0 and S.since("XXX") is None
S.purge(T0 + R.KEEP + 10 * R.MIN)
assert S.query("BTC-USDT", T0, T0 + R.MIN)["mins"] == {}
# HTTP
S2 = R.Store(); r2 = S2.begin("ETH-USDT", T0); S2.add("ETH-USDT", "a", T0 + 5, 10.0, 1.0, "buy"); S2.beat("ETH-USDT", r2, T0 + 90000); S2.commit()
srv = ThreadingHTTPServer(("127.0.0.1", 0), R.make_handler(S2, {"ETH-USDT"})); threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_port}"
resp = urllib.request.urlopen(f"{base}/fp?sym=ETH-USDT&from={T0}&to={T0 + 90000}")
assert resp.headers["Access-Control-Allow-Origin"] == "*" and json.loads(resp.read())["mins"][str(T0)] == [10.0, 1.0, 0.0]
assert json.loads(urllib.request.urlopen(f"{base}/health").read())["symbols"] == ["ETH-USDT"]
for bad, code in ((f"{base}/fp?sym=DOGE-USDT", 404), (f"{base}/fp?sym=ETH-USDT&from=abc", 400), (f"{base}/nope", 404)):
    try:
        urllib.request.urlopen(bad); raise AssertionError(bad)
    except urllib.error.HTTPError as e:
        assert e.code == code, (bad, e.code)
big = R.Store(); big.begin("ETH-USDT", T0)
for i in range(400):
    big.add("ETH-USDT", f"i{i}", T0 + i, 10.0 + i * 0.01, 1.0, "buy")
srv2 = ThreadingHTTPServer(("127.0.0.1", 0), R.make_handler(big, {"ETH-USDT"})); threading.Thread(target=srv2.serve_forever, daemon=True).start()
rq = urllib.request.Request(f"http://127.0.0.1:{srv2.server_port}/fp?sym=ETH-USDT&from={T0}&to={T0 + R.MIN}", headers={"Accept-Encoding": "gzip"})
raw = urllib.request.urlopen(rq); assert raw.headers["Content-Encoding"] == "gzip" and len(json.loads(gzip.decompress(raw.read()))["mins"][str(T0)]) == 1200
srv.shutdown(); srv2.shutdown()


# the WebSocket loop against a fake socket: subscribe ack starts a run, prints are stored, a drop ends it and the reconnect starts a NEW run
class FakeWS:
    def __init__(self, msgs, boom=False):
        self.msgs, self.boom, self.sent = msgs, boom, []

    async def send(self, m):
        self.sent.append(json.loads(m))

    def __aiter__(self):
        async def gen():
            for m in self.msgs:
                yield json.dumps(m)
            if self.boom:
                raise ConnectionError("drop")
        return gen()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False


conns = []


def connect(url, ping_interval=None):
    ws = FakeWS([{"event": "subscribe", "arg": {"channel": "trades", "instId": "SOL-USDT"}},
                 {"arg": {"channel": "trades", "instId": "SOL-USDT"}, "data": [{"instId": "SOL-USDT", "tradeId": f"t{len(conns)}", "px": "150.5", "sz": "2", "side": "sell", "ts": str(T0 + 5)},
                                                                              {"instId": "NOPE-USDT", "tradeId": "z", "px": "1", "sz": "1", "side": "buy", "ts": str(T0)}]}], boom=len(conns) == 0)
    conns.append(ws)
    return ws


S3 = R.Store()


async def go():
    task = asyncio.create_task(R.listen(S3, ["SOL-USDT"], connect=connect))
    await asyncio.sleep(2.5)
    task.cancel()


asyncio.run(go())
assert conns[0].sent[0]["op"] == "subscribe" and conns[0].sent[0]["args"] == [{"channel": "trades", "instId": "SOL-USDT"}]
assert len(conns) >= 2, "after the drop it must reconnect"
runs = S3.db.execute("SELECT COUNT(*) FROM runs WHERE sym='SOL-USDT'").fetchone()[0]
assert runs >= 2, "every connection is its own run"
rows = S3.db.execute("SELECT SUM(sell), COUNT(*) FROM fp WHERE sym='SOL-USDT'").fetchone()
assert rows[0] >= 2.0 and not S3.db.execute("SELECT 1 FROM fp WHERE sym='NOPE-USDT'").fetchone(), "unsubscribed symbols are ignored"
print("ok footprint recorder: aggregation, holes, http, websocket loop")
