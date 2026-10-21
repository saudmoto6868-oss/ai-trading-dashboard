"""KPI strip for the trade journal: counts, win rate, expectancy in R, profit factor, drawdown in R, cost-adjusted
expectancy, and an evidence badge that uses our own gate (n >= 100, t > 3, average R > 0 in both halves).

Pure functions on a DataFrame with an 'r' column (R multiples, +2 = won twice the risk). Optional 'symbol' and
'strategy' columns feed breakdown(). Nothing here places an order."""
import math

import numpy as np
import pandas as pd

GATE_N = 100        # minimum trades before any result can count as evidence
GATE_T = 3.0        # minimum t-statistic of the mean R vs 0
COST_R = 0.1        # planning estimate per trade in R (the lab uses the same number); not measured


def _r(df: pd.DataFrame) -> pd.Series:
    if "r" not in df.columns:
        raise ValueError("journal needs an 'r' column (R multiples)")
    return pd.to_numeric(df["r"], errors="coerce").dropna().astype(float).reset_index(drop=True)


def evidence(r: pd.Series) -> dict:
    """Badge for one set of trades: 'not evidence' (n < 100), 'passes gate', or 'not yet' (n >= 100 but a test fails)."""
    n = int(len(r))
    if n < 2:
        return {"badge": "not evidence", "n": n, "t": float("nan"), "halves": (float("nan"), float("nan"))}
    sd = float(r.std(ddof=1))
    t = float(r.mean() / (sd / math.sqrt(n))) if sd > 0 else float("nan")
    h = n // 2
    h1, h2 = float(r.iloc[:h].mean()) if h else float("nan"), float(r.iloc[h:].mean())
    passes = n >= GATE_N and t > GATE_T and h1 > 0 and h2 > 0
    if n < GATE_N:
        badge = "not evidence"
    else:
        badge = "passes gate" if passes else "not yet"
    return {"badge": badge, "n": n, "t": t, "halves": (h1, h2)}


def kpis(df: pd.DataFrame) -> dict:
    """The six headline numbers for the strip, plus the evidence block."""
    r = _r(df)
    n = int(len(r))
    if n == 0:
        return {"n": 0, "win_rate": float("nan"), "expectancy_r": float("nan"), "profit_factor": float("nan"),
                "max_dd_r": float("nan"), "net_expectancy_r": float("nan"), "evidence": evidence(r)}
    wins, losses = r[r > 0], r[r < 0]
    gross_loss = float(-losses.sum())
    cum = r.cumsum()
    dd = float((cum - cum.cummax()).min())   # worst fall from a running peak, in R (0 = never below a peak)
    return {
        "n": n,
        "win_rate": float((r > 0).mean()),
        "expectancy_r": float(r.mean()),
        "profit_factor": float(wins.sum() / gross_loss) if gross_loss > 0 else float("inf") if len(wins) else float("nan"),
        "max_dd_r": dd,
        "net_expectancy_r": float(r.mean() - COST_R),
        "evidence": evidence(r),
    }


def breakdown(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """One row per value of `key` (e.g. 'symbol' or 'strategy'): n, win rate, expectancy R, and the evidence badge."""
    if key not in df.columns:
        raise ValueError(f"journal has no '{key}' column")
    rows = []
    for name, grp in df.groupby(key):
        r = _r(grp)
        if not len(r):
            continue
        ev = evidence(r)
        rows.append({key: name, "n": int(len(r)), "win_rate": float((r > 0).mean()), "expectancy_r": float(r.mean()),
                     "t": ev["t"], "badge": ev["badge"]})
    return pd.DataFrame(rows).sort_values("expectancy_r", ascending=False).reset_index(drop=True) if rows else pd.DataFrame(
        columns=[key, "n", "win_rate", "expectancy_r", "t", "badge"])
