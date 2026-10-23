"""Technical Office control-room widgets (owner's reference images, 2026-10-22): dark cards with status dots, a gauge, alert
cards, an indicator grid, a system map and a tool grid. Pure HTML builders (no Streamlit import) so they can be tested;
main.py feeds them real numbers only (lab file, work board, workflow files, source checks)."""
from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TONE = {"ok": "#2dd4bf", "warn": "#f0b429", "bad": "#f87171", "info": "#93c5fd", "off": "#6b7480"}
STATUS_TONE = {"done": "ok", "running": "ok", "decided": "ok", "ready": "info", "review": "info", "in progress": "info",
               "open": "off", "waiting": "warn", "parked": "off", "blocked": "bad"}

CSS = """<style>
.xo-row{display:flex;flex-wrap:wrap;gap:12px;margin:4px 0 12px}
.xo-card{background:var(--uk-panel,#1b2027);border:1px solid var(--uk-line,#2a313a);border-radius:14px;padding:14px 16px;color:var(--uk-text,#e6e9ee);box-sizing:border-box}
.xo-h{font-size:15px;font-weight:700;margin:0 0 8px;color:var(--uk-text,#e6e9ee)}
.xo-sub{font-size:12px;color:var(--uk-dim,#a3adba)}
.xo-chip{display:inline-flex;align-items:center;gap:6px;background:var(--uk-panel2,#232a33);border-radius:8px;padding:5px 10px;font-size:12px;color:var(--uk-text,#e6e9ee);margin:0 6px 6px 0}
.xo-dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex:none}
.xo-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.xo-tile{background:var(--uk-panel2,#232a33);border-radius:10px;padding:10px 12px}
.xo-big{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:26px;font-weight:700;line-height:32px}
.xo-alert{background:var(--uk-panel2,#232a33);border-radius:10px;padding:10px 12px;margin-bottom:8px}
.xo-badge{border-radius:6px;padding:2px 8px;font-size:11px}
.xo-map{display:flex;flex-direction:column;align-items:center;gap:0}
.xo-maprow{display:flex;flex-wrap:wrap;justify-content:center;gap:12px}
.xo-node{background:var(--uk-panel2,#1f262e);border:1px solid var(--uk-line,#2f3742);border-radius:10px;padding:8px 10px;min-width:150px;display:flex;gap:8px;align-items:center;font-size:13px}
.xo-link{width:2px;height:22px;background:var(--uk-line,#3d4753);margin:2px 0}
.xo-tool{background:var(--uk-panel2,#232a33);border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:4px;min-height:86px}
.xo-table{width:100%;border-collapse:collapse;font-size:13px}.xo-table td,.xo-table th{border-bottom:1px solid var(--uk-line,#2a313a);padding:6px 8px;text-align:start}
.xo-table th{color:var(--uk-dim,#a3adba);font-weight:600}
</style>"""


def esc(x) -> str:
    return html.escape(str(x))


def dot(tone: str) -> str:
    return f"<span class='xo-dot' style='background:{TONE.get(tone, tone)}'></span>"


def badge(text: str, tone: str) -> str:
    c = TONE.get(tone, tone)
    return f"<span class='xo-badge' style='background:{c}22;color:{c}'>{esc(text)}</span>"


def chips(items) -> str:
    """items: (label, value, tone)."""
    return "<div>" + "".join(f"<span class='xo-chip'>{dot(t)}<span style='color:#a3adba'>{esc(a)}</span> <b>{esc(b)}</b></span>" for a, b, t in items) + "</div>"


