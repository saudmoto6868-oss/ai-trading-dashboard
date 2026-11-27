"""Radar views: similar / performance / correlation / signals / screener, day plan and SMT board. Split from page_radar.py (M7)."""
import html

import streamlit as st

from modules.i18n import L, lang as _ui_lang
from modules.page_kit import rt
from modules.page_bg import DAY_SYMBOLS
from modules.market_cache import get_klines
from config import CRYPTO_SYMBOLS
from modules.chart_scan import (ALL_FILTERS, SHORT as CS_SHORT)
from modules.page_radar_data import _CX, _fv_frames, _radar_closes, _radar_data, _radar_pass, _radar_symbols, _tf_bars


def render_radar_similar(f):
    """Find similar charts (Finviz, Sep 2026): rank the symbols and past stretches whose recent price path looks like the chosen one."""
    import altair as alt
    import pandas as _pd
    from modules import fv_screen as FV
    ar = _ui_lang() == "ar"
    A = lambda e, a: a if ar else e
    c = st.columns([0.2, 1.2, 1.3, 1.3])
    tf = f["tf"]
    c[0].markdown(f"<div class='uk-chip' style='margin-top:26px'>{html.escape(tf)}</div>", unsafe_allow_html=True)
    with st.spinner(L("Loading the candles of every Radar symbol (the first load can take up to a minute; later loads are cached)")):
        frames = _fv_frames(tuple(_radar_symbols(f)), tf)
    if not frames:
        st.info(L("No candles yet."))
        return
    if st.session_state.get("sm_sym") not in frames:   # the filters changed the list: forget a target that is no longer in it
        st.session_state.pop("sm_sym", None)
    target = c[1].selectbox(A("Chart to match", "الشارت المطلوب مشابهته"), sorted(frames), key="sm_sym")
    win = int(c[2].slider(A("Window (bars)", "النافذة (شموع)"), 10, 120, 40, 5, key="sm_win"))
    ahead = int(c[3].slider(A("Bars to look ahead", "شموع للمتابعة بعدها"), 5, 40, 10, 5, key="sm_ahead"))
    res = FV.similar(frames, target, win, ahead, top=12)
    if not res:
        st.info(A("Not enough candles for this window.", "الشموع مش كفاية للنافذة دي."))
        return
    df = _pd.DataFrame([{A("Symbol", "الرمز"): r["symbol"], A("Match (best stretch)", "التطابق (أحسن فترة)"): r["corr"], A("Match now", "التطابق دلوقتي"): r["corr_now"],
                         A("Ended bars ago", "انتهت من كام شمعة"): r["offset"], A("Window move %", "حركة النافذة %"): r["ret"],
                         A("What followed %", "اللي حصل بعدها %"): r["after"]} for r in res])
    st.dataframe(df, hide_index=True, width="stretch")
    lines = []
    tz = frames[target]["close"].astype(float).tail(win).values
    z = lambda x: (x - x.mean()) / (x.std() or 1)
    for i, v in enumerate(z(tz)):
        lines.append({"x": i, "z": v, "series": A("Chosen: ", "المختار: ") + target})
    for r in res[:3]:
        if r["symbol"] == target and r["offset"] == 0:
            continue
        cl = frames[r["symbol"]]["close"].astype(float).values; n = len(cl); seg = cl[n - r["offset"] - win:n - r["offset"]]
        for i, v in enumerate(z(seg)):
            lines.append({"x": i, "z": v, "series": f"{r['symbol']} ({r['corr']:.2f}, {r['offset']} " + A("bars ago", "شمعة فاتت") + ")"})
    st.altair_chart(alt.Chart(_pd.DataFrame(lines)).mark_line().encode(x=alt.X("x:Q", title=A("bars", "شموع")), y=alt.Y("z:Q", title=A("shape (z-score)", "الشكل (z-score)")), color=alt.Color("series:N", legend=alt.Legend(orient="bottom", title=None))).properties(height=260), width="stretch")
    st.caption(A("Match = Pearson correlation of the two price paths (1 = same shape, -1 = mirror). 'Best stretch' picks the best of every window in the history, so it is always high on noisy prices: compare it with 'Match now'. 'What followed' is history of that look-alike, a description, not a forecast. Educational, not investment advice.",
                 "التطابق = معامل ارتباط بيرسون بين مسارين للسعر (1 = نفس الشكل، -1 = مقلوب). «أحسن فترة» بتختار أحسن نافذة في التاريخ كله فبتطلع عالية دايماً على الأسعار المتذبذبة: قارنها بـ«التطابق دلوقتي». «اللي حصل بعدها» تاريخ الشبيه ده، وصف مش توقع. تعليمي، مش توصية استثمارية."))


