"""Price action + range schools the scanner did not have as SETUPS (audit 2026-11-06, docs/SCHOOLS_COVERAGE_2026-11-06.md).

All of these are written for the BULLISH case on the last candle; signals.detect_all runs them on the mirrored frame too (bearish twin, text flipped by signals._flip_text).
They are CONTEXT signals (family "PA": shown as tags / flags, never a star and never a trade by themselves, see scorer.CONTEXT_FAMILIES) and they are in signals.DETECTORS, so the
weekly strategy lab measures every key below (docs/academy/DEVELOPMENT_NOTES.md: nothing is promoted to primary without lab evidence and real costs).

  pa_engulf  bullish engulfing at support (after a decline)       pa_pin   hammer / pin bar at support (or after a sweep of it)
  pa_inside  inside-bar breakout (mother bar >= 1 ATR) in an uptrend / at support
  pa_star    morning star (3 candles) at a swing low
  rect       rectangle (range, >= 3 touches each side) breakout, and the retest of the broken edge
  dbl        double bottom: neckline break
  wyck       Wyckoff spring: range low pierced and reclaimed

No win rate is claimed here: the rules are textbook geometry, unvalidated until the lab has n >= 30 per key."""
from __future__ import annotations

import numpy as np



def _s():
    import modules.signals as sig   # lazy: signals.py imports this module at its end (DETECTORS), so a top-level import would be circular
    return sig


def _mk(*a, **k):
    return _s()._mk(*a, **k)


def atr_series(df):
    return _s().atr_series(df)


def fractal_pivots(df, n=3):
    return _s().fractal_pivots(df, n)


FAM = "PA"


def _arr(df):
    return (df[c].to_numpy(float) for c in ("open", "high", "low", "close"))


def _atr(df):
    a = float(atr_series(df).iloc[-1])
    return a if np.isfinite(a) and a > 0 else 0.0


def _support(df, atr, lo_price, close, look=80):
    """Level of the most recent confirmed swing low the last candles are AT (within 0.5 ATR) or swept and reclaimed; None if there is none."""
    n = len(df)
    for i, p, k in reversed(fractal_pivots(df, 3)):
        if k != "L" or n - 1 - i > look or n - 1 - i < 4:
            continue
        if abs(lo_price - p) <= 0.5 * atr or (lo_price < p and close > p):
            return p
    return None


def pa_engulf_bull(df):
    if len(df) < 40:
        return []
    o, h, l, c = _arr(df)
    atr = _atr(df)
    if not atr or not (c[-2] < o[-2] and c[-1] > o[-1] and o[-1] <= c[-2] and c[-1] >= o[-2]) or c[-1] - o[-1] < 0.8 * atr or not c[-2] < c[-7]:
        return []
    lvl = _support(df, atr, float(min(l[-2:])), float(c[-1]))
    if lvl is None:
        return []
    return [_mk(FAM, "Bullish engulfing at support", "a candle body engulfed the previous bearish body at support {lvl}, after a decline: buyers took over at the level",
                prices={"lvl": lvl, "sl": float(min(l[-2:]))}, vals={"body": round((c[-1] - o[-1]) / atr, 2)}, zone=(float(min(l[-2:])), float(c[-1])))]


def pa_pin_bull(df):
    if len(df) < 40:
        return []
    o, h, l, c = _arr(df)
    atr = _atr(df)
    rng = h[-1] - l[-1]
    body = abs(c[-1] - o[-1])
    lw, uw = min(o[-1], c[-1]) - l[-1], h[-1] - max(o[-1], c[-1])
    if not atr or rng < 0.9 * atr or lw < 2 * max(body, 0.1 * rng) or uw > 0.25 * rng or c[-1] < l[-1] + 0.6 * rng or not c[-1] < c[-6]:
        return []
    lvl = _support(df, atr, float(l[-1]), float(c[-1]))
    if lvl is None:
        return []
    return [_mk(FAM, "Hammer / pin bar at support", "long lower wick rejected support {lvl} (the close is in the upper part of the candle): sellers were refused",
                prices={"lvl": lvl, "sl": float(l[-1])}, vals={"wick": round(lw / max(rng, 1e-12), 2)}, zone=(float(l[-1]), float(min(o[-1], c[-1]))))]


def pa_inside_bull(df):
    if len(df) < 60:
        return []
    o, h, l, c = _arr(df)
    atr = _atr(df)
    if not atr or not (h[-2] <= h[-3] and l[-2] >= l[-3]) or h[-3] - l[-3] < atr or not (c[-1] > h[-3] and c[-1] > o[-1]):
        return []
    cs = df["close"]
    up = float(cs.ewm(span=21, adjust=False).mean().iloc[-1]) > float(cs.ewm(span=50, adjust=False).mean().iloc[-1])
    lvl = _support(df, atr, float(l[-3]), float(c[-1]))
    if not (up or lvl is not None):
        return []
    return [_mk(FAM, "Inside-bar breakout", "the candle inside the mother bar was broken: a close above the mother bar high {hi} (uptrend or at support)",
                prices={"hi": float(h[-3]), "sl": float(l[-3])}, vals={}, zone=(float(l[-3]), float(h[-3])))]


