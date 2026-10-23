"""Teaching diagrams for the Academy (the animation classes .an / .dr / .pl live in ui_kit.css(): a <style> inside the SVG would make the page hide the whole element), drawn as SVG strings (owner 2026-10-23: the pictures were not clear). Every diagram is built from numbers, so the bearish
version is the same drawing mirrored; colours come from the page's CSS variables (the Theme menu), with fallbacks. Labels are Arabic, or English when modules.i18n.lang() == 'en' (the _EN table).
Nothing here is a price forecast: the candles are illustrations made from a few waypoints, not market data."""
from __future__ import annotations

import html
import random

UP, DN = "#0ecb81", "#f6465d"
TXT, DIM, ACC, LINE = "var(--uk-text,#eaecef)", "var(--uk-dim,#8d97a5)", "var(--uk-acc,#f0b90b)", "var(--uk-line,#3a4452)"
BG = "var(--uk-panel,#161b22)"
W, H = 400, 230
PAD_L, PAD_R, PAD_T, PAD_B = 12, 12, 16, 16


def _en() -> bool:
    try:
        from modules.i18n import lang
        return lang() == "en"
    except Exception:
        return False


_EN = {
    'شمعة صاعدة': 'Bullish candle',
    'شمعة هابطة': 'Bearish candle',
    'أعلى سعر High': 'High',
    'الإغلاق Close': 'Close',
    'الافتتاح Open': 'Open',
    'أقل سعر Low': 'Low',
    'الجسم': 'Body',
    'تشريح الشمعة اليابانية': 'Anatomy of a Japanese candle',
    'دوجي': 'Doji',
    'تردد': 'Hesitation',
    'مطرقة': 'Hammer',
    'رفض هبوط': 'Rejects lows',
    'شهاب': 'Shooting star',
    'رفض صعود': 'Rejects highs',
    'ابتلاع صاعد': 'Bullish engulfing',
    'جسم يغطي اللي قبله': 'Body covers prior',
    'الشمعة وحدها إشارة ضعيفة: قيمتها من مكانها (مستوى) وسياقها (اتجاه)': 'A lone candle is weak: value comes from its level and trend context',
    'أشكال شموع شائعة': 'Common candle shapes',
    'هيكل السوق: قمم وقيعان أعلى': 'Market structure: higher highs and lows',
    'هيكل السوق: قمم وقيعان أدنى': 'Market structure: lower highs and lows',
    'كسر هذا القاع = تغيّر الهيكل (BOS)': 'Break of this low = structure change (BOS)',
    'هيكل السوق': 'Market structure',
    'دعم ومقاومة: مناطق مش خطوط': 'Support and resistance: zones, not lines',
    'دعم ومقاومة (معكوسة)': 'Support and resistance (mirrored)',
    'منطقة دعم': 'Support zone',
    'منطقة مقاومة': 'Resistance zone',
    'كسر': 'Break',
    'الدعم صار مقاومة': 'Support became resistance',
    'دعم ومقاومة': 'Support and resistance',
    '7 صفقات: 3 رابحة و4 خاسرة (نسبة نجاح 43%) ومع ذلك الصافي +2.5R': '7 trades, 3 wins and 4 losses (43%), yet net +2.5R',
    'التوقع = متوسط الصفقة = 2.5 ÷ 7 = +0.36R   |   الخط = الرصيد التراكمي': 'Expectancy = 2.5 ÷ 7 = +0.36R per trade  |  Line = running balance',
    '1R = المبلغ اللي بتخسره لو الوقف ضرب (مثلاً 1% من الحساب)': '1R = the amount lost if the stop is hit (e.g. 1% of the account)',
    'مضاعفات المخاطرة R': 'R risk multiples',
    'اختراق ثم إعادة اختبار': 'Breakout then retest',
    'كسر ثم إعادة اختبار': 'Break then retest',
    'مقاومة': 'Resistance',
    'اختراق بإغلاق وحجم': 'Breakout on a close and volume',
    'إعادة اختبار = دخول': 'Retest = entry',
    'وقف تحت المنطقة': 'Stop below the zone',
    'اختراق وإعادة اختبار': 'Breakout and retest',
    'اتجاه صاعد مع متوسط متحرك': 'Uptrend with a moving average',
    'اتجاه هابط مع متوسط متحرك': 'Downtrend with a moving average',
    'متوسط متحرك: مرجع الاتجاه': 'Moving average: the trend reference',
    'دخول مع الاتجاه عند كسر آخر قمة': 'Entry with the trend on a break of the last high',
    'وقف تحت آخر قاع (أو ATR)': 'Stop below the last low (or ATR)',
    'تتبع الاتجاه': 'Trend following',
    'العودة للمتوسط: شغّال في النطاق وبيفشل في الترند': 'Mean reversion: works in ranges, fails in trends',
    'شراء عند الحد الأدنى': 'Buy at the lower edge',
    'بيع عند الحد الأعلى': 'Sell at the upper edge',
    'ترند قوي = ممنوع تعاند': 'Strong trend = do not fight it',
    'العودة للمتوسط': 'Mean reversion',
    'جلسات اليوم (توقيت نيويورك، تقريبي)': 'Sessions of the day (New York time, approximate)',
    'آسيا: بناء نطاق': 'Asia: building a range',
    'لندن: كنس سيولة وانعكاس': 'London: liquidity sweep and reversal',
    'كنس قاع آسيا': 'Sweep of the Asia low',
    'نيويورك: استمرار أو عكس': 'New York: continue or reverse',
    'جلسات التداول': 'Trading sessions',
    'الحجم عند كل سعر (Volume Profile)': 'Volume at each price (Volume Profile)',
    'POC أعلى حجم': 'POC: highest volume',
    'VAH حد المنطقة العليا': 'VAH: upper edge of the area',
    'VAL حد المنطقة السفلى': 'VAL: lower edge of the area',
    'منطقة القيمة ≈ 70% من الحجم، والسعر بيميل يرجع لـ POC': 'Value area ≈ 70% of the volume; price tends to return to the POC',
    'بروفايل الحجم': 'Volume profile',
    'Footprint: كل سعر داخل الشمعة = بيع (يسار) × شراء (يمين)': 'Footprint: each price inside the candle = sell (left) × buy (right)',
    'شمعة 1': 'Candle 1',
    'شمعة 2: شراء عدواني': 'Candle 2: aggressive buying',
    'شمعة 3': 'Candle 3',
    'الملوّن = خلل 3:1 (طرف أقوى بـ 3 أضعاف)': 'Colored = 3:1 imbalance (one side 3x stronger)',
    'امتصاص: حجم كبير عند مستوى والسعر ما كملش': 'Absorption: large volume at a level and price did not continue',
    'الفريم الكبير: الاتجاه': 'Large timeframe: direction',
    'الفريم المتوسط: التراجع للمنطقة': 'Middle timeframe: pullback to the zone',
    'الفريم الصغير: المحفز': 'Small timeframe: the trigger',
    'منطقة': 'Zone',
    'دخول': 'Entry',
    'الفريمات المتعددة': 'Multiple timeframes',
    'سحب سيولة ← إزاحة ← Order Block / FVG': 'Liquidity sweep → displacement → Order Block / FVG',
    'سيولة تحت القاع': 'Liquidity under the low',
    'كنس السيولة': 'Liquidity sweep',
    'FVG فجوة': 'FVG gap',
    'دخول عند الرجوع': 'Entry on the return',
    'مفاهيم SMC': 'SMC concepts',
    'نموذج Gartley (صعودي)': 'Gartley pattern (bullish)',
    'نموذج Gartley (هبوطي)': 'Gartley pattern (bearish)',
    'B = 0.618 من XA': 'B = 0.618 of XA',
    'D = 0.786 من XA': 'D = 0.786 of XA',
    'منطقة انعكاس PRZ': 'Reversal zone PRZ',
    'نموذج هارمونيك': 'Harmonic pattern',
    'موجة دافعة 1-2-3-4-5 ثم تصحيح A-B-C': 'Impulse wave 1-2-3-4-5 then correction A-B-C',
    'الموجة 4 ما تدخلش تحت قمة 1': 'Wave 4 must not drop below the top of 1',
    'الموجة 2 ما تنزلش تحت البداية': 'Wave 2 must not fall below the start',
    'موجات إليوت': 'Elliott waves',
    'مروحة جان من قاع مهم': 'Gann fan from an important low',
    'فوق 1×1 = قوة، تحتها = ضعف (رأي، مش دليل)': 'Above 1×1 = strength, below it = weakness (opinion, not proof)',
    'مروحة جان': 'Gann fan',
    'عينة التدريب (تحسين الإعدادات)': 'Training (settings tuned)',
    'عينة الاختبار: دي الوحيدة اللي بنصدّقها': 'Test sample: the only one we trust',
    'خط منقط = قبل التكلفة | أخضر = بعد التكلفة | أحمر = نفس الاستراتيجية خارج العينة': 'Dotted = before cost | green = after cost | red = out of sample',
    'الباك تست بأمانة': 'Honest backtesting',
    'حالة السوق': 'Market state',
    'ترند ولا نطاق؟': 'Trend or range?',
    'الفريم الأكبر': 'Higher TF',
    'مع الاتجاه؟': 'With the trend?',
    'الموقع': 'Location',
    'عند مستوى/منطقة؟': 'At a level?',
    'المحفز': 'Trigger',
    'اختراق/رفض/كنس': 'Break/sweep',
    'تأكيد عند المستوى': 'Confirm at level',
    'التوقيت': 'Timing',
    'جلسة مناسبة؟': 'Right session?',
    'الخطة': 'The plan',
    'وقف وهدف وR≥1.5': 'Stop/TP, R≥1.5',
    'أي «لا» = ماتدخلش': 'Any no = skip',
    'سجّل كل صفقة (حتى الممتنع عنها): من غير سجل مفيش قياس': 'Log every trade (even skipped): no log, no measurement',
    'قائمة التحقق قبل الصفقة': 'Pre-trade checklist',
}
_EN_KEYS = sorted(_EN, key=len, reverse=True)


