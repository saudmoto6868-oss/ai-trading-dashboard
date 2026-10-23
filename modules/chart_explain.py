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
    "hanging_man": ("الرجل المشنوق", "نفس شكل المطرقة لكن بعد صعود: البياعين نزّلوا السعر جامد جوه الشمعة والمشترين لحقوه، علامة إن المشترين بيتعبوا.", "sell"),
    "inverted_hammer": ("مطرقة مقلوبة", "ذيل علوي طويل بعد هبوط: المشترين حاولوا يطلّعوا السعر بقوة، ولو الشمعة اللي بعدها أخضر يبقى بداية رفض للهبوط.", "buy"),
    "harami": ("هارامي", "شمعة صغيرة جوه جسم شمعة كبيرة قبلها: الزخم وقف ومحدش مسيطر، والاتجاه السابق بيتشكك فيه.", None),
    "piercing": ("خط الاختراق", "بعد شمعة حمرا كبيرة تفتح خضرا تحت إغلاقها وتقفل فوق نصها: المشترين رجّعوا أكتر من نص الهبوط في شمعة واحدة.", "buy"),
    "dark_cloud": ("الغطاء السحابي المظلم", "بعد شمعة خضرا كبيرة تفتح حمرا فوق إغلاقها وتقفل تحت نصها: البياعين رجّعوا أكتر من نص الصعود في شمعة واحدة.", "sell"),
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

# ---- English versions (shown when the site language is English; same ids, same shapes) ----------------------------
PATTERN_EN = {
    "cp_channel_up": ("Rising channel", "Higher highs and higher lows between two parallel lines: buyers are in control and every dip gets bought.",
                      "It holds while price stays inside the channel; a close below the lower line = the trend is weakening."),
    "cp_channel_dn": ("Falling channel", "Lower highs and lower lows between two parallel lines: sellers are in control and every bounce gets sold.",
                      "It holds while price stays inside the channel; a close above the upper line = a possible change."),
    "cp_channel_h": ("Sideways range", "Price is boxed between support and resistance: the two sides are balanced and nobody has won yet.",
                     "The real signal comes when price exits the range on a close with above-average volume."),
    "cp_wedge_up": ("Rising wedge (usually bearish)", "Price keeps rising but every wave is weaker and the two lines narrow: buying is tiring.",
                    "A close below the lower line; without a break it is still rising."),
    "cp_wedge_dn": ("Falling wedge (usually bullish)", "Price keeps falling but every wave is weaker and the two lines narrow: selling is running out.",
                    "A close above the upper line."),
    "cp_tri_asc": ("Ascending triangle", "Flat resistance and rising lows: buyers step in earlier each time and press on the resistance.",
                   "A close above resistance with volume; the textbook target = the height of the triangle."),
    "cp_tri_desc": ("Descending triangle", "Flat support and falling highs: sellers sell cheaper each time and press on the support.",
                    "A close below support with volume."),
    "cp_tri_sym": ("Symmetrical triangle", "Falling highs and rising lows: hesitation and compression before a big move; the direction is not settled.",
                   "Wait for a close outside either side; the previous trend is the more likely direction."),
    "cp_hs": ("Head and shoulders", "3 peaks with the middle one highest: buyers failed to make a new high after the head.",
              "A close below the neckline; before the break it is only a possibility."),
    "cp_ihs": ("Inverse head and shoulders", "3 troughs with the middle one lowest: sellers failed to push lower.",
               "A close above the neckline."),
    "cp_multi_top": ("Multiple top (3+)", "Price was rejected at the same level 3 times or more: strong supply there.",
                     "A break of the low between the peaks; a break above the level itself cancels the pattern."),
    "cp_multi_bottom": ("Multiple bottom (3+)", "Price bounced from the same level 3 times or more: strong demand there.",
                        "A break of the high between the troughs; a break below the level cancels the pattern."),
    "cp_tl_support": ("On a support trendline", "Price has fallen to the rising trendline: the usual place for buyers.",
                      "A bounce with a strong candle = continuation; a close below the line = trend break."),
    "cp_tl_resist": ("On a resistance trendline", "Price has risen to the falling trendline: the usual place for sellers.",
                     "A rejection with a strong candle = the decline continues; a close above the line = trend break."),
    "chan_up": ("Breakout above a channel", "Price left above the regression channel: unusual buying momentum.", "Best if the line is retested from above and holds."),
    "chan_dn": ("Breakdown below a channel", "Price left below the regression channel: unusual selling momentum.", "Best if the line is retested from below and rejected."),
    "tl_up": ("Falling trendline broken upward", "The downtrend line broke: sellers lost control, at least for now.",
              "A higher low after the break, or a successful retest."),
    "tl_dn": ("Rising trendline broken downward", "The uptrend line broke: buyers lost control, at least for now.",
              "A lower high after the break, or a failed retest."),
    "dbl_top": ("Double top", "Two peaks at the same level: a second attempt failed to break the high.", "A break of the low in the middle."),
    "dbl_bottom": ("Double bottom", "Two troughs at the same level: a second attempt failed to break the low.", "A break of the high in the middle."),
}

