"""SMT divergence (Smart Money Tool): two CORRELATED markets are compared swing by swing on the SAME timeframe.
Bullish: A prints a lower swing low while B holds a higher low (B refuses to confirm). Bearish: A prints a higher
swing high while B fails to make one. Inverse pairs (DXY vs EURUSD / gold) are handled by mirroring B.

Pairs: crypto majors (OKX, 24/7, candles line up exactly) and, from the Yahoo feed, forex / gold / silver against the
dollar index (inverse) and a few index pairs. Candles are matched on time; daily bars of different venues are matched by
calendar day. Too little overlap or |correlation| < MIN_CORR -> no signal (never a guess)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from modules.signals import _finalize, _mk, atr_series, fractal_pivots, invert

MIN_CORR = 0.5   # |correlation| of the last 100 returns needed for a divergence to mean anything

# (A, B, inverse). "Y:" ids come from the Yahoo feed (forex / gold / indices); inverse=True means B moves AGAINST A (USD pairs vs the dollar index).
DXY = "Y:DX-Y.NYB"
SMT_PAIRS = [
    ("BTC-USDT", "ETH-USDT", False), ("BTC-USDT", "SOL-USDT", False), ("ETH-USDT", "SOL-USDT", False),
    ("ETH-USDT", "BNB-USDT", False), ("SOL-USDT", "AVAX-USDT", False),
    # forex / metals vs the dollar (inverse) and USD-quoted majors against each other
    ("Y:EURUSD=X", DXY, True), ("Y:GBPUSD=X", DXY, True), ("Y:AUDUSD=X", DXY, True), ("Y:GC=F", DXY, True), ("Y:SI=F", DXY, True),
    ("Y:EURUSD=X", "Y:GBPUSD=X", False), ("Y:AUDUSD=X", "Y:NZDUSD=X", False), ("Y:GC=F", "Y:SI=F", False),
    ("Y:USDJPY=X", "Y:EURUSD=X", True), ("Y:USDCHF=X", "Y:EURUSD=X", True),
    # US indices
    ("Y:^GSPC", "Y:^IXIC", False), ("Y:^NDX", "Y:^GSPC", False), ("Y:^DJI", "Y:^GSPC", False),
]


def peers_of(symbol: str):
    """-> [(peer_symbol, inverse)] for one symbol (perp / futures ids map to their spot id)."""
    base = symbol.split("-SWAP")[0]
    if base.count("-") > 1:
        base = "-".join(base.split("-")[:2])
    out = []
    for a, b, inv in SMT_PAIRS:
        if a == base:
            out.append((b, inv))
        elif b == base:
            out.append((a, inv))
    return out


def _smt_bull(a: pd.DataFrame, b: pd.DataFrame, label: str, max_age: int = 15, min_gap: int = 5, max_gap: int = 60):
    """a, b share the same index (aligned candles). Returns bullish-SMT signals for the *pair* (A made the lower low)."""
    piv = [(i, p) for i, p, k in fractal_pivots(a, 3) if k == "L"]
    n = len(a)
    if len(piv) < 2 or n - 1 - piv[-1][0] > max_age:
        return []
    la, lb, ca = a["low"].values, b["low"].values, a["close"].values
    atr_a, atr_b = float(atr_series(a).iloc[-1]), float(atr_series(b).iloc[-1])
    i2, p2 = piv[-1]
    if la[i2 + 1:].size and la[i2 + 1:].min() <= p2:
        return []
    if ca[-1] < p2 + 0.3 * atr_a:
        return []
    for i1, p1 in reversed(piv[:-1][-3:]):
        if not (min_gap <= i2 - i1 <= max_gap) or p2 >= p1 - 0.1 * atr_a or la[i1 + 1:i2].min() <= p2:
            continue
        b1 = float(lb[max(0, i1 - 3):i1 + 4].min())          # B's low around A's first swing
        b2 = float(lb[max(0, i2 - 3):].min())                # B's lowest since A's second swing
        if b2 >= b1 + 0.1 * atr_b:
            return [_mk("Liquidity", f"SMT divergence vs {label}",
                        "SMT: this market made a new low {p2} (previous low {p1}) but " + label + " did NOT confirm - it held above its own previous low; "
                        "correlated markets disagree, the footprint of a smart-money reversal",
                        prices={"p1": p1, "p2": p2}, vals={"peer": label})]
    return []


def _align(df: pd.DataFrame, peer_df: pd.DataFrame) -> pd.DataFrame:
    """Merge the two candle sets on time. Daily / weekly bars of different venues (forex vs futures) start at different
    hours, so when the exact merge is too short and the bars are >= ~1 day apart, match them by calendar day."""
    cols = ["time", "open", "high", "low", "close"]
    m = df[cols].merge(peer_df[cols], on="time", suffixes=("", "_b"))
    if len(m) >= 60:
        return m
    step = df["time"].diff().median()
    if pd.notna(step) and step >= pd.Timedelta(hours=20):
        a, b = df[cols].copy(), peer_df[cols].copy()
        a["time"], b["time"] = a["time"].dt.normalize(), b["time"].dt.normalize()
        return a.drop_duplicates("time").merge(b.drop_duplicates("time"), on="time", suffixes=("", "_b"))
    return m


def smt_signals(df: pd.DataFrame, peer_df: pd.DataFrame, peer_label: str, inverse: bool = False):
    """Finalized signals (same dict shape as detect_all) for the scanned market `df` against one correlated `peer_df`.
    Both directions, and both roles (this market made the extreme / the peer did)."""
    if df is None or peer_df is None or "time" not in df.columns or "time" not in peer_df.columns:
        return []
    m = _align(df, peer_df)
    if len(m) < 60:
        return []
    m = m.sort_values("time").reset_index(drop=True)
    a = m[["time", "open", "high", "low", "close"]]
    b = m[["open_b", "high_b", "low_b", "close_b"]].rename(columns=lambda c: c[:-2])
    cr = a["close"].pct_change().tail(100).corr(b["close"].pct_change().tail(100))   # ignore SMT when the pair has decoupled
    if not np.isfinite(cr) or (cr > -MIN_CORR if inverse else cr < MIN_CORR):
        return []
    if inverse:
        b = invert(b)
    out = []
    for flipped in (False, True):
        fa, fb = (invert(a), invert(b)) if flipped else (a, b)
        sigs = _smt_bull(fa, fb, peer_label) or _smt_bull(fb, fa, peer_label)   # A swept / or the peer swept and A held
        out += [_finalize(s, flipped) for s in sigs]
    return out
