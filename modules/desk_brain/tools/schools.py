"""Tools for the Wyckoff, News and Sentiment agents (OmniDesk 10-agent structure)."""
from __future__ import annotations

import logging

import numpy as np
import requests

from ..config import NEWS_API_KEY, UNIVERSE
from ..data import sources
from ..data.cache import cached
from . import macro
from .indicators import atr, rsi, zscore_last

log = logging.getLogger("desk.schools")


def _px(x: float) -> str:
    return f"{x:,.2f}" if abs(x) >= 1000 else f"{x:.5g}"


def wyckoff_tool(symbol: str) -> dict:
    """Trading range of the last 40 daily bars, the trend before it, spring / upthrust,
    sign of strength / weakness, and effort vs result (volume vs spread)."""
    df, src = sources.prices(UNIVERSE[symbol]["yf"], "1d")
    a = float(atr(df).iloc[-1])
    rng = df.iloc[-40:]
    base = rng.iloc[:-10]
    hi, lo = float(base["High"].max()), float(base["Low"].min())
    width = (hi - lo) / a if a else 0
    before = df["Close"].iloc[-100:-40]
    prior = float(np.sign(before.iloc[-1] - before.iloc[0])) if len(before) > 2 else 0.0
    last10 = rng.iloc[-10:]
    last = float(df["Close"].iloc[-1])
    spring = bool((last10["Low"] < lo).any() and last > lo)
    upthrust = bool((last10["High"] > hi).any() and last < hi)
    vol = df["Volume"].astype(float)
    has_vol = bool(vol.iloc[-60:].sum() > 0)
    v_ratio = float(vol.iloc[-5:].mean() / vol.iloc[-60:].mean()) if has_vol and vol.iloc[-60:].mean() else None
    sos = bool(last > hi and (v_ratio is None or v_ratio > 1.2))
    sow = bool(last < lo and (v_ratio is None or v_ratio > 1.2))
    spread = float((rng["High"] - rng["Low"]).iloc[-5:].mean() / ((rng["High"] - rng["Low"]).mean() or 1))
    effort = None
    if v_ratio is not None:
        effort = ("جهد كبير ونتيجة صغيرة (امتصاص)" if v_ratio > 1.3 and spread < 0.8 else
                  "جهد ونتيجة متناسقين" if v_ratio > 1.0 else "حجم ضعيف")
    is_range = width <= 8
    if is_range and prior < 0:
        schematic = "تجميع محتمل (Accumulation)"
    elif is_range and prior > 0:
        schematic = "توزيع محتمل (Distribution)"
    else:
        schematic = "ترند (Markup)" if last > hi else "ترند (Markdown)" if last < lo else "داخل نطاق غير واضح"
    phase = ("C (Spring)" if spring else "C (Upthrust)" if upthrust else "D (SOS)" if sos else
             "D (SOW)" if sow else "B (بناء السبب)" if is_range else "E")
    bias = 1 if (spring or sos) else -1 if (upthrust or sow) else 0
    return {"tool": "wyckoff", "title": f"Wyckoff · {symbol}", "source": [src],
            "data": {"symbol": symbol, "range_high": hi, "range_low": lo, "width_atr": round(width, 1),
                     "prior_trend": int(prior), "schematic": schematic, "phase": phase, "spring": spring,
                     "upthrust": upthrust, "sos": sos, "sow": sow, "volume_ratio": None if v_ratio is None else round(v_ratio, 2),
                     "effort_vs_result": effort, "bias": bias, "has_volume": has_vol},
            "look_at": f"{schematic}، المرحلة {phase}. النطاق {_px(lo)}–{_px(hi)} بعرض {width:.1f} ATR. "
                       + ("Spring: كسر القاع ورجع جوه النطاق. " if spring else "")
                       + ("Upthrust: كسر القمة ورجع جوه. " if upthrust else "")
                       + (f"الحجم آخر 5 أيام {v_ratio:.2f}× المتوسط: {effort}." if v_ratio is not None else
                          "لا يوجد حجم لهذا السوق على ياهو، فقراءة الجهد والنتيجة غير متاحة.")}