CANDLE_EN = {
    "hammer": ("Hammer", "Sellers pushed price down hard inside the candle, buyers pushed it back and it closed near the high: rejection of lower prices.", "buy"),
    "shooting_star": ("Shooting star", "Buyers pushed price up, sellers pushed it back and it closed near the low: rejection of higher prices.", "sell"),
    "bull_engulf": ("Bullish engulfing", "A green candle whose body covers the previous red body: buyers took over completely in one candle.", "buy"),
    "bear_engulf": ("Bearish engulfing", "A red candle whose body covers the previous green body: sellers took over completely in one candle.", "sell"),
    "doji": ("Doji", "Open and close are almost the same: full indecision, neither side won. After a long trend it can mean fatigue.", None),
    "inside": ("Inside candle", "The whole candle sits inside the previous candle's range: compression and rest before a move; leaving its range is the signal.", None),
    "morning_star": ("Morning star", "A strong drop, then a small hesitating candle, then a strong rise: the selling is done and buyers are back.", "buy"),
    "evening_star": ("Evening star", "A strong rise, then a small hesitating candle, then a strong drop: the buying is done and sellers are back.", "sell"),
    "three_white": ("Three white soldiers", "3 green candles in a row, each closing higher: steady, orderly buying.", "buy"),
    "three_black": ("Three black crows", "3 red candles in a row, each closing lower: steady, orderly selling.", "sell"),
    "bull_marubozu": ("Bullish marubozu", "A large green candle with almost no wicks: buyers dominated from open to close.", "buy"),
    "bear_marubozu": ("Bearish marubozu", "A large red candle with almost no wicks: sellers dominated from open to close.", "sell"),
    "hanging_man": ("Hanging man", "The same shape as a hammer but after a rise: sellers pushed price down hard inside the candle and buyers caught it, a sign buyers are tiring.", "sell"),
    "inverted_hammer": ("Inverted hammer", "A long upper wick after a drop: buyers tried hard to push price up; if the next candle is green it can be the start of a rejection of the decline.", "buy"),
    "harami": ("Harami", "A small candle inside the body of a bigger candle before it: momentum stopped, nobody is in charge, and the previous direction is being questioned.", None),
    "piercing": ("Piercing line", "After a big red candle, a green one opens below its close and closes above its midpoint: buyers took back more than half of the drop in one candle.", "buy"),
    "dark_cloud": ("Dark cloud cover", "After a big green candle, a red one opens above its close and closes below its midpoint: sellers took back more than half of the rise in one candle.", "sell"),
}