def render_radar_perf(f):
    """Finviz 'Performance' view: % change over fixed spans per symbol on the panel's timeframe, for the symbols that pass the panel's filters."""
    import pandas as _pd
    import altair as alt
    tf = f["tf"]
    syms = _radar_symbols(f)
    if not syms:
        st.info(L("No symbol meets ALL the chosen filters right now."))
        return
    px = _radar_closes(tuple(syms), tf)
    if px.empty:
        st.info(L("No candles yet."))
        return
    mins = _tf_bars(tf)
    if mins <= 1440:   # time spans: 1 h, 4 h, 24 h, 3 d, 1 w, 10 d, counted in candles of this timeframe
        spans = {k_: max(1, round(h_ * 60 / mins)) for k_, h_ in (("1 h", 1), ("4 h", 4), ("24 h", 24), ("3 d", 72), ("1 w", 168), ("10 d", 240))}
    else:              # daily and longer: candle counts
        spans = {"1 bar": 1, "5 bars": 5, "20 bars": 20, "60 bars": 60, "120 bars": 120, "250 bars": 250}
    sort_default = "24 h" if "24 h" in spans else "20 bars"
    rows = []
    for s in px.columns:
        c = px[s].dropna()
        r = {"Symbol": s, "Price": float(c.iloc[-1])}
        for k, n in spans.items():
            r[k] = round((c.iloc[-1] / c.iloc[-1 - n] - 1) * 100, 2) if len(c) > n else None
        r["Volatility 24 h %"] = round(float(c.pct_change().tail(24).std() * 100), 2) if len(c) > 25 else None   # last 24 candles of the chosen timeframe
        rows.append(r)
    df = _pd.DataFrame(rows)
    sort_by = st.segmented_control(L("Sort by"), list(spans), default=sort_default, key="perf_sort") or sort_default
    if sort_by not in spans:
        sort_by = sort_default
    df = df.sort_values(sort_by, ascending=False, na_position="last")
    k = st.columns(4)
    v = df[sort_by].dropna()
    k[0].metric(L("Symbols"), len(df)); k[1].metric(L("Up") + f" ({sort_by})", int((v > 0).sum())); k[2].metric(L("Down") + f" ({sort_by})", int((v < 0).sum()))
    k[3].metric(L("Median") + f" ({sort_by})", f"{v.median():+.2f}%" if len(v) else "-")
    pc = {c: st.column_config.NumberColumn(format="%+.2f%%") for c in spans}
    st.dataframe(df.rename(columns={"Symbol": L("Symbol"), "Price": L("Price"), "Volatility 24 h %": L("Volatility 24 h %")}), hide_index=True,
                 width="stretch", column_config={**pc, L("Price"): st.column_config.NumberColumn(format="%.4g")})
    long = df.melt(id_vars="Symbol", value_vars=list(spans), var_name="span", value_name="pct").dropna()
    st.markdown(f"**{L('Change % by period (heat map)')}**")
    st.altair_chart(alt.Chart(long).mark_rect().encode(
        x=alt.X("span:N", sort=list(spans), title=None), y=alt.Y("Symbol:N", sort=list(df["Symbol"]), title=None),
        color=alt.Color("pct:Q", scale=alt.Scale(scheme="redyellowgreen", domainMid=0), title="%"), tooltip=["Symbol", "span", "pct"]
    ).properties(height=max(200, 20 * len(df))), width="stretch")
    st.caption(f"{tf} · {len(df)} / {len(rt().SCAN_SYMBOLS)} " + L("symbols") + " · " + L("Candles from the same source as the charts. Educational, not investment advice."))


