"""research/trade_db: swing levels use only confirmed pivots on the right side of price; trade walk exit types, MFE/MAE. Plain script."""
import numpy as np

from research.trade_db.build_db import swings, walk_trade

# swings: a pivot high at bar 5 (above close) and a pivot low at bar 10 (below close); bar 15 = now
hi = np.array([10, 11, 12, 13, 14, 20, 14, 13, 12, 11, 10, 11, 12, 13, 14, 15, 16], float)
lo = hi - 1; lo[10] = 5
sup, res = swings(hi, lo, c=15.0, i=15, n=3)
assert res == 20 and sup == 5, (sup, res)
# an unconfirmed pivot (fewer than n bars after it) must not count
hi2 = hi.copy(); hi2[14] = 30
sup2, res2 = swings(hi2, lo, c=15.0, i=15, n=3)
assert res2 == 20, res2

# walk_trade: long, stop 1, target 1.5R
cl = np.array([100, 100.5, 101, 101.6, 101.0])
h = cl + .2; l = cl - .2
ex, r, b, mfe, mae = walk_trade(h, l, cl, 0, 1, 1.0, 10)
assert ex == "tp" and r == 1.5 and b == 3 and mfe >= 1.5 and mae < .5, (ex, r, b, mfe, mae)
ex, r, *_ = walk_trade(h, l, cl, 0, -1, 1.0, 10)
assert ex == "sl" and r == -1.0
ex, r, b, *_ = walk_trade(np.array([100, 100.1, 100.2]), np.array([100, 99.9, 99.95]), np.array([100, 100.05, 100.1]), 0, 1, 1.0, 2)
assert ex == "time" and abs(r - 0.1) < 1e-9 and b == 2
print("ok trade_db")
