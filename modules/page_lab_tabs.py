"""Technical Office tabs: backtest agent, scanner, detector, lab tables. Split from page_lab.py (M7, 500-line rule)."""
import html
import json
from pathlib import Path

import streamlit as st

from modules.i18n import L, lang as _ui_lang
from modules.page_kit import md_sections as _md_sections
from modules.page_radar_filters import _strat_name
from modules.page_radar_data import _CS_TFS


def _bt_agent(sym, tf):
    """Backtest agent (owner 2026-10-22): explain the idea in words, the agent turns it into rules, the dashboard tests them."""
    from modules import strategy_agent as A, strategy_rules as SR
    from modules import ai_provider as AP
    st.markdown(f"**{L('Explain your idea to the backtest agent')}**")
    hist = st.session_state.setdefault("bt_agent_hist", [])
    for h in hist[-6:]:
        with st.chat_message("user"):
            st.write(h["q"])
        with st.chat_message("assistant"):
            st.write(h["a"])
    prov, key = AP.pick()
    if not key:
        st.info(L("The agent needs a ChatGPT key (OPENAI_API_KEY) or the free Gemini key (GEMINI_API_KEY) in Streamlit secrets. Until then, build the rules by hand in Technical Office > Backtest."))
        return
    st.caption(L("Answered by") + (" ChatGPT" if prov == "openai" else " Gemini"))
    q = st.text_area(L("Your idea"), key="bt_agent_q", placeholder=L("e.g. buy when RSI 14 is under 30 and the close is above the 200 EMA, on the daily chart"))
    c = st.columns([1, 1, 4])
    if c[0].button(L("Ask the agent"), key="bt_agent_go") and q.strip():
        try:
            ans = A.ask(q.strip(), hist, key, provider=prov)
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")
            return
        hist.append({"q": q.strip(), "a": ans.get("reply", "")}); st.session_state["bt_agent_last"] = ans
    if c[1].button(L("New conversation"), key="bt_agent_reset"):
        st.session_state["bt_agent_hist"] = []; st.session_state.pop("bt_agent_last", None)
    ans = st.session_state.get("bt_agent_last")
    if not ans:
        return
    if ans.get("questions"):
        st.markdown("**" + L("The agent asks") + ":** " + " · ".join(ans["questions"]))
    if ans.get("assumptions"):
        st.caption(L("Assumptions / not testable here") + ": " + " · ".join(ans["assumptions"]))
    st.code(SR.to_json(ans["strategy"]) if not ans["errors"] else json.dumps(ans["strategy"], ensure_ascii=False, indent=1), language="json")
    if ans["errors"]:
        from modules import office_ui as _OU
        st.warning(" · ".join(_OU.rule_error(x, _ui_lang() == "ar") for x in ans["errors"]))
        return
    b = st.columns([1.4, 1, 3])
    if b[0].button(L("Test the agent's rules"), type="primary", key="bt_agent_run"):
        _bt_run_show(ans["strategy"], sym, tf)
    if b[1].button(L("Save rule"), key="bt_agent_save"):
        SR.SessionStore(st.session_state).save(ans["strategy"]); st.success(L("Saved for this session"))


