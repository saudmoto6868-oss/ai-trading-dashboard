"""Backtest runner on hand-made bars, with a frozen in-sample / out-of-sample split (plain script)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import pandas as pd
from modules.strategy_bt import freeze_split, run

n = 200
base = pd.DataFrame({"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1.0}, index=range(n))
m = np.zeros(n, bool); m[50] = True
# price rips up after the entry: long hits the target (+1.5 R), net = 1.5 - 0.1. cut=30 puts the entry out-of-sample
up = base.copy(); up.loc[51:, ["open", "high", "low", "close"]] = 110.0
r = run(up, m, "long", cut=30)
assert r["n"] == 1 and r["gross_r"] == [1.5] and abs(r["net_r"][0] - 1.4) < 1e-9
assert r["evidence"]["badge"] == "not evidence" and r["verdict_on"] == "out_of_sample" and r["in_sample"]["n"] == 0
# the same entry before the cut is in-sample only: it is reported but the verdict (OOS) sees nothing
r = run(up, m, "long", cut=100)
assert r["in_sample"]["n"] == 1 and r["in_sample"]["gross_r"] == [1.5] and r["n"] == 0
# crash after the entry: long stops out (-1 R); the same bars are a winner for a short
dn = base.copy(); dn.loc[51:, ["open", "high", "low", "close"]] = 90.0
assert run(dn, m, "long", cut=30)["gross_r"] == [-1.0] and run(dn, m, "short", cut=30)["gross_r"] == [1.5]
# one bar that touches both stop and target counts as a loss (conservative)
both = base.copy(); both.loc[51, ["high", "low"]] = [120.0, 80.0]
assert run(both, m, "long", cut=30)["gross_r"] == [-1.0]
# cooldown drops signals that fire back to back
m2 = np.zeros(n, bool); m2[[50, 52, 70]] = True
assert run(up, m2, "long", cut=30)["n"] == 2
# bad input is a clear error, including a bad split / cut, before anything runs
for bad in (lambda: run(base, m, "up"), lambda: run(base, m[:5], "long"), lambda: run(base[["close"]], m, "long"),
            lambda: run(base, m, split=0.95), lambda: run(base, m, split=True), lambda: run(base, m, cut=5),
            lambda: run(base, m, cut=199), lambda: run(base, m, cut=1.5)):
    try:
        bad(); raise SystemExit("should fail")
    except ValueError:
        pass
# no entries -> empty result, no crash
assert run(base, np.zeros(n, bool))["n"] == 0
# the split is frozen from the arguments: fraction -> index, explicit cut wins, datetime index reports the time
assert freeze_split(base)["cut_index"] == 100 and freeze_split(base, 0.25)["cut_index"] == 50 and freeze_split(base, 0.25, cut=80)["cut_index"] == 80
di = base.copy(); di.index = pd.date_range("2026-01-01", periods=n, freq="h")
assert freeze_split(di)["cut_time"] == str(di.index[100])
# CHANGING DATA AFTER THE CUT DOES NOT CHANGE THE IN-SAMPLE RESULT (bars at / after the cut are never read for in-sample)
rng = np.random.default_rng(7)
c = 100 + np.cumsum(rng.normal(0, 1, 6000))
nz = pd.DataFrame({"open": c, "high": c + 0.5, "low": c - 0.5, "close": c, "volume": 1.0})
ent = rng.random(6000) < 0.1
a = run(nz, ent, "long", cut=3000)
nz2 = nz.copy(); nz2.loc[3000:, ["open", "high", "low", "close"]] = nz2.loc[3000:, ["open", "high", "low", "close"]].iloc[::-1].to_numpy() + 50
b = run(nz2, ent, "long", cut=3000)
assert a["in_sample"]["net_r"] == b["in_sample"]["net_r"] and a["in_sample"]["evidence"] == b["in_sample"]["evidence"] and a["in_sample"]["n"] > 50
assert a["net_r"] != b["net_r"]   # the out-of-sample part does react to its own data
# the out-of-sample trades never start before the cut, in-sample trades never start at / after it
assert min(a["entry_idx"]) >= 3000 and max(a["in_sample"]["entry_idx"]) < 3000
# gate end to end: noise must not pass on the out-of-sample verdict
assert a["n"] >= 100 and a["evidence"]["badge"] == "not yet"
print("test_strategy_bt: all passed")
