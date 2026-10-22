"""Backtest runner for Technical Office v2. Takes an entry mask (bool per bar, e.g. from strategy_rules.evaluate), walks the
bars with an ATR stop and an R target, charges the 0.1 R round-trip cost, and judges the result with the evidence gate in
kpi.py (n >= 100, t > 3, both halves positive). The split between in-sample and out-of-sample is frozen BEFORE any trade is
walked; the verdict uses the out-of-sample part only, in-sample is reported for information. Pure and offline: it needs a
DataFrame, never fetches data, never trades. Big runs belong in GitHub Actions (owner approval); this is the engine they call."""
from __future__ import annotations

import numpy as np
import pandas as pd

from modules.kpi import COST_R, evidence

STOP_ATR, RR, HORIZON, COOLDOWN, SPLIT, WARMUP = 1.5, 1.5, 48, 6, 0.5, 20


def _atr(df: pd.DataFrame, n: int = 14) -> np.ndarray:
    """Causal ATR: the value at bar i uses bars <= i only, so a later bar can never change it."""
    pc = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def freeze_split(df: pd.DataFrame, split: float = SPLIT, cut: int | None = None) -> dict:
    """Validate and fix the cut before the run. `cut` (a bar index) wins over `split` (fraction in-sample).
    Both sides need room for the warm-up bars; raises ValueError otherwise."""
    n = len(df)
    if cut is None:
        if isinstance(split, bool) or not isinstance(split, (int, float)) or not 0.1 <= split <= 0.9:
            raise ValueError("split must be a fraction between 0.1 and 0.9")
        cut = int(round(n * split))
    elif isinstance(cut, bool) or not isinstance(cut, (int, np.integer)):
        raise ValueError("cut must be a bar index (integer)")
    cut = int(cut)
    if cut < WARMUP + 2 or n - cut < 2:
        raise ValueError(f"cut {cut} leaves too few bars on one side (n={n}, warm-up {WARMUP})")
    t = df.index[cut] if isinstance(df.index, pd.DatetimeIndex) else None
    return {"cut_index": cut, "cut_time": None if t is None else str(t), "n_bars": n, "in_sample_bars": cut, "out_of_sample_bars": n - cut}


def _walk(hi, lo, cl, atr, mask, start, stop, d, stop_atr, rr, horizon, cooldown):
    """Trades whose signal bar is in [start, stop) and whose whole life fits before `stop`: nothing at or after
    `stop` is ever read. A trade still open at `stop` is dropped, not guessed."""
    rs, idx, last = [], [], -10**9
    for i in np.flatnonzero(mask[start:stop]) + start:
        if i - last < cooldown or i < WARMUP or not atr[i] > 0:
            continue
        stop_d = stop_atr * atr[i]; e = cl[i]; sl = e - d * stop_d; tp = e + d * rr * stop_d; r = None
        for j in range(i + 1, min(stop, i + 1 + horizon)):
            if (lo[j] <= sl) if d > 0 else (hi[j] >= sl):
                r = -1.0; break
            if (hi[j] >= tp) if d > 0 else (lo[j] <= tp):
                r = rr; break
        if r is None:
            j = i + horizon
            if j >= stop:
                continue
            r = float(np.clip(d * (cl[j] - e) / stop_d, -1.0, rr))
        rs.append(r); idx.append(int(i)); last = i
    return rs, idx


def _part(rs, idx, cost_r):
    gross = pd.Series(rs, dtype=float); net = gross - cost_r
    return {"n": len(rs), "entry_idx": idx, "gross_r": gross.tolist(), "net_r": net.tolist(),
            "win_rate": float((gross > 0).mean()) if rs else float("nan"),
            "gross_expectancy_r": float(gross.mean()) if rs else float("nan"),
            "net_expectancy_r": float(net.mean()) if rs else float("nan"),
            "evidence": evidence(net)}


def run(df: pd.DataFrame, entries, side: str = "long", stop_atr: float = STOP_ATR, rr: float = RR,
        horizon: int = HORIZON, cooldown: int = COOLDOWN, cost_r: float = COST_R,
        split: float = SPLIT, cut: int | None = None) -> dict:
    """Entry at the signal bar's close; stop first when one bar touches both (conservative); time exit at `horizon` bars
    clipped to [-1, rr]. In-sample = bars before the frozen cut, out-of-sample = from the cut on, each walked on its own.
    The top-level `evidence` / `n` / `net_r` are the OUT-OF-SAMPLE part; `in_sample` is for information only."""
    if side not in ("long", "short"):
        raise ValueError("side must be long or short")
    need = {"high", "low", "close"}
    if not need <= set(df.columns):
        raise ValueError(f"df needs columns {sorted(need)}")
    mask = np.asarray(entries, bool)
    if len(mask) != len(df):
        raise ValueError("entries must have one value per bar")
    frozen = freeze_split(df, split, cut)   # validated and fixed before any trade is walked
    c = frozen["cut_index"]
    hi, lo, cl = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    atr = _atr(df); d = 1 if side == "long" else -1
    ins = _part(*_walk(hi, lo, cl, atr, mask, 0, c, d, stop_atr, rr, horizon, cooldown), cost_r)
    oos = _part(*_walk(hi, lo, cl, atr, mask, c, len(cl), d, stop_atr, rr, horizon, cooldown), cost_r)
    return {"side": side, "split": frozen, "cost_r": cost_r, "verdict_on": "out_of_sample", **oos,
            "in_sample": ins, "out_of_sample": {k: v for k, v in oos.items()},
            "note": "verdict = out-of-sample only; in-sample is information. cost 0.1 R is a planning estimate, not measured; fewer than 100 trades is not evidence"}