def _av_news(tickers: str) -> tuple[list, str]:
    def go():
        if not NEWS_API_KEY:
            return [], "none"
        try:
            r = requests.get("https://www.alphavantage.co/query",
                             params={"function": "NEWS_SENTIMENT", "tickers": tickers, "limit": 50, "apikey": NEWS_API_KEY}, timeout=20)
            r.raise_for_status()
            return r.json().get("feed", []), "alphavantage"
        except Exception as e:
            log.warning("news failed: %s", e)
            return [], "none"
    return cached(f"news:{tickers}", 1800, go)


def _av_ticker(symbol: str) -> str:
    m = UNIVERSE[symbol]
    if m["kind"] == "crypto":
        return f"CRYPTO:{m['base']}"
    if m["kind"] == "fx":
        return f"FOREX:{m['base']},FOREX:{m['quote']}"
    return {"XAU": "FOREX:XAU", "XAG": "FOREX:XAG", "SPX": "SPY", "NDX": "QQQ"}.get(m["base"], m["base"])


# ---- free keyless headline feeds (public RSS) + transparent lexicon sentiment ----
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from ..config import DATA_MODE

NEWS_FEEDS = {
    "FXStreet": "https://www.fxstreet.com/rss/news",
    "ForexLive": "https://www.forexlive.com/feed/news",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Investing.com": "https://www.investing.com/rss/news.rss",
}
_UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
       "Accept": "application/rss+xml, application/xml, text/xml, */*"}

# Entity -> keywords (matched on word boundaries, lowercase). Currencies, metals, indices, crypto.
ENTITY_KEYWORDS = {
    "USD": ["usd", "dollar", "greenback", "fed", "fomc", "powell", "cpi", "nfp", "nonfarm", "payrolls", "treasury yields", "us yields"],
    "EUR": ["eur", "euro", "ecb", "lagarde", "eurozone"],
    "GBP": ["gbp", "pound", "sterling", "boe", "bank of england", "bailey"],
    "JPY": ["jpy", "yen", "boj", "bank of japan", "ueda"],
    "AUD": ["aud", "aussie", "rba", "australian dollar"],
    "NZD": ["nzd", "kiwi", "rbnz", "new zealand dollar"],
    "CAD": ["cad", "loonie", "boc", "bank of canada", "canadian dollar"],
    "CHF": ["chf", "swiss franc", "snb", "swiss national bank"],
    "XAU": ["gold", "xau", "bullion"],
    "XAG": ["silver", "xag"],
    "SPX": ["s&p", "s&p 500", "spx", "stocks", "wall street", "equities", "dow"],
    "NDX": ["nasdaq", "ndx", "tech stocks"],
    "BTC": ["bitcoin", "btc"],
    "ETH": ["ether", "ethereum", "eth"],
}
_ENTITY_RE = {k: re.compile(r"(?<![a-z0-9])(?:" + "|".join(re.escape(w) for w in sorted(v, key=len, reverse=True)) + r")(?![a-z0-9])")
              for k, v in ENTITY_KEYWORDS.items()}

