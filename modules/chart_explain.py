"""Radar hover explanation (owner 2026-10-22): instead of many small tags on each chart, hovering the chart shows a plain
Arabic explanation: the chart pattern and its psychology (breakout, trend break ...), the last candles' pattern and the
psychology behind it, where price sits against EMA 9 / 20 / 50 / 200, and the timeframe ladder (higher frame first).

Sources for the texts: the classic definitions (Edwards & Magee for chart patterns, Steve Nison for candlesticks, Elder's
triple screen for the timeframe ladder). The candle rules below are this dashboard's own simple geometry; textbook bias is
NOT a measured edge - the Radar card shows the lab's number next to it.
"""
from __future__ import annotations

import pandas as pd

# chart patterns: id -> (Arabic name, what it is + psychology, what confirms it)
PATTERN_AR = {
    "cp_channel_up": ("قناة صاعدة", "قمم وقيعان أعلى بين خطين متوازيين: المشترين متحكمين وكل نزول بيتشرى.",
                      "الاستمرار طول ما السعر جوه القناة؛ كسر الخط السفلي بإغلاق = ضعف الترند."),
    "cp_channel_dn": ("قناة هابطة", "قمم وقيعان أقل بين خطين متوازيين: البياعين متحكمين وكل ارتداد بيتباع.",
                      "الاستمرار طول ما السعر جوه القناة؛ اختراق الخط العلوي بإغلاق = بداية تغيير."),
    "cp_channel_h": ("رينج أفقي", "السعر محصور بين دعم ومقاومة: توازن بين الطرفين ومحدش كسب لسه.",
                     "الإشارة الحقيقية مع الخروج من الرينج بإغلاق وفوليوم أعلى من المتوسط."),
    "cp_wedge_up": ("وتد صاعد (سلبي غالباً)", "السعر بيطلع بس كل موجة أضعف والخطين بيضيقوا: الشراء بيتعب.",
                    "كسر الخط السفلي بإغلاق؛ من غير كسر هو لسه صاعد."),
    "cp_wedge_dn": ("وتد هابط (إيجابي غالباً)", "السعر بينزل بس كل موجة أضعف والخطين بيضيقوا: البيع بيخلص.",
                    "اختراق الخط العلوي بإغلاق."),
    "cp_tri_asc": ("مثلث صاعد", "مقاومة أفقية وقيعان بتعلى: المشترين بيدخلوا أبدر كل مرة وبيضغطوا على المقاومة.",
                   "اختراق المقاومة بإغلاق وفوليوم؛ الهدف التقليدي = ارتفاع المثلث."),
    "cp_tri_desc": ("مثلث هابط", "دعم أفقي وقمم بتنزل: البياعين بيبيعوا أرخص كل مرة وبيضغطوا على الدعم.",
                    "كسر الدعم بإغلاق وفوليوم."),
    "cp_tri_sym": ("مثلث متماثل", "قمم بتنزل وقيعان بتعلى: تردد وانضغاط قبل حركة كبيرة، والاتجاه مش محسوم.",
                   "استنى الخروج من أي ضلع بإغلاق؛ الاتجاه السابق هو الأرجح."),
    "cp_hs": ("رأس وكتفين", "3 قمم الوسطى أعلاهم: المشترين فشلوا يعملوا قمة جديدة بعد الرأس.",
              "كسر خط الرقبة بإغلاق؛ قبل الكسر هو احتمال بس."),
    "cp_ihs": ("رأس وكتفين مقلوب", "3 قيعان الوسطى أوطاهم: البياعين فشلوا يكملوا النزول.",
               "اختراق خط الرقبة بإغلاق."),
    "cp_multi_top": ("قمة متعددة (3+)", "السعر رفض نفس المستوى 3 مرات أو أكتر: عرض قوي هناك.",
                     "كسر القاع اللي بين القمم؛ اختراق المستوى نفسه يلغي النموذج."),
    "cp_multi_bottom": ("قاع متعدد (3+)", "السعر ارتد من نفس المستوى 3 مرات أو أكتر: طلب قوي هناك.",
                        "اختراق القمة اللي بين القيعان؛ كسر المستوى يلغي النموذج."),
    "cp_tl_support": ("على خط ترند داعم", "السعر نازل لخط الترند الصاعد: مكان المشترين المعتاد.",
                      "ارتداد بشمعة قوية = استمرار؛ إغلاق تحت الخط = كسر ترند."),
    "cp_tl_resist": ("على خط ترند مقاوم", "السعر طالع لخط الترند الهابط: مكان البياعين المعتاد.",
                     "رفض بشمعة قوية = استمرار الهبوط؛ إغلاق فوق الخط = كسر ترند."),
    "chan_up": ("اختراق قناة لفوق", "السعر خرج فوق قناة الانحدار: زخم شراء غير عادي.", "الأفضل إعادة اختبار للخط من فوق وثباته."),
    "chan_dn": ("كسر قناة لتحت", "السعر خرج تحت قناة الانحدار: زخم بيع غير عادي.", "الأفضل إعادة اختبار للخط من تحت ورفضه."),
    "tl_up": ("كسر خط الترند الهابط لفوق", "الترند الهابط اتكسر: البياعين فقدوا السيطرة على الأقل مؤقتاً.",
              "قاع أعلى بعد الكسر أو إعادة اختبار ناجحة."),
    "tl_dn": ("كسر خط الترند الصاعد لتحت", "الترند الصاعد اتكسر: المشترين فقدوا السيطرة على الأقل مؤقتاً.",
              "قمة أقل بعد الكسر أو إعادة اختبار فاشلة."),
    "dbl_top": ("قمة مزدوجة", "قمتين عند نفس المستوى: محاولة تانية فشلت تكسر القمة.", "كسر القاع اللي في النص."),
    "dbl_bottom": ("قاع مزدوج", "قاعين عند نفس المستوى: محاولة تانية فشلت تكسر القاع.", "اختراق القمة اللي في النص."),
}

