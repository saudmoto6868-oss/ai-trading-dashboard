"""Spot brain (owner 2026-11-06: 'a mastermind for spot only'). One market in -> what to do on FOUR horizons, what to do with
what we already hold, and why - from every school + order flow + institutions + news.

Horizon      looks at                                              typical hold
  day        4H structure / RSI / MACD + order flow (T&S, CVD, book, funding, premium) + news       1-3 days
  week       1D + 1W schools + the ideas recipes (breakout, divergence, Elliott, patterns)          1-4 weeks
  month      1W + 1M schools + ICT discount / premium + institutions (COT)                          1-3 months
  year       1M trend + cycle value (200-week avg, Mayer multiple, drawdown from ATH) + COT         6-12 months
Each horizon -> score -100..100 -> verdict: buy (>= 40) / accumulate (15..40) / wait (-15..15) / reduce (-40..-15) /
sell-protect (<= -40), with an entry zone, stop and target from that horizon's own timeframe, and the reasons.
Holdings guard: for every position in the ledger -> hold / reduce / protect / exit, so we do not sit on something that is falling.
HONEST: rules from the schools, not backtested per horizon yet; the combined weekly score showed no edge (2026-11-06)."""
from __future__ import annotations

import math

import numpy as np

H = {"day": ("يوم لـ 3 أيام", "4h"), "week": ("أسبوع لـ 4", "1d"), "month": ("شهر لـ 3", "1w"), "year": ("6 لـ 12 شهر", "1mo")}
H_AR = {"day": "اليومي", "week": "الأسبوعي", "month": "الشهري", "year": "السنوي"}
VERDICT = [(40, "buy", "شراء"), (15, "accumulate", "تجميع"), (-15, "wait", "استنى"), (-40, "reduce", "خفّف"), (-101, "sell", "بيع / احمي")]


def verdict(score: float) -> tuple[str, str]:
    for thr, k, ar in VERDICT:
        if score >= thr:
            return k, ar
    return "sell", "بيع / احمي"


def _avg_votes(r: dict | None) -> float | None:
    if not r or not r.get("ok"):
        return None
    v = list(r["votes"].values())
    return sum(v) / len(v) if v else 0.0


def _f(x):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    ax = abs(x)
    return f"{x:,.0f}" if ax >= 1000 else f"{x:,.2f}" if ax >= 1 else f"{x:.4f}"


def _levels(r: dict, px: float) -> dict:
    """Entry zone / stop / target for one timeframe read (bullish OB / FVG / OTE below, swing high / range top above)."""
    if not r or not r.get("ok"):
        return {}
    atr = r["atr"] or px * 0.02
    z = [x for x in (r.get("obs", []) + r.get("fvg", [])) if x["side"] == "bull" and x["lo"] < px]
    dr = r.get("dr") or {}
    if z:
        best = max(z, key=lambda x: x["hi"])
        lo, hi = best["lo"], min(best["hi"], px)
    elif dr and dr.get("up_leg"):
        lo, hi = sorted(dr["ote"])
        hi = min(hi, px)
    else:
        lo, hi = px - atr, px
    stop = lo - 0.8 * atr
    highs = sorted(p for _, p, k in r.get("piv", []) if k == "H" and p > px * 1.005)
    tgt = next((t for t in highs if (t - (lo + hi) / 2) >= 1.5 * ((lo + hi) / 2 - stop)), None) or (dr.get("hi") if dr and dr.get("hi", 0) > px else None)
    e = (lo + hi) / 2
    rr = (tgt - e) / (e - stop) if tgt and e > stop else None
    return {"entry": (lo, hi), "stop": stop, "target": tgt, "rr": rr}


TF_HZ = {"4h": "day", "1d": "week", "1w": "month", "1mo": "year"}


def setup_vote(setups: list | None, key: str) -> tuple[float | None, list[str]]:
    """Net live setups on this horizon (buy - exit, setups the lab found WORSE than normal are ignored) -> vote + line."""
    rel = [x for x in (setups or []) if TF_HZ.get(x["tf"]) == key and not str(x.get("ev_label", "")).startswith("كان أسوأ")]
    if not rel:
        return None, []
    nb = sum(1 for x in rel if x["side"] == "buy")
    ne = len(rel) - nb
    schools = sorted({x["school_ar"] for x in rel if x["side"] == "buy"})
    return float(np.sign(nb - ne)), [f"سيت أبات شغالة: {nb} شراء / {ne} خروج" + (f" ({'، '.join(schools[:4])})" if schools else "")]


