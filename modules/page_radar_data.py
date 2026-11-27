"""Radar data layer: chart-scan data, filters' pass/hit tests, closes and constants. Split from page_radar.py (M7, 500-line rule)."""
import time

import pandas as pd
import streamlit as st

from modules.i18n import L
from modules.page_kit import rt
from modules.page_bg import _peer_frames, _peers_for
from modules.scorer import scan_symbol, fetch_tfs
from modules.market_cache import fetch_frames
from modules.chart_scan import (features as cs_features, match_filters, mini_chart_svg, move_flags, strategy_flags)


_CS_TFS = ["1m", "5m", "13m", "15m", "30m", "1h", "2h", "3h", "4h", "6h", "7h", "8h", "12h", "1d", "3d", "1w", "1mo"]


def _screen_cols(df):
    """Finviz-style screener numbers for one candle frame (Radar > Screener): last-candle and 20-bar change, volume vs its
    20-bar average, ATR as % of price, trend vs EMA 20/50. Plain arithmetic on the candles already downloaded."""
    import numpy as np
    c, h, l, v = (df[k].astype(float) for k in ("close", "high", "low", "volume"))
    last, prev = float(c.iloc[-1]), float(c.iloc[-2])
    tr = np.maximum(h - l, np.maximum((h - c.shift()).abs(), (l - c.shift()).abs()))
    e20, e50 = float(c.ewm(span=20, adjust=False).mean().iloc[-1]), float(c.ewm(span=50, adjust=False).mean().iloc[-1])
    va = float(v.iloc[-21:-1].mean() or 0)
    return {"chg": round((last / prev - 1) * 100, 2) if prev else None,
            "chg20": round((last / float(c.iloc[-21]) - 1) * 100, 2) if len(c) > 21 and float(c.iloc[-21]) else None,
            "volx": round(float(v.iloc[-1]) / va, 2) if va > 0 else None,
            "atrp": round(float(tr.iloc[-14:].mean()) / last * 100, 2) if last else None,
            "trend": "up" if last > e20 > e50 else "down" if last < e20 < e50 else "mixed"}


from modules import chart_explain as _CX


@st.cache_data(ttl=300, show_spinner=False)
def _last_ts(df):
    """Open time of the last candle as 'MM-DD HH:MM' (UTC), or ''."""
    try:
        import pandas as _p
        v = df["time"].iloc[-1]
        t = _p.to_datetime(v, unit="ms", utc=True) if isinstance(v, (int, float)) or str(getattr(v, "dtype", "")).startswith("int") else _p.to_datetime(v, utc=True)
        return t.strftime("%m-%d %H:%M")
    except Exception:
        return ""


def _fv_with_ref(df, sym, ref_sym, ref_df):
    """Finviz-style metrics + beta / correlation against the reference symbol (none for the reference itself or when no reference is in the universe)."""
    from modules import fv_screen as _FV
    m = _FV.metrics(df)
    if m is not None and ref_df is not None and sym != ref_sym:
        m.update(_FV.relation(df, ref_df))
    return m


@st.cache_data(ttl=120, show_spinner=False)   # speed: every Radar rerun / page switch used to refetch all candles
def _plines_ms(df, pl):
    """Pattern lines in bar indices -> {pattern id: [[t0 ms, p0, t1 ms, p1], ...]} so the Radar's Workspace chart can draw them."""
    try:
        ts = pd.to_datetime(df.reset_index(drop=True)["time"])
        ms = lambda i: int(ts.iloc[int(i)].timestamp() * 1000)   # noqa: E731
        return {k: [[ms(a), float(p), ms(b), float(q)] for a, p, b, q in v] for k, v in (pl or {}).items()}
    except Exception:   # extra drawing data: never break the scan
        return {}


