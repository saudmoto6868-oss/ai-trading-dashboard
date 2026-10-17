"""Out-of-sample test of the Workspace 'Gann zone trades' (same rules as workspace_app.html gannFit / gannTrades, timeframe grid only).

Walk-forward: the Gann grid (start swing, spacing, time spacing) is fitted on the first FIT_SHARE of the candles only; the zone rule then trades
the remaining candles it never saw:
  * time windows = start + k x time spacing (+- ZW bars); price levels = Se7s grid (averages, square, secondary angles, rings to cover the range);
  * a candle touching a level (+- 0.25 ATR) that closes back away from it (body in that direction, > 0.1 ATR past the level) = entry at its close;
  * stop = beyond the touch - 0.25 ATR; TP1 = next level in the direction at >= 1R (else 1.5R); time stop = the second time window after entry.
Baseline = the same entries with a random direction (same stop distance / target in R). No costs: real results are worse."""
from __future__ import annotations

import math

import numpy as np

FIT_SHARE, ZW, K_PIV = 0.6, 2, 5


def pivots(h, l, K=K_PIV):
    out = []
    for i in range(K, len(h) - K):
        if h[i] == h[i - K:i + K + 1].max():
            out.append((i, h[i], 1))
        if l[i] == l[i - K:i + K + 1].min():
            out.append((i, l[i], -1))
    return out


def grid(P, s, d, cycles=1, shape=4, sec=True):
    step = 360 / shape / (2 if sec else 1); out = [P]; base = P
    for _ in range(cycles):
        r = math.sqrt(base / s); L = ((r + 2) ** 2 if d > 0 else max(0.0, r - 2) ** 2) * s
        a = step
        while a <= 360 + 1e-9:
            out.append(base + (L - base) * a / 360); a += step
        base = L
    return out


def cycles_needed(P, s, d, lo, hi):
    base, c = P, 0
    while c < 12:
        c += 1; r = math.sqrt(base / s); base = ((r + 2) ** 2 if d > 0 else max(0.0, r - 2) ** 2) * s
        if (base >= hi) if d > 0 else (base <= lo):
            break
    return c


def fit(h, l, c):
    """-> dict(P, s, i0, tsp) fitted on these candles only, or None (mirrors gannFit)."""
    n = len(h)
    if n < 60:
        return None
    piv = pivots(h, l)
    if len(piv) < 8:
        return None
    tr = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1]))); atr = float(tr.mean()); tol = 0.25 * atr
    W = max(20, round(n * 0.08))
    major = [q for q in piv if q[0] <= n * 0.9 and (h[max(0, q[0] - W):q[0] + W + 1].max() <= q[1] if q[2] > 0 else l[max(0, q[0] - W):q[0] + W + 1].min() >= q[1])][-14:]
    best = None
    for i0, P, _ in major:
        lo, hi = float(l[i0:].min()), float(h[i0:].max()); later = [q for q in piv if q[0] > i0 + 5]
        if len(later) < 6:
            continue
        for d in (1, -1):
            for k in range(-4, 7):
                for m in (1, 2, 2.5, 5):
                    s = m * 10 ** k; R = 4 * math.sqrt(P * s) + 4 * s
                    if not (0.04 * P <= R <= 1.2 * P):
                        continue
                    lv = np.array(grid(P, s, d, cycles_needed(P, s, d, lo, hi)))
                    hits = sum(1 for q in later if np.abs(lv - q[1]).min() <= tol)
                    if hits < 4:
                        continue
                    gap = abs(lv[-1] - P) / max(1, len(lv) - 1)
                    mu = np.mean([sum(1 for q in later if np.abs(lv + f * gap - q[1]).min() <= tol) for f in (.2, .4, .6, .8)])
                    z = (hits - mu) / math.sqrt(mu + 1)
                    if best is None or z > best["z"]:
                        best = {"P": P, "s": s, "d": d, "i0": i0, "z": z}
    if not best:
        return None
    later_i = [q[0] for q in piv if q[0] > best["i0"] + 5]; bt = None
    for tsp in (30, 36, 40, 45, 60, 72, 90, 120, 144, 180):
        def hits_t(off):
            h_ = m_ = 0; t = best["i0"] + tsp + off
            while t < n - 2:
                m_ += 1; h_ += any(abs(i - t) <= 2 for i in later_i); t += tsp
            return h_, m_
        hh, mm = hits_t(0)
        if mm < 2:
            continue
        mu = np.mean([hits_t(round(f * tsp))[0] for f in (.25, .5, .75)]); z = (hh - mu) / math.sqrt(mu + 1)
        if bt is None or z > bt[1]:
            bt = (tsp, z)
    best["tsp"] = bt[0] if bt else 90; best["atr"] = atr
    return best


def trade_test(df, rng):
    """-> list of (R, R_random) for zone trades in the out-of-sample part of one series."""
    h, l, c, o = (df[k].values.astype(float) for k in ("high", "low", "close", "open"))
    n = len(c); cut = int(n * FIT_SHARE); F = fit(h[:cut], l[:cut], c[:cut])
    if not F:
        return []
    atr, tol = F["atr"], 0.25 * F["atr"]
    lv = sorted(set(grid(F["P"], F["s"], 1, cycles_needed(F["P"], F["s"], 1, l.min(), h.max())) + grid(F["P"], F["s"], -1, cycles_needed(F["P"], F["s"], -1, l.min(), h.max()))))
    lv = np.array([p for p in lv if p > 0])
    wins = [F["i0"] + k * F["tsp"] for k in range(1, 10_000) if F["i0"] + k * F["tsp"] < n + 3 * F["tsp"]]
    out = []
    for wi, tk in enumerate(wins):
        if tk < cut:
            continue
        for i in range(max(cut, tk - ZW), min(n, tk + ZW + 1)):
            near = lv[(lv >= l[i] - tol) & (lv <= h[i] + tol)]; done = False
            for L in near:
                d = 1 if (c[i] > L + .1 * atr and c[i] > o[i] and l[i] <= L + tol) else -1 if (c[i] < L - .1 * atr and c[i] < o[i] and h[i] >= L - tol) else 0
                if not d:
                    continue
                en = c[i]; sl = (min(l[i], L) - tol) if d > 0 else (max(h[i], L) + tol); rk = abs(en - sl)
                if rk <= 0:
                    continue
                cand = lv[lv > en + rk] if d > 0 else lv[lv < en - rk][::-1]; tp = cand[0] if len(cand) else en + d * 1.5 * rk
                t_stop = wins[wi + 2] + ZW if wi + 2 < len(wins) else i + 2 * F["tsp"]
                rr = abs(tp - en) / rk

                def sim(dd):
                    s_ = en - dd * rk; t_ = en + dd * rr * rk
                    for j in range(i + 1, n):
                        if j > t_stop:
                            return (c[j - 1] - en) * dd / rk
                        if (l[j] <= s_) if dd > 0 else (h[j] >= s_):
                            return -1.0
                        if (h[j] >= t_) if dd > 0 else (l[j] <= t_):
                            return rr
                    return None
                r1 = sim(d); r0 = sim(1 if rng.random() < .5 else -1)
                if r1 is not None and r0 is not None:
                    out.append((float(r1), float(r0)))
                done = True; break
            if done:
                break
    return out
