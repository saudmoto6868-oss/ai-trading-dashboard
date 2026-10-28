"""Evidence summary tab (Stats page; the owner's "Decision Desk" idea, as EVIDENCE CONTEXT, not a trade decision).

For one ready setup of the last Workspace scan it puts side by side: what the scanner saw (direction, score / max, trade type, tags, plan) and what the lab says about
the setup's own detectors (average R, the same `lab_tiers.evidence` the scanner uses, with the opposing-signal penalty), plus a warning when a detector is OFF in the lab.
There is NO pass / block gate and no buy / sell advice: scanner stars were inverted in the owner's journal, and lab averages are not proof (n < 30 is "not evidence").
Input = the scan payload from main.py (`mini` = ready setups, each with the detector keys and the opposing flag).
"""
from __future__ import annotations

from modules.lab_shared import MIN_N, fmt_r, t


def lab_view(setup: dict) -> dict:
    """{ev, off, n_keys}: lab evidence of this setup's detectors on its timeframe (None = the lab has no usable number)."""
    keys = [k for k in (setup.get("keys") or []) if k]
    out = {"ev": None, "off": [], "n_keys": len(keys)}
    try:
        from modules.lab_tiers import LAB_TF, evidence, off_keys
        tf = str(setup.get("tfk") or "").lower()
        res = {"signals": [{"key": k} for k in keys], "against": bool(setup.get("against"))}
        out["ev"] = evidence(res, LAB_TF.get(tf, tf)) if keys else None
        off = off_keys()
        out["off"] = [k for k in keys if k in off]
    except Exception:
        pass
    return out


def label(setup: dict) -> str:
    d = {"bullish": "▲", "bearish": "▼"}.get(str(setup.get("direction")), "·")
    return f"{setup.get('symbol', '?')} · {setup.get('tfk', '?')} · {d} · {setup.get('score', 0)}/{setup.get('max', 0)}"


def render_decision_desk(payload: dict | None = None) -> None:
    import streamlit as st
    from modules.ui_kit import strip

    ready = [s for s in ((payload or {}).get("mini") or []) if isinstance(s, dict)]
    if not ready:
        st.info(t("مفيش Setup جاهز في آخر مسح. المسح بيشتغل في الخلفية بعد فتح التطبيق؛ ارجع بعد شوية.",
                  "No ready setup in the last scan. The scan runs in the background after the app starts; come back in a minute."))
        return
    pick = st.selectbox(t("الـSetup", "Setup"), range(len(ready)), format_func=lambda i: label(ready[i]), key="evsum_pick")
    s = ready[pick]
    lv = lab_view(s)
    ev = lv["ev"]
    lab_txt = fmt_r(ev) if ev is not None else t("مفيش رقم", "no number")
    state = (t("لا يوجد دليل معمل", "no lab number") if ev is None else t("avgR المعمل موجب (غير مثبت)", "lab avgR above 0 (not proven)") if ev > 0
             else t("avgR المعمل سالب أو صفر", "lab avgR at or below 0"))
    st.markdown(strip([
        (str(s.get("symbol", "—")), str(s.get("tfk", "—")), str(s.get("ttype") or ""), "", ""),
        (t("الاتجاه", "Direction"), {"bullish": t("شراء ▲", "Long ▲"), "bearish": t("بيع ▼", "Short ▼")}.get(str(s.get("direction")), "—"),
         f"{s.get('score', 0)}/{s.get('max', 0)}", "up" if s.get("direction") == "bullish" else "down" if s.get("direction") == "bearish" else "", t("نتيجة الماسح (مش دليل)", "scanner score (not evidence)")),
        (t("دليل المعمل", "Lab evidence"), lab_txt, state, "up" if ev and ev > 0 else "down" if ev is not None and ev <= 0 else "", t("متوسط R للكاشفات في المعمل", "average lab R of the detectors")),
        (t("كاشفات", "Detectors"), str(lv["n_keys"]), t("منها OFF: ", "OFF: ") + str(len(lv["off"])), "down" if lv["off"] else "", "")]), unsafe_allow_html=True)
    if s.get("against"):
        st.warning(t(f"فيه إشارة عاكسة: بتخصم 0.10R من دليل المعمل.", "An opposing signal is present: 0.10R is subtracted from the lab evidence."))
    if lv["off"]:
        st.warning(t("كاشفات خارج التقييم (OFF) في المعمل: ", "Detectors that are OFF in the lab: ") + ", ".join(f"`{k}`" for k in lv["off"][:6]))
    plan = s.get("plan") or {}
    if isinstance(plan, dict) and plan:
        st.subheader(t("خطة الماسح", "Scanner plan"))
        st.dataframe([{t("البند", "Item"): k, t("القيمة", "Value"): str(v)} for k, v in plan.items()], use_container_width=True, hide_index=True)
    tags = s.get("tags") if t("a", "b") == "a" else (s.get("tags_en") or s.get("tags"))
    if tags:
        st.markdown(t("**الوسوم:** ", "**Tags:** ") + " · ".join(str(x) for x in tags[:12]))
    st.caption(t(f"ده ملخص أدلة مش قرار تداول ولا نصيحة. أقل من {MIN_N} صفقة في المعمل = مش دليل، والمتوسطات الموجبة مع اختبارات كتير جزء منها صدفة. القرار للمتداول، وماحدش بينفذ أوامر تلقائي.",
                 f"An evidence summary, not a trade decision and not advice. Fewer than {MIN_N} lab trades = not evidence, and positive averages across many tests are partly chance. The decision stays with the trader; no automatic orders."))
