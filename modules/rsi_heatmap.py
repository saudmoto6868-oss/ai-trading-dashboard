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
TIMEFRAMES = ("5m", "15m", "30m", "1h", "4h", "1d")


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


def _style_rsi(value):
    if pd.isna(value) or value == "—":
        return "color:#8993a4"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ""
    if value >= 70:
        return "background-color:#6b3038;color:#fff;font-weight:700"
    if value <= 30:
        return "background-color:#245b4b;color:#fff;font-weight:700"
    return "background-color:#34445a;color:#fff"


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
            "Timeframes", TIMEFRAMES, default=["15m", "1h", "4h", "1d"],
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
        frames, errors = fetch_frames(symbols, timeframes, limit=120, workers=4)

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
    # Sort by the slowest selected timeframe's RSI, then by symbol for stable ordering.
    slowest_rsi = f"RSI {timeframes[-1]}"
    if slowest_rsi in df:
        df["_sort"] = pd.to_numeric(df[slowest_rsi], errors="coerce")
        df = df.sort_values("_sort", ascending=False, na_position="last").drop(columns="_sort")
    analysed = sum(bool(x) for x in detail.values())
    latest_values = [m[timeframes[0]]["rsi"] for m in detail.values() if timeframes[0] in m]
    overbought = sum(v >= 70 for v in latest_values)
    oversold = sum(v <= 30 for v in latest_values)
    aligned = sum(x.get("MTF alignment") in ("Bullish alignment", "Bearish alignment") for x in rows)
    a, b, c, d = st.columns(4)
    a.metric("Symbols with data", analysed, f"of {len(symbols)} requested")
    b.metric(f"Overbought ({timeframes[0]})", overbought)
    c.metric(f"Oversold ({timeframes[0]})", oversold)
    d.metric("Full MTF alignment", aligned)

    styled = df.style
    if rsi_cols:
        styled = styled.map(_style_rsi, subset=rsi_cols)
    st.dataframe(styled, use_container_width=True, hide_index=True)
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
