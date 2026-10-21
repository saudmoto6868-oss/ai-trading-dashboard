"""Keyless headline fallback from public RSS feeds (used when Finnhub / Alpha Vantage news are unavailable)."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import requests

from modules.news_utils import cairo_str, dedupe

FEEDS = [("CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
         ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
         ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/")]


def parse_rss(xml_text: str, source: str, limit: int = 10) -> list[dict]:
    out = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return out
    for it in root.iter("item"):
        t = (it.findtext("title") or "").strip()
        if t:
            raw = (it.findtext("pubDate") or "").strip()
            shown = raw   # no timezone in the feed date -> keep the raw text, do not guess
            try:
                dt = parsedate_to_datetime(raw)
                if dt.tzinfo is not None:
                    shown = cairo_str(dt.timestamp())
            except Exception:
                pass
            out.append({"title": t, "url": (it.findtext("link") or "").strip(), "source": source, "time": shown})
        if len(out) >= limit:
            break
    return out


def fetch(limit: int = 15) -> list[dict]:
    """Interleave the feeds; a dead feed is skipped. Never raises."""
    per = []
    for name, url in FEEDS:
        try:
            r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            per.append(parse_rss(r.text, name) if r.status_code == 200 else [])
        except requests.RequestException:
            per.append([])
    mixed = [a for grp in zip(*[g + [None] * (10 - len(g)) for g in per]) for a in grp if a]
    return dedupe(mixed, "title")[:limit]
