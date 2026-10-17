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

from modules import sig_filters as _sig_filters

BULL, BEAR = "bullish", "bearish"

FAMILY_ICONS = {
    "MA": "\U0001F4C8",         # chart increasing
    "VWAP": "⚓",           # anchor
    "TL": "\u2702\ufe0f",        # scissors: trendline break
    "Elliott": "\U0001F30A",    # wave
    "Unicorn": "\U0001F984",    # unicorn
    "MSB-OB": "\U0001F9F1",     # brick
    "Fib": "\U0001F4D0",        # triangular ruler
    "Liquidity": "\U0001F4A7",  # droplet
}
PRIMARY_FAMILIES = ("Elliott", "Unicorn", "MSB-OB", "Fib", "Liquidity")
CONFIRM_FAMILIES = ("MA", "VWAP", "TL")
ALL_FAMILIES = PRIMARY_FAMILIES + CONFIRM_FAMILIES  # 8 families -> max 8 stars


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
    ("falling", "rising"), ("rising", "falling"),
    ("low", "high"), ("high", "low"),
]
_SWAP_MAP = dict(_SWAPS)
_SWAP_RE = re.compile(r"(?<![\w{])(" + "|".join(sorted(map(re.escape, _SWAP_MAP), key=len, reverse=True)) + r")(?![\w}])")


def _flip_text(text: str) -> str:
    """Bearish twin of a bullish sentence (support<->resistance, above<->below ...)."""
    return _SWAP_RE.sub(lambda m: _SWAP_MAP[m.group(1)], text)


# stable ids so the Arabic text/tag layer does not depend on the English wording
_KEY_PATTERNS = [
    (r"Trendline break", "tlbreak"), (r"Sweep \+ CISD", "cisd"), (r"Model 2022", "m2022"), (r"bullish cross", "ma_cross"), (r"EMA stack", "ema_stack"), (r"VWAP", "vwap"),
    (r"Wave 3 start", "ew3"), (r"Wave 5 start", "ew5"), (r"ABC correction", "abc"), (r"Wave C", "wavec"),
    (r"Zombie", "zombie"), (r"Order block \(", "ob"), (r"OTE entry", "ote"), (r"Fair value gap", "fvg"), (r"Breaker block", "breaker"), (r"Judas", "judas"), (r"Fib retracement", "fib"), (r"Structure break", "msb_ob"), (r"liquidity sweep", "sweep"),
    (r"Unicorn", "unicorn"), (r"Liquidity line break", "liqline"), (r"OHL: open", "ohl_open"),
    (r"OHL: breaks", "ohl_break"), (r"At support", "level"), (r"-bar breakout", "breakout"),
    (r"RSI divergence", "rsi_div"), (r"MACD divergence", "macd_div"), (r"CRT sweep", "crt"), (r"SMT divergence", "smt"), (r"Donchian ensemble", "donch"), (r"Session AMD", "sess_amd"), (r"opening-range breakout", "orb"), (r"Kill Zone Sniper", "kzs"), (r"Power of Three", "po3"), (r"SMA 10/40", "sma1040"), (r"Donchian 55", "turtle55"),
]


def _mk(family, name, detail, prices=None, vals=None, zone=None, counter=False):
    """counter=True marks a signal whose direction is OPPOSITE to the frame it
    was detected in (e.g. the ABC correction after a bullish impulse)."""
    key = next((k for pat, k in _KEY_PATTERNS if re.search(pat, name)), "other")
    return {"family": family, "name": name, "key": key, "_t": detail, "_p": prices or {}, "_v": vals or {},
            "zone": zone, "counter": counter}


def _filter_note(v: dict) -> str:
    """What the Group-A quality filters measured (see sig_filters.py), appended to the signal text."""
    bits = []
    if v.get("strict"):
        bits.append("strict structure break")
    if v.get("obvol"):
        bits.append("order-block volume x" + str(v["obvol"]) + " of normal")
    if v.get("bovol"):
        bits.append("breakout volume x" + str(v["bovol"]) + ", est. net buying " + str(round(100 * v.get("bodelta", 0))) + "% (candle-based estimate)")
    return " [" + "; ".join(bits) + "]" if bits else ""


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
        "detail": tmpl.format(**{k: fp(v) for k, v in p.items()}, **sig["_v"]) + _filter_note(sig["_v"]),
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


