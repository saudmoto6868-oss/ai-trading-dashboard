"""Plateau Lab on synthetic candles (plain script). MOCK DATA ONLY: shows the method works, says nothing about real markets."""
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from modules import hub_core, hub_plateau as hp

def series(seed, n, drift=0.0, phi=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    r = np.zeros(n)
    for i in range(1, n):
        r[i] = drift + phi * r[i - 1] + vol * rng.standard_normal()
    return 100 * np.exp(np.cumsum(r))

# --- building blocks ---
x = np.arange(1.0, 11.0)
assert np.allclose(hp._sma(x, 3)[2:], [2, 3, 4, 5, 6, 7, 8, 9]) and np.isnan(hp._sma(x, 3)[0])
close = series(1, 600, phi=0.3)
p = hp.positions(close, 10, 50)
assert p[0] == 0 and set(np.unique(p)) <= {-1.0, 0.0, 1.0}
# no look-ahead: changing the LAST close cannot change any earlier position
c2 = close.copy(); c2[-1] *= 1.5
assert np.array_equal(hp.positions(c2, 10, 50)[:-1], p[:-1])
assert hp.bar_returns(close, p)[0] == 0
# costs bite: higher cost, lower total return
assert hp.bar_returns(close, p, 0.01).sum() < hp.bar_returns(close, p, 0.0).sum()
# trade_returns on a hand-made path
pos = np.array([0, 1, 1, 0, -1, -1, 0.0]); r = np.array([0, .01, .02, 0, -.01, -.02, 0])
assert np.allclose(hp.trade_returns(pos, r), [0.03, -0.03])

# --- smoothing pulls a lone spike down, keeps a plateau ---
Z = np.full((5, 5), -0.1); Z[2, 2] = 1.0
S = hp.smooth(Z)
assert S[2, 2] < 0 and hp.neighbour_stability(Z, (2, 2)) == 0.0
P = np.full((5, 5), 0.2)
assert hp.neighbour_stability(P, (2, 2)) == 1.0 and abs(hp.smooth(P)[2, 2] - 0.2) < 1e-12

# --- walk-forward: too short -> None; honest folds otherwise ---
assert hp.walk_forward(close[:100]) is None
wf = hp.walk_forward(series(2, 1500, phi=0.25))
assert wf and len(wf["folds"]) == 5 and wf["n_trades"] >= 3 and len(wf["equity"]) == wf["n_oos_bars"]
assert all(f["fold"] == i + 1 for i, f in enumerate(wf["folds"]))

# --- verdict: a random walk must NOT pass; None and missing-Truth cases are handled ---
tmp = Path(tempfile.mkdtemp())
fails = 0
for seed in range(12):
    out = hp.evaluate(series(100 + seed, 1500), key=f"rw{seed}", root=tmp)
    fails += (not out["promote"])
assert fails == 12, f"random walks promoted: {12 - fails}"
assert hp.verdict(None) == (False, ["series too short for walk-forward"])

# --- Truth Court's t is applied when published ---
hub_core.publish("truth", [], 564, extra={"bonferroni_t": 99.0}, root=tmp)
out = hp.evaluate(series(7, 1500, phi=0.4), key="trend", root=tmp)
assert not out["promote"] and any("Truth Court" in w for w in out["why_not"])

# --- publish merges keys and counts every cell as a trial ---
snap = hub_core.read("plateau", tmp)
keys = {f["key"] for f in snap["findings"]}
assert "trend" in keys and "rw0" in keys and snap["n_trials"] == sum(f["cells"] for f in snap["findings"]) > 0
hp.evaluate(series(7, 1500, phi=0.4), key="trend", root=tmp)      # same key twice = replaced, not duplicated
assert [f["key"] for f in hub_core.read("plateau", tmp)["findings"]].count("trend") == 1
print("test_hub_plateau: all passed")
