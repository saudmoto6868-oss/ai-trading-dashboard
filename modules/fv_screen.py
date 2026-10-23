"""Finviz-style screener (owner 2026-10-23): the same drop-down lists as Finviz's Technical tab, computed from the candles the Radar already
loads, for any market in the Radar universe (crypto, gold, oil, FX, indices). Plus 'Find similar charts' (Finviz, Sep 2026): rank the symbols
(and past stretches) whose recent price path looks like a chosen one.

Pure functions on pandas frames (columns open, high, low, close, volume); nothing here fetches or trades. Everything is a DESCRIPTION of the
candles; a filter match is not a signal (the weekly lab says no detector passes the evidence gate yet).

Finviz lists reproduced (names as on finviz.com): Performance, Performance 2, Volatility, RSI (14), Gap, 20/50/200-Day Simple Moving Average,
Change, Change from Open, 20-Day / 50-Day / 52-Week High/Low, Pattern, Candlestick, Average True Range, Relative Volume. Not reproduced because
they do not exist for these markets: fundamentals, earnings, analyst, insider, short float, themes, shares, float.
"""
from __future__ import annotations

import math
import re

import numpy as np
import pandas as pd

# ---- metrics ---------------------------------------------------------------------------------------------------------------------------

PERIODS = [("Today", 1), ("Week", 5), ("Month", 21), ("Quarter", 63), ("Half-year", 126), ("Year", 252)]   # in bars; named as Finviz does when the timeframe is daily
PERIODS_AR = {"Today": "النهارده", "Week": "أسبوع", "Month": "شهر", "Quarter": "ربع سنة", "Half-year": "نص سنة", "Year": "سنة"}


def _ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def rsi(close: pd.Series, n: int = 14) -> float | None:
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    v = 100 - 100 / (1 + up / dn)   # a series with no down moves gives dn = 0 -> inf -> RSI 100 (not NaN)
    return None if v.empty or pd.isna(v.iloc[-1]) else float(v.iloc[-1])


def metrics(df: pd.DataFrame) -> dict | None:
    """One row of Finviz-style technical numbers from a candle frame (>= 30 bars). Percent values are in %; None when there is not enough history."""
    if df is None or len(df) < 30:
        return None
    o, h, l, c = (df[k].astype(float).reset_index(drop=True) for k in ("open", "high", "low", "close"))
    v = df["volume"].astype(float).reset_index(drop=True) if "volume" in df else pd.Series([0.0] * len(df))
    n = len(c); px = float(c.iloc[-1]); pc = float(c.iloc[-2])
    m = {"price": px, "chg": (px / pc - 1) * 100, "chg_open": (px / float(o.iloc[-1]) - 1) * 100 if o.iloc[-1] else 0.0,
         "gap": (float(o.iloc[-1]) / pc - 1) * 100 if pc else 0.0, "n": n}
    for name, k in PERIODS:
        m["perf_" + name] = (px / float(c.iloc[-1 - k]) - 1) * 100 if n > k and c.iloc[-1 - k] else None
    rng = (h - l) / c * 100
    m["vol_week"] = float(rng.tail(5).mean()); m["vol_month"] = float(rng.tail(21).mean())
    m["rsi"] = rsi(c)
    for p in (20, 50, 200):
        if n >= p:
            sm = c.rolling(p).mean(); m[f"sma{p}"] = float(sm.iloc[-1]); m[f"sma{p}_rel"] = (px / float(sm.iloc[-1]) - 1) * 100
            m[f"sma{p}_prev"] = float(sm.iloc[-2]); m[f"sma{p}_prev_px"] = pc
        else:
            m[f"sma{p}"] = None
    for tag, k in (("20d", 20), ("50d", 50), ("52w", 252), ("all", n)):
        if n >= min(k, 30):
            w = slice(max(0, n - k), n); hi, lo = float(h.iloc[w].max()), float(l.iloc[w].min())
            m[f"hi_{tag}"] = hi; m[f"lo_{tag}"] = lo
            m[f"from_hi_{tag}"] = (px / hi - 1) * 100; m[f"from_lo_{tag}"] = (px / lo - 1) * 100
            m[f"newhi_{tag}"] = float(h.iloc[-1]) >= float(h.iloc[max(0, n - k):n - 1].max()) if n > 1 else False
            m[f"newlo_{tag}"] = float(l.iloc[-1]) <= float(l.iloc[max(0, n - k):n - 1].min()) if n > 1 else False
    pcl = c.shift(1); tr = pd.concat([h - l, (h - pcl).abs(), (l - pcl).abs()], axis=1).max(axis=1)
    m["atr"] = float(tr.ewm(alpha=1 / 14, adjust=False).mean().iloc[-1]); m["atr_pct"] = m["atr"] / px * 100
    avg = float(v.iloc[-21:-1].mean()) if n > 21 else 0.0
    m["relvol"] = float(v.iloc[-1]) / avg if avg > 0 else None; m["avgvol"] = avg
    return m