def think(b: dict, flow: dict | None = None, cot: dict | None = None, news: dict | None = None, ideas: list | None = None,
          holdings: list | None = None, setups: list | None = None) -> dict:
    from modules import spot_flow, spot_inst
    R = b["reads"]
    px = b.get("price") or next((r["px"] for r in R.values() if r.get("ok")), None)
    st = b.get("stats", {})
    fr = spot_flow.reading(flow) if flow else {"vote": 0, "lines": ["الأوردر فلو: مااتحملش"]}
    cr = spot_inst.reading(cot) if cot else {"vote": 0, "lines": ["المؤسسات (COT): مااتحملش"]}
    nt = news or {"score": 0, "items": []}
    nv = int(np.sign(nt.get("score", 0)))
    kinds = {i["kind"] for i in (ideas or []) if i["kind"] != "avoid"}
    tr = {"up": "صاعد", "down": "هابط"}
    hz = {}

    def pack(key, parts, reasons, tf):
        sv, sl = setup_vote(setups, key)
        parts = list(parts) + [(1.5, sv)]
        reasons = list(reasons) + sl
        num = sum(w * v for w, v in parts if v is not None)
        den = sum(w for w, v in parts if v is not None)
        sc = round(100 * num / den) if den else 0
        k, ar = verdict(sc)
        hz[key] = {"label": H[key][0], "tf": tf, "score": sc, "verdict": k, "verdict_ar": ar, "reasons": reasons[:6], **_levels(R.get(tf), px)}

    # day
    r4 = R.get("4h")
    pack("day", [(2, _avg_votes(r4)), (2, fr["vote"]), (1, nv)],
         [f"4 ساعات: الاتجاه {tr.get((r4 or {}).get('trend'), 'مش واضح')}, RSI {_f(float(r4['rsi'][-1])) if r4 and r4.get('ok') else '—'}"] + fr["lines"][:3]
         + ([f"الأخبار: {'بتدعم' if nv > 0 else 'ضد'}"] if nv else []), "4h")
    # week
    d1, w1 = R.get("1d"), R.get("1w")
    rec = 1 if kinds & {"breakout", "divergence", "elliott", "pattern"} else 0
    pack("week", [(1.5, _avg_votes(d1)), (2, _avg_votes(w1)), (1, rec), (0.5, nv)],
         [f"اليومي {tr.get((d1 or {}).get('trend'), 'مش واضح')} · الأسبوعي {tr.get((w1 or {}).get('trend'), 'مش واضح')}"]
         + ([f"وصفة شغالة: {', '.join(sorted(kinds))}"] if kinds else ["مفيش وصفة شراء شغالة على الأسبوعي"]), "1d")
    # month
    m1 = R.get("1mo")
    dr = (w1 or {}).get("dr") or {}
    disc = 1 if dr.get("zone") == "discount" else -1 if dr.get("zone") == "premium" else 0
    pack("month", [(2, _avg_votes(w1)), (2, _avg_votes(m1)), (1, disc), (1.5, cr["vote"])],
         [f"الشهري {tr.get((m1 or {}).get('trend'), 'مش واضح')} · السعر في {'الديسكاونت' if disc > 0 else 'البريميوم' if disc < 0 else '—'} الأسبوعي"] + cr["lines"][:2], "1w")
    # year (cycle value)
    val = 0
    vr = []
    if st.get("dist_200w") is not None:
        d = st["dist_200w"]
        val += 1 if d < 0 else -1 if d > 150 else 0
        vr.append(f"عن متوسط 200 أسبوع {d:+.0f}%" + (" (تحته = منطقة قيمة تاريخيًا)" if d < 0 else " (بعيد جدًا فوقه = سخونة)" if d > 150 else ""))
    if st.get("mayer") is not None:
        mm = st["mayer"]
        val += 1 if mm < 1 else -2 if mm > 2.4 else 0
        vr.append(f"مضاعف ماير {mm:.2f}" + (" (رخيص)" if mm < 1 else " (سخن)" if mm > 2.4 else ""))
    if st.get("dd_ath") is not None:
        dd = st["dd_ath"]
        val += 1 if dd < -60 else 0
        vr.append(f"من أعلى سعر تاريخي {dd:+.0f}%")
    pack("year", [(2, _avg_votes(m1)), (2, max(-1, min(1, val))), (1, cr["vote"])], vr + cr["lines"][:1], "1mo")
    # holdings guard
    guard = []
    for p in holdings or []:
        if p.get("asset") != b["symbol"] or (p.get("qty") or 0) <= 1e-12:
            continue
        inval = (b.get("plan") or {}).get("invalidation")
        wk_close = float(w1["c"][-1]) if w1 and w1.get("ok") else px
        if inval and wk_close < inval:
            act, why = "exit", f"القفلة الأسبوعية {_f(wk_close)} تحت مستوى الإلغاء {_f(inval)}"
        elif hz["month"]["score"] <= -15 or hz["year"]["score"] <= -15:
            act, why = "reduce", f"المدى المتوسط ضد الشراء (شهري {hz['month']['score']:+d} / سنوي {hz['year']['score']:+d})"
        elif hz["week"]["score"] <= -40 and hz["day"]["score"] <= -40:
            act, why = "protect", "اليومي والأسبوعي ضد بقوة - حط وقف تحت آخر قاع"
        else:
            act, why = "hold", "الاتجاه الكبير لسه مش ضدنا"
        guard.append({"asset": p["asset"], "qty": p["qty"], "avg": p.get("avg_usd"), "pnl_pct": p.get("unreal_pct"), "action": act, "why": why,
                      "action_ar": {"exit": "اخرج", "reduce": "خفّف 30-50%", "protect": "احمي بوقف", "hold": "احتفظ"}[act]})
    best = max(hz.items(), key=lambda kv: kv[1]["score"])
    worst = min(hz.items(), key=lambda kv: kv[1]["score"])
    if best[1]["score"] >= 15:
        head = f"أحسن مدة للشراء: {H_AR[best[0]]} ({best[1]['label']}) - {best[1]['verdict_ar']}"
    elif worst[1]["score"] <= -15:
        head = f"مش وقت شراء - {H_AR[worst[0]]} ضد ({worst[1]['verdict_ar']})"
    else:
        head = "مفيش ميزة واضحة على أي مدة - الاستنى قرار"
    return {"asset": b["symbol"], "price": px, "horizons": hz, "head": head, "flow": fr, "inst": cr, "news": nt, "guard": guard,
            "ideas": [i for i in (ideas or [])], "stats": st, "setups": setups or []}