# Lexicon: phrase -> weight, positive = good for the asset/currency named in the headline.
LEXICON = {
    "hawkish": 1.0, "rate hike": 1.0, "hikes rates": 1.0, "raises rates": 1.0, "higher for longer": 0.8, "tightening": 0.6,
    "dovish": -1.0, "rate cut": -1.0, "cuts rates": -1.0, "lowers rates": -1.0, "easing": -0.6, "stimulus": -0.4,
    "beats": 0.8, "beat expectations": 0.8, "above expectations": 0.7, "stronger than expected": 0.8, "hotter than expected": 0.6,
    "misses": -0.8, "missed expectations": -0.8, "below expectations": -0.7, "weaker than expected": -0.8, "cooler than expected": -0.5,
    "surges": 1.0, "soars": 1.0, "jumps": 0.8, "rallies": 0.8, "rallying": 0.8, "climbs": 0.6, "gains": 0.5, "rises": 0.5,
    "rebounds": 0.5, "record high": 0.8, "all-time high": 0.8, "strengthens": 0.6, "bullish": 0.8, "upgrade": 0.5,
    "plunges": -1.0, "tumbles": -1.0, "slumps": -0.9, "crashes": -1.0, "sinks": -0.8, "drops": -0.6, "falls": -0.6,
    "slides": -0.6, "declines": -0.5, "weakens": -0.6, "bearish": -0.8, "downgrade": -0.5, "selloff": -0.8, "sell-off": -0.8,
}
# Risk tone is applied per entity: +1 risk assets, -1 safe havens, 0 for the rest.
RISK_LEXICON = {"risk-on": 0.8, "risk on": 0.8, "risk appetite": 0.5, "risk-off": -0.8, "risk off": -0.8, "risk aversion": -0.6,
                "flight to safety": -0.8, "safe-haven": -0.5, "safe haven": -0.5}
_RISK_SIGN = {"SPX": 1, "NDX": 1, "BTC": 1, "ETH": 1, "AUD": 1, "NZD": 1, "JPY": -1, "CHF": -1, "XAU": -1}


for _w, _v in list(LEXICON.items()):   # "plunges" also matches "plunge"
    if " " not in _w and _w.endswith("s") and len(_w) > 4:
        for _b in (_w[:-1], _w[:-2] if _w.endswith("es") else _w[:-1]):
            LEXICON.setdefault(_b, _v)


def _phrase_re(words):
    return re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True)) + r")(?![a-z0-9])")


_LEX_RE = _phrase_re(LEXICON)
_RISK_RE = _phrase_re(RISK_LEXICON)


def lexicon_score(title: str, entity: str | None = None) -> float:
    """Score in [-1, 1]: positive = good for the asset named in the headline. Transparent sum of
    lexicon weights squashed with x/(1+|x|). Risk-on/off words count only when `entity` is known."""
    t = (title or "").lower()
    total = sum(LEXICON[m] for m in _LEX_RE.findall(t))
    sign = _RISK_SIGN.get(entity or "", 0)
    total += sign * sum(RISK_LEXICON[m] for m in _RISK_RE.findall(t))
    return round(total / (1 + abs(total)), 3)


def headline_entities(title: str) -> set[str]:
    t = (title or "").lower()
    return {k for k, rx in _ENTITY_RE.items() if rx.search(t)}


def headline_score_for(title: str, base: str, quote: str) -> float | None:
    """Signed toward the base: +score if the headline is about the base, -score if about the quote,
    None if it names neither or both (ambiguous)."""
    ents = headline_entities(title)
    b, q = base in ents, quote in ents
    if b == q:
        return None
    ent = base if b else quote
    s = lexicon_score(title, ent)
    return s if b else -s


