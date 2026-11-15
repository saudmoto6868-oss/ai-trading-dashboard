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


def heatmap_spec(points, tf, timeframes, height: int = 460):
    """Vega-Lite spec: zone bands + labelled dots + dashed average line (no extra dependency)."""
    avg = round(sum(p["rsi"] for p in points) / len(points), 2) if points else None
    n = max((p["rank"] for p in points), default=1)
    bands = [{"label": b[0], "y0": b[1], "y1": b[2], "colour": b[3]} for b in BANDS]
    tooltip = [{"field": "full", "title": "Symbol"}, {"field": "rsi", "title": f"RSI {tf}"},
               {"field": "band", "title": "Zone"}, {"field": "state", "title": "State"}, {"field": "price", "title": "Last close", "format": ",.6~g"}]
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
    return {"height": height, "layer": layers, "config": {"view": {"stroke": None}}}, avg


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


def _band_chips(counts, avg, tf, n_points, n_symbols):
    chips = [f'<span style="border:1px solid #f5a524;color:#f5a524;border-radius:10px;padding:1px 8px">'
             f'Avg RSI {tf}: <b>{avg:.2f}</b></span>' if avg is not None else ""]
    chips += [f'<span style="background:{b[3]}22;border:1px solid {b[3]};color:{b[3]};border-radius:10px;padding:1px 8px">'
              f'{b[0]} {b[1]}–{b[2]}: <b>{counts[b[0]]}</b></span>' for b in BANDS]
    chips.append(f'<span style="opacity:.7">{n_points}/{n_symbols} symbols on map</span>')
    st.markdown('<div style="display:flex;flex-wrap:wrap;gap:6px;font-size:12px;margin:2px 0 6px">'
                + "".join(chips) + "</div>", unsafe_allow_html=True)


@st.cache_data(ttl=60, show_spinner=False)
def _cached_flow(symbol):
    from modules.rsi_flow import fetch_flow
    return fetch_flow(symbol)


def _add_flow(rows, setups):
    """Order-flow snapshot for the best-ranked symbols that have a prints feed; adjusts their rank."""
    from concurrent.futures import ThreadPoolExecutor
    from modules.rsi_flow import FLOW_TOP_N, agreement, feed_of, flow_read
    for r in rows:
        r["Flow"], r["Flow vs setup"] = "", ""
    pick = [r for r in sorted(rows, key=lambda r: r["_rank"], reverse=True)
            if r["_rank"] > 0 and feed_of(r["Symbol"])[0]][:FLOW_TOP_N]
    if not pick:
        return
    with st.spinner(f"Order flow for {len(pick)} symbols…"), ThreadPoolExecutor(4) as pool:
        flows = list(pool.map(_cached_flow, [r["Symbol"] for r in pick]))
    for r, fl in zip(pick, flows):
        read = flow_read(fl)
        r["Flow"] = read["text"]
        agree = agreement(setups.get(r["Symbol"]), read["vote"])
        r["Flow vs setup"] = {"confirms": "✅ confirms", "against": "⚠️ against"}.get(agree, "")
        r["_rank"] += 1.5 if agree == "confirms" else -1.0 if agree == "against" else 0.0
        if agree == "confirms":
            r["_groups"] = r["_groups"] | {"Flow confirms"}


