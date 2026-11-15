"""RSI Heatmap Intelligence: multi-timeframe momentum research on native feeds.

No CoinGlass dependency. Uses TIA's market catalogue and the shared candle cache.
Only closed candles are used; unavailable feeds remain explicit.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

ASSET_CLASSES = (
    "Crypto", "Forex", "Metals", "Oil & Gas", "Indices", "Stocks", "Bonds",
    "Options", "Meme coins", "Egypt (EGX)", "Saudi (Tadawul)",
)
TIMEFRAMES = ("5m", "15m", "30m", "1h", "4h", "12h", "1d", "1w")
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


def heatmap_points(detail, symbols, tf, timeframes):
    """One dot per symbol with data on tf; x = catalogue rank (volume order), like CoinGlass."""
    points = []
    for rank, symbol in enumerate(symbols, start=1):
        per_tf = detail.get(symbol) or {}
        m = per_tf.get(tf)
        if not m:
            continue
        point = {"rank": rank, "symbol": _short(symbol), "full": symbol, "rsi": m["rsi"],
                 "band": rsi_band(m["rsi"]), "price": m["price"]}
        for other in timeframes:
            point[f"RSI {other}"] = per_tf[other]["rsi"] if other in per_tf else None
        points.append(point)
    return points


def _short(symbol):
    s = str(symbol)
    for prefix in ("HL:xyz:", "HL:", "Y:", "FH:"):
        if s.startswith(prefix):
            s = s[len(prefix):]
    for suffix in ("-USDT-SWAP", "-USDT", "-USD", "=X", ".CA", ".SR"):
        if s.endswith(suffix):
            s = s[: -len(suffix)]
    return s


def heatmap_spec(points, tf, timeframes):
    """Vega-Lite spec: zone bands + labelled dots + dashed average line (no extra dependency)."""
    avg = round(sum(p["rsi"] for p in points) / len(points), 2) if points else None
    n = max((p["rank"] for p in points), default=1)
    bands = [{"label": b[0], "y0": b[1], "y1": b[2], "colour": b[3]} for b in BANDS]
    tooltip = [{"field": "full", "title": "Symbol"}, {"field": "rsi", "title": f"RSI {tf}"},
               {"field": "band", "title": "Zone"}, {"field": "price", "title": "Last close", "format": ",.6~g"}]
    tooltip += [{"field": f"RSI {x}", "title": f"RSI {x}"} for x in timeframes if x != tf]
    x_scale = {"domain": [0, n + 1]}
    y_scale = {"domain": [0, 100]}
    layers = [
        {"data": {"values": bands}, "mark": {"type": "rect", "opacity": 0.13},
         "encoding": {"y": {"field": "y0", "type": "quantitative", "scale": y_scale},
                      "y2": {"field": "y1"},
                      "color": {"field": "colour", "type": "nominal", "scale": None, "legend": None}}},
        {"data": {"values": bands}, "mark": {"type": "text", "align": "right", "dx": -4, "fontSize": 11,
                                              "opacity": 0.8, "x": "width"},
         "encoding": {"y": {"field": "mid", "type": "quantitative", "scale": y_scale},
                      "text": {"field": "label"},
                      "color": {"field": "colour", "type": "nominal", "scale": None, "legend": None}},
         "transform": [{"calculate": "(datum.y0 + datum.y1) / 2", "as": "mid"}]},
        {"data": {"values": [{"y": v} for v in (30, 40, 60, 70)]},
         "mark": {"type": "rule", "strokeDash": [2, 4], "opacity": 0.35},
         "encoding": {"y": {"field": "y", "type": "quantitative", "scale": y_scale}}},
        {"data": {"values": points}, "mark": {"type": "circle", "size": 90, "opacity": 0.95,
                                               "stroke": "#111", "strokeWidth": 0.5},
         "encoding": {"x": {"field": "rank", "type": "quantitative", "scale": x_scale,
                            "axis": {"title": "Symbols (volume rank)", "labels": False, "ticks": False, "grid": False}},
                      "y": {"field": "rsi", "type": "quantitative", "scale": y_scale,
                            "axis": {"title": f"RSI(14) · {tf}", "values": [0, 30, 40, 50, 60, 70, 100]}},
                      "color": {"field": "band", "type": "nominal",
                                "scale": {"domain": [b[0] for b in BANDS], "range": [b[3] for b in BANDS]},
                                "legend": {"orient": "bottom", "title": None}},
                      "tooltip": tooltip}},
        {"data": {"values": points}, "mark": {"type": "text", "dy": -11, "fontSize": 11, "fontWeight": "bold"},
         "encoding": {"x": {"field": "rank", "type": "quantitative", "scale": x_scale},
                      "y": {"field": "rsi", "type": "quantitative", "scale": y_scale},
                      "text": {"field": "symbol"},
                      "color": {"field": "band", "type": "nominal", "legend": None,
                                "scale": {"domain": [b[0] for b in BANDS], "range": [b[3] for b in BANDS]}}}},
    ]
    if avg is not None:
        layers.append({"data": {"values": [{"avg": avg, "label": f"Avg RSI {avg:.2f}"}]},
                       "mark": {"type": "rule", "strokeDash": [6, 4], "strokeWidth": 1.5, "color": "#f5a524"},
                       "encoding": {"y": {"field": "avg", "type": "quantitative", "scale": y_scale}}})
        layers.append({"data": {"values": [{"avg": avg, "label": f"Avg RSI {avg:.2f}"}]},
                       "mark": {"type": "text", "align": "left", "dx": 4, "dy": -6, "x": 0,
                                "color": "#f5a524", "fontWeight": "bold"},
                       "encoding": {"y": {"field": "avg", "type": "quantitative", "scale": y_scale},
                                    "text": {"field": "label"}}})
    return {"height": 460, "layer": layers, "config": {"view": {"stroke": None}}}, avg


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


def render():
    st.markdown("### RSI Heatmap Intelligence")
    st.caption(
        "Multi-timeframe momentum map · Wilder RSI(14) · closed candles only · "
        "TIA/native market feeds · research only, not an execution signal"
    )
    c1, c2, c3 = st.columns([1.2, 1.35, 0.9])
    with c1:
        asset_class = st.selectbox("Market", ASSET_CLASSES, index=0, key="rsi_hm_market")
    with c2:
        timeframes = st.multiselect(
            "Timeframes", TIMEFRAMES, default=["15m", "1h", "4h", "12h", "1d", "1w"],
            key="rsi_hm_tfs",
        )
    with c3:
        limit = st.selectbox("Symbols", (10, 25, 50, 100, 200), index=2, key="rsi_hm_limit")
    if not timeframes:
        st.info("Select at least one timeframe.")
        return

    symbols, note = _symbols(asset_class, int(limit))
    if note:
        st.caption(note)
    if not symbols:
        st.warning("No verified symbols are currently available for this market. No synthetic symbols were added.")
        return

    from modules.market_cache import fetch_frames
    with st.spinner(f"Loading {len(symbols)} symbols across {len(timeframes)} timeframes…"):
        frames, errors = fetch_frames(symbols, timeframes, limit=WARMUP_BARS, workers=4)

    rows, detail = [], {}
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
        row = {"Symbol": symbol}
        prices = [per_tf[tf]["price"] for tf in reversed(timeframes) if tf in per_tf]
        row["Last price"] = prices[0] if prices else "—"
        row["MTF alignment"] = _alignment(per_tf, timeframes)
        row["Available TFs"] = f"{len(per_tf)}/{len(timeframes)}"
        for tf in timeframes:
            m = per_tf.get(tf)
            row[f"RSI {tf}"] = m["rsi"] if m else "—"
            row[f"Trend {tf}"] = m["trend"] if m else "—"
        rows.append(row)

    if not any(detail.values()):
        st.error("No symbols returned enough verified closed candles. Check the providers and selected timeframes.")
        if errors:
            with st.expander(f"Unavailable symbols ({len(errors)})"):
                st.json(errors)
        return

    df = pd.DataFrame(rows)
    rsi_cols = [f"RSI {tf}" for tf in timeframes]
    analysed = sum(bool(x) for x in detail.values())
    aligned = sum(x.get("MTF alignment") in ("Bullish alignment", "Bearish alignment") for x in rows)
    default_tf = "4h" if "4h" in timeframes else timeframes[0]
    chart_tf = st.radio("Heatmap timeframe", timeframes, index=timeframes.index(default_tf),
                        horizontal=True, key="rsi_hm_chart_tf")
    points = heatmap_points(detail, symbols, chart_tf, timeframes)
    spec, avg = heatmap_spec(points, chart_tf, timeframes)
    counts = {b[0]: sum(p["band"] == b[0] for p in points) for b in BANDS}
    cols = st.columns(len(BANDS) + 1)
    cols[0].metric(f"Avg RSI ({chart_tf})", f"{avg:.2f}" if avg is not None else "—",
                   f"{len(points)} of {len(symbols)} symbols")
    for col, band in zip(cols[1:], BANDS):
        col.metric(f"{band[0]} ({band[1]}–{band[2]})", counts[band[0]])
    if points:
        st.vega_lite_chart(spec, use_container_width=True)
    else:
        st.info(f"No symbol has verified closed candles on {chart_tf}.")
    st.caption(f"Symbols with data on any timeframe: {analysed}/{len(symbols)} · full MTF alignment: {aligned}")

    # CoinGlass-style table: sorted by the heatmap timeframe, RSI cells coloured by band.
    sort_col = f"RSI {chart_tf}"
    df["_sort"] = pd.to_numeric(df[sort_col], errors="coerce")
    df = df.sort_values("_sort", ascending=False, na_position="last").drop(columns="_sort")
    show_trend = st.toggle("Show EMA 9/21 trend per timeframe", value=False, key="rsi_hm_trend")
    keep = ["Symbol", "Last price"] + [c for tf in timeframes
                                      for c in ([f"RSI {tf}", f"Trend {tf}"] if show_trend else [f"RSI {tf}"])]
    keep += ["MTF alignment", "Available TFs"]
    view = df[keep]
    styled = view.style.map(_style_rsi, subset=rsi_cols).format(
        lambda v: f"{v:.2f}" if isinstance(v, (int, float)) else v, subset=rsi_cols).format(
        lambda v: f"{v:,.6g}" if isinstance(v, (int, float)) else v, subset=["Last price"])
    st.dataframe(styled, use_container_width=True, hide_index=True, height=min(38 * (len(view) + 1), 640))
    available_symbols = [s for s in symbols if detail.get(s)]
    selected = st.selectbox("Open symbol analysis", available_symbols, key="rsi_hm_symbol")
    selected_data = detail.get(selected, {})
    if selected_data:
        st.markdown("#### Selected symbol · timeframe breakdown")
        cards = st.columns(min(4, len(timeframes)))
        for i, tf in enumerate(timeframes):
            m = selected_data.get(tf)
            with cards[i % len(cards)]:
                st.metric(f"RSI · {tf}", f"{m['rsi']:.2f}" if m else "Unavailable",
                          m["zone"] if m else "No verified closed candles")
                if m:
                    st.caption(f"{m['trend']} · close {m['price']:,.6g}")
                    st.caption(f"Last closed: {m['last_closed']}")

    if st.button("Analyse selected symbol with TIA Director", key="rsi_hm_director"):
        from modules.tia_intelligence import director_report
        with st.spinner(f"Running TIA evidence review for {selected}…"):
            report = director_report(selected, asset_class)
        st.markdown("#### TIA Director")
        st.write(report.get("stance", "UNAVAILABLE"), "·", report.get("confidence", "LOW"))
        st.caption(report.get("director_summary", "No director summary returned."))
        for warning in report.get("warnings", []):
            st.warning(warning)
        st.json({"technical": report.get("technical", {}), "flow": report.get("flow", {}),
                 "sources": report.get("sources", {}), "options": report.get("options")})

    if errors:
        with st.expander(f"Symbols/timeframes with unavailable data ({len(errors)})"):
            st.json(errors)
    st.caption(
        "RSI is a momentum condition, not a buy/sell instruction. Overbought can persist in strong trends. "
        "Confirm with market structure, volume/liquidity, verified order flow and risk rules. "
        "EGX/Tadawul and some Yahoo-backed instruments may be delayed or unavailable."
    )
