"""
THE NEWS DESK
Pulls recent headlines from Finnhub's free tier and tags each with a
relevant asset icon for the small live news strip. Requires a free API key
from finnhub.io pasted into config.py (FINNHUB_API_KEY).
"""

import html
from datetime import datetime, timezone

import requests
import streamlit as st
from config import FINNHUB_API_KEY, FINNHUB_NEWS_URL
from modules.stock_fund import api_key as _finnhub_key   # config.py -> env var -> Streamlit secrets

ASSET_ICONS = {
    "forex": "[FX]",
    "crypto": "[CRYPTO]",
    "general": "[NEWS]",
    "merger": "[M&A]",
}


def _status(msg: str) -> list:
    """One placeholder row that the Workspace shows as a status line (never as a headline)."""
    return [{"headline": msg, "source": "", "url": "", "icon": "", "status": True}]


def _av_fallback(limit: int, why: list) -> list:
    """Finnhub failed -> Alpha Vantage NEWS_SENTIMENT headlines; if that fails too, keep Finnhub's status line."""
    try:
        from modules import alphavantage as av
        r = av.news()
    except Exception:
        return why
    rows = r.get("rows") or []
    if not rows:
        err = r.get("error") or "no articles"
        try:
            from modules import rss_news
            rss = rss_news.fetch(limit)
        except Exception:
            rss = []
        if rss:
            return [{"headline": a["title"], "source": a["source"], "url": a["url"], "icon": ASSET_ICONS["general"],
                     "summary": "", "datetime": a["time"]} for a in rss]
        return _status(why[0]["headline"] + f"  |  Alpha Vantage fallback: {err[:60]}")
    return [{"headline": a["title"], "source": f"{a['source']} (AV {a['score']:+.2f})", "url": a["url"] or "",
             "icon": ASSET_ICONS["general"], "summary": "", "datetime": a["time"]} for a in rows[:limit]]


@st.cache_data(ttl=300)
def get_latest_news(category: str = "general", limit: int = 10):
    res = _finnhub_news(category, limit)
    if res and res[0].get("status"):
        return _av_fallback(limit, res)
    return res


def _finnhub_news(category: str, limit: int):
    key = _finnhub_key()
    if not key:
        return _status("Finnhub: no key found - add FINNHUB_API_KEY in Streamlit Secrets (or config.py).")
    try:
        r = requests.get(FINNHUB_NEWS_URL, params={"category": category, "token": key}, timeout=10)
        if r.status_code in (401, 403):
            return _status(f"Finnhub: key rejected (HTTP {r.status_code}) - check FINNHUB_API_KEY.")
        if r.status_code == 429:
            return _status("Finnhub: rate limit reached - try again in a minute.")
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list):
            return _status("Finnhub: unexpected answer (not a news list).")
        data = data[:limit]
    except Exception as e:   # type name only: the exception text can contain the request URL with the key
        return _status(f"Finnhub: news fetch failed ({type(e).__name__}).")

    icon = ASSET_ICONS.get(category, ASSET_ICONS["general"])
    return [
        {"headline": item.get("headline", ""), "source": item.get("source", ""),
         "url": item.get("url", ""), "icon": icon, "summary": item.get("summary", ""),
         "datetime": (datetime.fromtimestamp(item["datetime"], timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                      if isinstance(item.get("datetime"), (int, float)) and item["datetime"] else "")}
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
