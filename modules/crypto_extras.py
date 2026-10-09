"""
THE CRYPTO DESK
Crypto-only extras: live OKX order book + time & sales tables, plus
quick-link helpers for CoinGlass heatmaps and DEXScreener meme-coin/whale
tracking (no free embeddable API for these two - shown as live links).
Switched from Binance to OKX because Binance returns HTTP 451 (geo-block)
from Streamlit Community Cloud's US-based servers; OKX's public endpoints
work fine from there with no API key needed.
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
    """Free DEXScreener search endpoint - used for meme-coin / whale-style
    tracking. No key required, rate-limited on their side."""
    try:
        r = requests.get(DEXSCREENER_SEARCH_URL, params={"q": query}, timeout=10)
        r.raise_for_status()
        return r.json().get("pairs", [])
    except Exception:
        return []
