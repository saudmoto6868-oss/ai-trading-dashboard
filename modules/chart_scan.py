"""
CHART SCANNER (Finviz-style screener + chart grid)
Pure functions (no Streamlit): indicator maths, boolean screener conditions per
symbol, and a tiny self-contained SVG candle chart (EMA 9/21/50 + VWAP).
"""

from __future__ import annotations

import base64
import html

import numpy as np
import pandas as pd

from modules.signals import atr_series, fractal_pivots, invert, zigzag

# filter id -> label (shown in the UI)
RSI_FILTERS = {
    "rsi_gt70": "RSI > 70 (overbought)", "rsi_gt80": "RSI > 80", "rsi_gt90": "RSI > 90",
    "rsi_lt30": "RSI < 30 (oversold)", "rsi_lt20": "RSI < 20", "rsi_lt10": "RSI < 10",
}
# Finviz / TradingView-screener style: state ("above / below") and event ("crossed above / below within the last N candles")
EMA_LENS = (9, 20, 50, 200)
EMA_PAIRS = ((9, 20), (20, 50), (50, 200))
EMA_FILTERS = {}
for _n in EMA_LENS:
    EMA_FILTERS.update({f"px_above_{_n}": f"Price above EMA {_n}", f"px_below_{_n}": f"Price below EMA {_n}",
                        f"px_xup_{_n}": f"Price crossed above EMA {_n}", f"px_xdn_{_n}": f"Price crossed below EMA {_n}"})
for _a, _b in EMA_PAIRS:
    EMA_FILTERS.update({f"ma_above_{_a}_{_b}": f"EMA {_a} above EMA {_b}", f"ma_below_{_a}_{_b}": f"EMA {_a} below EMA {_b}",
                        f"ma_xup_{_a}_{_b}": f"EMA {_a} crossed above EMA {_b} (golden)", f"ma_xdn_{_a}_{_b}": f"EMA {_a} crossed below EMA {_b} (death)"})
EMA_FILTERS.update({"stack_bull": "Bullish stack (price > EMA 9 > 20 > 50)", "stack_bear": "Bearish stack (price < EMA 9 < 20 < 50)",
                    "above_all": "Price above EMA 9/20/50 (all)", "below_all": "Price below EMA 9/20/50 (all)"})
PATTERN_FILTERS = {
    "chan_up": "Channel breakout (up)", "chan_dn": "Channel breakdown (down)",
    "tl_up": "Trendline break (down-trend line broken up)", "tl_dn": "Trendline break (up-trend line broken down)",
    "dbl_top": "Double top", "dbl_bottom": "Double bottom",
}
# strategy filters: id -> (label, matcher on the scanner's signals: family or key)
STRATEGY_FILTERS = {
    "st_elliott": ("Elliott Wave (3 / 5)", ("family", "Elliott")), "st_ew3": ("Elliott · Wave 3 start", ("key", "ew3")),
    "st_msb": ("SMC · MSB + Order Block", ("family", "MSB-OB")), "st_ob": ("Order Block", ("key", "ob")),
    "st_unicorn": ("ICT Unicorn", ("family", "Unicorn")), "st_breaker": ("Breaker Block", ("key", "breaker")),
    "st_fvg": ("Fair Value Gap (FVG)", ("key", "fvg")), "st_ote": ("ICT OTE (entry zone)", ("key", "ote")),
    "st_judas": ("ICT Judas swing", ("key", "judas")), "st_sweep": ("Liquidity sweep", ("key", "sweep")),
    "st_fib": ("Fibonacci", ("family", "Fib")), "st_vwap": ("VWAP", ("family", "VWAP")), "st_ma": ("Moving averages", ("family", "MA")),
}
ALL_FILTERS = {**RSI_FILTERS, **EMA_FILTERS, **PATTERN_FILTERS, **{k: v[0] for k, v in STRATEGY_FILTERS.items()}}


def flag_side(k: str):
    """'buy' / 'sell' / None: which side a plain filter id points to (used by the Buy-only / Sell-only switch)."""
    if k.startswith(("rsi_lt", "px_above", "px_xup", "ma_above", "ma_xup")) or k in ("stack_bull", "above_all", "chan_up", "tl_up", "dbl_bottom"):
        return "buy"
    if k.startswith(("rsi_gt", "px_below", "px_xdn", "ma_below", "ma_xdn")) or k in ("stack_bear", "below_all", "chan_dn", "tl_dn", "dbl_top"):
        return "sell"
    return None


def strategy_flags(df: pd.DataFrame):
    """-> (flags, sides) from the scanner's own detectors; sides[flag] = {'buy','sell'}."""
    from modules.signals import detect_all
    flags, sides = set(), {}
    try:
        sigs, _ = detect_all(df)
    except Exception:
        return flags, sides
    for sg in sigs:
        for fid, (_lab, (kind, val)) in STRATEGY_FILTERS.items():
            if sg.get(kind) == val:
                flags.add(fid)
                sides.setdefault(fid, set()).add("buy" if sg.get("direction") == "bullish" else "sell")
    return flags, sides
