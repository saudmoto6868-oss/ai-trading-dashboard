"""TIA — Trade Intelligence Agency terminal.

First implementation is a truthful, data-aware shell. It does not fabricate market
readings or place orders. Existing XPIX/Radar/Workspace modules remain authoritative.
"""
from __future__ import annotations

import streamlit as st


GOLD = "#D6AD62"
PALE_GOLD = "#F0D9A6"
MUTED = "#A99B80"


def _header():
    st.markdown(
        """
        <style>
        .tia-hero{background:linear-gradient(115deg,#090909 0%,#17130d 62%,#241a0c 100%);
          border:1px solid #594522;border-radius:16px;padding:22px 24px;margin:4px 0 16px}
        .tia-kicker{color:#c9a45e;font-size:11px;letter-spacing:3px;font-weight:700}
        .tia-title{color:#f0d9a6;font-size:30px;font-weight:750;letter-spacing:5px;margin:4px 0}
        .tia-sub{color:#bdb19b;font-size:12px;letter-spacing:1.4px}
        .tia-card{background:#11100e;border:1px solid #3c3222;border-radius:12px;
          padding:14px 15px;min-height:105px}
        .tia-card h4{color:#e4c27e;font-size:14px;margin:0 0 7px}
        .tia-card p{color:#b8b0a1;font-size:12px;margin:0;line-height:1.55}
        .tia-tag{display:inline-block;border:1px solid #725a31;border-radius:20px;
          color:#e1c17d;padding:3px 9px;font-size:10px;margin:3px 4px 3px 0}
        </style>
        <div class="tia-hero">
          <div class="tia-kicker">6868 · PARENT COMPANY</div>
          <div class="tia-title">TIA</div>
          <div class="tia-sub">TRADE INTELLIGENCE AGENCY · RESEARCH · INTELLIGENCE · DECISION</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _card(title: str, body: str):
    st.markdown(
        f'<div class="tia-card"><h4>{title}</h4><p>{body}</p></div>',
        unsafe_allow_html=True,
    )


def _overview():
    st.subheader("Intelligence Command Center")
    st.caption("Institution-level view. Live values appear only when a verified source is connected.")
    cols = st.columns(4)
    for col, label, value, help_text in [
        (cols[0], "Markets monitored", "—", "Connects to the existing Radar universe"),
        (cols[1], "Qualified opportunities", "—", "No opportunity is promoted without evidence"),
        (cols[2], "Active research tracks", "7", "Seven coordinated specialist functions"),
        (cols[3], "Portfolio risk", "—", "Requires verified portfolio and position data"),
    ]:
        col.metric(label, value, help=help_text)
    st.info("TIA is a new institutional layer. XPIX, Radar, Technical Office and Workspace remain unchanged and are reused as source systems.")
    a, b, c = st.columns(3)
    with a:
        _card("Market Intelligence", "Macro events, news catalysts, sessions and cross-asset context.")
        _card("Technical Intelligence", "Multi-timeframe structure, Price Action, SMC/ICT, Gann and Elliott context.")
    with b:
        _card("Order Flow & Liquidity", "Footprint, Delta, DOM, Time & Sales and liquidity evidence where feeds permit.")
        _card("Strategy & Innovation Lab", "Research, strategy hypotheses, indicator development and controlled experiments.")
    with c:
        _card("Quant Validation & Risk", "Backtests, out-of-sample checks, costs, drawdown and portfolio exposure.")
        _card("Trade Review & Decision", "Cross-team challenge, opportunity ranking and human-approved decision workflow.")


def _geometry():
    st.subheader("Geometric Intelligence")
    st.caption("Visual systems are tied to explicit analytical meanings; decorative motion is not presented as market evidence.")
    rows = [
        ("Radial Geometry", "Central asset with measured relationships to DXY, yields, metals, indices and catalysts. Distance is not correlation; show the calculated statistic and sample window."),
        ("Network Connections", "Nodes represent assets, events, strategies or liquidity zones. Edges represent measured correlation, lead/lag evidence or a traceable causal hypothesis."),
        ("Circular Data Systems", "Separate rings for market strength, session activity, portfolio exposure and risk components. Each ring has its own unit and source."),
        ("Polygonal Structures", "Triangulated structures for multi-factor confluence, liquidity geometry and regime comparisons; never imply a signal from shape alone."),
        ("Dynamic Grids", "Heatmaps for correlation, volatility, session activity, strategy performance and order-book liquidity, with clear source/time coverage."),
    ]
    for title, body in rows:
        _card(title, body)
    st.markdown("**Motion language**")
    st.write("Gold-first palette: charcoal / black, champagne gold, brass and restrained amber. Motion concepts: particle assembly, radial expansion, node-to-node pulses, grid illumination and controlled geometric morphing. The approved TIA monogram is a locked asset: do not redraw, reinterpret or morph its letter geometry.")


def _market():
    st.subheader("Trading Interface")
    tabs = st.segmented_control(
        "Trading modules",
        ["Candlestick & Structure", "Volume & Order Flow", "Heatmaps", "Portfolio Analytics"],
        default="Candlestick & Structure",
        key="tia_market_module",
        label_visibility="collapsed",
    )
    if tabs == "Candlestick & Structure":
        st.markdown("**Candlestick Charts · Market Structure**")
        st.write("Existing chart engine remains the chart source. Planned overlays: BOS/CHoCH, swing structure, FVG/IFVG, order blocks, liquidity sweeps, sessions, HTF levels and selectable strategy layers.")
        st.info("Integration state: design/specification stage. No duplicate chart renderer is introduced in this first shell.")
    elif tabs == "Volume & Order Flow":
        st.markdown("**Volume · Delta · Footprint · DOM · Time & Sales**")
        st.write("Display executed volume separately from displayed resting liquidity. Distinguish exchange-native values, broker-provided depth, derived estimates and unavailable history.")
        st.info("Order-flow modules remain in their existing XPIX locations until each integration is reviewed and tested.")
    elif tabs == "Heatmaps":
        st.markdown("**Liquidity · Volume · Correlation · Volatility · Sessions · Strategy Performance**")
        st.write("Each heatmap must disclose its unit, data provider, timestamp, sampling interval and coverage gaps.")
        st.info("No synthetic heatmap values are shown as live market data.")
    else:
        st.markdown("**Portfolio Exposure · Correlation Risk · Performance · Limits**")
        st.write("Planned measures: exposure by asset/class, correlated risk clusters, expectancy, profit factor, drawdown, R-multiples, session/strategy attribution and funded-account constraints.")
        st.info("Portfolio metrics remain unavailable until a verified journal/positions source is connected.")


def _agents():
    st.subheader("Seven specialist functions")
    agents = [
        ("01 · Intelligence Director", "Orchestration, priorities, evidence standards and final synthesis."),
        ("02 · Market Intelligence", "Macro, news, geopolitics, catalysts, sessions and cross-asset relationships."),
        ("03 · Technical Intelligence", "Price Action, SMC/ICT, Elliott, Gann, structure and multi-timeframe context."),
        ("04 · Order Flow & Liquidity", "Footprint, Delta, DOM, Time & Sales, execution and liquidity evidence."),
        ("05 · Strategy & Innovation Lab", "Research, strategy discovery, indicator development and experiments."),
        ("06 · Quant Validation & Risk", "Backtesting, walk-forward, costs, statistical validation and portfolio risk."),
        ("07 · Trade Review & Decision", "Challenge, confluence review, ranking, trade plans and post-trade learning."),
    ]
    for name, detail in agents:
        _card(name, detail)
    st.warning("The seven functions are organizational responsibilities, not a requirement to spawn seven isolated model instances. Shared services and specialist tools can support multiple functions.")


def render_tia():
    _header()
    selected = st.segmented_control(
        "TIA sections",
        ["Command Center", "Geometric Intelligence", "Trading Interface", "Seven Agents", "Roadmap"],
        default="Command Center",
        key="tia_section",
        label_visibility="collapsed",
    )
    if selected == "Command Center":
        _overview()
    elif selected == "Geometric Intelligence":
        _geometry()
    elif selected == "Trading Interface":
        _market()
    elif selected == "Seven Agents":
        _agents()
    else:
        st.subheader("TIA implementation roadmap")
        steps = [
            "Foundation: locked brand asset, information architecture and seven-function charter.",
            "Navigation shell: TIA tab between Radar and Workspace; preserve existing page IDs.",
            "Data contracts: source, timestamp, unit, coverage and confidence for every metric.",
            "Geometry layer: radial, network, circular, polygonal and dynamic-grid visualizations.",
            "Trading modules: chart/structure, order flow, heatmaps and portfolio analytics.",
            "Agent orchestration: shared memory, task routing, review and decision trail.",
            "Validation: unit tests, Streamlit AppTest, browser/mobile visual review and data-source checks.",
        ]
        for i, step in enumerate(steps, 1):
            st.markdown(f"**{i}.** {step}")
        st.caption("No merge, deployment, paid workflow or live order execution is performed by this branch.")
