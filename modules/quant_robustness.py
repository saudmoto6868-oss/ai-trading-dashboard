"""Robustness tab (Stats page): strategy x market-context grid built from the REAL lab rows (data/strategy_lab.json), no invented numbers.

Columns = contexts the weekly lab already splits every detector by: trend side (100-bar trend: with / flat / against) and session (UTC).
A cell = that detector's lab trades in that context: n, win %, avg R (gross), net R (avg R minus the planning cost COST_R), t vs a random
direction baseline, and the in-sample / out-of-sample halves. Verdict per cell:
  * not_evidence  n < MIN_N (printed, never ranked)
  * edge          n >= MIN_N, t above the bar, net > 0, both halves (IS and OOS, net of costs) > 0. Bar = max(3, Bonferroni t over every cell
                  with n >= MIN_N on the page): ~300 cells are looked at, so a lone t of 3 is what luck alone gives (hub_core.bonferroni_t, same as Research Hub)
  * positive      net > 0 but not all of the above (unproven)
  * negative      net < 0
"Survives the trend contexts" = at least 2 of with / flat / against have n >= MIN_N, and every one that does has net > 0 (flat is often empty). Past lab trades on candles only: not a forecast.
Markouts (1s / 10s / 60s after a fill) need real fill times + tick data; the lab has neither, so that panel says "not measured" instead of drawing numbers.
"""
from __future__ import annotations

from modules.hub_core import bonferroni_t
from modules.lab_shared import MIN_N, _all_rows, t

COST_R = 0.10   # same planning cost as the lab (strategy_lab.COST_R); lab avgR / is_avgR / oos_avgR are gross
TREND_CTX = ("trend-with", "trend-flat", "trend-against")
SESSION_CTX = ("ses-Asia 00-07", "ses-London 07-12", "ses-New York 12-20", "ses-Late 20-24")
CONTEXTS = TREND_CTX + SESSION_CTX
CTX_LABEL = {"trend-with": ("مع الترند", "With trend"), "trend-flat": ("ترند مسطح", "Flat trend"), "trend-against": ("ضد الترند", "Against trend"),
             "ses-Asia 00-07": ("آسيا", "Asia"), "ses-London 07-12": ("لندن", "London"), "ses-New York 12-20": ("نيويورك", "New York"),
             "ses-Late 20-24": ("آخر اليوم", "Late")}
_COLOR = {"edge": "#1f6f3a", "positive": "#2e4d34", "negative": "#6b2323", "not_evidence": "#5a4a1a", "none": "#222"}


def _net(v):
    return None if v is None else round(v - COST_R, 3)


def cell(row: dict | None, t_bar: float = 3.0) -> dict:
    """One context cell from one lab row (None -> empty cell)."""
    if not row:
        return {"n": 0, "verdict": "none"}
    n, avg = int(row.get("n") or 0), row.get("avgR")
    c = {"n": n, "win": row.get("win"), "avgR": avg, "net": _net(avg), "t": row.get("t"),
         "is_n": row.get("is_n"), "is_net": _net(row.get("is_avgR")), "oos_n": row.get("oos_n"), "oos_net": _net(row.get("oos_avgR"))}
    if n < MIN_N or avg is None:
        c["verdict"] = "not_evidence"
    elif c["net"] > 0 and (c["t"] or 0) > t_bar and (c["is_net"] or 0) > 0 and (c["oos_net"] or 0) > 0:
        c["verdict"] = "edge"
    elif c["net"] > 0:
        c["verdict"] = "positive"
    else:
        c["verdict"] = "negative"
    return c


def build_matrix(rows: list[dict]) -> list[dict]:
    """-> one entry per detector key (tf 'all'): {key, school, n_all, cells{ctx: cell}, tested, passed, survives_trend, trials, t_bar}, best first.
    trials = every context cell with n >= MIN_N on the page (the multiple-testing count); t_bar = the t a star needs after that many looks."""
    by = {}
    for r in rows:
        if r.get("tf") != "all" or str(r.get("key", "")).startswith("*") or r.get("school") == "exit":
            continue
        if r.get("side") == "all" or r.get("side") in CONTEXTS:
            by.setdefault(r["key"], {})[r["side"]] = r
    by = {k: v for k, v in by.items() if any(s in v for s in CONTEXTS)}
    trials = sum(int(r.get("n") or 0) >= MIN_N for v in by.values() for s, r in v.items() if s in CONTEXTS)
    t_bar = round(max(3.0, bonferroni_t(trials)), 2)
    out = []
    for k, sides in by.items():
        cells = {ctx: cell(sides.get(ctx), t_bar) for ctx in CONTEXTS}
        tested = [c for c in cells.values() if c["n"] >= MIN_N]
        trend = [cells[x] for x in TREND_CTX if cells[x]["n"] >= MIN_N]   # 'flat' is often empty: judge the trend contexts that have evidence
        base = sides.get("all") or next(iter(sides.values()))
        out.append({"key": k, "school": base.get("school", "Other"), "n_all": int((sides.get("all") or {}).get("n") or 0), "cells": cells,
                    "tested": len(tested), "passed": sum(c["net"] > 0 for c in tested),
                    "survives_trend": len(trend) >= 2 and all(c["net"] > 0 for c in trend), "trials": trials, "t_bar": t_bar})
    out.sort(key=lambda e: (-e["survives_trend"], -e["passed"], -(e["passed"] / e["tested"] if e["tested"] else 0), e["key"]))
    return out


