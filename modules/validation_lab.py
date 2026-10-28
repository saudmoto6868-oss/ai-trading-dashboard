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
_LAB_PATH = Path(__file__).resolve().parent.parent / "data" / "strategy_lab.json"
_MIN_N = 30          # minimum trades to show any number
_OFF_MIN_N = 300     # OFF threshold (mirrors lab_tiers)
_OFF_MAX_R = -0.06   # OFF threshold
_POS_MIN_R = 0.0     # positive-evidence threshold


def _load_rows() -> list[dict[str, Any]]:
    """Return all-side rows from strategy_lab.json; empty list on any error."""
    try:
        data = json.loads(_LAB_PATH.read_text())
        return [r for r in data.get("rows", []) if r.get("side") == "all"]
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


# ── public render ─────────────────────────────────────────────────────────────
def render_validation_lab() -> None:
    """Render the Validation Lab tab inside an active Streamlit context."""
    try:
        import streamlit as st
        from modules.ui_kit import strip
        from modules.i18n import L
    except Exception as exc:
        # Hard import failure — can't do anything useful
        import streamlit as st
        st.error(f"مختبر التحقق: خطأ في الاستيراد — {exc}")
        return

    rows = _load_rows()

    # ── no data ───────────────────────────────────────────────────────────────
    if not rows:
        st.info(
            L("لا توجد بيانات في ملف المعمل (data/strategy_lab.json). "
              "شغّل سير العمل Lab Backtest لتوليد البيانات.",
              "No lab data found (data/strategy_lab.json). "
              "Run the Lab Backtest workflow to generate data.")
        )
        return

    # ── summary numbers ───────────────────────────────────────────────────────
    total = len(rows)
    ev_pos = sum(1 for r in rows if r.get("n", 0) >= _MIN_N and r.get("avgR", 0) > _POS_MIN_R)
    off_count = sum(1 for r in rows if r.get("n", 0) >= _OFF_MIN_N and r.get("avgR", 0) <= _OFF_MAX_R)
    edge_count = sum(1 for r in rows if r.get("edge"))

    st.markdown(
        strip([
            (L("الكاشفات", "Detectors"), str(total), L("إجمالي", "total"), "", ""),
            (L("دليل إيجابي", "Positive EV"), str(ev_pos),
             f"n≥{_MIN_N}", "up", L("avgR > 0 مع بيانات كافية", "avgR > 0 with enough data")),
            (L("خارج التقييم", "OFF"), str(off_count),
             f"n≥{_OFF_MIN_N} & R≤{_OFF_MAX_R}", "down",
             L("مستبعد من حساب الدليل", "Excluded from evidence scoring")),
            (L("حافة مؤكدة", "Confirmed Edge"), str(edge_count),
             L("من المعمل", "lab flag"), "up" if edge_count else "",
             L("edge=True في ملف المعمل", "edge=True in lab file")),
        ]),
        unsafe_allow_html=True,
    )

    # ── school filter ─────────────────────────────────────────────────────────
    schools = sorted({r.get("school", "—") for r in rows})
    sel_school = st.selectbox(
        L("المدرسة", "School"),
        [L("الكل", "All")] + schools,
        key="vlab_school",
    )

    # ── tier filter ───────────────────────────────────────────────────────────
    tier_opts = {
        L("الكل", "All"): None,
        L("دليل إيجابي ✅", "Positive EV ✅"): "positive",
        L("حافة مؤكدة ⭐", "Confirmed Edge ⭐"): "edge",
        L("دليل سلبي ⚠️", "Negative EV ⚠️"): "negative",
        L("خارج التقييم 🚫", "OFF 🚫"): "off",
        L("بيانات قليلة 🔘", "Weak data 🔘"): "weak",
    }
    sel_label = st.selectbox(
        L("الفئة", "Tier"),
        list(tier_opts.keys()),
        key="vlab_tier",
    )
    sel_tier = tier_opts[sel_label]

    # ── filter rows ───────────────────────────────────────────────────────────
    filtered = rows
    if sel_school != L("الكل", "All"):
        filtered = [r for r in filtered if r.get("school") == sel_school]
    if sel_tier:
        filtered = [r for r in filtered if _tier(r) == sel_tier]

    filtered = sorted(filtered, key=lambda r: r.get("avgR", 0.0), reverse=True)

    if not filtered:
        st.info(L("لا توجد نتائج بهذا الفلتر.", "No results for this filter."))
        return

    # ── table ─────────────────────────────────────────────────────────────────
    _TIER_ICON = {
        "edge": "⭐", "positive": "✅", "neutral": "➖",
        "negative": "⚠️", "off": "🚫", "weak": "🔘",
    }

    cols = st.columns([2, 2, 1, 1, 1, 1, 1])
    headers = [
        L("المفتاح", "Key"),
        L("المدرسة", "School"),
        L("الإطار", "TF"),
        "n",
        L("فوز%", "Win%"),
        "avgR",
        L("الحالة", "Status"),
    ]
    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")

    for row in filtered:
        t = _tier(row)
        icon = _TIER_ICON.get(t, "")
        n = row.get("n", 0)
        win = row.get("win", 0)
        avg = row.get("avgR", 0.0)
        tf = row.get("tf", "—")

        # Dim rows with insufficient data
        dim = t == "weak"
        fmt_n = str(n) if not dim else f"*{n}*"
        fmt_win = f"{win:.1f}%" if not dim else f"*{win:.1f}%*"
        fmt_avg = f"{avg:+.3f}" if not dim else f"*{avg:+.3f}*"

        c = st.columns([2, 2, 1, 1, 1, 1, 1])
        c[0].markdown(f"`{row.get('key','')}`")
        c[1].markdown(row.get("school", "—"))
        c[2].markdown(tf)
        c[3].markdown(fmt_n)
        c[4].markdown(fmt_win)
        c[5].markdown(fmt_avg)
        c[6].markdown(icon)

    # ── footnotes ─────────────────────────────────────────────────────────────
    st.caption(
        L(
            f"n < {_MIN_N} = بيانات غير كافية (🔘). "
            f"OFF = n ≥ {_OFF_MIN_N} و avgR ≤ {_OFF_MAX_R} → مستبعد من حساب الدليل. "
            "⭐ = حافة مؤكدة من المعمل. لا أرقام مُخترعة — كل الأرقام من strategy_lab.json.",
            f"n < {_MIN_N} = insufficient data (🔘). "
            f"OFF = n ≥ {_OFF_MIN_N} and avgR ≤ {_OFF_MAX_R} → excluded from evidence scoring. "
            "⭐ = lab-confirmed edge. No invented numbers — all figures from strategy_lab.json."
        )
    )
