"""NEWS WATCH: headlines from outside the economic calendar, from primary and reputable public sources, classified and mapped to the markets they can move (owner 2026-11-06).

Sources (modules/news_watch.SOURCES) are public RSS / Atom feeds, no keys, ranked by tier:
  A  primary: central banks, statistics offices, the regulator (Fed, ECB, BoE, BLS, SEC) - the source itself
  B  major financial press / wires (CNBC, MarketWatch, BBC Business, FXStreet, Yahoo Finance)
  C  specialist crypto media (CoinDesk, Cointelegraph, The Block): only STRONG topics are alerted (ETF decision, hack / exploit, exchange failure, regulation)
A headline becomes an alert only when its topic is high impact, its tier is A / B (or C with a strong topic), it is fresh (<= 3 h) and not a duplicate. The alert says WHICH markets it can move and
that it can move them EITHER way; the "lean" (hawkish / dovish words, a cut vs a hike) is a low-confidence reading of the wording, not a forecast.

Honest limits: keyword classification, not understanding; a feed can be blocked or change its address (a dead feed is skipped and counted, never fatal); reachability of each feed from the build sandbox
was NOT verified here (mock-tested on sample XML). Nothing here predicts a price."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# (name, url, tier)
SOURCES = [
    ("Federal Reserve", "https://www.federalreserve.gov/feeds/press_all.xml", "A"),
    ("ECB", "https://www.ecb.europa.eu/rss/press.html", "A"),
    ("Bank of England", "https://www.bankofengland.co.uk/rss/news", "A"),
    ("US BLS", "https://www.bls.gov/feed/bls_latest.rss", "A"),
    ("SEC", "https://www.sec.gov/news/pressreleases.rss", "A"),
    ("CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html", "B"),
    ("MarketWatch", "https://feeds.marketwatch.com/marketwatch/topstories/", "B"),
    ("BBC Business", "https://feeds.bbci.co.uk/news/business/rss.xml", "B"),
    ("FXStreet", "https://www.fxstreet.com/rss/news", "B"),
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex", "B"),
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/", "C"),
    ("Cointelegraph", "https://cointelegraph.com/rss", "C"),
    ("The Block", "https://www.theblock.co/rss.xml", "C"),
]
MAX_AGE_H = 3

# topic -> (impact 1-3, regex, markets EN, markets AR, strong-for-tier-C)
TOPICS = {
    "rates": (3, r"\b(fomc|rate (cut|hike|decision)|interest rates?|federal funds|dot plot|powell|lagarde|bailey|ueda|hawkish|dovish|rate-setting|monetary policy)\b",
              "USD, gold, silver, indices, BTC / ETH, EUR/USD, GBP/USD, USD/JPY", "الدولار والدهب والفضة والمؤشرات وBTC وETH واليورو والإسترليني والين", False),
    "inflation": (3, r"\b(cpi|pce|ppi|inflation|consumer prices|producer prices)\b", "USD, gold, indices, BTC, bonds", "الدولار والدهب والمؤشرات وBTC", False),
    "jobs": (3, r"\b(nonfarm|non-farm|payrolls?|unemployment rate|jobless claims|employment situation|adp)\b", "USD, gold, indices, EUR/USD, USD/JPY", "الدولار والدهب والمؤشرات واليورو والين", False),
    "geopolitics": (3, r"\b(war|invasion|missile|airstrike|attack on|sanctions?|ceasefire|embargo|blockade|nuclear|escalat\w+|tensions?)\b", "gold, oil, USD, JPY, CHF, indices", "الدهب والنفط والدولار والين والفرنك والمؤشرات", False),
    "energy": (2, r"\b(opec\+?|crude (oil )?(inventories|output|production)|oil (price|supply)|refinery|pipeline)\b", "oil, CAD, indices, inflation-sensitive assets", "النفط والكندي والمؤشرات", False),
    "trade": (2, r"\b(tariffs?|trade war|export controls?|trade deal|customs duties)\b", "indices, USD, CNY, metals, crypto", "المؤشرات والدولار واليوان والمعادن والكريبتو", False),
    "crypto_event": (3, r"\b(etf (approval|approved|rejected|decision|filing)|spot (bitcoin|ether) etf|exchange (hack|halts?|insolvency|collapse)|exploit|hacked|bankruptcy|depeg|stablecoin (ban|law|bill)|sec (sues|charges|approves))\b",
                     "BTC, ETH, altcoins, crypto stocks", "BTC وETH والعملات البديلة وأسهم الكريبتو", True),
    "regulation": (2, r"\b(regulat\w+|crackdown|ban on|bill passes|executive order)\b", "the sector named in the headline", "القطاع المذكور", False),
    "earnings": (2, r"\b(earnings|guidance|profit warning|revenue beat|revenue miss|eps)\b", "the stock / sector named, indices", "السهم أو القطاع المذكور والمؤشرات", False),
    "banking": (3, r"\b(bank (run|failure|collapse)|liquidity crisis|bailout|credit crunch|default)\b", "indices, USD, gold, BTC, bank stocks", "المؤشرات والدولار والدهب وBTC وأسهم البنوك", False),
}
HAWK = re.compile(r"\b(hike|hikes|hawkish|higher for longer|tightening|hot (inflation|cpi)|beats? expectations|stronger than expected)\b", re.I)
DOVE = re.compile(r"\b(cut|cuts|dovish|easing|pause|cooling|softer than expected|misses? expectations|weaker than expected)\b", re.I)


def _dt(s):
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        try:
            d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        except Exception:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def parse_feed(xml_text: str, source: str, tier: str, limit: int = 30) -> list:
    """RSS <item> and Atom <entry>; -> [{title, url, source, tier, time (datetime|None)}]. Bad XML -> []."""
    out = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return out
    for it in list(root.iter("item")) + [e for e in root.iter() if e.tag.endswith("}entry")]:
        g = lambda name: next((c for c in it if c.tag.split("}")[-1] == name), None)
        t = g("title")
        title = (t.text or "").strip() if t is not None else ""
        if not title:
            continue
        lk = g("link")
        url = ((lk.get("href") or lk.text or "") if lk is not None else "").strip()
        d = next((x for x in (g("pubDate"), g("published"), g("updated")) if x is not None), None)   # Element truthiness = has children, so test for None
        out.append({"title": re.sub(r"\s+", " ", title), "url": url, "source": source, "tier": tier, "time": _dt(d.text if d is not None else None)})
        if len(out) >= limit:
            break
    return out


def classify(title: str, tier: str = "B") -> dict | None:
    """{topics, impact, assets_en, assets_ar, lean} or None when nothing high-impact matches."""
    low = title.lower()
    hits = [(k, v) for k, v in TOPICS.items() if re.search(v[1], low)]
    if not hits:
        return None
    impact = max(v[0] for _, v in hits)
    if tier == "C" and not any(v[4] for _, v in hits):
        return None
    if impact < 2:
        return None
    lean = "hawkish" if HAWK.search(title) and not DOVE.search(title) else "dovish" if DOVE.search(title) and not HAWK.search(title) else None
    return {"topics": [k for k, _ in hits], "impact": impact, "assets_en": "; ".join(dict.fromkeys(v[2] for _, v in hits)), "assets_ar": "؛ ".join(dict.fromkeys(v[3] for _, v in hits)), "lean": lean}


def fetch_all(fetch_text, sources=SOURCES) -> tuple[list, list]:
    """fetch_text(url) -> xml text. -> (items, dead source names). A failing feed never raises."""
    items, dead = [], []
    for name, url, tier in sources:
        try:
            txt = fetch_text(url)
            got = parse_feed(txt, name, tier) if txt else []
        except Exception:
            got = []
        if not got:
            dead.append(name)
        items += got
    return items, dead


def alerts(items, now=None, max_age_h: float = MAX_AGE_H) -> list:
    """Fresh, high-impact, de-duplicated headlines worth a message; best (tier, impact) first."""
    now = now or datetime.now(timezone.utc)
    seen, out = set(), []
    for it in items:
        c = classify(it["title"], it["tier"])
        if not c:
            continue
        if it["time"] is not None and (now - it["time"]).total_seconds() > max_age_h * 3600:
            continue
        key = re.sub(r"[^a-z0-9]+", " ", it["title"].lower()).strip()[:90]
        if key in seen:
            continue
        seen.add(key)
        out.append({"id": "news|" + key[:60], **it, **c})
    out.sort(key=lambda a: ("ABC".index(a["tier"]), -a["impact"]))
    return out


def format_news(a: dict, ar: bool = True) -> str:
    import html
    esc = html.escape
    lean = {"hawkish": ("ميل متشدد (قراية كلمات، مش توقع)", "hawkish wording (a reading of the words, not a forecast)"), "dovish": ("ميل متساهل (قراية كلمات، مش توقع)", "dovish wording (a reading of the words, not a forecast)")}.get(a["lean"])
    t = f"📰 <b>{esc(a['title'])}</b>\n{esc(a['source'])} (مصدر {a['tier']})" if ar else f"📰 <b>{esc(a['title'])}</b>\n{esc(a['source'])} (tier {a['tier']})"
    t += f"\n{'ممكن يحرك' if ar else 'can move'}: {esc(a['assets_ar'] if ar else a['assets_en'])} {'في الاتجاهين' if ar else 'either way'}"
    if lean:
        t += f"\n{esc(lean[0] if ar else lean[1])}"
    if a.get("url"):
        t += f"\n{esc(a['url'])}"
    return t[:3900] + ("\n<i>تنبيه مش إشارة دخول.</i>" if ar else "\n<i>A heads-up, not an entry signal.</i>")


def default_fetch_text(url: str) -> str:
    import requests
    r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0 (XPiX news watch)"})
    return r.text if r.status_code == 200 else ""
