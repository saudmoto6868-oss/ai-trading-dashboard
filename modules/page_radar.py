"""Radar page (index 1): chart scanner, screener, compare, signals, day plan and SMT board. Moved from main.py (maintenance plan M7).
Per-session values (theme, symbols, asset class) come from rt(), never from module globals: this module is shared by every session."""
import html
import json
import os
import time

import pandas as pd
import streamlit as st

from modules.i18n import L, lang as _ui_lang
from modules.page_kit import xl as _xl, rt
from modules.page_bg import _bg, _smt_events
from modules.risk_engine import build_trade_plan
from config import CRYPTO_SYMBOLS
from modules.asset_classes import MARKET_TYPES
from modules.context_feeds import calendar_rows as _calendar_rows
from modules.dom_panel import fmt_price
from modules.page_radar_data import _CX, _LADDER, _PT_IND, _PT_ORDER, _PT_SR, _TREND_AR, _TREND_EN, _cs_result, _htf_trend, _radar_data, _radar_hits, _radar_pass
from modules.market_map_view import render_market_map
from modules.page_radar_filters import _radar_filters
from modules.page_radar_views import render_day_plan, render_radar_corr, render_radar_perf, render_radar_screener, render_radar_signals, render_radar_similar, render_smt_board


def _radar_state(tf, data):
    """Radar strip (design board 'Radar'): daily market state, strong news in the next hour, data age. Never blocks the page."""
    out = {"regime": "-", "regime_sub": "", "news": "", "age": "-"}
    try:
        tr = list(_htf_trend(tuple(rt().SCAN_SYMBOLS), "1d").values())   # candles + EMA 20/50 only (the old full daily scan doubled the first load)
        if tr:
            up, dn = tr.count("up"), tr.count("down")
            out["regime"] = "trend up" if up >= 0.6 * len(tr) else "trend down" if dn >= 0.6 * len(tr) else "range / mixed"
            out["regime_sub"] = f"↑{up} ↓{dn} / {len(tr)}"
            out.update({"up": up, "dn": dn, "n": len(tr)})
    except Exception:
        pass
    now = time.time() * 1000
    cal = _bg("cal", _calendar_rows, [])
    hi = [e for e in cal or [] if e.get("impact") == "High" and 0 <= e["ts"] - now <= 3600_000]
    out["news"] = ", ".join(f"{e['country']} {e['title']}" for e in hi[:2])[:60]
    ts = [d.get("t") for d in data.values() if d.get("t")]
    if ts:
        s = int(time.time() - min(ts))
        out["age"] = f"{s} s" if s < 120 else f"{s // 60} min"
    return out


def _trade_card(sym, tf, want=None):
    """Task 17 trade card for a confirmed chart: side, entry, stop and 3 targets from the dashboard's own rule
    (risk_engine.build_trade_plan on the scanner result: stop behind the nearest support / resistance). Never an order.
    -> (one short line shown under the chart, the full card for the hover panel)."""
    try:
        r = _cs_result(sym, tf)
    except Exception:
        r = None
    if not r or r.get("direction") not in ("bullish", "bearish"):
        t = html.escape(L("Trade card: no clear direction on this timeframe"))
        return f"<div style='font-size:10px;color:#848e9c'>{t}</div>", t
    p = build_trade_plan({**r, "trend_bias": r["direction"]})
    long_ = p["direction"] == "Long"
    against = want and want != ("buy" if long_ else "sell")
    col = "#0ecb81" if long_ else "#f6465d"
    rd = p["risk_distance"] or 1e-12
    side = f"<b style='color:{col}'>{html.escape(L('Buy') if long_ else L('Sell'))}</b>"
    tps = " / ".join(f"{fmt_price(t)} ({abs(t - p['entry']) / rd:.1f}R)" for t in p["take_profits"])
    short = (f"<div style='font-size:10.5px;margin-top:2px'>{side} · {html.escape(L('entry'))} {fmt_price(p['entry'])} · "
             f"{html.escape(L('stop'))} {fmt_price(p['stop_loss'])}" + (" · <span style='color:#f0b429'>⚠</span>" if against else "") + "</div>")
    full = (f"{side} · {html.escape(L('entry'))} {fmt_price(p['entry'])} · {html.escape(L('stop'))} {fmt_price(p['stop_loss'])} "
            f"({p['risk_distance'] / p['entry'] * 100:.2f}%)<br>{html.escape(L('targets'))} {tps}"
            + (f"<br><span style='color:#f0b429'>{html.escape(L('Against the side filter'))}</span>" if against else "")
            + f"<br><span style='color:#848e9c'>{html.escape(L('Suggestion from the rules, not an order; size by your risk per trade.'))}</span>")
    return short, full


