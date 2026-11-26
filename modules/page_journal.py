"""Journal page (index 4). Moved from main.py unchanged (maintenance plan M7 / 4.2)."""

import streamlit as st

from modules.i18n import L
from modules.page_kit import xl as _xl


def render_kpi_strip(jdf):
    """KPI strip for the journal upload: six headline numbers, an evidence badge, and breakdowns by symbol / strategy."""
    from modules.kpi import COST_R, GATE_N, breakdown, kpis
    k = kpis(jdf)
    ev = k["evidence"]
    badge_col = {"passes gate": "🟢", "not yet": "🟠", "not evidence": "⚪"}[ev["badge"]]
    st.markdown(f"**{badge_col} {L('Evidence')}: {L(ev['badge'])}** "
                f"· n = {k['n']} ({L('needs')} {GATE_N}+) · t = {ev['t']:.2f} · "
                f"{L('avg R in both halves')}: {ev['halves'][0]:+.2f} / {ev['halves'][1]:+.2f}")
    c = st.columns(6)
    c[0].metric(L("Trades"), k["n"])
    c[1].metric(L("Win rate"), f"{k['win_rate']*100:.0f}%" if k["n"] else "–")
    c[2].metric(L("Expectancy (R)"), f"{k['expectancy_r']:+.2f}" if k["n"] else "–")
    c[3].metric(L("Profit factor"), ("∞" if k["profit_factor"] == float("inf") else f"{k['profit_factor']:.2f}") if k["n"] else "–")
    c[4].metric(L("Max drawdown (R)"), f"{k['max_dd_r']:.1f}" if k["n"] else "–")
    c[5].metric(L("After costs (R)"), f"{k['net_expectancy_r']:+.2f}" if k["n"] else "–")
    st.caption(L("Costs = {c} R per trade (planning estimate, not measured). Grey = under {n} trades, not evidence.").format(c=COST_R, n=GATE_N))
    for key, label in (("symbol", L("By symbol")), ("strategy", L("By strategy"))):
        if key in jdf.columns:
            st.markdown(f"**{label}**")
            _bd = breakdown(jdf, key).assign(badge=lambda x: x["badge"].map(L))
            st.dataframe(_bd.rename(columns={key: L("Symbol" if key == "symbol" else "Strategy"), "win_rate": L("Win rate"), "expectancy_r": L("Expectancy (R)"), "badge": L("Evidence")}), hide_index=True)


def _stats_journal_kpis(jdf):
    """Stats > My journal: net R, profit factor, drawdown in R, and live vs backtest (lab average)."""
    from modules import office_kpi as _OK, office_ui as U
    col = next((c for c in jdf.columns if str(c).strip().lower() in ("r", "r_multiple", "rr")), None)
    if col is None:
        return
    j = _OK.journal_kpis(jdf[col].tolist())
    if not j["n"]:
        return
    la = _OK.lab_avg(_OK.load())
    diff = None if la is None else round(j["avgR"] - la, 3)
    st.markdown(U.CSS + "<div class='xo-row'>" + U.indicators(L("Journal in R"), [
        (L("Trades"), j["n"], L("closed"), None),
        (L("Win rate"), f"{j['win']*100:.0f}%", "", None),
        (L("avg R"), f"{j['avgR']:+.3f}", L("net") + f" {j['net']:+.3f}", "ok" if j["net"] > 0 else "bad"),
        (L("Profit factor"), "-" if j["pf"] is None else j["pf"], L("gains / losses"), "ok" if (j["pf"] or 0) > 1 else "bad"),
        (L("Max drawdown"), f"{j['maxdd']}R", L("from the equity peak"), "warn" if j["maxdd"] < 0 else None),
        ("t", "-" if j["t"] is None else j["t"], L("evidence needs t > 3 and n >= 100"), "ok" if (j["t"] or 0) > 3 and j["n"] >= 100 else None),
        (L("Live vs backtest"), "-" if diff is None else f"{diff:+.3f}R", L("your avg R minus the lab's") + ("" if la is None else f" ({la:+.3f})"),
         None if diff is None else "ok" if diff >= 0 else "warn"),
        (L("Total"), f"{j['total']:+.2f}R", "", None)]) + "</div>", unsafe_allow_html=True)
    if j["n"] < 30:
        st.caption(L("Fewer than 30 trades: the live vs backtest comparison is noise for now."))