def run(asset: str, cls: str, name: str, candles=None, holdings=None, news_items=None, flow=None, cot=None) -> dict:
    """Network path: load everything for one market and think (flow / cot / news injectable for tests)."""
    from modules import spot_dash, spot_flow, spot_ideas, spot_inst, spot_news
    b = spot_dash.load_bundle(asset, candles)
    tagged = spot_news.tag(spot_news.fetch() if news_items is None else news_items)
    nt = spot_news.tilt(tagged, asset)
    fl = spot_flow.fetch(asset, cls) if flow is None else flow
    ct = spot_inst.fetch(asset) if cot is None else cot
    ideas, log = spot_ideas.build(asset, cls, name, b, nt)
    from modules import spot_setups
    try:
        setups = spot_setups.scan(b, fl, ct)
    except Exception as e:
        setups, log = [], log + [f"مكتبة السيت أبات: {type(e).__name__}"]
    out = think(b, fl, ct, nt, ideas, holdings, setups)
    out.update({"name": name, "cls": cls, "bundle": b, "raw_flow": fl, "raw_cot": ct, "log": log, "tagged": tagged[:8]})
    return out


def text_ar(br: dict) -> str:
    """Arabic Telegram text: the head line, the four horizons with levels, the holdings guard, flow + institutions."""
    lines = [f"🧠 {br.get('name', br['asset'])} · {_f(br['price'])} - {br['head']}"]
    for k in ("day", "week", "month", "year"):
        h = br["horizons"][k]
        lv = f" · دخول {_f(h['entry'][0])}-{_f(h['entry'][1])} وقف {_f(h.get('stop'))} هدف {_f(h.get('target'))}" if h.get("entry") and h["score"] >= 15 else ""
        lines.append(f"• {h['label']}: {h['verdict_ar']} ({h['score']:+d}){lv}")
    for g in br.get("guard", []):
        lines.append(f"📦 اللي معاك: {g['action_ar']} - {g['why']}")
    lines += ["📊 الأوردر فلو:"] + ["  " + x for x in br["flow"]["lines"][:8]] + ["🏦 المؤسسات:"] + ["  " + x.strip() for x in br["inst"]["lines"][:4]]
    lines.append("قواعد، لسه من غير باك تيست لكل مدة. مفيش أي أمر بيتنفذ.")
    return "\n".join(lines)
