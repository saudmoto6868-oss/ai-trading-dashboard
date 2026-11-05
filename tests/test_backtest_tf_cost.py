"""backtest_tf reports the average R and the NET average R after the round-trip cost (DECISIONS.md #2), not only the hit rate.
Run: PYTHONPATH=. python tests/test_backtest_tf_cost.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from modules import backtest_tf as bt  # noqa: E402

# 4 trades of one strategy on 1h: rr 1.5, cost 0.1 R each: 2 tp (+1.5) and 2 sl (-1) -> avgR = (3 - 2) / 4 = 0.25, net = 0.15
rows = [(["a", "*"], "tp", 1.5, 0.1), (["a", "*"], "sl", 1.5, 0.1), (["a", "*"], "tp", 1.5, 0.1), (["a", "*"], "sl", 1.5, 0.1), (["a", "*"], "exp", 1.5, 0.1)]
st = bt.aggregate({"1h": rows})
d = st["a"]["1h"]
assert d["n"] == 4 and d["tp"] == 2 and d["sl"] == 2 and d["exp"] == 1 and d["hit"] == 0.5, d
assert d["avgR"] == 0.25 and d["net"] == 0.15, d            # the expired trade counts in neither
# a high hit rate with a small reward is NOT a positive net: rr 0.3, 80 % tp, cost 0.1 R -> avgR = 0.8*0.3 - 0.2 = 0.04, net = -0.06
low = [(["b"], "tp", 0.3, 0.1)] * 8 + [(["b"], "sl", 0.3, 0.1)] * 2
db = bt.aggregate({"1h": low})["b"]["1h"]
assert db["hit"] == 0.8 and abs(db["avgR"] - 0.04) < 1e-9 and abs(db["net"] + 0.06) < 1e-9, db
# old rows without rr / cost still aggregate (no avgR / net)
old = bt.aggregate({"1h": [(["c"], "tp"), (["c"], "sl")]})["c"]["1h"]
assert old["hit"] == 0.5 and "net" not in old
# best_tf_net: only a positive net counts, and it needs MIN_N resolved trades
many = [(["z"], "tp", 2.0, 0.1)] * (bt.MIN_N // 2 + 1) + [(["z"], "sl", 2.0, 0.1)] * (bt.MIN_N // 2)
st2 = bt.aggregate({"1h": many, "4h": [(["z"], "tp", 0.3, 0.1)] * bt.MIN_N + [(["z"], "sl", 0.3, 0.1)] * 3})
assert st2["z"]["4h"]["hit"] > st2["z"]["1h"]["hit"] and st2["z"]["4h"]["net"] < 0 < st2["z"]["1h"]["net"], st2
assert bt.best_tf(st2)["z"] == "4h" and bt.best_tf_net(st2)["z"] == "1h", (bt.best_tf(st2), bt.best_tf_net(st2))
assert abs(bt.COST_PCT - 0.001) < 1e-12
print("ok backtest_tf cost")
