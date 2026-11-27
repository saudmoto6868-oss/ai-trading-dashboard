"""Technical Office flow lab, manual flow and strategy map. Split from page_lab.py (M7, 500-line rule)."""
import html

import streamlit as st

from modules.i18n import L, lang as _ui_lang
from modules.page_lab_tabs import _bt_run_show


def _flow_zone_section():
    """Flow lab > confluence-zone forward test: judge the zone log exported from the Workspace (menu 'Export zone test log')."""
    import json as _json
    from modules import zone_eval as ZE, office_ui as U
    st.markdown(f"<div class='xo-h'>{html.escape(L('Confluence zones: forward test'))}</div>", unsafe_allow_html=True)
    st.caption(L("The Workspace logs every confluence zone and follows the price; a zone 'holds' when price, after touching it, moves 6 bp back to where it came from before moving 6 bp through it. Every zone has a control level (the mirror price) tracked the same way. Export from the chart's indicator menu: 'Export zone test log'."))
    ups = st.file_uploader(L("Zone test logs (.json, one per symbol)"), type=["json"], accept_multiple_files=True, key="zl_up")
    if not ups:
        return
    try:
        recs = ZE.load([_json.loads(u.getvalue().decode("utf-8", "ignore")) for u in ups])
    except (ValueError, AttributeError) as e:
        st.error(f"{type(e).__name__}: {e}")
        return
    j = ZE.judge(recs)
    st.markdown("<div class='xo-row'>" + U.indicators(L("Zones"), [
        (L("Zones logged"), j["zones"], f"{L('touched')} {j['zone_touched']}", None),
        (L("Zones held / broke"), f"{j['zone_hold']} / {j['zone_break']}", L("after touching"), None),
        (L("Control held / broke"), f"{j['ctrl_hold']} / {j['ctrl_break']}", L("mirror level, same rule"), None),
        (L("Paired zones"), j["paired"], L("both resolved; the gate needs 100"), "warn" if j["paired"] < ZE.GATE_N else None),
        (L("Zone minus control"), "-" if j["diff"] is None else f"{j['diff']:+.3f}", f"t {j['t']} · " + L("halves") + f" {j['half1']} / {j['half2']}", "ok" if j["pass"] else "warn"),
        (L("Verdict"), L("passed") if j["pass"] else L("not evidence"), L("t > 3, both halves positive, n >= 100"), "ok" if j["pass"] else "warn")]) + "</div>", unsafe_allow_html=True)
    if j["by_strength"]:
        st.markdown(U.table([L("Sources agreeing"), L("Paired zones"), L("Zone minus control")], [[k, v["n"], "-" if v["diff"] is None else f"{v['diff']:+.3f}"] for k, v in j["by_strength"].items()]), unsafe_allow_html=True)
    st.divider()


