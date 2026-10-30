"""Monte Carlo on journal trades: zero-edge -> p not small, strong edge (n>=30) -> p small, losing -> p ~1, ruin grows with risk, n<30 = not evidence, seeded = repeatable.
Run: PYTHONPATH=. python tests/test_mc_journal.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np  # noqa: E402
from modules.mc_journal import mc_summary  # noqa: E402

g = np.random.default_rng(11)
zero = g.normal(0, 1.0, 80); zero -= zero.mean() - 0.0          # exactly zero mean, spread 1 R
edge = g.normal(0.5, 1.0, 80)
lose = g.normal(-0.5, 1.0, 80)
for risk in (0.01,):
    z, e, l = (mc_summary(x * risk, seed=1) for x in (zero, edge, lose))
    assert z["p_value"] > 0.3 and z["verdict"] == "could_be_luck", z
    assert e["p_value"] < 0.01 and e["verdict"] == "unlikely_luck", e
    assert l["p_value"] > 0.95 and l["verdict"] == "could_be_luck", l
lo, hi = mc_summary(edge * 0.01, seed=2), mc_summary(edge * 0.06, seed=2)
assert hi["ruin"] > lo["ruin"] and hi["ruin"] > 0.05, (lo["ruin"], hi["ruin"])
few = mc_summary(np.random.default_rng(3).normal(0.5, 1, 12) * 0.01, seed=4)
assert few["verdict"] == "not_evidence" and few["n"] == 12, few
a, b = mc_summary(edge * 0.01, seed=5), mc_summary(edge * 0.01, seed=5)
assert a == b and mc_summary([0.01], seed=1)["verdict"] == "too_few"
assert mc_summary([float("nan"), 0.01, -0.01, 0.02], seed=1)["n"] == 3
print("ok mc_journal", {k: round(v, 4) if isinstance(v, float) else v for k, v in e.items()})