def render_radar_corr(f):
    """Correlation of returns on the panel's timeframe, for the symbols that pass the panel's filters: which move together (one trade, not two) and which hedge."""
    import altair as alt
    syms = _radar_symbols(f)
    px = _radar_closes(tuple(syms), f["tf"]) if syms else None
    if px is None:
        st.info(L("No symbol meets ALL the chosen filters right now."))
        return
    if px.shape[1] < 2:
        st.info(L("Need at least two symbols with candles."))
        return
    rets = px.pct_change(fill_method=None).dropna(how="all")
    cm = rets.corr().round(2)
    long = cm.reset_index(names="a").melt(id_vars="a", var_name="b", value_name="corr")
    order = list(cm.columns)
    st.altair_chart(alt.Chart(long).mark_rect().encode(
        x=alt.X("b:N", sort=order, title=None), y=alt.Y("a:N", sort=order, title=None),
        color=alt.Color("corr:Q", scale=alt.Scale(scheme="blueorange", domain=[-1, 1]), title="corr"), tooltip=["a", "b", "corr"]
    ).properties(height=max(260, 22 * len(order))), width="stretch")
    pairs = long[long["a"] < long["b"]].sort_values("corr")
    a, b = st.columns(2)
    a.markdown(f"**{L('Move together (corr >= 0.8): treat as one position')}**")
    a.dataframe(pairs[pairs["corr"] >= 0.8].sort_values("corr", ascending=False).head(12), hide_index=True, width="stretch")
    b.markdown(f"**{L('Lowest correlation (diversify / hedge)')}**")
    b.dataframe(pairs.head(12), hide_index=True, width="stretch")
    st.caption(f"{f['tf']} · " + L("Pearson correlation of returns, last 260 candles. Correlation changes over time; it is not a forecast."))


def render_radar_signals(f):
    """Finviz 'Signal' list: every pattern / strategy signal live now, the symbols it fired on, its side, and the lab's number."""
    import pandas as _pd
    from modules import office_kpi as _OK
    from modules.chart_scan import STRATEGY_FILTERS as _SF, PATTERN_FILTERS as _PF, flag_side
    tf = f["tf"]
    data = _radar_data(f)
    if data is None:
        return
    data = {s_: d_ for s_, d_ in data.items() if _radar_pass(d_, f)}   # only the symbols that pass the shared filters
    lab = _OK.load()
    by = {}
    for sym, d in data.items():
        for k in d["flags"]:
            if k in _SF or k in _PF:
                side = flag_side(k) or "/".join(d.get("sides", {}).get(k, [])) or "-"
                by.setdefault(k, []).append(f"{sym} ({side})" if side != "-" else sym)
    rows = []
    for k, syms in by.items():
        ev = _OK.evidence(lab, _SF[k][1][1], tf) if k in _SF and _SF[k][1][0] == "key" else None
        rows.append({"Signal": _SF[k][0] if k in _SF else _PF[k], "Kind": "Strategy" if k in _SF else "Pattern", "Count": len(syms),
                     "Symbols": ", ".join(sorted(syms)[:12]), "Lab net R": ev["net"] if ev else None, "Lab n": ev["n"] if ev else None,
                     "Lab": ("OFF" if ev["off"] else "passed" if ev["gate"] else "not evidence") if ev else "-"})
    if not rows:
        st.info(L("No signals on this timeframe right now."))
        return
    df = _pd.DataFrame(rows).sort_values(["Count", "Lab net R"], ascending=[False, False], na_position="last")
    k = st.columns(3)
    k[0].metric(L("Signals live"), len(df)); k[1].metric(L("Symbols scanned"), len(data))
    k[2].metric(L("With positive lab net R"), int((df["Lab net R"].fillna(-1) > 0).sum()))
    from collections import Counter as _Cnt
    _rc = _Cnt(d_.get("regime") for d_ in data.values() if d_.get("regime"))
    if _rc:
        st.caption(L("Market regime of the scanned symbols now") + ": " + " · ".join(f"{r_} {n_}" for r_, n_ in _rc.most_common()))
    df["Kind"] = df["Kind"].map(L); df["Lab"] = df["Lab"].map(L)
    st.dataframe(df.rename(columns={c: L(c) for c in df.columns}), hide_index=True, width="stretch",
                 column_config={L("Lab net R"): st.column_config.NumberColumn(format="%+.3f")})
    st.caption(L("Lab net R = the weekly lab's average R after 0.1R costs for that detector on the nearest lab timeframe. A signal is a suggestion, not evidence, until it passes the gate."))