def gauge(value: int, total: int, title: str, caption: str, center_label: str) -> str:
    """Half-ring gauge: value of total (e.g. groups that passed the evidence gate)."""
    frac = 0.0 if not total else max(0.0, min(1.0, value / total))
    ang = math.pi * (1 - frac)
    x, y = 120 + 100 * math.cos(ang), 125 - 100 * math.sin(ang)
    col = TONE["ok"] if frac >= .5 else TONE["warn"] if frac > 0 else TONE["bad"]
    arc = f"<path d='M 20 125 A 100 100 0 0 1 {x:.1f} {y:.1f}' fill='none' stroke='{col}' stroke-width='16' stroke-linecap='round'/>" if frac > 0 else \
          f"<circle cx='20' cy='125' r='8' fill='{col}'/>"
    return (f"<div class='xo-card' style='flex:1 1 280px;max-width:420px'><div class='xo-h'>{esc(title)}</div><div class='xo-sub'>{esc(caption)}</div>"
            f"<div style='position:relative;height:150px;display:flex;justify-content:center'><svg role='img' aria-label='{esc(value)} / {esc(total)}' width='240' height='140' viewBox='0 0 240 140'>"
            f"<path d='M 20 125 A 100 100 0 0 1 220 125' fill='none' stroke='#2a313a' stroke-width='16' stroke-linecap='round'/>{arc}</svg>"
            f"<div style='position:absolute;top:62px;text-align:center'><div class='xo-big' style='font-size:38px'>{esc(value)}<span style='font-size:18px;color:#a3adba'> / {esc(total)}</span></div>"
            f"<div class='xo-sub'>{esc(center_label)}</div></div></div></div>")


def alerts(title: str, items) -> str:
    """items: (headline, badge text, tone, note)."""
    body = "".join(f"<div class='xo-alert'><div style='font-size:14px;font-weight:600'>{esc(h)}</div><div style='display:flex;gap:8px;align-items:center;margin-top:4px'>"
                   f"{badge(b, t)}<span class='xo-sub'>{esc(n)}</span></div></div>" for h, b, t, n in items)
    return f"<div class='xo-card' style='flex:1 1 280px'><div class='xo-h'>{esc(title)}</div>{body or ''}</div>"


def indicators(title: str, items) -> str:
    """items: (label, value, sub, tone or None)."""
    tiles = "".join(f"<div class='xo-tile'><div class='xo-sub'>{esc(a)}</div><div class='xo-big' style='color:{TONE.get(t, '#e6e9ee') if t else '#e6e9ee'}'>{esc(v)}</div>"
                    f"<div class='xo-sub' style='font-size:11px'>{esc(s)}</div></div>" for a, v, s, t in items)
    return f"<div class='xo-card' style='flex:2 1 420px'><div class='xo-h'>{esc(title)}</div><div class='xo-grid'>{tiles}</div></div>"


def system_map(title: str, caption: str, rows) -> str:
    """rows: list of rows, each a list of (name, detail, tone); rows are joined top to bottom by a line."""
    parts = []
    for i, row in enumerate(rows):
        if i:
            parts.append("<div class='xo-link'></div>")
        parts.append("<div class='xo-maprow'>" + "".join(
            f"<div class='xo-node' style='border-color:{TONE.get(t, '#2f3742')}66'>{dot(t)}<span><b>{esc(n)}</b><br><span class='xo-sub'>{esc(d)}</span></span></div>"
            for n, d, t in row) + "</div>")
    return f"<div class='xo-card' style='flex:1 1 100%'><div class='xo-h'>{esc(title)}</div><div class='xo-sub' style='margin-bottom:10px'>{esc(caption)}</div><div class='xo-map'>{''.join(parts)}</div></div>"


def tools(title: str, items) -> str:
    """items: (name, what, status text, tone)."""
    cells = "".join(f"<div class='xo-tool'><b style='font-size:14px'>{esc(n)}</b><span class='xo-sub'>{esc(w)}</span><span style='font-size:11px;color:{TONE.get(t, '#a3adba')}'>{esc(s)}</span></div>"
                    for n, w, s, t in items)
    return f"<div class='xo-card' style='flex:1 1 100%'><div class='xo-h'>{esc(title)}</div><div class='xo-grid' style='grid-template-columns:repeat(auto-fill,minmax(200px,1fr))'>{cells}</div></div>"


def table(headers, rows) -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<div class='xo-card' style='overflow-x:auto'><table class='xo-table'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


# ---- data helpers -------------------------------------------------------------------------------------------------

def load_tasks(path=ROOT / "data" / "office_tasks.json") -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {"tasks": []}


def task_counts(tasks) -> dict:
    out = {}
    for t in tasks:
        out[t.get("status", "open")] = out.get(t.get("status", "open"), 0) + 1
    return out


