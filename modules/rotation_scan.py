"""Class rotation tab (Stats page): where did the last Workspace scan find setups, by asset class?

Input = the Workspace scan payload main.py already builds in the background (`scan`: symbol -> timeframe -> setup, `mini`: ready setups).
No new download and no new scan here (Streamlit Cloud throttles the CPU). It describes what the scan found, it is NOT evidence and not a forecast.
Per class: symbols with a setup, setups long / short, average score share (score / max), the biggest score.
"""
from __future__ import annotations

from modules.lab_shared import class_of, t

ORDER = ["Crypto", "Indices", "Metals", "Oil & Gas", "Forex", "Stocks", "Bonds", "Egypt (EGX)", "Saudi (Tadawul)", "Options", "Meme coins"]


def summarise(scan: dict) -> dict:
    """{class: {symbols, long, short, shares[], best:(share, symbol, tf)}} from the payload's `scan` map."""
    out: dict = {}
    for sym, tfs in (scan or {}).items():
        cls = class_of(sym)
        b = out.setdefault(cls, {"symbols": set(), "long": 0, "short": 0, "shares": [], "best": None})
        for tf, e in (tfs or {}).items():
            if not isinstance(e, dict):
                continue
            b["symbols"].add(sym)
            d = str(e.get("dir") or "")
            b["long"] += d == "bullish"
            b["short"] += d == "bearish"
            mx = e.get("max") or 0
            share = (e.get("score") or 0) / mx if mx else 0.0
            b["shares"].append(share)
            if b["best"] is None or share > b["best"][0]:
                b["best"] = (share, sym, e.get("tf") or tf)
    return out


def render_rotation_scan(payload: dict | None = None) -> None:
    import streamlit as st
    from modules.ui_kit import strip

    scan = (payload or {}).get("scan") or {}
    if not scan:
        st.info(t("مفيش نتيجة مسح جاهزة لسه. المسح بيشتغل في الخلفية بعد فتح التطبيق (أول دقيقة)؛ افتح الـWorkspace وارجع بعد شوية.",
                  "No scan result yet. The scan runs in the background after the app starts (first minute); open the Workspace and come back."))
        return
    s = summarise(scan)
    rows = [(c, s[c]) for c in ORDER if c in s] + [(c, s[c]) for c in s if c not in ORDER]
    total_sym = sum(len(b["symbols"]) for _, b in rows)
    longs, shorts = sum(b["long"] for _, b in rows), sum(b["short"] for _, b in rows)
    top = max(rows, key=lambda r: len(r[1]["symbols"]))
    st.markdown(strip([
        (t("رموز فيها Setup", "Symbols with a setup"), str(total_sym), t("آخر مسح", "last scan"), "", ""),
        (t("شراء / بيع", "Long / short"), f"{longs} / {shorts}", t("عدد الـSetups", "setups"), "", ""),
        (t("أكتر فئة", "Busiest class"), top[0], f"{len(top[1]['symbols'])} " + t("رمز", "symbols"), "", ""),
        (t("الفئات", "Classes"), str(len(rows)), t("فيها Setups", "with setups"), "", "")]), unsafe_allow_html=True)
    h = [t("الفئة", "Class"), t("رموز", "Symbols"), t("شراء", "Long"), t("بيع", "Short"), t("متوسط النتيجة %", "Avg score %"), t("أعلى رمز", "Top symbol")]
    st.dataframe([{h[0]: c, h[1]: len(b["symbols"]), h[2]: b["long"], h[3]: b["short"], h[4]: round(100 * sum(b["shares"]) / len(b["shares"])) if b["shares"] else None,
                   h[5]: f"{b['best'][1]} · {b['best'][2]}" if b["best"] else ""} for c, b in rows], use_container_width=True, hide_index=True)
    st.bar_chart({c: len(b["symbols"]) for c, b in rows})
    st.caption(t("ده وصف لآخر مسح (إشارات الماسح)، مش دليل ولا توقع. الفئات اللي بدون خلفية بيانات (مصر والسعودية من Yahoo بحجم صفر، والأوبشنز) غالبًا ما بتظهرش هنا.",
                 "This describes the last scan (scanner setups). It is not evidence and not a forecast. Classes without a live feed behind the scanner (Yahoo EGX / Tadawul with zero volume, options) mostly do not show up here."))
