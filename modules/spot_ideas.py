"""Spot ideas desk (owner 2026-11-06): 'someone whose job is to THINK about spot trades on the big timeframes with every school
- SMC, ICT, Elliott, Gann, classic chart patterns, breakouts - and the news, refreshed daily, shown like the reference picture'.

For each market (metals, oil, euro, crypto ...) it reads the Analyzer bundle (1M / 1W / 1D / 4H, spot_dash.load_bundle), the
Radar's detectors (signals.detect_all on 1D / 1W), the classic chart patterns (patterns.find), and the tagged news
(spot_news), then tries 7 setup recipes. A recipe fires only when its own conditions hold; every idea lists which schools agree,
entry zone, stop, targets, R:R, a base and an alternative scenario in Egyptian Arabic, its own KPIs and the news behind it.
A 'thinking log' records what was looked at and why an idea was or was not made.
HONEST: recipes are rules written from the schools, NOT backtested (the combined score backtest showed no edge, 2026-11-06).
Spot = buy only: bearish readings become 'avoid / take profit' cards, never shorts."""
from __future__ import annotations

import math

import numpy as np

UNIVERSE = [("GOLD", "metals", "الدهب"), ("SILVER", "metals", "الفضة"), ("COPPER", "metals", "النحاس"), ("OIL", "energy", "البترول"),
            ("EURUSD", "forex", "اليورو / دولار"), ("BTC", "crypto", "البيتكوين"), ("ETH", "crypto", "الإيثريوم"), ("SOL", "crypto", "سولانا")]
KIND_AR = {"discount": "تجميع في الديسكاونت (SMC / ICT)", "breakout": "اختراق كلاسيك + إعادة اختبار", "pattern": "نموذج شارت كلاسيك",
           "elliott": "نهاية تصحيح اليوت", "divergence": "انعكاس بالدايفرجنس", "gann": "مستوى + زمن جان", "avoid": "تجنّب الشراء / جني ربح"}
BULL_PAT = {"cp_ihs": "رأس وكتفين مقلوب", "cp_wedge_dn": "وتد هابط (إيجابي)", "cp_tri_asc": "مثلث صاعد", "cp_multi_bottom": "قاع متعدد",
            "cp_tl_support": "على خط دعم", "cp_channel_up": "قناة صاعدة"}


def _f(x):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    ax = abs(x)
    return f"{x:,.0f}" if ax >= 1000 else f"{x:,.2f}" if ax >= 1 else f"{x:.4f}"


def _rr(entry, stop, target):
    risk = entry - stop
    return (target - entry) / risk if risk > 0 and target and target > entry else None


def _donchian(r, n):
    h = r["h"]
    return float(h[-n - 1:-1].max()) if len(h) > n + 1 else None


