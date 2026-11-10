"""V7 research page (PAGE 18, Lab hub): READ-ONLY view of data/v7 (sources + claims from the CFX v7 research).

Owner 2026-11-10. Acceptance conditions: docs/V7_NEXT_STEP_REPLY_2026-11-10.md. It shows what exists and its status; it never shows a signal,
an entry / stop / target, or an order control. Data: data/v7/sources.json + claims.json only; a missing or malformed file is reported, no placeholder rows."""
from __future__ import annotations
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "v7")
PROJECT_FACT = {"project-setting", "process", "project-fact"}   # what OUR project does / the owner asked: not a market claim
OWN_RESEARCH = {"backtest"}                                      # figures from our own pipeline: research, never evidence by themselves


def load(folder: str = DATA) -> dict:
    """-> {"sources": [...], "claims": [...], "error": ""}. Any problem gives an error string and EMPTY lists (nothing is invented)."""
    out = {"sources": [], "claims": [], "error": ""}
    try:
        with open(os.path.join(folder, "sources.json"), encoding="utf-8") as f:
            S = json.load(f)
        with open(os.path.join(folder, "claims.json"), encoding="utf-8") as f:
            C = json.load(f)
        if not (isinstance(S, list) and isinstance(C, list)):
            raise ValueError("sources.json and claims.json must be lists")
        ids = {s["id"] for s in S}
        for c in C:
            for k in ("id", "source_id", "claim", "status", "confidence", "category", "timestamp_or_locator"):
                if k not in c:
                    raise ValueError(f"claim {c.get('id', '?')} lacks '{k}'")
            if c["source_id"] not in ids:
                raise ValueError(f"claim {c['id']} points to an unknown source")
        out["sources"], out["claims"] = S, C
    except Exception as e:   # noqa: BLE001 - shown to the user, never swallowed silently
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def kind(claim: dict) -> str:
    c = claim.get("category")
    return "project" if c in PROJECT_FACT else "own" if c in OWN_RESEARCH else "market"


def summarize(d: dict) -> dict:
    C = d["claims"]
    k = [kind(c) for c in C]
    market = [c for c, x in zip(C, k) if x == "market"]
    measured = [c for c in market if c.get("status") == "measured"]
    dates = sorted(s.get("fetched", "") for s in d["sources"] if s.get("fetched"))
    return {"sources": len(d["sources"]), "claims": len(C), "market": len(market), "project": k.count("project"), "own": k.count("own"),
            "measured": len(measured), "pct_tested": round(100 * len(measured) / len(market), 1) if market else 0.0,
            "from": dates[0] if dates else "", "to": dates[-1] if dates else ""}


DASH = os.path.join(ROOT, "research", "cfx", "dashboard")
_LIB_TAG = '<script src="vendor/lightweight-charts.standalone.production.js"></script>'
_DATA_TAG = '<script src="data.js"></script>'


def dashboard_html(base: str = DASH) -> tuple:
    """-> (html, error). The CFX research dashboard with its two script files inlined, so it runs inside one iframe. Any problem -> ("", reason)."""
    try:
        with open(os.path.join(base, "index.html"), encoding="utf-8") as f:
            html = f.read()
        with open(os.path.join(base, "vendor", "lightweight-charts.standalone.production.js"), encoding="utf-8") as f:
            lib = f.read()
        with open(os.path.join(base, "data.js"), encoding="utf-8") as f:
            data = f.read()
        if _LIB_TAG not in html or _DATA_TAG not in html:
            raise ValueError("index.html no longer references the two expected script files")
        safe = lambda s: s.replace("</script", "<\\/script")
        return html.replace(_LIB_TAG, "<script>" + safe(lib) + "</script>").replace(_DATA_TAG, "<script>" + safe(data) + "</script>"), ""
    except Exception as e:   # noqa: BLE001
        return "", f"{type(e).__name__}: {e}"


def _read(rel: str) -> str:
    try:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return f.read()
    except Exception:   # noqa: BLE001
        return ""