def _chart_scan_data(symbols: tuple, tf: str, look: int = 3):
    """-> {symbol: {'rsi', 'flags', 'svg', 'price'}} for one timeframe (cached 60 s)."""
    from modules import fv_screen as _FV
    from modules import radar_context as _RC
    frames, _errs = fetch_frames(list(symbols), [tf], limit=260, workers=8)
    pfr = _peer_frames(symbols, tf)
    out = {}
    _ref_sym = next((x for x in ("BTC-USDT", "BTC-USDT-SWAP", "HL:xyz:SP500", "Y:^GSPC", "HL:BTC") if (frames.get(x) or {}).get(tf) is not None), None)   # beta / correlation reference: BTC for crypto, the S&P 500 for TradFi
    _ref_df = (frames.get(_ref_sym) or {}).get(tf) if _ref_sym else None
    for sym in symbols:
        df = (frames.get(sym) or {}).get(tf)
        if df is None or len(df) < 60:
            continue
        f = cs_features(df, look)
        sflags, ssides = strategy_flags(df, _peers_for(sym, tf, pfr))
        flags = sorted(f["flags"] | sflags | move_flags(df))
        try:
            expl = _CX.explain_both(df, flags)   # hover text (both languages, this result is cached): chart pattern, candle psychology, EMAs
        except Exception:
            expl = {}
        out[sym] = {"plines": _plines_ms(df, f.get("plines")), "rsi": f["rsi"], "regime": f.get("regime"), "flags": flags, "explain": expl, "sides": {k: sorted(v) for k, v in ssides.items()}, "svg": mini_chart_svg(df, lines=f.get("lines")), "ctx": _RC.context(df), "price": float(df["close"].iloc[-1]),
                    "t": time.time(), "ts": _last_ts(df), "fv": _fv_with_ref(df, sym, _ref_sym, _ref_df), "cn": sorted(_FV.candle_set(df)), **_screen_cols(df)}
    return out


_CS_KEY = {"1m": "1m", "5m": "1m", "15m": "1m", "30m": "1h", "1h": "1h", "1d": "1d", "1w": "1w", "4h": "1h",
           "13m": "13m", "2h": "2h", "3h": "3h", "6h": "6h", "7h": "7h", "8h": "8h", "12h": "12h", "3d": "3d", "1mo": "1mo"}   # scorer knows 1m/1h/1d/1w; the rest borrow the nearest


@st.cache_data(ttl=120, show_spinner=False)
def _cs_result(sym: str, tf: str):
    """Full scanner result for one chart (signals, higher-timeframe view, scenarios) so it can be explained in Arabic."""
    key = _CS_KEY.get(tf, "1h")
    frames, _e = fetch_frames([sym], sorted({tf, key} | set(fetch_tfs(key))))
    fr = dict(frames.get(sym) or {})
    if tf not in fr:
        return None
    fr[key] = fr[tf]
    r = scan_symbol(sym, fr, key, peers=_peers_for(sym, tf, _peer_frames([sym], tf)))
    r["timeframe"] = tf
    return r




_LADDER = {"1m": ("1h", "15m"), "3m": ("1h", "15m"), "5m": ("4h", "1h"), "13m": ("4h", "1h"), "15m": ("4h", "1h"), "30m": ("1d", "4h"),
           "1h": ("1d", "4h"), "2h": ("1w", "1d"), "3h": ("1w", "1d"), "4h": ("1w", "1d"), "6h": ("1w", "1d"), "8h": ("1w", "1d"),
           "12h": ("1w", "1d"), "1d": ("1w",), "3d": ("1w",)}   # Elder's triple screen: each step ~4-6x the one below


@st.cache_data(ttl=600, show_spinner=False)
def _htf_trend(symbols: tuple, tf: str):
    """Trend per symbol on a higher timeframe for the hover ladder: up (close > EMA 20 > EMA 50), down, or mixed."""
    frames, _e = fetch_frames(list(symbols), [tf], limit=120, workers=8)
    out = {}
    for s in symbols:
        df = (frames.get(s) or {}).get(tf)
        if df is not None and len(df) >= 50:
            c = df["close"].astype(float)
            last, e20, e50 = float(c.iloc[-1]), float(c.ewm(span=20, adjust=False).mean().iloc[-1]), float(c.ewm(span=50, adjust=False).mean().iloc[-1])
            out[s] = "up" if last > e20 > e50 else "down" if last < e20 < e50 else "mixed"
    return out


_TREND_AR = {"up": "صاعد ↑", "down": "هابط ↓", "mixed": "مختلط ↔"}


_TREND_EN = {"up": "Up ↑", "down": "Down ↓", "mixed": "Mixed ↔"}


@st.cache_data(ttl=300, show_spinner=False)
def _radar_closes(symbols: tuple, tf: str = "1h"):
    """Close prices of the Radar universe on one timeframe (one download, cached 5 min) for Performance / Correlation."""
    import pandas as _pd
    frames, _e = fetch_frames(list(symbols), [tf], limit=260)
    cols = {}
    for s in symbols:
        df = (frames.get(s) or {}).get(tf)
        if df is not None and len(df) > 30:
            t = df["time"]
            t = _pd.to_datetime(t, unit="ms") if _pd.api.types.is_numeric_dtype(t) else _pd.to_datetime(t)
            cols[s] = _pd.Series(df["close"].astype(float).values, index=t.values)
    return _pd.DataFrame(cols).sort_index()   # aligned on candle time, so returns compare the same hours


