"""
THE NEWS DESK
Pulls recent headlines from Finnhub's free tier and tags each with a
relevant asset icon for the small live news strip. Requires a free API key
from finnhub.io pasted into config.py (FINNHUB_API_KEY).
"""

import requests
import streamlit as st
from config import FINNHUB_API_KEY, FINNHUB_NEWS_URL

ASSET_ICONS = {
    "forex": "[FX]",
    "crypto": "[CRYPTO]",
    "general": "[NEWS]",
    "merger": "[M&A]",
}


@st.cache_data(ttl=300)
def get_latest_news(category: str = "general", limit: int = 10):
    if not FINNHUB_API_KEY:
        return [{"headline": "Add your free Finnhub API key in config.py to enable live news.",
                  "source": "", "url": "", "icon": ASSET_ICONS.get("general")}]

    params = {"category": category, "token": FINNHUB_API_KEY}
    try:
        r = requests.get(FINNHUB_NEWS_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()[:limit]
    except Exception as e:
        return [{"headline": f"News fetch failed: {e}", "source": "", "url": "", "icon": ""}]

    icon = ASSET_ICONS.get(category, ASSET_ICONS["general"])
    return [
        {"headline": item.get("headline", ""), "source": item.get("source", ""),
         "url": item.get("url", ""), "icon": icon}
        for item in data
    ]
