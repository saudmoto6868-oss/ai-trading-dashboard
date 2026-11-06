"""Arabic / English free text -> safe XPiX bot actions (owner 2026-11-06: 'talk to the bot in Arabic, it follows the orders').

Rule-based first (fast, free, predictable). Only whitelisted actions exist: view / screenshot / switch symbol / timeframe /
open a widget / turn an indicator on or off / spot analyzer image / weekly briefing / ledger queries. NO orders, ever.
Unrecognised text -> [] and the bot falls back to its LLM answer.
route("ابعتلي صورة الدهب على الأسبوعي مع اليوت") ->
  [{'cmd':'ind','id':'ew','on':True}, {'cmd':'shot','asset':'GOLD','tf':'1W'}]"""
from __future__ import annotations

import re

ASSETS = [(("دهب", "ذهب", "الدهب", "الذهب", "gold", "xau", "xauusd"), "GOLD"), (("فضة", "فضه", "الفضة", "silver", "xag"), "SILVER"),
          (("نحاس", "النحاس", "copper"), "COPPER"), (("بلاتين", "platinum"), "PLATINUM"), (("بلاديوم", "palladium"), "PALLADIUM"),
          (("بيتكوين", "بتكوين", "البيتكوين", "bitcoin", "btc"), "BTC"), (("ايثريوم", "إيثريوم", "ايثيريوم", "الايث", "eth", "ethereum"), "ETH"),
          (("سولانا", "sol", "solana"), "SOL"), (("ريبل", "xrp"), "XRP")]
TFS = [(("شهري", "الشهري", "شهر", "monthly"), "1M"), (("أسبوعي", "اسبوعي", "الأسبوعي", "الاسبوعي", "ويكلي", "weekly"), "1W"),
       (("يومي", "اليومي", "ديلي", "daily"), "1D"), (("4 ساعات", "٤ ساعات", "اربع ساعات", "أربع ساعات", "4h", "4 ساعة"), "4H"),
       (("ساعة", "الساعة", "1h", "ساعه"), "1H"), (("ربع ساعة", "15 دقيقة", "15m"), "15m"), (("5 دقايق", "5 دقائق", "5m"), "5m")]
WIDGETS = [(("تايم اند سيلز", "تايم آند سيلز", "الصفقات", "time and sales", "time & sales", "tape"), "tape"),
           (("عمق السوق", "الدوم", "دوم", "dom", "depth"), "dom"), (("خريطة الاوردر فلو", "خريطة الأوردر فلو", "اوردر فلو", "أوردر فلو", "order flow"), "ofm"),
           (("تراكس", "تراك", "تتبع الأوامر", "تتبع الاوامر", "الليميت", "ليميت", "limit"), "limits"), (("التصفيات", "ليكويديشن", "liquidation"), "liq"),
           (("الإشارات", "الاشارات", "signals"), "signals"), (("التمركز", "لونج شورت", "open interest"), "posn"), (("خريطة rsi", "rsi heat"), "rsihm")]
INDS = [(("اليوت", "إليوت", "اليوت ويف", "elliott"), "ew"), (("جان", "gann"), "gann"), (("smt", "اس ام تي"), "smt"),
        (("دايفرجنس", "دايفيرجنس", "divergence"), "div"), (("هارمونيك", "harmonic"), "harm"), (("كيل زون", "killzone", "kill zone"), "kz"),
        (("فوليوم بروفايل", "volume profile"), "vp"), (("vwap",), "vwap"), (("rsi", "ار اس اي"), "rsi"), (("macd", "ماكد"), "macd"), (("adx",), "adx"),
        (("فوت برينت", "footprint"), "fp"), (("الدلتا", "دلتا", "delta"), "delta"), (("ote",), "ote"), (("msb",), "msb")]
SHOT_W = ("صورة", "صوره", "سكرين", "اسكرين", "سكرينة", "وريني", "ورّيني", "شوفلي", "اعرض", "screenshot", "shot", "show")
OFF_W = ("شيل", "اقفل", "طفي", "اخفي", "وقف", "off", "hide", "remove")
OUTLOOK_W = ("توقع", "الأسبوع الجاي", "الاسبوع الجاي", "الاسبوع ده", "الأسبوع ده", "هيطلع", "هينزل", "تقرير", "outlook", "نازل ولا طالع", "طالع ولا نازل")
ANALYZER_W = ("المحلل", "تحليل كامل", "كل المدارس", "analyzer", "داشبورد السبوت", "تحليل سبوت")
LEDGER = [(("مراكزي", "محفظتي", "السبوت بتاعي", "مراكز السبوت", "my spot"), "/spot"), (("فاتورة", "فواتير", "invoice"), "/inv"),
          (("اكسل", "إكسل", "excel"), "/spotxl"), (("تنبيهات السبوت",), "/spotalerts")]



