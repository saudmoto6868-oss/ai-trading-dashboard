"""Spot analyzer indicators (owner 2026-11-06): one frame in -> every reading the spot dashboard draws and scores.
Formulas are written out in docs/SPOT_ANALYZER.md. Pure pandas / numpy, no network.

Per timeframe (1M / 1W / 1D / 4H):
  MAs        EMA 20 / 50 / 200 (EMA_t = a x close_t + (1 - a) x EMA_t-1, a = 2 / (n + 1)), stack order
  RSI 14     Wilder: RS = avg gain / avg loss (smoothing 1/14), RSI = 100 - 100 / (1 + RS)
  MACD       EMA12 - EMA26, signal EMA9 of MACD, histogram = MACD - signal
  ADX 14     Wilder +DI / -DI / DX -> ADX (trend strength, > 25 trending, < 20 range)
  Bollinger  SMA20 +- 2 sd -> %B and width
  Divergence regular (price LL + RSI HL = bull; price HH + RSI LH = bear) and hidden, on the last two confirmed fractal swings
  SMC        fractal swings -> BOS (break in the trend direction) / CHoCH (first break against it), order blocks
             (last opposite candle before the displacement that broke), fair value gaps (3-candle gap, unfilled), equal
             highs / lows (liquidity pools within 0.1 ATR), dealing range -> premium / discount / equilibrium, OTE 0.62-0.79
  Elliott    volatility zig-zag -> last 5-leg impulse candidate (rules: w2 not beyond w1 start, w4 not into w1, w3 not the
             shortest) else last ABC; Fibonacci targets of the next leg
  Gann       Square of 9 from the last major pivot: (sqrt(P) +- 0.25 k)^2 = 45-degree steps; fitted Gann grid + time cycle (gann_lab)
Spot extras: 200-week SMA distance, Mayer multiple (close / SMA 200-day), drawdown from the all-time high, 1Y return."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd


# ---------------------------------------------------------------- basics
def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def wilder(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    out[n - 1] = np.nanmean(x[:n])
    for i in range(n, len(x)):
        out[i] = out[i - 1] + (x[i] - out[i - 1]) / n
    return out


def rsi(c: pd.Series, n: int = 14) -> np.ndarray:
    d = np.diff(c.to_numpy(float), prepend=np.nan)
    g, l_ = np.where(d > 0, d, 0.0), np.where(d < 0, -d, 0.0)
    g[0] = l_[0] = 0.0
    ag, al = wilder(g, n), wilder(l_, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = ag / al
        r = 100 - 100 / (1 + rs)
    r[(al == 0) & (ag > 0)] = 100.0
    return r


def macd(c: pd.Series):
    m = ema(c, 12) - ema(c, 26)
    sg = ema(m, 9)
    return m.to_numpy(), sg.to_numpy(), (m - sg).to_numpy()


def atr(df: pd.DataFrame, n: int = 14) -> np.ndarray:
    h, l_, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l_, np.maximum(abs(h - pc), abs(l_ - pc)))
    return wilder(tr, n)


def adx(df: pd.DataFrame, n: int = 14):
    h, l_, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    up, dn = np.diff(h, prepend=h[0]), -np.diff(l_, prepend=l_[0])
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l_, np.maximum(abs(h - pc), abs(l_ - pc)))
    a, p, m = wilder(tr, n), wilder(pdm, n), wilder(mdm, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        pdi, mdi = 100 * p / a, 100 * m / a
        dx = 100 * abs(pdi - mdi) / (pdi + mdi)
    dx = np.nan_to_num(dx)
    ad = np.full(len(dx), np.nan)
    if len(dx) >= 2 * n:
        ad[2 * n - 1] = dx[n:2 * n].mean()
        for i in range(2 * n, len(dx)):
            ad[i] = ad[i - 1] + (dx[i] - ad[i - 1]) / n
    return ad, pdi, mdi


def bollinger(c: pd.Series, n: int = 20, k: float = 2.0):
    m, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up, lo = m + k * sd, m - k * sd
    return ((c - lo) / (up - lo)).to_numpy(), ((up - lo) / m).to_numpy()


def fractals(h: np.ndarray, l_: np.ndarray, k: int = 2):
    """Confirmed swing highs / lows: the bar is the extreme of k bars each side. -> [(i, price, 'H'|'L')] by index."""
    out = []
    for i in range(k, len(h) - k):
        if h[i] == h[i - k:i + k + 1].max() and h[i] > h[i - k:i].max():
            out.append((i, float(h[i]), "H"))
        if l_[i] == l_[i - k:i + k + 1].min() and l_[i] < l_[i - k:i].min():
            out.append((i, float(l_[i]), "L"))
    return out


# ---------------------------------------------------------------- divergence
def divergences(c_hi: np.ndarray, c_lo: np.ndarray, osc: np.ndarray, piv, look: int = 60):
    """Regular + hidden RSI divergences between the last two swing lows (bull) and highs (bear) inside `look` bars.
    -> [{'kind', 'side', 'i1', 'i2', 'p1', 'p2', 'o1', 'o2'}]"""
    n = len(osc)
    out = []
    for kind_side, typ, price in (("bull", "L", c_lo), ("bear", "H", c_hi)):
        pts = [(i, p) for i, p, t in piv if t == typ and i >= n - look and np.isfinite(osc[i])][-2:]
        if len(pts) < 2:
            continue
        (i1, p1), (i2, p2) = pts
        o1, o2 = float(osc[i1]), float(osc[i2])
        if kind_side == "bull":
            kind = "regular" if p2 < p1 and o2 > o1 else "hidden" if p2 > p1 and o2 < o1 else None
        else:
            kind = "regular" if p2 > p1 and o2 < o1 else "hidden" if p2 < p1 and o2 > o1 else None
        if kind:
            out.append({"kind": kind, "side": kind_side, "i1": i1, "i2": i2, "p1": p1, "p2": p2, "o1": o1, "o2": o2})
    return out


# ---------------------------------------------------------------- SMC / ICT
def structure(df: pd.DataFrame, piv):
    """Walk the closes: a close above the last swing high = break up, below the last swing low = break down.
    First break against the current trend = CHoCH, breaks with it = BOS. -> (events, trend 'up'|'down'|None)"""
    c = df["close"].to_numpy(float)
    by = {}
    for i, p, t in piv:
        by.setdefault(i + 2, []).append((p, t, i))   # a k=2 fractal is known 2 bars later
    last_h = last_l = None
    trend, ev = None, []
    for j in range(len(c)):
        for p, t, i in by.get(j, []):
            if t == "H":
                last_h = (i, p)
            else:
                last_l = (i, p)
        if last_h and c[j] > last_h[1]:
            ev.append({"i": j, "from": last_h[0], "level": last_h[1], "dir": "up", "kind": "BOS" if trend == "up" else "CHoCH"})
            trend, last_h = "up", None
        elif last_l and c[j] < last_l[1]:
            ev.append({"i": j, "from": last_l[0], "level": last_l[1], "dir": "down", "kind": "BOS" if trend == "down" else "CHoCH"})
            trend, last_l = "down", None
    return ev, trend


def order_blocks(df: pd.DataFrame, events, keep: int = 3):
    """For each break: the last opposite-colour candle before the impulse that broke. Kept while price has not closed through it."""
    o, h, l_, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    out = []
    for e in events:
        rng = range(e["i"] - 1, max(e["from"], e["i"] - 15) - 1, -1)
        for k in rng:
            if (e["dir"] == "up" and c[k] < o[k]) or (e["dir"] == "down" and c[k] > o[k]):
                lo, hi = l_[k], h[k]
                after = c[e["i"]:]
                broken = (after < lo).any() if e["dir"] == "up" else (after > hi).any()
                if not broken:
                    out.append({"i": k, "lo": float(lo), "hi": float(hi), "side": "bull" if e["dir"] == "up" else "bear"})
                break
    return out[-keep:]


def fvgs(df: pd.DataFrame, keep: int = 4, min_atr: float = 0.25):
    """3-candle gaps: bull when low[i] > high[i-2], bear when high[i] < low[i-2]; dropped once a later candle fills it."""
    h, l_ = df["high"].to_numpy(float), df["low"].to_numpy(float)
    a = atr(df)
    out = []
    for i in range(2, len(h)):
        aa = a[i] if np.isfinite(a[i]) else 0
        if l_[i] > h[i - 2] and l_[i] - h[i - 2] >= min_atr * aa:
            lo, hi = h[i - 2], l_[i]
            if not (l_[i + 1:] <= lo).any():
                out.append({"i": i - 1, "lo": float(lo), "hi": float(hi), "side": "bull", "filled_pct": _fill(l_[i + 1:], lo, hi, True)})
        elif h[i] < l_[i - 2] and l_[i - 2] - h[i] >= min_atr * aa:
            lo, hi = h[i], l_[i - 2]
            if not (h[i + 1:] >= hi).any():
                out.append({"i": i - 1, "lo": float(lo), "hi": float(hi), "side": "bear", "filled_pct": _fill(h[i + 1:], lo, hi, False)})
    return out[-keep:]


def _fill(later, lo, hi, bull):
    if not len(later):
        return 0.0
    x = later.min() if bull else later.max()
    f = (hi - x) / (hi - lo) if bull else (x - lo) / (hi - lo)
    return float(min(1, max(0, f)))


def liquidity(piv, atr_last: float, look_from: int = 0):
    """Equal highs / lows: two or more swings within 0.1 ATR -> resting liquidity (stops) above / below."""
    out = []
    tol = 0.1 * atr_last if atr_last else 0
    for typ in ("H", "L"):
        pts = [(i, p) for i, p, t in piv if t == typ and i >= look_from]
        for a in range(len(pts)):
            for b in range(a + 1, len(pts)):
                if tol and abs(pts[a][1] - pts[b][1]) <= tol:
                    out.append({"i1": pts[a][0], "i2": pts[b][0], "level": (pts[a][1] + pts[b][1]) / 2, "side": "sell-side" if typ == "L" else "buy-side"})
    return out[-4:]


def dealing_range(piv, px: float):
    """Last swing high + low -> equilibrium (50 %), premium above / discount below, OTE 0.62-0.79 retracement of the last leg."""
    hs = [p for p in piv if p[2] == "H"]
    ls = [p for p in piv if p[2] == "L"]
    if not hs or not ls:
        return None
    H, L = hs[-1], ls[-1]
    hi, lo = H[1], L[1]
    if hi <= lo:
        return None
    eq = (hi + lo) / 2
    up_leg = L[0] < H[0]          # last leg went up -> OTE for longs is a retracement down from the high
    ote = (hi - 0.79 * (hi - lo), hi - 0.62 * (hi - lo)) if up_leg else (lo + 0.62 * (hi - lo), lo + 0.79 * (hi - lo))
    pos = (px - lo) / (hi - lo)
    return {"hi": hi, "lo": lo, "eq": eq, "ote": ote, "pos": pos, "zone": "premium" if pos > 0.5 else "discount", "up_leg": up_leg,
            "i_hi": H[0], "i_lo": L[0]}


# ---------------------------------------------------------------- Elliott / Fibonacci
def elliott(df: pd.DataFrame):
    """Last 5-leg impulse candidate (labels 0-5) when the rules hold, else the last ABC; Fibonacci targets for the next leg."""
    from modules.elliott_lab import impulse_rules
    from modules.harmonic import vol_dev, zigzag
    zz = zigzag(df["high"].to_numpy(float), df["low"].to_numpy(float), vol_dev(df, 3.0, 0.004, 0.08))
    if len(zz) < 4:
        return {"kind": None, "pivots": zz}
    for start in range(len(zz) - 6, -1, -1):
        seg = zz[start:start + 6]
        if len(seg) < 6:
            continue
        kinds = "".join(k for _, _, k in seg)
        if kinds in ("LHLHLH", "HLHLHL"):
            bull = kinds[0] == "L"
            r = impulse_rules([p for _, p, _ in seg[:5]], bull)
            s = 1 if bull else -1
            w1, w3, w5 = s * (seg[1][1] - seg[0][1]), s * (seg[3][1] - seg[2][1]), s * (seg[5][1] - seg[4][1])
            if r == 3 and w5 > 0 and not (w3 < w1 and w3 < w5) and start >= len(zz) - 9:
                lab = [(i, p, str(n)) for n, (i, p, _) in enumerate(seg)]
                tail = zz[start + 6:]
                lab += [(i, p, x) for (i, p, _), x in zip(tail, "ABC")]
                return {"kind": "impulse_up" if bull else "impulse_down", "labels": lab, "pivots": zz, "rules": r,
                        "targets": _fib_targets(seg[0][1], seg[5][1], bull, done=True)}
    a, b, c = zz[-3:]
    bull_abc = a[2] == "H"            # H L H ... a correction down that may be ending
    return {"kind": "abc", "labels": [(a[0], a[1], "A"), (b[0], b[1], "B"), (c[0], c[1], "C")][-3:], "pivots": zz,
            "targets": _fib_targets(b[1], c[1], c[1] > b[1], done=False)}


def _fib_targets(p0, p1, up, done):
    """Retracements of the leg p0 -> p1 (where a pullback may stop) + 1.272 / 1.618 extensions."""
    d = p1 - p0
    return {"0.382": p1 - 0.382 * d, "0.5": p1 - 0.5 * d, "0.618": p1 - 0.618 * d, "1.272": p0 + 1.272 * d, "1.618": p0 + 1.618 * d}


# ---------------------------------------------------------------- Gann
def sq9(pivot: float, steps: int = 4) -> list[float]:
    """Square of 9 levels from a pivot: (sqrt(P) +- 0.25 k)^2, k = 1..steps (each 0.25 in the root = 45 degrees)."""
    r = math.sqrt(pivot)
    lv = [(r + 0.25 * k) ** 2 for k in range(1, steps + 1)] + [(r - 0.25 * k) ** 2 for k in range(1, steps + 1) if r - 0.25 * k > 0]
    return sorted(lv)


def gann(df: pd.DataFrame, piv):
    out = {"sq9": [], "pivot": None, "fit": None}
    if piv:
        big = max(piv[-12:], key=lambda p: p[1]) if df["close"].iloc[-1] < np.mean([p[1] for p in piv[-12:]]) else min(piv[-12:], key=lambda p: p[1])
        out["pivot"] = big
        out["sq9"] = sq9(big[1], 6)
    try:
        from modules.spot_plan import _gann
        out["fit"] = _gann(df)
    except Exception:
        pass
    return out


# ---------------------------------------------------------------- one frame
def analyse(df: pd.DataFrame) -> dict:
    """Every reading for one frame + its vote per family (+1 bull / -1 bear / 0)."""
    if df is None or len(df) < 30:
        return {"ok": False}
    d = df.reset_index(drop=True)
    c = d["close"]
    px = float(c.iloc[-1])
    e20, e50, e200 = ema(c, 20).to_numpy(), ema(c, 50).to_numpy(), ema(c, 200).to_numpy()
    r = rsi(c)
    m, sg, hist = macd(c)
    ad, pdi, mdi = adx(d)
    pb, bw = bollinger(c)
    a = atr(d)
    h, l_ = d["high"].to_numpy(float), d["low"].to_numpy(float)
    piv = fractals(h, l_, 2)
    dv = divergences(h, l_, r, piv)
    ev, trend = structure(d, piv)
    obs = order_blocks(d, ev)
    gaps = fvgs(d)
    a_last = float(a[-1]) if np.isfinite(a[-1]) else 0.0
    liq = liquidity(piv, a_last, len(d) - 120)
    dr = dealing_range(piv, px)
    ew = elliott(d)
    gn = gann(d, piv)
    long_ok = len(d) >= 200
    votes = {}
    votes["ma"] = (1 if px > e50[-1] > e200[-1] else -1 if px < e50[-1] < e200[-1] else 0) if long_ok else (1 if px > e50[-1] else -1)
    votes["rsi"] = 1 if r[-1] > 55 else -1 if r[-1] < 45 else 0
    rd = [x for x in dv if x["i2"] >= len(d) - 15]
    if rd:
        votes["rsi"] = 1 if rd[-1]["side"] == "bull" else -1
    votes["macd"] = 1 if hist[-1] > 0 and hist[-1] >= hist[-2] else -1 if hist[-1] < 0 and hist[-1] <= hist[-2] else 0
    votes["smc"] = 1 if trend == "up" else -1 if trend == "down" else 0
    votes["ict"] = 0 if not dr else (1 if dr["zone"] == "discount" and trend != "down" else -1 if dr["zone"] == "premium" and trend != "up" else 0)
    votes["elliott"] = {"impulse_up": 1, "impulse_down": -1}.get(ew.get("kind"), 0)
    if ew.get("kind") in ("impulse_up", "impulse_down") and len(ew["labels"]) > 6:   # impulse done, ABC running: against it
        votes["elliott"] = -votes["elliott"]
    strength = float(ad[-1]) if np.isfinite(ad[-1]) else None
    return {"ok": True, "n": len(d), "px": px, "time": d["time"], "o": d["open"].to_numpy(float), "h": h, "l": l_, "c": c.to_numpy(float),
            "e20": e20, "e50": e50, "e200": e200 if long_ok else None, "rsi": r, "macd": m, "signal": sg, "hist": hist,
            "adx": strength, "pdi": float(pdi[-1]) if np.isfinite(pdi[-1]) else None, "mdi": float(mdi[-1]) if np.isfinite(mdi[-1]) else None,
            "pctb": float(pb[-1]) if np.isfinite(pb[-1]) else None, "bbw": float(bw[-1]) if np.isfinite(bw[-1]) else None,
            "atr": a_last, "piv": piv, "div": dv, "events": ev[-6:], "trend": trend, "obs": obs, "fvg": gaps, "liq": liq, "dr": dr,
            "elliott": ew, "gann": gn, "votes": votes}


TF_W = {"1mo": 3.0, "1w": 2.5, "1d": 1.5, "4h": 1.0}


def confluence(reads: dict, smt: dict | None = None) -> dict:
    """Weighted score -100..100 per timeframe and overall; ADX < 20 halves a frame's trend votes (range = weaker signal)."""
    per, num, den = {}, 0.0, 0.0
    for tf, r in reads.items():
        if not r.get("ok"):
            continue
        v = dict(r["votes"])
        if smt and smt.get(tf):
            v["smt"] = smt[tf]
        k = 0.5 if (r.get("adx") is not None and r["adx"] < 20) else 1.0
        s = sum(x * (k if f in ("ma", "smc", "macd") else 1.0) for f, x in v.items())
        per[tf] = round(100 * s / max(1, len(v)))
        num += TF_W.get(tf, 1) * s
        den += TF_W.get(tf, 1) * len(v)
    return {"per_tf": per, "score": round(100 * num / den) if den else 0}


