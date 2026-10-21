"""Backtest runner on hand-made bars (plain script)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import pandas as pd
from modules.strategy_bt import run

n = 200
base = pd.DataFrame({"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1.0}, index=range(n))
m = np.zeros(n, bool); m[50] = True
# price rips up after the entry: long hits the target (+1.5 R), net = 1.5 - 0.1
up = base.copy(); up.loc[51:, ["open", "high", "low", "close"]] = 110.0
r = run(up, m, "long")
assert r["n"] == 1 and r["gross_r"] == [1.5] and abs(r["net_r"][0] - 1.4) < 1e-9
assert r["evidence"]["badge"] == "not evidence"
# crash after the entry: long stops out (-1 R); the same bars are a winner for a short
dn = base.copy(); dn.loc[51:, ["open", "high", "low", "close"]] = 90.0
assert run(dn, m, "long")["gross_r"] == [-1.0] and run(dn, m, "short")["gross_r"] == [1.5]
# one bar that touches both stop and target counts as a loss (conservative)
both = base.copy(); both.loc[51, ["high", "low"]] = [120.0, 80.0]
assert run(both, m, "long")["gross_r"] == [-1.0]
# cooldown drops signals that fire back to back
m2 = np.zeros(n, bool); m2[[50, 52, 70]] = True
assert run(up, m2, "long")["n"] == 2
# bad input is a clear error
for bad in (lambda: run(base, m, "up"), lambda: run(base, m[:5], "long"), lambda: run(base[["close"]], m, "long")):
    try:
        bad(); raise SystemExit("should fail")
    except ValueError:
        pass
# no entries -> empty result, no crash
assert run(base, np.zeros(n, bool))["n"] == 0
# gate end to end: 400 random-walk trades with a fixed edge in R terms must not pass on pure noise
rng = np.random.default_rng(7)
c = 100 + np.cumsum(rng.normal(0, 1, 6000))
nz = pd.DataFrame({"open": c, "high": c + 0.5, "low": c - 0.5, "close": c, "volume": 1.0})
res = run(nz, rng.random(6000) < 0.1, "long")
assert res["n"] >= 100 and res["evidence"]["badge"] in ("not yet", "passes gate") and res["evidence"]["badge"] == "not yet"
print("test_strategy_bt: all passed")