def render_radar_screener(f):
    """Finviz-style table (owner 2026-10-22): one sortable table for the Radar universe, filtered by the SAME panel as the chart grid (no second set of
    options), and a top-movers bar chart. Same candles as the chart grid (cached)."""
    import pandas as _pd
    data = _radar_data(f)
    if data is None:
        return
    rows = []
    for sym, d in data.items():
        sig = [(_CX.FLAG_AR[k] if _ui_lang() == "ar" and k in _CX.FLAG_AR else L(CS_SHORT.get(k, k))) for k in d["flags"] if k in ALL_FILTERS]
        rows.append({"Symbol": sym, "Price": d["price"], "Change %": d.get("chg"), "20-bar %": d.get("chg20"), "RSI": d["rsi"],
                     "Volume ×avg": d.get("volx"), "ATR %": d.get("atrp"), "Trend": d.get("trend"), "Signals": len(sig), "Which": " · ".join(sig[:8])})
    df = _pd.DataFrame(rows)
    if df.empty:
        st.info(L("No symbols match the selected conditions right now."))
        return
    df = df[df["Symbol"].isin([s_ for s_, d_ in data.items() if _radar_pass(d_, f)])]
    k = st.columns(5)
    k[0].metric(L("Matched"), f"{len(df)} / {len(rows)}")
    k[1].metric(L("Trend up"), int((df["Trend"] == "up").sum()))
    k[2].metric(L("Trend down"), int((df["Trend"] == "down").sum()))
    k[3].metric(L("Oversold (RSI ≤ 30)"), int((df["RSI"] <= 30).sum()))
    k[4].metric(L("Overbought (RSI ≥ 70)"), int((df["RSI"] >= 70).sum()))
    shown_df = df.sort_values("20-bar %", ascending=False, na_position="last").assign(Trend=lambda x: x["Trend"].map(L))
    st.dataframe(shown_df.rename(columns={c: L(c) for c in shown_df.columns}), hide_index=True, width="stretch",
                 column_config={L("Price"): st.column_config.NumberColumn(format="%.4g"),
                                L("Change %"): st.column_config.NumberColumn(format="%+.2f%%"), L("20-bar %"): st.column_config.NumberColumn(format="%+.2f%%"),
                                "RSI": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f"),
                                L("Volume ×avg"): st.column_config.NumberColumn(format="%.2f×"), "ATR %": st.column_config.NumberColumn(format="%.2f%%")})
    top = df.dropna(subset=["20-bar %"]).sort_values("20-bar %")
    if len(top):
        import altair as alt
        top = _pd.concat([top.head(8), top.tail(8)]).drop_duplicates("Symbol")
        st.markdown(f"**{L('Top movers over 20 bars')}**")
        st.altair_chart(alt.Chart(top).mark_bar().encode(
            x=alt.X("20-bar %:Q", title="%"), y=alt.Y("Symbol:N", sort="-x", title=None),
            color=alt.condition("datum['20-bar %'] > 0", alt.value("#2dd4bf"), alt.value("#f87171")), tooltip=["Symbol", "20-bar %", "RSI", "Trend"]
        ).properties(height=max(160, 18 * len(top))), width="stretch")
    st.caption(L("Educational, not investment advice. Same candles as the Charts tab; no automatic orders."))