# ---- filters ---------------------------------------------------------------------------------------------------------------------------
# a filter = (key, group, English name, Arabic name, [(option code, English label, Arabic label)]); `test(key, code, m, ctx)` decides one symbol

def _perf_opts():
    out = []
    for name, _k in PERIODS:
        ar = PERIODS_AR[name]
        out += [(f"{name}|up", f"{name} Up", f"{ar} صاعد"), (f"{name}|down", f"{name} Down", f"{ar} هابط")]
        out += [(f"{name}|+{x}", f"{name} +{x}%", f"{ar} +{x}%") for x in (5, 10, 20, 50)] + [(f"{name}|-{x}", f"{name} -{x}%", f"{ar} -{x}%") for x in (5, 10, 20, 50)]
    return out


def _sma_opts(p):
    o = [("below", f"Price below SMA{p}", f"السعر تحت SMA{p}"), ("below10", f"Price 10% below SMA{p}", f"السعر أقل بـ 10% من SMA{p}"),
         ("below20", f"Price 20% below SMA{p}", f"السعر أقل بـ 20% من SMA{p}"), ("above", f"Price above SMA{p}", f"السعر فوق SMA{p}"),
         ("above10", f"Price 10% above SMA{p}", f"السعر أعلى بـ 10% من SMA{p}"), ("above20", f"Price 20% above SMA{p}", f"السعر أعلى بـ 20% من SMA{p}"),
         ("cross", f"Price crossed SMA{p}", f"السعر قطع SMA{p}"), ("crossup", f"Price crossed SMA{p} above", f"السعر قطع SMA{p} لفوق"),
         ("crossdn", f"Price crossed SMA{p} below", f"السعر قطع SMA{p} لتحت")]
    for q in (50, 200):
        if q > p:
            o += [(f"sma{q}a", f"SMA{p} above SMA{q}", f"SMA{p} فوق SMA{q}"), (f"sma{q}b", f"SMA{p} below SMA{q}", f"SMA{p} تحت SMA{q}"),
                  (f"sma{q}xa", f"SMA{p} crossed above SMA{q}", f"SMA{p} قطع SMA{q} لفوق"), (f"sma{q}xb", f"SMA{p} crossed below SMA{q}", f"SMA{p} قطع SMA{q} لتحت")]
    return o


def _hl_opts(tag, name):
    o = [("newhi", f"{name} New High", f"{name} قمة جديدة"), ("newlo", f"{name} New Low", f"{name} قاع جديد")]
    o += [(f"hi{x}", f"{x}% or more below High", f"أقل من القمة بـ {x}% أو أكتر") for x in (5, 10, 20, 30, 50)]
    o += [(f"hi0_{x}", f"0-{x}% below High", f"0-{x}% تحت القمة") for x in (3, 5, 10)]
    o += [(f"lo{x}", f"{x}% or more above Low", f"أعلى من القاع بـ {x}% أو أكتر") for x in (5, 10, 20, 30, 50, 100)]
    o += [(f"lo0_{x}", f"0-{x}% above Low", f"0-{x}% فوق القاع") for x in (3, 5, 10)]
    return o