FLAG_EN = {
    "rsi_gt70": "RSI above 70 (overbought)", "rsi_gt80": "RSI above 80", "rsi_gt90": "RSI above 90",
    "rsi_lt30": "RSI below 30 (oversold)", "rsi_lt20": "RSI below 20", "rsi_lt10": "RSI below 10",
    "chg_up2": "Last candle +2% or more", "chg_dn2": "Last candle −2% or more", "vol_2x": "Volume 2x the average", "vol_3x": "Volume 3x the average",
    "st_elliott": "Elliott waves", "st_ew3": "Start of wave 3 (Elliott)", "st_msb": "Market structure break + order block (SMC)", "st_ob": "Order block",
    "st_unicorn": "Unicorn (ICT)", "st_breaker": "Breaker block", "st_fvg": "Fair value gap (FVG)", "st_ote": "OTE entry zone (ICT)",
    "st_judas": "Judas swing (ICT)", "st_sweep": "Liquidity sweep", "st_ifvg": "Inverse FVG (IFVG)", "st_harm": "Harmonic patterns",
    "st_mss": "Market structure shift MSS / CHoCH", "st_pd": "Discount / premium zone", "st_silver": "Silver Bullet (ICT)", "st_mit": "Mitigation block",
    "st_bvd": "Breakout with delta volume", "st_smt": "SMT divergence between correlated pairs", "st_crt": "CRT (sweep of a larger candle's range and return)",
    "st_sessamd": "Session AMD", "st_orb": "Opening range breakout", "st_kzs": "Kill zone sniper", "st_po3": "Power of Three",
    "st_donch": "Donchian trend", "st_sma1040": "SMA 10/40 cross", "st_turtle55": "55-day breakout (Turtle)", "st_rsidiv": "RSI divergence",
    "st_macddiv": "MACD divergence", "st_fib": "Fibonacci", "st_vwap": "VWAP", "st_ma": "Moving averages", "st_m2022": "ICT 2022 model",
    "st_cisd": "Sweep + CISD", "st_tl": "Trendline break",
}


def _is_ar(ar) -> bool:
    if ar is not None:
        return bool(ar)
    try:
        from modules.i18n import lang
        return lang() == "ar"
    except Exception:
        return False


def flag_name(k: str, default: str = "", ar: bool | None = None) -> str:
    """Short phrase for a Radar flag in the page language (default when the flag has no phrase)."""
    return (FLAG_AR if _is_ar(ar) else FLAG_EN).get(k, default)


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
    if lower >= 2 * body[i] and upper <= 0.35 * rng[i] and body[i] > 0.05 * rng[i] and trend_up:
        out.append("hanging_man")
    if upper >= 2 * body[i] and lower <= 0.35 * rng[i] and body[i] > 0.05 * rng[i] and trend_dn:
        out.append("inverted_hammer")
    top0, bot0, top1, bot1 = max(o[i - 1], c[i - 1]), min(o[i - 1], c[i - 1]), max(o[i], c[i]), min(o[i], c[i])
    if body[i - 1] > avg_body and body[i] < 0.6 * body[i - 1] and top1 < top0 and bot1 > bot0:
        out.append("harami")
    if dn(i - 1) and up(i) and body[i - 1] > avg_body and o[i] < c[i - 1] and (o[i - 1] + c[i - 1]) / 2 < c[i] < o[i - 1]:
        out.append("piercing")
    if up(i - 1) and dn(i) and body[i - 1] > avg_body and o[i] > c[i - 1] and o[i - 1] < c[i] < (o[i - 1] + c[i - 1]) / 2:
        out.append("dark_cloud")
    if h[i] <= h[i - 1] and l[i] >= l[i - 1]:
        out.append("inside")
    return out


