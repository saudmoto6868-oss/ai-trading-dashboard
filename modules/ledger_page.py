"""Strategy Ledger page (PAGE 23, Trading hub next to the Journal; owner 2026-11-24): every strategy's plans, each one replayed on the
candles and explained, ranked per strategy with gradual advice. Data: modules/signal_ledger.py. Read-only except "Grade now"."""
from __future__ import annotations

import time

import pandas as pd
import streamlit as st

from modules import signal_ledger as SL
from modules.i18n import lang

_SRC = {"scanner": ("Server scanner", "سكانر السيرفر"), "orderflow": ("Order flow (direction test: stop 1 ATR, target 1.5 ATR)", "الأوردر فلو (اختبار اتجاه: ستوب 1 ATR، هدف 1.5 ATR)"), "kzs": ("Kill Zone Sniper", "كيل زون سنايبر"), "2.6": ("2.6 strategy", "استراتيجية 2.6"),
        "gann": ("Gann zones", "زونات جان"), "harmonic": ("Harmonic patterns", "الأنماط التوافقية")}
_LEVEL = {"collecting": ("collecting (n < 10)", "بنجمّع (أقل من 10)"), "lean": ("lean, NOT evidence (10-29)", "ميل، مش دليل (10-29)"),
          "evidence": ("evidence (n >= 30, positive after costs)", "دليل (30+، موجب بعد التكاليف)"),
          "evidence_weak": ("n >= 30, edge not proven", "30+، الميزة مش مثبتة")}
_OUT = {"tp1": "TP1", "tp2": "TP2", "tp3": "TP3", "sl": "SL", "time": ("time exit", "خروج بالوقت"), "no_fill": ("not filled", "ماتنفذتش"),
        "ran_away": ("missed (ran away)", "فاتتنا"), "no_data": ("no candles", "مفيش شموع")}


def _ar() -> bool:
    return lang() == "ar"


def _t(en: str, ar: str) -> str:
    return ar if _ar() else en


def _w(pair) -> str:
    return pair if isinstance(pair, str) else pair[1 if _ar() else 0]


def _src(k: str) -> str:
    head, _, rest = k.partition(" · ")
    if head.startswith("setup:"):   # the brain's setup detectors, one strategy each
        return _t("Setup ", "سيتاب ") + head[6:].upper() + (" · " + rest if rest else "")
    return _w(_SRC.get(head, (head, head))) + (" · " + rest if rest else "")


def _utc(ms) -> str:
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(int(ms) / 1000)) if ms else ""