def _office_flow_lab():
    """Technical Office > Flow lab: the forward-test judge for order-flow signals (modules/flow_log.py). Reads the collector's log
    (or an uploaded one), fills the forward returns, tests the frozen rules after costs against a random-sign control, and applies
    the lab's gate. Nothing here is a trade signal; a rule only earns trust by passing."""
    import json as _json
    import pandas as _pd
    from modules import flow_log as FL, office_ui as U
    st.markdown(U.CSS, unsafe_allow_html=True)
    if _ui_lang() == "ar":
        st.markdown("<div class='xo-card' dir='rtl' style='line-height:25px'><b>الفكرة:</b> الدفتر والشريط ما لهمش تاريخ طويل نختبر عليه، فبنختبرهم <b>للأمام</b>: "
                    "الـ collector بيسجل كل ثواني مؤشرات الدفتر والشريط، والحكم بيقيس عائد السعر بعدها بـ 5 ثواني و30 ثانية و5 دقايق وساعة، "
                    "بقواعد مجمدة، بعد التكلفة، ومقارنة بإشارة عشوائية. القاعدة تعدّي بس لو <b>n ≥ 100 ، t > 3 ، والنصين موجبين</b>.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='xo-card' dir='ltr' style='line-height:25px'><b>The idea:</b> the order book and the tape have no long history to test on, so they are tested <b>forward</b>: "
                    "the collector records the book and tape indicators every few seconds, and the judge measures the price return 5 seconds, 30 seconds, 5 minutes and one hour later, "
                    "with frozen rules, after costs, and against a random-sign control. A rule passes only if <b>n ≥ 100, t > 3 and both halves are positive</b>.</div>", unsafe_allow_html=True)
    _flow_zone_section()
    up = st.file_uploader(L("Flow log (.jsonl)"), type=["jsonl", "json", "txt"], key="fl_up")
    rows = []
    if up is not None:
        for ln in up.getvalue().decode("utf-8", "ignore").splitlines():
            try:
                r_ = _json.loads(ln)
            except ValueError:
                continue
            if isinstance(r_, dict) and all(k in r_ for k in ("sym", "t", "mid")):   # a row without these cannot be labelled
                rows.append(r_)
        rows.sort(key=lambda r: (r["sym"], r["t"]))
        src = up.name
    else:
        rows = FL.load(); src = str(FL.PATH)
    c = st.columns([1, 1, 2])
    cost = c[0].number_input(L("Cost per trade (bps)"), 0.0, 100.0, float(FL.COST_BPS), 1.0, key="fl_cost",
                             help=L("Taker fee both ways + half spread + slippage; a planning number. 10 bps = 0.10%"))
    secs = c[1].selectbox(L("Collect now (seconds)"), [0, 60, 120, 300], format_func=lambda x: "-" if not x else str(x), key="fl_secs")
    if secs and c[2].button(L("Collect BTC / ETH / SOL now") + f" ({secs} s)", key="fl_go"):
        with st.spinner(L("Collecting from OKX ...")):
            n = FL.collect(["BTC-USDT", "ETH-USDT", "SOL-USDT"], int(secs), 2.0)
        st.success(f"{n} " + L("rows added"))
        rows = FL.load()
    if not rows:
        st.info(L("No log yet. Collect from the button above, or run: python modules/flow_log.py collect BTC-USDT,ETH-USDT,SOL-USDT 3600 2"))
        return
    j = FL.judge(rows, float(cost))
    st.markdown("<div class='xo-row'>" + U.indicators(L("Log") + f" · {src}", [
        (L("Rows"), f"{j['rows']:,}", ", ".join(j["symbols"]), None),
        (L("Hours covered"), f"{j['hours']}", L("a few hours is a pipeline test, not evidence"), "warn" if j["hours"] < 24 else "ok"),
        (L("Rules x horizons tried"), j["trials"], L("every variant counts as a trial; t > 3 is the bar"), None),
        (L("Passed the gate"), len(j["passed"]), L("n >= 100, t > 3, both halves positive, after cost"), "ok" if j["passed"] else "bad")]) + "</div>", unsafe_allow_html=True)
    df = _pd.DataFrame([r for r in j["results"] if r["n"]])
    if df.empty:
        st.info(L("Not enough rows for any horizon yet."))
        return
    df["verdict"] = df["pass"].map(lambda p: L("passed") if p else L("not evidence"))
    st.dataframe(df[["rule", "horizon", "n", "gross_bps", "net_bps", "t", "control_net_bps", "half1", "half2", "verdict"]].rename(columns={
        "rule": L("Rule"), "horizon": L("Horizon (s)"), "gross_bps": L("gross bps"), "net_bps": L("net bps"), "control_net_bps": L("random-sign control"),
        "half1": L("first half"), "half2": L("second half"), "verdict": L("Verdict")}), hide_index=True, width="stretch")
    st.caption(L("Rules are frozen in modules/flow_log.py (RULES): imb = book imbalance, ofi = top-of-book order-flow imbalance, cvd = taker buy minus sell. Poll cadence limits what is seen. Educational, not investment advice."))