def render() -> None:
    import streamlit as st
    import streamlit.components.v1 as components
    st.subheader("V7 research (CFX v7 single-oscillator chart)")
    st.caption("Research intake, read-only: nothing here is a recommendation or an order. Every claim is `unverified` until it is measured with its sample size; "
               "under 30 cases it is not evidence.")
    view = st.radio("View", ["Dashboard", "Chart images", "Rules", "Claims & evidence"], horizontal=True, key="v7_view", label_visibility="collapsed")
    if view == "Dashboard":
        st.warning("Research snapshot of the CFX v7 chart on GC=F gold FUTURES (not spot XAUUSD), window 6-10 Nov 2026. The dots and alerts are the research rule 'variant B' "
                   "(62 signals on the longer sample, 59.7% against the next 8 bars, p about 0.13): NOT an edge, NOT a recommendation, no orders. Time axis: Cairo.")
        html, err = dashboard_html()
        if err:
            st.error(f"The dashboard files could not be loaded: {err}")
        else:
            components.html(html, height=900, scrolling=True)
        return
    if view == "Chart images":
        for rel, cap in (("research/cfx/cfx_chart_real_v7.png", "Chart: price + SMA 144 / 77 + SMC/ICT overlays + session boxes"),
                         ("research/cfx/cfx_osc_v7.png", "Single oscillator pane: Stochastic 5,3,3 + RSI 14 + MACD 12,26,1"),
                         ("research/cfx/cfx_settings_v7.png", "Indicator settings")):
            p = os.path.join(ROOT, rel)
            if os.path.exists(p):
                st.image(p, caption=cap, use_container_width=True)
            else:
                st.info(f"{rel} is not in this deployment.")
        return
    if view == "Rules":
        txt = _read("research/cfx/README.md")
        st.markdown(txt) if txt else st.info("research/cfx/README.md is not in this deployment.")
        return
    d = load()
    if d["error"]:
        st.error(f"data/v7 could not be read: {d['error']}. Nothing is shown instead of guessing.")
        return
    s = summarize(d)
    a, b, c, e = st.columns(4)
    a.metric("Sources", s["sources"])
    b.metric("Market claims", s["market"])
    c.metric("Measured so far", f"{s['measured']} ({s['pct_tested']}%)")
    e.metric("Fetched", f"{s['from']} .. {s['to']}")
    st.caption(f"Also in the file: {s['project']} project facts (what our project does / the owner asked) and {s['own']} figures from our own pipeline. "
               "They are listed separately below and are not counted as tested market claims.")
    src = {x["id"]: x for x in d["sources"]}

    def rows(sel):
        return [{"id": q["id"], "claim": q["claim"], "source": src[q["source_id"]].get("title", q["source_id"]), "where": q["timestamp_or_locator"],
                 "confidence": q["confidence"], "status": q["status"], "testable": q.get("testable"), "how to test": q.get("how_to_test", "")} for q in sel]

    market = [q for q in d["claims"] if kind(q) == "market"]
    cats = sorted({q["category"] for q in market})
    pick = st.multiselect("Category", cats, default=cats)
    st.markdown("### Market claims (what outside sources say)")
    st.dataframe(rows([q for q in market if q["category"] in pick]), use_container_width=True, hide_index=True)
    st.markdown("### Our own pipeline figures (research, not evidence)")
    st.warning("Oscillator variant B: 62 signals on one Sep-Nov sample, 37 against the next-8-bar move / 25 with it (59.7% against). "
               "Two-sided binomial test against 50%: p is about 0.13, so it supports neither 'works' nor 'works inverted'. "
               "The variant was picked after trying three on the same sample. Not an edge.")
    st.dataframe(rows([q for q in d["claims"] if kind(q) == "own"]), use_container_width=True, hide_index=True)
    with st.expander("Project facts (not market claims)"):
        st.dataframe(rows([q for q in d["claims"] if kind(q) == "project"]), use_container_width=True, hide_index=True)
    with st.expander("Sources"):
        st.dataframe([{"id": x["id"], "title": x["title"], "type": x["type"], "published": x.get("published"), "fetched": x.get("fetched"), "url": x["url"]}
                      for x in d["sources"]], use_container_width=True, hide_index=True)
    st.caption("Review and conditions for the next step: docs/V7_CLAUDE_REVIEW_2026-11-10.md and docs/V7_NEXT_STEP_REPLY_2026-11-10.md. Not tested in a browser.")
