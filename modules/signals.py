"""
THE SIGNAL LAB
Own-built detectors for the scanner (nothing copied from any paid indicator;
they implement the *concepts* named in the "AI Trading Desk - Framework &
Checklist" doc). Every detector is written for the BULLISH case only; the
bearish case is produced by running the same code on a price-inverted copy
of the candles (high<->low, all prices negated) and flipping the results
back. That keeps the two sides exactly symmetric.

Signal families (see scorer.py for how they become stars):
  primary      : Elliott, Unicorn, MSB-OB, Fib, Liquidity
  confirmation : MA, VWAP   (doc: indicators are confirmation only)

All pivot-based logic uses fractal swings confirmed n bars later, so every
signal is something that was knowable on the last closed candle (no peeking).
Elliott counting in particular is a rule-based heuristic - treat it as a
prompt to look at the chart, not as truth.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

BULL, BEAR = "bullish", "bearish"

FAMILY_ICONS = {
    "MA": "\U0001F4C8",         # chart increasing
    "VWAP": "⚓",           # anchor
    "Elliott": "\U0001F30A",    # wave
    "Unicorn": "\U0001F984",    # unicorn
    "MSB-OB": "\U0001F9F1",     # brick
    "Fib": "\U0001F4D0",        # triangular ruler
    "Liquidity": "\U0001F4A7",  # droplet
}
PRIMARY_FAMILIES = ("Elliott", "Unicorn", "MSB-OB", "Fib", "Liquidity")
CONFIRM_FAMILIES = ("MA", "VWAP")
ALL_FAMILIES = PRIMARY_FAMILIES + CONFIRM_FAMILIES  # 7 families -> max 7 stars


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def fp(x: float) -> str:
    """Compact price formatting that works for 0.0004 coins and 90,000 coins."""
    ax = abs(x)
    if ax >= 1000:
        return f"{x:,.1f}"
    if ax >= 1:
        return f"{x:.3f}"
    return f"{x:.5f}"


def atr_series(df: pd.DataFrame, n: int = 14) -> pd.Series:
    pc = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n, min_periods=1).mean()


def invert(df: pd.DataFrame) -> pd.DataFrame:
    inv = df.copy()
    inv["open"], inv["close"] = -df["open"], -df["close"]
    inv["high"], inv["low"] = -df["low"], -df["high"]
    return inv


def fractal_pivots(df: pd.DataFrame, n: int = 3):
    """[(bar_index, price, 'H'|'L')], confirmed n bars after the pivot bar."""
    h, l = df["high"].values, df["low"].values
    out = []
    for i in range(n, len(df) - n):
        wh, wl = h[i - n:i + n + 1], l[i - n:i + n + 1]
        if int(np.argmax(wh)) == n:
            out.append((i, float(h[i]), "H"))
        if int(np.argmin(wl)) == n:
            out.append((i, float(l[i]), "L"))
    out.sort(key=lambda x: x[0])
    return out


def zigzag(df: pd.DataFrame, n: int = 3, min_atr: float = 1.5):
    """Alternating H/L pivots with tiny swings (< min_atr x ATR) filtered out."""
    a = atr_series(df).values
    zz = []
    for i, p, k in fractal_pivots(df, n):
        if zz and zz[-1][2] == k:
            if (k == "H" and p > zz[-1][1]) or (k == "L" and p < zz[-1][1]):
                zz[-1] = (i, p, k)
            continue
        if zz and abs(p - zz[-1][1]) < min_atr * a[i]:
            continue
        zz.append((i, p, k))
    return zz


def sr_levels(df: pd.DataFrame, lookback: int = 100, tolerance: float = 0.0015):
    """(resistances, supports) = clustered swing highs / lows."""
    recent = df.tail(lookback).reset_index(drop=True)
    piv = fractal_pivots(recent, 2)

    def cluster(vals):
        out = []
        for v in sorted(vals):
            if out and abs(v - out[-1][-1]) <= tolerance * abs(v):
                out[-1].append(v)
            else:
                out.append([v])
        return [float(np.mean(c)) for c in out]

    return cluster([p for _, p, k in piv if k == "H"]), cluster([p for _, p, k in piv if k == "L"])


_SWAPS = [
    ("swing-low", "swing-high"), ("swing-high", "swing-low"), ("Sell-side", "Buy-side"), ("Buy-side", "Sell-side"),
    ("bullish", "bearish"), ("bearish", "bullish"), ("support", "resistance"), ("resistance", "support"),
    ("above", "below"), ("below", "above"), ("Above", "Below"), ("Below", "Above"),
    ("buyers", "sellers"), ("longs", "shorts"), ("up-leg", "down-leg"), ("closed up", "closed down"),
    ("low", "high"), ("high", "low"),
]
_SWAP_MAP = dict(_SWAPS)
_SWAP_RE = re.compile(r"(?<![\w{])(" + "|".join(sorted(map(re.escape, _SWAP_MAP), key=len, reverse=True)) + r")(?![\w}])")


def _flip_text(text: str) -> str:
    """Bearish twin of a bullish sentence (support<->resistance, above<->below ...)."""
    return _SWAP_RE.sub(lambda m: _SWAP_MAP[m.group(1)], text)


# stable ids so the Arabic text/tag layer does not depend on the English wording
_KEY_PATTERNS = [
    (r"bullish cross", "ma_cross"), (r"EMA stack", "ema_stack"), (r"VWAP", "vwap"),
    (r"Wave 3 start", "ew3"), (r"Wave 5 start", "ew5"), (r"ABC correction", "abc"), (r"Wave C", "wavec"),
    (r"Zombie", "zombie"), (r"Order block \(", "ob"), (r"OTE entry", "ote"), (r"Fair value gap", "fvg"), (r"Breaker block", "breaker"), (r"Judas", "judas"), (r"Fib retracement", "fib"), (r"Structure break", "msb_ob"), (r"liquidity sweep", "sweep"),
    (r"Unicorn", "unicorn"), (r"Liquidity line break", "liqline"), (r"OHL: open", "ohl_open"),
    (r"OHL: breaks", "ohl_break"), (r"At support", "level"), (r"-bar breakout", "breakout"),
]


def _mk(family, name, detail, prices=None, vals=None, zone=None, counter=False):
    """counter=True marks a signal whose direction is OPPOSITE to the frame it
    was detected in (e.g. the ABC correction after a bullish impulse)."""
    key = next((k for pat, k in _KEY_PATTERNS if re.search(pat, name)), "other")
    return {"family": family, "name": name, "key": key, "_t": detail, "_p": prices or {}, "_v": vals or {},
            "zone": zone, "counter": counter}


def _finalize(sig: dict, flipped: bool) -> dict:
    p = {k: (-v if flipped else v) for k, v in sig["_p"].items()}
    zone = sig["zone"]
    if zone is not None and flipped:
        zone = (-zone[1], -zone[0])
    if zone is not None:
        p["zl"], p["zh"] = zone  # zone bounds always ordered low -> high, for display
    name, tmpl = sig["name"], sig["_t"]
    if flipped and not sig["counter"]:
        name, tmpl = _flip_text(name), _flip_text(tmpl)
    return {
        "family": sig["family"], "name": name, "key": sig["key"], "vals": dict(sig["_v"]),
        "direction": BEAR if (flipped ^ sig["counter"]) else BULL,
        "icon": FAMILY_ICONS[sig["family"]],
        "detail": tmpl.format(**{k: fp(v) for k, v in p.items()}, **sig["_v"]),
        "prices": p, "zone": zone,
    }


# --------------------------------------------------------------------------
# Confirmation family: moving averages + VWAP
# --------------------------------------------------------------------------

def ma_bull(df):
    out, c = [], df["close"]
    n = len(df)
    ema = lambda s: c.ewm(span=s, adjust=False).mean()
    specs = [
        ("EMA 9/21", ema(9), ema(21), 5, 30),
        ("EMA 50/200", ema(50), ema(200), 10, 200),
        ("SMA 50/200", c.rolling(50).mean(), c.rolling(200).mean(), 10, 200),
    ]
    for name, fast, slow, window, min_bars in specs:
        if n < min_bars:
            continue
        d = (fast - slow).values
        if not d[-1] > 0:
            continue
        for j in range(n - 1, max(n - 1 - window, 0), -1):  # most recent cross first
            if d[j] > 0 >= d[j - 1]:
                ago = n - 1 - j
                out.append(_mk("MA", f"{name} bullish cross",
                               "fast MA crossed above slow MA {ago} bar(s) ago", vals={"ago": ago}))
                break
    e9, e21, e50 = ema(9), ema(21), ema(50)
    if n >= 60 and e9.iloc[-1] > e21.iloc[-1] > e50.iloc[-1] and c.iloc[-1] > e9.iloc[-1]:
        out.append(_mk("MA", "EMA stack aligned (9/21/50)", "price above a fully stacked fast-to-slow EMA trend"))
    return out


def vwap_bull(df, window: int = 100):
    if n_short(df, 30):
        return []
    tp = (df["high"] + df["low"] + df["close"]) / 3
    vol = df["volume"].replace(0, np.nan)
    num = (tp * vol).rolling(window, min_periods=20).sum()
    den = vol.rolling(window, min_periods=20).sum()
    vwap = (num / den).iloc[-1]
    price = df["close"].iloc[-1]
    if pd.notna(vwap) and price > vwap:
        return [_mk("VWAP", "Above VWAP", "price {p} above rolling VWAP {v} (fair-value anchor favors longs)",
                    prices={"p": price, "v": float(vwap)})]
    return []


def n_short(df, k):
    return len(df) < k


# --------------------------------------------------------------------------
# Primary family: Elliott waves
# --------------------------------------------------------------------------

def _wave2_reaction(df, i2, p2):
    """(name, level) of the EMA 9/21/50 or VWAP that the wave-2 low tapped or
    crossed and that price now holds above; None if wave 2 hit none of them."""
    if i2 < 20 or i2 >= len(df):
        return None
    c = df["close"]
    a = float(atr_series(df).iloc[i2])
    lo, hi = max(0, i2 - 2), min(len(df), i2 + 3)
    low = float(df["low"].iloc[lo:hi].min())
    high = float(df["high"].iloc[lo:hi].max())
    tp = (df["high"] + df["low"] + df["close"]) / 3
    vol = df["volume"].replace(0, np.nan)
    vw = (tp * vol).rolling(100, min_periods=20).sum() / vol.rolling(100, min_periods=20).sum()
    cands = [(f"EMA{n}", c.ewm(span=n, adjust=False).mean()) for n in (9, 21, 50)] + [("VWAP", vw)]
    for name, ser in cands:
        lv = ser.iloc[lo:hi].mean()
        if pd.isna(lv):
            continue
        lv = float(lv)
        touched = low <= lv + 0.4 * a and high >= lv - 0.4 * a   # wave-2 low tapped / crossed it
        holds = float(c.iloc[-1]) > float(ser.iloc[-1])           # price is back above it now
        if touched and holds:
            return (name, lv)
    return None


def elliott_bull(df):
    """Rule-based impulse (0-1-2-3-4-5) + ABC detector on zig-zag pivots.
    Fires only for the *start* of a wave, per the watchlist spec:
      Wave 3 start, Wave 5 start (bullish) ... and ABC start / Wave C start
    after a completed bullish impulse (those two are bearish signals and are
    produced by the bullish function being run on the original data)."""
    out = []
    zz = zigzag(df)
    if len(zz) < 3:
        return out
    kinds = [k for _, _, k in zz]
    px = [p for _, p, _ in zz]
    price = float(df["close"].iloc[-1])

    # ---- Wave 3 start: pivots L(0) H(1) L(2) --------------------------------
    # Needs (a) a strong first move, (b) a 50-70% retracement (small tolerance),
    # and (c) wave 2 reacting OFF an EMA 9/21/50 or VWAP level (tap/cross + hold).
    if kinds[-3:] == ["L", "H", "L"]:
        p0, p1, p2 = px[-3:]
        i0_, i1_, i2 = zz[-3][0], zz[-2][0], zz[-1][0]
        w1 = p1 - p0
        if w1 > 0 and p2 > p0:
            ret = (p1 - p2) / w1
            if 0.45 <= ret <= 0.72 and p2 + 0.25 * w1 <= price <= p1 + 0.618 * w1:
                lvl = _wave2_reaction(df, i2, p2)
                if lvl:
                    ideal = " (ideal 50-61.8% zone)" if 0.5 <= ret <= 0.618 else ""
                    out.append(_mk(
                        "Elliott", "Wave 3 start",
                        "wave 2 retraced {ret:.0%} of wave 1{ideal} and reacted off " + lvl[0] + " {ma}; target 1.618 x W1 = {t}; invalid below {inv}",
                        prices={"t": p2 + 1.618 * w1, "inv": p0, "ma": lvl[1], "w0": p0, "w1": p1, "w2": p2},
                        vals={"ret": ret, "ideal": ideal, "ma_name": lvl[0], "idx": [int(i0_), int(i1_), int(i2)]}))

    # ---- Wave 5 start: L H L H L ---------------------------------------------
    if len(zz) >= 5 and kinds[-5:] == ["L", "H", "L", "H", "L"]:
        p0, p1, p2, p3, p4 = px[-5:]
        w1, w3 = p1 - p0, p3 - p2
        if p2 > p0 and p3 > p1 and p4 > p1 and w3 > w1 > 0:
            ret4 = (p3 - p4) / w3
            if 0.236 <= ret4 <= 0.5 and p4 + 0.2 * w1 <= price <= p4 + w1:
                out.append(_mk(
                    "Elliott", "Wave 5 start",
                    "wave 4 retraced {ret:.0%} of wave 3 (typ. 38.2%); target W5 = W1: {t1}, or 1.618 x (W1 start to W3 end): {t2}",
                    prices={"t1": p4 + w1, "t2": p0 + 1.618 * (p3 - p0), "w0": p0, "w1": p1, "w2": p2, "w3": p3, "w4": p4},
                    vals={"ret": ret4, "idx": [int(zz[-5][0]), int(zz[-4][0]), int(zz[-3][0]), int(zz[-2][0]), int(zz[-1][0])]}))

    # ---- after a COMPLETE impulse (L H L H L H) -> correction ------------------
    def valid_impulse(q):
        p0, p1, p2, p3, p4, p5 = q
        w1, w3, w5 = p1 - p0, p3 - p2, p5 - p4
        return (p2 > p0 and p4 > p1 and p3 > p1 and p5 > p3 and w1 > 0 and w3 > 0 and w5 > 0
                and w3 >= min(w1, w5))

    # ABC start (wave A): impulse just ended at pivot-H and price is falling away from it
    if len(zz) >= 6 and kinds[-6:] == ["L", "H", "L", "H", "L", "H"] and valid_impulse(px[-6:]):
        p0, p5 = px[-6], px[-1]
        if price <= p5 - 0.236 * (p5 - p0):
            out.append(_mk(
                "Elliott", "ABC correction start (wave A)",
                "5-wave impulse completed at {top}; price gave back 23.6%+ of it; typical correction 38.2-61.8% = {a}-{b}",
                prices={"top": p5, "a": p5 - 0.382 * (p5 - p0), "b": p5 - 0.618 * (p5 - p0)}, counter=True))
    # Wave C start: ..., p5(H), A(L), B(H) with price rolling over again
    if len(zz) >= 8 and kinds[-8:] == ["L", "H", "L", "H", "L", "H", "L", "H"] and valid_impulse(px[-8:-2]):
        p5, a, b = px[-3], px[-2], px[-1]
        if a < b < p5 and price <= b - 0.2 * (b - a):
            out.append(_mk(
                "Elliott", "Wave C start",
                "after impulse + A-B, price turning away from B {b}; C = A length target {t1}, 1.618 x A: {t2}",
                prices={"b": b, "t1": b - (p5 - a), "t2": b - 1.618 * (p5 - a)}, counter=True))
    return out


# --------------------------------------------------------------------------
# Primary family: Fibonacci reference levels
# --------------------------------------------------------------------------

FIB_ZONES = [
    ("OTE 0.62-0.79", 0.62, 0.79),
    ("Fibo POP 0.559-0.669", 0.559, 0.669),
    ("Gold zone 0.688-0.822", 0.688, 0.822),
]


def fib_bull(df):
    zz = zigzag(df)
    if len(zz) < 2 or zz[-1][2] != "H" or zz[-2][2] != "L":
        return []
    (ia, a, _), (ib, b, _) = zz[-2], zz[-1]
    leg = b - a
    atr = float(atr_series(df).iloc[ib])
    price = float(df["close"].iloc[-1])
    if leg < 2 * atr or not (a < price < b) or len(df) - ib > 150:
        return []
    ret = (b - price) / leg
    in_zones = [name for name, lo, hi in FIB_ZONES if lo <= ret <= hi]
    shallow = ""
    if abs(ret - 0.382) <= 0.03:
        shallow = "38.2% pullback (strong-trend continuation)"
    elif abs(ret - 0.236) <= 0.02:
        shallow = "23.6% pullback (very strong trend)"
    if not in_zones and not shallow:
        return []
    label = ", ".join(in_zones) if in_zones else shallow
    prices = {
        "start": a, "x1": a + 1.272 * leg, "x2": a + 1.618 * leg, "x3": a + 2.0 * leg,
        "m1": a + 0.33 * leg, "m2": a + 0.66 * leg, "m3": a + 0.99 * leg,
    }
    return [_mk(
        "Fib", "Fib retracement zone",
        "price at {ret:.0%} retrace of the last up-leg: " + label.replace("{", "").replace("}", "")
        + "; extensions 1.272/1.618/2.0: {x1} / {x2} / {x3}; Monkey TPs (0.33/0.66/0.99): {m1} / {m2} / {m3}; leg start {start}",
        prices=prices, vals={"ret": ret, "label": label})]


# --------------------------------------------------------------------------
# Primary family: market structure (MSB-OB, sweeps, Unicorn)
# --------------------------------------------------------------------------

def structure_breaks(df, n: int = 3, lookback: int = 80):
    """Bullish breaks of structure: first close above a confirmed swing high.
    -> [{'j': break bar, 'level': swing high, 'pivot': pivot bar}]"""
    piv = fractal_pivots(df, n)
    highs = [(i, p) for i, p, k in piv if k == "H"]
    c = df["close"].values
    events = []
    for j in range(max(1, len(df) - lookback), len(df)):
        cands = [(i, p) for i, p in highs if i + n <= j]
        if not cands:
            continue
        i, p = cands[-1]
        if c[j] > p and (j == i + 1 or (c[i + 1:j] <= p).all()):
            events.append({"j": j, "level": p, "pivot": i})
    # keep only the first break per swing high
    seen, uniq = set(), []
    for e in events:
        if e["pivot"] not in seen:
            seen.add(e["pivot"])
            uniq.append(e)
    return uniq


def _last_down_candle(df, upto: int, span: int = 6):
    o, c = df["open"].values, df["close"].values
    for k in range(upto, max(upto - span, -1), -1):
        if c[k] < o[k]:
            return k
    return upto


def _order_block(df, brk):
    """Last down candle before the up-move that produced the break."""
    i, j = brk["pivot"], brk["j"]
    low = df["low"].values
    s = i + int(np.argmin(low[i:j + 1]))
    k = _last_down_candle(df, s)
    return k, (float(low[k]), float(df["high"].values[k]))


def msb_ob_bull(df, max_age: int = 40):
    out = []
    atr = atr_series(df).values
    c, low = df["close"].values, df["low"].values
    price = float(c[-1])
    for brk in reversed(structure_breaks(df)):
        j = brk["j"]
        if len(df) - 1 - j > max_age:
            continue
        s = brk["pivot"] + int(np.argmin(low[brk["pivot"]:j + 1]))
        if c[j] - low[s] < 1.5 * atr[j]:
            continue  # no real displacement
        k, (zlo, zhi) = _order_block(df, brk)
        if (c[j + 1:] < zlo).any():
            continue  # order block invalidated
        pad = 0.15 * atr[-1]
        if len(df) - 1 > j and zlo - pad <= price <= zhi + pad:
            out.append(_mk(
                "MSB-OB", "Structure break + order block retest",
                "closed above swing high {lvl}; price now retesting the order block {zl} - {zh} (invalid below {lo})",
                prices={"lvl": brk["level"], "lo": zlo, "hi": zhi}, zone=(zlo, zhi)))
            break
    return out


def order_block_bull(df, max_age: int = 80):
    """Order block (swing-structure style): after a bullish break of structure the
    bar with the LOWEST low inside the move (pivot -> break) is the order block.
    Freshness: 'fresh' = price has not traded back into the zone since it formed
    (unmitigated); 'tested' = already touched but not closed through. Fires while
    price is inside / right above the zone, the moment it is worth watching."""
    out = []
    atr = atr_series(df).values
    c, hi_, lo_ = df["close"].values, df["high"].values, df["low"].values
    price = float(c[-1])
    for brk in reversed(structure_breaks(df)):
        j = brk["j"]
        if len(df) - 1 - j > max_age or j >= len(df) - 1:
            continue
        i = brk["pivot"]
        k = i + int(np.argmin(lo_[i:j + 1]))
        zlo, zhi = float(lo_[k]), float(hi_[k])
        if zhi - zlo < 0.2 * atr[k]:
            continue
        after = slice(j + 1, len(df) - 1)               # bars between the break and now (excluding current)
        if (c[after] < zlo).any():
            continue                                    # invalidated (closed through the block)
        touched = bool((lo_[after] <= zhi).any())
        pad = 0.5 * atr[-1]
        if zlo - 0.15 * atr[-1] <= price <= zhi + pad:
            st = "tested" if touched else "fresh"
            out.append(_mk("MSB-OB", "Order block (" + st + ")",
                           "bullish order block {zl} - {zh} formed before the structure break at {lvl}; " + st
                           + " block (" + ("never revisited = unmitigated" if not touched else "already revisited once") + "); invalid on a close below {zl}",
                           prices={"lvl": brk["level"]}, vals={"fresh": not touched}, zone=(zlo, zhi)))
            break
    return out


def fvgs_bull(df, start: int = 2):
    h, l = df["high"].values, df["low"].values
    res = []
    for i in range(max(2, start), len(df)):
        if l[i] > h[i - 2]:
            res.append({"i": i, "lo": float(h[i - 2]), "hi": float(l[i])})
    return res


def sweeps_bull(df, n: int = 3, lookback: int = 40):
    """Sell-side liquidity sweep: wick below a confirmed swing low, close back above it."""
    piv = fractal_pivots(df, n)
    lows = [(i, p) for i, p, k in piv if k == "L"]
    l, c = df["low"].values, df["close"].values
    res = []
    for j in range(max(1, len(df) - lookback), len(df)):
        cands = [(i, p) for i, p in lows if i + n <= j]
        if not cands:
            continue
        i, p = cands[-1]
        if l[j] < p and c[j] > p:
            res.append({"j": j, "level": p, "low": float(l[j])})
    return res


def sweep_signal_bull(df, max_age: int = 6):
    out = []
    sw = sweeps_bull(df)
    if sw and len(df) - 1 - sw[-1]["j"] <= max_age:
        s = sw[-1]
        out.append(_mk("Liquidity", "Sell-side liquidity sweep",
                       "wick took out the swing low {lvl} (low {lo}) and closed back above it - stops grabbed",
                       prices={"lvl": s["level"], "lo": s["low"]}))
    return out


def zombie_bull(df, max_age: int = 5):
    """'Zombie move': a liquidity sweep (stop-hunt wick below a swing low) that
    happens right AT the EMA9, followed by a sharp snap-back (>= 1 ATR off the
    wick low, back above the EMA9). A hyper-scalping pattern."""
    if len(df) < 40:
        return []
    c = df["close"].values
    e9 = df["close"].ewm(span=9, adjust=False).mean().values
    atr = float(atr_series(df).iloc[-1])
    if not atr > 0:
        return []
    for sw in reversed(sweeps_bull(df, lookback=max_age + 1)):
        j, lvl, lo = sw["j"], sw["level"], sw["low"]
        if len(df) - 1 - j > max_age:
            continue
        at_ema = abs(lvl - e9[j]) <= 0.4 * atr or lo <= e9[j] <= float(df['high'].iloc[j])  # level or sweep bar touches EMA9
        if j == len(df) - 1:
            snapped = c[-1] - lo >= 1.5 * atr and c[-1] > e9[-1]
        else:
            snapped = c[-1] - lo >= 1.2 * atr and c[-1] - c[j] >= 0.6 * atr and c[-1] > e9[-1]
        if at_ema and snapped:
            return [_mk("Liquidity", "Zombie move (sweep at EMA9)",
                        "stop-hunt wick took out the swing low {lvl} right at the EMA9 ({e}), then snapped back sharply",
                        prices={"lvl": lvl, "lo": lo, "e": float(e9[j])})]
    return []


def unicorn_bull(df, max_age: int = 60):
    """Sweep of lows -> bullish market-structure shift -> breaker block that
    overlaps a fair value gap = 'Unicorn' zone; fires while price retests it."""
    sw = sweeps_bull(df, lookback=max_age)
    if not sw:
        return []
    atr = atr_series(df).values
    c, o = df["close"].values, df["open"].values
    price = float(c[-1])
    highs = [(i, p) for i, p, k in fractal_pivots(df, 3) if k == "H"]
    for s in reversed(sw):
        j = s["j"]
        prior = [(i, p) for i, p in highs if i < j]
        if not prior:
            continue
        _, hh = prior[-1]
        m = next((x for x in range(j + 1, len(df)) if c[x] > hh), None)  # market structure shift
        if m is None:
            continue
        # breaker: last bullish candle before the sweep's final drop
        k = next((x for x in range(j - 1, max(j - 16, -1), -1) if c[x] > o[x]), None)
        if k is None:
            continue
        blo, bhi = float(df["low"].values[k]), float(df["high"].values[k])
        if (c[m + 1:] < blo).any():
            continue  # breaker failed (closed back through it after the shift)
        fv = [f for f in fvgs_bull(df, start=j) if f["i"] <= m + 1]
        best = None
        for f in fv:
            lo, hi = max(blo, f["lo"]), min(bhi, f["hi"])
            if lo < hi:
                best = (lo, hi)
        if best is None:
            continue
        lo, hi = best
        pad = 0.15 * atr[-1]
        if len(df) - 1 > m and lo - pad <= price <= hi + pad:
            return [_mk("Unicorn", "ICT Unicorn retest",
                        "sweep of {lvl}, structure shift above {hh}, breaker block overlaps a fair value gap at {zl} - {zh}",
                        prices={"lvl": s["level"], "hh": hh, "lo": lo, "hi": hi}, zone=(lo, hi))]
    return []


# --------------------------------------------------------------------------
# More ICT setups (counted inside the existing families so stars stay /7)
# --------------------------------------------------------------------------

def ote_bull(df):
    """OTE = Optimal Trade Entry: price retraced 62-79% of a displacement leg."""
    zz = zigzag(df)
    if len(zz) < 2 or zz[-1][2] != "H" or zz[-2][2] != "L":
        return []
    (ia, a, _), (ib, b, _) = zz[-2], zz[-1]
    leg = b - a
    atr = float(atr_series(df).iloc[ib])
    price = float(df["close"].iloc[-1])
    if leg < 2.5 * atr or len(df) - ib > 100 or not (a < price < b):
        return []
    ret = (b - price) / leg
    if 0.62 <= ret <= 0.79:
        lo, hi = b - 0.79 * leg, b - 0.62 * leg
        return [_mk("Fib", "OTE entry (62-79%)",
                    "displacement leg {a} -> {b}; price retraced {ret:.0%} into the OTE zone {zl} - {zh}; invalid below {a}",
                    prices={"a": a, "b": b}, vals={"ret": ret}, zone=(lo, hi))]
    return []


def fvg_bull(df, max_age: int = 30):
    """Fair Value Gap: a 3-candle imbalance still unfilled, price retesting it."""
    atr = atr_series(df).values
    c = df["close"].values
    price = float(c[-1])
    for f in reversed(fvgs_bull(df, start=max(2, len(df) - max_age))):
        i, lo, hi = f["i"], f["lo"], f["hi"]
        if hi - lo < 0.3 * atr[i] or i >= len(df) - 1:
            continue
        if (c[i + 1:] < lo).any():
            continue  # gap failed (closed through it)
        if lo - 0.15 * atr[-1] <= price <= hi + 0.15 * atr[-1]:
            return [_mk("MSB-OB", "Fair value gap retest",
                        "bullish imbalance {zl} - {zh} (formed {ago} bars ago) still open; price is filling it - a support zone",
                        vals={"ago": len(df) - 1 - i}, zone=(lo, hi))]
    return []


def breaker_bull(df, max_age: int = 60):
    """Breaker block: sweep of lows -> structure shift up -> price retests the
    last up-candle before the sweep (it flipped from resistance to support)."""
    sw = sweeps_bull(df, lookback=max_age)
    if not sw:
        return []
    atr = atr_series(df).values
    c, o = df["close"].values, df["open"].values
    price = float(c[-1])
    highs = [(i, p) for i, p, k in fractal_pivots(df, 3) if k == "H"]
    for sx in reversed(sw):
        j = sx["j"]
        prior = [(i, p) for i, p in highs if i < j]
        if not prior:
            continue
        hh = prior[-1][1]
        m = next((x for x in range(j + 1, len(df)) if c[x] > hh), None)
        k = next((x for x in range(j - 1, max(j - 16, -1), -1) if c[x] > o[x]), None)
        if m is None or k is None:
            continue
        blo, bhi = float(df["low"].values[k]), float(df["high"].values[k])
        if (c[m + 1:] < blo).any():
            continue
        if len(df) - 1 > m and blo - 0.15 * atr[-1] <= price <= bhi + 0.15 * atr[-1]:
            return [_mk("Unicorn", "Breaker block retest",
                        "sweep of {lvl}, structure shift above {hh}; price retesting the breaker block {zl} - {zh}",
                        prices={"lvl": sx["level"], "hh": hh}, zone=(blo, bhi))]
    return []


def judas_bull(df, window_bars: int = 8):
    """Judas swing: right after the day's open (00:00 UTC) price makes a false
    move DOWN through the open (>= 1 ATR), then reclaims it and trades above.
    Intraday timeframes only."""
    if "time" not in df.columns or len(df) < 40:
        return []
    t = pd.to_datetime(df["time"])
    step = (t.iloc[-1] - t.iloc[-2]).total_seconds()
    if step <= 0 or step >= 86400:
        return []
    day = t.dt.normalize()
    idx = np.where(day.values == day.values[-1])[0]
    if len(idx) < 4:
        return []
    d0 = idx[0]
    dopen = float(df["open"].iloc[d0])
    atr = float(atr_series(df).iloc[-1])
    early = df.iloc[d0:d0 + window_bars]
    fake_low = float(early["low"].min())
    price = float(df["close"].iloc[-1])
    if dopen - fake_low >= 1.0 * atr and price >= dopen + 0.3 * atr and len(df) - 1 >= d0 + 2:
        return [_mk("Liquidity", "Judas swing (false open move)",
                    "after the day's open {op}, price faked down to {lo} (stop run) then reclaimed the open and trades above it",
                    prices={"op": dopen, "lo": fake_low})]
    return []


# --------------------------------------------------------------------------
# Primary family: liquidity / OHL / key levels / breakouts
# --------------------------------------------------------------------------

def liq_break_bull(df, lookback: int = 50):
    """'Liquidity lines' = highs/lows of unusually high-volume bars; fires when
    price just closed through one of them (last 2 bars)."""
    if len(df) < 20:
        return []
    recent = df.tail(lookback)
    hv = recent[recent["volume"] > recent["volume"].mean() * 1.5].iloc[:-2]
    levels = sorted(set(hv["high"]).union(hv["low"]))
    c = df["close"].values
    for lvl in levels:
        if c[-3] < lvl <= c[-1] or c[-2] < lvl <= c[-1]:
            return [_mk("Liquidity", "Liquidity line break",
                        "closed through the liquidity level {lvl} (a level built on unusually heavy volume)", prices={"lvl": lvl})]
    return []


def ohl_bull(df):
    if len(df) < 20:
        return []
    atr = float(atr_series(df).iloc[-1])
    o, h, l, c = (float(df[k].iloc[-1]) for k in ("open", "high", "low", "close"))
    pc_h = float(df["high"].iloc[-2])
    if (h - l) >= 0.5 * atr and (o - l) <= 0.1 * atr and c > o:
        return [_mk("Liquidity", "OHL: open = low", "bar opened on its low and closed up - buyers in control from the open")]
    if (c - float(df["close"].iloc[-2])) >= 0.8 * atr and c > pc_h:
        return [_mk("Liquidity", "OHL: breaks prior high", "strong close above the previous bar's high ({ph})",
                    prices={"ph": pc_h})]
    return []


def key_level_bull(df, lookback: int = 100):
    res, sup = sr_levels(df, lookback)
    price = float(df["close"].iloc[-1])
    near = [s for s in sup if s <= price and (price - s) / abs(price) < 0.002]
    if near:
        return [_mk("Liquidity", "At support", "price sitting on a swing-low support level {lvl}", prices={"lvl": max(near)})]
    return []


def breakout_bull(df, lookback: int = 20):
    if len(df) < lookback + 2:
        return []
    prior = df.iloc[-(lookback + 1):-1]
    if df["close"].iloc[-1] > prior["high"].max():
        return [_mk("Liquidity", f"{lookback}-bar breakout", "closed above the {lookback}-bar high {lvl}".replace("{lookback}", str(lookback)),
                    prices={"lvl": float(prior["high"].max())})]
    return []


DETECTORS = (ma_bull, vwap_bull, elliott_bull, fib_bull, msb_ob_bull, order_block_bull, unicorn_bull,
             sweep_signal_bull, zombie_bull, ote_bull, fvg_bull, breaker_bull, judas_bull, liq_break_bull, ohl_bull, key_level_bull, breakout_bull)


def detect_all(df: pd.DataFrame, detectors=None):
    """-> (signals, errors). signals are plain dicts (see _finalize)."""
    detectors = detectors or DETECTORS
    sigs, errs = [], []
    if df is None or len(df) < 60:
        return sigs, ["not enough candles"]
    df = df.reset_index(drop=True)
    for flipped, frame in ((False, df), (True, invert(df))):
        for fn in detectors:
            try:
                sigs += [_finalize(s, flipped) for s in fn(frame)]
            except Exception as e:  # one broken detector must never kill the scan
                errs.append(f"{fn.__name__}: {e}")
    return sigs, errs
