"""الماسح والتدوير — Rotation & Scanner tab.

Shows signal distribution across asset classes using already-computed
scan results stored in st.session_state["scan_results"] (set by the
Radar / Scanner page on each run).

Why session_state only (no live fetch here):
  - This tab runs inside Stats page; triggering fresh candle downloads
    would double the CPU cost and get the app throttled on Streamlit Cloud.
  - The Radar page already scans and caches results; we just summarise them.
  - If no scan results exist yet, we show a clear prompt.

Output:
  - Strip: total signals / classes with signals / top class / avg lab score
  - Bar chart (st.bar_chart) of signal count per asset class
  - Table: per-class breakdown — count, avg lab evidence score, top detector

Usage:
    from modules.rotation_scan import render_rotation_scan
    render_rotation_scan()
"""
from __future__ import annotations
from modules.lab_shared import load_rows, MIN_N, fmt_r

# asset class order for display
_CLASS_ORDER = ["Crypto", "Indices", "Metals", "Oil & Gas", "Forex",
                "Stocks", "Bonds", "Options", "Meme coins"]


def _class_of(sym: str) -> str:
    """Best-effort class from symbol prefix; no external call."""
    s = sym.upper()
    if s.startswith("HL:"):
        seg = s.split(":")[1] if ":" in s[3:] else ""
        _hl_map = {
            "xau": "Metals", "xag": "Metals", "oil": "Oil & Gas",
            "spx": "Indices", "ndx": "Indices", "eurusd": "Forex",
            "gbpusd": "Forex", "usdjpy": "Forex",
        }
        return _hl_map.get(seg.lower(), "Stocks")
    if s.startswith("Y:"):
        return "Stocks"
    if s.startswith("FH:"):
        return "Forex"
    # OKX crypto default
    return "Crypto"


def _lab_ev_map() -> dict[str, float]:
    """key → avgR from lab (side==all, tf==all, n>=MIN_N). Cached per process."""
    global _EV_CACHE
    if _EV_CACHE:
        return _EV_CACHE
    _EV_CACHE = {r["key"]: r["avgR"] for r in load_rows("all")
                 if r.get("tf") == "all" and r.get("n", 0) >= MIN_N}
    return _EV_CACHE


_EV_CACHE: dict[str, float] = {}


def _signal_ev(signal: dict) -> float | None:
    m = _lab_ev_map()
    return m.get(signal.get("key"))


def _summarise(results: list[dict]) -> dict[str, dict]:
    """Return {class: {count, ev_vals, top_key}} from scan results."""
    buckets: dict[str, dict] = {}
    for r in results:
        sym = r.get("symbol", "")
        cls = r.get("asset_class") or _class_of(sym)
        if cls not in buckets:
            buckets[cls] = {"count": 0, "ev_vals": [], "keys": {}}
        buckets[cls]["count"] += len(r.get("signals", []))
        for s in r.get("signals", []):
            ev = _signal_ev(s)
            if ev is not None:
                buckets[cls]["ev_vals"].append(ev)
            k = s.get("key", "")
            if k:
                buckets[cls]["keys"][k] = buckets[cls]["keys"].get(k, 0) + 1
    return buckets


# ── public render ─────────────────────────────────────────────────────────────
def render_rotation_scan() -> None:
    try:
        import streamlit as st
        from modules.ui_kit import strip
        from modules.i18n import L
    except Exception as exc:
        import streamlit as st
        st.error(f"الماسح والتدوير: خطأ — {exc}")
        return

    # pull cached scan results
    results = st.session_state.get("scan_results") or []

    if not results:
        st.info(L(
            "لا توجد نتائج مسح بعد. افتح صفحة الرادار (Radar) وشغّل المسح أولاً، "
            "ثم ارجع هنا لترى توزيع الإشارات.",
            "No scan results yet. Open the Radar page and run a scan first, "
            "then come back here to see the signal distribution."
        ))
        return

    buckets = _summarise(results)
    if not buckets:
        st.info(L("المسح لا يحتوي على إشارات.", "Scan contains no signals."))
        return

    total_sigs = sum(b["count"] for b in buckets.values())
    classes_with = len([b for b in buckets.values() if b["count"] > 0])
    top_cls = max(buckets, key=lambda c: buckets[c]["count"])
    all_ev = [v for b in buckets.values() for v in b["ev_vals"]]
    avg_ev = round(sum(all_ev) / len(all_ev), 3) if all_ev else None

    # ── strip ──────────────────────────────────────────────────────────────
    st.markdown(strip([
        (L("الإشارات", "Signals"),      str(total_sigs),       L("إجمالي","total"),         "", ""),
        (L("الفئات النشطة","Active classes"), str(classes_with), L("من","of") + f" {len(_CLASS_ORDER)}", "", ""),
        (L("أعلى فئة","Top class"),     top_cls,                str(buckets[top_cls]["count"]) + " " + L("إشارة","sigs"), "up", ""),
        (L("متوسط دليل المعمل","Avg lab EV"), fmt_r(avg_ev),   L("عبر الفئات","across classes"), "up" if avg_ev and avg_ev > 0 else "down" if avg_ev and avg_ev < 0 else "", ""),
    ]), unsafe_allow_html=True)

    # ── bar chart ──────────────────────────────────────────────────────────
    ordered = [(c, buckets[c]["count"]) for c in _CLASS_ORDER if c in buckets]
    ordered += [(c, buckets[c]["count"]) for c in buckets if c not in _CLASS_ORDER]
    if ordered:
        import pandas as _pd
        df_chart = _pd.DataFrame(ordered, columns=["class", "signals"]).set_index("class")
        st.bar_chart(df_chart)

    # ── table ──────────────────────────────────────────────────────────────
    st.subheader(L("تفصيل حسب الفئة", "Breakdown by asset class"))
    cols = st.columns([2, 1, 1, 2])
    for c, h in zip(cols, [L("الفئة","Class"), L("إشارات","Signals"),
                            L("متوسط دليل","Avg EV"), L("أكثر كاشف","Top detector")]):
        c.markdown(f"**{h}**")

    for cls, b in sorted(buckets.items(), key=lambda x: -x[1]["count"]):
        ev_vals = b["ev_vals"]
        avg = round(sum(ev_vals) / len(ev_vals), 3) if ev_vals else None
        top_k = max(b["keys"], key=b["keys"].get) if b["keys"] else "—"
        c = st.columns([2, 1, 1, 2])
        c[0].markdown(L(cls, cls))
        c[1].markdown(str(b["count"]))
        c[2].markdown(fmt_r(avg))
        c[3].markdown(f"`{top_k}`")

    st.caption(L(
        "الإشارات من آخر مسح للرادار. متوسط دليل المعمل = avgR من strategy_lab.json (n≥30، tf=all). "
        "لا أرقام مُخترعة.",
        "Signals from last Radar scan. Avg lab EV = avgR from strategy_lab.json (n≥30, tf=all). "
        "No invented numbers."
    ))
