"""TIA unified market workspace and Intelligence Director UI."""
from __future__ import annotations
import streamlit as st


def render_tia():
    st.markdown("""
    <style>
    .tia-top{background:linear-gradient(110deg,#080a0d,#17140e 68%,#2a1e0b);border:1px solid #66502a;border-radius:15px;padding:15px 20px;margin:0 0 10px}
    .tia-k{font-size:10px;letter-spacing:3px;color:#c6a35e;font-weight:700}
    .tia-h{font-size:27px;letter-spacing:5px;color:#f3dfb5;font-weight:800}
    .tia-s{font-size:11px;letter-spacing:1.5px;color:#b9ad96}
    </style>
    <div class="tia-top"><div class="tia-k">TRADE INTELLIGENCE AGENCY · 6868</div>
    <div class="tia-h">TIA COMMAND WORKSPACE</div>
    <div class="tia-s">UNIFIED MARKETS · MULTI-SOURCE INTELLIGENCE · HUMAN-CONTROLLED DECISIONS</div></div>
    """,unsafe_allow_html=True)

    from modules.asset_classes import CLASSES
    from modules.tia_intelligence import symbols_for_class, director_report
    st.markdown("<style>.st-key-tia_row{margin:-6px 0 -10px} .st-key-tia_row [data-testid='stSelectbox'] label{display:none} .st-key-tia_row [data-baseweb='select']>div{min-height:30px} .st-key-tia_row button{min-height:30px;padding:0 10px}</style>", unsafe_allow_html=True)
    with st.container(key="tia_row"):   # owner 2026-11-10: one thin row (market | symbol | Run) so the workspace starts right under the top bar
        c_mkt, c_sym, c_run = st.columns([1, 2, 1], gap="small")
    market = c_mkt.selectbox("Market tab", CLASSES, index=0, key="tia_market_class", label_visibility="collapsed")
    catalog = symbols_for_class(market, top=60)
    symbols = catalog.get("symbols") or []
    if catalog.get("note"):
        st.caption(catalog["note"])
    if not symbols:
        st.warning("No verified symbols are currently available for this tab. No placeholder prices will be shown.")
        return

    selected = c_sym.selectbox("Symbol / instrument", symbols, key=f"tia_symbol_{market}", label_visibility="collapsed")
    run = c_run.button("Run TIA Director", type="primary", use_container_width=True)
    key = f"tia_director_{market}_{selected}"
    if run:
        with st.spinner("Collecting available market evidence and reconciling sources…"):
            st.session_state[key] = director_report(selected, market)
    from modules.tia_workspace import render_tia_workspace
    render_tia_workspace(height=900, universe=market, symbols=[selected] + [s for s in symbols if s != selected])   # right under the row; the Director report (if any) is listed BELOW it
    report = st.session_state.get(key)
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


