"""مكتب القرار — Decision Desk tab.

Aggregates the last Workspace scan result (session_state["last_result"])
into one decision card:
  - Direction + stars (from scorer.aggregate)
  - Lab evidence score (from lab_tiers.evidence)
  - OFF signal warning
  - HTF confirmation summary
  - Pre-planned scenarios (from scorer.scenarios)
  - Gate: passes only when direction set + stars >= 2 + evidence not None + not against

Why session_state only (no live scan):
  Same reason as rotation_scan — avoids double CPU on Stats page.
  The Workspace already ran the scan; we just summarise it here.

Usage:
    from modules.decision_desk import render_decision_desk
    render_decision_desk()
"""
from __future__ import annotations
from modules.lab_shared import fmt_r, no_data_msg

_STAR = "★"
_EMPTY = "☆"
_MAX_STARS = 5


def _stars(n: int) -> str:
    n = max(0, min(n, _MAX_STARS))
    return _STAR * n + _EMPTY * (_MAX_STARS - n)


def _gate(res: dict, ev) -> tuple[bool, str]:
    """Returns (passes, reason). Gate = direction set + stars>=2 + ev not None + not against."""
    d = res.get("direction", "neutral")
    stars = res.get("stars", 0)
    against = res.get("against", False)
    reasons = []
    if d == "neutral":     reasons.append("لا اتجاه / No direction")
    if stars < 2:          reasons.append(f"نجوم < 2 / Stars < 2 ({stars})")
    if ev is None:         reasons.append("لا دليل معمل / No lab evidence")
    if against:            reasons.append("إشارة عاكسة / Opposing signal")
    return (len(reasons) == 0, " · ".join(reasons))


def render_decision_desk() -> None:
    try:
        import streamlit as st
        from modules.ui_kit import strip
        from modules.i18n import L
    except Exception as exc:
        import streamlit as st
        st.error(f"مكتب القرار: خطأ — {exc}")
        return

    res = st.session_state.get("last_result") or {}

    if not res:
        st.info(L(
            "لا توجد نتيجة مسح حديثة. افتح صفحة الرادار، اختر رمزاً وشغّل المسح، "
            "ثم ارجع هنا.",
            "No recent scan result. Open Radar, pick a symbol and run a scan, "
            "then come back here."
        ))
        return

    sym  = res.get("symbol", "—")
    tf   = res.get("timeframe") or res.get("tf") or "—"
    direction = res.get("direction", "neutral")
    stars_n   = res.get("stars", 0)
    against   = res.get("against", False)

    # ── lab evidence ──────────────────────────────────────────────────────
    ev = None
    try:
        from modules.lab_tiers import evidence
        ev = evidence(res, tf)
    except Exception:
        pass

    # ── OFF warnings ──────────────────────────────────────────────────────
    off_sigs = []
    try:
        from modules.lab_tiers import off_keys
        off = off_keys()
        off_sigs = [s for s in res.get("signals", []) if s.get("key") in off]
    except Exception:
        pass

    # ── gate ──────────────────────────────────────────────────────────────
    passes, gate_reason = _gate(res, ev)
    gate_label = L("✅ يمرّ البوابة", "✅ Passes gate") if passes else L("🚫 لا يمرّ", "🚫 Blocked")
    gate_tone  = "up" if passes else "down"

    # ── strip ──────────────────────────────────────────────────────────────
    dir_ar = {"bull": "صعود 🟢", "bear": "هبوط 🔴", "neutral": "محايد ⚪"}.get(direction, direction)
    st.markdown(strip([
        (sym,                           tf,                  "",                    "",           ""),
        (L("الاتجاه", "Direction"),     L(dir_ar, direction.upper()), _stars(stars_n), "up" if direction=="bull" else "down" if direction=="bear" else "", ""),
        (L("دليل المعمل", "Lab EV"),    fmt_r(ev),           L("avgR","avgR"),       "up" if ev and ev>0 else "down" if ev and ev<0 else "", ""),
        (L("البوابة", "Gate"),          gate_label,          gate_reason[:40] if not passes else "", gate_tone, gate_reason),
    ]), unsafe_allow_html=True)

    # ── against / off warnings ─────────────────────────────────────────────
    if against:
        st.warning(L("⚠️ يوجد إشارة عاكسة — تُطبَّق عقوبة 0.10R على دليل المعمل.",
                     "⚠️ Opposing signal present — 0.10R penalty applied to lab evidence."))
    if off_sigs:
        keys = ", ".join(f"`{s.get('key')}`" for s in off_sigs[:5])
        st.warning(L(f"🚫 كاشفات خارج التقييم (OFF) موجودة لكن لا تؤثر على النجوم: {keys}",
                     f"🚫 OFF detectors present (excluded from scoring): {keys}"))

    # ── HTF confirmation ───────────────────────────────────────────────────
    htf = res.get("htf", [])
    if htf:
        st.subheader(L("تأكيد الإطار الأعلى (HTF)", "Higher Timeframe Confirmation"))
        for h in htf:
            label = h.get("tf", "")
            if not h.get("available"):
                st.markdown(f"**{label}**: {L('لا بيانات','no data')}")
            elif h.get("confirms"):
                names = ", ".join(f"{s.get('icon','')} {s.get('name','')}" for s in h["confirms"][:3])
                st.markdown(f"**{label}**: ✅ {L('يؤكد','confirms')} — {names}")
            else:
                trend = L("الترند موافق، ","trend agrees, ") if h.get("trend_aligned") else ""
                st.markdown(f"**{label}**: ➖ {trend}{L('لا إشارة هيكلية','no structure signal')}")

    # ── scenarios ──────────────────────────────────────────────────────────
    sc = []
    try:
        from modules.scorer import scenarios
        sc = scenarios(res)
    except Exception:
        pass
    if sc:
        st.subheader(L("السيناريوهات المخططة", "Pre-planned scenarios"))
        for i, s in enumerate(sc[:3], 1):
            st.markdown(f"**{i}.** {s}")

    # ── signals detail ─────────────────────────────────────────────────────
    sigs = [s for s in res.get("signals", []) if s.get("key") not in {o.get("key") for o in off_sigs}]
    if sigs:
        with st.expander(L(f"الإشارات ({len(sigs)})", f"Signals ({len(sigs)})")):
            cols = st.columns([1, 2, 1, 1])
            for c, h in zip(cols, ["", L("الاسم","Name"), L("العائلة","Family"), L("الاتجاه","Dir")]):
                c.markdown(f"**{h}**")
            for s in sigs:
                c = st.columns([1, 2, 1, 1])
                c[0].markdown(s.get("icon", ""))
                c[1].markdown(s.get("name", s.get("key", "")))
                c[2].markdown(s.get("family", ""))
                c[3].markdown("🟢" if s.get("direction") == "bull" else "🔴" if s.get("direction") == "bear" else "")

    st.caption(L(
        "البوابة: اتجاه + نجوم ≥ 2 + دليل معمل + لا إشارة عاكسة. "
        "القرار النهائي للمتداول دائماً. لا نصيحة استثمارية.",
        "Gate: direction + stars ≥ 2 + lab evidence + no opposing signal. "
        "Final decision always belongs to the trader. Not investment advice."
    ))
