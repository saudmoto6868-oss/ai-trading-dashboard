"""RSI Heatmap Intelligence: market-wide RSI research using existing feeds.

Uses the platform's own TIA market catalog and candle cache. CoinGlass is not
a dependency. Missing feeds remain visible as unavailable, never fabricated.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

ASSET_CLASSES = ("Crypto", "Metals", "Oil & Gas", "Indices", "Forex", "Stocks", "Bonds", "Meme coins", "Egypt (EGX)", "Saudi (Tadawul)")
TIMEFRAMES = ("5m", "15m", "30m", "1h", "4h", "1d")


def rsi_wilder(closes, period=14):
    """Wilder RSI over close prices; requires period+1 observations."""
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
    return round(100 - 100 / (1 + avg_gain / avg_loss), 2)


def rsi_zone(value):
    if value is None:
        return "Unavailable"
    if value >= 70:
        return "Overbought"
    if value <= 30:
        return "Oversold"
    return "Neutral"


def _symbols(asset_class, limit):
    from modules.tia_intelligence import symbols_for_class
    catalog = symbols_for_class(asset_class, top=limit)
    return catalog.get("symbols", [])[:limit], catalog.get("note", "")


def _row(symbol, timeframe):
    from modules.market_cache import get_klines
    df = get_klines(symbol, timeframe, 100)
    if df is None or len(df) < 16:
        raise ValueError("Insufficient candle history")
    # Ignore the still-forming candle to avoid intrabar RSI flicker.
    closed = df.iloc[:-1]
    if len(closed) < 15:
        raise ValueError("Insufficient closed candles")
    closes = closed["close"].astype(float).tolist()
    value = rsi_wilder(closes, 14)
    if value is None:
        raise ValueError("RSI unavailable")
    last = float(closes[-1])
    ema9 = pd.Series(closes).ewm(span=9, adjust=False).mean().iloc[-1]
    ema21 = pd.Series(closes).ewm(span=21, adjust=False).mean().iloc[-1]
    trend = "Bullish" if ema9 > ema21 else "Bearish" if ema9 < ema21 else "Mixed"
    return {
        "Symbol": symbol, "RSI 14": value, "Zone": rsi_zone(value),
        "Trend": trend, "Last price": last,
        "Last closed candle": str(closed["time"].iloc[-1]) if "time" in closed else "—",
    }


def _style_rsi(value):
    if value >= 70:
        return "background-color:#6b3038;color:#fff;font-weight:700"
    if value <= 30:
        return "background-color:#245b4b;color:#fff;font-weight:700"
    return "background-color:#34445a;color:#fff"


def render():
    st.markdown("### RSI Heatmap Intelligence")
    st.caption("Market-wide momentum map · Wilder RSI(14) · Closed candles only · Research, not an execution signal")
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        asset_class = st.selectbox("Market", ASSET_CLASSES, index=0, key="rsi_hm_market")
    with c2:
        timeframe = st.selectbox("Timeframe", TIMEFRAMES, index=3, key="rsi_hm_tf")
    with c3:
        limit = st.selectbox("Symbols", (10, 25, 50, 100), index=1, key="rsi_hm_limit")
    symbols, note = _symbols(asset_class, limit)
    if note:
        st.caption(note)
    if not symbols:
        st.warning("No verified symbols are currently available for this market. No synthetic symbols were added.")
        return
    rows, errors = [], []
    progress = st.progress(0, text="Loading verified candle data…")
    for i, symbol in enumerate(symbols):
        try:
            rows.append(_row(symbol, timeframe))
        except Exception as exc:
            errors.append((symbol, f"{type(exc).__name__}: {str(exc)[:100]}"))
        progress.progress((i + 1) / len(symbols), text=f"Analysed {i + 1}/{len(symbols)} symbols")
    progress.empty()
    if not rows:
        st.error("No symbols returned enough verified closed candles. Check the market data provider.")
        if errors:
            st.caption(f"{len(errors)} symbols unavailable.")
        return
    df = pd.DataFrame(rows).sort_values("RSI 14", ascending=False).reset_index(drop=True)
    overbought = int((df["RSI 14"] >= 70).sum())
    oversold = int((df["RSI 14"] <= 30).sum())
    a, b, c, d = st.columns(4)
    a.metric("Symbols analysed", len(df))
    b.metric("Overbought ≥70", overbought)
    c.metric("Oversold ≤30", oversold)
    d.metric("Unavailable", len(errors))
    st.dataframe(
        df.style.map(_style_rsi, subset=["RSI 14"]),
        use_container_width=True, hide_index=True,
        column_config={"RSI 14": st.column_config.ProgressColumn("RSI 14", min_value=0, max_value=100, format="%.2f")},
    )
    selected = st.selectbox("Open symbol analysis", df["Symbol"].tolist(), key="rsi_hm_symbol")
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
        with st.expander(f"Unavailable symbols ({len(errors)})"):
            st.dataframe(pd.DataFrame(errors, columns=["Symbol", "Reason"]), use_container_width=True, hide_index=True)
    st.caption("RSI is a momentum condition, not a buy/sell instruction. Overbought can persist in strong trends; confirm with trend, volume/liquidity and risk rules.")
