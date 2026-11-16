"""Statistical & execution helpers for strategy_lab (Tasks 4, 5, 7, 8)."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence, Tuple
import math
import numpy as np
import pandas as pd
from scipy.stats import false_discovery_control


def dedup_clusters(
    trades: Sequence[Dict[str, Any]],
    candle_bucket_seconds: int = 3600,
) -> List[Dict[str, Any]]:
    """Keep one trade per (symbol, cluster_id)."""
    seen: set[Tuple[str, Any]] = set()
    unique: List[Dict[str, Any]] = []
    for tr in trades:
        sym = str(tr.get("symbol", "ALL"))
        if "cluster_id" in tr and tr["cluster_id"] is not None:
            cid = tr["cluster_id"]
        else:
            ts = tr.get("candle_ts") or tr.get("timestamp") or tr.get("open_time") or 0
            cid = int(float(ts) // candle_bucket_seconds)
        key = (sym, cid)
        if key not in seen:
            seen.add(key)
            unique.append(tr)
    return unique


def block_bootstrap(
    returns_r: Sequence[float],
    n_resamples: int = 1000,
    block_size: int = 5,
    seed: int = 42,
) -> Dict[str, float]:
    """Moving-block bootstrap preserving temporal order."""
    arr = np.asarray(returns_r, dtype=float)
    n = len(arr)
    if n < 2:
        return {"t_bootstrap": 0.0, "ci_low": 0.0, "ci_high": 0.0, "mean_r": float(arr.mean()) if n else 0.0}

    rng = np.random.default_rng(seed)
    b = max(1, min(block_size, n))
    n_blocks = math.ceil(n / b)
    max_start = max(1, n - b + 1)

    t_stats = np.empty(n_resamples, dtype=float)
    means = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        starts = rng.integers(0, max_start, size=n_blocks)
        sample = np.concatenate([arr[s : s + b] for s in starts])[:n]
        std = sample.std(ddof=1)
        m = sample.mean()
        means[i] = m
        t_stats[i] = (m / (std / math.sqrt(n))) if std > 0 else 0.0

    return {
        "t_bootstrap": round(float(np.mean(t_stats)), 4),
        "ci_low": round(float(np.percentile(means, 2.5)), 4),
        "ci_high": round(float(np.percentile(means, 97.5)), 4),
        "mean_r": round(float(np.mean(means)), 4),
    }


def oos_split_by_date(
    df: pd.DataFrame,
    date_col: str = "timestamp",
    train_pct: float = 0.60,
    val_pct: float = 0.20,
    purge_bars: int = 5,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Chronological 60/20/20 split with purge gaps."""
    if df.empty or date_col not in df.columns:
        return df, df.iloc[0:0].copy(), df.iloc[0:0].copy()

    ordered = df.sort_values(date_col).reset_index(drop=True)
    n = len(ordered)
    i1 = int(n * train_pct)
    i2 = int(n * (train_pct + val_pct))
    train = ordered.iloc[: max(0, i1 - purge_bars)].copy()
    val = ordered.iloc[i1 : max(i1, i2 - purge_bars)].copy()
    test = ordered.iloc[i2:].copy()
    return train, val, test


def apply_bh_correction(
    rows: Sequence[Dict[str, Any]],
    p_col: str = "p_value",
    alpha: float = 0.05,
) -> Tuple[List[Dict[str, Any]], str]:
    """Apply Benjamini-Hochberg FDR correction."""
    if not rows:
        return [], f"After multiple-testing correction (BH, α={alpha:.0%}): 0 rows pass"

    pvals = np.asarray([float(r.get(p_col, 1.0)) for r in rows], dtype=float)
    adj_p = false_discovery_control(pvals, method="bh")
    ranks = np.argsort(np.argsort(pvals)) + 1

    updated: List[Dict[str, Any]] = []
    passed = 0
    for row, q_val, rank in zip(rows, adj_p, ranks):
        sig = bool(q_val <= alpha)
        if sig:
            passed += 1
        updated.append(
            {
                **row,
                "p_value": float(row.get(p_col, 1.0)),
                "significant_bh": sig,
                "fdr_rank": int(rank),
                "bh_adjusted_p": round(float(q_val), 6),
            }
        )

    summary = f"After multiple-testing correction (BH, α={alpha:.0%}): {passed} rows pass"
    return updated, summary


def simulate_limit_fill(
    order_price: float,
    side: str,
    candle_close: float,
    fill_distance: float = 0.0,
) -> bool:
    """Limit fill requires price to clear order by fill_distance (0.0 = touch)."""
    s = side.lower()
    if s in ("buy", "long"):
        return candle_close < (order_price - fill_distance) if fill_distance > 0 else candle_close <= order_price
    return candle_close > (order_price + fill_distance) if fill_distance > 0 else candle_close >= order_price


def run_fill_sensitivity(
    orders: Sequence[Dict[str, Any]],
    distances: Iterable[float] = (0.0, 0.5, 1.0),
) -> List[Dict[str, Any]]:
    """Evaluate fill rate across fill_distance sensitivity grid."""
    results: List[Dict[str, Any]] = []
    for d in distances:
        filled = sum(
            1
            for o in orders
            if simulate_limit_fill(o["order_price"], o["side"], o["candle_close"], fill_distance=d)
        )
        results.append(
            {
                "fill_distance": float(d),
                "filled_count": filled,
                "total_orders": len(orders),
                "note": f"Realistic fill assumption: gap {d} points past order level",
            }
        )
    return results


def aggregate_by_regime(trades: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aggregate n, win %, and avg R across market regimes."""
    buckets: Dict[str, List[float]] = {}
    for tr in trades:
        reg = str(tr.get("regime", "Unknown"))
        buckets.setdefault(reg, []).append(float(tr.get("pnl_r", 0.0)))

    summary: List[Dict[str, Any]] = []
    for reg, rs in sorted(buckets.items()):
        n = len(rs)
        wins = sum(1 for r in rs if r > 0)
        summary.append(
            {
                "regime": reg,
                "n": n,
                "regime_win_pct": round((wins / n) * 100.0, 2) if n else 0.0,
                "regime_avg_r": round(sum(rs) / n, 4) if n else 0.0,
            }
        )
    return summary