@st.cache_data(ttl=300, show_spinner=False)
def _fv_frames(symbols: tuple, tf: str):
    """Candle frames of the Radar universe on one timeframe (up to 300 bars, cached 5 min) for the Finviz-style screener and Similar charts."""
    frames, _e = fetch_frames(list(symbols), [tf], limit=300)
    return {s: f[tf] for s, f in frames.items() if f.get(tf) is not None and len(f[tf]) >= 30}


def _radar_hits(d, f):
    """(conditions met, conditions chosen) for one chart: indicator / pattern / strategy flags plus the Finviz-style technical lists."""
    from modules import fv_screen as _FV
    hits = sum(1 for k in f["sel"] if match_filters(d, [k], f["want"], False))
    if f["fv"] and d.get("fv"):
        ctx = {"candles": set(d.get("cn", ())), "flags": set(d["flags"])}
        hits += sum(1 for k, c in f["fv"].items() if _FV.test(k, c, d["fv"], ctx))
    return hits, len(f["sel"]) + len(f["fv"])


def _radar_pass(d, f):
    if f.get("regime") and d.get("regime") not in f["regime"]:   # market-regime filter (Radar panel): symbols in another regime drop out
        return False
    h, n = _radar_hits(d, f)
    if not n:
        return match_filters(d, [], f["want"], False)
    return h > 0 if f["any"] else h == n


def _radar_symbols(f):
    """Symbols of the universe that pass the shared panel (all of them when no filter is set). Every Radar view uses this, so the filters work everywhere."""
    if not (f["sel"] or f["fv"] or f["want"]):
        return list(rt().SCAN_SYMBOLS)
    data = _radar_data(f)
    return [s_ for s_, d_ in (data or {}).items() if _radar_pass(d_, f)]


def _tf_bars(tf):
    """Candle length of a timeframe label in minutes (for the performance spans)."""
    import re as _re
    m = _re.match(r"(\d+)(m|h|d|w|mo)$", tf)
    n, u = (int(m.group(1)), m.group(2)) if m else (1, "h")
    return n * {"m": 1, "h": 60, "d": 1440, "w": 10080, "mo": 43200}[u]


def _radar_data(f):
    """Scan data of the universe on the panel's timeframe (cached), or None after a message."""
    try:
        with st.spinner(L("Loading the candles of every Radar symbol (the first load can take up to a minute; later loads are cached)")):
            return _chart_scan_data(tuple(rt().SCAN_SYMBOLS), f["tf"], f["look"])
    except Exception as e:
        st.warning(f"Could not load candles: {e}")
        return None


_PT_IND = {   # Radar flag -> the Workspace chart's indicator (its ƒx menu id) that draws it
    "st_elliott": "ew", "st_ew3": "ew", "sch_elliott": "ew", "st_harm": "harm", "sch_harmonic": "harm",
    "st_msb": "msb", "st_ob": "msb", "st_breaker": "msb", "st_mss": "msb", "st_mit": "msb", "st_unicorn": "msb", "sch_ict": "msb",
    "st_ote": "ote", "st_fib": "ote", "sch_fib": "ote", "st_fvg": "sig", "st_ifvg": "sig", "st_judas": "sig", "st_silver": "sig", "st_m2022": "sig", "st_pd": "sig",
    "st_smt": "smt", "sch_smt": "smt", "st_kzs": "kzs", "st_sessamd": "kz", "st_orb": "kz", "st_po3": "kz", "sch_session": "kz",
    "st_donch": "don", "st_turtle55": "don", "st_sma1040": "ma", "st_ma": "ma", "sch_trend": "don", "st_vwap": "vwap", "st_bvd": "bvd",
    "st_rsidiv": "rsi", "st_macddiv": "macd", "sch_mom": "rsi", "st_sweep": "ll", "sch_liq": "ll", "vol_2x": "volume", "vol_3x": "volume",
}


_PT_ORDER = ["ew", "harm", "msb", "ote", "sig", "smt", "kzs", "kz", "ll", "bvd", "don", "vwap", "ma", "rsi", "macd", "volume"]   # main tools first: point 1 opens by itself


_PT_SR = {"st_rect", "st_dbl", "st_crt", "st_wyck", "sch_level", "sch_rect", "sch_wyck", "dbl_top", "dbl_bottom", "chan_up", "chan_dn", "tl_up", "tl_dn"}