def workflows(folder=ROOT / ".github" / "workflows") -> list:
    """[{file, name, schedule, manual, writes}] read from the workflow files (no YAML library needed)."""
    out = []
    for p in sorted(Path(folder).glob("*.yml")):
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        m = re.search(r"^name:\s*(.+)$", txt, re.M)
        crons = re.findall(r"cron:\s*[\"']([^\"']+)[\"']", txt)
        out.append({"file": p.name, "name": (m.group(1).strip().strip("\"'") if m else p.stem), "schedule": ", ".join(crons),
                    "manual": "workflow_dispatch" in txt, "writes": bool(re.search(r"contents:\s*write", txt)) or "git push" in txt})
    return out


# ---- Arabic for the Technical Office text that comes from files / modules (owner rule: one language at a time) ------------
# Merged into modules.i18n.AR without overriding keys other code already translated (so L() finds them on every page).
OFFICE_AR = {
    "verdict = out-of-sample only; in-sample is information. cost 0.1 R is a planning estimate, not measured; fewer than 100 trades is not evidence":
        "الحكم على الجزء خارج العينة بس؛ داخل العينة للمعلومة. تكلفة 0.1 R تقدير تخطيط مش متقاس؛ أقل من 100 صفقة مش دليل",
    "in-sample": "داخل العينة", "out-of-sample": "خارج العينة", "part": "الجزء", "trade": "الصفقة", "net R": "صافي R",
    "cumulative net R": "صافي R التراكمي", "Chain": "السلسلة", "Other": "أخرى", "avg R": "متوسط R",
    "all": "الكل", "long": "شراء", "short": "بيع",
    "UI": "الواجهة", "Risk": "المخاطر", "Workspace / Journal": "مساحة العمل / اليومية",
    "Above EMAs": "فوق EMAs", "Below EMAs": "تحت EMAs", "Stack↑": "ترتيب EMAs ↑", "Stack↓": "ترتيب EMAs ↓", "Channel↑": "قناة ↑", "Channel↓": "قناة ↓",
    "Trendline↑": "ترند لاين ↑", "Trendline↓": "ترند لاين ↓", "Chan↑": "قناة ↑", "Chan↓": "قناة ↓", "Range": "عرضي", "Wedge↑": "وتد ↑", "Wedge↓": "وتد ↓",
    "Tri asc": "مثلث صاعد", "Tri desc": "مثلث هابط", "Tri sym": "مثلث متماثل", "H&S": "رأس وكتفين", "Inv H&S": "رأس وكتفين مقلوب", "Multi top": "قمم متعددة",
    "Multi bot": "قيعان متعددة", "TL sup": "ترند دعم", "TL res": "ترند مقاومة", "Double Top": "قمة مزدوجة", "Double Bottom": "قاع مزدوج",
}
LAB_CELLS = {
    "rank": "الترتيب", "key": "الكاشف", "school": "المدرسة", "win %": "نسبة النجاح %", "random win %": "نجاح العشوائي %", "random avg R": "متوسط R العشوائي",
    "edge": "الفرق", "tf": "الإطار", "long n": "عدد الشراء", "long avg R": "متوسط R شراء", "short n": "عدد البيع", "short avg R": "متوسط R بيع",
    "with n": "مع الاتجاه: العدد", "with win %": "مع الاتجاه: النجاح %", "with avg R": "مع الاتجاه: متوسط R",
    "against n": "ضد الاتجاه: العدد", "against win %": "ضد الاتجاه: النجاح %", "against avg R": "ضد الاتجاه: متوسط R",
    "when": "الوقت", "Mon": "الاثنين", "Tue": "الثلاثاء", "Wed": "الأربعاء", "Thu": "الخميس", "Fri": "الجمعة", "Sat": "السبت", "Sun": "الأحد",
    "Asia 00-07": "آسيا 00-07", "Late 20-24": "متأخر 20-24", "London 07-12": "لندن 07-12", "New York 12-20": "نيويورك 12-20",
    "group": "المجموعة", "1st half n": "النصف الأول: العدد", "1st half avg R": "النصف الأول: متوسط R", "2nd half n": "النصف الثاني: العدد",
    "2nd half avg R": "النصف الثاني: متوسط R", "all signals": "كل الإشارات", "a": "الكاشف أ", "b": "الكاشف ب", "together": "معا",
    "opposite": "عكس بعض", "agreeing families": "العائلات المتفقة", "Gann hit %": "إصابة جان %", "Gann tries": "محاولات جان",
    "ordinary hit %": "الإصابة العادية %", "ordinary tries": "المحاولات العادية", "difference (sigma)": "الفرق (سيجما)", "trades": "الصفقات",
    "random-direction avg R": "متوسط R لاتجاه عشوائي", "difference (t)": "الفرق (t)", "window": "النافذة", "days": "أيام",
    "mean daily return %": "متوسط العائد اليومي %", "15 days around new moon": "15 يوم حول القمر الجديد", "15 days around full moon": "15 يوم حول البدر",
    "exit": "الخروج", "net avg R (after costs)": "صافي متوسط R (بعد التكاليف)", "total R": "إجمالي R", "signal": "الإشارة", "filters": "الفلاتر",
    "random-dir win %": "نجاح اتجاه عشوائي %", "avg move %": "متوسط الحركة %", "off / on": "إيقاف / تشغيل",
    "filters do not touch them": "الفلاتر لا تؤثر عليها", "same on / off": "نفس النتيجة تشغيل وإيقاف", "*ALL*": "الكل",
}
_LAB_HEAD = [   # (heading starts with, Arabic heading)
    ("Every detector on its own", "كل كاشف لوحده (كل الأطر الزمنية)"),
    ("Schools of analysis", "مدارس التحليل (كل كواشفها مجمعة)"),
    ("Best timeframe per detector", "أفضل إطار زمني لكل كاشف (n >= 30)"),
    ("Long vs short", "شراء مقابل بيع"),
    ("Trend filter", "فلتر الترند: إشارة مع ترند الـ 100 شمعة مقابل ضده (زخم السلاسل الزمنية)"),
    ("Time of day", "وقت اليوم (جلسات UTC، شموع داخل اليوم) واليوم من الأسبوع - كل الكواشف مجمعة"),
    ("Chain grades", "درجات السلسلة (docs/PIPELINE.md): كل إشارة كاشف موسومة بـ 5 طبقات سياق - ترند الفريم الأعلى، الموقع (خصم / علاوة)، الفوليوم، نظام التقلب، الجلسة"),
    ("Conflicts", "التعارضات (إشارات في اتجاهين متعاكسين على نفس الشمعة)"),
    ("Confluence", "التوافق: عائلات أكتر متفقة = أحسن؟"),
    ("Gann time cycles", "دورات جان الزمنية: قمة أو قاع تاني خلال ±2 شمعة من القمة أو القاع + 30/45/60/90/120/144/180 شمعة مقابل إزاحات عادية"),
    ("Gann zone trades", "صفقات مناطق جان خارج العينة (walk-forward: الشبكة بتتعاد على كل اللي قبل كل شريحة 10% من النصف الأخير، والتداول في الشريحة دي بس؛ قاعدة الـ Workspace مع الخروج بالوقت)"),
    ("Gann astro", "فلك جان: طور القمر (شموع يومية، كل الرموز مجمعة؛ Dichev & Janes 2001 لقيا أيام القمر الجديد حوالي ضعف أيام البدر)"),
    ("Exit variants", "بدائل الخروج على نفس الدخولات (نسبة العائد للمخاطرة ووقف التعادل)"),
    ("Filter on/off backtest", "اختبار الفلاتر تشغيل / إيقاف (البند 1) - أول تشغيل فعلي 2026-10-18 (GitHub Actions، BTC / ETH / SOL × 15m / 1h / 4h / 1d؛ الجدول الكامل في FILTER_COMPARE.md)"),
]
_LAB_LINES = {
    "Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).":
        "شرط احتساب الدرجة: n >= 100، و t > 3 مقابل اتجاه عشوائي، ومتوسط R > 0 في النصفين (النصف الأول = داخل العينة، الثاني = خارج العينة).",
    "Costs: 0.1R per trade assumed (net column = avg R - costs). Costs are a planning estimate, not measured.":
        "التكاليف: 0.1R للصفقة (عمود الصافي = متوسط R ناقص التكاليف). التكاليف تقدير تخطيط مش متقاس.",
    "Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). Only the totals below are for the whole pool; per-detector rows are in the JSON.":
        "أنهي هدف / خروج يدي أحسن توقع. نقطة التعادل = نسبة النجاح المطلوبة = 1/(1+RR). t = متوسط R مقابل صفر (مقارنة على نفس الدخولات تقريباً). المجاميع تحت للمجموعة كلها بس؛ صفوف كل كاشف في ملف الـ JSON.",
    "Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.":
        "سيجما تقريبية (محاولات متداخلة). فوق +3 على أكتر من إطار زمني تبقى دليل على توقيت جان؛ حوالي 0 = إزاحات عادية. اختبارات المشي العشوائي: الأعداد الثابتة -1.2؛ الأشكال (الضابط = نفس النقاط بطول دورة قمة تانية) من +0.4 لـ +2.5 على 4 بذور، فالمعتبر بس اللي فوق +3 على أكتر من إطار.",
    "Direction hit-rate over the next 10 bars, no costs / stops; pooled over the 12 series (n-weighted):":
        "نسبة إصابة الاتجاه خلال الـ 10 شموع الجاية، من غير تكاليف أو وقف؛ مجمعة على الـ 12 سلسلة (موزونة بـ n):",
    "Verdict: **no filter passes the bar.** Best case liqline +4 points win rate (about 1.3 sigma, and \"on\" is a subset of \"off\", so even less);":
        "الحكم: **ولا فلتر عدّى المعيار.** أحسن حالة liqline بزيادة 4 نقاط في نسبة النجاح (حوالي 1.3 سيجما، و\"تشغيل\" جزء من \"إيقاف\" فالفرق أقل);",
    "breaker / ob gains sit on small or shrinking n. Filters stay as they are (they cut signal count, they do not hurt); nothing promoted.":
        "مكاسب breaker / ob قايمة على n صغير أو بيقل. الفلاتر زي ما هي (بتقلل عدد الإشارات ومبتضرش)؛ مفيش حاجة اترقّت.",
}
_LAB_RX = [
    (re.compile(r"^Random-walk self-test \(walk-forward, 6 x 5000 bars\): ([+\-\d.]+)R vs random ([+\-\d.]+)R, t ([+\-\d.]+) \((\d+) trades\) - so only t > \+3 with n >= 100 on several timeframes counts as evidence\. No costs\.$"),
     "اختبار ذاتي على مشي عشوائي (walk-forward، 6 × 5000 شمعة): {0}R مقابل عشوائي {1}R، t {2} ({3} صفقة) - فالمعتبر دليل بس t > +3 مع n >= 100 على أكتر من إطار زمني. من غير تكاليف."),
    (re.compile(r"^Difference t = ([+\-\d.]+) \(\|t\| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous\)\.$"),
     "الفرق t = {0} (|t| > 2 تلميح، و > 3 دليل؛ الرموز المتداخلة مرتبطة ببعض فالتقدير سخي)."),
]
_HEAD_TXT = {"htf": "الفريم الأعلى", "loc": "الموقع", "vol": "الفوليوم", "reg": "نظام التقلب", "time": "الجلسة"}
_CELL_RX = [
    (re.compile(r"^grade (A\+*|B|C)(?: / (.+))?$"), lambda m: "الدرجة " + m.group(1) + (" / " + m.group(2) if m.group(2) else "")),
    (re.compile(r"^layer (htf|loc|vol|reg|time)$"), lambda m: "طبقة " + _HEAD_TXT[m.group(1)]),
    (re.compile(r"^no (htf|loc|vol|reg|time)$"), lambda m: "من غير " + _HEAD_TXT[m.group(1)]),
    (re.compile(r"^(\d\+?) families( \(with opposition\))?$"), lambda m: m.group(1) + " عائلات" + (" (مع تعارض)" if m.group(2) else "")),
    (re.compile(r"^(\w+) shapes 120/180/240/360 deg$"), lambda m: m.group(1) + " أشكال 120/180/240/360 درجة"),
]


