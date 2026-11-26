"""2.6 Lab page: the 2.6 method on a live chart (entries, stops, targets) + how to read it.

Research only: it never places orders. Stop / target rules are provisional
(see modules/two_six_chart.py) until the creator's rules are confirmed.
"""
import pandas as pd
import streamlit as st

SYMBOLS = {"Gold (Hyperliquid)": "HL:xyz:GOLD", "Gold futures (Yahoo GC=F)": "Y:GC=F",
           "Silver (Hyperliquid)": "HL:xyz:SILVER", "BTC": "BTC-USDT"}
GUIDE = """
**How the 2.6 setups are drawn (provisional rules, not the creator's confirmed rules)**

- **H1 · Retracement:** after a swing completes (low → high, or high → low), measure the leg.
  Entry is a pullback of *leg ÷ 2.6* (≈ 38.5 %, almost the Fibonacci 38.2 %).
- **H2 · Liquidity:** two equal highs (or lows) form a pool; price wicks through it and closes back inside (sweep).
  Take the last opposite leg, divide by 2.6, and place the entry that distance beyond the pool.
- **Stop / targets:** *u* = leg ÷ 2.6. Stop = entry ∓ u (1R). TP1 = 1R, TP2 = 2R.
  If a candle touches the stop and a target, it counts as stopped (worst case).
- **On the chart:** dashed purple = measured leg · green/red line = entry · red dotted = stop ·
  blue dotted = TP1 / TP2 · yellow dotted = swept pool · arrow = filled · square = exit.
- Results below are a replay on the candles shown, **not evidence** (small n, no costs, rules unconfirmed).
"""


def _df(sym, tf, limit):
    from modules.market_cache import get_klines
    return get_klines(sym, tf, limit)


def _journal_block(plays, times, sym, tf, last_close) -> None:
    """2.6 journal: save every setup of these candles (updated in place) and show the review of each one."""
    from pathlib import Path
    from modules import two_six_journal as tj
    path = Path(__file__).resolve().parents[1] / "data" / "two_six" / "journal.jsonl"
    st.subheader("2.6 journal")
    st.caption("Each setup = one row: why it was taken or rejected, its review, the best live setup now, and the follow-up. "
               "Saved in data/two_six (git-ignored). Research only.")
    if st.button("Save these setups to the journal", key="ts_journal_save"):
        recs = tj.build_records(plays, [str(t) for t in times], sym, tf, last_price=last_close)
        changed = tj.upsert(recs, path)
        st.success(f"Journal updated: {changed} row(s) changed, {len(recs)} setups on these candles.")
    rows = tj.load(path)
    s = tj.summary(rows)
    st.info(f"Journal: {s['rows']} rows · {s['live']} live · {s['expired']} expired · {s['text']}")
    if rows:
        view = [{"time": r["time"], "setup": f"{r['kind']} {r['side']} {r['tf']}", "status": r["status"],
                 "R": r["outcome_r"], "best now": "★" if r.get("best_now") else "",
                 "why taken": " · ".join(r["why_taken"]), "why rejected": " · ".join(r["why_rejected"]),
                 "review": r["review"], "follow-up": r["followup"], "note": r.get("note", "")}
                for r in sorted(rows, key=lambda r: r["time"], reverse=True)[:100]]
        st.dataframe(pd.DataFrame(view), hide_index=True, width="stretch")


def render() -> None:
    from modules import two_six_chart as tc
    st.title("2.6 Strategy")
    st.caption("Matimatiki 2.6 · entries / stops / targets on the chart · research only, no orders")
    c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 1, 1, 1, 1, 1, 1])
    sym = SYMBOLS[c1.selectbox("Market", list(SYMBOLS), key="ts_sym")]
    tf = c2.selectbox("Timeframe", ["5m", "15m", "1h", "4h", "1d"], index=1, key="ts_tf")
    ratio = c3.selectbox("Ratio", [2.6, 2.618], key="ts_ratio")
    use_h1 = c4.checkbox("H1 retracement", True, key="ts_h1")
    use_h2 = c5.checkbox("H2 liquidity", True, key="ts_h2")
    swing = c6.selectbox("Swing size", [3, 5, 8, 13], index=1, key="ts_swing", help="bars on each side that confirm a swing high / low")
    show = c7.selectbox("Show last", [3, 6, 10, 20], index=1, key="ts_show")
    try:
        df = _df(sym, tf, 500)
    except Exception as exc:
        st.warning(f"No candles for {sym} {tf}: {type(exc).__name__}: {exc}")
        df = None
    if df is not None and len(df) >= 50:
        plays = tc.setups(tc.bars_from_df(df), ratio=ratio, left=swing, right=swing, use_h1=use_h1, use_h2=use_h2)
        shown = plays[-show:]
        st.iframe(tc.chart_html(df, shown), height=580, alt="2.6 chart")
        times = list(df["time"])
        rows = [{"time": times[p["known"]], "type": p["kind"], "side": p["side"], "status": p["status"],
                 "entry": round(p["entry"], 2), "stop": round(p["stop"], 2),
                 "TP1": round(p["tp1"], 2), "TP2": round(p["tp2"], 2)} for p in reversed(plays)]
        st.subheader("Setups (latest first)")
        st.caption(f"{len(plays)} setups on these {len(df)} candles · the chart shows the latest {len(shown)}")
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        done = [p["status"] for p in plays if p["status"] in ("TP2", "stopped", "TP1 then stop")]
        if done:
            st.caption("Closed on this replay: " + ", ".join(f"{k} {done.count(k)}" for k in ("TP2", "TP1 then stop", "stopped"))
                       + f" (n={len(done)}; not evidence below n=30 and without costs)")
        _journal_block(plays, times, sym, tf, float(df["close"].iloc[-1]))
    elif df is not None:
        st.warning("Not enough candles to find setups.")
    st.markdown(GUIDE)
    with st.expander("Research status (engines, tests, next steps)"):
        _research_status()


def _research_status() -> None:
    # one view at a time: only the picked section runs (maintenance plan M4)
    view = st.segmented_control("View", ["Overview", "Strategy engines", "Evidence & next steps"], default="Overview", key="tsl_status_view", label_visibility="collapsed") or "Overview"
    if view == "Overview":
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

    if view == "Strategy engines":
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

    if view == "Evidence & next steps":
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