def render():
    from modules.rsi_setups import GROUPS, read_setup, setup_rank, groups_of
    st.markdown("#### RSI Heatmap Intelligence")
    f = st.columns([1.0, 2.2, 0.6, 0.7, 1.4, 1.3, 0.85])
    asset_class = f[0].selectbox("Market", ASSET_CLASSES, index=0, key="rsi_hm_market")
    timeframes = f[1].multiselect("Timeframes", TIMEFRAMES, default=["15m", "1h", "4h", "12h", "1d", "1w"],
                                  key="rsi_hm_tfs")
    limit = f[2].selectbox("Symbols", (10, 25, 50, 100, 200), index=2, key="rsi_hm_limit")
    if not timeframes:
        st.info("Select at least one timeframe.")
        return
    timeframes = [tf for tf in TIMEFRAMES if tf in timeframes]   # keep fast -> slow order
    default_tf = "4h" if "4h" in timeframes else timeframes[0]
    chart_tf = f[3].selectbox("Map TF", timeframes, index=timeframes.index(default_tf), key="rsi_hm_chart_tf")
    show = f[4].multiselect("Show", GROUPS, default=[], key="rsi_hm_show", placeholder="All states")
    query = f[5].text_input("Search", key="rsi_hm_search", placeholder="BTC, gold, squeeze, ★…")
    deep = f[6].toggle("Radar", value=True, key="rsi_hm_deep",
                       help="Run the Radar strategies + chart patterns on the map timeframe (slower).")
    from modules.rsi_flow import FLOW_TOP_N
    use_flow = f[6].toggle("Flow", value=True, key="rsi_hm_flow",
                           help=f"Order-flow snapshot (OKX / Hyperliquid prints, book, funding) for the top {FLOW_TOP_N} setups.")

    symbols, note = _symbols(asset_class, int(limit))
    if not symbols:
        st.warning("No verified symbols are currently available for this market. No synthetic symbols were added.")
        return

    from modules.market_cache import fetch_frames
    with st.spinner(f"Loading {len(symbols)} symbols × {len(timeframes)} timeframes…"):
        frames, errors = fetch_frames(symbols, timeframes, limit=WARMUP_BARS, workers=4)

    rows, detail, setups = [], {}, {}
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
            setup = read_setup(_closed_frame((frames.get(symbol) or {}).get(chart_tf)), deep=deep)
        except Exception:
            setup = None
        setups[symbol] = setup
        prices = [per_tf[tf]["price"] for tf in timeframes if tf in per_tf]
        radar = (setup or {}).get("radar") or {}
        row = {"Symbol": symbol, "Price": prices[0] if prices else None,
               "State": setup["state"] if setup else "—", "Speed": setup["speed"] if setup else "",
               "Regime": setup["regime"] if setup else "—",
               "Radar": (f"{'★' * radar['stars']} {radar['direction']} {radar['icons']}".strip()
                         if radar.get("stars") else ("·" if radar else "—")),
               "Patterns": ", ".join(setup["patterns"][:2]) if setup and setup["patterns"] else ""}
        for tf in timeframes:
            row[f"RSI {tf}"] = per_tf[tf]["rsi"] if tf in per_tf else None
        row["MTF"] = _alignment(per_tf, timeframes)
        row["_rank"] = setup_rank(setup)
        row["_groups"] = groups_of(setup)
        rows.append(row)

    if not any(detail.values()):
        st.error("No symbols returned enough verified closed candles. Check the providers and selected timeframes.")
        if errors:
            with st.expander(f"Unavailable symbols ({len(errors)})"):
                st.json(errors)
        return

    if use_flow:
        _add_flow(rows, setups)
    points = heatmap_points(detail, symbols, chart_tf, timeframes)
    for p in points:
        s_ = setups.get(p["full"]) or {}
        p["state"] = s_.get("state", "")
        if s_.get("speed"):
            p["symbol"] = f"{p['symbol']} {s_['speed']}"
    spec, avg = heatmap_spec(points, chart_tf, timeframes, height=380)
    counts = {b[0]: sum(p["band"] == b[0] for p in points) for b in BANDS}

    df = pd.DataFrame(rows)
    if show:
        df = df[df["_groups"].map(lambda g: bool(g & set(show)))]
    if query.strip():
        q = query.strip().lower()
        hay = df.drop(columns=["_groups", "_rank"]).astype(str).agg(" ".join, axis=1).str.lower()
        df = df[hay.str.contains(q, regex=False)]
    df = df.sort_values(["_rank", f"RSI {chart_tf}"], ascending=[False, False], na_position="last")

    left, right = st.columns([1.15, 1])
    with left:
        _band_chips(counts, avg, chart_tf, len(points), len(symbols))
        if points:
            st.vega_lite_chart(spec, use_container_width=True)
        else:
            st.info(f"No symbol has verified closed candles on {chart_tf}.")
    with right:
        st.markdown(f"**Watch first · {chart_tf}** <span style='opacity:.6;font-size:12px'>"
                    "Radar stars, fresh reversals / momentum / squeeze, speed</span>", unsafe_allow_html=True)
        top = df[df["_rank"] > 0].head(10)
        if top.empty:
            st.caption("Nothing stands out with the current filters.")
        else:
            st.dataframe(top[["Symbol", "State", "Speed", "Radar"] + (["Flow vs setup"] if use_flow else []) + [f"RSI {chart_tf}"]].style.map(
                _style_rsi, subset=[f"RSI {chart_tf}"]).format("{:.2f}", subset=[f"RSI {chart_tf}"], na_rep="—"),
                use_container_width=True, hide_index=True, height=380)

    rsi_cols = [f"RSI {tf}" for tf in timeframes]
    view = df.drop(columns=["_rank", "_groups"])
    if use_flow:   # flow next to the Radar, not at the far right
        lead = ["Symbol", "Price", "State", "Speed", "Regime", "Radar", "Flow", "Flow vs setup"]
        view = view[lead + [c for c in view.columns if c not in lead]]
    st.caption(f"{len(view)} of {len(rows)} symbols · sorted by setup, then RSI {chart_tf} · {note}".rstrip(" ·"))
    st.dataframe(view.style.map(_style_rsi, subset=rsi_cols)
                 .map(lambda v: _ALIGN_STYLE.get(v, ""), subset=["MTF"])
                 .format("{:.2f}", subset=rsi_cols, na_rep="—")
                 .format("{:,.6g}", subset=["Price"], na_rep="—"),
                 use_container_width=True, hide_index=True, height=360)

    with st.expander("Symbol detail · TIA Director"):
        available_symbols = [s for s in symbols if detail.get(s)]
        selected = st.selectbox("Symbol", available_symbols, key="rsi_hm_symbol")
        selected_data = detail.get(selected, {})
        cards = st.columns(max(1, min(6, len(timeframes))))
        for i, tf in enumerate(timeframes):
            m = selected_data.get(tf)
            with cards[i % len(cards)]:
                st.metric(f"RSI · {tf}", f"{m['rsi']:.2f}" if m else "—", rsi_band(m["rsi"]) if m else "No data",
                          delta_color="off")
                if m:
                    st.caption(f"{m['trend']} · {m['last_closed']}")
        if st.button("Analyse with TIA Director", key="rsi_hm_director"):
            from modules.tia_intelligence import director_report
            with st.spinner(f"Running TIA evidence review for {selected}…"):
                report = director_report(selected, asset_class)
            st.write(report.get("stance", "UNAVAILABLE"), "·", report.get("confidence", "LOW"))
            st.caption(report.get("director_summary", "No director summary returned."))
            for warning in report.get("warnings", []):
                st.warning(warning)
            st.json({"technical": report.get("technical", {}), "flow": report.get("flow", {}),
                     "sources": report.get("sources", {}), "options": report.get("options")})

    if errors:
        with st.expander(f"Unavailable symbols/timeframes ({len(errors)})"):
            st.json(errors)
    st.caption(
        "Wilder RSI(14), closed candles only, 250-bar warm-up. State = RSI phase + speed (● fast, ●● very fast over "
        f"{3} candles) + regime; Radar = the platform's strategy detectors on the map timeframe. Flow = snapshot of the "
        "last 500 prints, order book ±1 % and perp funding (OKX; Hyperliquid for HL: markets) for the top setups, "
        "cached 60 s; Yahoo / EGX / Tadawul have no public prints. A guide to where to look, not a buy/sell signal."
    )