# the Chart Scanner scans the whole universe synchronously (can take minutes on a cold server): it runs AFTER the Workspace,
# otherwise the first tab stays blank until the scan finishes (Streamlit renders in code order, not tab order)
def render_day_plan(scan_symbols):
    """Radar > Day plan: today's trades by session and timeframe confluence (modules/day_plan.py). Standard = confluence; option = scalp on one timeframe."""
    from modules import day_plan as _DP, day_plan_ui as _DPU
    ar = _ui_lang() == "ar"
    st.markdown(_DPU.timeline_html(_DP.session_clock(), ar=ar), unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.3, 1, 1.4, 1])
    mode_lbl = c1.radio(L("Mode"), ["Timeframe confluence (standard)", "Scalp (one timeframe)"], key="dp_mode")
    mode = "conf" if mode_lbl.startswith("Timeframe") else "scalp"
    trig = None
    if mode == "scalp":
        trig = (c2.selectbox(L("Trigger timeframe"), ["5m", "15m", "1h"], key="dp_tf"),)
    mv = c3.selectbox(L("Minimum possible move (points)"), ["Any", 100, 150, 200, 300, 1000], key="dp_pts")
    stars = c4.slider(L("Min stars"), 1, 4, 2, key="dp_stars")
    schools = st.multiselect(L("Only these schools (empty = all)"), ["SMC / ICT", "Elliott wave", "Fibonacci", "Liquidity", "Trend (MA)", "Levels / breakouts", "Time (sessions)", "Price action", "Chart patterns (range)", "Wyckoff", "Momentum / divergence", "Harmonic"], key="dp_sch")
    uni = st.radio(L("Universe"), ["Day-plan list", "Current Radar universe"], horizontal=True, key="dp_uni")
    tr = st.number_input(L("Stop starts moving after (points)"), 10, 5000, 100, 10, key="dp_trail", help=L("Standard mode: once a trade is this many points in profit the stop moves to break-even, then trails."))
    syms = tuple(DAY_SYMBOLS if uni == "Day-plan list" else (scan_symbols or CRYPTO_SYMBOLS)[:20])

    @st.cache_data(ttl=300, show_spinner=False)
    def _run(syms_t, mode_, trig_, sch_t, mv_, stars_, tr_):
        return _DP.scan(list(syms_t), lambda s_, t_: get_klines(s_, t_, 300), mode=mode_, trigger_tfs=trig_, schools=list(sch_t) or None,
                        min_points=(0 if mv_ == "Any" else float(mv_)), min_stars=stars_, trail_start_points=float(tr_))

    with st.spinner(L("Building the day plan...")):
        plans = _run(syms, mode, trig, tuple(schools), mv, int(stars), float(tr))
    st.caption(L("Higher timeframes (1D + 4H) set the bias, the trigger timeframes give the entry; a plan is listed only when enough timeframes agree. Stars = the scanner's evidence count, not a win rate; new schools are context until the lab measures them. Not financial advice."))
    if not plans:
        st.info(L("No plan matches right now. Loosen the filters or wait for the next session."))
        return
    for p in plans[:30]:
        st.markdown(_DPU.card_html(p, ar=ar), unsafe_allow_html=True)
    if st.button(L("Send the top plans to Telegram"), key="dp_send"):
        from modules import telegram_alerts as _tga
        _n, _e = _DP.dispatch(plans, {}, _tga.send, top_n=3)
        st.success(f"Telegram: {_n} sent") if not _e else st.warning(_e)


def render_smt_board():
    """Radar > SMT pairs: every correlated pair on the chosen timeframes; each event shows BOTH markets side by side."""
    from modules import intermarket as _IM, intermarket_ui as _IMU
    ar = _ui_lang() == "ar"
    c1, c2 = st.columns([3, 1])
    tfs = c1.multiselect(L("Timeframes"), list(_IM.TF_ORDER[:7])[::-1], default=[t for t in ("15m", "1h", "4h", "1d")], key="smt_tfs")
    if c2.button(L("Rescan now"), key="smt_rescan"):
        st.cache_data.clear()

    @st.cache_data(ttl=300, show_spinner=False)
    def _run(tfs_t):
        return _IM.scan_pairs(lambda s_, t_: get_klines(s_, t_, 300), tfs=tfs_t)

    with st.spinner(L("Comparing the correlated pairs...")):
        ev = _run(tuple(tfs or ("1h",)))
    st.caption(L("SMT = two correlated markets disagree at a swing (one makes a new low / high, the other refuses). A hint of reversal, not a trade by itself; no win rate is claimed here. Pairs that stopped moving together are skipped."))
    if not ev:
        st.info(L("No SMT between the correlated pairs on these timeframes right now."))
        return
    for e in ev[:40]:
        st.markdown(_IMU.event_card(e, ar=ar), unsafe_allow_html=True)