def _bt_run_show(strat, sym, tf):
    """Run one strategy on real candles and show the verdict (out-of-sample), metrics, split and equity curve."""
    from modules import strategy_rules as SR, strategy_bt as BT
    from modules import office_ui as _OU  # noqa: F401 (side effect / kept on purpose)  # also registers the Arabic for the backtest note and chart labels
    from modules.market_cache import get_klines
    side = strat["side"]
    try:
        df = get_klines(sym.strip(), tf, 1000)
        res = BT.run(df, SR.evaluate(strat, df), side=side)
    except Exception as e:
        st.error(f"{type(e).__name__}: {e}")
        return
    ev = res.get("evidence") or {}; ins = res.get("in_sample") or {}
    m = st.columns(5)
    m[0].metric(L("Out-of-sample trades"), res.get("n", 0))
    m[1].metric(L("net avg R"), "-" if not res.get("n") else f"{res['net_expectancy_r']:+.3f}")
    m[2].metric(L("Win rate"), "-" if not res.get("n") else f"{res['win_rate'] * 100:.0f}%")
    m[3].metric(L("Verdict"), L(ev.get("badge", "not evidence")))
    m[4].metric(L("In-sample (info)"), f"{ins.get('n', 0)} · " + ("-" if not ins.get("n") else f"{ins['net_expectancy_r']:+.3f}R"))
    sp = res.get("split") or {}
    st.caption(L("Split frozen before any trade") + f": {L('in-sample')} {sp.get('in_sample_bars')} / {L('out-of-sample')} {sp.get('out_of_sample_bars')} " + L("candles")
               + f" · {len(df)} " + L("candles") + " " + L("loaded (the dashboard fetch is capped; long histories run in GitHub Actions)") + " · " + L(res.get("note", "")))
    seq = [("in-sample", v) for v in ins.get("net_r", [])] + [("out-of-sample", v) for v in res.get("net_r", [])]
    if seq:   # equity curve in R after costs: in-sample first (information), then the out-of-sample part the verdict uses
        import altair as alt
        import pandas as _pd
        _cp, _cr, _ct, _cc = L("part"), L("net R"), L("trade"), L("cumulative net R")   # column names shown in the chart and its tooltip
        eq = _pd.DataFrame([(L(p_), v) for p_, v in seq], columns=[_cp, _cr]); eq[_ct] = range(1, len(eq) + 1); eq[_cc] = eq[_cr].cumsum()
        st.altair_chart(alt.Chart(eq).mark_line(point=True).encode(x=alt.X(f"{_ct}:Q"), y=alt.Y(f"{_cc}:Q"),
                        color=alt.Color(f"{_cp}:N", scale=alt.Scale(domain=[L("in-sample"), L("out-of-sample")], range=["#93c5fd", "#2dd4bf"])),
                        tooltip=[_ct, _cp, _cr, _cc]).properties(height=240), width="stretch")


_RULE_IND = {"close": ("Close", "الإغلاق"), "open": ("Open", "الافتتاح"), "high": ("High", "القمة"), "low": ("Low", "القاع"), "volume": ("Volume", "الفوليوم"),
             "sma": ("SMA", "متوسط بسيط SMA"), "ema": ("EMA", "متوسط أسي EMA"), "rsi": ("RSI", "RSI"), "atr": ("ATR", "ATR (المدى)"), "roc": ("ROC", "معدل التغير ROC"),
             "hh": ("Highest high", "أعلى قمة"), "ll": ("Lowest low", "أقل قاع"), "macd_hist": ("MACD histogram", "هيستوجرام MACD"), "adx": ("ADX", "ADX (قوة الترند)"), "bbw": ("Bollinger width", "عرض بولينجر")}


_RULE_OPS = {">": ("above", "أكبر من"), ">=": ("at least", "أكبر من أو يساوي"), "<": ("below", "أصغر من"), "<=": ("at most", "أصغر من أو يساوي"),
             "crosses_above": ("crosses above", "يقطع لفوق"), "crosses_below": ("crosses below", "يقطع لتحت")}


def _rl(table):
    """format_func for the rule builder: readable names (Arabic when the page is Arabic) instead of the raw code names."""
    ar = _ui_lang() == "ar"
    return lambda k: (table.get(k, (k, k))[1 if ar else 0])


