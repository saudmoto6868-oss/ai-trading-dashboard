"""Portfolio / drawdown simulator: real trades replay in time order, the approximation keeps the lab's win % and avg R, cost and risk
are applied, drawdown / losing streak are right on a hand-made series, and the lab writes the per-trade file it reads.
Run: PYTHONPATH=. python tests/test_lab_portfolio.py"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np  # noqa: E402
from modules import lab_portfolio as P  # noqa: E402
from modules import strategy_lab as SL  # noqa: E402

# approximation keeps n, win % and the average R
row = {"key": "a", "tf": "all", "side": "all", "n": 200, "win": 40.0, "avgR": 0.05}
s = P.approx_series(row)
assert len(s) == 200 and sum(x == 1.5 for x in s) == 80 and abs(np.mean(s) - 0.05) < 1e-9, (len(s), np.mean(s))
assert P.approx_series({"n": 0}) == [] and P.approx_series({"n": 5, "win": 50}) == []

# equity: 1 % risk, cost 0.1 R; +1.5, -1, -1, +1.5 -> drawdown after two losses, streak 2
e = P.equity_stats([1.5, -1, -1, 1.5], 0.01)
assert e["n"] == 4 and e["loss_streak"] == 2 and abs(e["net_r_per_trade"] - 0.15) < 1e-9
assert abs(e["max_dd"] - (1 - 0.989 * 0.989)) < 1e-9, e["max_dd"]
assert P.equity_stats([], 0.01) == {"n": 0}

# real mode: two detectors merged by time; OOS filter; missing key reported
trades = {"rr": 1.5, "series": ["X 1h"], "trades": {"a": [[3, 0, -1.0, 1], [1, 0, 1.5, 0]], "b": [[2, 0, 1.5, 1]]}}
p = P.portfolio_r(["a", "b", "c"], trades, [])
assert p["mode"] == "real" and p["r"] == [1.5, 1.5, -1.0] and p["missing"] == ["c"] and p["per_key"]["a"] == 2
assert P.portfolio_r(["a", "b"], trades, [], oos_only=True)["r"] == [1.5, -1.0]

# approx mode when there is no trades file; simulate adds ruin + drawdown range
rows = [row, {**row, "key": "b", "win": 50.0, "avgR": 0.2}]
r = P.simulate(["a", "b"], None, rows, risk=0.01)
assert r["mode"] == "approx" and r["n"] == 400 and 0 <= r["ruin"] <= 1 and r["dd_p50"] <= r["dd_p95"] and "equity" in r
assert r["max_dd"] > 0 and r["verdict"] in ("could_be_luck", "unlikely_luck")

# block bootstrap keeps every value from the sample and needs >= 2 blocks
assert P.block_dd([0.01] * 5) == {}
bd = P.block_dd([0.01, -0.01] * 50, n_paths=200)
assert 0 < bd["dd_p50"] <= bd["dd_p95"] < 0.2

# the lab writes the series the simulator reads
ev = [("1h", "BTC-USDT", [{"key": "a", "ts": 20, "r": -1.0, "oos": True}, {"key": "a", "ts": 10, "r": 1.5, "oos": False}, {"key": "b", "ts": 5, "r": 0.3}]),
      ("4h", "ETH-USDT", [{"key": "b", "ts": 1, "r": 1.5, "oos": True}, {"key": "b", "r": 1.0}])]
ts_ = SL.trade_series(ev)
assert ts_["series"] == ["BTC-USDT 1h", "ETH-USDT 4h"] and ts_["trades"]["a"] == [[10, 0, 1.5, 0], [20, 0, -1.0, 1]]
assert ts_["trades"]["b"] == [[1, 1, 1.5, 1], [5, 0, 0.3, 0]]   # event without ts is skipped
with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, "t.json")
    open(f, "w").write(json.dumps(ts_))
    assert P.load_trades(f)["trades"]["a"][0][2] == 1.5
    assert P.load_trades(os.path.join(d, "none.json")) is None
print("ok lab_portfolio")