def trendbreak_bull(df, lookback: int = 120, max_age: int = 3):
    """Trendline break (bullish = a falling line through lower swing highs is broken UP; the bearish twin comes from the
    inverted frame). Rules (common trendline-break practice: LuxAlgo / TradingView trendline-break scripts):
      line   : through two fractal swing highs (n=3) at least 6 bars apart, the later one lower; the touches count
               (other swing highs within 0.25 ATR of the line). Between the first pivot and the break NO close may have
               been above the line (otherwise the line was already invalid).
      break  : a bar CLOSES above the line by >= 0.2 ATR (a poke / wick does not count), within the last `max_age` bars,
               the bar before it closed under the line (first break), and the latest close is still above the line.
      quality: needs >= 1 of: volume >= 1.2x its 20-bar mean (or >= 3 touches), strong breakout candle (body >= 60% of range,
               close in its top 30%), a retest (price came back to the line within 0.3 ATR after the break and held).
    Ordinary mean-reversion on the break bar itself is not a signal - it must hold above the line on the last close."""
    n = len(df)
    if n_short(df, 60):
        return []
    c, h, l, o, v = (df[k].values for k in ("close", "high", "low", "open", "volume"))
    a = atr_series(df).values
    piv = [p for p in fractal_pivots(df, 3) if p[2] == "H" and p[0] >= n - lookback]
    piv = piv[-5:]
    best = None
    for x in range(len(piv)):
        for y in range(x + 1, len(piv)):
            i1, p1, _ = piv[x]; i2, p2, _ = piv[y]
            if i2 - i1 < 6 or not p2 < p1:
                continue
            slope = (p2 - p1) / (i2 - i1)
            line = lambda i: p1 + slope * (i - i1)
            touches = 2 + sum(1 for (i3, p3, _) in piv if i3 not in (i1, i2) and i3 > i1 and abs(p3 - line(i3)) <= 0.25 * a[i3])
            for b in range(n - 1, max(i2 + 1, n - max_age) - 1, -1):                    # most recent break first
                if not (c[b] > line(b) + 0.2 * a[b] and c[b - 1] <= line(b - 1) + 0.05 * a[b - 1]):
                    continue
                if c[-1] <= line(n - 1) or any(c[j] > line(j) + 0.05 * a[j] for j in range(i1 + 1, b)):
                    continue                                                           # fell back under the line / line was already broken earlier
                rng = max(h[b] - l[b], 1e-12)
                vol_ok = n > 25 and v[b] > 0 and v[b] >= 1.2 * np.mean(v[max(0, b - 20):b])
                strong = (c[b] - o[b]) >= 0.6 * rng and (h[b] - c[b]) <= 0.3 * rng
                retest = any(l[j] <= line(j) + 0.3 * a[j] and c[j] > line(j) for j in range(b + 1, n))
                q = (vol_ok or touches >= 3) + strong + retest
                if q >= 1 and (best is None or (q, touches, -(n - 1 - b)) > best[0]):
                    best = ((q, touches, -(n - 1 - b)), b, line(b), touches, vol_ok, strong, retest, n - 1 - b)
                break
    if not best:
        return []
    _, b, lv, touches, vol_ok, strong, retest, ago = best
    why = [t for ok, t in ((vol_ok, "volume expansion"), (touches >= 3, "3+ touches"), (strong, "strong close"), (retest, "retest held")) if ok]
    return [_mk("TL", f"Trendline break ({touches} touches)",
                "close above a falling trendline ({tp}) {ago} bar(s) ago; confirmed by: " + ", ".join(why),
                prices={"tp": float(lv)}, vals={"ago": ago, "touches": touches, "q": len(why)})]


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


def _raid(df, lookback: int, lows=None):
    """The sell-side raid of the window: the window's LOWEST low (e) must lie below a confirmed swing low (lvl) that stood before it;
    j is the first bar that took that level out. -> (j, e, lvl) or None. Anchoring on the window's extreme (not on 'any bar under a stale
    swing low') keeps the later reversal bars from being mistaken for the raid."""
    n = len(df); l = df["low"].values
    if lows is None:
        lows = [(i, p) for i, p, k in fractal_pivots(df, 3) if k == "L"]
    s0 = max(3, n - lookback)
    e = s0 + int(np.argmin(l[s0:]))
    cand = [(i, p) for i, p in lows if i + 3 <= e and p > l[e] and i < e]
    if not cand:
        return None
    si, lvl = cand[-1]
    j = next((b for b in range(si + 1, e + 1) if l[b] < lvl), e)
    return j, e, lvl


