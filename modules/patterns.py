"""Item 20: Finviz-style chart patterns, detected on our own candles (any market / timeframe), with the lines to draw.

Finviz's pattern set: channel up / down / horizontal, wedge up / down, triangle ascending / descending / symmetrical,
head & shoulders (+ inverse), multiple top / bottom, trendline support / resistance. Finviz does not publish its rules,
so these are this dashboard's own geometric rules:
  * swing pivots = fractal pivots (3 bars each side) inside the last WINDOW bars;
  * upper line = least-squares line through the last 2-3 swing highs, lower line = same through the swing lows;
    a line counts only if every pivot it uses lies within TOL (0.6 ATR) of it and no close between its first pivot and
    now sits more than TOL beyond it (a broken line is a breakout, which the scanner already flags separately);
  * multiple top / bottom use the zigzag swings (legs >= 1.5 ATR), so small wiggles do not count as touches;
  * slope class per line: flat if it moves less than FLAT x ATR over the window, otherwise up / down;
  * parallel = the gap between the lines now is 0.7-1.3x the gap at the pattern start; converging = gap now < 0.75x start.
Shape -> pattern: both up + parallel = channel up, both down + parallel = channel down, both flat = horizontal channel,
both up + converging = wedge up (rising wedge), both down + converging = wedge down (falling wedge), flat top + rising
bottom = triangle ascending, falling top + flat bottom = triangle descending, falling top + rising bottom = symmetrical.
'side' is the usual textbook bias, NOT a measured edge - nothing here has been backtested.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from modules.signals import atr_series, fractal_pivots, invert, zigzag

WINDOW, TOL, FLAT = 100, 0.6, 2.0
PATTERNS = {   # id -> (label, textbook bias)
    "cp_channel_up": ("Channel up", "buy"), "cp_channel_dn": ("Channel down", "sell"), "cp_channel_h": ("Horizontal channel (range)", None),
    "cp_wedge_up": ("Wedge up (rising, bearish)", "sell"), "cp_wedge_dn": ("Wedge down (falling, bullish)", "buy"),
    "cp_tri_asc": ("Triangle ascending", "buy"), "cp_tri_desc": ("Triangle descending", "sell"), "cp_tri_sym": ("Triangle symmetrical", None),
    "cp_hs": ("Head & shoulders", "sell"), "cp_ihs": ("Inverse head & shoulders", "buy"),
    "cp_multi_top": ("Multiple top (3+)", "sell"), "cp_multi_bottom": ("Multiple bottom (3+)", "buy"),
    "cp_tl_support": ("Trendline support (price on the line)", "buy"), "cp_tl_resist": ("Trendline resistance (price on the line)", "sell"),
}
SHORT = {"cp_channel_up": "Chan↑", "cp_channel_dn": "Chan↓", "cp_channel_h": "Range", "cp_wedge_up": "Wedge↑", "cp_wedge_dn": "Wedge↓",
         "cp_tri_asc": "Tri asc", "cp_tri_desc": "Tri desc", "cp_tri_sym": "Tri sym", "cp_hs": "H&S", "cp_ihs": "Inv H&S",
         "cp_multi_top": "Multi top", "cp_multi_bottom": "Multi bot", "cp_tl_support": "TL sup", "cp_tl_resist": "TL res"}


def _fit(pts):
    x = np.array([p[0] for p in pts], float); y = np.array([p[1] for p in pts], float)
    if len(pts) == 2:
        k = (y[1] - y[0]) / (x[1] - x[0]); return k, y[0] - k * x[0]
    k, b = np.polyfit(x, y, 1); return float(k), float(b)


def _line(df, piv, kind, atr):
    """Best valid line through the last 3 (else 2) pivots of one kind -> (slope, intercept, first index) or None."""
    c = df["close"].values; n = len(df)
    for m in (3, 2):
        pts = [(i, p) for i, p, k in piv if k == kind][-m:]
        if len(pts) < m:
            continue
        k, b = _fit(pts)
        if max(abs(p - (k * i + b)) for i, p in pts) > TOL * atr:
            continue
        i0 = pts[0][0]; xs = np.arange(i0, n); ln = k * xs + b
        beyond = (c[i0:] - ln) if kind == "H" else (ln - c[i0:])
        if (beyond > TOL * atr).any():
            continue
        return k, b, i0
    return None


def _cls(k, atr):
    move = k * WINDOW / atr
    return "flat" if abs(move) < FLAT else ("up" if move > 0 else "down")


def _hs(df, atr):
    """Head & shoulders on the zigzag: H L H L H, head above both shoulders by >= 0.5 ATR, shoulders within
    max(1 ATR, 25% of the head height), the right shoulder <= 25 bars old, the close still above the neckline - 1 ATR."""
    zz = zigzag(df)
    seq = zz[-5:] if zz and zz[-1][2] == "H" else zz[-6:-1]   # a pull-back low after the right shoulder is normal
    if len(seq) < 5 or [k for _, _, k in seq] != ["H", "L", "H", "L", "H"]:
        return None
    (i1, ls, _), (j1, n1, _), (i2, hd, _), (j2, n2, _), (i3, rs, _) = seq
    neck = lambda i: n1 + (n2 - n1) * (i - j1) / (j2 - j1)
    height = hd - neck(i2)
    if not (hd - max(ls, rs) >= 0.5 * atr and abs(ls - rs) <= max(atr, 0.25 * height) and height > 0
            and len(df) - 1 - i3 <= 25 and df["close"].iloc[-1] > neck(len(df) - 1) - atr):
        return None
    last = len(df) - 1
    return [(i1, ls, i2, hd), (i2, hd, i3, rs), (j1, n1, last, neck(last))]


def find(df: pd.DataFrame) -> dict:
    """-> {pattern id: [(i0, p0, i1, p1), ...] lines in df's own bar indices}. Empty dict when nothing qualifies."""
    if df is None or len(df) < 60:
        return {}
    df = df.reset_index(drop=True); n = len(df)
    atr = float(atr_series(df).iloc[-1]) or 1e-12
    piv = [p for p in fractal_pivots(df, 3) if p[0] >= n - WINDOW]
    out = {}
    up, lo = _line(df, piv, "H", atr), _line(df, piv, "L", atr)
    last, c = n - 1, float(df["close"].iloc[-1])
    seg = lambda L, i0: (i0, L[0] * i0 + L[1], last, L[0] * last + L[1])
    if up and lo:
        i0 = max(min(up[2], lo[2]), n - WINDOW)
        if last - i0 >= 15:
            g0, g1 = (up[0] - lo[0]) * i0 + up[1] - lo[1], (up[0] - lo[0]) * last + up[1] - lo[1]
            su, sl = _cls(up[0], atr), _cls(lo[0], atr)
            pid = None
            if g0 > 0 and g1 > 0:
                r = g1 / g0
                if 0.7 <= r <= 1.3:
                    pid = {("up", "up"): "cp_channel_up", ("down", "down"): "cp_channel_dn", ("flat", "flat"): "cp_channel_h"}.get((su, sl))
                elif r < 0.75:
                    pid = {("up", "up"): "cp_wedge_up", ("down", "down"): "cp_wedge_dn", ("flat", "up"): "cp_tri_asc",
                           ("down", "flat"): "cp_tri_desc", ("down", "up"): "cp_tri_sym"}.get((su, sl))
            if pid:
                out[pid] = [seg(up, i0), seg(lo, i0)]
    # price sitting on a valid trendline (within TOL), whatever the other side does
    if lo and len([1 for i, p, k in piv if k == "L" and i >= lo[2]]) >= 2 and 0 <= c - (lo[0] * last + lo[1]) <= TOL * atr:
        out["cp_tl_support"] = [seg(lo, lo[2])]
    if up and len([1 for i, p, k in piv if k == "H" and i >= up[2]]) >= 2 and 0 <= (up[0] * last + up[1]) - c <= TOL * atr:
        out["cp_tl_resist"] = [seg(up, up[2])]
    # multiple top / bottom: 3+ swing highs (lows) within TOL of each other, price back below (above) them
    zzw = [z for z in zigzag(df) if z[0] >= n - WINDOW]   # only real swings (>= 1.5 ATR legs), not every 3-bar wiggle
    for kind, pid in (("H", "cp_multi_top"), ("L", "cp_multi_bottom")):
        ps = [(i, p) for i, p, k in zzw if k == kind]
        if len(ps) >= 3:
            ref = ps[-1][1]; same = [(i, p) for i, p in ps if abs(p - ref) <= 0.4 * atr]   # tighter than the trendlines: equal highs
            if len(same) >= 3 and same[-1][0] - same[0][0] >= 20 and (c < ref - 0.3 * atr if kind == "H" else c > ref + 0.3 * atr):
                lvl = float(np.mean([p for _, p in same])); out[pid] = [(same[0][0], lvl, last, lvl)]
    hs = _hs(df, atr)
    if hs:
        out["cp_hs"] = hs
    ihs = _hs(invert(df), atr)
    if ihs:
        out["cp_ihs"] = [(a, -p, b, -q) for a, p, b, q in ihs]
    return out