def _chg_opts():
    o = [("up", "Up", "صاعد"), ("down", "Down", "هابط")]
    o += [(f"+{x}", f"Up {x}%", f"صاعد {x}%") for x in (1, 2, 3, 5, 10, 15, 20)] + [(f"-{x}", f"Down {x}%", f"هابط {x}%") for x in (1, 2, 3, 5, 10, 15, 20)]
    return o


CANDLES = [("doji", "Doji", "دوجي"), ("hammer", "Hammer", "مطرقة"), ("hanging_man", "Hanging Man", "الرجل المشنوق"), ("inverted_hammer", "Inverted Hammer", "مطرقة مقلوبة"),
           ("shooting_star", "Shooting Star", "شهاب"), ("marubozu", "Marubozu", "ماروبوزو"), ("engulfing", "Engulfing", "ابتلاع"), ("harami", "Harami", "هارامي"),
           ("piercing", "Piercing Line", "خط الاختراق"), ("dark_cloud", "Dark Cloud Cover", "الغطاء السحابي المظلم"), ("morning_star", "Morning Star", "نجمة الصباح"),
           ("evening_star", "Evening Star", "نجمة المساء"), ("three_white", "Three White Soldiers", "3 جنود بيض"), ("three_black", "Three Black Crows", "3 غربان سود")]

FILTERS = [
    ("perf", "Technical", "Performance", "الأداء", _perf_opts()),
    ("perf2", "Technical", "Performance 2", "الأداء 2", _perf_opts()),
    ("vol", "Technical", "Volatility", "التقلب", [(f"week{x}", f"Week over {x}%", f"الأسبوع أكتر من {x}%") for x in (1, 2, 3, 5, 7, 10)] +
     [(f"month{x}", f"Month over {x}%", f"الشهر أكتر من {x}%") for x in (1, 2, 3, 4, 5, 8)]),
    ("rsi", "Technical", "RSI (14)", "RSI (14)", [("ob90", "Overbought (90)", "تشبع شراء (90)"), ("ob80", "Overbought (80)", "تشبع شراء (80)"), ("ob70", "Overbought (70)", "تشبع شراء (70)"),
     ("ob60", "Overbought (60)", "تشبع شراء (60)"), ("os40", "Oversold (40)", "تشبع بيع (40)"), ("os30", "Oversold (30)", "تشبع بيع (30)"), ("os20", "Oversold (20)", "تشبع بيع (20)"),
     ("os10", "Oversold (10)", "تشبع بيع (10)"), ("nob", "Not overbought (<60)", "مش متشبع شراء (<60)"), ("nos", "Not oversold (>40)", "مش متشبع بيع (>40)")]),
    ("gap", "Technical", "Gap", "الفجوة", [("up", "Up", "فجوة لفوق"), ("down", "Down", "فجوة لتحت")] + [(f"up{x}", f"Up {x}%", f"لفوق {x}%") for x in (1, 2, 5)] + [(f"dn{x}", f"Down {x}%", f"لتحت {x}%") for x in (1, 2, 5)]),
    ("sma20", "Technical", "20-Day Simple Moving Average", "المتوسط البسيط 20", _sma_opts(20)),
    ("sma50", "Technical", "50-Day Simple Moving Average", "المتوسط البسيط 50", _sma_opts(50)),
    ("sma200", "Technical", "200-Day Simple Moving Average", "المتوسط البسيط 200", _sma_opts(200)),
    ("chg", "Technical", "Change", "التغير", _chg_opts()),
    ("chgopen", "Technical", "Change from Open", "التغير من الافتتاح", _chg_opts()),
    ("hl20", "Technical", "20-Day High/Low", "أعلى/أقل 20 يوم", _hl_opts("20d", "20-Day")),
    ("hl50", "Technical", "50-Day High/Low", "أعلى/أقل 50 يوم", _hl_opts("50d", "50-Day")),
    ("hl52", "Technical", "52-Week High/Low", "أعلى/أقل 52 أسبوع", _hl_opts("52w", "52-Week")),
    ("hlall", "Technical", "All-Time High/Low", "أعلى/أقل في كل التاريخ المحمّل", _hl_opts("all", "All-Time")),
    ("pattern", "Technical", "Pattern", "النموذج", []),          # options come from modules/patterns.py (chart patterns), filled by the caller
    ("candle", "Technical", "Candlestick", "الشمعة", [(k, e, a) for k, e, a in CANDLES]),
    ("atr", "Technical", "Average True Range", "متوسط المدى الحقيقي ATR", [(f"o{x}", f"Over {x}% of price", f"أكتر من {x}% من السعر") for x in (0.5, 1, 2, 3, 5, 10)] +
     [(f"u{x}", f"Under {x}% of price", f"أقل من {x}% من السعر") for x in (0.5, 1, 2, 3)]),
    ("relvol", "Technical", "Relative Volume", "الفوليوم النسبي", [(f"o{x}", f"Over {x}", f"أكتر من {x}") for x in (10, 5, 3, 2, 1.5, 1)] + [(f"u{x}", f"Under {x}", f"أقل من {x}") for x in (2, 1, 0.75, 0.5, 0.25)]),
]
FILTER_KEYS = [f[0] for f in FILTERS]


