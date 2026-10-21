"""Backtest runner for Technical Office v2. Takes an entry mask (bool per bar, e.g. from strategy_rules.evaluate), walks the
bars with an ATR stop and an R target, charges the 0.1 R round-trip cost, and judges the result with the evidence gate in
kpi.py (n >= 100, t > 3, both halves positive). Pure and offline: it needs a DataFrame, never fetches data, never trades.
Big runs belong in GitHub Actions (owner approval); this is the engine they call."""
from __future__ import annotations

import numpy as np
import pandas as pd

from modules.kpi import COST_R, evidence

STOP_ATR, RR, HORIZON, COOLDOWN = 1.5, 1.5, 48, 6


def _atr(df: pd.DataFrame, n: int = 14) -> np.ndarray:
    pc = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def run(df: pd.DataFrame, entries, side: str = "long", stop_atr: float = STOP_ATR, rr: float = RR,
        horizon: int = HORIZON, cooldown: int = COOLDOWN, cost_r: float = COST_R) -> dict:
    """Gross and net R per trade. Entry at the signal bar's close; stop first when one bar touches both (conservative);
    time exit at `horizon` bars clipped to [-1, rr]. Returns the trades, summary and the evidence verdict on NET R."""
    if side not in ("long", "short"):
        raise ValueError("side must be long or short")
    need = {"high", "low", "close"}
    if not need <= set(df.columns):
        raise ValueError(f"df needs columns {sorted(need)}")
    mask = np.asarray(entries, bool)
    if len(mask) != len(df):
        raise ValueError("entries must have one value per bar")
    hi, lo, cl = (df[c].to_numpy(float) for c in ("high", "low", "close"))
    atr = _atr(df); d = 1 if side == "long" else -1
    rs, idx, last = [], [], -10**9
    for i in np.flatnonzero(mask):
        if i - last < cooldown or i < 20 or i >= len(cl) - 1 or not atr[i] > 0:
            continue
        stop_d = stop_atr * atr[i]; e = cl[i]; sl = e - d * stop_d; tp = e + d * rr * stop_d; r = None
        for j in range(i + 1, min(len(cl), i + 1 + horizon)):
            if (lo[j] <= sl) if d > 0 else (hi[j] >= sl):
                r = -1.0; break
            if (hi[j] >= tp) if d > 0 else (lo[j] <= tp):
                r = rr; break
        if r is None:
            j = min(len(cl) - 1, i + horizon)
            r = float(np.clip(d * (cl[j] - e) / stop_d, -1.0, rr))
        rs.append(r); idx.append(i); last = i
    gross = pd.Series(rs, dtype=float)
    net = gross - cost_r
    ev = evidence(net)
    return {"side": side, "n": len(rs), "entry_idx": idx, "gross_r": gross.tolist(), "net_r": net.tolist(),
            "win_rate": float((gross > 0).mean()) if rs else float("nan"),
            "gross_expectancy_r": float(gross.mean()) if rs else float("nan"),
            "net_expectancy_r": float(net.mean()) if rs else float("nan"),
            "cost_r": cost_r, "evidence": ev,
            "note": "cost 0.1 R is a planning estimate, not measured; fewer than 100 trades is not evidence"}
