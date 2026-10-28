"""معايرة الكاشفات — Calibration Lab tab.

Shows for each detector (n>=30):
 - In-sample vs Out-of-sample avgR  →  overfitting signal when IS >> OOS
 - Per-timeframe breakdown          →  which TF the detector actually works on
 - Grade breakdown (A/B/C)         →  does quality grade improve the edge?

Data comes from strategy_lab.json rows:
  side=="all"  + tf breakdown  → per-TF calibration
  side=="grade …"              → grade breakdown (only *CHAIN* has these)
  is_avgR / oos_avgR fields    → present on some rows; shown when available

Honest rule: IS>OOS gap shown as ⚠️ overfit warning. Missing fields → hidden.
No numbers invented.

Usage:
    from modules.calibration_lab import render_calibration_lab
    render_calibration_lab()
"""
from __future__ import annotations
from modules.lab_shared import load_rows, tier, fmt_r, TIER_ICON, MIN_N, no_data_msg


# ── helpers ───────────────────────────────────────────────────────────────────
def _overfit_flag(row: dict) -> str:
    """⚠️ if IS avgR is much better than OOS (gap > 0.05R)."""
    is_r = row.get("is_avgR")
    oos_r = row.get("oos_avgR")
    if is_r is None or oos_r is None:
        return ""
    return "⚠️" if (is_r - oos_r) > 0.05 else "✅"


def _tf_table(key: str, tf_rows: list[dict]) -> list[dict]:
    """Return per-TF rows for a given key, sorted by avgR desc."""
    return sorted(
        [r for r in tf_rows if r["key"] == key and r["tf"] != "all"],
        key=lambda r: r.get("avgR", 0), reverse=True
    )


# ── public render ─────────────────────────────────────────────────────────────
def render_calibration_lab() -> None:
    try:
        import streamlit as st
        from modules.ui_kit import strip
        from modules.i18n import L
    except Exception as exc:
        import streamlit as st
        st.error(f"معايرة الكاشفات: خطأ — {exc}")
        return

    all_rows = load_rows("all")
    if not all_rows:
        no_data_msg(st, "لا توجد بيانات في ملف المعمل.", "No lab data found.")
        return

    # split: summary rows (tf==all) vs per-tf rows
    summary = [r for r in all_rows if r.get("tf") == "all"]
    tf_rows  = [r for r in all_rows if r.get("tf") != "all"]

    # ── strip ─────────────────────────────────────────────────────────────────
    has_oos  = sum(1 for r in summary if r.get("oos_avgR") is not None)
    overfit  = sum(1 for r in summary if _overfit_flag(r) == "⚠️")
    with_tf  = len({r["key"] for r in tf_rows})

    st.markdown(strip([
        (L("الكاشفات", "Detectors"),   str(len(summary)),  L("إجمالي","total"),      "",     ""),
        (L("IS vs OOS",  "IS vs OOS"),  str(has_oos),       L("متوفر","available"),   "up"  if has_oos else "", ""),
        (L("إشارة تشبّع","Overfit ⚠️"), str(overfit),       L("IS >> OOS بـ 0.05R+","IS >> OOS by 0.05R+"), "down" if overfit else "", ""),
        (L("لها تفصيل TF","Has TF data"), str(with_tf),    L("كاشف","detectors"),    "", ""),
    ]), unsafe_allow_html=True)

    # ── IS vs OOS table ───────────────────────────────────────────────────────
    oos_rows = [r for r in summary if r.get("is_avgR") is not None]
    if oos_rows:
        st.subheader(L("مقارنة داخل العينة / خارجها (IS vs OOS)", "In-sample vs Out-of-sample"))
        st.caption(L("فجوة > 0.05R تعني احتمال تشبّع في التحسين (⚠️). لا يعني فشلًا قاطعًا.",
                     "Gap > 0.05R suggests possible overfitting (⚠️). Not a definitive failure."))
        oos_rows_s = sorted(oos_rows, key=lambda r: (r.get("is_avgR",0) - r.get("oos_avgR",0)), reverse=True)
        cols = st.columns([2, 1, 1, 1, 1, 1])
        for c, h in zip(cols, [L("المفتاح","Key"), "n", "avgR", "IS avgR", "OOS avgR", ""]):
            c.markdown(f"**{h}**")
        for r in oos_rows_s:
            c = st.columns([2, 1, 1, 1, 1, 1])
            c[0].markdown(f"`{r['key']}`")
            c[1].markdown(str(r["n"]))
            c[2].markdown(fmt_r(r.get("avgR")))
            c[3].markdown(fmt_r(r.get("is_avgR")))
            c[4].markdown(fmt_r(r.get("oos_avgR")))
            c[5].markdown(_overfit_flag(r))
    else:
        st.info(L("حقول IS/OOS غير موجودة في الملف الحالي — ستظهر بعد تحديث المعمل.",
                  "IS/OOS fields not in current lab file — will appear after next lab run."))

    # ── per-TF breakdown ──────────────────────────────────────────────────────
    st.subheader(L("أداء الكاشف حسب الإطار الزمني", "Detector performance by timeframe"))
    keys = sorted({r["key"] for r in tf_rows})
    sel = st.selectbox(L("الكاشف", "Detector"), keys, key="cal_key")
    rows_k = _tf_table(sel, tf_rows)
    if rows_k:
        cols = st.columns([1, 1, 1, 1, 1])
        for c, h in zip(cols, [L("الإطار","TF"), "n", L("فوز%","Win%"), "avgR", ""]):
            c.markdown(f"**{h}**")
        for r in rows_k:
            t = tier(r)
            c = st.columns([1, 1, 1, 1, 1])
            c[0].markdown(r["tf"])
            c[1].markdown(str(r["n"]) if r["n"] >= MIN_N else f"*{r['n']}*")
            c[2].markdown(f"{r.get('win',0):.1f}%")
            c[3].markdown(fmt_r(r.get("avgR")))
            c[4].markdown(TIER_ICON.get(t, ""))
    else:
        st.info(L("لا يوجد تفصيل TF لهذا الكاشف.", "No per-TF data for this detector."))

    st.caption(L(f"n < {MIN_N} → بيانات غير كافية (🔘). أرقام من strategy_lab.json فقط.",
                 f"n < {MIN_N} → insufficient data (🔘). All figures from strategy_lab.json."))
