"""
THE NEWS DESK
Pulls recent headlines from Finnhub's free tier and tags each with a
relevant asset icon for the small live news strip. Requires a free API key
from finnhub.io pasted into config.py (FINNHUB_API_KEY).
"""

import html

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


TICKER_CSS = """<style>
.news-ticker{overflow:hidden;white-space:nowrap;background:#161a1e;border:1px solid #2b3139;
border-radius:6px;padding:6px 0;margin:4px 0 8px 0}
.news-ticker .track{display:inline-block;white-space:nowrap;animation:news-scroll var(--dur,90s) linear infinite}
.news-ticker:hover .track{animation-play-state:paused}
.news-ticker a{color:#eaecef;text-decoration:none}
.news-ticker a:hover{color:#f0b90b;text-decoration:underline}
.news-ticker .src{color:#848e9c}
@keyframes news-scroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}
</style>"""


def ticker_html(items: list) -> str:
    """Continuously scrolling one-line news ticker (pauses on hover). Content
    is duplicated so the loop is seamless. '$' is entity-escaped because
    st.markdown would otherwise treat $...$ as LaTeX."""
    parts, plain_len = [], 0
    for it in items:
        head = (it.get("headline") or "").strip()
        if not head:
            continue
        src = (it.get("source") or "").strip()
        icon = html.escape(it.get("icon") or "")
        text = html.escape(head).replace("$", "&#36;")
        plain_len += len(head) + len(src) + 8
        tail = f" <span class='src'>&mdash; {html.escape(src)}</span>" if src else ""
        url = (it.get("url") or "").strip()
        if url.startswith(("http://", "https://")):
            body = f"<a href='{html.escape(url, quote=True)}' target='_blank' rel='noopener'>{text}</a>"
        else:
            body = text
        parts.append(f"{icon} {body}{tail}")
    if not parts:
        parts = ["No news right now."]
        plain_len = 20
    sep = "&nbsp;&nbsp;&nbsp;&#9679;&nbsp;&nbsp;&nbsp;"
    line = sep.join(parts) + sep
    dur = max(40, int(plain_len / 9))  # roughly constant reading speed
    return (
        TICKER_CSS
        + f"<div class='news-ticker'><div class='track' style='--dur:{dur}s'>{line}{line}</div></div>"
    )
