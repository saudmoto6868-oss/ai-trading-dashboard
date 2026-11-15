"""TIA unified market workspace and Intelligence Director UI.

Owner 2026-11-10: the market / symbol / Run Director controls are NOT Streamlit widgets any more (CSS could not shrink them): they live inside the
workspace toolbar (modules/tia_workspace.py) and talk to this page through URL parameters tia_mkt / tia_sym / tia_run.
"""
from __future__ import annotations
import streamlit as st


def render_tia():
    from modules.asset_classes import CLASSES
    from modules.tia_intelligence import symbols_for_class, director_report
    qp = st.query_params
    market = qp.get("tia_mkt") if qp.get("tia_mkt") in CLASSES else CLASSES[0]
    catalog = symbols_for_class(market, top=60)
    symbols = catalog.get("symbols") or []
    if not symbols:
        st.warning("No verified symbols are currently available for this tab. No placeholder prices will be shown.")
        return
    selected = qp.get("tia_sym") if qp.get("tia_sym") in symbols else symbols[0]
    key = f"tia_director_{market}_{selected}"
    if qp.get("tia_run"):
        with st.spinner("Collecting available market evidence and reconciling sources…"):
            st.session_state[key] = director_report(selected, market)
        try:
            del st.query_params["tia_run"]   # a reload must not run the Director again
        except Exception:
            pass
    report = st.session_state.get(key)

    ctrl = {"markets": list(CLASSES), "market": market, "symbols": list(symbols), "selected": selected,
            "agents": {"ran": bool(report), "stance": (report or {}).get("stance"),
                          "sources": {k: (v or {}).get("status") for k, v in ((report or {}).get("sources") or {}).items()},
                          "tech": {k: {"status": (v or {}).get("status"), "trend": (v or {}).get("trend")} for k, v in ((report or {}).get("technical") or {}).items()},
                          "warnings": [str(w)[:140] for w in ((report or {}).get("warnings") or [])[:6]]}}
    from modules.tia_workspace import render_tia_workspace
    render_tia_workspace(height=900, universe=market, symbols=[selected] + [s for s in symbols if s != selected], ctrl=ctrl)
    if catalog.get("note"):
        st.caption(catalog["note"])

    if report:
        st.markdown("### TIA Intelligence Director")
        stance = report.get("stance", "UNAVAILABLE")
        st.subheader(stance)
        st.write(report.get("director_summary", ""))
        technical = report.get("technical") or {}
        cols = st.columns(max(1, min(4, len(technical))))
        for col, (tf, item) in zip(cols, technical.items()):
            with col:
                if item.get("status") == "ok":
                    st.metric(tf.upper(), item.get("trend", "—"), f"RSI {item.get('rsi14', '—')} · {item.get('return20_pct', '—')}% / 20 bars")
                else:
                    st.metric(tf.upper(), "UNAVAILABLE")
        src = report.get("sources") or {}
        st.caption("Source coverage: " + " · ".join(f"{k}: {v.get('status')}" for k, v in src.items()))
        for warning in report.get("warnings", []):
            st.warning(warning)
        with st.expander("Evidence and provenance"):
            st.json({"sources": src, "technical": technical, "flow": report.get("flow"), "options": report.get("options")})
        st.caption("Research bias only. No order execution. Conflicting or unavailable evidence reduces confidence.")