def ema_lines(df: pd.DataFrame, ar: bool | None = None) -> list:
    """Plain lines (Arabic or English by the page language): price vs EMA 9 / 20 / 50 / 200, their order, and a fresh 50/200 cross."""
    ar = _is_ar(ar)
    c = df["close"].astype(float)
    e = {n: c.ewm(span=n, adjust=False).mean() for n in (9, 20, 50, 200)}
    px = float(c.iloc[-1])
    role = {9: "الزخم القصير", 20: "ترند قصير", 50: "ترند متوسط", 200: "ترند طويل"} if ar else         {9: "short-term momentum", 20: "short-term trend", 50: "medium-term trend", 200: "long-term trend"}
    above = [n for n in e if px > float(e[n].iloc[-1])]
    if ar:
        lines = ["السعر " + ("فوق" if n in above else "تحت") + f" EMA {n} ({role[n]})" for n in (9, 20, 50, 200) if len(c) >= n]
    else:
        lines = ["Price " + ("above" if n in above else "below") + f" EMA {n} ({role[n]})" for n in (9, 20, 50, 200) if len(c) >= n]
    v = {n: float(e[n].iloc[-1]) for n in e}
    if px > v[9] > v[20] > v[50]:
        lines.append("ترتيب صاعد كامل (سعر > 9 > 20 > 50): ترند صاعد صحي، والشراء عند الرجوع لـ 20 أو 50." if ar else
                     "Full bullish order (price > 9 > 20 > 50): a healthy uptrend, where buying is usually looked at on pullbacks to the 20 or 50.")
    elif px < v[9] < v[20] < v[50]:
        lines.append("ترتيب هابط كامل (سعر < 9 < 20 < 50): ترند هابط صحي، والبيع عند الارتداد لـ 20 أو 50." if ar else
                     "Full bearish order (price < 9 < 20 < 50): a healthy downtrend, where selling is usually looked at on bounces to the 20 or 50.")
    elif v[9] > v[20] > v[50]:
        lines.append("المتوسطات مرتبة صاعدة (9 > 20 > 50) بس السعر تحت EMA 9: تراجع جوه ترند صاعد، مش رينج." if ar else
                     "The averages are in bullish order (9 > 20 > 50) but price is below EMA 9: a pullback inside an uptrend, not a range.")
    elif v[9] < v[20] < v[50]:
        lines.append("المتوسطات مرتبة هابطة (9 < 20 < 50) بس السعر فوق EMA 9: ارتداد جوه ترند هابط، مش رينج." if ar else
                     "The averages are in bearish order (9 < 20 < 50) but price is above EMA 9: a bounce inside a downtrend, not a range.")
    else:
        lines.append("المتوسطات متلخبطة: مفيش ترند واضح على الفريم ده، الرينج أرجح." if ar else
                     "The averages are tangled: no clear trend on this timeframe, a range is more likely.")
    if len(c) >= 210:
        d = (e[50] - e[200]).tail(10)
        if d.iloc[0] < 0 < d.iloc[-1]:
            lines.append("تقاطع ذهبي جديد (50 فوق 200) في آخر 10 شمعات." if ar else "A new golden cross (50 above 200) in the last 10 candles.")
        elif d.iloc[0] > 0 > d.iloc[-1]:
            lines.append("تقاطع موت جديد (50 تحت 200) في آخر 10 شمعات." if ar else "A new death cross (50 below 200) in the last 10 candles.")
    return lines


def explain(df: pd.DataFrame, flags, ar: bool | None = None) -> dict:
    """-> {'patterns': [(name, psychology, confirm)], 'candles': [(name, psychology, bias)], 'ema': [lines]} for one chart,
    in the page language (ar=None) or the given one."""
    ar = _is_ar(ar)
    P, C = (PATTERN_AR, CANDLE_AR) if ar else (PATTERN_EN, CANDLE_EN)
    pats = [P[k] for k in flags if k in P]
    return {"patterns": pats, "candles": [C[k] for k in candles(df)], "ema": ema_lines(df, ar) if df is not None and len(df) >= 50 else []}


def explain_both(df: pd.DataFrame, flags) -> dict:
    """{'ar': explain(..), 'en': explain(..)} - language-neutral so a cached result can be shown in either language."""
    return {"ar": explain(df, flags, True), "en": explain(df, flags, False)}
