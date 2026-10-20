"""SMT school in the strategy lab: the walk asks smt_signals per bar against each correlated peer (synthetic, no network)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from modules import strategy_lab as sl
from modules.smt import peers_of

rng = np.random.default_rng(7)
n = 900
c = 100 + np.cumsum(rng.normal(0, 1, n))
df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=n, freq="1h"), "open": c, "high": c + .6, "low": c - .6, "close": c, "volume": rng.uniform(10, 30, n)})
peer = df.copy()
peer["close"] = peer["close"] * 1.01

# 1) pairs: Hyperliquid metals / oil / indices are reachable from the lab universe
assert ("HL:xyz:SILVER", False) in peers_of("HL:xyz:GOLD")
assert ("HL:xyz:BRENTOIL", False) in peers_of("HL:xyz:CL")

# 2) no peers -> no SMT calls
calls = {"n": 0, "args": None}
orig = sl.smt_signals
def fake(win, pwin, label, inv=False):
    calls["n"] += 1
    calls["args"] = (len(win), len(pwin), label, inv)
    return [{"family": "Liquidity", "name": "SMT divergence vs " + label, "key": "smt", "direction": sl.BULL}]
sl.smt_signals = fake
try:
    ev0, _ = sl.walk(df.copy(), "1h", stride=4)
    assert calls["n"] == 0 and not any(e["key"] == "smt" for e in ev0)

    # 3) with a peer -> SMT runs on every walk step, its signals become events (direction kept)
    ev1, _ = sl.walk(df.copy(), "1h", stride=4, peers=[(peer, "HL:xyz:SILVER", False)])
finally:
    sl.smt_signals = orig
assert calls["n"] > 100, calls
assert calls["args"][2] == "HL:xyz:SILVER" and calls["args"][1] > 0 and calls["args"][1] <= calls["args"][0], calls
smt_ev = [e for e in ev1 if e["key"] == "smt"]
assert smt_ev and all(e["d"] == 1 and e["fam"] == "Liquidity" for e in smt_ev), smt_ev[:2]
assert sl.SCHOOL["smt"] == "Intermarket (SMT)"
print("ok strategy smt", len(smt_ev), "smt events, calls", calls["n"])
