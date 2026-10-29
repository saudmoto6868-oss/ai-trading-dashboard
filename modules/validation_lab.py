"""مختبر التحقق — Validation Lab tab.

Reads data/strategy_lab.json (via lab_tiers._load) and renders:
 - Summary strip: total detectors / evidence+ / OFF / edge
 - Tier table: each all-side row grouped by school, sorted by avgR desc
 - OFF section: detectors excluded from scoring (n>=300, avgR<=-0.06)

Honest rules (owner's lab policy):
 - Never invent win rates. All numbers come from strategy_lab.json.
 - "Not evidence" when n < 30 (shown as dim row).
 - edge flag comes from the lab file, not from Claude.
 - t-stat not in current file → skip; add when present.

Usage (in main.py tab):
    from modules.validation_lab import render_validation_lab
    render_validation_lab()
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# ── constants ────────────────────────────────────────────────────────────────
from modules import lab_tiers as _LT

_LAB_PATH = Path(__file__).resolve().parent.parent / "data" / "strategy_lab.json"
_MIN_N = _LT.MIN_N          # minimum trades to show any number (same constants as the evidence score)
_OFF_MIN_N = _LT.OFF_MIN_N  # OFF threshold
_OFF_MAX_R = _LT.OFF_R      # OFF threshold
_POS_MIN_R = 0.0            # avgR above this is only "positive, not proven" (see _tier)


def _t(ar: str, en: str) -> str:
    """Arabic / English text by the app language (modules.i18n.L takes ONE argument, so it cannot take both)."""
    try:
        from modules.i18n import lang
        return ar if lang() == "ar" else en
    except Exception:
        return en


_cache = {"mtime": None, "path": None, "rows": []}


def _load_rows() -> list[dict[str, Any]]:
    """Return all-side rows from strategy_lab.json (cached by file mtime); empty list on any error."""
    try:
        m = os.path.getmtime(_LAB_PATH)
        if _cache["mtime"] == m and _cache["path"] == str(_LAB_PATH):
            return _cache["rows"]
        data = json.loads(_LAB_PATH.read_text())
        rows = [r for r in data.get("rows", []) if r.get("side") == "all"]
        _cache.update(mtime=m, path=str(_LAB_PATH), rows=rows)
        return rows
    except Exception:
        return []


def _tier(row: dict) -> str:
    """Classify a row into display tier (for colour/icon)."""
    n = row.get("n", 0)
    avg = row.get("avgR", 0.0)
    if n < _MIN_N:
        return "weak"          # grey — not enough data
    if n >= _OFF_MIN_N and avg <= _OFF_MAX_R:
        return "off"           # red — excluded from scoring
    if row.get("edge"):
        return "edge"          # gold — lab confirmed edge
    if avg > _POS_MIN_R:
        return "positive"      # green
    if avg < 0:
        return "negative"      # red-ish
    return "neutral"           # flat


# ── public render ─────────────────────────────────────────────────
def render_validation_lab() -> None:
    """Render the Validation Lab tab inside an active Streamlit context."""
    import streamlit as st
    try:
        from modules.ui_kit import strip
    except Exception as exc:
        st.error(_t("مختبر التحقق: خطأ في الاستيراد — ", "Validation Lab: import error - ") + str(exc))
        return

    rows = _load_rows()

    # ── no data ─────────────────────────────────────────────────
    if not rows:
        st.info(_t("لا توجد بيانات في ملف المعمل (data/strategy_lab.json). شغّل سير العمل Lab Backtest لتوليد البيانات.",
                   "No lab data found (data/strategy_lab.json). Run the Lab Backtest workflow to generate data."))
        return

    # ── summary numbers ───────────────────────────────────────────────
    total = len(rows)
    pos = [r for r in rows if r.get("n", 0) >= _MIN_N and r.get("avgR", 0) > _POS_MIN_R]
    off_count = sum(1 for r in rows if r.get("n", 0) >= _OFF_MIN_N and r.get("avgR", 0) <= _OFF_MAX_R)
    edge_count = sum(1 for r in rows if r.get("edge"))

    st.markdown(
        strip([
            (_t("الكاشفات", "Detectors"), str(total), _t("إجمالي", "total"), "", ""),
            (_t("avgR موجب (غير مثبت)", "avgR > 0 (not proven)"), str(len(pos)),
             f"n≥{_MIN_N}", "",
             _t("موجب في العيّنة؛ مع عدد كبير من الاختبارات جزء منه صدفة. المثبت = حافة مؤكدة فقط.",
                "Positive in the sample; with this many tests part of it is chance. Only a confirmed edge is proven.")),
            (_t("خارج التقييم", "OFF"), str(off_count),
             f"n≥{_OFF_MIN_N} & R≤{_OFF_MAX_R}", "down",
             _t("مستبعد من حساب الدليل", "Excluded from evidence scoring")),
            (_t("حافة مؤكدة", "Confirmed Edge"), str(edge_count),
             _t("من المعمل", "lab flag"), "up" if edge_count else "",
             _t("edge=True في ملف المعمل", "edge=True in lab file")),
        ]),
        unsafe_allow_html=True,
    )

    # ── filters ───────────────────────────────────────────────
    all_lbl = _t("الكل", "All")
    schools = sorted({r.get("school", "—") for r in rows})
    sel_school = st.selectbox(_t("المدرسة", "School"), [all_lbl] + schools, key="vlab_school")
    tier_opts = {
        all_lbl: None,
        _t("حافة مؤكدة ⭐", "Confirmed Edge ⭐"): "edge",
        _t("avgR موجب (غير مثبت) ➕", "avgR > 0 (not proven) ➕"): "positive",
        _t("دليل سلبي ⚠️", "Negative ⚠️"): "negative",
        _t("خارج التقييم 🚫", "OFF 🚫"): "off",
        _t("بيانات قليلة 🔘", "Weak data 🔘"): "weak",
    }
    sel_label = st.selectbox(_t("الفئة", "Tier"), list(tier_opts.keys()), key="vlab_tier")
    sel_tier = tier_opts[sel_label]

    filtered = rows
    if sel_school != all_lbl:
        filtered = [r for r in filtered if r.get("school") == sel_school]
    if sel_tier:
        filtered = [r for r in filtered if _tier(r) == sel_tier]
    filtered = sorted(filtered, key=lambda r: r.get("avgR", 0.0), reverse=True)

    if not filtered:
        st.info(_t("لا توجد نتائج بهذا الفلتر.", "No results for this filter."))
        return

    # ── table: ONE element (a row-per-st.columns loop made ~1600 elements) ───────
    icon = {"edge": "⭐", "positive": "➕", "neutral": "➖", "negative": "⚠️", "off": "🚫", "weak": "🔘"}
    h = [_t("المفتاح", "Key"), _t("المدرسة", "School"), _t("الإطار", "TF"), "n", _t("فوز%", "Win%"), "avgR",
         _t("عشوائي avgR", "Random avgR"), _t("الفرق", "Diff"), _t("الحالة", "Status")]
    table = []
    for r in filtered:
        t = _tier(r)
        avg, base = float(r.get("avgR", 0.0)), r.get("base_avgR")
        table.append({h[0]: r.get("key", ""), h[1]: r.get("school", "—"), h[2]: r.get("tf", "—"), h[3]: int(r.get("n", 0)),
                      h[4]: round(float(r.get("win", 0)), 1), h[5]: round(avg, 3),
                      h[6]: None if base is None else round(float(base), 3), h[7]: None if base is None else round(avg - float(base), 3),
                      h[8]: icon.get(t, "")})
    st.dataframe(table, use_container_width=True, hide_index=True)

    # ── footnotes ─────────────────────────────────────────────────
    st.caption(_t(
        f"n < {_MIN_N} = بيانات غير كافية (🔘). OFF = n ≥ {_OFF_MIN_N} و avgR ≤ {_OFF_MAX_R} → مستبعد من حساب الدليل. "
        "⭐ = حافة مؤكدة من المعمل فقط؛ ➕ = avgR موجب في العيّنة وغير مثبت. «عشوائي avgR» = نتيجة الدخول العشوائي في نفس الاختبار. "
        "لا أرقام مُخترعة — كل الأرقام من strategy_lab.json.",
        f"n < {_MIN_N} = insufficient data (🔘). OFF = n ≥ {_OFF_MIN_N} and avgR ≤ {_OFF_MAX_R} → excluded from evidence scoring. "
        "⭐ = lab-confirmed edge only; ➕ = avgR above 0 in the sample, not proven. 'Random avgR' = random entries in the same test. "
        "No invented numbers - all figures from strategy_lab.json."))