def _t(s: str) -> str:
    """English-mode label (owner 2026-10-23: one language at a time); Arabic mode returns the label unchanged."""
    if not _en():
        return s
    if s in _EN:
        return _EN[s]
    for k in _EN_KEYS:
        if k in s:
            s = s.replace(k, _EN[k])
    return s


def _e(s) -> str:
    return html.escape(_t(str(s)))


def waypoints(points: list, per_leg: int = 5, seed: int = 7, noise: float = 0.18) -> list:
    """Candles (o, h, l, c) that walk through the price waypoints; deterministic wiggle so every diagram looks the same on every run."""
    rnd = random.Random(seed)
    closes = []
    for a, b in zip(points, points[1:]):
        for k in range(1, per_leg + 1):
            base = a + (b - a) * k / per_leg
            closes.append(base + (rnd.random() - 0.5) * abs(b - a) * noise)
    out, prev = [], points[0]
    for c in closes:
        wick = abs(c - prev) * 0.35 + 0.15
        out.append((prev, max(prev, c) + rnd.random() * wick, min(prev, c) - rnd.random() * wick, c))
        prev = c
    return out


class Chart:
    """A small price panel: candles plus annotations placed by candle index and price."""

    def __init__(self, candles: list, w: int = W, h: int = H, mirror: bool = False, lo=None, hi=None, x0: int = 0, y0: int = 0, title: str = ""):
        self.c, self.w, self.h, self.x0, self.y0, self.mirror, self.title = candles, w, h, x0, y0, mirror, title
        vals = [v for k in candles for v in k[1:3]]
        a_, b_ = (min(vals) if vals else 0), (max(vals) if vals else 1)
        pad = (b_ - a_) * 0.07                                       # headroom so labels and the title do not sit on the candles
        self.lo, self.hi = (a_ - pad if lo is None else lo), (b_ + pad if hi is None else hi)
        self.parts: list = []
        self.n = max(1, len(candles))
        self.step = (w - PAD_L - PAD_R) / self.n

    def y(self, p: float) -> float:
        if self.mirror:
            p = self.lo + self.hi - p
        return self.y0 + PAD_T + (self.hi - p) / (self.hi - self.lo or 1) * (self.h - PAD_T - PAD_B)

    def x(self, i: float) -> float:
        return self.x0 + PAD_L + (i + 0.5) * self.step

    def add(self, s: str):
        self.parts.append(s)
        return self

    def candles(self, bodies: float = 0.62):
        bw = max(2.0, self.step * bodies)
        for i, (o, h, l, c) in enumerate(self.c):
            up = (c >= o) != self.mirror
            col = UP if up else DN
            x = self.x(i)
            top, bot = sorted((self.y(o), self.y(c)))
            self.add(f"<g class='an' style='animation-delay:{i * 0.03:.2f}s'><line x1='{x:.1f}' x2='{x:.1f}' y1='{self.y(h):.1f}' y2='{self.y(l):.1f}' stroke='{col}' stroke-width='1.2'/>"
                     f"<rect x='{x - bw / 2:.1f}' y='{top:.1f}' width='{bw:.1f}' height='{max(1.2, bot - top):.1f}' fill='{col}' rx='1'/></g>")
        return self

    def hline(self, p, label="", color=ACC, dash="5 4", x1=0, x2=None):
        y = self.y(p)
        xa, xb = self.x(x1) - self.step / 2, (self.x(x2) if x2 is not None else self.x0 + self.w - PAD_R)
        self.add(f"<line x1='{xa:.1f}' x2='{xb:.1f}' y1='{y:.1f}' y2='{y:.1f}' stroke='{color}' stroke-width='1.3' stroke-dasharray='{dash}'/>")
        if label:
            self.text(self.x0 + self.w - PAD_R - 2, y - 3, label, color, anchor="end")
        return self

    def zone(self, p1, p2, i1=0, i2=None, label="", color=ACC, op=0.16):
        ya, yb = sorted((self.y(p1), self.y(p2)))
        xa = self.x(i1) - self.step / 2
        xb = (self.x(i2) + self.step / 2) if i2 is not None else self.x0 + self.w - PAD_R
        self.add(f"<rect class='an' style='animation-delay:.9s' x='{xa:.1f}' y='{ya:.1f}' width='{xb - xa:.1f}' height='{max(2.0, yb - ya):.1f}' fill='{color}' opacity='{op}' stroke='{color}' stroke-opacity='.6' rx='2'/>")
        if label:
            self.text(xa + 4, ya + 11, label, color)
        return self

    def line(self, a, b, color=ACC, dash="", width=1.6, label="", arrow=False):
        (i1, p1), (i2, p2) = a, b
        self.add(f"<line x1='{self.x(i1):.1f}' y1='{self.y(p1):.1f}' x2='{self.x(i2):.1f}' y2='{self.y(p2):.1f}' stroke='{color}' stroke-width='{width}' "
                 f"{'stroke-dasharray=' + repr(dash) if dash else ''}{' marker-end=' + repr('url(#ar)') if arrow else ''}/>")
        if label:
            self.text((self.x(i1) + self.x(i2)) / 2, (self.y(p1) + self.y(p2)) / 2 - 5, label, color, anchor="middle")
        return self

    def poly(self, pts, color=ACC, width=2.0, dash=""):
        d = " ".join(f"{self.x(i):.1f},{self.y(p):.1f}" for i, p in pts)
        self.add(f"<polyline {'class=' + repr('dr') if not dash else ''} points='{d}' fill='none' stroke='{color}' stroke-width='{width}' stroke-linejoin='round' {'stroke-dasharray=' + repr(dash) if dash else ''}/>")
        return self

    def text(self, x, y, s, color=TXT, size=10.5, anchor="start", weight="600"):
        s = _t(str(s))
        half = len(str(s)) * size * 0.52 / 2                         # rough text width, so labels never leave the panel
        lo, hi = self.x0 + 6, self.x0 + self.w - 6
        if anchor == "middle":
            x = min(max(x, lo + half), hi - half)
        elif anchor == "start" and x + 2 * half > hi:
            x, anchor = min(x, hi), "end"
        elif anchor == "end" and x - 2 * half < lo:
            x, anchor = max(x, lo), "start"
        self.add(f"<text x='{x:.1f}' y='{y:.1f}' fill='{color}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' stroke='{BG}' stroke-width='3.2' paint-order='stroke' "
                 f"stroke-linejoin='round' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>{_e(s)}</text>")
        return self

    def tag(self, i, p, s, color=ACC, dy=-9, dot=True):
        """dy is written for the bullish drawing (negative = above the point); the mirrored drawing flips it automatically."""
        x, y = self.x(i), self.y(p)
        if self.mirror:
            dy = 6 - dy if dy < 0 else -dy - 2
        if dot:
            self.add(f"<circle class='pl' cx='{x:.1f}' cy='{y:.1f}' r='3.4' fill='{color}'/>")
            if abs(dy) >= 8:                                           # arrow from the label to the point it explains
                ya = y + (dy + (3 if dy < 0 else -11))
                yb = y + (-5 if dy < 0 else 5)
                self.add(f"<line x1='{x:.1f}' y1='{ya:.1f}' x2='{x:.1f}' y2='{yb:.1f}' stroke='{color}' stroke-width='1.3' marker-end='url(#ar)' opacity='.85'/>")
        return self.text(x, y + dy, s, color, anchor="middle")

    def body(self) -> str:
        t = f"<text x='{self.x0 + self.w / 2:.0f}' y='{self.y0 + 11}' fill='{DIM}' font-size='10' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>{_e(self.title)}</text>" if self.title else ""
        return t + "".join(self.parts)


