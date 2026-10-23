"""Strategy map (owner 2026-10-22): every indicator / detector / pattern in the dashboard classified once, so a strategy is
built from PARTS with different jobs instead of one indicator being called a strategy.

  * kind     : indicator (one measurement of the candles) | event (a detector that fires on a bar) | context (data around the price)
  * cluster  : the redundancy group. Members of a cluster measure the same thing with different maths (SMA / EMA / MACD all
               smooth closing prices), so a strategy takes AT MOST ONE part from a cluster.
  * role     : context (which side / regime) | setup (is price somewhere favourable) | trigger (when to enter) | filter (when to
               skip) | exit | sizing. One part per role; an indicator can play different roles in different strategies.
  * blueprint: a named complete strategy = parts by role. `rules` is set only when the strategy can run in the rule engine
               (strategy_rules) today; the others are tested by the weekly lab (data/strategy_lab.json) or need an indicator
               the engine does not have yet.

Sources for the taxonomy (honest labels, see EVIDENCE): the 'one indicator per category' idea is practitioner / StockCharts
(folklore); trend-following and time-series momentum have peer-reviewed support (Moskowitz-Ooi-Pedersen 2012; Brock-Lakonishok-
LeBaron 1992, with decay and data-snooping caveats in Park-Irwin 2007); ICT / SMC / CRT / Ichimoku / Triple Screen have no peer-
reviewed test; t > 3 for a new rule is Harvey-Liu-Zhu (2016). The text below is guidance; the NUMBERS shown next to it always come
from the weekly lab file, never from here.
"""
from __future__ import annotations

from modules import office_kpi as K

ROLES = {"context": "السياق (الاتجاه / النظام)", "setup": "الإعداد (مكان مناسب)", "trigger": "الزناد (توقيت الدخول)",
         "filter": "الفلتر (متى أتجنب)", "exit": "الخروج", "sizing": "حجم الصفقة"}

EVIDENCE = {"peer": ("منشور ومحكّم", "ok"), "blog": ("مدونات / كتب فقط", "warn"), "folk": ("متداول من غير اختبار منشور", "warn"),
            "measured": ("مقاس عندنا في المعمل", "info")}

# cluster id -> (Arabic name, what its members measure, the redundancy rule in one line)
CLUSTERS = {
    "trend_ma": ("الترند بالمتوسطات", "اتجاه سعر الإغلاق بعد تنعيمه (متأخر)", "SMA وEMA وMACD وتقاطع المتوسطات وترتيبها كلها نفس الفكرة؛ خد واحد."),
    "breakout": ("اختراق المدى", "كسر أعلى / أقل سعر في آخر N شمعة", "دونشيان وتيرتل وكسر المستوى وكسر الخط نفس الفكرة بأرقام مختلفة؛ خد واحد."),
    "momentum": ("الزخم", "سرعة التغير (متشبع شراء / بيع) وتباعده عن السعر", "RSI وStochastic وCCI وROC بتقيس نفس الشيء؛ خد واحد. (MACD-hist محسوب في عنقود الترند بالمتوسطات.)"),
    "volatility": ("التقلب", "حجم الحركة (للوقف والحجم والانضغاط)", "ATR وعرض بولينجر ومدى كيلتنر كلهم تقلب؛ خد واحد."),
    "trend_strength": ("قوة الترند", "هل فيه ترند أصلاً (مش اتجاهه)", "ADX فلتر نظام السوق، مش تأكيد تاني للاتجاه."),
    "volume": ("الفوليوم والتدفق", "مين بيدفع السعر (حجم، دلتا، فوتبرنت)", "الفوليوم النسبي وOBV وCMF قريبين من بعض؛ الفوتبرنت لايف بس."),
    "structure": ("هيكل السوق", "كسر قمة / قاع مؤكد (MSS / CHoCH / BOS)", "كلها تسميات لنفس منطق القمم والقيعان؛ خد واحد."),
    "zones": ("مناطق عدم التوازن", "منطقة اندفاع سابقة بيرجع لها السعر (FVG / OB / Breaker / Unicorn)", "كلها أشكال لنفس الفكرة (منطقة اندفاع)؛ خد واحد."),
    "liquidity": ("السيولة", "سحب قمة / قاع واضح ثم رجوع (Sweep / CRT / خط سيولة)", "Sweep وCRT وخط السيولة نفس الحدث على مدى مختلف."),
    "retrace": ("التصحيح", "مستوى تصحيح من موجة (فيبوناتشي / OTE / خصم-بريميوم)", "كلها نسب على نفس الموجة؛ خد واحد."),
    "time": ("الوقت والجلسات", "التوقيت (لندن / نيويورك / Kill Zone)", "فلتر توقيت؛ مش إشارة بحد ذاته."),
    "waves": ("الموجات والنماذج", "عدّ موجات أو شكل هندسي (إليوت / هارمونيك / قناة / مثلث)", "ذاتية وكتير؛ كلها تتعامل كإعداد مش زناد."),
    "intermarket": ("بين الأسواق", "تباعد بين أسواق مترابطة (SMT)", "سياق؛ ما يتكررش مع باقي العناقيد."),
    "macro": ("الاقتصاد والأخبار", "تقويم، تمويل (funding)، أخبار", "فلتر تجنب وسياق؛ مش زناد."),
}

