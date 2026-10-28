"""Calibration tab (Stats page): is a result still there outside the sample it was tuned on?

Two honest views from data/strategy_lab.json (nothing invented):
 1. Chain study rows (*CHAIN*, the only rows that carry is_avgR / oos_avgR): in-sample vs out-of-sample average R per grade / layer.
    A gap of IS over OOS above 0.05R is flagged as a possible over-fit; n < 30 is dimmed as "not evidence".
 2. One detector across timeframes (side "all", tf != "all"): n, win %, avgR, the random-entry baseline and the difference.
There is no time series in the file, so this tab does NOT show decay over time (that needs weekly snapshots).
"""
from __future__ import annotations

from modules.lab_shared import MIN_N, _all_rows, load_rows, t

_GAP = 0.05


def chain_rows() -> list[dict]:
    return [r for r in _all_rows() if r.get("key") == "*CHAIN*" and r.get("oos_avgR") is not None and r.get("is_avgR") is not None]


def flag(row: dict) -> str:
    if row.get("is_n", 0) < MIN_N or row.get("oos_n", 0) < MIN_N:
        return "🔘"
    return "⚠️" if (row["is_avgR"] - row["oos_avgR"]) > _GAP else "✅" if row["oos_avgR"] > 0 else "➖"


def tf_rows(key: str) -> list[dict]:
    return sorted([r for r in load_rows("all") if r.get("key") == key and r.get("tf") != "all"], key=lambda r: r.get("avgR", 0), reverse=True)


def render_calibration_lab() -> None:
    import streamlit as st
    from modules.ui_kit import strip

    ch = chain_rows()
    if not ch:
        st.info(t("لا توجد بيانات معايرة في ملف المعمل.", "No calibration data in the lab file."))
        return
    ok = [r for r in ch if r.get("is_n", 0) >= MIN_N and r.get("oos_n", 0) >= MIN_N]
    gap = [r for r in ok if (r["is_avgR"] - r["oos_avgR"]) > _GAP]
    pos = [r for r in ok if r["oos_avgR"] > 0]
    st.markdown(strip([
        (t("صفوف السلسلة", "Chain rows"), str(len(ch)), t("فيها داخل/خارج العينة", "with in/out of sample"), "", ""),
        (t("كفاية بيانات", "Enough data"), str(len(ok)), f"n≥{MIN_N} " + t("في الاتنين", "in both"), "", ""),
        (t("فجوة محتملة", "Possible over-fit"), str(len(gap)), f"IS − OOS > {_GAP}R", "down" if gap else "", ""),
        (t("OOS موجب", "OOS above 0"), str(len(pos)), t("غير مثبت", "not proven"), "", t("avgR خارج العينة فوق صفر", "out-of-sample avgR above 0"))]), unsafe_allow_html=True)
    st.subheader(t("داخل العينة مقابل خارجها (دراسة السلسلة)", "In-sample vs out-of-sample (chain study)"))
    h = [t("الحالة", "Group"), "n", "avgR", "IS n", "IS avgR", "OOS n", "OOS avgR", t("الفجوة", "Gap"), ""]
    table = [{h[0]: r["side"], h[1]: int(r["n"]), h[2]: round(r["avgR"], 3), h[3]: int(r["is_n"]), h[4]: round(r["is_avgR"], 3), h[5]: int(r["oos_n"]),
              h[6]: round(r["oos_avgR"], 3), h[7]: round(r["is_avgR"] - r["oos_avgR"], 3), h[8]: flag(r)} for r in sorted(ch, key=lambda r: r["n"], reverse=True)]
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.caption(t(f"⚠️ = IS أحسن من OOS بأكتر من {_GAP}R (احتمال تشبّع)، 🔘 = n < {MIN_N} (مش دليل)، ✅ = OOS موجب، ➖ = غير ذلك. الملف مفيهوش زمن، فالانحلال عبر الوقت غير معروض.",
                 f"⚠️ = IS beats OOS by more than {_GAP}R (possible over-fit), 🔘 = n < {MIN_N} (not evidence), ✅ = OOS above 0, ➖ = otherwise. The file has no time axis, so decay over time is not shown."))

    keys = sorted({r["key"] for r in load_rows("all") if r.get("tf") != "all" and r.get("key") != "*CHAIN*"})
    if keys:
        st.subheader(t("كاشف واحد عبر الفريمات", "One detector across timeframes"))
        k = st.selectbox(t("الكاشف", "Detector"), keys, key="calib_key")
        rows = tf_rows(k)
        h2 = [t("الفريم", "TF"), "n", t("فوز%", "Win%"), "avgR", t("عشوائي avgR", "Random avgR"), t("الفرق", "Diff")]
        st.dataframe([{h2[0]: r["tf"], h2[1]: int(r["n"]), h2[2]: round(r.get("win", 0), 1), h2[3]: round(r["avgR"], 3),
                       h2[4]: None if r.get("base_avgR") is None else round(r["base_avgR"], 3),
                       h2[5]: None if r.get("base_avgR") is None else round(r["avgR"] - r["base_avgR"], 3)} for r in rows], use_container_width=True, hide_index=True)