# candlestick patterns: id -> (Arabic name, psychology, bias)
CANDLE_AR = {
    "hammer": ("مطرقة", "البياعين نزّلوا السعر جامد جوه الشمعة والمشترين رجّعوه وقفلوا قريب من الأعلى: رفض للأسعار الأوطى.", "buy"),
    "shooting_star": ("شهاب", "المشترين طلّعوا السعر والبياعين رجّعوه وقفلوا قريب من الأدنى: رفض للأسعار الأعلى.", "sell"),
    "bull_engulf": ("ابتلاع شرائي", "شمعة خضرا جسمها غطى جسم الحمرا اللي قبلها: المشترين أخدوا السيطرة كلها في شمعة واحدة.", "buy"),
    "bear_engulf": ("ابتلاع بيعي", "شمعة حمرا جسمها غطى جسم الخضرا اللي قبلها: البياعين أخدوا السيطرة كلها في شمعة واحدة.", "sell"),
    "doji": ("دوجي", "الفتح والإغلاق تقريباً واحد: تردد كامل، ولا طرف كسب. بعد ترند طويل ممكن يبقى تعب.", None),
    "inside": ("شمعة داخلية", "الشمعة كلها جوه مدى اللي قبلها: انضغاط وراحة قبل حركة؛ الخروج من مداها هو الإشارة.", None),
    "morning_star": ("نجمة الصباح", "هبوط قوي، بعده شمعة صغيرة تردد، بعدها صعود قوي: البيع خلص والمشترين رجعوا.", "buy"),
    "evening_star": ("نجمة المساء", "صعود قوي، بعده شمعة صغيرة تردد، بعدها هبوط قوي: الشراء خلص والبياعين رجعوا.", "sell"),
    "three_white": ("3 جنود بيض", "3 شمعات خضرا ورا بعض كل واحدة بتقفل أعلى: شراء مستمر ومنظم.", "buy"),
    "three_black": ("3 غربان سود", "3 شمعات حمرا ورا بعض كل واحدة بتقفل أوطى: بيع مستمر ومنظم.", "sell"),
    "bull_marubozu": ("ماروبوزو صاعد", "شمعة خضرا كبيرة من غير ذيول تقريباً: المشترين مسيطرين من الفتح للإغلاق.", "buy"),
    "bear_marubozu": ("ماروبوزو هابط", "شمعة حمرا كبيرة من غير ذيول تقريباً: البياعين مسيطرين من الفتح للإغلاق.", "sell"),
}