# component id -> (Arabic name, kind, cluster, roles it can play, source). source: ("lab", detector key) | ("rule", engine name) |
# ("scan", scanner filter id) | ("live", description) | ("data", description)
COMPONENTS = {
    # engine indicators (testable today in the rule engine)
    "sma": ("المتوسط SMA", "indicator", "trend_ma", ("context", "trigger"), ("rule", "sma")),
    "ema": ("المتوسط EMA", "indicator", "trend_ma", ("context", "trigger"), ("rule", "ema")),
    "macd_hist": ("هيستوجرام MACD", "indicator", "trend_ma", ("trigger",), ("rule", "macd_hist")),
    "rsi": ("RSI", "indicator", "momentum", ("setup", "trigger"), ("rule", "rsi")),
    "roc": ("معدل التغير ROC", "indicator", "momentum", ("context", "trigger"), ("rule", "roc")),
    "atr": ("ATR", "indicator", "volatility", ("filter", "exit", "sizing"), ("rule", "atr")),
    "bbw": ("عرض بولينجر", "indicator", "volatility", ("setup", "filter"), ("rule", "bbw")),
    "adx": ("ADX", "indicator", "trend_strength", ("filter",), ("rule", "adx")),
    "hh": ("قناة دونشيان (أعلى / أقل N)", "indicator", "breakout", ("trigger", "exit"), ("rule", "hh")),
    "volume": ("الفوليوم", "indicator", "volume", ("filter",), ("rule", "volume")),
    # lab detectors (events)
    "ma_cross": ("تقاطع المتوسطات", "event", "trend_ma", ("trigger",), ("lab", "ma_cross")),
    "ema_stack": ("ترتيب المتوسطات", "event", "trend_ma", ("context",), ("lab", "ema_stack")),
    "sma1040": ("SMA 10/40 (صناديق التحوط)", "event", "trend_ma", ("context", "trigger"), ("lab", "sma1040")),
    "vwap": ("VWAP", "event", "trend_ma", ("setup",), ("lab", "vwap")),
    "donch": ("دونشيان المركّب", "event", "breakout", ("trigger",), ("lab", "donch")),
    "turtle55": ("تيرتل 55", "event", "breakout", ("trigger",), ("lab", "turtle55")),
    "breakout": ("اختراق", "event", "breakout", ("trigger",), ("lab", "breakout")),
    "level": ("مستوى", "event", "breakout", ("setup",), ("lab", "level")),
    "ohl_open": ("مستوى الافتتاح OHL", "event", "breakout", ("setup",), ("lab", "ohl_open")),
    "ohl_break": ("كسر OHL", "event", "breakout", ("trigger",), ("lab", "ohl_break")),
    "tlbreak": ("كسر خط الترند", "event", "breakout", ("trigger",), ("lab", "tlbreak")),
    "rsi_div": ("دايفرجنس RSI", "event", "momentum", ("setup", "trigger"), ("lab", "rsi_div")),
    "macd_div": ("دايفرجنس MACD", "event", "momentum", ("setup", "trigger"), ("lab", "macd_div")),
    "msb_ob": ("MSB + أوردر بلوك", "event", "structure", ("trigger",), ("lab", "msb_ob")),
    "cisd": ("CISD (تغير تسليم السعر)", "event", "structure", ("trigger",), ("lab", "cisd")),
    "m2022": ("موديل ICT 2022", "event", "structure", ("trigger",), ("lab", "m2022")),
    "fvg": ("فجوة FVG", "event", "zones", ("setup",), ("lab", "fvg")),
    "ob": ("أوردر بلوك", "event", "zones", ("setup",), ("lab", "ob")),
    "breaker": ("بريكر بلوك", "event", "zones", ("setup",), ("lab", "breaker")),
    "unicorn": ("يونيكورن", "event", "zones", ("setup",), ("lab", "unicorn")),
    "sweep": ("سحب سيولة", "event", "liquidity", ("setup",), ("lab", "sweep")),
    "liqline": ("خط السيولة", "event", "liquidity", ("setup", "trigger"), ("lab", "liqline")),
    "crt": ("CRT", "event", "liquidity", ("setup", "trigger"), ("lab", "crt")),
    "zombie": ("زومبي", "event", "liquidity", ("setup",), ("lab", "zombie")),
    "fib": ("فيبوناتشي", "event", "retrace", ("setup",), ("lab", "fib")),
    "ote": ("منطقة OTE", "event", "retrace", ("setup",), ("lab", "ote")),
    "judas": ("جوداس سوينج", "event", "time", ("setup", "trigger"), ("lab", "judas")),
    "sess_amd": ("AMD الجلسة", "event", "time", ("setup",), ("lab", "sess_amd")),
    "kzs": ("قناص الكيل زون", "event", "time", ("filter", "trigger"), ("lab", "kzs")),
    "po3": ("Power of Three", "event", "time", ("setup",), ("lab", "po3")),
    "orb": ("اختراق مدى الافتتاح", "event", "time", ("trigger",), ("lab", "orb")),
    "ew3": ("موجة إليوت 3", "event", "waves", ("setup",), ("lab", "ew3")),
    "abc": ("تصحيح ABC", "event", "waves", ("setup",), ("lab", "abc")),
    "smt": ("SMT بين الأسواق", "event", "intermarket", ("context", "filter"), ("lab", "smt")),
    # context data we already have (not backtestable far back, or not candles)
    "footprint": ("فوتبرنت / دلتا / دفتر الأوامر", "context", "volume", ("trigger", "filter"), ("live", "لايف بس: مفيش تاريخ طويل نختبر عليه")),
    "funding": ("معدل التمويل (funding)", "context", "macro", ("filter", "context"), ("data", "OKX / Hyperliquid؛ مش متوصل بالمعمل لسه")),
    "calendar": ("التقويم الاقتصادي", "context", "macro", ("filter",), ("data", "متوصل بالرادار (خبر قوي خلال ساعة)")),
    "htf": ("اتجاه الفريم الأكبر", "context", "trend_ma", ("context",), ("lab", "chain:htf")),
}