def cisd_bull(df, lookback: int = 40, max_age: int = 6):
    """Sweep + CISD (Change in State of Delivery), bullish; the bearish twin comes from the inverted frame.
    Rules (ICT CISD model as taught in the channel summaries and described by LuxAlgo):
      1. liquidity : a bar trades BELOW the latest confirmed swing low (sell-side liquidity taken).
      2. the run   : the last unbroken series of DOWN-closing candles into the lowest low after that sweep.
      3. CISD level: the OPEN of the first candle of that series.
      4. confirm   : a later candle BODY closes above that level (a wick through it does not count), within `max_age` bars,
                     and the latest close is still above the level.
      5. structure : price has NOT yet broken the last swing high that stood before the sweep - the point of the model is to
                     be in BEFORE the market-structure break. (If it already broke, MSB-OB covers it.)
    Entry = retest of the CISD level, stop under the sweep low, target the swing highs (1-3R).
    Quality tags: displacement (a fair value gap left by the confirming move), retest held, London / New York window."""
    n = len(df)
    if n_short(df, 60):
        return []
    o, h, l, c = (df[k].values for k in ("open", "high", "low", "close"))
    a = atr_series(df).values
    piv = fractal_pivots(df, 3)
    lows = [(i, p) for i, p, k in piv if k == "L"]
    highs = [(i, p) for i, p, k in piv if k == "H"]
    for _once in (0,):
        rd = _raid(df, lookback, lows)
        if rd is None:
            continue
        j, e, lvl = rd                                                        # e = the extreme of the sweep move
        prior_h = [p for i, p in highs if i < j]
        if not prior_h:
            continue
        struct = prior_h[-1]
        m = e
        while m >= 0 and not c[m] < o[m]:
            m -= 1                                                            # last down-close at/under the extreme
        if m < 1:
            continue
        s0 = m
        while s0 - 1 >= 0 and c[s0 - 1] < o[s0 - 1]:
            s0 -= 1                                                           # first candle of that down series
        cl = float(o[s0])
        conf = next((b for b in range(e + 1, n) if c[b] > cl and c[b] > o[b]), None)
        if conf is None or n - 1 - conf > max_age or c[-1] <= cl:
            continue
        if h[conf:].max() > struct or h[e + 1:conf].max(initial=-1e18) > struct:
            continue                                                          # structure already broken -> not a pre-break entry
        fvg = any(l[k] > h[k - 2] for k in range(max(2, conf), min(n, conf + 2)))
        retest = any(l[k] <= cl + 0.3 * a[k] and c[k] > cl for k in range(conf + 1, n))
        kz = False
        if "time" in df.columns:
            hr = pd.to_datetime(df["time"].iloc[conf]).hour
            kz = 7 <= hr < 10 or 12 <= hr < 15                                # London / New York windows in UTC (DST ignored)
        why = [t for ok, t in ((fvg, "displacement + FVG"), (retest, "retest held"), (kz, "London/NY window")) if ok]
        sl = float(l[e])
        return [_mk("Liquidity", "Sweep + CISD",
                    "swing low {lvl} swept (low {sl}); candle body closed above the CISD level {cl} (open of the last down-candle series) "
                    "{ago} bar(s) ago, structure not broken yet" + ("; " + ", ".join(why) if why else "") + "; stop under {sl}, target the swing high {st}",
                    prices={"lvl": float(lvl), "sl": sl, "cl": cl, "st": float(struct)},
                    vals={"ago": n - 1 - conf, "q": len(why)})]
    return []


