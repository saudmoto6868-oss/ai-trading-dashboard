"""Monte Carlo on the owner's REAL journal trades (no invented data): resample the closed trades to see how much luck there is in the result.

What it tells (descriptions, not a forecast):
  * p_value: one-sided bootstrap test of "the average trade is above 0". The null = the same trades with their mean removed (same spread, zero edge);
    p = share of null runs whose total return is at least the sample's expected total. Small p + enough trades = the average is unlikely to be luck.
  * ruin: share of resampled runs (same number of trades) that fall more than `ruin_dd` below their own running peak.
  * final-equity range (5 % / 50 % / 95 %) of resampled runs.
Honesty rules (project rules): under MIN_N trades = NOT evidence; resampling a sample shows variability, it never proves an edge; past trades only.
"""
from __future__ import annotations

import numpy as np

from modules.lab_shared import MIN_N


def mc_summary(returns, n_paths: int = 5000, ruin_dd: float = 0.20, horizon: int | None = None, seed: int | None = None) -> dict:
    """returns = per-trade fractional returns (0.01 = +1 % of the account). Returns a dict of plain numbers + a verdict key."""
    r = np.asarray([x for x in np.asarray(returns, float).ravel() if np.isfinite(x)], float)
    n = int(r.size)
    if n < 2:
        return {"n": n, "ok": False, "verdict": "too_few"}
    rng = np.random.default_rng(seed)
    N = int(horizon or n)
    draw = r[rng.integers(0, n, size=(n_paths, N))]                    # resampled runs of N trades
    eq = np.cumprod(1.0 + draw, axis=1)
    peak = np.maximum.accumulate(np.concatenate([np.ones((n_paths, 1)), eq], axis=1), axis=1)[:, 1:]
    dd = 1.0 - eq / peak
    ruin = float((dd.max(axis=1) >= ruin_dd).mean())
    final = eq[:, -1]
    centred = r - r.mean()                                              # null: zero-mean trades
    null_tot = centred[rng.integers(0, n, size=(n_paths, N))].sum(axis=1)
    observed = float(r.mean() * N)
    p = float((np.sum(null_tot >= observed) + 1) / (n_paths + 1))
    if n < MIN_N:
        verdict = "not_evidence"
    elif p < 0.05 and r.mean() > 0:
        verdict = "unlikely_luck"
    else:
        verdict = "could_be_luck"
    q = np.percentile(final, [5, 50, 95])
    return {"n": n, "ok": True, "mean_trade": float(r.mean()), "p_value": p, "ruin": ruin, "ruin_dd": float(ruin_dd), "horizon": N,
            "final_p5": float(q[0]), "final_p50": float(q[1]), "final_p95": float(q[2]), "verdict": verdict, "paths": int(n_paths)}
