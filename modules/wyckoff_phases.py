"""WYCKOFF ACCUMULATION PHASES (A to E), bullish case only, on the last candles of one frame (owner 2026-11-09: "Wyckoff phases").

What it labels (a textbook reading of an accumulation range, NOT a signal and NOT validated):
  SC  selling climax: a wide-range low after a decline (volume spike when volume exists)
  AR  automatic rally: the high of the bounce right after the SC (= range top R, SC low = range bottom S)
  ST  secondary test: a later low back near S on lower volume / smaller range than the SC
  SPR spring: a dip below S that closes back above it
  SOS sign of strength: a close above R
  LPS last point of support: after the SOS, a pullback that holds above R
Phase: A = SC + AR (+ ST), B = the range builds (2+ tests of S or R), C = a spring, D = a SOS, E = price clearly above R after an LPS (>= 1 ATR).
A CONTEXT label in family "PA" terms: shown as a tag, never a star, never a trade by itself. It is not in signals.DETECTORS yet: the weekly lab has to measure it first
(docs/academy/DEVELOPMENT_NOTES.md). A distribution (bearish) twin is obtained by running the same function on the mirrored frame (signals._flip_text for the words)."""
from __future__ import annotations

import numpy as np

LOOK = 90          # candles scanned
MIN_DROP_ATR = 3.0  # decline into the SC


def _atr(df) -> float:
    from modules.signals import atr_series
    a = float(atr_series(df).iloc[-1])
    return a if np.isfinite(a) and a > 0 else 0.0


def analyze(df) -> dict | None:
    """{'phase': 'A'..'E', 'events': [(name, bar_index_from_end, price)], 'S': .., 'R': .., 'bias': 'bullish'} or None when no accumulation structure is found."""
    if df is None or len(df) < LOOK + 40:
        return None
    atr = _atr(df)
    if not atr:
        return None
    seg = df.iloc[-LOOK:]
    h, l, c = (seg[x].to_numpy(float) for x in ("high", "low", "close"))
    v = seg["volume"].to_numpy(float) if "volume" in seg else None
    n = len(seg)
    rng = h - l
    # SC: the climax bar = biggest range x volume among the bars near the window's lows (a later spring may print a LOWER low than the SC, that is normal)
    cut = n - 4
    score = rng * (v / max(float(np.median(v)), 1e-12) if v is not None else 1.0)
    low_zone = np.flatnonzero(l[:cut] <= np.percentile(l, 25))
    if not len(low_zone):
        return None
    i_sc = int(low_zone[np.argmax(score[low_zone])])
    if i_sc < 8:
        return None
    if h[max(0, i_sc - 15):i_sc].max() - l[i_sc] < MIN_DROP_ATR * atr or rng[i_sc] < 1.2 * atr:
        return None
    if v is not None and v[i_sc] < 1.3 * float(np.median(v)):
        return None   # no volume climax
    # AR: highest high within 12 bars after the SC
    j_end = min(n, i_sc + 13)
    i_ar = i_sc + 1 + int(np.argmax(h[i_sc + 1:j_end]))
    S, R = float(l[i_sc]), float(h[i_ar])
    if R - S < 1.5 * atr or R - S > 14 * atr:
        return None
    ev = [("SC", i_sc, S), ("AR", i_ar, R)]
    after = range(i_ar + 1, n)
    tests, spring, sos, lps = [], None, None, None
    for i in after:
        if spring is None and sos is None and abs(l[i] - S) <= 0.5 * atr and l[i] >= S - 0.1 * atr and (rng[i] < rng[i_sc]) and (v is None or v[i] < v[i_sc]):
            if not tests or i - tests[-1] >= 3:
                tests.append(i)
        if spring is None and sos is None and l[i] < S - 0.1 * atr and c[i] > S and S - l[i] <= 1.5 * atr:
            spring = i
        if sos is None and c[i] > R + 0.15 * atr and (spring is not None or len(tests) >= 1):
            sos = i
        elif sos is not None and lps is None and i > sos + 1 and R - 0.3 * atr <= l[i] <= R + 0.6 * atr and c[i] > R:
            lps = i
    for t in tests:
        ev.append(("ST", t, float(l[t])))
    if spring is not None:
        ev.append(("SPR", spring, float(l[spring])))
    if sos is not None:
        ev.append(("SOS", sos, float(c[sos])))
    if lps is not None:
        ev.append(("LPS", lps, float(l[lps])))
    last = float(c[-1])
    if sos is not None and lps is not None and last >= R + 1.0 * atr:
        phase = "E"
    elif sos is not None:
        phase = "D"
    elif spring is not None:
        phase = "C"
    elif len(tests) >= 2 or (len(tests) >= 1 and n - 1 - i_ar > 15):
        phase = "B"
    else:
        phase = "A"
    if last < S - 1.5 * atr:      # range broken down: the reading is void
        return None
    return {"phase": phase, "events": [(nm, n - 1 - i, p) for nm, i, p in ev], "S": S, "R": R, "bias": "bullish", "atr": atr}


def tag(df) -> list:
    """Context signals for signals/scorer style tags; empty when there is no structure. Not wired into DETECTORS (lab first)."""
    r = analyze(df)
    if not r:
        return []
    return [{"family": "PA", "key": "wyck_phase", "name": f"Wyckoff accumulation: phase {r['phase']}", "direction": "bullish", "icon": "W",
             "text": f"range {r['S']:.6g} - {r['R']:.6g}, events: " + ", ".join(e[0] for e in r["events"]), "context": True}]