def model2022_bull(df, lookback: int = 40, max_age: int = 8):
    """ICT Model 2022 (bullish; bearish twin from the inverted frame): raid -> displacement + market-structure shift -> FVG entry.
      1. raid        : a bar trades below the latest confirmed swing low (sell-side liquidity taken).
      2. MSS         : after the raid's extreme, a bar CLOSES above the most recent swing high that stood before it, with a real
                       body (>= 0.6 ATR) - 'displacement'. A structure break with no raid before it is not a Model 2022 setup.
      3. imbalance   : that move leaves a bullish fair value gap = the entry zone (limit order inside it).
      4. stop        : under the raid's low.   target : the opposing liquidity pool (highest swing high in the window).
      5. time        : only taken in a New York killzone / Silver Bullet window (checked when the frame has a 'time' column).
    A setup that is still waiting for the structure break is the CISD signal's job; this one is the confirmed version."""
    n = len(df)
    if n_short(df, 60):
        return []
    o, h, l, c = (df[k].values for k in ("open", "high", "low", "close"))
    a = atr_series(df).values
    piv = fractal_pivots(df, 3)
    lows = [(i, p) for i, p, k in piv if k == "L"]
    highs = [(i, p) for i, p, k in piv if k == "H"]
    for _once in (0,):
        rd = _raid(df, lookback, lows)
        if rd is None:
            continue
        j, e, lvl = rd
        opp = [p for i, p in highs if i < e]
        if not opp:
            continue
        sh = opp[-1]
        m = next((b for b in range(e + 1, n) if c[b] > sh and (c[b] - o[b]) >= 0.6 * a[b]), None)
        if m is None or n - 1 - m > max_age or c[-1] <= l[e]:
            continue
        gaps = [k for k in range(max(2, e + 1), min(n, m + 2)) if l[k] > h[k - 2]]
        if not gaps:
            continue
        k = gaps[-1]; zone = (float(h[k - 2]), float(l[k]))
        in_window = True
        if "time" in df.columns:
            from modules.context import time_window
            tw = time_window(df.iloc[:m + 1])
            in_window = bool(tw["kz"] or tw["silver"]) if tw["ny_hour"] is not None else True
        if not in_window:
            continue
        pool = max([p for i, p in highs if i >= n - lookback] or [sh])
        return [_mk("Liquidity", "Model 2022 (raid + MSS + FVG)",
                    "swing low {lvl} raided (low {sl}), then a displacement candle closed above the swing high {sh} {ago} bar(s) ago leaving a fair value gap; "
                    "entry inside the gap, stop under {sl}, target the liquidity pool {pool}",
                    prices={"lvl": float(lvl), "sl": float(l[e]), "sh": float(sh), "pool": float(pool), "t": float(pool), "inv": float(l[e])},
                    vals={"ago": n - 1 - m}, zone=zone)]
    return []


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


# --------------------------------------------------------------------------
# Momentum divergence (RSI / MACD regular) + CRT (Candle Range Theory)
# --------------------------------------------------------------------------

def _rsi_arr(close: pd.Series, n: int = 14) -> np.ndarray:
    d = close.diff()
    au = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    ad = (-d).clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    out = 100 - 100 / (1 + au / ad.replace(0, np.nan))
    return out.where(ad != 0, 100.0).fillna(50.0).values


def _macd_arr(close: pd.Series) -> np.ndarray:
    return (close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()).values


def _div_bull(df, osc, osc_name, key_name, o_thr, zone_ok, show, max_age=15, min_gap=5, max_gap=60):
    """Regular BULLISH divergence: price prints a lower swing low, the oscillator a HIGHER low at the same swing.
    Bearish is the mirror and comes from running this on the inverted frame."""
    piv = [(i, p) for i, p, k in fractal_pivots(df, 3) if k == "L"]
    n = len(df)
    if len(piv) < 2 or n - 1 - piv[-1][0] > max_age:
        return []
    l, c = df["low"].values, df["close"].values
    atr = float(atr_series(df).iloc[-1])
    i2, p2 = piv[-1]
    if l[i2 + 1:].size and l[i2 + 1:].min() <= p2:
        return []
    if c[-1] < p2 + 0.3 * atr:                          # price must already be turning up
        return []
    for i1, p1 in reversed(piv[:-1][-3:]):
        if not (min_gap <= i2 - i1 <= max_gap) or p2 >= p1 - 0.1 * atr:
            continue
        if l[i1 + 1:i2].min() <= p2:                    # something lower in between -> not a clean pair
            continue
        o1, o2 = float(osc[i1]), float(osc[i2])
        if o2 - o1 >= o_thr and zone_ok(o1, o2):
            return [_mk("MA", f"{osc_name} divergence", "price made a new low {p2} (previous low {p1}) but " + osc_name +
                        " did NOT confirm: " + osc_name + " {o2} vs {o1} at the previous low",
                        prices={"p1": p1, "p2": p2}, vals={"o1": show(df, o1), "o2": show(df, o2)})]
    return []


def _inv_frame(df):                                     # the mirrored frame has negative prices
    return float(df["close"].iloc[-1]) < 0


def rsi_div_bull(df):
    if len(df) < 60:
        return []
    r = _rsi_arr(df["close"])
    show = lambda d, v: f"{(100 - v if _inv_frame(d) else v):.0f}"
    return _div_bull(df, r, "RSI", "rsi_div", 2.0, lambda o1, o2: o1 < 45, show)


def macd_div_bull(df):
    if len(df) < 70:
        return []
    m = _macd_arr(df["close"])
    atr = float(atr_series(df).iloc[-1]) or 1e-9
    show = lambda d, v: f"{(-v if _inv_frame(d) else v):.4g}"
    return _div_bull(df, m, "MACD", "macd_div", 0.03 * atr, lambda o1, o2: o1 < 0, show)


