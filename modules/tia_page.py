""""TIA unified market workspace and Intelligence Director UI."""
from __future__ import annotations

import streamlit as st


def render_tia():
    st.markdown("""
    <style>
    .tia-top{display:flex;align-items:center;justify-content:space-between;gap:10px;
      background:linear-gradient(100deg,#090b0e,#17140e 72%,#211a0d);
      border:1px solid #51432c;border-radius:9px;padding:7px 12px;margin:0 0 7px}
    .tia-k{font-size:8px;letter-spacing:1.5px;color:#c6a35e;font-weight:700}
    .tia-h{font-size:16px;letter-spacing:1.8px;color:#f3dfb5;font-weight:800;line-height:1.2}
    .tia-s{font-size:8px;letter-spacing:.5px;color:#a99d89}
    div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"]{font-size:10px!important;margin-bottom:1px!important}
    div[data-testid="stSelectbox"] [data-baseweb="select"]>div{min-height:31px!important;font-size:11px!important}
    div[data-testid="stSelectbox"] [data-baseweb="select"] input{font-size:11px!important}
    div[data-testid="stButton"] button{min-height:31px!important;height:31px!important;
      padding:0 8px!important;font-size:10px!important;white-space:nowrap}
    div[data-testid="stVerticalBlock"]{gap:.25rem!important}
    .tia-report{border:1px solid #51432c;background:#11110f;border-radius:8px;padding:8px 10px;margin:4px 0}
    div[data-baseweb="popover"] li{font-size:11px!important;min-height:26px!important}
    div[data-baseweb="popover"] ul{max-height:260px!important}
    @media(max-width:700px){
      .tia-top{padding:6px 8px}.tia-h{font-size:13px;letter-spacing:1px}
      .tia-s{display:none}
      div[data-testid="stSelectbox"] [data-baseweb="select"]>div{font-size:10px!important}
    }
    </style>
    <div class="tia-top">
      <div><div class="tia-k">TRADE INTELLIGENCE AGENCY · 6868</div>
      <div class="tia-h">TIA COMMAND WORKSPACE</div></div>
      <div class="tia-s">UNIFIED MARKETS · LIVE EVIDENCE · HUMAN CONTROL</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("إدارة فريق الوكلاء والتعليمات", expanded=False):
        from modules.tia_agent_admin import render_agent_admin
        render_agent_admin()

    from modules.asset_classes import CLASSES
    from modules.tia_intelligence import symbols_for_class, director_report

    st.markdown('<div class="tia-tools">', unsafe_allow_html=True)
    market_col, symbol_col, run_col = st.columns([0.85, 1.35, 0.62], vertical_alignment="bottom", gap="small")
    with market_col:
        market = st.selectbox("السوق", CLASSES, index=0, key="tia_market_class")
    catalog = symbols_for_class(market, top=60)
    symbols = catalog.get("symbols") or []
    with symbol_col:
        if symbols:
            selected = st.selectbox("الرمز", symbols, key=f"tia_symbol_{market}")
        else:
            selected = None
            st.selectbox("الرمز", ["لا توجد رموز متاحة"], disabled=True, key=f"tia_symbol_empty_{market}")
    with run_col:
        run = st.button("TIA Director", type="primary", use_container_width=True, disabled=not bool(symbols))
    st.markdown('</div>', unsafe_allow_html=True)

    if catalog.get("note"):
        st.caption(catalog["note"])
    if not symbols:
        st.warning("لا توجد رموز موثوقة متاحة لهذا السوق حالياً؛ لن نعرض أسعاراً افتراضية.")
    else:
        key = f"tia_director_{market}_{selected}"
        if run:
            with st.spinner("يجمع TIA الأدلة المتاحة ويراجع توافق المصادر…"):
                st.session_state[key] = director_report(selected, market)
        report = st.session_state.get(key)
        if report:
            with st.container(border=True):
                stance = report.get("stance", "UNAVAILABLE")
                st.markdown(f"**{selected} · TIA Director · {stance}**")
                st.caption(report.get("director_summary", ""))
                technical = report.get("technical") or {}
                if technical:
                    cols = st.columns(max(1, min(4, len(technical))))
                    for col, (tf, item) in zip(cols, technical.items()):
                        with col:
                            if item.get("status") == "ok":
                                st.metric(tf.upper(), item.get("trend", "—"),
                                          f"RSI {item.get('rsi14', '—')} · {item.get('return20_pct', '—')}%")
                            else:
                                st.metric(tf.upper(), "UNAVAILABLE")
                src = report.get("sources") or {}
                st.caption("المصادر: " + " · ".join(f"{k}: {v.get('status')}" for k, v in src.items()))
                for warning in report.get("warnings", []):
                    st.warning(warning)
                vk = report.get("visual_knowledge") or {}
                vks = vk.get("summary") or {}
                st.markdown("**Image-derived playbook · مرجع تعليمي غير معتمد كإشارة**")
                st.caption(f"{vks.get('module_count', 0)} وحدات معرفية · {vks.get('pattern_count', 0)} نمط مستخرج · لا توجد إشارة تلقائية من الصور")
                with st.expander("قواعد Price Action والشموع وVolume Profile وOrder Flow"):
                    for mid, state in (vk.get("modules") or {}).items():
                        st.markdown(f"**{mid}** · {state.get('status', 'unknown')}")
                        st.caption(state.get("reason", ""))
                    st.markdown("**تسلسل التقييم المقترح**")
                    for step in vk.get("workflow", []):
                        st.write("• " + step)
                with st.expander("تفاصيل الأدلة ومصادر البيانات"):
                    st.json({"sources": src, "technical": technical, "flow": report.get("flow"),
                             "options": report.get("options")})
                st.caption("تحليل بحثي فقط؛ لا ينفذ أوامر تداول.")
    
    st.markdown("### TIA Market Workspace")
    st.caption("اختر السوق والرمز من الشريط المختصر أعلاه؛ أدوات الشارت والتدفق تظل داخل مساحة العمل.")
    from modules.tia_workspace import render_tia_workspace
    render_tia_workspace(height=1040, universe=market, symbols=symbols or None)
