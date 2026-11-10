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
    # owner 2026-11-10: market | symbol | Run live ON the workspace toolbar row (right of + Widget): the row is pulled down over the iframe's empty toolbar area;
    # the spacer column and the row itself let clicks through, so the + Widget buttons underneath keep working.
    # !important everywhere: the global theme CSS of main.py sets selectbox / button sizes with higher weight (the first attempt kept the old size)
    st.markdown("<style>.st-key-tia_row{position:relative;z-index:50;margin:0 0 -34px!important;padding:0!important;pointer-events:none;height:26px!important;min-height:0!important;overflow:visible} .st-key-tia_row [data-testid='stHorizontalBlock']{gap:6px!important;align-items:flex-start!important} .st-key-tia_row [data-testid='stColumn']:not(:first-child){pointer-events:auto} .st-key-tia_row [data-testid='stColumn']:last-child{pointer-events:none} .st-key-tia_row button{white-space:nowrap!important} .st-key-tia_row [data-testid='stSelectbox']{margin:0!important;min-height:0!important} .st-key-tia_row [data-testid='stSelectbox'] label{display:none!important} .st-key-tia_row [data-baseweb='select']>div{min-height:24px!important;height:24px!important;padding-top:0!important;padding-bottom:0!important} .st-key-tia_row [data-baseweb='select'] div,.st-key-tia_row [data-baseweb='select'] span,.st-key-tia_row [data-baseweb='select'] input{font-size:10.5px!important;line-height:1.1!important} .st-key-tia_row [data-baseweb='select'] svg{width:12px!important;height:12px!important} .st-key-tia_row [data-testid='stElementContainer']{margin:0!important} .st-key-tia_row button{min-height:24px!important;height:24px!important;padding:0 8px!important;margin:0!important} .st-key-tia_row button p{font-size:10.5px!important;line-height:1!important}</style>", unsafe_allow_html=True)
    with st.container(key="tia_row"):
        c_sp, c_mkt, c_sym, c_run, c_end = st.columns([20, 7, 10, 8, 55], gap="small")   # narrow controls next to the + Widget buttons; both outer columns let clicks through
    market = c_mkt.selectbox("Market tab", CLASSES, index=0, key="tia_market_class", label_visibility="collapsed")
    catalog = symbols_for_class(market, top=60)
    symbols = catalog.get("symbols") or []
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
    if catalog.get("note"):
        st.caption(catalog["note"])   # below the workspace, so it never shifts the toolbar row
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


