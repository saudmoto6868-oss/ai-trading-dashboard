"""News -> which market it may push and which way (owner 2026-11-06: 'a geopolitical headline that affects gold or oil').

KEYWORD RULES, not understanding: each headline (English or Arabic) is matched against simple themes; a theme maps to a
usual market reaction (textbook, not measured here): war / attacks -> gold up, oil up, risk assets down; rate cuts / dovish
Fed -> gold up, dollar down (EURUSD up), crypto up; hot inflation / hawkish -> gold down, dollar up; OPEC cut -> oil up;
ETF inflows -> crypto up; hacks / bans -> crypto down. The board shows the headline + the rule, so the owner can judge."""
from __future__ import annotations

import re

# theme: (words, {asset: +1 / -1}, Arabic reason)
THEMES = [
    ("geopolitics", ("war", "attack", "missile", "strike", "invasion", "conflict", "sanction", "escalat", "troops", "drone", "ceasefire collapse",
                     "حرب", "هجوم", "صاروخ", "ضربة", "غزو", "عقوبات", "تصعيد", "مسيرة", "اشتباك"),
     {"GOLD": 1, "SILVER": 1, "OIL": 1, "BTC": -1, "ETH": -1, "SOL": -1, "EURUSD": -1}, "توتر جيوسياسي: الدهب والبترول بيطلعوا عادة والمخاطرة بتنزل"),
    ("peace", ("ceasefire", "peace deal", "truce", "de-escalat", "هدنة", "وقف إطلاق النار", "اتفاق سلام", "تهدئة"),
     {"GOLD": -1, "OIL": -1, "BTC": 1, "ETH": 1, "SOL": 1}, "تهدئة: الملاذ الآمن بيهدى والمخاطرة بتتحسن"),
    ("dovish", ("rate cut", "cuts rates", "dovish", "easing", "lower rates", "خفض الفائدة", "تخفيض الفائدة", "تيسير"),
     {"GOLD": 1, "SILVER": 1, "EURUSD": 1, "BTC": 1, "ETH": 1, "SOL": 1, "COPPER": 1}, "فايدة أقل: الدولار بيضعف والدهب والكريبتو بيستفيدوا"),
    ("hawkish", ("rate hike", "raises rates", "hawkish", "hot inflation", "inflation rises", "strong dollar", "رفع الفائدة", "التضخم يرتفع", "الدولار يرتفع"),
     {"GOLD": -1, "SILVER": -1, "EURUSD": -1, "BTC": -1, "ETH": -1, "SOL": -1}, "فايدة أعلى / دولار قوي: ضغط على الدهب والكريبتو"),
    ("opec_cut", ("opec cut", "output cut", "supply cut", "production cut", "أوبك تخفض", "خفض الإنتاج"),
     {"OIL": 1}, "خفض إنتاج البترول: البترول بيطلع عادة"),
    ("opec_up", ("output increase", "raise output", "production increase", "زيادة الإنتاج"),
     {"OIL": -1}, "زيادة إنتاج البترول: ضغط على السعر"),
    ("china_growth", ("china stimulus", "stimulus", "china growth", "تحفيز", "الصين تحفز"),
     {"COPPER": 1, "SILVER": 1, "OIL": 1}, "تحفيز / نمو: المعادن الصناعية بتستفيد"),
    ("recession", ("recession", "slowdown", "layoffs", "ركود", "تباطؤ"),
     {"COPPER": -1, "OIL": -1, "GOLD": 1}, "خوف من ركود: النحاس والبترول بينزلوا والدهب ملاذ"),
    ("crypto_up", ("etf inflow", "etf approval", "approves etf", "adoption", "treasury buys bitcoin", "تدفقات", "اعتماد صندوق"),
     {"BTC": 1, "ETH": 1, "SOL": 1}, "تدفقات / اعتماد: إيجابي للكريبتو"),
    ("crypto_down", ("hack", "exploit", "ban", "crackdown", "lawsuit", "sec sues", "اختراق", "حظر", "دعوى"),
     {"BTC": -1, "ETH": -1, "SOL": -1}, "اختراق / حظر / قضايا: سلبي للكريبتو"),
    ("central_bank_gold", ("central bank gold", "gold reserves", "buys gold", "البنوك المركزية الذهب", "احتياطي الذهب"),
     {"GOLD": 1}, "البنوك المركزية بتشتري دهب"),
]
NAMES = {"GOLD": ("gold", "دهب", "ذهب"), "SILVER": ("silver", "فضة"), "OIL": ("oil", "crude", "brent", "opec", "نفط", "بترول", "خام"),
         "COPPER": ("copper", "نحاس"), "BTC": ("bitcoin", "btc", "بيتكوين", "crypto", "كريبتو", "عملات مشفرة"), "ETH": ("ether", "ethereum", "إيثريوم"),
         "SOL": ("solana", "سولانا"), "EURUSD": ("euro", "ecb", "يورو", "المركزي الأوروبي"), "DXY": ("dollar", "دولار")}


def _hit(text: str, words) -> bool:
    """English words match whole words only ('war' must not match 'warns'); Arabic words match inside (prefixes ال / و / ب)."""
    for w in words:
        if w.isascii():
            tail = r"[a-z]*" if len(w) >= 5 else r"(?:s|es|ed)?"   # 'escalat' -> escalates; 'war' -> wars, never 'warns'
            if re.search(r"(?<![a-z])" + re.escape(w) + tail + r"(?![a-z])", text):
                return True
        elif w in text:
            return True
    return False


def tag(items: list[dict]) -> list[dict]:
    """Each headline -> themes matched + per-asset push (+1 / -1). Headlines that name a market get it even without a theme."""
    out = []
    for it in items:
        t = " " + str(it.get("title") or it.get("headline") or "").lower() + " "
        push, why = {}, []
        for name, words, eff, reason in THEMES:
            if _hit(t, words):
                for a, v in eff.items():
                    push[a] = push.get(a, 0) + v
                why.append(reason)
        named = [a for a, w in NAMES.items() if _hit(t, w)]
        if push or named:
            out.append({**it, "title": it.get("title") or it.get("headline"), "push": {a: int(max(-1, min(1, v))) for a, v in push.items() if v}, "named": named, "why": why})
    return out


def tilt(tagged: list[dict], asset: str) -> dict:
    """{'score': up - down, 'up': n, 'down': n, 'items': top headlines for this asset}"""
    rel = [x for x in tagged if asset in x["push"] or asset in x["named"]]
    up = sum(1 for x in rel if x["push"].get(asset, 0) > 0)
    dn = sum(1 for x in rel if x["push"].get(asset, 0) < 0)
    rel.sort(key=lambda x: -abs(x["push"].get(asset, 0)))
    return {"score": up - dn, "up": up, "down": dn, "items": rel[:4]}


def fetch() -> list[dict]:
    """World monitor (economic / political / geopolitical, Arabic + English) + market RSS. Never raises."""
    items = []
    try:
        from modules.world_news import fetch_world
        w, _errs = fetch_world()
        items += w
    except Exception:
        pass
    try:
        from modules import rss_news
        items += rss_news.fetch(30)
    except Exception:
        pass
    seen, out = set(), []
    for x in items:
        k = re.sub(r"\W+", "", str(x.get("title") or x.get("headline") or "").lower())[:80]
        if k and k not in seen:
            seen.add(k)
            out.append(x)
    return out
