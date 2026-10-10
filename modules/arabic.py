"""
THE ARABIC LAYER
Pure helpers (no Streamlit) that turn the scanner's structured results into:
  * short coloured TAG boxes (strategy abbreviations) for each symbol row,
  * the trade-type chip (سكالب / داي تريد / سوينج / بوزشن),
  * an Arabic written analysis (signals, higher timeframes, plan, scenarios),
  * a TradingView link, and
  * an annotated chart image (inline SVG) with the zone / entry / stop / targets
    drawn on the symbol's recent candles.

The English detector wording stays untouched; every signal carries a stable
"key" (see signals._KEY_PATTERNS) and its numbers, and the Arabic sentences
are built from those.
"""

from __future__ import annotations

import html

import pandas as pd

from config import TV_SYMBOL_MAP
from modules.signals import fp

ISO_L, ISO_R = "⁨", "⁩"  # isolate numbers so they do not reorder inside Arabic text


def n_(x) -> str:
    return f"{ISO_L}{x}{ISO_R}"


TRADE_AR = {"Scalp": "سكالب", "Day Trade": "داي تريد", "Swing": "سوينج", "Position": "بوزشن"}
TRADE_COLOR = {"Scalp": "#f6465d", "Day Trade": "#f0b90b", "Swing": "#4aa3ff", "Position": "#b57cff"}
TF_AR = {"1m": "دقيقة", "1h": "ساعة", "1d": "يومي", "1w": "أسبوعي"}
DIR_AR = {"bullish": "صاعد", "bearish": "هابط", "neutral": "محايد"}
TV_INTERVAL = {"1m": "1", "1h": "60", "1d": "D", "1w": "W"}

# tag text, background, text colour
TAGS = {
    "Elliott": ("اليوت", "#f0b90b", "#000"),
    "Unicorn": ("يونيكورن", "#b57cff", "#000"),
    "MSB-OB": ("MSB-OB", "#26c6da", "#000"),
    "Fib": ("فيبو", "#ff9800", "#000"),
    "MA": ("متوسطات", "#5a6b7d", "#fff"),
    "VWAP": ("VWAP", "#5a6b7d", "#fff"),
}
KEY_TAGS = {
    "sweep": ("سيولة", "#4aa3ff", "#000"),
    "liqline": ("سيولة", "#4aa3ff", "#000"),
    "breakout": ("اختراق", "#0ecb81", "#000"),
    "ohl_break": ("اختراق", "#0ecb81", "#000"),
    "ohl_open": ("OHL", "#8bc34a", "#000"),
    "level": ("دعم/مقاومة", "#9e9e9e", "#000"),
    "zombie": ("زومبي", "#ff5fa2", "#000"),
}


def tag_for(sig: dict) -> tuple:
    return KEY_TAGS.get(sig.get("key")) or TAGS.get(sig.get("family"), (sig.get("family", "?"), "#555", "#fff"))


def tags_html(signals: list) -> str:
    seen, out = set(), []
    for s in signals:
        text, bg, fg = tag_for(s)
        if text in seen:
            continue
        seen.add(text)
        out.append(
            f"<span style='display:inline-block;background:{bg};color:{fg};font-size:11px;font-weight:700;"
            f"padding:1px 6px;margin:0 3px 2px 0;border-radius:3px'>{html.escape(text)}</span>"
        )
    return "".join(out)


def trade_chip_html(trade_type: str) -> str:
    col = TRADE_COLOR.get(trade_type, "#848e9c")
    return (f"<span style='display:inline-block;border:1px solid {col};color:{col};font-size:11px;"
            f"font-weight:700;padding:0 6px;border-radius:9px'>{html.escape(TRADE_AR.get(trade_type, trade_type))}</span>")


# --------------------------------------------------------------------------
# Signals in Arabic
# --------------------------------------------------------------------------