def _office_backtest():
    """Build a strategy (rules) and backtest it on real candles: verdict on the frozen out-of-sample part only."""
    from modules import strategy_rules as SR, strategy_bt as BT  # noqa: F401
    st.caption(L("Rules are kept for this session only (owner decision 2026-10-22). Small runs here; big runs go to GitHub Actions with the owner's approval. No orders, ever."))
    store = SR.SessionStore(st.session_state)
    c = st.columns([1.2, 0.8, 0.8, 0.8, 1])
    sym = c[0].text_input(L("Symbol"), "BTC-USDT", key="bt_sym")
    tf = c[1].selectbox(L("Timeframe"), ["1h", "4h", "1d"], index=2, key="bt_tf")   # the labels the data feeds use (see _CS_TFS)
    side = c[2].selectbox(L("Side"), list(SR.SIDES), format_func=L, key="bt_side")
    logic = c[3].selectbox(L("Logic"), list(SR.LOGIC), key="bt_logic")
    name = c[4].text_input(L("Name"), "my rule", key="bt_name")
    _bt_agent(sym, tf)
    st.markdown(f"**{L('Or build the rules by hand')}**")
    inds = list(SR.INDICATORS)
    rules = []
    for i in range(int(st.number_input(L("Rules"), 1, 6, 1, key="bt_nr"))):
        r = st.columns([1, 0.6, 1, 1, 0.6])
        ind = r[0].selectbox(L("Indicator") + f" {i + 1}", inds, index=inds.index("close") if i == 0 else inds.index("rsi"), key=f"bt_i{i}", format_func=_rl(_RULE_IND))
        per = r[1].number_input(L("Period"), 2, 500, 14 if i == 0 else 20, key=f"bt_p{i}") if SR.INDICATORS[ind] else None
        op = r[2].selectbox(L("Condition"), list(SR.OPS), index=SR.OPS.index("crosses_above") if i == 0 else SR.OPS.index("<"), key=f"bt_o{i}", format_func=_rl(_RULE_OPS))
        vk = r[3].selectbox(L("Compare with"), [L("number")] + inds, index=1 + inds.index("ema") if i == 0 else 0, key=f"bt_vk{i}", format_func=lambda k: k if k == L("number") else _rl(_RULE_IND)(k))
        if vk == L("number"):
            val = float(r[4].number_input(L("Value"), value=70.0, key=f"bt_v{i}"))
        else:
            val = {"indicator": vk}
            if SR.INDICATORS[vk]:
                val["period"] = int(r[4].number_input(L("Period"), 2, 500, 50, key=f"bt_vp{i}"))
        rule = {"indicator": ind, "op": op, "value": val}
        if per is not None:
            rule["period"] = int(per)
        rules.append(rule)
    strat = {"name": name, "side": side, "logic": logic, "rules": rules}
    errs = SR.validate(strat)
    with st.expander("JSON", expanded=False):
        st.code(SR.to_json(strat) if not errs else str(strat), language="json")
    if errs:
        from modules import office_ui as _OU
        st.error(" · ".join(_OU.rule_error(x, _ui_lang() == "ar") for x in errs))
        return
    b = st.columns([1, 1, 4])
    if b[0].button(L("Save rule"), key="bt_save"):
        store.save(strat); st.success(L("Saved for this session"))
    run = b[1].button(L("Run backtest"), type="primary", key="bt_run")
    if store.names():
        st.caption(L("Saved this session") + ": " + ", ".join(store.names()))
    if run:
        _bt_run_show(strat, sym, tf)


def _office_lab():
    st.caption(L("Real OKX / Hyperliquid candles, run weekly by GitHub Actions, every result against a random-direction baseline. "
                 "Evidence bar: n >= 100 and t > 3. Under 30 trades = not evidence. Judge by the net avg R column (0.1R costs per trade taken off); avg R alone has no costs."))
    lab, flt = _md_sections("STRATEGY_LAB.md"), _md_sections("STRATEGIES.md")
    if not lab:
        st.info(L("No lab results yet - they appear after the first weekly run."))
        return
    first = [k for k in lab if k.startswith("Gann zone trades OUT OF SAMPLE")] + [k for k in lab if k.startswith("Gann time cycles")] + \
            [k for k in lab if k.startswith("Gann astro")] + [k for k in lab if k.startswith("Trend filter")]
    filt = [k for k in flt if k.startswith("Filter on/off backtest")]
    from modules import office_ui as _OU
    _la = _ui_lang() == "ar"
    for k in first[:1]:
        with st.expander(_OU.lab_title(k, _la), expanded=True):
            st.markdown(_OU.lab_md(lab[k], _la, L))
    for k in filt:
        with st.expander(L("Group-A filters ON vs OFF (item 1)"), expanded=True):
            st.markdown(_OU.lab_md(flt[k], _la, L))
    for k in first[1:]:
        with st.expander(_OU.lab_title(k, _la), expanded=False):
            st.markdown(_OU.lab_md(lab[k], _la, L))
    rest = [k for k in lab if k not in first]
    if rest:
        pick = st.selectbox(L("More tables"), rest, key="lab_more", format_func=lambda k_: _OU.lab_title(k_, _la))
        st.markdown(_OU.lab_md(lab[pick], _la, L))


# Scanner presets by trading style (Playbook > By trading style): Radar timeframe + the detectors that style uses
_SCAN_PRESETS = {
    "Scalp": {"tf": "5m", "strat": ["st_judas", "st_sweep", "st_crt", "st_ote", "st_kzs"], "mode": "Any selected"},
    "Day": {"tf": "1h", "strat": ["st_cisd", "st_rsidiv", "st_sessamd", "st_m2022"], "mode": "Any selected"},
    "Swing": {"tf": "1d", "strat": ["st_tl", "st_macddiv", "st_bvd", "st_donch"], "mode": "Any selected"},
    "Position": {"tf": "1w", "strat": ["st_turtle55", "st_sma1040", "st_donch"], "mode": "Any selected"},
}