def svg(*parts: str, w: int = W, h: int = H, alt: str = "") -> str:
    defs = (f"<defs><marker id='ar' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='6' markerHeight='6' orient='auto-start-reverse'><path d='M0 0L10 5L0 10z' fill='{ACC}'/></marker></defs>")
    return (f"<svg viewBox='0 0 {w} {h}' width='100%' direction='ltr' style='direction:ltr;max-width:{w * 1.5:.0f}px;background:{BG};border:1px solid {LINE};border-radius:10px' role='img' aria-label='{_e(alt)}'>"
            f"{defs}{''.join(parts)}</svg>")


def _pick(side: str, bull, bear):
    return bear if side == "bear" else bull


# ---- the diagrams -----------------------------------------------------------------------------------------------------------------------------

def candles_anatomy(side: str = "bull") -> str:
    out = []
    for cx, up, name in ((110, True, "شمعة صاعدة"), (290, False, "شمعة هابطة")):
        col = UP if up else DN
        top_w, bot_w, hi, lo = (70, 120, 36, 196) if up else (70, 120, 36, 196)
        o, c_ = (150, 80) if up else (80, 150)
        out.append(f"<line x1='{cx}' x2='{cx}' y1='{hi}' y2='{lo}' stroke='{col}' stroke-width='3'/><rect x='{cx - 22}' y='{min(o, c_)}' width='44' height='{abs(o - c_)}' fill='{col}' rx='3'/>")
        out.append(f"<text x='{cx}' y='222' fill='{TXT}' font-size='12' text-anchor='middle' font-weight='700' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>{name}</text>")
        lab = (("أعلى سعر High", hi, 1), ("الإغلاق Close" if up else "الافتتاح Open", c_ if up else o, 1), ("الافتتاح Open" if up else "الإغلاق Close", o if up else c_, 1), ("أقل سعر Low", lo, 1))
        for k, (t, y, _s) in enumerate(lab):
            x2 = cx + 40 if up else cx - 40
            out.append(f"<line x1='{cx + (24 if up else -24)}' x2='{x2 + (6 if up else -6)}' y1='{y}' y2='{y}' stroke='{LINE}' stroke-dasharray='3 3'/>"
                       f"<text x='{x2 + (10 if up else -10)}' y='{y + 4}' fill='{DIM}' font-size='10.5' text-anchor='{'start' if up else 'end'}' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>{t}</text>")
        out.append(f"<text x='{cx + (-30 if up else 30)}' y='{(o + c_) / 2 + 4}' fill='{TXT}' font-size='10' text-anchor='{'end' if up else 'start'}' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>الجسم</text>")
    return svg("".join(out), alt="تشريح الشمعة اليابانية")


