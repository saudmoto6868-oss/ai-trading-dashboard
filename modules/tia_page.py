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
    </style><div class="tia-hero"><div class="tia-kicker">TRADE INTELLIGENCE AGENCY</div><div class="tia-title">TIA</div><div class="tia-sub">INSTITUTIONAL FINANCIAL INTELLIGENCE · RESEARCH · DECISION</div></div>""", unsafe_allow_html=True)

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
        _card("Strategy & Research Intelligence","Research, strategy discovery and indicator development.")
    with c:
        _card("Quant & Risk Intelligence","Backtests, out-of-sample checks, costs and portfolio risk.")
        _card("Trade Decision & Performance Intelligence","Challenge, ranking, trade plans and human-approved decisions.")

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

def _meeting_room():
    st.subheader("TIA Meeting Room")
    st.caption("Dedicated identity archive, source references, decisions, review notes and project files.")
    st.markdown("### Locked identity rules")
    for item in [
      "Use the last owner-approved TIA logo exactly; do not redraw, distort or convert it into a 77 motif.",
      "TIA dominates; descriptor remains subordinate and no wider than the TIA mark.",
      "6868 remains contiguous, centered and on the same background.",
      "Charcoal/black foundation; champagne, brass and warm gold primary; orange/amber restrained.",
      "Create original patterns inspired by references, never copies of reference artwork.",
      "Motion transforms particles and surrounding fields, not the approved letter geometry."]:
        st.markdown("- "+item)
    st.divider()
    st.markdown("### Archive record")
    for title,desc in [
      ("01 · Approved identity","Locked logo, wordmark proportions, 6868 signature and usage rules."),
      ("02 · Explorations","Historical logo generations, dark/gold posters, minimal variants and alternate lockups."),
      ("03 · Moodboards","M7 / 77 boards, gold-first boards, orange/cream boards and dark UI compositions."),
      ("04 · Motion references","Particle assembly, Morphiq-inspired transitions, topographic contours, dotted meshes and final logo hold."),
      ("05 · Meeting record","Chronological owner decisions, handoffs, reviews and unresolved approvals."),
      ("06 · Project files","TIA page shell, foundation charter, meeting archive, meeting notes and whiteboard item.")]:
        _card(title,desc)
    st.markdown("### Reference links")
    st.markdown("- [TIA identity and motion reference folder](https://drive.google.com/drive/folders/1L1QNx2ZNAGk5kBKfQf2sBUJzvcDUdDAz)")
    st.markdown("- [Threads motion reference — Morphiq](https://www.threads.com/@alvarodiazds_/post/DfcYGnQTRVW)")
    st.markdown("- Repository archive: docs/TIA_MEETING_ROOM.md")
    st.markdown("### Image inventory")
    st.caption("The repository archive records filenames and provenance. Binary copies of every original image are not yet verified in this branch.")
    st.markdown("Identity boards: a_detailed_polished_branding_identity_system_bo.png; a_cohesive_brand_identity_moodboard_in_a_dark_char.png; a_sleek_high_end_dark_ui_moodboard_composition_wi.png.")
    st.markdown("M7 boards: M7 Market Intelligence Brand Board.png; M7 Market Intelligence Brand Board(1).png; M7 Market Intelligence Brand System.png; 77% Market Intelligence Brand Board.png.")
    st.markdown("Logo explorations: tia_trade_intelligence_agency_logo.png; trade_intelligence_agency_global_logo.png; glossy_tia_logo_with_golden_wave.png; luxury_tia_logo_with_golden_wave.png; futuristic_tia_golden_wave_logo.png; futuristic_tia_logo_with_golden_wave.png; futuristic_tia_logo_with_golden_mesh.png; luxury_tia_trade_intelligence_logo.png; luxury_gold_wave_tia_logo_poster.png; minimalist_tia_6868_gold_logo.png.")
    st.info("The 171 MB screen recording is referenced from its Drive folder; it has not been copied into Git.")

def _knowledge_room():
    st.subheader("Knowledge & Decision Registry")
    st.caption("TIA-native records only. The separate Academy project remains independent; this workspace consumes no Academy files or database.")
    try:
        from modules.tia_knowledge_store import TIAKnowledgeStore
        store = TIAKnowledgeStore()
        health = store.health()
    except Exception as exc:
        st.error(f"TIA knowledge store unavailable: {type(exc).__name__}: {exc}")
        return
    st.metric("Local store status", health.status.upper())
    st.caption(f"Backend: {health.backend} · Schema: {health.schema_version or 'unknown'} · {health.detail}")
    if health.status != "ready":
        st.warning("Registry data is unavailable or requires attention. No empty-state or zero-value fallback is presented as valid data.")
        return
    left, right = st.columns(2)
    with left:
        st.markdown("#### Approved knowledge")
        try:
            records = store.list_knowledge(status="approved", limit=20)
            if not records:
                st.info("No approved knowledge records yet.")
            for record in records:
                with st.expander(record["title"]):
                    st.caption(f'{record["category"]} · {record["created_by"]} · {record["content_sha256"][:12]}')
                    st.write(record["body"])
                    if record.get("source_url"):
                        st.markdown(f'[Open source]({record["source_url"]})')
        except Exception as exc:
            st.error(f"Knowledge query failed: {type(exc).__name__}: {exc}")
    with right:
        st.markdown("#### Recent meeting events")
        try:
            events = store.list_meeting_events(limit=20)
            if not events:
                st.info("No meeting events recorded yet.")
            for event in events:
                with st.expander(f'{event["kind"].upper()} · {event["title"]}'):
                    st.caption(f'{event["meeting_id"]} · {event["actor"]} · {event["event_id"]}')
                    st.write(event["body"])
            if events:
                st.caption("Append-only hash chain: " + ("verified" if store.verify_meeting_chain() else "verification failed"))
        except Exception as exc:
            st.error(f"Meeting journal query failed: {type(exc).__name__}: {exc}")
    st.info("This first increment is read-only in the interface. Shared-database deployment, access control and backup/restore validation are separate release gates.")

def render_tia():
    _header()
    selected=st.segmented_control("TIA sections",["Command Center","Geometric Intelligence","Trading Interface","Seven Agents","TIA Meeting Room","Knowledge & Decisions","Roadmap"],default="Command Center",key="tia_section",label_visibility="collapsed")
    if selected=="Command Center": _overview()
    elif selected=="Geometric Intelligence": _geometry()
    elif selected=="Trading Interface": _market()
    elif selected=="Seven Agents": _agents()
    elif selected=="TIA Meeting Room": _meeting_room()
    elif selected=="Knowledge & Decisions": _knowledge_room()
    else:
        st.subheader("TIA implementation roadmap")
        for i,step in enumerate(["Lock approved brand asset and charter.","Preserve navigation and existing page IDs.","Define source/time/unit/coverage data contracts.","Build five geometry systems.","Integrate chart, order-flow, heatmap and portfolio modules.","Add orchestration and decision trail.","Validate tests and desktop/mobile rendering."],1):
            st.markdown(f"**{i}.** {step}")
        st.caption("No merge, deployment or live order execution is performed by this branch.")