def build(asset: str, cls: str, name_ar: str, b: dict, news: dict | None = None) -> tuple[list[dict], list[str]]:
    """-> (ideas, thinking log lines) for one market."""
    R = b["reads"]
    w, m, d1 = R.get("1w") or {}, R.get("1mo") or {}, R.get("1d") or {}
    log, ideas = [], []
    if not w.get("ok"):
        return [], [f"{name_ar}: مفيش شموع أسبوعية كفاية - اتخطيته."]
    px = b.get("price") or w["px"]
    atr = w["atr"] or px * 0.03
    tr = {"up": "صاعد", "down": "هابط"}
    dr = w.get("dr") or {}
    log.append(f"{name_ar} {_f(px)}: الشهري {tr.get(m.get('trend'), 'مش واضح')}، الأسبوعي {tr.get(w.get('trend'), 'مش واضح')}، "
               f"درجة المدارس {b['conf']['score']:+d}" + (f"، السعر في {'الديسكاونت' if dr.get('zone') == 'discount' else 'البريميوم'} {dr['pos'] * 100:.0f}% من الرينج" if dr else ""))
    nt = news or {"score": 0, "items": []}
    if nt["items"]:
        log.append(f"  الأخبار: {nt['up']} بتدعم الطلوع و{nt['down']} بتدعم النزول - " + " | ".join(x["title"][:70] for x in nt["items"][:2]))
    m_down = m.get("ok") and m.get("trend") == "down"
    sells = (b.get("plan") or {}).get("sells", []) or [px + 2 * atr, px + 3.5 * atr]
    base = {"asset": asset, "cls": cls, "name": name_ar, "price": px, "atr_w": atr, "news": nt, "score": b["conf"]["score"]}

    struct = [p for _, p, k in (w.get("piv") or []) if k == "H"] + [p for _, p, k in (m.get("piv") or []) if k == "H"] if m.get("ok") else \
        [p for _, p, k in (w.get("piv") or []) if k == "H"]
    struct += [dr.get("hi")] if dr else []

    def add(kind, entry_lo, entry_hi, stop, schools, why, kpis, targets=None, horizon="أسابيع لشهور"):
        entry = (entry_lo + entry_hi) / 2
        risk = entry - stop
        cands = sorted({round(t, 10) for t in list(targets or []) + list(sells) + struct if t and t > entry_hi * 1.01})
        tg = []
        for t in cands:   # first target must pay at least 1.5 R; targets closer than 0.5 % to each other count once
            if risk > 0 and (t - entry) / risk >= 1.5 and all(abs(t / x - 1) > 0.005 for x in tg):
                tg.append(t)
        tg = tg[:3]
        if not tg:
            log.append(f"  ✗ {KIND_AR[kind]}: الشروط موجودة بس أقرب هدف من الهيكل مايديش 1.5 ضعف المخاطرة - اتلغت")
            return
        rr = _rr(entry, stop, tg[0])
        agree = list(dict.fromkeys(schools))
        if nt["score"] > 0:
            agree.append("الأخبار")
        conf = len(agree) + (1 if not m_down else -1) + (1 if rr and rr >= 2 else 0)
        alt = f"لو قفل أسبوع تحت {_f(stop)} الفكرة تتلغي ونستنى قاع جديد." if kind != "avoid" else f"لو قفل أسبوع فوق {_f(tg[0])} يبقى الاتجاه أقوى من المتوقع."
        ideas.append({**base, "kind": kind, "title": KIND_AR[kind], "entry": (entry_lo, entry_hi), "stop": stop, "targets": tg, "rr": rr,
                      "schools": agree, "conf": conf, "why": why, "alt": alt, "kpis": kpis, "horizon": horizon,
                      "against": ["الشهري هابط"] if m_down else []})
        log.append(f"  ✅ فكرة: {KIND_AR[kind]} - {why}")

    # 1. discount accumulation (SMC order block / FVG inside the ICT discount)
    zones = [z for z in (w.get("obs", []) + w.get("fvg", [])) if z["side"] == "bull" and z["lo"] < px and z["hi"] > px - 2.5 * atr]
    if dr.get("zone") == "discount" and zones and w.get("trend") != "down":
        z = max(zones, key=lambda z: z["hi"])
        add("discount", z["lo"], min(z["hi"], px), z["lo"] - 0.5 * atr, ["ICT ديسكاونت", "SMC منطقة طلب", "هيكل مش هابط"],
            f"السعر في الديسكاونت ({dr['pos'] * 100:.0f}%) وفوق منطقة طلب أسبوعية {_f(z['lo'])}-{_f(z['hi'])}",
            {"مكان في الرينج": f"{dr['pos'] * 100:.0f}%", "EQ 50%": _f(dr["eq"]), "قمة الرينج": _f(dr["hi"])}, [dr["eq"], dr["hi"]] + sells)
    elif dr:
        log.append(f"  ✗ تجميع ديسكاونت: {'السعر في البريميوم' if dr.get('zone') == 'premium' else 'مفيش منطقة طلب قريبة' if not zones else 'الهيكل الأسبوعي هابط'}")
    # 2. classic breakout of the 20 / 55-week high, buy the retest
    for n in (55, 20):
        lvl = _donchian(w, n)
        if lvl and w["c"][-1] > lvl and w["c"][-2] <= lvl * 1.03:
            rng = lvl - float(w["l"][-n - 1:-1].min())
            add("breakout", lvl - 0.3 * atr, lvl + 0.2 * atr, lvl - 1.2 * atr, [f"اختراق قمة {n} أسبوع", "كلاسيك / تيرتل"],
                f"قفلة أسبوعية فوق قمة {n} أسبوع {_f(lvl)} - الشراء على إعادة الاختبار مش على الطاير",
                {"مستوى الاختراق": _f(lvl), "ارتفاع الرينج": _f(rng), "هدف القياس": _f(lvl + rng)}, [lvl + rng * 0.618, lvl + rng] + sells)
            break
    else:
        log.append("  ✗ اختراق: مفيش قفلة أسبوعية جديدة فوق قمة 20 / 55 أسبوع")
    # 3. classic chart patterns (Finviz-style, the Radar's pattern scanner)
    try:
        from modules import patterns
        import pandas as pd
        wdf = pd.DataFrame({"time": w["time"], "open": w["o"], "high": w["h"], "low": w["l"], "close": w["c"]})
        found = {k: v for k, v in patterns.find(wdf).items() if k in BULL_PAT}
    except Exception:
        found = {}
    if found:
        k = next(iter(found))
        line = found[k][-1]
        lv = float(line[3])
        lo = min(lv, px) - 0.3 * atr
        add("pattern", lo, max(lv, px), lo - 0.8 * atr, [f"نموذج: {BULL_PAT[k]}", "شارت باترن"],
            f"أسبوعي: {BULL_PAT[k]} - خط النموذج عند {_f(lv)}", {"النموذج": BULL_PAT[k], "خط النموذج": _f(lv)})
    else:
        log.append("  ✗ نماذج الشارت: مفيش نموذج إيجابي على الأسبوعي")
    # 4. Elliott: ABC correction ended near 0.5-0.618 with a daily CHoCH up
    ew = w.get("elliott") or {}
    ch_up = any(e["kind"] == "CHoCH" and e["dir"] == "up" for e in (d1.get("events") or [])[-3:])
    if ew.get("kind") == "abc" and ew.get("labels") and ch_up:
        c_lvl = ew["labels"][-1][1]
        add("elliott", c_lvl, px, c_lvl - 0.6 * atr, ["اليوت: نهاية ABC", "SMC: CHoCH يومي صاعد"],
            f"تصحيح ABC أسبوعي خلص عند {_f(c_lvl)} واليومي عمل CHoCH لفوق", {"قاع C": _f(c_lvl), "هدف 1.272": _f((ew.get("targets") or {}).get("1.272"))})
    else:
        log.append("  ✗ اليوت: " + ("التصحيح لسه مااتأكدش (مفيش CHoCH يومي)" if ew.get("kind") == "abc" else "مفيش تصحيح ABC أسبوعي"))
    # 5. regular bullish RSI divergence on 1W or 1D, in the discount
    dv = [(tf, x) for tf in ("1w", "1d") for x in ((R.get(tf) or {}).get("div") or []) if x["side"] == "bull" and x["kind"] == "regular"
          and x["i2"] >= (R.get(tf) or {}).get("n", 0) - 8]
    if dv and dr.get("zone") == "discount":
        tf, x = dv[0]
        add("divergence", x["p2"], px, x["p2"] - 0.6 * atr, [f"دايفرجنس RSI {'أسبوعي' if tf == '1w' else 'يومي'}", "ICT ديسكاونت"],
            f"السعر عمل قاع أوطى {_f(x['p2'])} والـ RSI عمل قاع أعلى ({x['o1']:.0f} → {x['o2']:.0f})", {"RSI": f"{x['o2']:.0f}", "قاع الدايفرجنس": _f(x["p2"])})
    else:
        log.append("  ✗ دايفرجنس: " + ("مفيش دايفرجنس صاعد جديد" if not dv else "فيه دايفرجنس بس السعر مش في الديسكاونت"))
    # 6. Gann: price on a square-of-9 level inside a time window
    g = w.get("gann") or {}
    fit = g.get("fit") or {}
    near = [v for v in g.get("sq9", []) if abs(v / px - 1) < 0.012 and v <= px * 1.005]
    if near and fit.get("bars_to_turn") is not None and fit["bars_to_turn"] <= 2:
        v = near[0]
        add("gann", v - 0.3 * atr, px, v - atr, ["جان: مستوى مربع التسعة", "جان: نافذة زمنية"],
            f"السعر على مستوى جان {_f(v)} وفيه نافذة انعكاس زمنية خلال {fit['bars_to_turn']} أسبوع", {"مستوى جان": _f(v), "الدورة": f"{fit.get('tsp')} أسبوع"})
    else:
        log.append("  ✗ جان: مفيش مستوى + نافذة زمنية مع بعض")
    # 7. avoid / take profit (spot never shorts)
    bear_div = any(x["side"] == "bear" and x["kind"] == "regular" for x in (w.get("div") or []))
    has_breakout = any(i["kind"] == "breakout" for i in ideas)
    if dr.get("zone") == "premium" and not has_breakout and (bear_div or b["conf"]["score"] <= -35 or nt["score"] < 0):
        hi = dr["hi"]
        ideas.append({**base, "kind": "avoid", "title": KIND_AR["avoid"], "entry": None, "stop": None, "targets": [hi], "rr": None,
                      "schools": ["ICT بريميوم"] + (["دايفرجنس هابط"] if bear_div else []) + (["الأخبار ضد"] if nt["score"] < 0 else []),
                      "conf": 2 + bear_div, "why": f"السعر غالي (بريميوم {dr['pos'] * 100:.0f}%)" + (" ومعاه دايفرجنس هابط" if bear_div else ""),
                      "alt": f"لو قفل أسبوع فوق {_f(hi)} الاتجاه أقوى - استنى رجوع للـ EQ {_f(dr['eq'])} قبل أي شراء.", "kpis": {"مكان في الرينج": f"{dr['pos'] * 100:.0f}%", "EQ": _f(dr["eq"])},
                      "horizon": "دلوقتي", "against": []})
        log.append("  ⚠️ تنبيه: منطقة غالية - مش وقت شراء سبوت، لو معاك اجني جزء")
    if not ideas:
        log.append(f"  ⇒ {name_ar}: مفيش فكرة النهارده - مستني.")
    return ideas, log


