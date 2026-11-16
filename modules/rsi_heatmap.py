"""RSI Heatmap Intelligence: multi-timeframe momentum research on native feeds.

No CoinGlass dependency. Uses TIA's market catalogue and the shared candle cache.
Only closed candles are used; unavailable feeds remain explicit.
"""
from __future__ import annotations

import json
from pathlib import Path

from modules import rsi_ar as _AR

import pandas as pd
import streamlit as st

ASSET_CLASSES = (
    "Crypto", "Forex", "Metals", "Oil & Gas", "Indices", "Stocks", "Bonds",
    "Options", "Meme coins", "Egypt (EGX)", "Saudi (Tadawul)",
)
TIMEFRAMES = ("1m", "5m", "15m", "30m", "1h", "4h", "12h", "1d", "1w")
WARMUP_BARS = 250   # Wilder RSI converges after ~250 bars (StockCharts); fewer drifts from TradingView

# CoinGlass-style bands, top to bottom: (label, low, high, colour)
BANDS = (
    ("Overbought", 70, 100, "#e5484d"),
    ("Strong", 60, 70, "#f2a1a3"),
    ("Neutral", 40, 60, "#8b95a5"),
    ("Weak", 30, 40, "#8fd6b4"),
    ("Oversold", 0, 30, "#1f9d6b"),
)


def rsi_wilder(closes, period: int = 14):
    """Standard Wilder RSI: SMA seed followed by Wilder's recursive smoothing."""
    values = [float(x) for x in closes]
    if period < 2 or len(values) <= period:
        return None
    changes = [b - a for a, b in zip(values[:-1], values[1:])]
    gains = [max(x, 0.0) for x in changes]
    losses = [max(-x, 0.0) for x in changes]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(changes)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0 if avg_gain else 50.0
    return round(100.0 - 100.0 / (1.0 + avg_gain / avg_loss), 2)


def rsi_zone(value):
    if value is None:
        return "Unavailable"
    if value >= 70:
        return "Overbought"
    if value <= 30:
        return "Oversold"
    return "Neutral"


def rsi_band(value):
    """Five CoinGlass bands; boundaries belong to the outer band (70 = Overbought, 30 = Oversold)."""
    if value is None:
        return "Unavailable"
    v = float(value)
    if v >= 70:
        return "Overbought"
    if v >= 60:
        return "Strong"
    if v > 40:
        return "Neutral"
    if v > 30:
        return "Weak"
    return "Oversold"


def _short(symbol):
    s = str(symbol)
    for prefix in ("HL:xyz:", "HL:", "Y:", "FH:"):
        if s.startswith(prefix):
            s = s[len(prefix):]
    for suffix in ("-USDT-SWAP", "-USDT", "-USD", "=X", ".CA", ".SR"):
        if s.endswith(suffix):
            s = s[: -len(suffix)]
    return s


def _symbols(asset_class: str, limit: int):
    from modules.tia_intelligence import symbols_for_class
    catalog = symbols_for_class(asset_class, top=limit)
    return list(dict.fromkeys(catalog.get("symbols", [])))[:limit], catalog.get("note", "")


def _closed_frame(df):
    """Feed adapters return the newest candle too; exclude it to avoid intrabar repainting."""
    if df is None or len(df) < 2:
        return None
    closed = df.iloc[:-1].copy()
    if len(closed) < 15:
        return None
    return closed


def _measure(df):
    closed = _closed_frame(df)
    if closed is None or "close" not in closed:
        return None
    closes = pd.to_numeric(closed["close"], errors="coerce").dropna()
    if len(closes) < 15:
        return None
    values = closes.astype(float).tolist()
    rsi = rsi_wilder(values, 14)
    if rsi is None:
        return None
    ema9 = pd.Series(values).ewm(span=9, adjust=False).mean().iloc[-1]
    ema21 = pd.Series(values).ewm(span=21, adjust=False).mean().iloc[-1]
    trend = "Bullish" if ema9 > ema21 else "Bearish" if ema9 < ema21 else "Mixed"
    stamp = str(closed["time"].iloc[-1]) if "time" in closed else "—"
    return {"rsi": rsi, "zone": rsi_zone(rsi), "trend": trend,
            "price": float(values[-1]), "last_closed": stamp}


