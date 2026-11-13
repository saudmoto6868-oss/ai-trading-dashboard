"""Standalone Streamlit entry point for the 2.6 research workspace.

This UI intentionally exposes research status only. It does not create orders,
fetch prices, or manufacture backtest metrics.
"""
import streamlit as st


def render() -> None:
    st.title("2.6 Strategy Intelligence")
    st.caption("Matimatiki · Standalone multi-market research workspace")
    st.warning(
        "RESEARCH ONLY — no live execution. No validated edge or performance "
        "results are available yet."
    )

    a, b, c, d = st.columns(4)
    a.metric("Repository", "MR !70 merged", "main · bd761281")
    b.metric("Validation", "Not verified", "CI quota exceeded")
    c.metric("First market", "XAUUSD", "Then FX · Indices")
    d.metric("Market data", "Awaiting data", "Broker OHLC required")

    overview, engines, evidence = st.tabs(
        ["Overview", "Strategy engines", "Evidence & next steps"]
    )
    with overview:
        left, right = st.columns(2)
        with left:
            st.subheader("Independent research pipeline")
            st.write(
                "2.6 is isolated from CFX and XPIX. The approved scope is "
                "historical research, reproducible testing, and paper simulation."
            )
            st.markdown(
                "- **Scope:** Full standalone research product\n"
                "- **Markets:** XAUUSD → FX → Indices\n"
                "- **Execution:** Disabled\n"
                "- **Results:** No validated performance claims"
            )
        with right:
            st.subheader("Research guardrails")
            st.markdown(
                "- No live orders or broker execution\n"
                "- No synthetic candles presented as market data\n"
                "- H1 and H2 must be evaluated independently\n"
                "- GC=F futures proxy is not spot XAUUSD\n"
                "- Optional ICT / SMC / Fibonacci / Gann filters require ablation tests"
            )
        st.subheader("XAUUSD market workspace")
        st.info(
            "Chart is waiting for validated broker XAUUSD OHLC data. "
            "No illustrative prices, candles, or signals are generated."
        )
        st.caption(
            "Required contract: timezone-aware ISO-8601 timestamps, strictly "
            "increasing unique times, positive OHLC values, and OHLC integrity."
        )

    with engines:
        h1, h2 = st.columns(2)
        with h1:
            st.subheader("H1 · Retracement Entry")
            st.success("Event-study harness exists")
            st.write(
                "Candidate retracement entry based on a confirmed impulse leg "
                "and the 1/2.6 ratio. Current event-study code covers H1 only."
            )
            st.markdown(
                "- Confirmed pivots with right-side delay\n"
                "- Leg-direction-aware event construction\n"
                "- Touch-based limit fill is a simulation assumption\n"
                "- Not a complete SL/TP or portfolio backtest"
            )
        with h2:
            st.subheader("H2 · Liquidity Projection")
            st.info("Event builder exists (assumption-based; not run on real data)")
            st.write(
                "Separate hypothesis: measure a completed impulse and project "
                "from an independently identified liquidity reference."
            )
            st.markdown(
                "- EQH / EQL or swept-liquidity anchor\n"
                "- Explicit sweep trigger and causal timestamp\n"
                "- Independent event study and statistical evaluation\n"
                "- Must not inherit H1 results"
            )

    with evidence:
        st.subheader("Validation backlog")
        items = [
            "Run unit tests after CI quota returns",
            "Acquire broker XAUUSD spot M1/M5 OHLC + cost metadata",
            "Add matched controls and event de-clustering",
            "Add block bootstrap / permutation and untouched holdout",
            "Confirm H2 rules vs creator videos; run on real data",
            "Only then consider FX expansion",
        ]
        for item in items:
            st.checkbox(item, value=False, key="two_six_todo_" + str(items.index(item)))
        st.subheader("Repository documentation")
        base = "https://gitlab.com/6868-group/ai-trading-dashboard/-/blob/main/research/strategies/2.6/"
        st.markdown(
            f"- [README]({base}README.md)\n"
            f"- [Implementation plan]({base}IMPLEMENTATION_PLAN.md)\n"
            f"- [Architecture]({base}ARCHITECTURE.md)"
        )

    st.caption(
        "2.6 Strategy Intelligence · Research only · No financial advice · "
        "No live trading capability"
    )