def _nw(words):
    """Normalised words + the same words with Arabic prefixes stripped (so phrases match the stripped copies of the text)."""
    out = []
    for w in words:
        w = w.lower().replace("إ", "ا").replace("أ", "ا").replace("آ", "ا").replace("ة", "ه")
        for v in (w, " ".join(_strip(x, False) for x in w.split())):
            if v not in out:
                out.append(v)
    return tuple(out)


def _has(text: str, words) -> str | None:
    for w in sorted(_nw(words), key=len, reverse=True):
        if re.search(r"(?<![\w])" + re.escape(w.lower()) + r"(?![\w])", text):
            return w
    return None


def _first(text: str, table):
    hits = []
    for words, val in table:
        w = _has(text, words)
        if w:
            hits.append((text.find(w), val))
    out = []
    for _, v in sorted(hits):
        if v not in out:
            out.append(v)
    return out


MULTI = ("وبال", "وال", "بال", "فال", "لل", "ال")
SINGLE = ("و", "ب", "ل", "ف")


def _strip(tok: str, single: bool) -> str:
    for p in MULTI:
        if tok.startswith(p) and len(tok) - len(p) >= 2:
            return tok[len(p):]
    if single:
        for p in SINGLE:
            if tok.startswith(p) and len(tok) - len(p) >= 3:
                return _strip(tok[len(p):], False)
    return tok


def normalise(text: str) -> str:
    """Text + two copies with Arabic prefixes removed (لل / ال / و / ب ...), so 'للبيتكوين' and 'وعمق السوق' match."""
    t = str(text).lower().replace("إ", "ا").replace("أ", "ا").replace("آ", "ا").replace("ة", "ه").strip()
    toks = re.findall(r"\S+", t)
    a = " ".join(_strip(x, False) for x in toks)
    b = " ".join(_strip(x, True) for x in toks)
    return f" {t} | {a} | {b} "


def route(text: str) -> list[dict]:
    t = normalise(text)
    acts = []
    assets = _first(t, ASSETS)
    m = re.search(r"\b([a-z]{2,6})(?:-usdt)?\b", t)
    if not assets and m and m.group(1) not in {"rsi", "macd", "adx", "smt", "vwap", "ote", "msb", "dom", "eth", "btc", "show", "shot", "tape", "off", "hide", "gold", "my", "spot", "excel"}:
        assets = [m.group(1).upper()]
    tfs = _first(t, TFS)
    tf = "1H" if tfs == ["1H"] else next((x for x in tfs if x != "1H"), None)
    asset = assets[0] if assets else None
    for cmd_words, cmd in LEDGER:
        if _has(t, cmd_words):
            arg = ""
            if cmd == "/inv":
                mm = re.search(r"(?:فاتوره|فواتير|invoice)\s+(\S+)", t)
                arg = mm.group(1) if mm else ""
            return [{"cmd": "ledger", "text": (cmd + " " + arg).strip()}]
    if _has(t, OUTLOOK_W):
        return [{"cmd": "outlook", "asset": asset or "GOLD"}]
    if _has(t, ANALYZER_W):
        return [{"cmd": "spotchart", "asset": asset or "GOLD"}]
    off = bool(_has(t, OFF_W))
    for wid in _first(t, WIDGETS):
        acts.append({"cmd": "panel", "type": wid})
    for ind in _first(t, INDS):
        acts.append({"cmd": "ind", "id": ind, "on": not off})
    if acts or asset or tf or _has(t, SHOT_W):
        acts.append({"cmd": "shot", "asset": asset, "tf": tf})
    return acts


def platform_symbols(asset: str | None, syms: list[str]) -> str | None:
    """Platform symbol for an asset name: GOLD -> HL:xyz:GOLD (else Yahoo GC=F), BTC -> BTC-USDT ..."""
    if not asset:
        return None
    a = asset.upper()
    cands = {"GOLD": ["HL:xyz:GOLD", "Y:GC=F", "XAU-USDT-SWAP"], "SILVER": ["HL:xyz:SILVER", "Y:SI=F"], "COPPER": ["HL:xyz:COPPER", "Y:HG=F"],
             "PLATINUM": ["HL:xyz:PLATINUM", "Y:PL=F"], "PALLADIUM": ["HL:xyz:PALLADIUM", "Y:PA=F"]}.get(a, [a, f"{a}-USDT", f"{a}-USDT-SWAP"])
    return next((c for c in cands if c in syms), None)