_CELL = {"Overbought": "background-color:#e5484d;color:#fff;font-weight:700",
         "Strong": "background-color:#f2a1a3;color:#2b1b1c",
         "Neutral": "background-color:#3a4455;color:#e8ecf2",
         "Weak": "background-color:#8fd6b4;color:#12291f",
         "Oversold": "background-color:#1f9d6b;color:#fff;font-weight:700"}


def _style_rsi(value):
    if value is None or value == "—" or (isinstance(value, float) and pd.isna(value)):
        return "color:#8993a4"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ""
    return _CELL[rsi_band(value)]


def _alignment(measures, timeframes):
    trends = [measures.get(tf, {}).get("trend") for tf in timeframes]
    trends = [x for x in trends if x in ("Bullish", "Bearish")]
    if not trends:
        return "Unavailable"
    if len(trends) != len(timeframes):
        return "Partial"
    if all(x == "Bullish" for x in trends):
        return "Bullish alignment"
    if all(x == "Bearish" for x in trends):
        return "Bearish alignment"
    return "Mixed"


_ALIGN_STYLE = {"Bullish alignment": "color:#1f9d6b;font-weight:700", "Bearish alignment": "color:#e5484d;font-weight:700"}
TF_SECONDS = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400, "12h": 43200, "1d": 86400, "1w": 604800}
_BOARD = Path(__file__).with_name("rsi_board.html")


@st.cache_data(ttl=60, show_spinner=False)
def _cached_flow(symbol):
    from modules.rsi_flow import fetch_flow
    return fetch_flow(symbol)