def render():
    st.subheader(_t("Strategy Ledger", "دفتر الاستراتيجيات"))
    st.caption(_t(
        "Every strategy's plans, kept apart. Each plan is replayed on the candles after it appeared: fill, targets / stop in time order, how far it went for / "
        "against us, what happened after the exit, the best entry that existed, and the same trade with other stop / target sizes. Forward only (no replayed "
        "history). R = the plan's own risk; costs %.2fR per trade are taken off; a candle touching stop and target counts the stop. Under 30 trades nothing is evidence. "
        "Advice is a suggestion for the lab, it never changes a strategy by itself." % SL.COST_R,
        "خطط كل استراتيجية، كل واحدة لوحدها. كل خطة بتتعاد على الشموع اللي بعدها: التنفيذ، الأهداف / الستوب بالترتيب، راحت قد إيه معانا / ضدنا، حصل إيه بعد الخروج، "
        "أحسن دخول كان موجود، ونفس الصفقة بأحجام ستوب / هدف تانية. للأمام بس (من غير تاريخ متعاد). R = مخاطرة الخطة نفسها؛ التكاليف %.2fR للصفقة مخصومة؛ شمعة لمست الستوب "
        "والهدف = ستوب. تحت 30 صفقة مفيش دليل. النصيحة اقتراح للمعمل، مش بتغيّر الاستراتيجية لوحدها." % SL.COST_R))
    sigs = SL.all_signals()
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button(_t("Grade now", "قيّم دلوقتي"), help=_t("Replays the signals whose time has come (needs price data).", "بيعيد الإشارات اللي وقتها جه (محتاج بيانات أسعار).")):
            try:
                from modules.market_cache import get_klines
                n = SL.grade_pending(get_klines, limit=120)
                st.success(_t("%d graded" % n, "اتقيّم %d" % n))
                sigs = SL.all_signals()
            except Exception as e:
                st.error(f"{type(e).__name__}: {e}")
    pend = sum(1 for s in sigs if s.get("status") == "pending")
    with c2:
        st.metric(_t("Signals", "الإشارات"), len(sigs), _t("%d waiting" % pend, "%d مستنية" % pend), delta_color="off")
    with c3:
        by = st.radio(_t("Group by", "التجميع"), ["src", "src_sub", "src_tf", "why"], horizontal=True, key="sl_by",
                      format_func=lambda k: {"src": _t("strategy", "الاستراتيجية"), "src_sub": _t("strategy + detail", "الاستراتيجية + التفصيل"),
                                             "src_tf": _t("strategy + timeframe", "الاستراتيجية + الفريم"), "why": _t("scanner ingredient", "مكوّن السكانر")}[k])
    if not sigs:
        st.info(_t("No signals yet. They arrive from the server scanner (Workspace scan) and from chart strategies (Kill Zone Sniper, 2.6, Gann, Harmonic) while their chart is open.",
                   "لسه مفيش إشارات. بتيجي من سكانر السيرفر (سكان الـ Workspace) ومن استراتيجيات الشارت (كيل زون سنايبر، 2.6، جان، الهارمونيك) وهي مفتوحة على الشارت."))
        return
    stats = SL.stats(by=by, sigs=sigs)
    order = {"evidence": 0, "evidence_weak": 1, "lean": 2, "collecting": 3}
    rows = sorted(stats.items(), key=lambda kv: (order[kv[1]["level"]], -((kv[1].get(kv[1].get("best_style") or "split") or {}).get("lb") or -9), -kv[1]["n"]))
    table = []
    for k, r in rows:
        b = r.get(r.get("best_style") or "split") or {}
        rc, ls = r.get("reach", {}), r.get("lessons", {})
        table.append({_t("Strategy", "الاستراتيجية"): _src(k), _t("Level", "المستوى"): _w(_LEVEL[r["level"]]), _t("Filled", "اتنفذت"): r["n"],
                      _t("Signals", "إشارات"): r["signals"], _t("No fill %", "ماتنفذتش %"): r.get("no_fill_pct"),
                      _t("Win %", "فوز %"): b.get("win_pct"), _t("Avg R", "متوسط R"): b.get("avg_r"), _t("Best exit", "أحسن خروج"): r.get("best_style"),
                      "TP1 %": rc.get("tp1"), "TP2 %": rc.get("tp2"), "TP3 %": rc.get("tp3"), "SL %": r.get("sl_pct"),
                      _t("Early %", "بدري %"): ls.get("early_entry"), _t("Late %", "متأخر %"): ls.get("late_entry"),
                      _t("Stop hunt %", "صيد ستوب %"): ls.get("stop_hunt"), _t("Left 1R+ %", "ساب 1R+ %"): ls.get("left_on_table"),
                      _t("Best stop|target", "أحسن ستوب|هدف"): (r.get("best_cell") or {}).get("cell")})
    st.dataframe(pd.DataFrame(table), hide_index=True, width="stretch")
    st.markdown("#### " + _t("What the ledger suggests (gradually)", "اللي الدفتر بيقترحه (بالتدريج)"))
    for k, r in rows:
        with st.expander(_src(k) + " · " + _w(_LEVEL[r["level"]]) + " · n=%d" % r["n"], expanded=r["level"] in ("evidence", "lean")):
            for a in SL.advice(r, ar=_ar()):
                st.markdown("- " + a)
    st.markdown("#### " + _t("Every trade, replayed", "كل صفقة، متعادة"))
    graded = [s for s in sigs if s.get("status") == "graded"]
    srcs = sorted({s["src"] for s in sigs})
    pick = st.multiselect(_t("Strategies", "الاستراتيجيات"), srcs, default=srcs, format_func=_src, key="sl_src")
    show = [s for s in graded if s["src"] in pick][:300]
    trows = []
    for s in show:
        rv = s["review"]
        o = _OUT.get(rv.get("outcome"), rv.get("outcome"))
        trows.append({_t("Time (UTC)", "الوقت (UTC)"): _utc(s["t0"]), _t("Strategy", "الاستراتيجية"): _src(s["src"] + (" · " + s["sub"] if s.get("sub") else "")),
                      _t("Symbol", "الرمز"): s["symbol"], "TF": s["tf"], _t("Side", "الاتجاه"): s["dir"], _t("Result", "النتيجة"): _w(o),
                      "R": (rv.get("r") or {}).get("split"), "MFE": rv.get("mfe_r"), "MAE": rv.get("mae_before_tp1_r"),
                      _t("Why", "ليه"): " · ".join(SL.lesson_text(x, _ar()) for x in rv.get("lessons", []))})
    if trows:
        st.dataframe(pd.DataFrame(trows), hide_index=True, width="stretch")
        opts = {f'{_utc(s["t0"])} · {s["symbol"]} {s["tf"]} {s["dir"]} · {_src(s["src"])}': s for s in show}
        sel = st.selectbox(_t("Open one trade", "افتح صفقة"), list(opts), key="sl_one")
        if sel:
            _card(opts[sel])
    else:
        st.caption(_t("No graded trade yet for these strategies.", "لسه مفيش صفقة اتقيّمت للاستراتيجيات دي."))


