"""modules/zone_collector.py offline: synthetic books/trades through the real engine, no network."""
import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import zone_collector as C, zone_eval as E  # noqa: E402


def test_run_logs_zone_and_resolves():
    state = {"i": 0, "now": 1_700_000_000.0}
    def book(i, mid):
        bids = [(round(mid - 0.1 * k, 1), 1.0) for k in range(1, 400)]
        asks = [(round(mid + 0.1 * k, 1), 1.0) for k in range(1, 400)]
        return bids, asks
    def fetch(sym):
        i = state["i"]; state["i"] += 1
        mid = 100.0 if i < 40 else 99.0 - 0.01 * (i - 40)
        bids, asks = book(i, mid)
        bids[4] = (bids[4][0], 80.0); asks[4] = (asks[4][0], 80.0)   # persistent walls both sides
        t = int((1_700_000_000 + i * 2) * 1000)
        trs = [{"t": t - 100, "p": asks[4][0], "q": 3.0, "side": "Buy", "id": i * 10 + k} for k in range(6)]  # prints at the ask wall
        return t, bids, asks, trs
    def sleep(s): state["now"] += s
    d = tempfile.mkdtemp()
    out = C.run(["X-USDT"], 400, out_dir=d, log=lambda *_: None, fetch=fetch, sleep=sleep, clock=lambda: state["now"])
    recs = out["X-USDT"]
    assert recs and all(r["src"] == "collector" for r in recs)
    p = os.path.join(d, ".zone_log_X-USDT.json")
    assert json.load(open(p))["sym"] == "X-USDT"


if __name__ == "__main__":
    test_run_logs_zone_and_resolves(); print("ok zone_collector")