# strategy blueprints. parts: (role, component id, one-line note). rules = strategy_rules dict when it can run today.
BLUEPRINTS = [
    {"id": "connors_rsi2", "name": "Connors RSI2 (ارتداد داخل ترند)", "style": "Swing", "evidence": "blog",
     "evidence_note": "اختبارات مدونات / كتب على الأسهم والمؤشرات؛ ضعيف على الكريبتو، والارتداد قصير المدى نتايجه مختلطة.",
     "parts": [("context", "sma", "الإغلاق فوق SMA 200: اتجاه كبير صاعد"), ("setup", "rsi", "RSI(2) تحت 10: تراجع حاد قصير"),
               ("exit", "sma", "إغلاق فوق SMA 5 (في الأصل؛ الباك تيست بتاعنا بوقف ATR وهدف R)")],
     "rules": {"name": "Connors RSI2", "side": "long", "logic": "AND", "rules": [
         {"indicator": "close", "op": ">", "value": {"indicator": "sma", "period": 200}},
         {"indicator": "rsi", "period": 2, "op": "<", "value": 10.0}]},
     "tf": "1d"},
    {"id": "turtle", "name": "تيرتل: اختراق دونشيان", "style": "Position", "evidence": "blog",
     "evidence_note": "كتب وتجارب تاريخية؛ فيه دعم أكاديمي عام لمتابعة الترند، لكن القاعدة نفسها مش منشورة باختبار حديث بعد التكلفة.",
     "parts": [("trigger", "hh", "الإغلاق يعدّي أعلى 55 شمعة"), ("sizing", "atr", "حجم الصفقة بقيمة ATR (N)"), ("exit", "hh", "كسر أقل 20 شمعة (في الأصل)")],
     "rules": {"name": "Turtle 55", "side": "long", "logic": "AND", "rules": [
         {"indicator": "close", "op": "crosses_above", "value": {"indicator": "hh", "period": 55}}]},
     "tf": "1d", "lab": ["turtle55", "donch"]},
    {"id": "tsmom", "name": "زخم السلسلة الزمنية (Time-series momentum)", "style": "Position", "evidence": "peer",
     "evidence_note": "Moskowitz-Ooi-Pedersen 2012 (Journal of Financial Economics): عائد آخر 12 شهر بيتنبأ بعائد الشهر الجاي على عقود كتير. هنا نسخة قصيرة لأن الداتا 300 شمعة تقريباً.",
     "parts": [("context", "roc", "عائد 100 شمعة موجب (بديل قصير لـ 12 شهر)"), ("filter", "sma", "الإغلاق فوق SMA 100"), ("sizing", "atr", "حجم بالتقلب (مستهدف تقلب ثابت)")],
     "rules": {"name": "TSMOM short", "side": "long", "logic": "AND", "rules": [
         {"indicator": "roc", "period": 100, "op": ">", "value": 0.0},
         {"indicator": "close", "op": ">", "value": {"indicator": "sma", "period": 100}}]},
     "tf": "1d", "warn": "ROC والمتوسط في عنقودين مختلفين لكن الاتنين بيقيسوا ترند؛ ده في الواقع جزء واحد مكرر. النسخة الأصلية: علامة عائد 12 شهر فقط."},
    {"id": "squeeze", "name": "انضغاط بولينجر ثم اختراق", "style": "Day", "evidence": "blog",
     "evidence_note": "كتب ومدونات (Bollinger / Carter)؛ تجمع التقلب نفسه موثق جيداً، لكن القاعدة دي مش مختبرة منشور.",
     "parts": [("setup", "bbw", "عرض بولينجر(20) أضيق من عرضه(100): انضغاط"), ("trigger", "hh", "الإغلاق يعدّي أعلى 20 شمعة")],
     "rules": {"name": "Squeeze breakout", "side": "long", "logic": "AND", "rules": [
         {"indicator": "bbw", "period": 20, "op": "<", "value": {"indicator": "bbw", "period": 100}},
         {"indicator": "close", "op": "crosses_above", "value": {"indicator": "hh", "period": 20}}]},
     "tf": "1h"},
    {"id": "ma_adx", "name": "تقاطع متوسطات + فلتر ADX", "style": "Swing", "evidence": "blog",
     "evidence_note": "تقاطع المتوسطات له دراسات قديمة (Brock et al. 1992) تراجعت أرباحها بعد التكلفة (Park-Irwin 2007)؛ ADX كفلتر مدونات.",
     "parts": [("trigger", "ema", "EMA 20 يعدّي EMA 50"), ("filter", "adx", "ADX فوق 20: فيه ترند أصلاً")],
     "rules": {"name": "EMA cross with ADX", "side": "long", "logic": "AND", "rules": [
         {"indicator": "ema", "period": 20, "op": "crosses_above", "value": {"indicator": "ema", "period": 50}},
         {"indicator": "adx", "period": 14, "op": ">", "value": 20.0}]},
     "tf": "4h", "lab": ["ma_cross"]},
    {"id": "macd_ema200", "name": "MACD + EMA 200 (مثال لتركيب ضعيف)", "style": "Swing", "evidence": "folk",
     "evidence_note": "وصفة شائعة؛ الاتنين من نفس العنقود (ترند بالمتوسطات) فالتأكيد التاني مفيهوش معلومة جديدة.",
     "parts": [("context", "ema", "الإغلاق فوق EMA 200"), ("trigger", "macd_hist", "هيستوجرام MACD يعدّي الصفر")],
     "rules": {"name": "MACD with EMA200", "side": "long", "logic": "AND", "rules": [
         {"indicator": "close", "op": ">", "value": {"indicator": "ema", "period": 200}},
         {"indicator": "macd_hist", "op": "crosses_above", "value": 0.0}]},
     "tf": "4h"},
    {"id": "ict_chain", "name": "ICT / SMC المتسلسل", "style": "Day", "evidence": "folk",
     "evidence_note": "متداول وما فيهوش اختبار منشور محكّم؛ عندنا اختبار المعمل الأسبوعي بس (سلسلة 5 طبقات).",
     "parts": [("context", "htf", "اتجاه الفريم الأكبر"), ("setup", "sweep", "سحب سيولة"), ("trigger", "cisd", "CISD / كسر هيكل"),
               ("setup", "fvg", "رجوع لفجوة FVG"), ("filter", "kzs", "داخل Kill Zone"), ("exit", "liqline", "السيولة المقابلة")],
     "rules": None, "needs": "بيتقاس في المعمل الأسبوعي (درجة A+++ = 5 طبقات)، مش في محرك القواعد.", "lab": ["sweep", "cisd", "fvg", "kzs", "msb_ob"]},
    {"id": "crt", "name": "CRT: سحب مدى شمعة الفريم الأكبر", "style": "Day", "evidence": "folk",
     "evidence_note": "متداول بين متداولي ICT؛ ما فيهوش اختبار منشور.",
     "parts": [("context", "htf", "شمعة الفريم الأكبر (4H / 1H)"), ("setup", "crt", "سحب قمتها أو قاعها"), ("trigger", "crt", "رجوع الإغلاق جوه المدى"),
               ("exit", "crt", "الطرف التاني للمدى")],
     "rules": None, "needs": "محتاج فريمين في نفس القاعدة (القواعد عندنا فريم واحد)، وبيتقاس في المعمل.", "lab": ["crt", "sweep"]},
    {"id": "triple", "name": "Elder: الشاشات التلاتة", "style": "Swing", "evidence": "blog",
     "evidence_note": "كتاب Elder 'Trading for a Living'؛ مفيش اختبار منشور محكّم.",
     "parts": [("context", "macd_hist", "ترند الفريم الأسبوعي"), ("setup", "rsi", "تراجع على اليومي عكس الترند"), ("trigger", "hh", "كسر أعلى الشمعة السابقة على 4H")],
     "rules": None, "needs": "محتاج فريمات متعددة داخل القاعدة الواحدة؛ ده التطوير الجاي لمحرك القواعد.", "lab": []},
]