def _office_scanner():
    """Technical Office > Scanner control (owner 2026-10-22: control the scanner from the office). Sets the Radar's
    timeframe, chart count, match mode, side and detectors for this session, by trading style or by hand, and shows the
    lab's number for every chosen detector on that timeframe before you open the Radar."""
    from modules import office_kpi as _OK, office_ui as U
    from modules.chart_scan import STRATEGY_FILTERS as _SF
    st.markdown(U.CSS, unsafe_allow_html=True)
    cur = st.session_state.get("radar_def", {})
    style = st.segmented_control(L("Preset by trading style"), ["Manual"] + list(_SCAN_PRESETS), default="Manual", format_func=L, key="sc_style")
    p = _SCAN_PRESETS.get(style or "Manual", {})
    c = st.columns(4)
    tf = c[0].selectbox(L("Timeframe"), _CS_TFS, index=_CS_TFS.index(p.get("tf") or cur.get("tf") or "1h"), key=f"sc_tf_{style}")
    n = c[1].number_input(L("Charts"), 1, 120, int(cur.get("n", 20)), key="sc_n")
    modes = ["All selected", "Any selected"]
    mode = c[2].selectbox(L("Match"), modes, index=modes.index(p.get("mode") or cur.get("mode") or "All selected"), format_func=L, key=f"sc_mode_{style}")
    sides = ["Both", "Buy only", "Sell only"]
    side = c[3].selectbox(L("Side"), sides, index=sides.index(cur.get("side", "Both")), format_func=L, key="sc_side")
    strat = st.multiselect(L("Detectors"), list(_SF), default=p.get("strat") or cur.get("strat", []), format_func=_strat_name, key=f"sc_strat_{style}")
    lab = _OK.load()
    rows, weak = [], []
    for k in strat:
        ev = _OK.evidence(lab, _SF[k][1][1], tf) if _SF[k][1][0] == "key" else None
        if ev and ev["net"] <= 0:
            weak.append(_strat_name(k))
        rows.append([U.esc(_strat_name(k)), U.esc(ev["tf"]) if ev else "-", ev["n"] if ev else "-", f"{ev['net']:+.3f}" if ev else "-",
                     U.badge(L("OFF") if ev and ev["off"] else L("passed") if ev and ev["gate"] else L("not evidence") if ev else L("no lab row"),
                             "bad" if ev and (ev["off"] or ev["net"] <= 0) else "ok" if ev and ev["gate"] else "warn")])
    if rows:
        st.markdown(f"<div class='xo-h'>{html.escape(L('What the lab says about these detectors on this timeframe'))}</div>", unsafe_allow_html=True)
        st.markdown(U.table([L("Detector"), L("Lab timeframe"), "n", L("net"), L("Gate")], rows), unsafe_allow_html=True)
        if weak:
            st.warning(L("Negative after costs on the lab's numbers:") + " " + ", ".join(weak))
    a, b = st.columns([1, 3])
    if a.button(L("Apply to the Radar"), type="primary", key="sc_apply"):
        st.session_state["radar_def"] = {"tf": tf, "n": int(n), "mode": mode, "side": side, "strat": strat}
        for k_ in ("cs_tf", "cs_n", "cs_mode", "cs_side"):
            st.session_state.pop(k_, None)
        st.session_state["cs_strat"] = list(strat)
        st.query_params["strat"] = ",".join(strat) if strat else ""
        b.success(L("Saved for this session. Open the Radar page to see it."))
    if cur:
        st.caption(L("Radar now") + f": {cur.get('tf')} · {cur.get('n')} {L('charts')} · {L(cur.get('mode', ''))} · {L(cur.get('side', ''))} · "
                   + (", ".join(_strat_name(k) for k in cur.get("strat", []) if k in _SF) or "-"))