def spot_stats(daily: pd.DataFrame | None, weekly: pd.DataFrame | None, monthly: pd.DataFrame | None) -> dict:
    """Spot-only context: 200-week SMA, Mayer multiple, drawdown from ATH, 52-week range, 1Y return, 30-day realized vol."""
    out = {}
    if weekly is not None and len(weekly) >= 30:
        c = weekly["close"]
        n = min(200, len(c))
        out["sma200w"] = float(c.tail(n).mean())
        out["sma200w_n"] = n
        out["dist_200w"] = float(c.iloc[-1] / out["sma200w"] - 1) * 100
        last52 = weekly.tail(52)
        out["hi52"], out["lo52"] = float(last52["high"].max()), float(last52["low"].min())
        if len(c) > 52:
            out["ret1y"] = float(c.iloc[-1] / c.iloc[-53] - 1) * 100
    if daily is not None and len(daily) >= 200:
        c = daily["close"]
        out["mayer"] = float(c.iloc[-1] / c.tail(200).mean())
        lr = np.log(c).diff().tail(30)
        out["vol30"] = float(lr.std() * math.sqrt(365) * 100)
    src = monthly if monthly is not None and len(monthly) else weekly
    if src is not None and len(src):
        ath = float(src["high"].max())
        px = float((daily if daily is not None and len(daily) else src)["close"].iloc[-1])
        out["ath"], out["dd_ath"] = ath, (px / ath - 1) * 100
    return out
