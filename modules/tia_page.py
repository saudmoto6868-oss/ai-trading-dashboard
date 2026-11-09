"""TIA — Trade Intelligence Agency terminal."""
from __future__ import annotations
import streamlit as st

GOLD = "#D6AD62"

def _header():
    st.markdown("""<style>
    .tia-hero{background:linear-gradient(115deg,#090909,#17130d 62%,#241a0c);border:1px solid #594522;border-radius:16px;padding:22px 24px;margin:4px 0 16px}
    .tia-kicker{color:#c9a45e;font-size:11px;letter-spacing:3px;font-weight:700}
    .tia-title{color:#f0d9a6;font-size:30px;font-weight:750;letter-spacing:5px;margin:4px 0}
    .tia-sub{color:#bdb19b;font-size:12px;letter-spacing:1.4px}
    .tia-card{background:#11100e;border:1px solid #3c3222;border-radius:12px;padding:14px 15px;min-height:85px}
    .tia-card h4{color:#e4c27e;font-size:14px;margin:0 0 7px}
    .tia-card p{color:#b8b0a1;font-size:12px;margin:0;line-height:1.55}
    </style><div class="tia-hero"><div class="tia-kicker">6868 · PARENT COMPANY</div><div class="tia-title">TIA</div><div class="tia-sub">TRADE INTELLIGENCE AGENCY · RESEARCH · INTELLIGENCE · DECISION</div></div>""", unsafe_allow_html=True)

def _card(title, body):
    st.markdown(f'<div class="tia-card"><h4>{title}</h4><p>{body}</p></div>', unsafe_allow_html=True)

def _overview():
    st.subheader("Intelligence Command Center")
    st.caption("Institution-level view. Live values appear only when a verified source is connected.")
    cols=st.columns(4)
    for col,label,value,help_text in [(cols[0],"Markets monitored","—","Existing Radar universe"),(cols[1],"Qualified opportunities","—","Evidence required"),(cols[2],"Active research tracks","7","Seven coordinated functions"),(cols[3],"Portfolio risk","—","Verified portfolio data required")]:
        col.metric(label,value,help=help_text)
    st.info("TIA is an institutional layer. XPIX, Radar, Technical Office and Workspace remain authoritative source systems.")
    a,b,c=st.columns(3)
    with a:
        _card("Market Intelligence","Macro events, news catalysts, sessions and cross-asset context.")
        _card("Technical Intelligence","Price Action, SMC/ICT, Gann, Elliott and multi-timeframe structure.")
    with b:
        _card("Order Flow & Liquidity","Footprint, Delta, DOM, Time & Sales where feeds permit.")
        _card("Strategy & Innovation Lab","Research, strategy discovery and indicator development.")
    with c:
        _card("Quant Validation & Risk","Backtests, out-of-sample checks, costs and portfolio risk.")
        _card("Trade Review & Decision","Challenge, ranking, trade plans and human-approved decisions.")

def _geometry():
    st.subheader("Geometric Intelligence")
    for title,body in [
        ("Radial Geometry","Central asset with measured relationships to DXY, yields, metals, indices and catalysts."),
        ("Network Connections","Nodes represent assets, events, strategies or liquidity zones; edges require measured or traceable relationships."),
        ("Circular Data Systems","Separate rings for strength, sessions, exposure and risk; every ring has units and source."),
        ("Polygonal Structures","Multi-factor confluence and liquidity geometry; never imply a signal from shape alone."),
        ("Dynamic Grids","Heatmaps for correlation, volatility, sessions, liquidity and strategy performance.")]:
        _card(title,body)
    st.write("Gold-first palette: charcoal/black, champagne, brass and warm gold. Orange/amber is restrained. Motion may use particle assembly, radial expansion, node pulses and grid illumination, but must never distort the locked approved TIA logo.")

def _market():
    st.subheader("Trading Interface")
    view=st.segmented_control("Trading modules",["Candlestick & Structure","Volume & Order Flow","Heatmaps","Portfolio Analytics"],default="Candlestick & Structure",key="tia_market_module",label_visibility="collapsed")
    details={
      "Candlestick & Structure":"Reuse the existing chart engine. Planned overlays: BOS/CHoCH, swings, FVG/IFVG, order blocks, liquidity sweeps, sessions and HTF levels.",
      "Volume & Order Flow":"Volume, Delta, Footprint, DOM and Time & Sales. Separate executed trades from resting liquidity and derived estimates.",
      "Heatmaps":"Liquidity, volume, correlation, volatility, sessions and strategy performance. Every view declares source, timestamp, unit and coverage.",
      "Portfolio Analytics":"Exposure, correlation clusters, expectancy, profit factor, drawdown, R-multiples and funded-account limits."}
    st.write(details.get(view,""))
    st.info("No synthetic live values. Existing XPIX modules remain authoritative until integrations are reviewed and tested.")

def _agents():
    st.subheader("Seven specialist functions")
    for name,detail in [
      ("01 · Intelligence Director","Orchestration, priorities, evidence standards and final synthesis."),
      ("02 · Market Intelligence","Macro, news, geopolitics, catalysts, sessions and cross-asset context."),
      ("03 · Technical Intelligence","Price Action, SMC/ICT, Elliott, Gann and multi-timeframe structure."),
      ("04 · Order Flow & Liquidity","Footprint, Delta, DOM, Time & Sales and liquidity evidence."),
      ("05 · Strategy & Innovation Lab","Research, strategy discovery, indicator development and experiments."),
      ("06 · Quant Validation & Risk","Backtesting, walk-forward, costs, validation and portfolio risk."),
      ("07 · Trade Review & Decision","Challenge, ranking, trade plans and post-trade learning.")]:
        _card(name,detail)
    st.warning("Seven organizational responsibilities, not a requirement for seven isolated model instances.")

def render_tia():
    _header()
    selected=st.segmented_control("TIA sections",["Command Center","Geometric Intelligence","Trading Interface","Seven Agents","Roadmap"],default="Command Center",key="tia_section",label_visibility="collapsed")
    if selected=="Command Center": _overview()
    elif selected=="Geometric Intelligence": _geometry()
    elif selected=="Trading Interface": _market()
    elif selected=="Seven Agents": _agents()
    else:
        st.subheader("TIA implementation roadmap")
        for i,step in enumerate(["Lock approved brand asset and charter.","Preserve navigation and existing page IDs.","Define source/time/unit/coverage data contracts.","Build five geometry systems.","Integrate chart, order-flow, heatmap and portfolio modules.","Add orchestration and decision trail.","Validate tests and desktop/mobile rendering."],1):
            st.markdown(f"**{i}.** {step}")
        st.caption("No merge, deployment or live order execution is performed by this branch.")