def desk(candles=None, news_items=None, universe=None) -> dict:
    """Run every market. -> {'ideas': ranked, 'log': [...], 'markets': [...], 'news': tagged headlines}"""
    from modules import spot_dash, spot_news
    items = spot_news.fetch() if news_items is None else news_items
    tagged = spot_news.tag(items)
    ideas, log, markets = [], [], []
    for asset, cls, name in (universe or UNIVERSE):
        try:
            b = spot_dash.load_bundle(asset, candles)
        except Exception as e:
            log.append(f"{name}: الداتا مش متاحة ({type(e).__name__})")
            continue
        nt = spot_news.tilt(tagged, asset)
        idea, lg = build(asset, cls, name, b, nt)
        ideas += idea
        log += lg
        w = b["reads"].get("1w") or {}
        if w.get("ok"):
            c = w["c"]
            markets.append({"asset": asset, "name": name, "cls": cls, "price": b.get("price") or w["px"], "wk": float(c[-1] / c[-2] - 1) * 100,
                            "score": b["conf"]["score"], "zone": (w.get("dr") or {}).get("zone"), "news": nt["score"], "spark": list(c[-52:]),
                            "n_ideas": len([i for i in idea if i["kind"] != "avoid"])})
    ideas.sort(key=lambda i: (i["kind"] != "avoid", i["conf"], i["rr"] or 0), reverse=True)
    risk = sum(1 for x in tagged if x["push"].get("GOLD", 0) > 0 and x["push"].get("BTC", 0) < 0) - sum(1 for x in tagged if x["push"].get("BTC", 0) > 0)
    return {"ideas": ideas, "log": log, "markets": markets, "news": tagged[:12], "risk_off": risk}