def candle_patterns(side: str = "bull") -> str:
    def one(cx, o, h, l, c, name, note, hl=False):
        col = UP if c >= o else DN
        top, bot = sorted((o, c))
        s = (f"<line x1='{cx}' x2='{cx}' y1='{h}' y2='{l}' stroke='{col}' stroke-width='2.4'/><rect x='{cx - 12}' y='{top}' width='24' height='{max(2, bot - top)}' fill='{col}' rx='2'/>")
        s += f"<text x='{cx}' y='196' fill='{TXT}' font-size='11' text-anchor='middle' font-weight='700' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>{name}</text>"
        s += f"<text x='{cx}' y='211' fill='{DIM}' font-size='9.5' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>{note}</text>"
        return s
    parts = [one(50, 100, 60, 140, 102, "دوجي", "تردد"), one(130, 80, 78, 150, 92, "مطرقة", "رفض هبوط"), one(210, 70, 52, 80, 62, "شهاب", "رفض صعود")]
    parts.append(f"<line x1='290' x2='290' y1='70' y2='150' stroke='{DN}' stroke-width='2'/><rect x='282' y='95' width='16' height='28' fill='{DN}' rx='2'/>")
    parts.append(f"<line x1='322' x2='322' y1='60' y2='160' stroke='{UP}' stroke-width='2'/><rect x='310' y='80' width='24' height='62' fill='{UP}' rx='2'/>")
    parts.append(f"<text x='306' y='196' fill='{TXT}' font-size='11' text-anchor='middle' font-weight='700' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>ابتلاع صاعد</text>"
                 f"<text x='306' y='211' fill='{DIM}' font-size='9.5' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>جسم يغطي اللي قبله</text>")
    parts.append(f"<text x='200' y='22' fill='{DIM}' font-size='10' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>الشمعة وحدها إشارة ضعيفة: قيمتها من مكانها (مستوى) وسياقها (اتجاه)</text>")
    return svg("".join(parts), alt="أشكال شموع شائعة")


def structure(side: str = "bull") -> str:
    m = side == "bear"
    c = Chart(waypoints([100, 112, 106, 121, 113, 131, 123, 140], 4, 3), mirror=m, title="هيكل السوق: قمم وقيعان أعلى" if not m else "هيكل السوق: قمم وقيعان أدنى")
    c.candles()
    pts = [(4, 112), (8, 106), (12, 121), (16, 113), (20, 131), (24, 123)]
    names = ["HH", "HL", "HH", "HL", "HH", "HL"] if not m else ["LL", "LH", "LL", "LH", "LL", "LH"]
    for k, ((i, p), n) in enumerate(zip(pts, names)):
        c.tag(i - 1, p, n, UP if not m else DN, dy=-9 if k % 2 == 0 else 15)        # even = a high, odd = a low (the mirror flips the side)
    c.hline(106, "كسر هذا القاع = تغيّر الهيكل (BOS)", DN if not m else UP, x1=8, x2=24)
    return svg(c.body(), alt="هيكل السوق")