SHORT = {
    **{k: ("RSI>" if "gt" in k else "RSI<") + k[-2:] for k in RSI_FILTERS},
    **{f"px_above_{n}": f"Px>EMA{n}" for n in EMA_LENS}, **{f"px_below_{n}": f"Px<EMA{n}" for n in EMA_LENS},
    **{f"px_xup_{n}": f"Px↑EMA{n}" for n in EMA_LENS}, **{f"px_xdn_{n}": f"Px↓EMA{n}" for n in EMA_LENS},
    **{f"ma_above_{a}_{b}": f"{a}>{b}" for a, b in EMA_PAIRS}, **{f"ma_below_{a}_{b}": f"{a}<{b}" for a, b in EMA_PAIRS},
    **{f"ma_xup_{a}_{b}": f"{a}×{b}↑" for a, b in EMA_PAIRS}, **{f"ma_xdn_{a}_{b}": f"{a}×{b}↓" for a, b in EMA_PAIRS},
    "stack_bull": "Stack↑", "stack_bear": "Stack↓", "above_all": "فوق EMAs", "below_all": "تحت EMAs",
    "chan_up": "Channel↑", "chan_dn": "Channel↓", "tl_up": "Trendline↑", "tl_dn": "Trendline↓",
    "dbl_top": "Double Top", "dbl_bottom": "Double Bottom",
}
SHORT.update({k: v[0].split(" (")[0] for k, v in STRATEGY_FILTERS.items()})
CROSS_LOOKBACK = 3  # a cross counts if it happened within the last N candles


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    """Wilder's RSI."""
    d = close.diff()
    up, dn = d.clip(lower=0), (-d).clip(lower=0)
    au, ad = up.ewm(alpha=1 / n, adjust=False).mean(), dn.ewm(alpha=1 / n, adjust=False).mean()
    rs = au / ad.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.where(ad != 0, 100.0).fillna(50.0)


def _crossed_up(a: pd.Series, b: pd.Series, look: int = CROSS_LOOKBACK) -> bool:
    d = (a - b).values
    for i in range(len(d) - look, len(d)):
        if i >= 1 and d[i - 1] <= 0 < d[i]:
            return True
    return False


def _double_top(df) -> bool:
    zz = zigzag(df)
    if len(zz) < 3 or [k for _, _, k in zz[-3:]] != ["H", "L", "H"]:
        return False
    (_, h1, _), (_, lo, _), (i2, h2, _) = zz[-3:]
    atr = float(atr_series(df).iloc[i2])
    price = float(df["close"].iloc[-1])
    return (abs(h1 - h2) <= max(0.5 * atr, 0.004 * h2) and min(h1, h2) - lo >= 1.5 * atr
            and price < h2 and len(df) - 1 - i2 <= 30 and price > lo - 3 * atr)


def _channel_break(df, n: int = 50) -> tuple[bool, bool]:
    """Linear-regression channel (+-2 sigma) of the last n closes; True when the
    close has just broken out of it (within the last 2 candles)."""
    if len(df) < n + 5:
        return False, False
    c = df["close"].values
    x = np.arange(n)
    ys = c[-n - 3:-3]                      # fit on the window BEFORE the latest 3 candles
    k, b = np.polyfit(x, ys, 1)
    sig = float(np.std(ys - (k * x + b)))
    if sig <= 0:
        return False, False
    fit = lambda i: k * (n - 1 + i) + b    # i = 1..3 candles after the window
    up = c[-1] > fit(3) + 2 * sig and c[-4] <= fit(0) + 2 * sig
    dn = c[-1] < fit(3) - 2 * sig and c[-4] >= fit(0) - 2 * sig
    return bool(up), bool(dn)


def _trendline_break(df) -> tuple[bool, bool]:
    """(down-trend line broken UP, up-trend line broken DOWN) using the last two
    swing highs / lows; the break must be fresh (within the last 3 candles)."""
    piv = fractal_pivots(df, 3)
    c = df["close"].values
    last = len(df) - 1
    up_break = dn_break = False
    highs = [(i, p) for i, p, k in piv if k == "H"][-2:]
    lows = [(i, p) for i, p, k in piv if k == "L"][-2:]
    if len(highs) == 2 and highs[1][1] < highs[0][1] and last - highs[1][0] >= 4:
        (i1, p1), (i2, p2) = highs; m = (p2 - p1) / (i2 - i1); line = lambda i: p2 + m * (i - i2)
        up_break = c[-1] > line(last) and c[-1 - CROSS_LOOKBACK] <= line(last - CROSS_LOOKBACK)
    if len(lows) == 2 and lows[1][1] > lows[0][1] and last - lows[1][0] >= 4:
        (i1, p1), (i2, p2) = lows; m = (p2 - p1) / (i2 - i1); line = lambda i: p2 + m * (i - i2)
        dn_break = c[-1] < line(last) and c[-1 - CROSS_LOOKBACK] >= line(last - CROSS_LOOKBACK)
    return bool(up_break), bool(dn_break)


