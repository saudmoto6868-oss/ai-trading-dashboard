"""One 'Lab Summary' page (owner 2026-10-28: the four separate lab tabs were mostly tables). A short summary on top, then each
former tab as a collapsed section, so nothing is lost and nothing clutters. Evidence only: no trade decision, no advice."""
from __future__ import annotations

from modules.lab_shared import MIN_N, load_rows, t, tier


def lab_numbers() -> dict:
    """Counts from the weekly lab file (side == 'all' rows): how many tests, how many have enough trades, how many sit above 0, flagged, OFF."""
    rows = load_rows("all")
    enough = [r for r in rows if r.get("n", 0) >= MIN_N]
    tiers = [tier(r) for r in rows]
    return {"rows": len(rows), "enough": len(enough), "positive": sum(1 for r in enough if r.get("avgR", 0) > 0),
            "edge": tiers.count("edge"), "off": tiers.count("off")}


def render_lab_summary(payload: dict | None = None) -> None:
    import streamlit as st
    from modules import calibration_lab, decision_desk, rotation_scan, validation_lab

    k = lab_numbers()
    if not k["rows"]:
        st.info(t("لا توجد بيانات في ملف المعمل (data/strategy_lab.json).", "No data in the lab file (data/strategy_lab.json)."))
    else:
        a, b, c, d = st.columns(4)
        a.metric(t("اختبارات المعمل", "Lab tests"), k["rows"])
        b.metric(t(f"فيها {MIN_N}+ صفقة", f"With {MIN_N}+ trades"), k["enough"])
        c.metric(t("متوسطها موجب (غير مثبت)", "Average above 0 (not proven)"), k["positive"])
        d.metric(t("علامة edge / OFF", "edge flag / OFF"), f"{k['edge']} / {k['off']}")
        st.caption(t(f"أقل من {MIN_N} صفقة = مش دليل. كل اختبار إضافي بيزوّد فرصة نتيجة موجبة بالصدفة. ده وصف للمعمل مش توقع ولا نصيحة.",
                     f"Under {MIN_N} trades = not evidence. Every extra test raises the chance of a positive result by luck. A description of the lab, not a forecast or advice."))
    sections = [(t("آخر مسح: ملخص الأدلة لكل Setup", "Last scan: evidence per setup"), lambda: decision_desk.render_decision_desk(payload or {})),
                (t("دوران الفئات (آخر مسح)", "Class rotation (last scan)"), lambda: rotation_scan.render_rotation_scan(payload or {})),
                (t("المعايرة: داخل/خارج العينة", "Calibration: in/out of sample"), calibration_lab.render_calibration_lab),
                (t("جدول المعمل الكامل", "Full lab table"), validation_lab.render_validation_lab)]
    for title, fn in sections:
        with st.expander(title, expanded=False):
            try:
                fn()
            except Exception as exc:
                st.error(f"{title}: {exc}")