def pa_star_bull(df):
    if len(df) < 40:
        return []
    o, h, l, c = _arr(df)
    atr = _atr(df)
    b1, b2 = abs(c[-3] - o[-3]), abs(c[-2] - o[-2])
    if not atr or not (c[-3] < o[-3] and b1 >= 0.8 * atr and b2 <= 0.35 * atr and b2 <= 0.3 * max(h[-2] - l[-2], 1e-12) + 0.35 * atr and max(o[-2], c[-2]) <= c[-3] + 0.1 * atr
                       and c[-1] > o[-1] and c[-1] > (o[-3] + c[-3]) / 2):
        return []
    low = float(min(l[-3:]))
    if low > float(np.min(l[-31:-3])) + 1.0 * atr:   # a star in the middle of nowhere is not a bottom
        return []
    return [_mk(FAM, "Morning star at a swing low", "bearish candle, small indecision candle, then a bullish candle closing above the middle of the first one, at a swing low {lo}",
                prices={"lo": low, "sl": low}, vals={}, zone=(low, float(c[-1])))]


def _range(df, atr, seg_end, W):
    """(R, S, touches_R, touches_S) of the box in bars [seg_end - W, seg_end): closes inside, >= 3 separate touches of the top and of the bottom (>= 2 for a spring); None if it is not a box."""
    if seg_end - W < 5:
        return None
    h, l, c = (df[x].to_numpy(float)[seg_end - W:seg_end] for x in ("high", "low", "close"))
    R, S = float(np.sort(h)[-2:].mean()), float(np.sort(l)[:2].mean())
    height = R - S
    if not (1.5 * atr <= height <= 7 * atr) or c.max() > R + 0.3 * atr or c.min() < S - 0.3 * atr:
        return None

    def touches(arr, lvl, above):
        idx = np.flatnonzero((arr >= lvl - 0.3 * atr) if above else (arr <= lvl + 0.3 * atr))
        return int(1 + (np.diff(idx) >= 3).sum()) if len(idx) else 0

    return R, S, touches(h, R, True), touches(l, S, False)


def rect_bull(df):
    if len(df) < 80:
        return []
    o, h, l, c = _arr(df)
    atr = _atr(df)
    if not atr:
        return []
    n = len(df)
    for W in (30, 50):
        seg_end = n - 4
        box = _range(df, atr, seg_end, W)
        if not box or box[2] < 3 or box[3] < 3:
            continue
        R, S = box[0], box[1]
        after_c, after_l = c[seg_end:], l[seg_end:]
        if after_c.max() <= R + 0.15 * atr or c[-1] <= R:
            continue
        retest = bool(after_l.min() <= R + 0.3 * atr and c[-1] > R + 0.1 * atr and np.argmax(after_c > R + 0.15 * atr) < len(after_c) - 1)
        nm = "Rectangle breakout retest" if retest else "Rectangle breakout"
        return [_mk(FAM, nm, "price closed above a rectangle (top {hi}, bottom {lo}, " + f"{box[2]} / {box[3]}" + " touches) " + ("and retested the broken top: support now" if retest else "") ,
                    prices={"hi": R, "lo": S}, vals={"touches": min(box[2], box[3]), "retest": int(retest)}, zone=(R - 0.3 * atr, R + 0.3 * atr))]
    return []


def dbl_bull(df):
    if len(df) < 70:
        return []
    o, h, l, c = _arr(df)
    atr = _atr(df)
    if not atr:
        return []
    n = len(df)
    lows = [(i, p) for i, p, k in fractal_pivots(df, 3) if k == "L" and n - 1 - i <= 50]
    for a in range(len(lows) - 1, 0, -1):
        i2, p2 = lows[a]
        if n - 1 - i2 > 25:
            continue
        for b in range(a - 1, -1, -1):
            i1, p1 = lows[b]
            if not (8 <= i2 - i1 <= 60) or abs(p1 - p2) > 0.5 * atr:
                continue
            neck = float(h[i1:i2 + 1].max())
            if neck - max(p1, p2) < 2 * atr or not (c[-1] > neck + 0.1 * atr and c[-4] <= neck):
                continue
            return [_mk(FAM, "Double bottom neckline break", "two lows at {lo} ({gap} bars apart) and a close above the neckline {neck}",
                        prices={"lo": float(min(p1, p2)), "neck": neck, "sl": float(min(p1, p2))}, vals={"gap": i2 - i1}, zone=(neck - 0.3 * atr, neck + 0.3 * atr))]
    return []


def wyck_bull(df):
    if len(df) < 80:
        return []
    o, h, l, c = _arr(df)
    atr = _atr(df)
    if not atr:
        return []
    n = len(df)
    for W in (30, 50):
        seg_end = n - 4
        box = _range(df, atr, seg_end, W)
        if not box or box[2] < 2 or box[3] < 2:
            continue
        R, S = box[0], box[1]
        pierce = float(l[-3:].min())
        if S - 1.2 * atr <= pierce < S - 0.1 * atr and c[-1] > S and c[-1] > o[-1] and c[-1] < R:
            return [_mk(FAM, "Wyckoff spring (range low swept, then reclaimed)", "price dipped below the range low {lo} to {sp} and closed back inside the range (top {hi}): a spring",
                        prices={"lo": S, "hi": R, "sp": pierce, "sl": pierce}, vals={"touches": min(box[2], box[3])}, zone=(pierce, S))]
    return []


PA_DETECTORS = (pa_engulf_bull, pa_pin_bull, pa_inside_bull, pa_star_bull, rect_bull, dbl_bull, wyck_bull)