# the other Radar signals in one short Arabic phrase each (the hover's "other signals" line)
FLAG_AR = {
    "rsi_gt70": "RSI فوق 70 (تشبع شراء)", "rsi_gt80": "RSI فوق 80", "rsi_gt90": "RSI فوق 90",
    "rsi_lt30": "RSI تحت 30 (تشبع بيع)", "rsi_lt20": "RSI تحت 20", "rsi_lt10": "RSI تحت 10",
    "chg_up2": "آخر شمعة +2% أو أكتر", "chg_dn2": "آخر شمعة −2% أو أكتر", "vol_2x": "فوليوم ضعف المتوسط", "vol_3x": "فوليوم 3 أضعاف المتوسط",
    "st_elliott": "موجات إليوت", "st_ew3": "بداية الموجة 3 (إليوت)", "st_msb": "كسر هيكل + أوردر بلوك (SMC)", "st_ob": "أوردر بلوك",
    "st_unicorn": "يونيكورن (ICT)", "st_breaker": "بريكر بلوك", "st_fvg": "فجوة سعرية FVG", "st_ote": "منطقة دخول OTE (ICT)",
    "st_judas": "جوداس سوينج (ICT)", "st_sweep": "سحب سيولة", "st_ifvg": "فجوة معكوسة IFVG", "st_harm": "نماذج هارمونيك",
    "st_mss": "تغيير هيكل MSS / CHoCH", "st_pd": "منطقة خصم / بريميوم", "st_silver": "سيلفر بوليت (ICT)", "st_mit": "ميتيجيشن بلوك",
    "st_bvd": "اختراق بفوليوم دلتا", "st_smt": "دايفرجنس SMT بين أزواج مرتبطة", "st_crt": "CRT (سحب مدى شمعة أكبر ورجوع)",
    "st_sessamd": "AMD الجلسة", "st_orb": "اختراق مدى الافتتاح", "st_kzs": "قناص الكيل زون", "st_po3": "Power of Three",
    "st_donch": "ترند دونشيان", "st_sma1040": "تقاطع SMA 10/40", "st_turtle55": "اختراق 55 يوم (تيرتل)", "st_rsidiv": "دايفرجنس RSI",
    "st_macddiv": "دايفرجنس MACD", "st_fib": "فيبوناتشي", "st_vwap": "VWAP", "st_ma": "المتوسطات المتحركة", "st_m2022": "موديل ICT 2022",
    "st_cisd": "سحب + CISD", "st_tl": "كسر خط ترند",
}


def candles(df: pd.DataFrame) -> list:
    """Candlestick patterns on the last closed candles (the last row is treated as closed). -> list of ids, strongest first."""
    if df is None or len(df) < 20:
        return []
    o, h, l, c = (df[k].astype(float).values for k in ("open", "high", "low", "close"))
    rng = [max(h[i] - l[i], 1e-12) for i in range(len(c))]
    body = [abs(c[i] - o[i]) for i in range(len(c))]
    avg_body = sum(body[-21:-1]) / 20 or 1e-12
    up, dn = (lambda i: c[i] > o[i]), (lambda i: c[i] < o[i])
    i = len(c) - 1
    trend_dn = c[i - 1] < c[i - 6]   # short context: patterns are reversals only after a move into them
    trend_up = c[i - 1] > c[i - 6]
    out = []
    if i >= 2 and dn(i - 2) and body[i - 2] > avg_body and body[i - 1] < 0.5 * avg_body and up(i) and body[i] > avg_body \
            and c[i] > (o[i - 2] + c[i - 2]) / 2:
        out.append("morning_star")
    if i >= 2 and up(i - 2) and body[i - 2] > avg_body and body[i - 1] < 0.5 * avg_body and dn(i) and body[i] > avg_body \
            and c[i] < (o[i - 2] + c[i - 2]) / 2:
        out.append("evening_star")
    if all(up(j) and body[j] > 0.6 * avg_body for j in (i - 2, i - 1, i)) and c[i] > c[i - 1] > c[i - 2]:
        out.append("three_white")
    if all(dn(j) and body[j] > 0.6 * avg_body for j in (i - 2, i - 1, i)) and c[i] < c[i - 1] < c[i - 2]:
        out.append("three_black")
    if up(i) and dn(i - 1) and c[i] >= o[i - 1] and o[i] <= c[i - 1] and body[i] > body[i - 1]:
        out.append("bull_engulf")
    if dn(i) and up(i - 1) and c[i] <= o[i - 1] and o[i] >= c[i - 1] and body[i] > body[i - 1]:
        out.append("bear_engulf")
    lower, upper = min(o[i], c[i]) - l[i], h[i] - max(o[i], c[i])
    if lower >= 2 * body[i] and upper <= 0.35 * rng[i] and body[i] > 0.05 * rng[i] and trend_dn:
        out.append("hammer")
    if upper >= 2 * body[i] and lower <= 0.35 * rng[i] and body[i] > 0.05 * rng[i] and trend_up:
        out.append("shooting_star")
    if body[i] >= 1.5 * avg_body and upper + lower <= 0.1 * rng[i]:
        out.append("bull_marubozu" if up(i) else "bear_marubozu")
    if body[i] <= 0.1 * rng[i] and rng[i] > 0.3 * avg_body:
        out.append("doji")
    if h[i] <= h[i - 1] and l[i] >= l[i - 1]:
        out.append("inside")
    return out


