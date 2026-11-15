"""Plain, well-known indicator formulas (no black boxes)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    pc = df["Close"].shift()
    tr = pd.concat([df["High"] - df["Low"], (df["High"] - pc).abs(), (df["Low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def swings(df: pd.DataFrame, k: int = 3) -> tuple[list[tuple[pd.Timestamp, float]], list[tuple[pd.Timestamp, float]]]:
    """Fractal swing highs/lows: a bar higher (lower) than k bars on each side."""
    h, l = df["High"].values, df["Low"].values
    highs, lows = [], []
    for i in range(k, len(df) - k):
        if h[i] == max(h[i - k:i + k + 1]):
            highs.append((df.index[i], float(h[i])))
        if l[i] == min(l[i - k:i + k + 1]):
            lows.append((df.index[i], float(l[i])))
    return highs, lows


def clip1(x: float) -> float:
    if x is None or not np.isfinite(x):
        return 0.0
    return float(max(-1.0, min(1.0, x)))


def zscore_last(s: pd.Series, n: int) -> float:
    w = s.dropna().iloc[-n:]
    if len(w) < 5 or w.std() == 0:
        return 0.0
    return float((w.iloc[-1] - w.mean()) / w.std())
