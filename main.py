"""
THE FLOOR MANAGER
Orchestrates every employee module above and renders the final dashboard.
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

st.set_page_config(page_title="AI Trading Desk", layout="wide", page_icon="\U0001F4CA")

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
    st.sidebar.markdown(f"- [{label}]({url})")

with st.expander("\U0001F4F0 Live news (Finnhub)", expanded=False):
    news_items = get_latest_news(category="general", limit=8)
    for item in news_items:
        if item["url"]:
            st.markdown(f"{item['icon']} [{item['headline']}]({item['url']}) \u2014 *{item['source']}*")
        else:
            st.markdown(f"{item['icon']} {item['headline']}")


def score_mt5_group(symbols):
    results = []
    for sym in symbols:
        try:
            df = get_mt5_data(sym, "H1")
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
        stars = ("\u2B50" * filled) + ("\u25AB\uFE0F" * empty)
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 3])
            c1.markdown(f"**{row['symbol']}**  \n{row['trade_type']}")
            c2.markdown(f"{stars}  \nBias: {row['trend_bias']}")
            reasons_txt = ", ".join(row["reasons"]) if row["reasons"] else "None"
            c3.markdown(f"Price: {row['price']:.5f}  \nReasons: {reasons_txt}")
    check_and_fire_alerts(filtered, play_sound=play_sound)


tab_crypto, tab_forex, tab_metals, tab_stocks, tab_meme = st.tabs(
    ["\U0001FA99 Crypto", "\U0001F4B1 Forex", "\U0001F947 Metals", "\U0001F4C8 Stocks", "\U0001F438 Meme Coins"]
)

with tab_crypto:
    col_chart, col_watch = st.columns([2, 1])
    with col_chart:
        pick = st.selectbox("Chart symbol", CRYPTO_SYMBOLS, key="crypto_chart_pick")
        render_tv_chart(pick)
    with col_watch:
        st.subheader("Watchlist")
        results = score_crypto_group(CRYPTO