def support_resistance(side: str = "bull") -> str:
    m = side == "bear"
    pts = [104, 100, 109, 100.6, 109.4, 100.2, 108.6, 99, 94, 99.2, 93, 91]
    c = Chart(waypoints(pts, 4, 5, 0.1), mirror=m, title="دعم ومقاومة: مناطق مش خطوط" if not m else "دعم ومقاومة (معكوسة)")
    c.candles()
    c.zone(99.2, 101.2, 0, 24, "منطقة دعم", UP if not m else DN).zone(108.2, 110, 0, 24, "منطقة مقاومة", DN if not m else UP)
    c.tag(20, 99.2, "كسر", DN if not m else UP, dy=15)
    c.tag(36, 99.2, "الدعم صار مقاومة", ACC, dy=-9)
    return svg(c.body(), alt="دعم ومقاومة")


def risk_r(side: str = "bull") -> str:
    rs = [-1, -1, 3, -1, 2, -1, 1.5]
    cum, t = [], 0.0
    for r in rs:
        t += r
        cum.append(t)
    x0, bw, gap, base, k = 30, 34, 14, 120, 20
    p = []
    for i, r in enumerate(rs):
        x = x0 + i * (bw + gap)
        col = UP if r > 0 else DN
        h = abs(r) * k
        p.append(f"<rect x='{x}' y='{base - h if r > 0 else base}' width='{bw}' height='{h}' fill='{col}' rx='2'/>"
                 f"<text x='{x + bw / 2}' y='{base - h - 4 if r > 0 else base + h + 11}' fill='{TXT}' font-size='10.5' text-anchor='middle' font-weight='700' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>{r:+g}R</text>")
    pts = " ".join(f"{x0 + i * (bw + gap) + bw / 2},{base - c_ * k}" for i, c_ in enumerate(cum))
    p.append(f"<line x1='20' x2='380' y1='{base}' y2='{base}' stroke='{LINE}'/><polyline points='{pts}' fill='none' stroke='{ACC}' stroke-width='2.4'/>")
    p.append(f"<text x='200' y='20' fill='{TXT}' font-size='11.5' text-anchor='middle' font-weight='700' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>7 صفقات: 3 رابحة و4 خاسرة (نسبة نجاح 43%) ومع ذلك الصافي +2.5R</text>")
    p.append(f"<text x='200' y='38' fill='{DIM}' font-size='10.5' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>التوقع = متوسط الصفقة = 2.5 ÷ 7 = +0.36R   |   الخط = الرصيد التراكمي</text>")
    p.append(f"<text x='200' y='222' fill='{DIM}' font-size='10' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>1R = المبلغ اللي بتخسره لو الوقف ضرب (مثلاً 1% من الحساب)</text>")
    return svg("".join(p), alt="مضاعفات المخاطرة R")


def breakout(side: str = "bull") -> str:
    m = side == "bear"
    pts = [103, 109, 104.5, 109.2, 105, 109.4, 116, 110.6, 118, 122]
    cs = waypoints(pts, 4, 11, 0.12)
    c = Chart(cs, mirror=m, title="اختراق ثم إعادة اختبار" if not m else "كسر ثم إعادة اختبار")
    c.candles().zone(108.4, 110.2, 0, 22, "مقاومة", DN if not m else UP)
    c.tag(24, 116, "اختراق بإغلاق وحجم", ACC, dy=-9)
    c.tag(28, 110.6, "إعادة اختبار = دخول", UP if not m else DN, dy=16)
    c.hline(107, "وقف تحت المنطقة", DN if not m else UP, x1=24)
    return svg(c.body(), alt="اختراق وإعادة اختبار")


def trend(side: str = "bull") -> str:
    m = side == "bear"
    cs = waypoints([100, 108, 105, 114, 110, 121, 117, 128, 125, 135], 4, 2, 0.15)
    c = Chart(cs, mirror=m, title="اتجاه صاعد مع متوسط متحرك" if not m else "اتجاه هابط مع متوسط متحرك")
    c.candles()
    cl = [k[3] for k in cs]
    ma = [sum(cl[max(0, i - 7):i + 1]) / len(cl[max(0, i - 7):i + 1]) for i in range(len(cl))]
    c.poly([(i, v) for i, v in enumerate(ma)], ACC, 2.0)
    c.text(c.x0 + 16, c.y(ma[2]) + 30, "متوسط متحرك: مرجع الاتجاه", ACC)
    c.tag(18, cs[18][3], "دخول مع الاتجاه عند كسر آخر قمة", UP if not m else DN, dy=-10)
    c.tag(15, min(k[2] for k in cs[13:17]), "وقف تحت آخر قاع (أو ATR)", DN if not m else UP, dy=16)
    return svg(c.body(), alt="تتبع الاتجاه")


def mean_reversion(side: str = "bull") -> str:
    m = side == "bear"
    pts = [100, 106, 98, 105, 99, 107, 99, 104, 100, 112, 119, 126]
    cs = waypoints(pts, 4, 8, 0.12)
    c = Chart(cs, mirror=m, lo=88, hi=130, title="العودة للمتوسط: شغّال في النطاق وبيفشل في الترند")
    c.candles()
    cl = [k[3] for k in cs]
    mean, up, lo_ = [], [], []
    for i in range(len(cl)):
        w = cl[max(0, i - 11):i + 1]
        mu = sum(w) / len(w)
        sd = (sum((x - mu) ** 2 for x in w) / len(w)) ** 0.5
        mean.append(mu); up.append(mu + 1.7 * sd + 1.5); lo_.append(mu - 1.7 * sd - 1.5)
    c.poly(list(enumerate(up)), DIM, 1.2, "4 3").poly(list(enumerate(lo_)), DIM, 1.2, "4 3").poly(list(enumerate(mean)), ACC, 1.6)
    c.tag(8, cl[8], "شراء عند الحد الأدنى", UP if not m else DN, dy=16).tag(21, cl[21], "بيع عند الحد الأعلى", DN if not m else UP, dy=-9)
    c.tag(42, cl[42], "ترند قوي = ممنوع تعاند", ACC, dy=-9)
    return svg(c.body(), alt="العودة للمتوسط")