BP = {b["id"]: b for b in BLUEPRINTS}


def component(cid: str) -> dict:
    n, kind, cl, roles, src = COMPONENTS[cid]
    return {"id": cid, "name": n, "kind": kind, "cluster": cl, "roles": roles, "src": src}


def check(parts, ar: bool = True) -> list:
    """Redundancy / completeness warnings for a strategy's parts [(role, component id, note)] - Arabic, empty list = clean.
    Rules: at most one part per cluster (a repeat adds no information); a trigger or setup is required; an exit or sizing is advised.
    A component's `roles` are advisory (shown in the map), not enforced here."""
    if not ar:
        return check_en(parts)
    out, seen_cluster = [], {}
    for role, cid, _n in parts:
        c = component(cid)
        k = c["cluster"]
        if k in seen_cluster and seen_cluster[k] != cid:
            out.append(f"«{c['name']}» و«{component(seen_cluster[k])['name']}» من نفس العنقود ({CLUSTERS[k][0]}): تكرار، خد واحد.")
        seen_cluster.setdefault(k, cid)
    roles = {r for r, _c, _n in parts}
    if "trigger" not in roles and "setup" not in roles:
        out.append("مفيش زناد ولا إعداد: الاستراتيجية ناقصة.")
    if not roles & {"exit", "sizing"}:
        out.append("مفيش خروج ولا حجم صفقة: ناقصة (الباك تيست بيستخدم وقف ATR وهدف R موحد).")
    return out


