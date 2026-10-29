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
# --- regime slicing: bars land in the regime of THEIR candle, small groups are flagged ---
wf2 = hp.walk_forward(series(2, 1500, phi=0.25))
assert wf2["oos_start"] == 1500 // 6 and len(wf2["oos_returns"]) == wf2["n_oos_bars"] == 1500 - 1500 // 6
labs = ["Trend" if i % 2 else "Chop" for i in range(1500)]
bd = hp.regime_breakdown(labs, wf2["oos_start"], wf2["oos_returns"])
assert {b["regime"] for b in bd} == {"Trend", "Chop"} and sum(b["bars"] for b in bd) == wf2["n_oos_bars"]
assert all(b["evidence"] for b in bd)
# a hand-made check: bar i of the OOS series is candle oos_start + i
tiny = hp.regime_breakdown(["", "", "A", "B", "A"], 2, [0.01, 0.02, 0.03], min_bars=2)
by = {b["regime"]: b for b in tiny}
assert by["A"]["bars"] == 2 and abs(by["A"]["mean"] - 0.02) < 1e-12 and by["B"]["bars"] == 1 and not by["B"]["evidence"] and by["B"]["sharpe"] is None
warm = hp.regime_breakdown(["", ""], 0, [0.1, -0.1])
assert warm[0]["regime"] == "warm-up"                                                    # blank labels are not a regime
assert hp.regime_breakdown(["A"], 5, [0.1])[0]["regime"] == "warm-up"                   # past the end of the labels
out_l = hp.evaluate(series(8, 1500, phi=0.2), key="lab", root=tmp, labels=labs)
assert out_l["by_regime"] and {b["regime"] for b in out_l["by_regime"]} == {"Trend", "Chop"}
assert hp.evaluate(series(8, 1500), key="nolab", root=tmp)["by_regime"] is None
f = {x["key"]: x for x in hub_core.read("plateau", tmp)["findings"]}
assert set(f["lab"]["by_regime"]) == {"Trend", "Chop"} and f["nolab"]["by_regime"] is None
assert "regime" in hp.SPEC.consumes
# the shared definition feeds both tabs the same labels
from modules import regime_lib, hub_regime
assert hub_regime.label is regime_lib.label and hub_regime.REGIMES == regime_lib.REGIMES
print("test_hub_plateau: all passed")
