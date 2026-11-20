"""Backtest of the Order Flow Desk's five setups (docs/MEETING_ROOM.md 2026-11-08) on footprint bars built from real trades.

Data: every trade (time, price, size, which side was the aggressor), e.g. Binance aggTrades from data.binance.vision
(scripts/of_setups_bt.py downloads them; free, no key). The build sandbox cannot reach it: the engine here is tested on
synthetic trades only. NO RESULTS EXIST YET - run the script, and under 30 trades per setup nothing is evidence.

Bars are built from trades (OHLC, volume, delta = aggressive buys - aggressive sells, footprint = bid / ask volume per price row).
Every rule is decided at the CLOSE of a bar with only that bar and older bars; entry = the NEXT bar's open; stop first when a bar
touches both stop and target; costs are taken off every trade in R.

Setups (directions: +1 long, -1 short):
 1 absorption   bar touches a level (previous day high / low / POC / VAH / VAL), |delta| >= 2x the median |delta| of the last 50 bars,
                range <= 0.6 ATR (big aggression, small move) -> trade AGAINST the aggressor (big selling absorbed at a low = long)
 2 cvd_div      bar makes a new 20-bar high but cumulative delta is below its value at the previous 20-bar high -> short (mirror long)
 3 delta_push   EMA50 rising, bar dips into the previous day's value area with weak selling (delta < 0, |delta| < median) and
                closes up -> long (mirror short)
 4 stacked      >= 3 consecutive price rows in the bar where ask volume >= 3x bid volume (diagonal-free, same row) -> long (mirror)
 5 dom_reject   needs order-book history: NOT testable from trades (reported as such)
Order flow alone is not a signal (the minutes' own rule): setups 2-4 also need price within 0.5 ATR of a level unless level=False.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SETUPS = ("absorption", "cvd_div", "delta_push", "stacked")
NOT_TESTABLE = {"dom_reject": "needs order-book history (resting orders over time); trades alone cannot show it"}


def bars(trades: pd.DataFrame, sec: int = 300, tick: float | None = None) -> pd.DataFrame:
    """trades: columns t (ms), p, q, buyer_maker (True = the SELLER was the aggressor). -> bars with o h l c v delta fp.
    fp = {price row: [bid volume (sells hitting the bid), ask volume (buys lifting the ask)]}; tick = row size (auto ~ price/2000)."""
    tr = trades.sort_values("t")
    if tick is None:
        tick = float(10 ** np.floor(np.log10(max(tr.p.median() / 2000, 1e-8))))
    b = (tr.t // (sec * 1000)) * sec * 1000
    out = []
    for t0, g in tr.groupby(b.values, sort=True):
        s = np.where(g.buyer_maker.values, -1.0, 1.0)   # +1 = aggressive buy, -1 = aggressive sell
        rows = np.round(g.p.values / tick) * tick
        fp = {}
        for r, q, x in zip(rows, g.q.values, s):
            a = fp.setdefault(round(float(r), 10), [0.0, 0.0])
            a[1 if x > 0 else 0] += float(q)
        out.append({"t": int(t0), "o": g.p.iloc[0], "h": g.p.max(), "l": g.p.min(), "c": g.p.iloc[-1], "v": g.q.sum(), "delta": float((g.q.values * s).sum()), "fp": fp})
    df = pd.DataFrame(out)
    df.attrs["tick"] = tick
    return df


def _atr(df, n=14):
    pc = df.c.shift(1)
    tr = pd.concat([df.h - df.l, (df.h - pc).abs(), (df.l - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n, min_periods=3).mean()


def _prev_day_levels(df):
    """Per bar: previous UTC day's high, low and volume-profile POC / VAH / VAL (known from the start of the day: no look-ahead)."""
    day = df.t // 86_400_000
    lv = {}
    for d, g in df.groupby(day):
        prof = {}
        for fp in g.fp:
            for p, (bv, av) in fp.items():
                prof[p] = prof.get(p, 0.0) + bv + av
        if not prof:
            continue
        ps = sorted(prof); vs = np.array([prof[p] for p in ps]); i = int(vs.argmax()); a = b = i; acc = vs[i]
        while acc < 0.7 * vs.sum() and (a > 0 or b < len(vs) - 1):
            if b < len(vs) - 1 and (a == 0 or vs[b + 1] >= vs[a - 1]):
                b += 1; acc += vs[b]
            else:
                a -= 1; acc += vs[a]
        lv[d + 1] = {"pdh": g.h.max(), "pdl": g.l.min(), "poc": ps[i], "vah": ps[b], "val": ps[a]}
    cols = ["pdh", "pdl", "poc", "vah", "val"]
    return pd.DataFrame([lv.get(d, {k: np.nan for k in cols}) for d in day], index=df.index)[cols]