def _next_close_ms(last_closed, tf):
    """Close time of the candle now forming = open of the last closed candle + 2 bars (None when unknown)."""
    try:
        t = pd.Timestamp(last_closed)
        if t.year < 2000:
            return None
        t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
        return int(t.value // 1_000_000 + 2 * TF_SECONDS[tf] * 1000)
    except Exception:
        return None


def _extras(df):
    """RSI trail, ATR % and volume vs its 20-candle average on the map timeframe (closed candles)."""
    out = {"trail": [], "atr_pct": None, "vol_x": None}
    if df is None or len(df) < 20:
        return out
    from modules.rsi_setups import rsi_trail
    from modules.signals import atr_series
    try:
        out["trail"] = [round(x, 2) for x in rsi_trail(df["close"].tolist())]
        if {"high", "low"} <= set(df.columns):
            out["atr_pct"] = round(100 * float(atr_series(df).iloc[-1]) / float(df["close"].iloc[-1]), 2)
        if "volume" in df.columns:
            v = pd.to_numeric(df["volume"], errors="coerce")
            base = float(v.iloc[-21:-1].mean())
            out["vol_x"] = round(float(v.iloc[-1]) / base, 2) if base > 0 else None
    except Exception:
        pass
    return out


def _board_score(rec):
    if not rec:
        return -1
    plan = rec.get("plan") or {}
    return rec["conv"] + min(plan.get("rr", 0), 4) * 6 + (10 - 2 * rec["fresh"] if rec.get("fresh") is not None else 0)


def _candle_key(df):
    """Last closed candle time: the board only needs recomputing when a new candle closes."""
    try:
        return str(df["time"].iloc[-1])
    except Exception:
        return "?"


@st.cache_data(ttl=300, show_spinner=False)
def _cached_read(sym, candle, chart_tf, deep, _df, vote=0):
    """Strategy schools per symbol, cached per closed candle (Live refresh stops re-running all 9 schools)."""
    from modules.rsi_confluence import read_symbol
    from modules.rsi_setups import read_setup
    return read_symbol(_df, read_setup(_df), vote, deep)


def build_items(symbols, detail, setups, frames, chart_tf, timeframes, deep=True, use_flow=True):
    """One record per symbol for the board (pure apart from the cached flow fetch)."""
    from modules.rsi_confluence import derive_tags, read_symbol
    from modules.rsi_flow import FLOW_TOP_N, feed_of, flow_read
    closed = {s: _closed_frame((frames.get(s) or {}).get(chart_tf)) for s in symbols}
    recs = {}
    for s in symbols:
        try:
            recs[s] = _cached_read(s, _candle_key(closed[s]), chart_tf, deep, closed[s]) if deep else None
        except Exception:
            recs[s] = None
    flows = {}
    if use_flow:
        pick = [s for s in sorted(symbols, key=lambda s: _board_score(recs.get(s)), reverse=True)
                if setups.get(s) and feed_of(s)[0]][:FLOW_TOP_N]
        if pick:
            from concurrent.futures import ThreadPoolExecutor
            with st.spinner(f"Order flow for {len(pick)} symbols…"), ThreadPoolExecutor(4) as pool:
                flows = dict(zip(pick, pool.map(_cached_flow, pick)))
        for s, fl in flows.items():
            vote = flow_read(fl)["vote"]
            if deep and vote:
                try:
                    recs[s] = _cached_read(s, _candle_key(closed[s]), chart_tf, deep, closed[s], vote)
                except Exception:
                    pass
    top25 = set(sorted(recs, key=lambda s: _board_score(recs[s]), reverse=True)[:25])
    items = []
    for rank, s in enumerate(symbols, start=1):
        per_tf, setup, rec = detail.get(s) or {}, setups.get(s) or {}, recs.get(s)
        if not per_tf:
            continue
        m = per_tf.get(chart_tf)
        fl = flows.get(s)
        fr = flow_read(fl) if fl else None
        it = {"sym": _short(s), "full": s, "rank": rank,
              "price": next((per_tf[tf]["price"] for tf in timeframes if tf in per_tf), None),
              "rsi": {tf: (per_tf[tf]["rsi"] if tf in per_tf else None) for tf in timeframes},
              "rsi_map": m["rsi"] if m else None, "state": setup.get("state", "—"), "speed": setup.get("speed", ""),
              "regime": setup.get("regime", "—"), "next_close": _next_close_ms(m["last_closed"], chart_tf) if m else None,
              "flow": ({"buy": fr["parts"].get("buy_share"), "book": fr["parts"].get("imbalance"), "text": fr["text"]}
                       if fr else ({} if use_flow else None)),
              "verdict": setup.get("state", "—"), "dir": 0, "conv": None, "votes": None, "plan": None, "fresh": None}
        if rec:
            it.update({k: rec[k] for k in ("verdict", "dir", "conv", "bull", "bear", "bull_pct", "bear_pct", "fresh", "plan")})
            it["votes"] = {sc: {"v": v["vote"], "n": v["names"][:4]} for sc, v in rec["votes"].items()}
        it.update(_extras(closed.get(s)))
        it["phase"] = setup.get("phase", "")
        it["htf"] = {tf: (1 if per_tf[tf]["trend"] == "Bullish" else -1 if per_tf[tf]["trend"] == "Bearish" else 0)
                     for tf in timeframes if tf in per_tf}
        it["src"] = feed_of(s)[0] or ("yahoo" if s.startswith("Y:") else "other")
        it["tags"], it["urgent"] = derive_tags(it, chart_tf, timeframes)
        it.update(_detail(s, rec, closed.get(s), chart_tf, top25, setup))
        items.append(it)
    return items


def _sig_rows(rec, cap=12):
    """Arabic signal rows for the drawer: matching side first, then the rest (English data, Arabic text)."""
    from modules.arabic import signal_ar, tag_for
    from modules.rsi_confluence import school_of
    if not rec:
        return []
    side = rec.get("dir") or 0
    sigs = sorted(rec.get("signals", []), key=lambda s: (s.get("direction") == "bullish") != (side > 0))
    out = []
    for s in sigs[:cap]:
        try:
            name, detail = signal_ar(s, True)
        except Exception:
            name, detail = s.get("name", ""), ""
        t = tag_for(s, True)
        out.append({"school": school_of(s), "n": name, "d": str(detail)[:200], "v": 1 if s.get("direction") == "bullish" else -1,
                    "t": t[0], "c": t[1]})
    return out


def _detail(sym, rec, df, chart_tf, top25, setup):
    """Drawer + chart data: Arabic signal rows, harmonics / patterns, last 50 candles and nearest S/R levels."""
    out = {"sigs": _sig_rows(rec), "harm": (rec or {}).get("harm", []), "pats": (rec or {}).get("pats", []),
           "ohlc": [], "lv": []}
    if df is None or len(df) < 10 or "open" not in df:
        return out
    tail = df[["open", "high", "low", "close"]].tail(50).astype(float).round(8).values.tolist()
    out["ohlc"] = tail
    try:
        from modules.signals import sr_levels
        res, sup = sr_levels(df)
        last = float(df["close"].iloc[-1])
        out["lv"] = ([{"p": float(x), "k": "R"} for x in sorted(res) if x > last][:2]
                     + [{"p": float(x), "k": "S"} for x in sorted(sup, reverse=True) if x < last][:2])
    except Exception:
        out["lv"] = []
    return out


def board_html(items, chart_tf, timeframes):
    from modules.rsi_confluence import SCHOOLS, SHORT, TAGS
    pts = [i["rsi_map"] for i in items if i["rsi_map"] is not None]
    src = {}
    for i in items:
        src[i.get("src", "other")] = src.get(i.get("src", "other"), 0) + 1
    data = {"src": src, "flow_n": sum(1 for i in items if i.get("flow") and i["flow"].get("buy") is not None),
            "built": pd.Timestamp.now(tz="UTC").strftime("%H:%M:%S UTC"), "tags": list(TAGS),
            "tf": chart_tf, "timeframes": timeframes, "schools": list(SCHOOLS), "short": SHORT, "items": items,
            "avg": round(sum(pts) / len(pts), 2) if pts else None,
            "bands": [{"name": b[0], "lo": b[1], "hi": b[2], "c": b[3]} for b in BANDS],
            "ar": {"school": _AR.SCHOOL,
                   "verdict": _AR.VERDICT,
                   "phase": _AR.PHASE,
                   "tag": _AR.TAG,
                   "band": _AR.BAND,
                   "regime": _AR.REGIME}}
    blob = json.dumps(data, ensure_ascii=False, default=float).replace("</", "<\\/")
    return _BOARD.read_text(encoding="utf-8").replace("__DATA__", blob)


_HEADER_CSS = """<style>
.block-container{padding-top:2.2rem!important}
div[data-testid='stHorizontalBlock']:has(.rsi-hm-title){align-items:center;gap:6px;margin-bottom:-6px}
.rsi-hm-title{font-weight:800;font-size:15px;white-space:nowrap;letter-spacing:.2px}
.rsi-hm-title span{color:#f5a524;font-weight:600}
div[data-testid='stHorizontalBlock']:has(.rsi-hm-title) div[data-baseweb='select']>div{min-height:30px;height:30px;font-size:12px;
  border-radius:15px;background:#151a22;border-color:#2a3240}
div[data-testid='stHorizontalBlock']:has(.rsi-hm-title) div[data-baseweb='select'] svg{width:14px}
div[data-testid='stHorizontalBlock']:has(.rsi-hm-title) [data-testid='stButtonGroup'] button{min-height:26px;height:26px;padding:0 9px;
  font-size:11.5px;border-radius:13px}
div[data-testid='stHorizontalBlock']:has(.rsi-hm-title) [data-testid='stWidgetLabel'] p{font-size:11.5px}
div[data-testid='stHorizontalBlock']:has(.rsi-hm-title) label[data-baseweb='checkbox']{gap:4px}
</style>"""


def render():
    from modules.rsi_setups import read_setup
    st.markdown(_HEADER_CSS, unsafe_allow_html=True)
    f = st.columns([1.0, 1.05, 3.4, 0.95, 0.95, 0.5], gap="small", vertical_alignment="center")
    f[0].markdown("<div class='rsi-hm-title'>RSI Heatmap</div>", unsafe_allow_html=True)
    asset_class = f[1].selectbox("السوق", ASSET_CLASSES, index=0, key="rsi_hm_market", label_visibility="collapsed")
    picked = f[2].pills("الفريمات", TIMEFRAMES, selection_mode="multi", default=["15m", "1h", "4h", "1d"],
                        key="rsi_hm_tfs", label_visibility="collapsed") or []
    limit = f[3].selectbox("العملات", (10, 20, 30, 50, 100, 200, 300), index=1, key="rsi_hm_limit",
                           label_visibility="collapsed", format_func=lambda n: f"{n} عملة")
    timeframes = [tf for tf in TIMEFRAMES if tf in picked]
    if not timeframes:
        st.info("اختار فريم واحد على الأقل.")
        return
    default_tf = "4h" if "4h" in timeframes else timeframes[0]
    chart_tf = f[4].selectbox("فريم الخريطة", timeframes, index=timeframes.index(default_tf), key="rsi_hm_chart_tf",
                              label_visibility="collapsed", format_func=lambda t: f"خريطة {t}")
    with f[5].popover("⚙"):
        deep = st.toggle("Radar: كل الاستراتيجيات", value=True, key="rsi_hm_deep",
                         help="كل مدارس الاستراتيجيات + هارمونيك + نماذج الشارت (أبطأ).")
        use_flow = st.toggle("Flow: الأوردر فلو", value=False, key="rsi_hm_flow",
                             help="لقطة الأوردر فلو لأفضل 20 setup (OKX / Hyperliquid).")
        live = st.selectbox("تحديث تلقائي", (0, 1, 2, 5, 15), index=0, key="rsi_hm_live",
                            format_func=lambda m: "مقفول" if not m else f"كل {m} دقيقة")
    if live:
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=live * 60_000, key="rsi_hm_autorefresh")
        except Exception:
            st.caption("streamlit-autorefresh not installed: Live is off.")

    symbols, note = _symbols(asset_class, int(limit))
    if not symbols:
        st.warning("No verified symbols are currently available for this market. No synthetic symbols were added.")
        return
    from modules.market_cache import fetch_frames
    with st.spinner(f"Loading {len(symbols)} symbols × {len(timeframes)} timeframes…"):
        frames, errors = fetch_frames(symbols, timeframes, limit=WARMUP_BARS, workers=4)

    detail, setups = {}, {}
    for symbol in symbols:
        per_tf = {}
        for tf in timeframes:
            try:
                measure = _measure((frames.get(symbol) or {}).get(tf))
            except Exception:
                measure = None
            if measure:
                per_tf[tf] = measure
        detail[symbol] = per_tf
        try:
            setups[symbol] = read_setup(_closed_frame((frames.get(symbol) or {}).get(chart_tf)))
        except Exception:
            setups[symbol] = None
    if not any(detail.values()):
        st.error("No symbols returned enough verified closed candles. Check the providers and selected timeframes.")
        if errors:
            with st.expander(f"Unavailable symbols ({len(errors)})"):
                st.json(errors)
        return

    with st.spinner("Reading every school on the map timeframe…" if deep else "Building the board…"):
        items = build_items(symbols, detail, setups, frames, chart_tf, timeframes, deep, use_flow)
    st.iframe(board_html(items, chart_tf, timeframes), height=780, alt="RSI heatmap map and setup board")

    if errors:
        with st.expander(f"Unavailable symbols/timeframes ({len(errors)})"):
            st.json(errors)
    st.caption(
        f"{note + ' · ' if note else ''}Wilder RSI(14), closed candles, 250-bar warm-up. Conviction = net schools agreeing "
        "out of 9 (Structure SMC/ICT, Liquidity, Imbalance FVG/OTE, Elliott, Fib/Harmonic, Trend, Momentum, Price action, "
        "Order flow) - a count, not a probability. Plan = last close, stop beyond the nearest swing level (else 1.5 ATR), "
        "target = next opposite level (else 2R). Footprint is not read here. A guide to where to look, not a trade order."
    )