def ema_lines(df: pd.DataFrame) -> list:
    """Plain Arabic lines: price vs EMA 9 / 20 / 50 / 200, their order, and a fresh 50/200 cross."""
    c = df["close"].astype(float)
    e = {n: c.ewm(span=n, adjust=False).mean() for n in (9, 20, 50, 200)}
    px = float(c.iloc[-1])
    role = {9: "الزخم القصير", 20: "ترند قصير", 50: "ترند متوسط", 200: "ترند طويل"}
    above = [n for n in e if px > float(e[n].iloc[-1])]
    lines = ["السعر " + ("فوق" if n in above else "تحت") + f" EMA {n} ({role[n]})" for n in (9, 20, 50, 200) if len(c) >= n]
    v = {n: float(e[n].iloc[-1]) for n in e}
    if px > v[9] > v[20] > v[50]:
        lines.append("ترتيب صاعد كامل (سعر > 9 > 20 > 50): ترند صاعد صحي، والشراء عند الرجوع لـ 20 أو 50.")
    elif px < v[9] < v[20] < v[50]:
        lines.append("ترتيب هابط كامل (سعر < 9 < 20 < 50): ترند هابط صحي، والبيع عند الارتداد لـ 20 أو 50.")
    elif v[9] > v[20] > v[50]:
        lines.append("المتوسطات مرتبة صاعدة (9 > 20 > 50) بس السعر تحت EMA 9: تراجع جوه ترند صاعد، مش رينج.")
    elif v[9] < v[20] < v[50]:
        lines.append("المتوسطات مرتبة هابطة (9 < 20 < 50) بس السعر فوق EMA 9: ارتداد جوه ترند هابط، مش رينج.")
    else:
        lines.append("المتوسطات متلخبطة: مفيش ترند واضح على الفريم ده، الرينج أرجح.")
    if len(c) >= 210:
        d = (e[50] - e[200]).tail(10)
        if d.iloc[0] < 0 < d.iloc[-1]:
            lines.append("تقاطع ذهبي جديد (50 فوق 200) في آخر 10 شمعات.")
        elif d.iloc[0] > 0 > d.iloc[-1]:
            lines.append("تقاطع موت جديد (50 تحت 200) في آخر 10 شمعات.")
    return lines


def explain(df: pd.DataFrame, flags) -> dict:
    """-> {'patterns': [(name, psychology, confirm)], 'candles': [(name, psychology, bias)], 'ema': [lines]} for one chart."""
    pats = [PATTERN_AR[k] for k in flags if k in PATTERN_AR]
    return {"patterns": pats, "candles": [CANDLE_AR[k] for k in candles(df)], "ema": ema_lines(df) if df is not None and len(df) >= 50 else []}