def _office_detector():
    """Technical Office > Detector analysis: one detector's full lab card - every timeframe and side, best timeframe,
    vs random, gate, OFF, and which trading style it fits; bars of net R per timeframe."""
    import altair as alt
    import pandas as _pd
    from modules import office_kpi as _OK, office_ui as U
    st.markdown(U.CSS, unsafe_allow_html=True)
    lab = _OK.load()
    keys = _OK.detector_keys(lab)
    if not keys:
        st.info(L("No lab file yet (data/strategy_lab.json)."))
        return
    k = st.selectbox(L("Detector"), keys, index=keys.index("liqline") if "liqline" in keys else 0, key="det_key")
    c = _OK.detector_card(lab, k)
    b, a = c["best"] or {}, c["all"] or {}
    st.markdown("<div class='xo-row'>" + U.indicators(f"{k} · {L(c['school'] or '-')}", [
        (L("All timeframes"), f"{a.get('net', 0):+.3f}R" if a else "-", f"n {a.get('n', '-')} · " + L("net"), "bad" if a and a["net"] <= 0 else "ok" if a else None),
        (L("Best timeframe"), f"{b.get('tf', '-')}", f"{L('net')} {b['net']:+.3f}R · n {b['n']}" if b else "", "ok" if b and b["net"] > 0 else "bad" if b else None),
        (L("vs random"), f"{b['vs_random']:+.3f}" if b else "-", L("best timeframe minus random entries"), "ok" if b and b["vs_random"] > 0 else "warn" if b else None),
        (L("Status"), L("OFF") if c["off"] else L("passed") if b and b.get("gate") else L("not evidence"),
         L("n >= 300 and avg R <= -0.06") if c["off"] else (L("n under 100 on the best timeframe") if not c["best_is_evidence_size"] else L("needs t > 3 and both halves positive")),
         "bad" if c["off"] else "ok" if b and b.get("gate") else "warn"),
        (L("Trading styles"), " · ".join(L(s) for s in c["styles"]) or "-", L("from the timeframes it was tested on"), None)]) + "</div>", unsafe_allow_html=True)
    try:   # a frozen holdout on older candles, when one was run for this detector (modules/lab_holdout.py)
        import json as _json
        ho = _json.loads((Path(__file__).resolve().parent.parent / "data" / f"holdout_{k}_1d.json").read_text(encoding="utf-8"))
        hr = ho["result"]
        st.markdown(f"<div class='xo-h' style='margin-top:6px'>{html.escape(L('Frozen holdout on older candles (1d)'))}</div>", unsafe_allow_html=True)
        st.markdown("<div class='xo-row'>" + U.indicators(L("Holdout") + f" · {len(ho['per_symbol'])} " + L("symbols"), [
            ("n", hr["n"], L("signals"), None),
            (L("net avg R"), f"{hr['net_avgR']:+.3f}", L("gross") + f" {hr['gross_avgR']:+.3f}", "ok" if hr["net_avgR"] > 0 else "bad"),
            (L("Random entries"), f"{hr['random_avgR']:+.3f}", L("gross avg R of random direction on the same bars"), "warn"),
            ("t", f"{hr['t_vs_random']}", L("vs random; the bar is 3"), "bad" if hr["t_vs_random"] <= 3 else "ok"),
            (L("Halves"), f"{hr['h1']['net_avgR']:+.3f} / {hr['h2']['net_avgR']:+.3f}", L("net, first / second half"), None),
            (L("Verdict"), L("passed") if hr["pass"] else L("not evidence"), L("rule frozen before the run"), "ok" if hr["pass"] else "warn")]) + "</div>", unsafe_allow_html=True)
    except (OSError, ValueError, KeyError):
        pass
    df = _pd.DataFrame(c["rows"])
    if df.empty:
        return
    per = df[(df["side"] == "all") & (df["tf"] != "all")]
    if len(per):
        order = [t for t in ("1m", "15m", "1h", "4h", "1d") if t in set(per["tf"])]
        st.altair_chart(alt.Chart(per).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("tf:N", sort=order, title=None), y=alt.Y("net:Q", title=L("net") + " R"),
            color=alt.condition("datum.net > 0", alt.value("#2dd4bf"), alt.value("#f87171")), tooltip=["tf", "n", "net", "vs_random"]
        ).properties(height=200), width="stretch")
    df = df.assign(win=df["win"].map(lambda w: None if w is None else f"{w:.0f}%"), gate=df["gate"].map(lambda g: L("passed") if g else "-"),
                   side=df["side"].map(L), tf=df["tf"].map(L))
    st.dataframe(df.rename(columns={"tf": L("Timeframe"), "side": L("Side"), "win": L("Win rate"), "avgR": L("avg R"), "net": L("net"), "vs_random": L("vs random"), "gate": L("Gate")}),
                 hide_index=True, width="stretch")
    st.caption(L("All numbers from the weekly lab file; net = avg R - 0.1R. Educational, not investment advice."))