def signal_ar(s: dict) -> tuple:
    """(Arabic name, Arabic detail) for one finalized signal dict."""
    k, p, v = s.get("key"), s.get("prices", {}), s.get("vals", {})
    bull = s["direction"] == "bullish"
    up, dn = ("فوق", "تحت") if bull else ("تحت", "فوق")
    f = lambda key: n_(fp(p[key])) if key in p else "-"
    if k == "ma_cross":
        nm = s["name"].replace(" bullish cross", "").replace(" bearish cross", "")
        return (f"تقاطع {nm} {'صاعد' if bull else 'هابط'}",
                f"المتوسط السريع قطع البطيء {'لأعلى' if bull else 'لأسفل'} منذ {n_(v.get('ago', '?'))} شمعة")
    if k == "ema_stack":
        return ("ترتيب المتوسطات EMA 9/21/50",
                f"السعر {up} متوسطات مرتبة بالكامل (اتجاه {'صاعد' if bull else 'هابط'} قوي)")
    if k == "vwap":
        return (f"{up} VWAP", f"السعر {f('p')} {up} VWAP المتحرك {f('v')} (نقطة التوازن العادلة تدعم {'الشراء' if bull else 'البيع'})")
    if k == "ew3":
        ideal = " (المنطقة المثالية 50-61.8%)" if v.get("ideal") else ""
        return ("بداية الموجة 3 (إليوت)",
                f"الموجة 2 ارتدت {n_(format(v.get('ret', 0), '.0%'))} من الموجة 1{ideal}؛ الهدف 1.618×الموجة 1 = {f('t')}؛ "
                f"تلغى الفكرة {dn} {f('inv')}")
    if k == "ew5":
        return ("بداية الموجة 5 (إليوت)",
                f"الموجة 4 ارتدت {n_(format(v.get('ret', 0), '.0%'))} من الموجة 3 (المعتاد 38.2%)؛ الهدف: الموجة 5 = الموجة 1 عند {f('t1')}، "
                f"أو 1.618× من بداية الموجة 1 حتى نهاية الموجة 3 عند {f('t2')}")
    if k == "abc":
        return ("بداية تصحيح ABC (الموجة A)",
                f"اكتملت موجة دافعة من 5 موجات عند {f('top')}؛ السعر استرد 23.6%+ منها؛ التصحيح المعتاد 38.2-61.8% = {f('a')} - {f('b')}")
    if k == "wavec":
        return ("بداية الموجة C",
                f"بعد الدافعة والموجتين A-B السعر يبتعد عن B ({f('b')})؛ هدف C = طول A عند {f('t1')}، أو 1.618×A عند {f('t2')}")
    if k == "fib":
        label = str(v.get("label", ""))
        label = (label.replace("Gold zone", "المنطقة الذهبية")
                 .replace("38.2% pullback (strong-trend continuation)", "تراجع 38.2% (استمرار اتجاه قوي)")
                 .replace("23.6% pullback (very strong trend)", "تراجع 23.6% (اتجاه قوي جدا)"))
        return ("منطقة فيبوناتشي",
                f"السعر عند ارتداد {n_(format(v.get('ret', 0), '.0%'))} من آخر موجة {'صاعدة' if bull else 'هابطة'} ({label})؛ "
                f"الامتدادات 1.272/1.618/2.0: {f('x1')} / {f('x2')} / {f('x3')}؛ أهداف Monkey: {f('m1')} / {f('m2')} / {f('m3')}؛ "
                f"بداية الموجة {f('start')}")
    if k == "msb_ob":
        return ("كسر هيكل + إعادة اختبار أوردر بلوك",
                f"إغلاق {up} {'قمة' if bull else 'قاع'} الهيكل {f('lvl')}؛ السعر يعيد اختبار الأوردر بلوك {f('zl')} - {f('zh')} "
                f"(تلغى الفكرة {dn} {f('zl') if bull else f('zh')})")
    if k == "sweep":
        return (f"سحب سيولة {'البيع' if bull else 'الشراء'}",
                f"ذيل الشمعة كسر {'القاع' if bull else 'القمة'} {f('lvl')} وأغلق عائدا {up} المستوى - تم جمع الستوبات")
    if k == "unicorn":
        return ("يونيكورن ICT (إعادة اختبار)",
                f"سحب سيولة {f('lvl')} ثم تحول هيكلي {f('hh')}، وبريكر بلوك متداخل مع فجوة القيمة العادلة FVG عند {f('zl')} - {f('zh')}")
    if k == "zombie":
        return ("حركة الزومبي (سحب سيولة عند EMA9)",
                f"ذيل كسر {'قاع' if bull else 'قمة'} {f('lvl')} عند EMA9 ({f('e')}) ثم ارتد بقوة {'لأعلى' if bull else 'لأسفل'} - سحب ستوبات ثم انعكاس سريع")
    if k == "liqline":
        return ("كسر خط السيولة", f"إغلاق عبر مستوى السيولة {f('lvl')} (مستوى بُني على حجم تداول عالٍ بشكل غير عادي)")
    if k == "ohl_open":
        return (f"OHL: الفتح = {'القاع' if bull else 'القمة'}",
                f"الشمعة فتحت على {'قاعها' if bull else 'قمتها'} وأغلقت {'صاعدة' if bull else 'هابطة'} - "
                f"{'المشترون' if bull else 'البائعون'} مسيطرون من الافتتاح")
    if k == "ohl_break":
        return (f"OHL: كسر {'قمة' if bull else 'قاع'} الشمعة السابقة",
                f"إغلاق قوي {up} {'قمة' if bull else 'قاع'} الشمعة السابقة ({f('ph')})")
    if k == "level":
        return (f"عند {'دعم' if bull else 'مقاومة'}", f"السعر على مستوى {'دعم' if bull else 'مقاومة'} {f('lvl')}")
    if k == "breakout":
        n = "".join(ch for ch in s["name"] if ch.isdigit()) or "20"
        return (f"{'اختراق' if bull else 'كسر'} آخر {n} شمعة",
                f"إغلاق {'فوق أعلى' if bull else 'تحت أدنى'} {n} شمعة عند {f('lvl')}")
    return (s.get("name", ""), s.get("detail", ""))