def features(df: pd.DataFrame, look: int = CROSS_LOOKBACK) -> dict:
    """-> {'rsi': float, 'flags': set(filter ids)} for one symbol/timeframe."""
    if df is None or len(df) < 60:
        return {"rsi": None, "flags": set()}
    df = df.reset_index(drop=True)
    c = df["close"]
    r = float(rsi(c).iloc[-1])
    e = {n: ema(c, n) for n in EMA_LENS if n < len(c) - 5}
    f = set()
    for lim in (70, 80, 90):
        if r > lim: f.add(f"rsi_gt{lim}")
    for lim in (30, 20, 10):
        if r < lim: f.add(f"rsi_lt{lim}")
    last = float(c.iloc[-1])
    for n, en in e.items():
        v = float(en.iloc[-1])
        f.add(f"px_above_{n}" if last > v else f"px_below_{n}")
        if _crossed_up(c, en, look): f.add(f"px_xup_{n}")
        if _crossed_up(en, c, look): f.add(f"px_xdn_{n}")
    for a_, b_ in EMA_PAIRS:
        if a_ in e and b_ in e:
            f.add(f"ma_above_{a_}_{b_}" if float(e[a_].iloc[-1]) > float(e[b_].iloc[-1]) else f"ma_below_{a_}_{b_}")
            if _crossed_up(e[a_], e[b_], look): f.add(f"ma_xup_{a_}_{b_}")
            if _crossed_up(e[b_], e[a_], look): f.add(f"ma_xdn_{a_}_{b_}")
    v9, v20, v50 = (float(e[n].iloc[-1]) for n in (9, 20, 50))
    if last > v9 > v20 > v50: f.add("stack_bull")
    if last < v9 < v20 < v50: f.add("stack_bear")
    if last > max(v9, v20, v50): f.add("above_all")
    if last < min(v9, v20, v50): f.add("below_all")
    cu, cd = _channel_break(df)
    if cu: f.add("chan_up")
    if cd: f.add("chan_dn")
    tu, td = _trendline_break(df)
    if tu: f.add("tl_up")
    if td: f.add("tl_dn")
    if _double_top(df): f.add("dbl_top")
    if _double_top(invert(df)): f.add("dbl_bottom")
    return {"rsi": r, "flags": f}


def mini_chart_svg(df: pd.DataFrame, bars: int = 60, w: int = 300, h: int = 150) -> str:
    """Candles + EMA 9/21/50 + VWAP as an <img> data URI (Streamlit-safe)."""
    d = df.tail(bars).reset_index(drop=True)
    if len(d) < 10:
        return ""
    full = df["close"]
    em = {n: ema(full, n).tail(bars).values for n in (9, 21, 50)}
    tp = (d["high"] + d["low"] + d["close"]) / 3
    vol = d["volume"].replace(0, np.nan)
    vw = ((tp * vol).cumsum() / vol.cumsum()).bfill().values
    lo = float(min(d["low"].min(), *(np.nanmin(v) for v in em.values()), np.nanmin(vw)))
    hi = float(max(d["high"].max(), *(np.nanmax(v) for v in em.values()), np.nanmax(vw)))
    # keep the plot focused on price: clip indicator-driven extremes to 15% beyond candles
    clo, chi = float(d["low"].min()), float(d["high"].max()); pad = (chi - clo) * 0.15 or 1
    lo, hi = max(lo, clo - pad), min(hi, chi + pad)
    span = (hi - lo) or 1.0
    n = len(d); step = (w - 8) / n; bw = max(1.0, step * 0.62)
    y = lambda v: round(h - 4 - (min(max(v, lo), hi) - lo) / span * (h - 8), 1)
    x = lambda i: round(4 + step * (i + .5), 1)
    parts = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'><rect width='{w}' height='{h}' fill='#0b0e11'/>"]
    for i, (o, hh, ll, cc) in enumerate(zip(d["open"], d["high"], d["low"], d["close"])):
        col = "#0ecb81" if cc >= o else "#f6465d"
        parts.append(f"<line x1='{x(i)}' x2='{x(i)}' y1='{y(hh)}' y2='{y(ll)}' stroke='{col}' stroke-width='1'/>"
                     f"<rect x='{round(x(i) - bw / 2, 1)}' y='{min(y(o), y(cc))}' width='{round(bw, 1)}' height='{max(1.0, abs(y(o) - y(cc)))}' fill='{col}'/>")
    for arr, col, dash in ((em[9], "#f0b90b", ""), (em[21], "#4aa3ff", ""), (em[50], "#b57cff", ""), (vw, "#e6e6e6", "3 2")):
        pts = " ".join(f"{x(i)},{y(v)}" for i, v in enumerate(arr))
        parts.append(f"<polyline fill='none' stroke='{col}' stroke-width='1.1' {'stroke-dasharray=' + chr(39) + dash + chr(39) if dash else ''} points='{pts}'/>")
    parts.append("</svg>")
    return "data:image/svg+xml;base64," + base64.b64encode("".join(parts).encode()).decode()
