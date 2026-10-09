"""
THE CRYPTO DESK
Crypto-only extras: live Binance order book and time and sales tables,
plus quick-link helpers for CoinGlass heatmaps and DEXScreener meme-coin
or whale tracking (no free embeddable API for these two - shown as live
links).
"""

import requests
import streamlit as st
from config import DEXSCREENER_SEARCH_URL
from modules.data_fetcher import get_binance_order_book, get_binance_time_and_sales


def render_order_book(symbol: str, limit: int = 15):
    bids, asks = get_binance_order_book(symbol, limit=limit)
    return bids, asks


def render_time_and_sales(symbol: str, limit: int = 20):
    return get_binance_time_and_sales(symbol, limit=limit)


@st.cache_data(ttl=60)
def search_dexscreener_pairs(query: str):
    try:
        r = requests.get(DEXSCREENER_SEARCH_URL, params={"q": query}, timeout=10)
        r.raise_for_status()
        return r.json().get("pairs", [])
    except Exception:
        return []