def members(lab: dict, cluster: str) -> list:
    """Lab numbers for the detector members of one cluster: best timeframe with n >= 100 (else best overall, flagged), net avg R."""
    rows = []
    for cid, (name, kind, cl, roles, src) in COMPONENTS.items():
        if cl != cluster:
            continue
        r = {"id": cid, "name": name, "kind": kind, "src": src, "best": None, "n_ok": False}
        if src[0] == "lab" and not src[1].startswith("chain:"):
            card = K.detector_card(lab, src[1]) if lab else {}
            if card.get("best"):
                r["best"], r["n_ok"], r["off"] = card["best"], card["best_is_evidence_size"], card["off"]
        rows.append(r)
    return rows


def cluster_best(lab: dict, cluster: str):
    """The cluster's strongest representative (by net avg R among members with n >= 100, OFF detectors excluded); None when none qualifies."""
    ok = [m for m in members(lab, cluster) if m["best"] and m["n_ok"] and not m.get("off")]   # an OFF detector is never the representative
    return max(ok, key=lambda m: m["best"]["net"]) if ok else None


def agreement(lab: dict, a: str, b: str):
    """% of the bars where both detectors fired AND pointed the same way (lab 'conflicts' table), with the bar count; None if absent."""
    for r in (lab or {}).get("conflicts", []):
        if {r["a"], r["b"]} == {a, b}:
            return round(100 - r["rate"], 1), r["together"]
    return None