def _hover_panel(sym, tf, d, ladder, card_full=""):
    """The text that opens when the mouse is on a Radar chart: timeframe ladder, chart patterns, candles, EMAs, signals,
    lab evidence and the trade card - plain language in the page language (Arabic or English), so the tile itself stays clean (owner 2026-10-22)."""
    from modules.chart_scan import ALL_FILTERS as _AF
    ar_ = _ui_lang() == "ar"
    ex = d.get("explain") or {}
    ex = ex.get("ar" if ar_ else "en", ex if "patterns" in ex else {})   # cached as both languages; an older flat dict is used as is
    e = html.escape
    parts = []
    lad = [(t, ladder.get(t, {}).get(sym)) for t in _LADDER.get(tf, ())] + [(tf, d.get("trend"))]
    trs = [x for _t, x in lad if x]
    agree = len(trs) > 1 and len(set(trs)) == 1 and trs[0] != "mixed"
    parts.append(_xl("<b>تدرج الفريمات (من الأكبر):</b> ", "<b>Timeframe ladder (largest first):</b> ") + " ← ".join(f"{t}: {(_TREND_AR if ar_ else _TREND_EN).get(x, '-')}" for t, x in lad)
                 + ((_xl("<br><span style='color:#5eead4'>الفريمات متفقة: الدخول مع الاتجاه أقوى.</span>", "<br><span style='color:#5eead4'>The timeframes agree: an entry with the trend is stronger.</span>")) if agree else
                    _xl("<br><span style='color:#f0b429'>الفريمات مش متفقة: الفريم الأكبر هو اللي يحكم، والصغير للتوقيت بس.</span>",
                        "<br><span style='color:#f0b429'>The timeframes disagree: the larger one decides, the smaller one is for timing only.</span>") if len(set(trs)) > 1 else ""))
    for name, psy, conf in ex.get("patterns", []):
        parts.append(f"<b>{_xl('نموذج الشارت', 'Chart pattern')}: {e(name)}</b><br>{e(psy)}<br><span style='color:#a3adba'>{_xl('التأكيد', 'Confirmation')}: {e(conf)}</span>")
    for name, psy, bias in ex.get("candles", []):
        c = "#0ecb81" if bias == "buy" else "#f6465d" if bias == "sell" else "#a3adba"
        parts.append(f"<b style='color:{c}'>{_xl('الشمعة', 'Candle')}: {e(name)}</b><br>{e(psy)}")
    if ex.get("ema"):
        parts.append(_xl("<b>المتوسطات:</b><br>", "<b>Moving averages:</b><br>") + "<br>".join(e(x) for x in ex["ema"]))
    sig = [_CX.flag_name(k, L(_AF[k])) for k in d["flags"]   # EMA position / stacks are in the EMA block, patterns above
           if k in _AF and not k.startswith(("px_", "ma_", "cp_", "chan_", "tl_", "dbl_", "stack_", "above_all", "below_all"))]
    if sig:
        parts.append(_xl("<b>إشارات تانية:</b> ", "<b>Other signals:</b> ") + e(" · ".join(sig[:10])))
    ev = _radar_evidence(d["flags"], tf)
    if ev:
        parts.append(ev)
    if card_full:
        parts.append(_xl("<b>كارت الصفقة:</b><br>", "<b>Trade card:</b><br>") + card_full)
    parts.append("<span style='color:#848e9c'>" + _xl("النموذج والشمعة = الانحياز المعروف في الكتب، مش دليل مقاس. تعليمي، مش توصية.",
                                                     "Pattern and candle = the textbook bias, not a measured edge. Educational, not advice.") + "</span>")
    return f"<div class='xr-tip' dir='{'rtl' if ar_ else 'ltr'}'{'' if ar_ else chr(32) + 'style=' + chr(34) + 'text-align:left' + chr(34)}>" +"<hr>".join(parts) + "</div>"


