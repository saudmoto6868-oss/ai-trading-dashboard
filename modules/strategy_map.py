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


def check(parts) -> list:
    """Redundancy / completeness warnings for a strategy's parts [(role, component id, note)] - Arabic, empty list = clean.
    Rules: at most one part per cluster (a repeat adds no information); a trigger or setup is required; an exit or sizing is advised.
    A component's `roles` are advisory (shown in the map), not enforced here."""
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


def gaps(lab: dict) -> list:
    """Roles / clusters with no member that has evidence-size lab data and a positive net: where the dashboard is thin."""
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