def _office_flow_manual():
    """Technical Office > Flow manual: chartless methods (order book, tape, funding / OI, options) - what each measures, how to read it,
    how it is used, where it breaks, the evidence, which tool shows it, the daily routine and the forward-test protocol."""
    from modules import flow_manual as _FMM, office_ui as U
    from modules.i18n import lang as _lang
    _ar = _lang() == "ar"; _dir = "rtl" if _ar else "ltr"; FM = type("FM", (), _FMM.get(_ar))
    st.markdown(U.CSS, unsafe_allow_html=True)
    st.markdown("<div class='xo-card' dir='" + _dir + "' style='line-height:26px'><b style='font-size:16px'>" + ("الخلاصة: نعتمد عليها بإيه؟" if _ar else "Bottom line: what can we rely on them for?") + "</b><br>"
                + "<br>".join("• " + x for x in FM.HEADLINE) + "</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='xo-h' style='margin-top:10px'>{html.escape(L('Tools we have and their limits'))}</div>", unsafe_allow_html=True)
    st.markdown(U.table([L("Tool"), L("Shows"), L("Where"), L("Data"), L("Limits")], [[f"<b>{U.esc(a)}</b>", U.esc(b), U.esc(c), U.esc(d), U.esc(e)] for a, b, c, d, e in FM.TOOLS]), unsafe_allow_html=True)
    st.markdown(f"<div class='xo-h' style='margin-top:10px'>{html.escape(L('Methods: how to read, how to use, where it breaks'))}</div>", unsafe_allow_html=True)
    for m in FM.METHODS:
        tt, tone = FM.TIERS[m["tier"]]
        with st.expander(m["title"] + " — " + tt.split(" · ")[0], expanded=False):
            st.markdown(f"<div dir='{_dir}' style='line-height:25px'>{U.badge(tt, tone)}<br><b>{'بيقيس:' if _ar else 'Measures:'}</b> {U.esc(m['measures'])}<br><b>{'إزاي تقراه:' if _ar else 'How to read it:'}</b><ol style='margin:4px 0'>"
                        + "".join(f"<li>{U.esc(x)}</li>" for x in m["read"]) + f"</ol><b>{'الاستخدام:' if _ar else 'How it is used:'}</b> {U.esc(m['setup'])}<br><b>{'بيفشل فين:' if _ar else 'Where it fails:'}</b> {U.esc(m['fails'])}<br>"
                        f"<b>{'الدليل:' if _ar else 'Evidence:'}</b> {U.esc(m['evidence'])}<br><b>{'الداتا عندنا:' if _ar else 'Our data:'}</b> {U.esc(m['data'])}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='xo-h' style='margin-top:10px'>{html.escape(L('Daily routine'))}</div>", unsafe_allow_html=True)
    st.markdown(U.table([L("Step"), L("What to do")], [[f"<b>{U.esc(a)}</b>", U.esc(b)] for a, b in FM.ROUTINE]), unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        st.markdown(f"<div class='xo-h'>{html.escape(L('Forward test: how a flow signal earns trust'))}</div>", unsafe_allow_html=True)
        st.markdown("<div class='xo-card' dir='" + _dir + "' style='line-height:24px'>" + "<br>".join(f"{i}. {U.esc(x)}" for i, x in enumerate(FM.FORWARD_TEST, 1)) + "</div>", unsafe_allow_html=True)
    with b:
        st.markdown(f"<div class='xo-h'>{html.escape(L('What is still missing'))}</div>", unsafe_allow_html=True)
        st.markdown("<div class='xo-card' dir='" + _dir + "' style='line-height:24px'>" + "<br>".join("• " + U.esc(x) for x in FM.MISSING) + "</div>", unsafe_allow_html=True)
    st.caption(L("Research sources are named per method (OPENED = read in full, otherwise a search snippet or background knowledge). Educational, not investment advice."))


def _office_strategy_map():
    """Technical Office > Strategy map (owner 2026-10-22): an indicator is one measurement, a strategy is parts with different jobs.
    Clusters (what repeats what), the strongest member of each from the lab, whether stacking helps, the named strategies as
    role slots with redundancy warnings, and the gaps. Every number is the weekly lab's; the explanations are guidance."""
    from modules import office_kpi as _OK, office_ui as U, strategy_map as _SM
    st.markdown(U.CSS, unsafe_allow_html=True)
    lab = _OK.load()
    from modules.i18n import lang as _lang
    _ar = _lang() == "ar"; _dir = "rtl" if _ar else "ltr"
    if _ar:
        st.markdown(
            "<div class='xo-card' dir='rtl' style='line-height:24px'><b>القاعدة:</b> المؤشر قياس واحد (RSI مثلاً)، والكاشف حدث بيظهر على شمعة (زي FVG)، "
            "والاستراتيجية مجموعة أجزاء كل جزء ليه وظيفة: <b>سياق ← إعداد ← زناد ← فلتر ← خروج ← حجم</b>. "
            "<b>جزء واحد لكل وظيفة، وجزء واحد لكل عنقود</b>: لو اتنين بيقيسوا نفس الشيء فالتاني تكرار مش تأكيد. "
            "مستوى الدليل مكتوب لكل استراتيجية بصراحة، والأرقام جاية من المعمل الأسبوعي بس.</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='xo-card' dir='ltr' style='line-height:24px'><b>The rule:</b> an indicator is one measurement (RSI, for example), a detector is an event that shows on a candle (like FVG), "
            "and a strategy is a set of parts where each part has a job: <b>context → setup → trigger → filter → exit → size</b>. "
            "<b>One part per job, and one part per cluster</b>: if two measure the same thing, the second is a repeat, not a confirmation. "
            "The evidence level is stated openly for each strategy, and the numbers come only from the weekly lab.</div>", unsafe_allow_html=True)
    # 1. clusters
    st.markdown(f"<div class='xo-h' style='margin-top:10px'>{html.escape(L('Clusters: what repeats what'))}</div>", unsafe_allow_html=True)
    rows = []
    for cl, (name, meas, rule) in _SM.clusters(_ar).items():
        mem = _SM.members(lab, cl); best = _SM.cluster_best(lab, cl)
        names = " · ".join(_SM.comp_name(m["id"], _ar) for m in mem)
        if best:
            bb = best["best"]
            rep = f"{U.esc(_SM.comp_name(best['id'], _ar))} {U.esc(bb['tf'])} · {bb['net']:+.3f}R · n {bb['n']}" + ("" if bb["net"] > 0 else f" <span style='color:#f87171'>({html.escape(L('below the cost'))})</span>")
        else:
            rep = "<span style='color:#a3adba'>" + ("مفيش عضو بـ n ≥ 100" if _ar else "No member with n ≥ 100") + "</span>"
        rows.append([f"<b>{U.esc(name)}</b>", U.esc(meas), U.esc(names), rep, U.esc(rule)])
    st.markdown(U.table([L("Cluster"), L("Measures"), L("Members"), L("Strongest member (lab, n >= 100)"), L("Redundancy rule")], rows), unsafe_allow_html=True)
    # 2. agreement between detectors + does stacking help
    a, b = st.columns(2)
    with a:
        st.markdown(f"<div class='xo-h'>{html.escape(L('Detectors that fire together (lab)'))}</div>", unsafe_allow_html=True)
        pr = [[U.esc(r["a"]), U.esc(r["b"]), r["together"], f"{100 - r['rate']:.0f}%"]
              for r in sorted(lab.get("conflicts", []), key=lambda r: r["rate"])[:12]]
        st.markdown(U.table([L("Detector"), L("Detector"), L("Bars together"), L("Same direction")], pr), unsafe_allow_html=True)
        st.caption(L("High same-direction share + many shared bars = the pair adds little to each other. About 50% = the pair is noise together."))
    with b:
        st.markdown(f"<div class='xo-h'>{html.escape(L('Does stacking more families help? (lab)'))}</div>", unsafe_allow_html=True)
        sk = _SM.stacking(lab)
        st.markdown(U.table([L("Agreeing families"), "n", L("net")], [[U.esc(k.replace("families", L("families"))), n, U.badge(f"{v:+.3f}R" + ("" if n >= _OK.GATE_N else " · n<100"), "ok" if v > 0 and n >= _OK.GATE_N else "bad" if v <= 0 else "warn")] for k, n, v in sk]), unsafe_allow_html=True)
        st.caption(L("Rows without opposing signals. More agreeing families gave no clear improvement (4+ was the worst row), and every row with n >= 100 is below zero after costs."))
    # 3. strategies
    st.markdown(f"<div class='xo-h' style='margin-top:10px'>{html.escape(L('Strategies as parts by role'))}</div>", unsafe_allow_html=True)
    names = {b["id"]: _SM.bp_text(b["id"], _ar)["name"] for b in _SM.BLUEPRINTS}
    pick = st.selectbox(L("Strategy"), list(names), format_func=names.get, key="sm_pick")
    bp = _SM.BP[pick]; bpt = _SM.bp_text(pick, _ar)
    ev_t, ev_tone = _SM.evidence(_ar)[bp["evidence"]]
    st.markdown(f"<div class='xo-row'><div class='xo-card' dir='{_dir}' style='flex:1 1 100%'><b style='font-size:16px'>{U.esc(bpt['name'])}</b> "
                f"{U.badge(L(bp['style']), 'info')} {U.badge(ev_t, ev_tone)}<div class='xo-sub' style='margin-top:6px'>{U.esc(bpt['evidence_note'])}</div></div></div>", unsafe_allow_html=True)
    prow = []
    for (role, cid, _note_ar), note in zip(bp["parts"], bpt["parts"]):
        c = _SM.component(cid); card = _OK.detector_card(lab, c["src"][1]) if c["src"][0] == "lab" and not c["src"][1].startswith("chain:") and lab else {}
        bb = card.get("best")
        prow.append([U.esc(_SM.roles(_ar)[role].split(" (")[0]), f"<b>{U.esc(_SM.comp_name(cid, _ar))}</b>", U.esc(_SM.clusters(_ar)[c["cluster"]][0]), U.esc(note),
                     f"{U.esc(bb['tf'])} {bb['net']:+.3f}R · n {bb['n']}" if bb else "<span style='color:#a3adba'>-</span>"])
    st.markdown(U.table([L("Role"), L("Part"), L("Cluster"), L("What it does here"), L("Lab (best timeframe)")], prow), unsafe_allow_html=True)
    for w in _SM.check(bp["parts"], _ar) + ([bpt["warn"]] if bpt.get("warn") else []):
        st.warning(w)
    if bp.get("lab"):
        lr = []
        for k in bp["lab"]:
            c = _OK.detector_card(lab, k)
            if c.get("best"):
                lr.append([U.esc(k), U.esc(c["best"]["tf"]), c["best"]["n"], f"{c['best']['net']:+.3f}", f"{c['best']['vs_random']:+.3f}",
                           U.badge(L("OFF") if c["off"] else L("passed") if c["best"]["gate"] else L("not evidence"), "bad" if c["off"] else "ok" if c["best"]["gate"] else "warn")])
        if lr:
            st.markdown(U.table([L("Detector"), L("Timeframe"), "n", L("net"), L("vs random"), L("Gate")], lr), unsafe_allow_html=True)
    if bp.get("rules"):
        c1 = st.columns([1.2, 0.8, 3])
        sym = c1[0].text_input(L("Symbol"), "BTC-USDT", key=f"sm_sym_{pick}")
        tfs = ["1h", "4h", "1d"]
        tf = c1[1].selectbox(L("Timeframe"), tfs, index=tfs.index(bp.get("tf", "1d")), key=f"sm_tf_{pick}")
        with st.expander("JSON", expanded=False):
            from modules import strategy_rules as _SR
            st.code(_SR.to_json(bp["rules"]), language="json")
        if st.button(L("Try it on real candles"), type="primary", key=f"sm_run_{pick}"):
            _bt_run_show(bp["rules"], sym, tf)
        st.caption(L("Exploratory run: every variant you try counts as another trial. A real verdict needs a frozen out-of-sample window recorded in the meeting room before the run. Exit here = the engine's standard ATR stop and 1.5R target."))
    else:
        st.info(bpt.get("needs") or "")
    # 4. gaps
    gp = _SM.gaps(lab, _ar)
    if gp:
        st.markdown(f"<div class='xo-h' style='margin-top:10px'>{html.escape(L('Gaps: where the dashboard is thin'))}</div>", unsafe_allow_html=True)
        st.markdown(U.table([L("Cluster"), L("Gap")], [[U.esc(n), U.esc(t)] for n, t in gp]), unsafe_allow_html=True)
    st.caption(L("Taxonomy from practitioner and academic sources (labelled per strategy); numbers from data/strategy_lab.json. Educational, not investment advice."))