def stacking(lab: dict) -> list:
    """Does stacking more families help? Lab 'confluence' rows (no-opposition rows only): [(label, n, net avg R)]."""
    out = []
    for k, v in ((lab or {}).get("confluence") or {}).items():
        if "opposition" not in k and v.get("n"):
            out.append((k, v["n"], round(v["avgR"] - K.COST_R, 3)))
    return out


def gaps(lab: dict, ar: bool = True) -> list:
    """Roles / clusters with no member that has evidence-size lab data and a positive net: where the dashboard is thin."""
    if not ar:
        return gaps_en(lab)
    out = []
    for cl, (name, _m, _r) in CLUSTERS.items():
        mem = members(lab, cl)
        if not mem:
            continue
        lab_mem = [m for m in mem if m["src"][0] == "lab"]
        best = cluster_best(lab, cl)
        if not lab_mem and any(m["src"][0] == "rule" for m in mem):
            out.append((name, "مؤشرات في محرك القواعد بس؛ لسه مفيش اختبار أسبوعي ليها"))
        elif lab_mem and (not best or best["best"]["net"] <= 0):
            out.append((name, "ولا عضو فيه n ≥ 100 وصافيه موجب"))
        if any(m["src"][0] in ("live", "data") for m in mem):
            out.append((name, "فيه بيانات عندنا (لايف / مصدر) مش متوصلة بالاختبار"))
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# English version (one language at a time: owner rule 2026-10-23). The Arabic tables above are unchanged; English lives in the
# *_EN tables below and the accessors pick by language. ar=None follows the site language (modules.i18n.lang()).
# check() and gaps() keep Arabic as their default so existing callers and tests are unchanged.
# ---------------------------------------------------------------------------------------------------------------------------
ROLES_EN = {"context": "Context (trend / regime)", "setup": "Setup (a favourable place)", "trigger": "Trigger (entry timing)",
            "filter": "Filter (when to avoid)", "exit": "Exit", "sizing": "Position size"}

EVIDENCE_EN = {"peer": ("Published and peer reviewed", "ok"), "blog": ("Blogs / books only", "warn"), "folk": ("Widely used, no published test", "warn"),
               "measured": ("Measured by our lab", "info")}

CLUSTERS_EN = {
    "trend_ma": ("Trend by moving averages", "Direction of the closing price after smoothing (lagging)", "SMA, EMA, MACD, MA crosses and MA stacking are all the same idea; take one."),
    "breakout": ("Range breakout", "A break of the highest / lowest price of the last N candles", "Donchian, Turtle, level break and trendline break are the same idea with different numbers; take one."),
    "momentum": ("Momentum", "Speed of change (overbought / oversold) and its divergence from price", "RSI, Stochastic, CCI and ROC measure the same thing; take one. (MACD-hist is counted in the Trend by moving averages cluster.)"),
    "volatility": ("Volatility", "Size of the move (for stop, size and squeeze)", "ATR, Bollinger width and Keltner range are all volatility; take one."),
    "trend_strength": ("Trend strength", "Whether there is a trend at all (not its direction)", "ADX is a market-regime filter, not a second confirmation of direction."),
    "volume": ("Volume and flow", "Who is pushing the price (volume, delta, footprint)", "Relative volume, OBV and CMF are close to each other; the footprint is live only."),
    "structure": ("Market structure", "A confirmed break of a high / low (MSS / CHoCH / BOS)", "All are names for the same highs-and-lows logic; take one."),
    "zones": ("Imbalance zones", "A prior impulse zone price returns to (FVG / OB / Breaker / Unicorn)", "All are shapes of the same idea (an impulse zone); take one."),
    "liquidity": ("Liquidity", "A sweep of an obvious high / low followed by a return (Sweep / CRT / liquidity line)", "Sweep, CRT and the liquidity line are the same event on a different range."),
    "retrace": ("Retracement", "A retracement level of a swing (Fibonacci / OTE / discount-premium)", "All are ratios on the same swing; take one."),
    "time": ("Time and sessions", "Timing (London / New York / Kill Zone)", "A timing filter; not a signal by itself."),
    "waves": ("Waves and patterns", "Counting waves or a geometric shape (Elliott / harmonic / channel / triangle)", "Subjective and plentiful; all are treated as a setup, not a trigger."),
    "intermarket": ("Intermarket", "Divergence between correlated markets (SMT)", "Context; does not duplicate the other clusters."),
    "macro": ("Economy and news", "Calendar, funding, news", "An avoid-filter and context; not a trigger."),
}