def signals(df: pd.DataFrame, level: bool = True) -> pd.DataFrame:
    """-> one row per signal: i (bar index, decided at its close), setup, dir. Only bars <= i are read."""
    atr = _atr(df); L = _prev_day_levels(df); med = df.delta.abs().rolling(50, min_periods=10).median().shift(1)
    cvd = df.delta.cumsum(); ema = df.c.ewm(span=50, adjust=False).mean()
    out = []
    for i in range(30, len(df)):
        r, a = df.iloc[i], atr.iloc[i]
        if not (a > 0):
            continue
        lvls = [x for x in L.iloc[i].values if np.isfinite(x)]
        near = lambda price: any(abs(price - x) <= 0.5 * a for x in lvls)
        touch = [x for x in lvls if r.l - 0.1 * a <= x <= r.h + 0.1 * a]
        m = med.iloc[i]
        # 1 absorption: big aggression, small move, at a level -> against the aggressor
        if touch and np.isfinite(m) and m > 0 and abs(r.delta) >= 2 * m and (r.h - r.l) <= 0.6 * a:
            out.append((i, "absorption", -1 if r.delta > 0 else 1))
        # 2 cumulative-delta divergence at a fresh 20-bar extreme
        w = df.iloc[i - 20:i]
        if r.h > w.h.max():
            j = w.h.idxmax()
            if cvd.iloc[i] < cvd.loc[j] and (not level or near(r.h)):
                out.append((i, "cvd_div", -1))
        if r.l < w.l.min():
            j = w.l.idxmin()
            if cvd.iloc[i] > cvd.loc[j] and (not level or near(r.l)):
                out.append((i, "cvd_div", 1))
        # 3 delta push: pullback into yesterday's value area with weak counter-delta, closing back with the trend
        va = L.iloc[i]
        if np.isfinite(va.vah) and np.isfinite(m) and m > 0:
            up, dn = ema.iloc[i] > ema.iloc[i - 5], ema.iloc[i] < ema.iloc[i - 5]
            inva = r.l <= va.vah and r.h >= va.val
            if up and inva and r.delta < 0 and abs(r.delta) < m and r.c > r.o:
                out.append((i, "delta_push", 1))
            if dn and inva and r.delta > 0 and abs(r.delta) < m and r.c < r.o:
                out.append((i, "delta_push", -1))
        # 4 stacked imbalance: 3+ consecutive rows dominated 3:1 by one side
        if r.fp:
            ps = sorted(r.fp); run_b = run_s = best_b = best_s = 0
            for p in ps:
                bv, av = r.fp[p]
                run_b = run_b + 1 if av >= 3 * max(bv, 1e-12) and av > 0 else 0
                run_s = run_s + 1 if bv >= 3 * max(av, 1e-12) and bv > 0 else 0
                best_b, best_s = max(best_b, run_b), max(best_s, run_s)
            if best_b >= 3 and best_s < 3 and (not level or near(r.c)):
                out.append((i, "stacked", 1))
            if best_s >= 3 and best_b < 3 and (not level or near(r.c)):
                out.append((i, "stacked", -1))
    return pd.DataFrame(out, columns=["i", "setup", "dir"])


def simulate(df: pd.DataFrame, sig: pd.DataFrame, stop_atr: float = 1.0, rr: float = 2.0, hold: int = 24, cost_r: float = 0.1) -> pd.DataFrame:
    """Entry at the next bar's open, stop = stop_atr x ATR (at the signal bar), target = rr x risk; stop first on a two-sided bar;
    exit at the close after `hold` bars. One trade at a time per setup. -> trades with R net of cost_r."""
    atr = _atr(df); rows = []; busy = {}
    for s in sig.itertuples():
        e_i = s.i + 1
        if e_i >= len(df) or busy.get(s.setup, -1) >= e_i:
            continue
        a = atr.iloc[s.i]; entry = df.o.iloc[e_i]; risk = stop_atr * a
        if not (risk > 0):
            continue
        stop, tgt, d = entry - s.dir * risk, entry + s.dir * rr * risk, s.dir
        R, x = None, None
        for k in range(e_i, min(len(df), e_i + hold)):
            h, l = df.h.iloc[k], df.l.iloc[k]
            hit_s = l <= stop if d > 0 else h >= stop
            hit_t = h >= tgt if d > 0 else l <= tgt
            if hit_s:
                R, x = -1.0, k; break
            if hit_t:
                R, x = rr, k; break
        if R is None:
            x = min(len(df), e_i + hold) - 1
            R = d * (df.c.iloc[x] - entry) / risk
        busy[s.setup] = x
        rows.append({"setup": s.setup, "dir": d, "i": s.i, "t": int(df.t.iloc[e_i]), "entry": entry, "R": R - cost_r})
    return pd.DataFrame(rows, columns=["setup", "dir", "i", "t", "entry", "R"])


def report(tr: pd.DataFrame) -> pd.DataFrame:
    """Per setup: n, win %, average R net, total R, and the verdict (under 30 trades = not evidence)."""
    out = []
    for s in SETUPS:
        g = tr[tr.setup == s]
        n = len(g)
        out.append({"setup": s, "n": n, "win%": round(100 * (g.R > 0).mean(), 1) if n else None, "avgR": round(g.R.mean(), 3) if n else None,
                    "totalR": round(g.R.sum(), 2) if n else 0.0, "verdict": "not evidence (n < 30)" if n < 30 else ("positive net of costs" if g.R.mean() > 0 else "loses net of costs")})
    for s, why in NOT_TESTABLE.items():
        out.append({"setup": s, "n": 0, "win%": None, "avgR": None, "totalR": 0.0, "verdict": "not testable: " + why})
    return pd.DataFrame(out)