def htf_lines_ar(res: dict) -> list:
    out = []
    for h in res.get("htf", []):
        label = TF_AR.get(h["tf"], h["tf"])
        if not h["available"]:
            out.append(f"{label}: لا توجد بيانات")
        elif h["confirms"]:
            names = "، ".join(signal_ar(s)[0] for s in h["confirms"][:3])
            out.append(f"{label}: يؤكد - {names}")
        else:
            trend = "الاتجاه متوافق، " if h.get("trend_aligned") else ""
            out.append(f"{label}: {trend}لا توجد إشارة هيكل/منطقة في هذا الاتجاه")
    return out


def scenarios_ar(res: dict) -> list:
    d = res["direction"]
    if d == "neutral" or not res["signals"]:
        return ["لا يوجد اتجاه مسيطر - لا شيء للتخطيط له. انتظر التقاء الإشارات."]
    long = d == "bullish"
    prices = {}
    for s in res["signals"]:
        prices.update(s["prices"])
    zones = [s["zone"] for s in res["signals"] if s.get("zone")]
    inv = prices.get("inv") or prices.get("start")
    if zones:
        lo, hi = zones[0]
        inv = lo if long else hi
    tgt = prices.get("t") or prices.get("x1") or prices.get("t1") or prices.get("m3")
    first = ("1) المنطقة/المستوى يصمد: انتظر شمعة " + ("تثبت وترتد" if long else "تثبت وتُرفض") + f" ثم ادخل {'شراء' if long else 'بيع'}"
             + (f"؛ الهدف الأول حول {n_(fp(tgt))}." if tgt else "."))
    out = [first]
    if inv:
        out.append(f"2) المستوى يفشل: إغلاق شمعة {'تحت' if long else 'فوق'} {n_(fp(inv))} يلغي الفكرة - ابتعد أو انظر للاتجاه المعاكس.")
    out.append("3) فخ: السعر يخترق ثم يعود ويغلق - لا تعاكس الاختراق إلا بعد تأكيد الأوردر بوك / الصفقات (امتصاص الحائط وعدم وجود متابعة).")
    return out