COMPONENTS_EN = {
    "sma": "SMA moving average", "ema": "EMA moving average", "macd_hist": "MACD histogram", "rsi": "RSI", "roc": "Rate of change (ROC)",
    "atr": "ATR", "bbw": "Bollinger width", "adx": "ADX", "hh": "Donchian channel (highest / lowest N)", "volume": "Volume",
    "ma_cross": "Moving-average cross", "ema_stack": "Moving-average stacking", "sma1040": "SMA 10/40 (hedge funds)", "vwap": "VWAP",
    "donch": "Compound Donchian", "turtle55": "Turtle 55", "breakout": "Breakout", "level": "Level", "ohl_open": "Open level (OHL)",
    "ohl_break": "OHL break", "tlbreak": "Trendline break", "rsi_div": "RSI divergence", "macd_div": "MACD divergence",
    "msb_ob": "MSB + order block", "cisd": "CISD (change in state of delivery)", "m2022": "ICT 2022 model", "fvg": "FVG gap",
    "ob": "Order block", "breaker": "Breaker block", "unicorn": "Unicorn", "sweep": "Liquidity sweep", "liqline": "Liquidity line",
    "crt": "CRT", "zombie": "Zombie", "fib": "Fibonacci", "ote": "OTE zone", "judas": "Judas swing", "sess_amd": "Session AMD",
    "kzs": "Kill Zone sniper", "po3": "Power of Three", "orb": "Opening range breakout", "ew3": "Elliott wave 3", "abc": "ABC correction",
    "smt": "SMT between markets", "footprint": "Footprint / delta / order book", "funding": "Funding rate", "calendar": "Economic calendar",
    "htf": "Higher-timeframe trend",
}

# live / data component sources (the 'src' text of the context components)
SRC_EN = {
    "footprint": "Live only: no long history to test on",
    "funding": "OKX / Hyperliquid; not wired to the lab yet",
    "calendar": "Wired to the Radar (a strong news event within an hour)",
}

# blueprint id -> English text; "parts" notes are in the same order as the Arabic parts
BP_EN = {
    "connors_rsi2": {"name": "Connors RSI2 (pullback inside a trend)",
                     "evidence_note": "Blog / book tests on stocks and indices; weak on crypto, and short-term mean-reversion results are mixed.",
                     "parts": ["Close above SMA 200: a big uptrend", "RSI(2) below 10: a sharp short pullback",
                               "Close above SMA 5 (the original; our backtest uses an ATR stop and an R target)"]},
    "turtle": {"name": "Turtle: Donchian breakout",
               "evidence_note": "Books and historical experiments; there is general academic support for trend following, but the rule itself is not published with a recent test after costs.",
               "parts": ["Close breaks the highest of 55 candles", "Position size by the ATR value (N)", "A break of the lowest of 20 candles (the original)"]},
    "tsmom": {"name": "Time-series momentum",
              "evidence_note": "Moskowitz-Ooi-Pedersen 2012 (Journal of Financial Economics): the last 12 months' return predicts next month's return across many contracts. Here is a short version because we have only about 300 candles.",
              "parts": ["100-candle return positive (a short substitute for 12 months)", "Close above SMA 100", "Volatility-based size (a fixed volatility target)"],
              "warn": "ROC and the moving average sit in two different clusters but both measure trend; in practice this is one repeated part. The original version uses only the sign of the 12-month return."},
    "squeeze": {"name": "Bollinger squeeze then breakout",
                "evidence_note": "Books and blogs (Bollinger / Carter); volatility clustering itself is well documented, but this rule has no published test.",
                "parts": ["Bollinger width(20) narrower than its width(100): a squeeze", "Close breaks the highest of 20 candles"]},
    "ma_adx": {"name": "Moving-average cross + ADX filter",
               "evidence_note": "MA crosses have old studies (Brock et al. 1992) whose profits faded after costs (Park-Irwin 2007); ADX as a filter is blog-level.",
               "parts": ["EMA 20 crosses EMA 50", "ADX above 20: there is a trend at all"]},
    "macd_ema200": {"name": "MACD + EMA 200 (an example of a weak combination)",
                    "evidence_note": "A common recipe; both come from the same cluster (trend by moving averages), so the second confirmation adds no new information.",
                    "parts": ["Close above EMA 200", "MACD histogram crosses zero"]},
    "ict_chain": {"name": "ICT / SMC chain",
                  "evidence_note": "Widely used with no published peer-reviewed test; we only have the weekly lab test (a 5-layer chain).",
                  "parts": ["Higher-timeframe trend", "Liquidity sweep", "CISD / structure break", "Return to an FVG gap", "Inside a Kill Zone", "The opposite liquidity"],
                  "needs": "Measured in the weekly lab (grade A+++ = 5 layers), not in the rule engine."},
    "crt": {"name": "CRT: a sweep of the higher-timeframe candle range",
            "evidence_note": "Used among ICT traders; no published test.",
            "parts": ["The higher-timeframe candle (4H / 1H)", "A sweep of its high or low", "Close returns inside the range", "The other end of the range"],
            "needs": "Needs two timeframes in one rule (our rules are single-timeframe), and it is measured in the lab."},
    "triple": {"name": "Elder: the Triple Screen",
               "evidence_note": "Elder's book 'Trading for a Living'; no published peer-reviewed test.",
               "parts": ["Weekly-timeframe trend", "A pullback on the daily against the trend", "A break of the previous candle's high on 4H"],
               "needs": "Needs multiple timeframes inside a single rule; that is the next development of the rule engine."},
}


