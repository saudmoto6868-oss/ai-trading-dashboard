
`
"""
THE FLOOR MANAGER
Orchestrates every employee module above and renders the final dashboard:
tabs per asset class, TradingView chart and watchlist per tab, crypto-only
order book, time and sales, heatmap links, a live news strip, trade-type
filters, and fired alerts with sound and trade plans.

Run locally:   streamlit run main.py
Deploy free:   push this folder to GitHub, then deploy on
               https://share.streamlit.io (Streamlit Community Cloud).
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from config import (
    FOREX_SYMBOLS, METALS_SYMBOLS, INDEX_SYMBOLS, STOCK_SYMBOLS,
    CRYPTO_SYMBOLS, ALL_MT5_SYMBOLS, EXTERNAL_LINKS, TRADE_TYPES,
)
from modules.data_fetcher import get_mt5_data, get_binance_klines
from modules.scorer import score_symbol
from modules.alerts import check_and_fire_alerts
from modules.tv_widget import render_tv_chart
from modules.news_feed import get_latest_news
from modules.crypto_extras import render_order_book, render_time_and_sales, search_dexscreener_pairs

st.set_page_config(page_title="AI Trading Desk", layout="wide", page_icon="📊")

st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    .stTabs [data-baseweb="tab"] { color: #eaecef; }
    .stTabs [aria-selected="true"] { color: #f0b90b; border-bottom-color: #f0b90b; }
    div[data-testid="stMetricValue"] { color: #f0b90b; }
</style>
""", unsafe_allow_html=True)

st.title("AI Trading Desk")
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.sidebar.header("Filters")
selected_trade_types = st.sidebar.multiselect(
    "Trade type", options=TRADE_TYPES, default=TRADE_TYPES
)
play_sound = st.sidebar.checkbox("Play sound on strong signals", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("Quick links")
for label, url in EXTERNAL_LINKS.items():
    st.sidebar.markdown(f"- {label}")

with st.expander("📰 Live news (Finnhub)", expanded=False):
    news_items = get_latest_news(category="general", limit=8)
    for item in news_items:
        if item["url"]:
            st.markdown(f"{item['icon']} [{item['headline']}]({item['url']}) — *{item['source']}*")
        else:
            st.markdown(f"{item['icon']} {item['headline']}")


def score_mt5_group(symbols):
    results = []
    for sym in symbols:
        try:
            import MetaTrader5 as mt5
            df = get_mt5_data(sym, mt5.TIMEFRAME_H1)
            if df is not None and len(df) > 60:
                res = score_symbol(df, timeframe_label="H1")
                res["symbol"] = sym
                results.append(res)
        except Exception as e:
            st.warning(f"{sym}: {e}")
    return results


def score_crypto_group(symbols):
    results = []
    for sym in symbols:
        try:
            df = get_binance_klines(sym, interval="1h", limit=300)
            res = score_symbol(df, timeframe_label="H1")
            res["symbol"] = sym
            results.append(res)
        except Exception as e:
            st.warning(f"{sym}: {e}")
    return results


def render_watchlist(results, trade_type_filter):
    filtered = [r for r in results if r["trade_type"] in trade_type_filter]
    if not filtered:
        st.info("No symbols match the current filter.")
        return
    df = pd.DataFrame(filtered).sort_values("score", ascending=False)
    for _, row in df.iterrows():
        filled = int(row["score"])
        empty = int(row["max_score"] - row["score"])
        stars = ("⭐" * filled) + ("▫️" * empty)
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 3])
            c1.markdown(f"{row['symbol']}  \n{row['trade_type']}")
[10/9/2026 3:40 PM] Saud 6868: c2.markdown(f"{stars}  \nBias: {row['trend_bias']}")
            reasons_txt = ", ".join(row["reasons"]) if row["reasons"] else "None"
            c3.markdown(f"Price: {row['price']:.5f}  \nReasons: {reasons_txt}")
    check_and_fire_alerts(filtered, play_sound=play_sound)


tab_crypto, tab_forex, tab_metals, tab_stocks, tab_meme = st.tabs(
    ["🪙 Crypto", "💱 Forex", "🥇 Metals", "📈 Stocks", "🐸 Meme Coins"]
)

with tab_crypto:
    col_chart, col_watch = st.columns([2, 1])
    with col_chart:
        pick = st.selectbox("Chart symbol", CRYPTO_SYMBOLS, key="crypto_chart_pick")
        render_tv_chart(pick)
    with col_watch:
        st.subheader("Watchlist")
        results = score_crypto_group(CRYPTO_SYMBOLS)
        render_watchlist(results, selected_trade_types)

    st.markdown("---")
    ob_col, ts_col = st.columns(2)
    ob_symbol = st.selectbox("Order book / Time & Sales symbol", CRYPTO_SYMBOLS, key="crypto_ob_pick")
    with ob_col:
        st.subheader("Order Book (live)")
        try:
            bids, asks = render_order_book(ob_symbol)
            st.markdown("Asks")
            st.dataframe(asks.sort_values("price").head(10), hide_index=True)
            st.markdown("Bids")
            st.dataframe(bids.sort_values("price", ascending=False).head(10), hide_index=True)
        except Exception as e:
            st.warning(f"Order book unavailable: {e}")
    with ts_col:
        st.subheader("Time & Sales (live)")
        try:
            trades = render_time_and_sales(ob_symbol)
            st.dataframe(trades.sort_values("time", ascending=False), hide_index=True)
        except Exception as e:
            st.warning(f"Time & sales unavailable: {e}")

with tab_forex:
    col_chart, col_watch = st.columns([2, 1])
    with col_chart:
        pick = st.selectbox("Chart symbol", FOREX_SYMBOLS, key="forex_chart_pick")
        render_tv_chart(pick)
    with col_watch:
        st.subheader("Watchlist")
        results = score_mt5_group(FOREX_SYMBOLS)
        render_watchlist(results, selected_trade_types)

with tab_metals:
    col_chart, col_watch = st.columns([2, 1])
    with col_chart:
        pick = st.selectbox("Chart symbol", METALS_SYMBOLS, key="metals_chart_pick")
        render_tv_chart(pick)
    with col_watch:
        st.subheader("Watchlist")
        results = score_mt5_group(METALS_SYMBOLS)
        render_watchlist(results, selected_trade_types)

with tab_stocks:
    col_chart, col_watch = st.columns([2, 1])
    with col_chart:
        pick = st.selectbox("Chart symbol", STOCK_SYMBOLS, key="stocks_chart_pick")
        render_tv_chart(pick)
    with col_watch:
        st.subheader("Watchlist")
        results = score_mt5_group(STOCK_SYMBOLS)
        render_watchlist(results, selected_trade_types)

with tab_meme:
    st.subheader("Meme coin / whale tracking (DEXScreener)")
    query = st.text_input("Search token (name or contract address)", value="")
    if query:
        pairs = search_dexscreener_pairs(query)
        if not pairs:
            st.info("No pairs found, or DEXScreener rate limit hit — try again shortly.")
        for p in pairs[:10]:
            with st.container(border=True):
                st.markdown(
                    f"**{p.get('baseToken', {}).get('symbol', '?')}/"
                    f"{p.get('quoteToken', {}).get('symbol', '?')}** "
                    f"on {p.get('chainId', '?')} — "
                    f"Price: ${p.get('priceUsd', '?')} — "
                    f"24h volume: ${p.get('volume', {}).get('h24', '?')}"
                )
                st.markdown(f"[View on DEXScreener]({p.get('url', '#')})")
    else:
        st.info("Enter a token name or contract address above to search live DEXScreener pairs.")
    st.markdown(f"Or browse trending pairs directly: [{EXTERNAL_LINKS['DEXScreener Trending']}]({EXTERNAL_LINKS['DEXScreener Trending']})")
`

خد وقتك في نسخ ده، هو كبير. خد كله من أول سطر لحد آخر سطر، والصقه، واختار Commit directly to the main branch، وبعدين Commit changes. ده آخر ملف في المشروع كله!