def _install_ar() -> None:
    try:
        from modules.i18n import AR
    except Exception:
        return
    for k, v in OFFICE_AR.items():
        AR.setdefault(k, v)


_install_ar()


def lab_title(k: str, ar: bool) -> str:
    """Section title of STRATEGY_LAB.md / STRATEGIES.md in the page language (English text unchanged)."""
    if ar:
        for pre, a in _LAB_HEAD:
            if k.startswith(pre):
                return a
    return k


def _lab_cell(c: str, tr) -> str:
    s = c.strip()
    if not s:
        return c
    if s in LAB_CELLS:
        return LAB_CELLS[s]
    for rx, f in _CELL_RX:
        m = rx.match(s)
        if m:
            return f(m)
    return tr(s)


def lab_md(md: str, ar: bool, tr=None) -> str:
    """Markdown body of a lab section in the page language: table header cells, school / row labels and the fixed prose lines are
    translated; numbers are never touched. Lines it does not know stay as written (English)."""
    if not ar:
        return md
    tr = tr or (lambda s: s)
    out = []
    for ln in md.split("\n"):
        st = ln.strip()
        if st.startswith("|"):
            if set(st) <= set("|-: "):
                out.append(ln); continue
            out.append("|" + "|".join(" " + _lab_cell(c, tr).strip() + " " for c in st.strip("|").split("|")) + "|")
        elif st in _LAB_LINES:
            out.append(_LAB_LINES[st])
        else:
            for rx, tpl in _LAB_RX:
                m = rx.match(st)
                if m:
                    out.append(tpl.format(*m.groups())); break
            else:
                out.append(ln)
    return "\n".join(out)