def _cmp_pct(val, code):
    """'up' / 'down' / '+5' / '-10' against a percent value."""
    if val is None:
        return False
    if code == "up":
        return val > 0
    if code == "down":
        return val < 0
    t = float(code)
    return val >= t if t > 0 else val <= t


def test(key: str, code: str, m: dict, ctx: dict | None = None) -> bool:
    """Does one symbol (metrics m) pass filter `key` = option `code`? ctx = {'flags': set of chart-pattern ids, 'candles': set of candle ids}."""
    ctx = ctx or {}
    if key in ("perf", "perf2"):
        name, c = code.split("|"); return _cmp_pct(m.get("perf_" + name), c)
    if key == "vol":
        w, x = (("vol_week", float(code[4:])) if code.startswith("week") else ("vol_month", float(code[5:]))); return m[w] > x
    if key == "rsi":
        r = m.get("rsi"); t = {"ob": ">=", "os": "<="}
        if r is None:
            return False
        if code == "nob":
            return r < 60
        if code == "nos":
            return r > 40
        x = float(code[2:]); return r >= x if code.startswith("ob") else r <= x
    if key == "gap":
        g = m["gap"]; return g > 0 if code == "up" else g < 0 if code == "down" else g >= float(code[2:]) if code.startswith("up") else g <= -float(code[2:])
    if key in ("sma20", "sma50", "sma200"):
        p = int(key[3:]); rel = m.get(f"sma{p}_rel")
        if rel is None:
            return False
        if code == "below": return rel < 0
        if code == "above": return rel > 0
        if code in ("below10", "below20"): return rel <= -float(code[5:])
        if code in ("above10", "above20"): return rel >= float(code[5:])
        if code in ("cross", "crossup", "crossdn"):
            s0, s1, p0, p1 = m[f"sma{p}_prev"], m[f"sma{p}"], m[f"sma{p}_prev_px"], m["price"]; up = p0 <= s0 and p1 > s1; dn = p0 >= s0 and p1 < s1
            return up if code == "crossup" else dn if code == "crossdn" else (up or dn)
        mt = re.match(r"sma(\d+)(x?)([ab])$", code)
        q, crossed, above = int(mt.group(1)), mt.group(2) == "x", mt.group(3) == "a"
        sq, sp = m.get(f"sma{q}"), m.get(f"sma{p}")
        if sq is None or sp is None:
            return False
        if not crossed:
            return sp > sq if above else sp < sq
        sq0, sp0 = m.get(f"sma{q}_prev"), m.get(f"sma{p}_prev")
        return sp0 is not None and sq0 is not None and ((sp0 <= sq0 and sp > sq) if above else (sp0 >= sq0 and sp < sq))
    if key in ("chg", "chgopen"):
        return _cmp_pct(m["chg" if key == "chg" else "chg_open"], code)
    if key in ("hl20", "hl50", "hl52", "hlall"):
        tag = {"hl20": "20d", "hl50": "50d", "hl52": "52w", "hlall": "all"}[key]
        if f"hi_{tag}" not in m:
            return False
        if code == "newhi": return bool(m[f"newhi_{tag}"])
        if code == "newlo": return bool(m[f"newlo_{tag}"])
        fh, fl = m[f"from_hi_{tag}"], m[f"from_lo_{tag}"]
        if code.startswith("hi0_"): return -float(code[4:]) <= fh <= 0
        if code.startswith("hi"): return fh <= -float(code[2:])
        if code.startswith("lo0_"): return 0 <= fl <= float(code[4:])
        return fl >= float(code[2:])
    if key == "pattern":
        return code in ctx.get("flags", ())
    if key == "candle":
        return code in ctx.get("candles", ())
    if key == "atr":
        x = float(code[1:]); return m["atr_pct"] > x if code[0] == "o" else m["atr_pct"] < x
    if key == "relvol":
        r = m.get("relvol")
        if r is None:
            return False
        x = float(code[1:]); return r > x if code[0] == "o" else r < x
    raise KeyError(key)