def _txt(c: dict) -> str:
    if c["verdict"] == "none":
        return "—"
    s = f"{c['net']:+.2f}R · n={c['n']}" if c.get("net") is not None else f"n={c['n']}"
    return s + (" ⭐" if c["verdict"] == "edge" else " ⚠" if c["verdict"] == "not_evidence" else "")


def render() -> None:
    import pandas as pd
    import streamlit as st

    st.subheader(t("متانة الاستراتيجيات — من صفقات المختبر الحقيقية", "Strategy robustness - from the real lab trades"))
    mx = build_matrix(_all_rows())
    if not mx:
        st.info(t("مفيش بيانات مختبر (data/strategy_lab.json فاضي أو مش موجود). مفيش أرقام تتعرض.",
                  "No lab data (data/strategy_lab.json missing or empty). No numbers to show."))
        return
    bar, trials = mx[0]["t_bar"], mx[0]["trials"]
    st.caption(t(f"كل خانة = صافي R لكل صفقة بعد خصم تكلفة تقديرية {COST_R}R، وعدد الصفقات. أقل من {MIN_N} صفقة = مش دليل (⚠). "
                 f"⭐ = صافي موجب + t أكبر من {bar} مقابل اتجاه عشوائي + موجب في نصّي البيانات (داخل وخارج العينة). "
                 f"الحد {bar} مش 3 لأن الصفحة بتبص على {trials} خانة مرة واحدة (تصحيح Bonferroni)، فـ t=3 لوحدها ممكن تطلع بالحظ. صفقات تاريخية على شموع، مش توقع ولا نصيحة.",
                 f"Each cell = net R per trade after a {COST_R}R planning cost, and the trade count. Under {MIN_N} trades = not evidence (⚠). "
                 f"⭐ = net positive + t > {bar} vs a random direction + positive in both halves (in- and out-of-sample). "
                 f"The bar is {bar}, not 3, because the page looks at {trials} cells at once (Bonferroni), so a lone t of 3 can be luck. Past candle-based lab trades, not a forecast or advice."))
    schools = sorted({e["school"] for e in mx})
    c1, c2 = st.columns([2, 1])
    pick = c1.multiselect(t("المدرسة", "School"), schools, default=[], key="rb_school", placeholder=t("الكل", "All"))
    only = c2.checkbox(t("اللي بتصمد في كل حالات الترند بس", "Only those that survive every trend context"), key="rb_only")
    rows = [e for e in mx if (not pick or e["school"] in pick) and (not only or e["survives_trend"])]
    n_surv = sum(e["survives_trend"] for e in mx)
    m = st.columns(3)
    m[0].metric(t("استراتيجيات", "Strategies"), len(mx))
    m[1].metric(t("بتصمد مع/مسطح/ضد الترند", "Survive with/flat/against trend"), n_surv)
    m[2].metric(t("خانات فيها ⭐", "Cells with ⭐"), sum(c["verdict"] == "edge" for e in mx for c in e["cells"].values()))
    if not rows:
        st.info(t("مفيش استراتيجية بتعدي الفلتر ده.", "No strategy passes this filter."))
    else:
        cols = [t(*CTX_LABEL[c]) for c in CONTEXTS]
        df = pd.DataFrame([{t("الاستراتيجية", "Strategy"): e["key"], t("المدرسة", "School"): e["school"],
                            **{cols[i]: _txt(e["cells"][c]) for i, c in enumerate(CONTEXTS)},
                            t("صافي موجب / مختبر", "Net + / tested"): f"{e['passed']}/{e['tested']}"} for e in rows])
        verd = pd.DataFrame([{cols[i]: e["cells"][c]["verdict"] for i, c in enumerate(CONTEXTS)} for e in rows])

        def _style(_):
            s = pd.DataFrame("", index=df.index, columns=df.columns)
            for col in cols:
                s[col] = [f"background-color:{_COLOR[v]};color:#eee" for v in verd[col]]
            return s
        st.dataframe(df.style.apply(_style, axis=None), hide_index=True, use_container_width=True)
        key = st.selectbox(t("تفاصيل استراتيجية", "Strategy details"), [e["key"] for e in rows], key="rb_detail")
        e = next(x for x in rows if x["key"] == key)
        st.dataframe(pd.DataFrame([{t("الحالة", "Context"): t(*CTX_LABEL[c]), "n": e["cells"][c]["n"], t("نجاح %", "Win %"): e["cells"][c].get("win"),
                                    t("متوسط R (قبل التكلفة)", "Avg R (gross)"): e["cells"][c].get("avgR"), t("صافي R", "Net R"): e["cells"][c].get("net"),
                                    "t": e["cells"][c].get("t"), t("صافي داخل العينة", "In-sample net"): e["cells"][c].get("is_net"),
                                    t("صافي خارج العينة", "Out-of-sample net"): e["cells"][c].get("oos_net"), t("الحكم", "Verdict"): e["cells"][c]["verdict"]}
                                   for c in CONTEXTS]), hide_index=True, use_container_width=True)
    st.markdown("#### " + t("Markout (حركة السعر بعد الدخول بـ 1ث / 10ث / 60ث)", "Markouts (price move 1s / 10s / 60s after the fill)"))
    st.info(t("مش متقاس لسه: محتاج أوقات تنفيذ حقيقية وبيانات تيك، والمختبر شغال على شموع بس. مش هنعرض أرقام لحد ما يبقى فيه سجل تنفيذ حقيقي.",
              "Not measured yet: it needs real fill times and tick data, and the lab only uses candles. No numbers are shown until a real fill log exists."))