def sessions(side: str = "bull") -> str:
    m = side == "bear"
    pts = [100, 102, 100.5, 102.2, 100.8, 98.4, 104, 108, 106.5, 111]
    cs = waypoints(pts, 4, 4, 0.12)
    c = Chart(cs, mirror=m, title="جلسات اليوم (توقيت نيويورك، تقريبي)")
    c.candles()
    c.zone(100.2, 102.6, 0, 15, "آسيا: بناء نطاق", DIM, 0.14).zone(95, 112, 16, 27, "", ACC, 0.06)
    c.add(f"<text x='{c.x(21):.0f}' y='{c.y(96.3):.0f}' fill='{ACC}' font-size='10.5' text-anchor='middle' font-weight='700' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>لندن: كنس سيولة وانعكاس</text>")
    c.hline(100.2, "", DIM, "3 3", 0, 22)
    c.tag(19, 98.4, "كنس قاع آسيا", DN if not m else UP, dy=15)
    c.tag(33, 108, "نيويورك: استمرار أو عكس", UP if not m else DN, dy=-10)
    c.text(c.x(1), c.y(94.2), "20:00 → 00:00", DIM, 9.5).text(c.x(17), c.y(94.2), "02:00 → 05:00", DIM, 9.5).text(c.x(30), c.y(94.2), "07:00 → 10:00", DIM, 9.5)
    return svg(c.body(), alt="جلسات التداول")


def volume_profile(side: str = "bull") -> str:
    prices = list(range(100, 121))
    vol = [max(2, int(40 * 2.718 ** (-((p - 108) / 5.0) ** 2) + (12 if p in (112, 113) else 0))) for p in prices]
    tot = sum(vol)
    poc = prices[vol.index(max(vol))]
    acc, area = vol.index(max(vol)), {poc}
    s = vol[acc]
    lo_i = hi_i = acc
    while s < 0.7 * tot:
        a = vol[lo_i - 1] if lo_i > 0 else -1
        b = vol[hi_i + 1] if hi_i < len(vol) - 1 else -1
        if a >= b:
            lo_i -= 1; s += vol[lo_i]
        else:
            hi_i += 1; s += vol[hi_i]
    val, vah = prices[lo_i], prices[hi_i]
    y = lambda p: 200 - (p - 99) * 8.6
    p = []
    cs = waypoints([101, 106, 104, 112, 109, 118, 110, 108], 3, 9, 0.2)
    ch = Chart(cs, 190, 230, lo=99, hi=121, title="")
    ch.candles(0.55)
    p.append(ch.body())
    p.append(f"<text x='290' y='14' fill='{DIM}' font-size='10' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>الحجم عند كل سعر (Volume Profile)</text>")
    for pr, v in zip(prices, vol):
        inside = val <= pr <= vah
        col = ACC if pr == poc else ("#6aa7ff" if inside else DIM)
        p.append(f"<rect x='200' y='{y(pr) - 3.6:.1f}' width='{v * 3.2:.1f}' height='7' fill='{col}' opacity='{0.95 if inside else 0.5}' rx='1.5'/>")
    for lbl, pr, col in (("POC أعلى حجم", poc, ACC), ("VAH حد المنطقة العليا", vah, "#6aa7ff"), ("VAL حد المنطقة السفلى", val, "#6aa7ff")):
        p.append(f"<line x1='20' x2='395' y1='{y(pr):.1f}' y2='{y(pr):.1f}' stroke='{col}' stroke-dasharray='4 4' opacity='.7'/>"
                 f"<text x='392' y='{y(pr) - 3:.1f}' fill='{col}' font-size='10' text-anchor='end' font-weight='700' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>{lbl}</text>")
    p.append(f"<text x='200' y='225' fill='{DIM}' font-size='9' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>منطقة القيمة ≈ 70% من الحجم، والسعر بيميل يرجع لـ POC</text>")
    return svg("".join(p), alt="بروفايل الحجم")


def order_flow(side: str = "bull") -> str:
    p = [f"<text x='200' y='16' fill='{DIM}' font-size='10' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>Footprint: كل سعر داخل الشمعة = بيع (يسار) × شراء (يمين)</text>"]
    cols = [(60, [(103, "40×18"), (102, "55×31"), (101, "90×60"), (100, "120×190"), (99, "70×40")], "شمعة 1"),
            (200, [(103, "10×35"), (102, "22×80"), (101, "35×210"), (100, "30×95"), (99, "8×20")], "شمعة 2: شراء عدواني"),
            (330, [(103, "6×14"), (102, "12×18"), (101, "20×25"), (100, "15×22"), (99, "9×11")], "شمعة 3")]
    for cx, rows, name in cols:
        for k, (pr, txt) in enumerate(rows):
            y = 40 + k * 28
            a, b = [int(v) for v in txt.split("×")]
            imb = b >= 3 * a or a >= 3 * b
            col = UP if b >= 3 * a else DN if a >= 3 * b else None
            p.append(f"<rect x='{cx - 52}' y='{y}' width='104' height='24' fill='{col or LINE}' opacity='{0.35 if col else 0.18}' rx='3'/>"
                     f"<text x='{cx}' y='{y + 16}' fill='{TXT}' font-size='11' text-anchor='middle' font-weight='{'800' if imb else '500'}' font-family='ui-monospace,Consolas,monospace'>{txt}</text>")
            if cx == 60:
                p.append(f"<text x='{cx - 58}' y='{y + 16}' fill='{DIM}' font-size='9' text-anchor='end' font-family='ui-monospace,Consolas,monospace'>{pr}</text>")
        p.append(f"<text x='{cx}' y='194' fill='{TXT}' font-size='10.5' text-anchor='middle' font-weight='700' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>{name}</text>")
    p.append(f"<text x='200' y='207' fill='{DIM}' font-size='9.5' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>الملوّن = خلل 3:1 (طرف أقوى بـ 3 أضعاف)</text>")
    p.append(f"<text x='200' y='221' fill='{DIM}' font-size='9.5' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>امتصاص: حجم كبير عند مستوى والسعر ما كملش</text>")
    return svg("".join(p), alt="Footprint")


