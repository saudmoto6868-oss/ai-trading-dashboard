"""World Monitor feed: free public RSS, grouped by topic (economic / political / geopolitical) and
language (Arabic / foreign). The browser filters with switches, so we fetch everything once (cached).
No tweets: there is no reliable free source for Trump / Fed posts."""
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import timezone
from email.utils import parsedate_to_datetime
from html import unescape

import requests

# id, url, language, topic, label
FEEDS = [
    ("bbc-biz",   "https://feeds.bbci.co.uk/news/business/rss.xml",   "en", "economic",    "BBC Business"),
    ("bbc-pol",   "https://feeds.bbci.co.uk/news/politics/rss.xml",   "en", "political",   "BBC Politics"),
    ("bbc-world", "https://feeds.bbci.co.uk/news/world/rss.xml",      "en", "geopolitical", "BBC World"),
    ("aj-en",     "https://www.aljazeera.com/xml/rss/all.xml",        "en", "geopolitical", "Al Jazeera"),
    ("reuters",   "https://news.google.com/rss/search?q=site:reuters.com+markets+OR+economy&hl=en-US&gl=US&ceid=US:en", "en", "economic", "Reuters"),
    ("bbc-ar",    "https://feeds.bbci.co.uk/arabic/rss.xml",          "ar", "geopolitical", "BBC عربي"),
    ("aj-ar",    "https://news.google.com/rss/search?q=site:aljazeera.net&hl=ar&gl=EG&ceid=EG:ar", "ar", "geopolitical", "الجزيرة"),
    ("ar-econ",   "https://news.google.com/rss/search?q=%D8%A7%D9%84%D8%A7%D9%82%D8%AA%D8%B5%D8%A7%D8%AF+%D8%A7%D9%84%D8%A3%D8%B3%D9%88%D8%A7%D9%82&hl=ar&gl=EG&ceid=EG:ar", "ar", "economic", "أخبار الاقتصاد"),
]
_TAG = re.compile(r"<[^>]+>")


def parse_rss(xml_text: str, feed) -> list:
    """RSS 2.0 / Atom -> [{headline, source, url, summary, datetime, ts, topic, lang}]. Never raises."""
    fid, _url, lang, topic, label = feed
    try:
        root = ET.fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
    except Exception:
        return []
    out = []
    for it in list(root.iter("item")) + [e for e in root.iter() if e.tag.endswith("}entry")]:
        def g(*names):
            for n in names:
                for ch in it:
                    if ch.tag.split("}")[-1] == n and (ch.text or ch.get("href")):
                        return (ch.text or ch.get("href") or "").strip()
            return ""
        title = unescape(_TAG.sub("", g("title"))).strip()
        link = g("link") or ""
        if not title or not link.startswith(("http://", "https://")):
            continue
        ts = 0
        try:
            raw = g("pubDate", "updated", "published")
            try:
                dt = parsedate_to_datetime(raw)
            except Exception:
                from datetime import datetime
                dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            ts = int(dt.timestamp())
        except Exception:
            pass
        summ = unescape(_TAG.sub("", g("description", "summary"))).strip()[:400]
        out.append({"headline": title, "source": label, "url": link, "summary": summ, "ts": ts, "topic": topic, "lang": lang,
                    "datetime": __import__("datetime").datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if ts else ""})
    return out


def _one(feed, timeout=8):
    try:
        r = requests.get(feed[1], timeout=timeout, headers={"User-Agent": "Mozilla/5.0 (6868X news reader)"})
        r.raise_for_status()
        return feed[0], parse_rss(r.content, feed)[:15], None
    except Exception as e:
        return feed[0], [], f"{feed[4]}: {type(e).__name__}"


def fetch_world(feeds=FEEDS, per_feed=12):
    """-> (items newest-first, [failed feed names]). Run in parallel, each feed capped, failures reported not raised."""
    with ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(_one, feeds))
    items, errs = [], []
    for _fid, rows, err in res:
        items += rows[:per_feed]
        if err:
            errs.append(err)
    items.sort(key=lambda x: x["ts"], reverse=True)
    return items, errs