# --------------------------------------------------------------------------
# Chart link + annotated image
# --------------------------------------------------------------------------

def tv_link(symbol: str, tf: str) -> str:
    sym = TV_SYMBOL_MAP.get(symbol) or ("BINANCE:" + symbol.replace("-", "") if symbol.endswith("-USDT") else symbol.replace("-", ""))
    return f"https://www.tradingview.com/chart/?symbol={sym}&interval={TV_INTERVAL.get(tf, '60')}"


def chart_svg(df: pd.DataFrame, res: dict, plan: dict | None, bars: int = 70, width: int = 640, height: int = 300) -> str:
    """Self-contained SVG: recent candles + zones + key levels + entry/stop/targets
    + a dashed path from price to the first target. No dependencies."""
    if df is None or len(df) < 10:
        return ""
    d = df.tail(bars).reset_index(drop=True)
    n = len(d)
    left, right, top, bot = 8, 74, 10, 18
    pw, ph = width - left - right, height - top - bot
    long = res["direction"] == "bullish"
    levels = []  # (price, label, color, dash)
    zones = []
    for s in res.get("signals", []):
        if s.get("zone"):
            zones.append((s["zone"][0], s["zone"][1], tag_for(s)[1]))
    if plan:
        levels.append((plan["entry"], "دخول", "#4aa3ff", ""))
        levels.append((plan["stop_loss"], "وقف", "#f6465d", "5,4"))
        for i, tp in enumerate(plan["take_profits"], 1):
            levels.append((tp, f"هدف {i}", "#0ecb81", "5,4"))
    for sup in (res.get("supports") or [])[:3]:
        levels.append((float(sup), "دعم", "#848e9c", "2,4"))
    for rs in (res.get("resistances") or [])[:3]:
        levels.append((float(rs), "مقاومة", "#848e9c", "2,4"))
    vals = list(d["high"]) + list(d["low"]) + [lv[0] for lv in levels if lv[2] != "#848e9c"]
    for z in zones:
        vals += [z[0], z[1]]
    lo, hi = float(min(vals)), float(max(vals))
    pad = (hi - lo) * 0.05 or 1.0
    lo, hi = lo - pad, hi + pad
    y = lambda v: top + (hi - v) / (hi - lo) * ph
    step = pw / n
    x = lambda i: left + (i + 0.5) * step
    o = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {width} {height}' width='100%' "
         f"style='background:#0b0e11;border:1px solid #2b3139;border-radius:6px;max-width:{width}px'>"]
    for z_lo, z_hi, col in zones:
        o.append(f"<rect x='{left}' y='{y(z_hi):.1f}' width='{pw}' height='{max(2, y(z_lo) - y(z_hi)):.1f}' fill='{col}' opacity='.18'/>")
    for price, label, col, dash in levels:
        if not (lo <= price <= hi):
            continue
        yy = y(price)
        o.append(f"<line x1='{left}' x2='{left + pw}' y1='{yy:.1f}' y2='{yy:.1f}' stroke='{col}' stroke-width='1' "
                 f"{'stroke-dasharray=' + chr(39) + dash + chr(39) if dash else ''}/>")
        o.append(f"<text x='{width - 4}' y='{yy - 2:.1f}' fill='{col}' font-size='10' text-anchor='end'>"
                 f"{html.escape(label)} {fp(price)}</text>")
    for i in range(n):
        r = d.iloc[i]
        up = r["close"] >= r["open"]
        col = "#0ecb81" if up else "#f6465d"
        o.append(f"<line x1='{x(i):.1f}' x2='{x(i):.1f}' y1='{y(r['high']):.1f}' y2='{y(r['low']):.1f}' stroke='{col}'/>")
        yo, yc = y(r["open"]), y(r["close"])
        o.append(f"<rect x='{x(i) - step * 0.33:.1f}' y='{min(yo, yc):.1f}' width='{step * 0.66:.1f}' "
                 f"height='{max(1.0, abs(yo - yc)):.1f}' fill='{col}'/>")
    if plan:  # scenario path: from last close to TP1
        x0, y0 = x(n - 1), y(float(d['close'].iloc[-1]))
        tp1 = plan["take_profits"][0]
        if lo <= tp1 <= hi:
            o.append(f"<line x1='{x0:.1f}' y1='{y0:.1f}' x2='{left + pw - 4}' y2='{y(tp1):.1f}' stroke='#f0b90b' "
                     f"stroke-width='2' stroke-dasharray='6,4'/>")
            o.append(f"<circle cx='{left + pw - 4}' cy='{y(tp1):.1f}' r='4' fill='#f0b90b'/>")
    title = f"{res['symbol']} - {DIR_AR.get(res['direction'], '')} - {TRADE_AR.get(res['trade_type'], '')}"
    o.append(f"<text x='{width - 8}' y='{height - 5}' fill='#848e9c' font-size='10' text-anchor='end'>{html.escape(title)}</text>")
    o.append("</svg>")
    return "".join(o)