def render_page():   # journal (2026-11-09: mock Edge Map / Robustness / Execution and the duplicate Lab evidence tab removed - the lab lives in Lab > Technical Office)
    global _c, _dd, _e, _html, _jdf, _m, _mc, _mc_render, _mc_summary, _msg, _pd, _ret, _risk, _st, _stab, _up, perf_stats, quantstats_html, returns_from_trades   # module-level names, as in main.py before (M7)
    if st.session_state.get("stats_tab") not in ("My journal", "Monte Carlo"):
        st.session_state.pop("stats_tab", None)
    _stab = st.segmented_control(" ", ["My journal", "Monte Carlo"], default="My journal", format_func=L, key="stats_tab", label_visibility="collapsed") or "My journal"
    if _stab == "Monte Carlo":
        from modules.quant_montecarlo import render as _mc_render
        _mc_render()
        st.stop()
    st.subheader(L("Performance report (QuantStats)"))
    st.caption(L("The Workspace journal lives in your browser, so export it first: Journal widget > CSV button. Upload that file here. "
                 "Returns = R x the % of the account you risk per trade. Evidence from the dashboard's own signals only - not a proven edge."))
    import pandas as _pd
    from modules.perf_report import perf_stats, quantstats_html, returns_from_trades
    _up = st.file_uploader(L("Journal CSV (columns: time, r)"), type=["csv"], key="perf_csv")
    _risk = st.number_input(L("Risk per trade (% of account)"), min_value=0.1, max_value=10.0, value=1.0, step=0.1, key="perf_risk")
    if _up is not None:
        try:
            _jdf = _pd.read_csv(_up)
            render_kpi_strip(_jdf)
            _stats_journal_kpis(_jdf)
            _ret = returns_from_trades(_jdf, float(_risk))
            if len(_ret) < 5:
                st.warning(L("Need at least 5 closed trades for meaningful statistics."))
            else:
                _st = perf_stats(_ret)
                _c = st.columns(4)
                _c[0].metric(L("Trades"), _st["n"]); _c[1].metric(L("Total return"), f"{_st['total_return']*100:.1f}%")
                _c[2].metric(L("Max drawdown"), f"{_st['max_drawdown']*100:.1f}%"); _c[3].metric(L("Win rate"), f"{_st['win_rate']*100:.0f}%")
                _c = st.columns(3)
                _c[0].metric("Sharpe", f"{_st['sharpe']:.2f}"); _c[1].metric("Sortino", f"{_st['sortino']:.2f}"); _c[2].metric(L("Stats source"), _st["source"])
                st.line_chart((1 + _ret).cumprod().rename("equity"))
                from modules.mc_journal import mc_summary as _mc_summary
                with st.expander(_xl("فحص الحظ — Monte Carlo على صفقاتك الحقيقية", "Luck check - Monte Carlo on your real trades"), expanded=False):
                    _dd = st.slider(_xl("حد الخسارة الكاملة (هبوط من القمة %)", "Ruin threshold (drop from peak %)"), 10, 50, 20, 5, key="mc_ruin") / 100
                    _mc = _mc_summary(_ret.values, ruin_dd=_dd, seed=7)
                    if _mc.get("ok"):
                        _m = st.columns(4)
                        _m[0].metric(_xl("P-value (المتوسط > 0)", "P-value (mean > 0)"), f"{_mc['p_value']:.3f}")
                        _m[1].metric(_xl("احتمال الخسارة الكاملة", "Ruin probability"), f"{_mc['ruin']*100:.1f}%")
                        _m[2].metric(_xl("نطاق النهاية 5% / 95%", "Final range 5% / 95%"), f"{_mc['final_p5']:.2f}x / {_mc['final_p95']:.2f}x")
                        _m[3].metric(_xl("عدد الصفقات", "Trades"), _mc["n"])
                        _msg = {"not_evidence": _xl("أقل من 30 صفقة = مش دليل.", "Under 30 trades = NOT evidence."),
                                "could_be_luck": _xl("النتيجة ممكن تكون حظ (P-value مش صغير).", "The result could be luck (p-value is not small)."),
                                "unlikely_luck": _xl("المتوسط مش غالبًا حظ على العينة دي، بس ده مش إثبات حافة مستقبلية.", "The average is unlikely to be luck in this sample, but it does not prove a future edge.")}[_mc["verdict"]]
                        (st.warning if _mc["verdict"] != "unlikely_luck" else st.info)(_msg)
                        st.caption(_xl("إعادة سحب صفقاتك الفعلية (5000 مسار بنفس عدد الصفقات)؛ P-value من اختبار bootstrap بخط مقارنة صفري المتوسط. وصف للماضي، مش توقع ولا نصيحة.",
                                       "Resamples your actual trades (5000 runs of the same number of trades); the p-value is a bootstrap test against the same trades with zero mean. A description of the past, not a forecast or advice."))
                _html = quantstats_html(_ret)
                if _html:
                    st.iframe(_html, height=900, alt="QuantStats performance report")
                else:
                    st.info(L("QuantStats is not installed here, so only the built-in statistics are shown."))
        except Exception as _e:
            st.error(f"Could not read the file: {type(_e).__name__}: {_e}")