def _card(s: dict):
    """The written scenario vs what the candles did, in plain sentences."""
    rv, ar = s["review"], _ar()
    st.markdown("**" + _t("The plan as written", "الخطة زي ما اتكتبت") + f"**: {s['dir']} · entry {s['entry']:g} · SL {s['sl']:g} · "
                + " · ".join("TP%d %g (%.2fR)" % (i + 1, t, r) for i, (t, r) in enumerate(zip(s["tps"], rv.get("rr") or [0] * len(s["tps"])))))
    if s.get("why"):
        st.caption(_t("Reasons it listed: ", "الأسباب اللي كتبها: ") + ", ".join(s["why"]))
    if not rv.get("filled"):
        st.markdown("- " + " ".join(SL.lesson_text(x, ar) for x in rv.get("lessons", [])) + _t(" Price moved %.2fR toward the target meanwhile.", " السعر اتحرك %.2fR ناحية الهدف في الوقت ده.") % rv.get("move_without_us_r", 0))
        return
    hits = rv.get("hits") or {}
    st.markdown("- " + _t("Filled %s (after %d candles)", "اتنفذت %s (بعد %d شمعة)") % (_utc(rv.get("fill_t")), rv.get("bars_to_fill", 0)))
    for lv in ("tp1", "tp2", "tp3"):
        if lv in hits:
            st.markdown("- %s %s" % (lv.upper(), _utc(hits[lv])))
    if rv.get("sl_t"):
        st.markdown("- " + _t("Stop %s", "الستوب %s") % _utc(rv["sl_t"]))
    r = rv.get("r") or {}
    st.markdown("- " + _t("R: thirds + break-even %.2f · all at TP1 %.2f · all at the last target %.2f (before costs)",
                          "R: تلت عند كل هدف + نقطة الدخول %.2f · كله عند TP1 %.2f · كله عند آخر هدف %.2f (قبل التكاليف)") % (r.get("split", 0), r.get("tp1_all", 0), r.get("last_all", 0)))
    st.markdown("- " + _t("Best move our way %.2fR, worst against us before TP1 %.2fR", "أحسن حركة معانا %.2fR، وأسوأ حركة ضدنا قبل TP1 %.2fR") % (rv.get("mfe_r", 0), rv.get("mae_before_tp1_r", 0)))
    b = rv.get("best") or {}
    st.markdown("- " + _t("Best chance that existed: enter at %g (%s) for a %.2fR move with this stop size",
                          "أحسن فرصة كانت موجودة: دخول عند %g (%s) لحركة %.2fR بنفس حجم الستوب") % (b.get("entry", 0), _utc(b.get("t")), b.get("move_r", 0)))
    for x in rv.get("lessons", []):
        st.markdown("- **" + SL.lesson_text(x, ar) + "**")
    notes = SL.context_notes(s, ar)
    if notes:
        st.caption(_t("At entry: ", "وقت الدخول: ") + " · ".join(notes))
    g = rv.get("grid") or {}
    if g:
        ms, ks = SL.SL_GRID, SL.TP_GRID
        df = pd.DataFrame([[g.get("%g|%g" % (m, k)) for k in ks] for m in ms], index=[_t("stop %g×", "ستوب %g×") % m for m in ms], columns=["TP %gR" % k for k in ks])
        st.caption(_t("Same trade, other sizes (R per unit of each stop, before costs):", "نفس الصفقة بأحجام تانية (R لكل وحدة من الستوب ده، قبل التكاليف):"))
        st.dataframe(df, width="stretch")