# --------------------------------------------------------------------------
# Payload for the Workspace (alert cards + overlay on our own chart)
# --------------------------------------------------------------------------

TF_CHART = {"1m": "1m", "1h": "1H", "1d": "1D", "1w": "1W"}
TF_SECONDS = {"1m": 60, "1h": 3600, "1d": 86400, "1w": 604800}


def duration_ar(seconds: float) -> str:
    if seconds < 90 * 60:
        return f"~{max(1, round(seconds / 60))} دقيقة"
    if seconds < 48 * 3600:
        return f"~{round(seconds / 3600)} ساعة"
    if seconds < 21 * 86400:
        return f"~{round(seconds / 86400)} يوم"
    return f"~{round(seconds / 604800)} أسبوع"


def eta_ar(df: pd.DataFrame, plan: dict, tf: str) -> dict:
    """Rough time-to-target: a target one ATR away needs roughly two bars of
    noisy trading to be reached. A guide, not a promise."""
    from modules.signals import atr_series

    try:
        atr = float(atr_series(df).iloc[-1])
    except Exception:
        return {}
    if not atr or atr <= 0:
        return {}
    sec = TF_SECONDS.get(tf, 3600)
    out = {}
    for i in (0, 2):
        dist = abs(plan["take_profits"][i] - plan["entry"])
        out[f"tp{i + 1}"] = duration_ar(max(1, 2 * dist / atr) * sec)
    return out


def scan_entry(r: dict, df: pd.DataFrame) -> dict | None:
    """Everything the Workspace needs for one scanner result. Entry uses the last
    CLOSED candle so the payload stays stable between candle closes."""
    from modules.risk_engine import build_trade_plan

    if r["direction"] not in ("bullish", "bearish") or df is None or len(df) < 3:
        return None
    price = float(df["close"].iloc[-2])
    plan = build_trade_plan({**r, "price": price, "trend_bias": r["direction"]})
    tags, seen = [], set()
    for s in r["signals"]:
        t = tag_for(s)
        if t[0] not in seen:
            seen.add(t[0])
            tags.append([t[0], t[1], t[2]])
    zones = [[round(float(s["zone"][0]), 6), round(float(s["zone"][1]), 6), tag_for(s)[1]] for s in r["signals"] if s.get("zone")]
    return {
        "symbol": r["symbol"], "direction": r["direction"], "score": int(r["score"]), "max": int(r["max_score"]),
        "trade": TRADE_AR.get(r["trade_type"], r["trade_type"]), "tf": TF_AR.get(r["timeframe"], r["timeframe"]),
        "tfc": TF_CHART.get(r["timeframe"], "1H"), "tags": tags, "zones": zones,
        "plan": {"entry": round(plan["entry"], 6), "stop": round(plan["stop_loss"], 6),
                 "tps": [round(x, 6) for x in plan["take_profits"]]},
        "eta": eta_ar(df, plan, r["timeframe"]), "tv": tv_link(r["symbol"], r["timeframe"]),
    }