_CRT_MAP = ((300, 3600, "1H"), (3600, 14400, "4H"), (14400, 86400, "1D"), (86400, 604800, "1W"))


def crt_bull(df, fresh: int = 5):
    """Candle Range Theory (bullish): the last COMPLETED higher-timeframe candle is the reference range. A later
    candle wicks BELOW its low (sweep of sell-side liquidity) and closes back inside; entry on that reclaim, stop under
    the sweep wick, target the opposite side of the range. HTF is derived from the same candles (1m->1H, 1h->4H, 4h->1D, 1d->1W)."""
    if "time" not in df.columns or len(df) < 60:
        return []
    t = pd.to_datetime(df["time"])
    if t.dt.tz is not None:
        t = t.dt.tz_localize(None)
    sec = ((t - pd.Timestamp(0)) // pd.Timedelta(seconds=1)).values.astype("int64")
    step = int(np.median(np.diff(sec[-30:]))) if len(sec) > 3 else 0
    m = next(((per, lab) for mx, per, lab in _CRT_MAP if 0 < step <= mx), None)
    if not m or step >= m[0]:
        return []
    per, lab = m
    g = (sec - (345600 if per == 604800 else 0)) // per
    ids = list(dict.fromkeys(g.tolist()))
    if len(ids) < 3:
        return []
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    n, atr = len(df), float(atr_series(df).iloc[-1])
    for rid in (ids[-2], ids[-3]):
        idx = np.where(g == rid)[0]
        if len(idx) < 0.6 * per / step:                 # partial candle (start of the data) -> not a real range
            continue
        rh, rl = float(h[idx].max()), float(l[idx].min())
        rng = rh - rl
        start = int(idx[-1]) + 1
        if rng < 3 * atr or start >= n - 1:
            continue
        if (c[start:] >= rh).any():                      # the range was already taken out on the other side
            continue
        sw = next((k for k in range(start, n) if l[k] < rl), None)
        if sw is None:
            continue
        j = next((k for k in range(sw, n) if c[k] > rl), None)
        if j is None or n - 1 - j > fresh or (c[j:] <= rl).any():
            continue
        sl = float(l[sw:].min())
        if rl - sl > 1.0 * rng or c[-1] > rl + 0.5 * rng:   # sweep too deep / entry already late
            continue
        if (rh - c[-1]) < (c[-1] - sl):                  # need at least 1R to the far side of the range
            continue
        return [_mk("Liquidity", f"CRT sweep ({lab} range low)",
                    "reference " + lab + " candle range {rl} - {rh}: price swept below the range low then closed back inside; "
                    "entry on the reclaim, stop beyond the sweep wick {sl}, target the other side of the range {rh}",
                    prices={"rl": rl, "rh": rh, "sl": sl}, vals={"tf": lab}, zone=(sl, rl))]
    return []


# --------------------------------------------------------------------------
# Donchian-channel ensemble (trend following)
# --------------------------------------------------------------------------
# Idea from "Catching Crypto Trends" (Zarattini, Pagani, Barbon, SSRN 5209907): aggregate several Donchian-channel
# trend models with DIFFERENT lookbacks into one signal. The abstract does not publish the lookback list or any
# thresholds, so the horizons and the 2/3-agreement + fresh-breakout rule below are this dashboard's own choices.
DONCH_LOOKBACKS = (5, 10, 20, 30, 60, 90, 150, 250, 360)


def donchian_state(close, n: int):
    """Channel model for one lookback on CLOSES: +1 after a close above the previous n closes' high, -1 after a close
    below their low, otherwise the previous state holds. -> (state, bars since the last change of state)."""
    c = np.asarray(close, dtype=float)
    st, age = 0, 0
    for i in range(n, len(c)):
        w = c[i - n:i]
        new = 1 if c[i] > w.max() else -1 if c[i] < w.min() else st
        age = 0 if new != st else age + 1
        st = new
    return st, age


def donchian_bull(df, min_agree: float = 2 / 3, fresh_bars: int = 3):
    c = df["close"].values
    lbs = [n for n in DONCH_LOOKBACKS if len(c) >= n + 10]
    if len(lbs) < 4:
        return []
    longs, fresh = 0, False
    for n in lbs:
        stt, age = donchian_state(c, n)
        if stt > 0:
            longs += 1
            fresh = fresh or age < fresh_bars
    if longs / len(lbs) >= min_agree and fresh:
        return [_mk("MA", "Donchian ensemble trend", "{k} of {m} Donchian channels ({lo}-{hi} bars) are in a breakout state - price closed above the channel high - "
                    "and a fresh breakout fired within the last 3 bars: trend-following ensemble", vals={"k": longs, "m": len(lbs), "lo": lbs[0], "hi": lbs[-1]})]
    return []


# --------------------------------------------------------------------------
# Item 15: classic hedge-fund / CTA trend rules. Daily (or weekly) bars only - on intraday bars these periods mean nothing.
# N = 20-bar average true range (the Turtle "N"); the stop / invalidation is entry - 2N, as in the Turtle rules.
# Same MA family as the other trend followers, so they never add a star on their own family count.
# --------------------------------------------------------------------------
def _daily_plus(df) -> bool:
    step = _bar_minutes(df)
    return bool(step) and step >= 1440 * 0.9


def sma1040_bull(df, fresh: int = 3):
    """Dual moving-average trend rule (managed-futures classic): SMA 10 crossed above SMA 40 within the last `fresh`
    bars, is still above it, and the close is above SMA 40. Invalidation = entry - 2N."""
    if not _daily_plus(df) or len(df) < 60:
        return []
    c = df["close"]
    f, s = c.rolling(10).mean().values, c.rolling(40).mean().values
    n = len(df)
    for j in range(n - 1, n - 1 - fresh, -1):
        if f[j - 1] <= s[j - 1] and f[j] > s[j]:
            break
    else:
        return []
    if not (f[-1] > s[-1] and c.iloc[-1] > s[-1]):
        return []
    N = float(atr_series(df, 20).iloc[-1]); px = float(c.iloc[-1])
    return [_mk("MA", "SMA 10/40 trend cross (hedge-fund rule)",
                "SMA 10 {s10} crossed above SMA 40 {s40} " + str(n - 1 - j) + " bar(s) ago and the close is above both: managed-futures dual-MA "
                "trend rule; stop 2N (2 x 20-bar ATR) at {inv}", prices={"s10": float(f[-1]), "s40": float(s[-1]), "inv": px - 2 * N},
                vals={"ago": n - 1 - j, "N": round(N, 6)})]


def turtle55_bull(df, fresh: int = 3):
    """Turtle System 2 entry: a CLOSE above the highest high of the previous 55 bars (the original used an intraday touch;
    a close is used here so the signal does not repaint), first time within the last `fresh` bars.
    Stop = entry - 2N, exit = a close below the 20-bar low (shown as the trailing exit level)."""
    if not _daily_plus(df) or len(df) < 80:
        return []
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    n = len(df)
    brk = [j for j in range(n - fresh, n) if c[j] > h[j - 55:j].max()]
    if not brk:
        return []
    j = brk[0]
    if j > 0 and c[j - 1] > h[j - 56:j - 1].max():
        return []                                    # already in a breakout before the window - not a fresh entry
    N = float(atr_series(df, 20).iloc[-1]); px = float(c[-1])
    hi55, ex20 = float(h[j - 55:j].max()), float(l[n - 20:].min())
    if px <= ex20:
        return []
    return [_mk("MA", "Donchian 55 breakout (Turtle System 2)",
                "a close above the 55-bar high {lvl} (" + str(n - 1 - j) + " bar(s) ago): Turtle System 2 entry; stop 2N at {inv}, "
                "trailing exit on a close below the 20-bar low {x}", prices={"lvl": hi55, "inv": px - 2 * N, "x": ex20},
                vals={"ago": n - 1 - j, "N": round(N, 6)})]


# --------------------------------------------------------------------------
# ICT session model (UTC, fixed approximations - ICT quotes New York times, which shift with daylight saving):
#   Asia range (accumulation) 00:00-07:00, London window (manipulation) 07:00-12:00, New York window 12:00-17:00 (distribution)
#   Opening range = first 15 minutes after the London open (07:00) and the New York open (13:30)
# --------------------------------------------------------------------------
ASIA_END_H, LONDON_END_H, DIST_END_H = 7, 12, 17
OPEN_RANGES = ((7, 0), (13, 30))   # (hour, minute) UTC


def _bar_minutes(df):
    t = df["time"]
    if len(t) < 3:
        return None
    return float(t.diff().dropna().median().total_seconds()) / 60.0


def session_amd_bull(df):
    """Power of 3 / AMD: Asia range builds, London sweeps its LOW (stop run) and price closes back inside -> distribution up."""
    step = _bar_minutes(df)
    if not step or step > 60:
        return []
    t = df["time"]; day = t.iloc[-1].normalize(); h = t.iloc[-1].hour + t.iloc[-1].minute / 60
    if not (ASIA_END_H <= h < DIST_END_H):
        return []
    asia = df[(t >= day) & (t < day + pd.Timedelta(hours=ASIA_END_H))]
    if len(asia) < max(4, int(180 / step)):
        return []
    al, ah = float(asia["low"].min()), float(asia["high"].max())
    after = df[(t >= day + pd.Timedelta(hours=ASIA_END_H)) & (t <= day + pd.Timedelta(hours=LONDON_END_H))]
    if after.empty:
        return []
    atr = float(atr_series(df).iloc[-1])
    sweep = float(after["low"].min())
    if sweep >= al - 0.1 * atr or float(after["high"].max()) > ah:      # no sweep of the low, or the high was taken first
        return []
    close = float(df["close"].iloc[-1])
    if close < al + 0.3 * atr or close >= ah:
        return []
    return [_mk("Liquidity", "Session AMD sweep",
                "AMD session model: the Asian range (accumulation) low {al} was swept to {sw} in the London window (manipulation) and price closed back above it; "
                "distribution phase targets the Asian high {ah}, stop below the sweep {sw}",
                prices={"al": al, "ah": ah, "sw": sweep, "t": ah, "inv": sweep})]


def session_orb_bull(df):
    """Opening-range breakout: first 15 minutes after the London / New York open define the range; a fresh close above its high."""
    step = _bar_minutes(df)
    if not step or step > 15:
        return []
    t = df["time"]; last = t.iloc[-1]; day = last.normalize(); atr = float(atr_series(df).iloc[-1])
    for hh, mm in OPEN_RANGES:
        o = day + pd.Timedelta(hours=hh, minutes=mm); e = o + pd.Timedelta(minutes=15)
        if not (e <= last <= o + pd.Timedelta(hours=3)):
            continue
        orng = df[(t >= o) & (t < e)]
        if len(orng) < max(1, int(15 / step)):
            continue
        oh, ol = float(orng["high"].max()), float(orng["low"].min())
        post = df[t >= e]
        c = post["close"].values
        up = c > oh + 0.1 * atr
        if not up[-1] or (post["close"].values < ol).any():
            continue
        first = int(np.argmax(up))
        if len(c) - 1 - first > 6:      # breakout must be fresh
            continue
        return [_mk("Liquidity", "Session opening-range breakout",
                    "Opening range (first 15 minutes after the {sess} open) {ol} - {oh}: price closed above the range high and has not closed below its low; "
                    "range high is the pivot, stop below the range low",
                    prices={"oh": oh, "ol": ol, "t": oh + (oh - ol) * 2, "inv": ol}, vals={"sess": "London" if hh == 7 else "New York"})]
    return []

# --------------------------------------------------------------------------
# Group B: Kill Zone Sniper + Power of Three (new). Times are New York (daylight-saving aware).
# Both fire only INSIDE a kill zone; both need a displacement candle (not just a poke) and at least 1.5R to the
# target, because a bare power-of-three entry has a weak default R:R.
# --------------------------------------------------------------------------
KZ_NY = (("London", 2, 5), ("NY AM", 7, 10))     # same windows as modules/context.py


def _ny_clock(df):
    t = pd.to_datetime(df["time"])
    t = t.dt.tz_localize("UTC") if t.dt.tz is None else t
    return t.dt.tz_convert("America/New_York")


def _kz_name(ts):
    hr = ts.hour + ts.minute / 60
    return next((n for n, a, b in KZ_NY if a <= hr < b), None)


def _intraday(df, max_min: int = 60):
    step = _bar_minutes(df)
    return bool(step) and step <= max_min


def killzone_sniper_bull(df, fresh: int = 3, look: int = 20):
    """ICT Kill Zone Sniper (bullish): inside London / NY-AM a candle sweeps the lowest low of the last 20 bars, closes back
    above it with a displacement body (>= 0.9 ATR, bullish); with real volume the candle must also trade >= 1.5x its 20-bar
    average. Entry on that candle's close, stop under the sweep wick, target the swing high of the last 30 bars (>= 1.5R)."""
    if "time" not in df.columns or len(df) < 60 or not _intraday(df):
        return []
    n = len(df); clk = _ny_clock(df)
    o, h, l, c = (df[x].values for x in ("open", "high", "low", "close"))
    atr = atr_series(df).values
    vol_ok = "volume" in df.columns and (np.nan_to_num(df["volume"].values) > 0).mean() >= 0.9
    v = df["volume"].values.astype(float) if vol_ok else None
    for j in range(n - 1, max(n - 2 - fresh, look + 2), -1):
        kz = _kz_name(clk.iloc[j])
        if not kz:
            continue
        lvl = float(l[j - look:j].min())
        if not (l[j] < lvl and c[j] > lvl and c[j] > o[j] and (c[j] - o[j]) >= 0.9 * atr[j]):
            continue
        vr = None
        if vol_ok:
            avg = float(np.mean(v[j - 20:j]))
            vr = float(v[j] / avg) if avg > 0 else 0.0
            if vr < 1.5:
                continue
        sl = float(l[j:].min())
        tgt = float(h[max(0, n - 30):].max())
        px = float(c[-1])
        if (c[j:] <= sl).any() or px - sl <= 0 or (tgt - px) < 1.5 * (px - sl):
            continue
        txt = ("inside the " + kz + " kill zone a candle swept the 20-bar low {lvl} and closed back above it with a displacement body"
               + (" on " + str(round(vr, 1)) + "x average volume" if vr else "") + "; stop under the sweep wick {sl}, target the recent swing high {t}")
        return [_mk("Liquidity", "Kill Zone Sniper sweep", txt, prices={"lvl": lvl, "sl": sl, "t": tgt, "inv": sl}, vals={"kz": kz, "vr": round(vr, 1) if vr else 0}, zone=(sl, lvl))]
    return []


def power_of_three_bull(df, fresh: int = 4):
    """ICT Power of Three (bullish), restricted: day opens (00:00 New York) = accumulation reference; MANIPULATION = price
    trades >= 0.5 ATR BELOW the daily open and that low prints inside a kill zone; the entry is only allowed after the
    REBOUND is confirmed - a bullish displacement candle that closes back ABOVE the daily open (return inside the range).
    Stop under the manipulation low, target = the higher of (daily open + 2x the manipulation depth) and yesterday's high, and the move must still offer >= 1.5R."""
    if "time" not in df.columns or len(df) < 60 or not _intraday(df):
        return []
    n = len(df); clk = _ny_clock(df)
    day = clk.dt.normalize()
    last_day = day.iloc[-1]
    idx = np.where((day == last_day).values)[0]
    if len(idx) < 8:
        return []
    o, h, l, c = (df[x].values for x in ("open", "high", "low", "close"))
    atr = atr_series(df).values
    d0 = int(idx[0]); op = float(o[d0])
    seg = slice(d0, n)
    ml_i = d0 + int(np.argmin(l[seg])); ml = float(l[ml_i])
    if op - ml < 0.5 * atr[-1] or not _kz_name(clk.iloc[ml_i]):
        return []                                        # no real dip below the open, or it did not happen in a kill zone
    j = next((k for k in range(ml_i, n) if c[k] > op and c[k] > o[k] and (c[k] - o[k]) >= 0.7 * atr[k]), None)
    if j is None or n - 1 - j > fresh or (c[j:] <= op).any():
        return []                                        # no confirmed rebound / too old / lost the open again
    px = float(c[-1]); sl = ml - 0.1 * atr[-1]; tgt = op + 2 * (op - ml)
    prev = np.where((day == day.iloc[d0 - 1]).values)[0] if d0 > 0 else []
    if len(prev):
        pdh = float(h[prev].max())                       # yesterday's high = the usual distribution objective
        tgt = max(tgt, pdh) if pdh > px else tgt
    if px - sl <= 0 or (tgt - px) < 1.5 * (px - sl):
        return []
    return [_mk("Liquidity", "Power of Three rebound",
                "Power of Three: the day opened at {op}, price was manipulated down to {ml} inside a kill zone, then rebounded with a displacement candle and closed back above the daily open; "
                "stop under the manipulation low, distribution target {t}",
                prices={"op": op, "ml": ml, "t": tgt, "inv": sl}, zone=(ml, op))]


DETECTORS_SESSION = (session_amd_bull, session_orb_bull)

DETECTORS = (ma_bull, vwap_bull, trendbreak_bull, cisd_bull, model2022_bull, elliott_bull, fib_bull, msb_ob_bull, order_block_bull, unicorn_bull,
             sweep_signal_bull, zombie_bull, ote_bull, fvg_bull, breaker_bull, judas_bull, liq_break_bull, ohl_bull, key_level_bull, breakout_bull,
             rsi_div_bull, macd_div_bull, crt_bull, donchian_bull, sma1040_bull, turtle55_bull, session_amd_bull, session_orb_bull, killzone_sniper_bull, power_of_three_bull)


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
                sigs += [_finalize(s, flipped) for s in _sig_filters.apply(frame, fn(frame))]
            except Exception as e:  # one broken detector must never kill the scan
                errs.append(f"{fn.__name__}: {e}")
    return sigs, errs