def _radar_evidence(flags, tf):
    """One line per chart: the lab's number for the strongest detector on it (design board 'Radar': detector evidence)."""
    from modules import office_kpi as _OK
    from modules.chart_scan import STRATEGY_FILTERS as _SF
    d = _OK.load()
    ev = [e for e in (_OK.evidence(d, _SF[k][1][1], tf) for k in flags if k in _SF and _SF[k][1][0] == "key") if e]
    if not ev:
        return ""
    e = max(ev, key=lambda x: (not x["off"], x["n"] >= _OK.GATE_N, x["net"]))
    note = L("OFF") if e["off"] else L("passed") if e["gate"] else L("not evidence")
    col = "#f87171" if e["off"] or e["net"] <= 0 else "#5eead4" if e["gate"] else "#a3adba"
    return (f"<div style='font-size:10px;color:#848e9c;margin-top:2px'>{html.escape(L('Detector evidence'))}: "
            f"<span style='color:{col}'>{html.escape(e['key'])} {e['tf']} · {html.escape(L('net'))} {e['net']:+.3f}R · n {e['n']} · {html.escape(note)}</span></div>")


def render_chart_scanner(f):
    tf, sel, want, n_show = f["tf"], f["sel"], f["want"], f["n"]
    data = _radar_data(f)
    if data is None:
        return
    nsel = len(sel) + len(f["fv"])
    shown = [(sym, d) for sym, d in data.items() if _radar_pass(d, f)]
    if not shown and data and nsel:   # filters must really filter: say 0 matched, and offer the nearest charts (some conditions met) instead of everything
        near = sorted(((sym, d) for sym, d in data.items() if _radar_hits(d, f)[0] > 0), key=lambda sd: -_radar_hits(sd[1], f)[0])
        st.warning(L("No symbol meets ALL the chosen filters right now.") + (" " + L("Nearest (some of the conditions) are shown below.") if near else ""))
        shown = near
    # owner rule (meeting room 2026-10-22): confirmed = every chosen condition holds for THIS chart (not just the mode);
    # ranking = confirmed first, then candidates; inside each group, more conditions hit first, then symbol
    def _hits(d):
        return _radar_hits(d, f)[0]
    def _confirmed(d):
        return nsel > 0 and _hits(d) == nsel
    shown.sort(key=lambda sd: (0 if _confirmed(sd[1]) else 1, -_hits(sd[1]), sd[0]))
    # KPI strip (decision moment, owner's control-room images 2026-10-22): counts come from the charts on screen only
    n_conf = sum(1 for _s, _d in shown if _confirmed(_d)) if nsel else 0
    _rs = _radar_state(tf, data)
    from modules import ui_kit as _UK
    _n_all = max(1, len(data))
    _up_pct = 100.0 * _rs.get("up", 0) / _rs["n"] if _rs.get("n") else 0.0
    _dn = _rs.get("dn", 0)
    # ONE short top line (owner 2026-11-21): count + Summary + Open setups + grid size; everything else is charts
    from modules import radar_open_setups as _OS
    _orows = _OS.open_setups(data, {s_ for s_, _d in shown})
    ss = st.session_state
    ss.setdefault("cs_cols", 4)
    ss.setdefault("cs_h", 360)
    _tl = f.get("slots") or tuple(st.columns([0.9, 1.0, 0.8, 3.0], vertical_alignment="center")[:3])   # the filter line's last 3 boxes (one line, owner 2026-11-21)
    with _tl[0].popover(f"{L('Summary')} {len(shown)}/{len(data)}"):
        st.caption(f"{len(shown)} / {len(data)} {L('symbols match')} · {tf} · {nsel} {L('conditions')}" + (f" · {L('showing')} {int(n_show)}" if len(shown) > n_show else "")
                   + " · ◆ " + L("suggestion only, no orders"))
        st.markdown(_UK.strip([
            (L("Matched"), f"{len(shown)} / {len(data)}", f"{L('Timeframe')} {tf} · {nsel} {L('conditions')}", "", L("Charts that pass every chosen filter")),
            (L("Confirmed"), n_conf if nsel else "-", L("every condition holds"), "up" if n_conf else "", L("Every chosen condition holds on this chart")),
            (L("Candidates"), (len(shown) - n_conf) if nsel else "-", L("some conditions hold"), "warn" if nsel and len(shown) - n_conf else "", L("Some chosen conditions hold")),
            (L("Market (daily)"), L(_rs["regime"]), f"{_up_pct:.0f}% {L('up')} · {_dn} {L('down')}", "up" if _rs["regime"] == "trend up" else "down" if _rs["regime"] == "trend down" else "warn",
             L("Share of the Radar symbols above / below their daily EMA 20 and 50")),
            (L("News within 1 h"), L("yes") if _rs["news"] else L("no"), _rs["news"] or "", "warn" if _rs["news"] else "",
             L("High-impact events from the economic calendar in the next hour; the Playbook says no entry +-1 h around them")),
            (L("Data age"), _rs["age"], f"{len(data)} {L('symbols')}", "", ""),
        ]), unsafe_allow_html=True)
    with _tl[1].popover(L("Open setups") + f" ({len(_orows)})"):
        _sm = _OS.summary(_orows)
        st.caption(f"long {_sm['long']} · short {_sm['short']} · unclear {_sm['unclear']} · in the Radar filter {_sm['in_filter']}. "
                   "2.6 boxes and harmonic target prices are not in the scanner data yet (read-only, no orders).")
        if _orows:
            st.dataframe(pd.DataFrame(_orows), hide_index=True, width="stretch", height=240)
    with _tl[2].popover(f"▦ {int(ss.get('cs_n') or n_show)}·{int(ss['cs_cols'])}"):   # grid size: how many charts, per row, height
        st.number_input(L("Charts"), min_value=1, max_value=60, step=1, key="cs_n", help=L("How many charts in the grid"))
        st.selectbox(L("Columns"), [1, 2, 3, 4, 5, 6, 7, 8], key="cs_cols", format_func=lambda n: f"{n} " + L("per row"))
        st.selectbox(L("Height"), [260, 300, 360, 420, 500, 600], key="cs_h", format_func=lambda n: f"{n}px")
    if not shown:
        st.info(L("No symbols match the selected conditions right now."))
        return
    shown = shown[:int(ss.get("cs_n") or n_show)]
    per_row, ch_h = int(ss.get("cs_cols") or 4), int(ss.get("cs_h") or 360)
    _top = [s for s, d_ in shown[:3] if nsel and _confirmed(d_)]
    if _top:   # build the trade cards' scanner results side by side (each is cached), instead of one after another
        from concurrent.futures import ThreadPoolExecutor
        try:
            with ThreadPoolExecutor(4) as _ex:
                list(_ex.map(lambda s: _cs_result(s, tf), _top))
        except Exception:
            pass
    _lt = _LADDER.get(tf, ())
    _symt = tuple(rt().SCAN_SYMBOLS)
    try:   # the ladder's higher timeframes load side by side, once for the whole grid
        from concurrent.futures import ThreadPoolExecutor as _TPE
        with _TPE(max(1, len(_lt))) as _ex2:
            _lad_main = dict(zip(_lt, _ex2.map(lambda t_: _htf_trend(_symt, t_), _lt)))
    except Exception:
        _lad_main = {t_: {} for t_ in _lt}
    # owner 2026-11-21: every chart is OUR Workspace chart widget (indicators menu, tools, own timeframe), the scanner's finds as numbered points under it
    items = []
    for i_c, (sym, d) in enumerate(shown):
        card_s = card_f = ""
        if nsel and _confirmed(d) and i_c < 3:   # task 17: trade card for the top confirmed
            card_s, card_f = _trade_card(sym, tf, want)
        info = _hover_panel(sym, tf, d, {t: _lad_main.get(t, {}) for t in _lt}, card_f) + (_radar_structure_html(d) or "") + (card_s or "")
        items.append({"sym": sym, "tf": tf, "tag": (_xl("مؤكد", "Confirmed") if _confirmed(d) else _xl("مرشح", "Candidate")) if nsel else "",
                      "info": info, "pts": _radar_points(d)})
    from modules.workspace import build_workspace_html
    syms = [it["sym"] for it in items]
    ys = [s_ for s_ in syms if s_.startswith("Y:")]
    key = json.dumps([items, per_row, ch_h, _ui_lang(), rt().UI_THEME, os.path.getmtime(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modules", "workspace_app.html"))], sort_keys=True, default=str)   # a new build of the chart app = a new page
    last = ss.get("radar_ws_doc")
    if last and last[0] == key and time.time() - last[2] < 300:   # same grid: the same page (no reload, the charts keep their live feeds)
        doc = last[1]
    else:
        yf = {}
        if ys:
            try:
                from modules.yahoo_feed import embed
                yf = embed(ys, bars=160)
            except Exception as e_y:
                st.caption(f"Yahoo: {type(e_y).__name__}")
        doc = build_workspace_html(syms, None, "ar" if _ui_lang() == "ar" else "en", solo="radar", radar={"cols": per_row, "h": ch_h, "items": items}, yf=yf,
                                   ui_theme="" if rt().UI_THEME == "classic" else rt().UI_THEME, ui_bg=rt().UI_BG, ui_mat=rt().UI_MAT)
        ss["radar_ws_doc"] = (key, doc, time.time())
    rows = -(-len(items) // per_row)
    st.iframe(doc, height=rows * ch_h + 40, alt="Radar charts")   # + the "indicators on ALL charts" bar


def _radar_points(d):
    """Numbered points under a Radar chart: chart patterns (their own lines), then one point per Workspace indicator that draws a find
    (Elliott, harmonic, MSB ...), then support / resistance, then the rest as plain labels. Labels are the filter names; dir = the scanner's side."""
    from modules.chart_scan import ALL_FILTERS as _AF
    from modules import patterns as _PAT
    from modules import radar_open_setups as _OS
    flags = [k for k in d.get("flags", []) if k in _AF and not k.startswith(("px_", "ma_", "stack_", "above_all", "below_all"))]
    nm = lambda k: (_CX.flag_name(k, L(_AF[k])) if k in _AF else k)[:26]   # noqa: E731
    out, by_ind, sr, info = [], {}, [], []
    for pid, lines in (d.get("plines") or {}).items():
        out.append({"label": L(_PAT.SHORT.get(pid, pid)), "tip": nm(pid), "dir": _OS.direction_of(pid, d), "kind": "lines", "lines": lines})
    flags.sort(key=lambda k: k.startswith("sch_"))   # the exact find names first; a school flag only adds to its tool's point (or names it when alone)
    for k in flags:
        if k.startswith("cp_"):
            continue
        ind = "rsi" if k.startswith("rsi_") else _PT_IND.get(k)
        if ind:
            by_ind.setdefault(ind, []).append(k)
        elif k in _PT_SR:
            sr.append(k)
        elif not k.startswith("sch_"):
            info.append(k)
    for ind in sorted(by_ind, key=lambda i: _PT_ORDER.index(i) if i in _PT_ORDER else 99):
        ks = by_ind[ind]
        out.append({"label": nm(ks[0]).replace("School · ", "") + (f" +{len(ks) - 1}" if len(ks) > 1 else ""), "tip": " · ".join(nm(k) for k in ks), "dir": _OS.direction_of(ks[0], d), "kind": "ind", "ind": ind})
    out.append({"label": L("S/R") + (f" · {nm(sr[0])}" if sr else ""), "tip": " · ".join(nm(k) for k in sr) or L("Daily + weekly support / resistance"),
                "dir": _OS.direction_of(sr[0], d) if sr else "", "kind": "sr"})
    out += [{"label": nm(k), "tip": nm(k), "dir": _OS.direction_of(k, d), "kind": "info"} for k in info[:4]]
    return out


def _radar_structure_html(d):
    try:
        from modules import radar_structure as _RS
        return _RS.html_block(_RS.read(d))
    except Exception:
        return ""


def _page_1():   # cscan
    try:   # one tab bar, charts first (owner 2026-10-22/23); ONE filter panel under it feeds every view; only the open view runs
        # views merged (owner 2026-11-16): Screener + Signal list, and Similar charts + Correlation + Performance under "Compare"
        _OLD_RV = {"Signal list": ("Screener", "Signal list"), "Similar charts": ("Compare", "Similar charts"), "Correlation": ("Compare", "Correlation"), "Performance": ("Compare", "Performance")}
        if st.session_state.get("radar_view") in _OLD_RV:
            _o = _OLD_RV[st.session_state["radar_view"]]
            st.session_state["radar_view"] = _o[0]
            st.session_state["radar_sub_s" if _o[0] == "Screener" else "radar_sub_c"] = _o[1]
        _rv = st.segmented_control(L("Radar"), ["Chart grid", "Day plan", "SMT pairs", "Screener", "Compare", "Heat map"], default="Chart grid", format_func=L, key="radar_view", label_visibility="collapsed") or "Chart grid"
        _disp = _rv
        if _rv == "Screener":
            _disp = st.segmented_control(L("Screener"), ["Screener", "Signal list"], default="Screener", key="radar_sub_s", label_visibility="collapsed", format_func=L) or "Screener"
        elif _rv == "Compare":
            _disp = st.segmented_control(L("Compare"), ["Similar charts", "Correlation", "Performance"], default="Similar charts", key="radar_sub_c", label_visibility="collapsed", format_func=L) or "Similar charts"
        try:   # intermarket SMT (gold / silver, BTC / ETH, ...): always one line on top, and its own board
            from modules import intermarket_ui as _IMU
            st.markdown(_IMU.banner_html(_smt_events(), ar=(_ui_lang() == "ar")), unsafe_allow_html=True)
        except Exception:
            pass
        import importlib as _il
        from modules import asset_classes as _acm
        if "wide" not in _acm.class_symbols.__code__.co_varnames:   # a hot redeploy can leave the old module in memory (Streamlit keeps imported modules): reload it once
            _acm = _il.reload(_acm)
        rt().SCAN_SYMBOLS, _ac_msg2 = _acm.class_symbols(rt().asset_cls, CRYPTO_SYMBOLS, top=int(st.session_state.get("uni_n", 24)), mtype=MARKET_TYPES.get(rt().market_type, "SPOT"), wide=True)
        rt().SCAN_SYMBOLS = (rt().SCAN_SYMBOLS or list(CRYPTO_SYMBOLS))[:int(st.session_state.get("uni_n", 24))]
        _rf = _radar_filters(_disp) if _rv not in ("SMT pairs", "Day plan") else None
        if _disp == "SMT pairs":
            render_smt_board()
        elif _disp == "Day plan":
            render_day_plan(rt().SCAN_SYMBOLS)
        elif _disp == "Heat map":
            render_market_map()
        elif _disp == "Similar charts":
            render_radar_similar(_rf)
        elif _disp in ("Performance", "Correlation", "Signal list"):
            {"Performance": render_radar_perf, "Correlation": render_radar_corr, "Signal list": render_radar_signals}[_disp](_rf)
        elif _disp == "Screener":
            render_radar_screener(_rf)
        else:
            render_chart_scanner(_rf)
        try:   # X77 (owner 2026-11-20): send a Radar symbol to the X77 store; saves only
            from modules.x77_page import send_box as _x77_send
            _x77_send(rt().SCAN_SYMBOLS)
        except Exception as _xe:
            st.caption(f"X77: {type(_xe).__name__}")
    except Exception as _e:
        st.error(f"Chart Scanner error: {type(_e).__name__}: {_e}")