def mtf(side: str = "bull") -> str:
    m = side == "bear"
    p = []
    panels = [("الفريم الكبير: الاتجاه", [100, 104, 102, 108, 106, 113], 0), ("الفريم المتوسط: التراجع للمنطقة", [110, 113, 109.5, 111, 108.5, 109.5], 77), ("الفريم الصغير: المحفز", [109, 108.6, 109.2, 108.8, 110.4, 111.6], 154)]
    for k, (t, pts, y0) in enumerate(panels):
        c = Chart(waypoints(pts, 3, 20 + k, 0.15), 400, 76, mirror=m, y0=y0, title=t)
        c.candles(0.55)
        if k == 1:
            c.zone(108.3, 109.8, 0, 14, "منطقة", ACC)
        if k == 2:
            c.tag(11, 110.4, "دخول", UP if not m else DN, dy=-8)
        p.append(c.body())
    return svg("".join(p), h=230, alt="الفريمات المتعددة")


def smc(side: str = "bull") -> str:
    m = side == "bear"
    pts = [108, 104, 105.5, 102.5, 101, 100, 99.2, 107, 112, 109.4, 111.4, 116]
    cs = waypoints(pts, 3, 6, 0.1)
    c = Chart(cs, mirror=m, title="سحب سيولة ← إزاحة ← Order Block / FVG")
    c.candles()
    c.hline(100.4, "سيولة تحت القاع", DIM, "3 3", 3, 14)
    c.tag(18, 99.2, "كنس السيولة", DN if not m else UP, dy=15)
    c.zone(99.4, 101.6, 15, 17, "OB", ACC, 0.25)
    c.zone(103.6, 105.4, 19, 23, "FVG فجوة", "#6aa7ff", 0.22)
    c.tag(29, 109.4, "دخول عند الرجوع", UP if not m else DN, dy=16)
    return svg(c.body(), alt="مفاهيم SMC")


def harmonic(side: str = "bull") -> str:
    m = side == "bear"
    X, A = 100.0, 130.0
    B = A - 0.618 * (A - X)
    C = B + 0.618 * (A - B)
    D = A - 0.786 * (A - X)
    c = Chart(waypoints([X, A, B, C, D, D + 9], 4, 13, 0.1), mirror=m, lo=94, hi=134, title="نموذج Gartley (صعودي)" if not m else "نموذج Gartley (هبوطي)")
    c.candles(0.45)
    idx = {"X": 0, "A": 4, "B": 8, "C": 12, "D": 16}
    price = {"X": X, "A": A, "B": B, "C": C, "D": D}
    c.poly([(idx[k], price[k]) for k in "XABCD"], ACC, 2.0)
    for k in "XABCD":
        c.tag(idx[k], price[k], k, ACC, dy=-9 if k in "AC" else 15)
    c.text(c.x(5), c.y(116) + 0, "B = 0.618 من XA", DIM, 9.5).text(c.x(14.5), c.y(105), "D = 0.786 من XA", DIM, 9.5)
    c.tag(18, D + 3.5, "منطقة انعكاس PRZ", UP if not m else DN, dy=-9, dot=False)
    return svg(c.body(), alt="نموذج هارمونيك")


def elliott(side: str = "bull") -> str:
    m = side == "bear"
    pts = {"0": (0, 100), "1": (5, 112), "2": (9, 106), "3": (17, 134), "4": (22, 122), "5": (29, 142), "A": (34, 128), "B": (38, 136), "C": (46, 114)}
    seq = [pts[k] for k in pts]
    cs = waypoints([p for _, p in seq], 4, 17, 0.08)
    c = Chart(cs, mirror=m, title="موجة دافعة 1-2-3-4-5 ثم تصحيح A-B-C")
    c.candles(0.42)
    c.poly([(i * 1, p) for (i, p) in [(k * 4, pr) for k, (_, pr) in enumerate(seq)]], ACC, 1.8, "5 3")
    for n, (k, (_, pr)) in zip(pts, enumerate(seq)):
        c.tag(k * 4, pr, n, ACC, dy=-9 if n in "135B" else 15)
    c.hline(112, "الموجة 4 ما تدخلش تحت قمة 1", DN if not m else UP, "3 3", 20, 28)
    c.hline(100, "الموجة 2 ما تنزلش تحت البداية", DN if not m else UP, "3 3", 4, 12)
    return svg(c.body(), alt="موجات إليوت")