def telegram_text(r: dict, top: int = 4) -> str:
    """Short Egyptian-Arabic daily message: the best ideas with entry / stop / targets + the news mood."""
    buy = [i for i in r["ideas"] if i["kind"] != "avoid"][:top]
    avoid = [i for i in r["ideas"] if i["kind"] == "avoid"]
    lines = [f"🧠 أفكار السبوت النهارده - {len(buy)} فكرة شراء من {len(r['markets'])} سوق"]
    mood = r.get("risk_off", 0)
    lines.append("مزاج الأخبار: " + ("خوف / ملاذ آمن (الدهب والبترول عادة بيستفيدوا)" if mood > 0 else "شهية مخاطرة" if mood < 0 else "محايد"))
    for k, i in enumerate(buy, 1):
        a, b = i["entry"]
        lines.append(f"\n{k}) {i['name']} - {i['title']} · توافق {i['conf']} · {i['rr']:.1f}R")
        lines.append(f"   ليه: {i['why']}")
        lines.append(f"   دخول على دفعات {_f(b)} / {_f((a + b) / 2)} / {_f(a)} · وقف تحت {_f(i['stop'])} (قفلة أسبوعية)")
        lines.append("   أهداف: " + " / ".join(_f(t) for t in i["targets"]) + f" · المدارس: {'، '.join(i['schools'])}")
        if i["news"]["items"]:
            lines.append(f"   خبر: {i['news']['items'][0]['title'][:90]}")
    if avoid:
        lines.append("\n⚠️ تجنّب الشراء دلوقتي: " + "، ".join(f"{i['name']} ({i['why']})" for i in avoid[:3]))
    if not buy:
        lines.append("مفيش فكرة شروطها اتحققت النهارده - الاستنى قرار.")
    lines.append("\nقواعد من المدارس، لسه من غير باك تيست. كمية صغيرة. مفيش أي أمر بيتنفذ.")
    return "\n".join(lines)