def apply(selected: dict, rows: dict, ctxs: dict | None = None) -> list:
    """selected = {filter key: option code}; rows = {symbol: metrics}; ctxs = {symbol: ctx}. -> symbols passing ALL selected filters (Finviz: filters are ANDed)."""
    ctxs = ctxs or {}
    return [s for s, m in rows.items() if m and all(test(k, c, m, ctxs.get(s)) for k, c in selected.items() if c)]


# ---- find similar charts -----------------------------------------------------------------------------------------------------------------

def _znorm(x):
    x = np.asarray(x, float); sd = x.std()
    return (x - x.mean()) / sd if sd > 0 else None


def similar(frames: dict, target: str, window: int = 40, ahead: int = 10, top: int = 12) -> list:
    """Find similar charts: Pearson correlation between the target's last `window` closes and (a) the last `window` closes of every other
    symbol and (b) every earlier stretch of any symbol (best offset per symbol, not overlapping the target's own present).
    -> [{symbol, corr (best stretch; inflated by picking the best of ~N windows, so compare with corr_now), corr_now (the same symbol's LAST window), offset (bars ago the match ended; 0 = now), ret (% over the matched window), after (% over the next `ahead` bars, None if not yet)}].
    'after' is HISTORY of what followed that look-alike, a description, never a forecast."""
    base = frames.get(target)
    if base is None or len(base) < window + 5:
        return []
    tz = _znorm(base["close"].astype(float).tail(window).values)
    if tz is None:
        return []
    out = []
    for sym, df in frames.items():
        c = df["close"].astype(float).values; n = len(c)
        if n < window + 2:
            continue
        best, now_r = None, None
        for end in range(n, window - 1, -1):                       # end = exclusive end index of the stretch
            if sym == target and end > n - window:                  # the target's own present (and overlaps of it) are not "similar"
                continue
            z = _znorm(c[end - window:end])
            if z is None:
                continue
            r = float(np.dot(tz, z) / window)
            if end == n:
                now_r = r
            if best is None or r > best[0]:
                best = (r, end)
        if best:
            r, end = best; seg = c[end - window:end]
            out.append({"symbol": sym, "corr": round(r, 3), "corr_now": None if now_r is None else round(now_r, 3), "offset": n - end, "ret": round((seg[-1] / seg[0] - 1) * 100, 2),
                        "after": round((c[end - 1 + ahead] / c[end - 1] - 1) * 100, 2) if end - 1 + ahead < n else None})
    return sorted(out, key=lambda x: -x["corr"])[:top]


_CANDLE_MAP = {"bull_engulf": "engulfing", "bear_engulf": "engulfing", "bull_marubozu": "marubozu", "bear_marubozu": "marubozu"}


def candle_set(df) -> set:
    """Finviz candlestick ids present on the LAST candle of the frame (detector: modules/chart_explain.candles)."""
    from modules import chart_explain as X
    return {_CANDLE_MAP.get(k, k) for k in X.candles(df)} & {c[0] for c in CANDLES}