def parse_rss(xml_text: str, source: str) -> list[dict]:
    """RSS 2.0 <item> or Atom <entry> -> [{title, url, ts, source}]."""
    root = ET.fromstring(xml_text)
    out = []
    for it in list(root.iter("item")) + [e for e in root.iter() if e.tag.endswith("}entry")]:
        def g(name):
            for ch in it:
                if ch.tag.split("}")[-1] == name:
                    return (ch.text or ch.attrib.get("href") or "").strip()
            return ""
        title = re.sub(r"\s+", " ", g("title"))
        if not title:
            continue
        raw = g("pubDate") or g("published") or g("updated")
        ts = None
        if raw:
            try:
                d = parsedate_to_datetime(raw)
            except Exception:
                try:
                    d = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                except Exception:
                    d = None
            if d is not None:
                ts = (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(timezone.utc).isoformat()
        out.append({"title": title, "url": g("link"), "ts": ts, "source": source})
    return out


def _fetch_feed(name: str, url: str) -> tuple[list, str | None]:
    def go():
        try:
            r = requests.get(url, headers=_UA, timeout=8)
            r.raise_for_status()
            return parse_rss(r.text, name), None
        except Exception as e:
            log.info("feed %s failed: %s", name, e)
            return [], f"{name}: {type(e).__name__}"
    return cached(f"rss:{name}", 900, go, keep=lambda v: v[1] is None)


def _all_feeds() -> tuple[list, list]:
    items, errors = [], []
    for name, url in NEWS_FEEDS.items():
        try:
            got, err = _fetch_feed(name, url)
        except Exception as e:  # never fail the tool because of a feed
            got, err = [], f"{name}: {type(e).__name__}"
        items += got
        if err:
            errors.append(err)
    return items, errors


_DEMO_TEMPLATES = {
    "USD": ["Fed's Powell sounds hawkish as CPI beats expectations", "Dollar slides as NFP misses expectations", "Fed holds rates, dollar steady"],
    "EUR": ["ECB's Lagarde dovish as euro weakens", "Euro rallies after eurozone data beats expectations", "ECB keeps rates unchanged"],
    "GBP": ["BoE hawkish hold lifts sterling", "Pound tumbles as UK data misses expectations", "BoE's Bailey cautious on outlook"],
    "JPY": ["BoJ's Ueda hints at rate hike, yen rallies", "Yen weakens as BoJ stays dovish", "Yen steady ahead of BoJ"],
    "AUD": ["RBA hawkish, aussie climbs", "Aussie slumps on weak China risk-off", "RBA minutes offer little new"],
    "NZD": ["RBNZ rate cut weighs, kiwi falls", "Kiwi rises on risk-on mood", "RBNZ on hold"],
    "CAD": ["BoC hawkish surprise, loonie jumps", "Loonie slides as oil drops", "BoC's decision looms"],
    "CHF": ["SNB dovish, Swiss franc weakens", "Swiss franc gains in risk-off", "SNB keeps policy unchanged"],
    "XAU": ["Gold surges on safe-haven demand", "Gold falls as yields rise", "Gold little changed ahead of data"],
    "XAG": ["Silver rallies with gold", "Silver slides as dollar firms", "Silver steady"],
    "SPX": ["Wall Street rallies, S&P 500 record high", "Stocks sink in risk-off selloff", "S&P 500 flat ahead of earnings"],
    "NDX": ["Nasdaq jumps as tech stocks rebound", "Nasdaq tumbles on rate fears", "Nasdaq little changed"],
    "BTC": ["Bitcoin surges past resistance", "Bitcoin slumps as risk-off hits crypto", "BTC consolidates"],
    "ETH": ["Ether rallies on ETF inflows", "Ethereum drops after selloff", "ETH range-bound"],
}


def _demo_headlines(symbol: str) -> list[dict]:
    m = UNIVERSE[symbol]
    seed = sum(ord(c) for c in symbol)
    out = []
    for i, ent in enumerate((m["base"], m["quote"])):
        tpl = _DEMO_TEMPLATES.get(ent, [])
        for j in range(3):
            if tpl:
                out.append({"title": tpl[(seed + i + j) % len(tpl)], "url": "", "ts": None, "source": "demo"})
    return out


def _score_for_symbol(symbol: str, items: list[dict]) -> list[dict]:
    m = UNIVERSE[symbol]
    seen, out = set(), []
    for it in items:
        key = it["title"].lower()
        if key in seen:
            continue
        s = headline_score_for(it["title"], m["base"], m["quote"]) if it.get("score") is None else it["score"]
        if s is None:
            continue
        seen.add(key)
        out.append({"title": it["title"], "source": it["source"], "ts": it.get("ts"), "score": s, "url": it.get("url", "")})
    return out


def _label(score: float, n: int) -> str:
    if n < 3:
        return "thin"
    return "bullish" if score >= 0.15 else "bearish" if score <= -0.15 else "neutral"


def news_tool(symbol: str) -> dict:
    m = UNIVERSE[symbol]
    cal = macro.calendar_risk()
    events = [e for e in cal["data"]["events"] if e["ccy"] in (m["base"], m["quote"])]
    errors: list[str] = []
    demo = False
    items: list[dict] = []
    if DATA_MODE == "demo":
        demo = True
    else:
        items, errors = _all_feeds()
        # live mode with every feed down: no headlines (label "thin"), never fake ones. Demo headlines here would
        # mark the whole market as demo and stop the gate from journaling a real idea.
    srcs = set(cal["source"])
    if demo:
        items = _demo_headlines(symbol)
        srcs.add("demo")
    else:
        srcs |= {n for n in NEWS_FEEDS if not any(e.startswith(n + ":") for e in errors)}
    scored = _score_for_symbol(symbol, items)
    if not demo and NEWS_API_KEY:
        feed, nsrc = _av_news(_av_ticker(symbol))
        if nsrc == "alphavantage":
            srcs.add("alphavantage")
        for f in feed[:20]:
            try:
                scored.append({"title": f.get("title"), "source": "alphavantage:" + str(f.get("source")),
                               "ts": f.get("time_published"), "score": round(float(f.get("overall_sentiment_score", 0)), 3),
                               "url": f.get("url", "")})
            except Exception:
                continue
    n = len(scored)
    score = round(float(np.mean([h["score"] for h in scored])), 3) if n else 0.0
    label = _label(score, n)
    heads = sorted(scored, key=lambda h: h["ts"] or "", reverse=True)[:8]
    ev = f"{len(events)} حدث قادم على العملتين خلال 48 ساعة. " if events else "لا أحداث قادمة قريبة. "
    if n:
        txt = (f"{n} عنوان" + (" (تجريبي، مش أخبار حقيقية)" if demo else "") + f": متوسط درجة القاموس {score:+.2f} ({label}). "
               "درجة القاموس إشارة تقريبية وليست دليلاً، اقرأ العناوين نفسها قبل الاعتماد عليها."
               + (" عناوين قليلة، الإشارة ضعيفة." if label == "thin" else ""))
    else:
        txt = "لا عناوين مطابقة لهذا السوق الآن (0 عنوان). درجة القاموس إشارة تقريبية وليست دليلاً."
    return {"tool": "news", "title": f"News · {symbol}", "source": sorted(srcs),
            "data": {"symbol": symbol, "events": events[:6], "blocked": [c for c in (m["base"], m["quote"]) if c in cal["data"]["blocked"]],
                     "headlines": heads, "score": score, "n": n, "label": label, "errors": errors, "demo": demo,
                     "news_sentiment": score if n else None, "headlines_available": bool(n)},
            "look_at": ev + txt}


def sentiment_tool(symbol: str) -> dict:
    """No free retail-positioning feed exists (see README). This is a CROWD PROXY, labelled
    as such: price stretch, RSI, and speculator COT extremes."""
    df, src = sources.prices(UNIVERSE[symbol]["yf"], "1d")
    c = df["Close"]
    r = float(rsi(c).iloc[-1])
    z = zscore_last(c.pct_change(20), 252)
    crowd = float(np.clip((r - 50) / 30 * 0.5 + z / 2 * 0.5, -1, 1))
    label = "حشد شرائي متطرف" if crowd > 0.6 else "حشد بيعي متطرف" if crowd < -0.6 else "محايد"
    return {"tool": "sentiment", "title": f"Sentiment (proxy) · {symbol}", "source": [src],
            "data": {"symbol": symbol, "crowd_proxy": round(crowd, 2), "rsi": round(r, 1), "move_z": round(z, 2),
                     "label": label, "retail_positioning": None},
            "look_at": f"مؤشر الحشد التقريبي {crowd:+.2f} ({label}): RSI {r:.0f} وحركة 20 يوم z={z:+.1f}. "
                       "ده بديل تقريبي، مش نسب مراكز التجزئة الحقيقية (مش متاحة مجاناً). الحشد المتطرف إشارة عكسية."}