_ERR_RX = [
    (re.compile(r"^contradictory rules on (.+): no value is above (.+) and below (.+) at once \(AND\)$"), "قواعد متناقضة على {0}: مفيش قيمة فوق {1} وتحت {2} في نفس الوقت (AND)"),
    (re.compile(r"^strategy must be an object$"), "الاستراتيجية لازم تكون كائن (object)"),
    (re.compile(r"^name: 1-60 letters / digits / space / - / _$"), "الاسم: من 1 لـ 60 حرف / رقم / مسافة / - / _"),
    (re.compile(r"^side must be one of (.+)$"), "الاتجاه لازم يكون واحد من {0}"),
    (re.compile(r"^logic must be one of (.+)$"), "المنطق لازم يكون واحد من {0}"),
    (re.compile(r"^at least one rule is required$"), "لازم قاعدة واحدة على الأقل"),
    (re.compile(r"^at most 12 rules$"), "12 قاعدة كحد أقصى"),
    (re.compile(r"^must be an object$"), "لازم تكون كائن (object)"),
    (re.compile(r"^unknown indicator '(.+)'$"), "مؤشر غير معروف '{0}'"),
    (re.compile(r"^period must be an integer 2-500$"), "الفترة لازم تكون رقم صحيح من 2 لـ 500"),
    (re.compile(r"^op must be one of (.+)$"), "الشرط لازم يكون واحد من {0}"),
    (re.compile(r"^value indicator '(.+)' unknown$"), "مؤشر القيمة '{0}' غير معروف"),
    (re.compile(r"^value period must be an integer 2-500$"), "فترة القيمة لازم تكون رقم صحيح من 2 لـ 500"),
    (re.compile(r"^value must be a finite number or an indicator$"), "القيمة لازم تكون رقم محدود أو مؤشر"),
    (re.compile(r"^tf must be a text label such as '1h'$"), "الإطار الزمني لازم يكون نص زي '1h'"),
]


def rule_error(msg: str, ar: bool) -> str:
    """strategy_rules.validate() message in the page language (English unchanged)."""
    if not ar:
        return msg
    m0 = re.match(r"^rule (\d+): (.*)$", msg)
    pre, body = ("", msg)
    if m0:
        pre, body = f"القاعدة {m0.group(1)}: ", m0.group(2)
    for rx, tpl in _ERR_RX:
        m = rx.match(body)
        if m:
            return pre + tpl.format(*m.groups())
    return msg


def en_only(text: str) -> str:
    """English page: drop a quoted Arabic term from a document line (the Playbook source quotes one Arabic label), so no Arabic shows."""
    return re.sub(r"\s*[\"'“«][؀-ۿ][^\"'”»]*[\"'”»]", "", text) if re.search("[؀-ۿ]", text) else text