def _ar(ar):
    if ar is None:
        from modules.i18n import lang
        return lang() == "ar"
    return bool(ar)


def roles(ar: bool | None = None) -> dict:
    return ROLES if _ar(ar) else ROLES_EN


def evidence(ar: bool | None = None) -> dict:
    return EVIDENCE if _ar(ar) else EVIDENCE_EN


def clusters(ar: bool | None = None) -> dict:
    return CLUSTERS if _ar(ar) else CLUSTERS_EN


def comp_name(cid: str, ar: bool | None = None) -> str:
    return COMPONENTS[cid][0] if _ar(ar) else COMPONENTS_EN[cid]


def bp_text(bid: str, ar: bool | None = None) -> dict:
    """Language-specific text of one blueprint: {name, evidence_note, parts: [notes in parts order], warn, needs} (warn / needs may be absent)."""
    b = BP[bid]
    if _ar(ar):
        return {"name": b["name"], "evidence_note": b["evidence_note"], "parts": [n for _r, _c, n in b["parts"]], "warn": b.get("warn"), "needs": b.get("needs")}
    e = BP_EN[bid]
    return {"name": e["name"], "evidence_note": e["evidence_note"], "parts": e["parts"], "warn": e.get("warn"), "needs": e.get("needs")}


def check_en(parts) -> list:
    """English version of check()."""
    out, seen_cluster = [], {}
    for role, cid, _n in parts:
        k = component(cid)["cluster"]
        if k in seen_cluster and seen_cluster[k] != cid:
            out.append(f"\"{COMPONENTS_EN[cid]}\" and \"{COMPONENTS_EN[seen_cluster[k]]}\" come from the same cluster ({CLUSTERS_EN[k][0]}): a repeat, take one.")
        seen_cluster.setdefault(k, cid)
    roles_ = {r for r, _c, _n in parts}
    if "trigger" not in roles_ and "setup" not in roles_:
        out.append("No trigger and no setup: the strategy is incomplete.")
    if not roles_ & {"exit", "sizing"}:
        out.append("No exit and no position size: incomplete (the backtest uses an ATR stop and a uniform R target).")
    return out


def gaps_en(lab: dict) -> list:
    """English version of gaps()."""
    out = []
    for cl, (_n, _m, _r) in CLUSTERS.items():
        name = CLUSTERS_EN[cl][0]
        mem = members(lab, cl)
        if not mem:
            continue
        lab_mem = [m for m in mem if m["src"][0] == "lab"]
        best = cluster_best(lab, cl)
        if not lab_mem and any(m["src"][0] == "rule" for m in mem):
            out.append((name, "Indicators in the rule engine only; no weekly test for them yet"))
        elif lab_mem and (not best or best["best"]["net"] <= 0):
            out.append((name, "No member has n ≥ 100 with a positive net"))
        if any(m["src"][0] in ("live", "data") for m in mem):
            out.append((name, "We have data (live / a source) that is not wired to the test"))
    return out