def gann(side: str = "bull") -> str:
    m = side == "bear"
    cs = waypoints([100, 107, 105, 113, 111, 119, 116, 124], 4, 3, 0.12)
    c = Chart(cs, mirror=m, lo=96, hi=128, title="مروحة جان من قاع مهم")
    c.candles(0.5)
    n = len(cs) - 1
    for name, slope in (("1×2", 0.35), ("1×1", 0.7), ("2×1", 1.4)):
        c.line((0, 100), (n, 100 + slope * n * 0.62), ACC if name == "1×1" else DIM, "" if name == "1×1" else "4 3", 1.8 if name == "1×1" else 1.2)
        c.text(c.x(n) - 2, c.y(100 + slope * n * 0.62) - 3, name, ACC if name == "1×1" else DIM, 10, "end")
    c.text(c.x(1), c.y(97.2), "فوق 1×1 = قوة، تحتها = ضعف (رأي، مش دليل)", DIM, 9.5)
    return svg(c.body(), alt="مروحة جان")


def backtest_honesty(side: str = "bull") -> str:
    p = []
    x = lambda i: 20 + i * 18
    ins = [100, 103, 101, 106, 110, 108, 114, 118, 121, 120]
    oos = [120, 118, 121, 117, 115, 118, 113, 111, 112, 108]
    cost = [100, 102, 99.6, 104, 107, 104.6, 109.6, 112.4, 114.2, 112.2]
    y = lambda v: 200 - (v - 98) * 4.1
    p.append(f"<rect x='{x(9)}' y='24' width='{x(21) - x(9) + 6}' height='176' fill='{ACC}' opacity='.08' rx='4'/><line x1='{x(9)}' x2='{x(9)}' y1='24' y2='200' stroke='{ACC}' stroke-dasharray='5 4'/>")
    p.append(f"<polyline fill='none' stroke='{DIM}' stroke-width='1.6' stroke-dasharray='4 3' points='" + " ".join(f"{x(i)},{y(v)}" for i, v in enumerate(ins)) + "'/>")
    p.append(f"<polyline fill='none' stroke='{UP}' stroke-width='2.4' points='" + " ".join(f"{x(i)},{y(v)}" for i, v in enumerate(cost)) + "'/>")
    p.append(f"<polyline fill='none' stroke='{DN}' stroke-width='2.4' points='" + " ".join(f"{x(9 + i)},{y(v)}" for i, v in enumerate(oos)) + "'/>")
    for t, xx, col in (("عينة التدريب (تحسين الإعدادات)", x(4), TXT), ("عينة الاختبار: دي الوحيدة اللي بنصدّقها", x(15), ACC)):
        p.append(f"<text x='{xx}' y='20' fill='{col}' font-size='10.5' text-anchor='middle' font-weight='700' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>{t}</text>")
    p.append(f"<text x='{x(1)}' y='218' fill='{DIM}' font-size='10' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>خط منقط = قبل التكلفة | أخضر = بعد التكلفة | أحمر = نفس الاستراتيجية خارج العينة</text>")
    return svg("".join(p), alt="الباك تست بأمانة")


def checklist(side: str = "bull") -> str:
    steps = [("1", "حالة السوق", "ترند ولا نطاق؟"), ("2", "الفريم الأكبر", "مع الاتجاه؟"), ("3", "الموقع", "عند مستوى/منطقة؟"), ("4", "المحفز", "اختراق/رفض/كنس"),
             ("5", "Order flow", "تأكيد عند المستوى"), ("6", "التوقيت", "جلسة مناسبة؟"), ("7", "الخطة", "وقف وهدف وR≥1.5")]
    p = []
    for k, (n, t, s) in enumerate(steps):
        col, row = k % 4, k // 4
        x, y = 14 + col * 96, 24 + row * 98
        p.append(f"<rect x='{x}' y='{y}' width='88' height='84' rx='10' fill='{BG}' stroke='{ACC if k in (2, 6) else LINE}' stroke-width='1.6'/>"
                 f"<circle cx='{x + 16}' cy='{y + 18}' r='11' fill='{ACC}'/><text x='{x + 16}' y='{y + 22}' fill='#111' font-size='12' text-anchor='middle' font-weight='800' font-family='system-ui,sans-serif'>{n}</text>"
                 f"<text x='{x + 44}' y='{y + 46}' fill='{TXT}' font-size='11.5' text-anchor='middle' font-weight='700' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>{t}</text>"
                 f"<text x='{x + 44}' y='{y + 64}' fill='{DIM}' font-size='9.5' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>{s}</text>")
        if col < 3 and k < 6:
            p.append(f"<text x='{x + 91}' y='{y + 46}' fill='{DIM}' font-size='14' text-anchor='middle'>←</text>")
    p.append(f"<text x='{14 + 3 * 96 + 44}' y='{24 + 98 + 46}' fill='{DIM}' font-size='10' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>أي «لا» = ماتدخلش</text>")
    p.append(f"<text x='200' y='222' fill='{DIM}' font-size='9.5' text-anchor='middle' font-family='system-ui,Segoe UI,Tahoma,sans-serif'>سجّل كل صفقة (حتى الممتنع عنها): من غير سجل مفيش قياس</text>")
    return svg("".join(p), alt="قائمة التحقق قبل الصفقة")


ART = {"candles": candles_anatomy, "patterns": candle_patterns, "structure": structure, "sr": support_resistance, "risk": risk_r, "breakout": breakout, "trend": trend,
       "meanrev": mean_reversion, "sessions": sessions, "vp": volume_profile, "orderflow": order_flow, "mtf": mtf, "smc": smc, "harmonic": harmonic, "elliott": elliott,
       "gann": gann, "backtest": backtest_honesty, "checklist": checklist}
MIRRORED = {"structure", "sr", "breakout", "trend", "meanrev", "sessions", "mtf", "smc", "harmonic", "elliott", "gann"}   # these have a bearish twin (the same drawing flipped)


def art(name: str, side: str = "bull") -> str:
    """The drawing as an SVG string; in English mode every label (including the raw-text ones) is translated and the flow arrows point left to right."""
    fn = ART.get(name)
    if not fn:
        return ""
    out = fn(side)
    if _en():
        out = _t(out)
        if name == "checklist":
            out = out.replace(">←</text>", ">→</text>")
    return out
