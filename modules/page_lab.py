"""Technical Office (page 2) and Lab Summary (page 8). Moved from main.py (maintenance plan M7)."""
import html
from pathlib import Path

import streamlit as st

from modules.i18n import L, lang as _ui_lang
from modules.page_kit import kit_css, xl as _xl, md_sections as _md_sections, office_bars as _office_bars, has_secret as _has_secret
from modules.page_bg import _scan_store
from modules.page_lab_tabs import _office_backtest, _office_detector, _office_lab, _office_scanner
from modules.page_lab_flow import _office_flow_lab, _office_flow_manual, _office_strategy_map


@st.cache_data(ttl=60, show_spinner=False)
def _source_status():
    return _source_ping()


def _source_ping():
    """Is each data source answering right now? (tiny public calls, 4 s timeout; _source_status caches it 60 s). Never sends a key."""
    import requests
    from modules import market_cache as _mc
    out = {}
    for name, key, fn in (("OKX", "OKX", lambda: requests.get("https://www.okx.com/api/v5/public/time", timeout=8)),
                          ("Hyperliquid", "HL", lambda: requests.post("https://api.hyperliquid.xyz/info", json={"type": "meta"}, timeout=8))):
        if _mc.recent_ok(key):   # the app's own candle downloads just worked: no extra call (a busy server made the 4 s ping time out = false "down")
            out[name] = True
            continue
        try:
            out[name] = bool(fn().ok)
        except Exception:
            out[name] = False
    return out


def _office_charts():
    from modules import office_kpi as _OK
    d = _OK.load()
    if not d:
        return
    a, b = st.columns(2)
    with a:
        _office_bars(_OK.pooled(d, "tf"), L("avg R by timeframe (dashed = 0.1R cost)"))
    with b:
        _office_bars(_OK.pooled(d, "school"), L("avg R by school (dashed = 0.1R cost)"))


def _holdouts():
    """Frozen holdout results on disk (data/holdout_*.json from modules/lab_holdout.py): [{'key', 'pass', 'n', 'net', 't'}]."""
    import json as _json
    out = []
    for p in sorted((Path(__file__).resolve().parent.parent / "data").glob("holdout_*.json")):
        try:
            j = _json.loads(p.read_text(encoding="utf-8")); r = j["result"]
            out.append({"key": j["frozen"]["key"], "pass": bool(r["pass"]), "n": r["n"], "net": r["net_avgR"], "t": r["t_vs_random"]})
        except (OSError, ValueError, KeyError):
            continue
    return out


def _office_overview():
    """Control room: status bar, evidence gauge, alerts, indicators, system map, tools (owner's reference images)."""
    from modules import office_kpi as _OK, office_ui as U
    s = _OK.summary(_OK.load()) or {}
    board = U.load_tasks().get("tasks", []); cnt = U.task_counts(board); src = _source_status()
    fred = _has_secret("FRED_API_KEY"); tg = _has_secret("TELEGRAM_BOT_TOKEN")
    b = s.get("best") or {}
    st.markdown(U.CSS, unsafe_allow_html=True)
    st.markdown(U.chips([(L("OKX"), L("live") if src.get("OKX") else L("down"), "ok" if src.get("OKX") else "bad"),
                         (L("Hyperliquid"), L("live") if src.get("Hyperliquid") else L("down"), "ok" if src.get("Hyperliquid") else "bad"),
                         ("FRED", L("key set") if fred else L("no key"), "ok" if fred else "off"),
                         (L("Telegram"), L("key set") if tg else L("no key"), "ok" if tg else "off"),
                         (L("Last lab run"), s.get("built") or "-", "info"),
                         (L("Blocked tasks"), cnt.get("blocked", 0), "bad" if cnt.get("blocked") else "ok")]), unsafe_allow_html=True)
    al = []
    if not s.get("passed"):
        al.append((L("Nothing has passed the evidence gate yet"), L("info"), "info",
                   L("The lab gives a t-stat to") + f" {s.get('det_t', 0)} / {s.get('det_rows', 0)} " + L("detector rows (and") + f" {s.get('chain_t', 0)} / {s.get('chain_rows', 0)} " + L("chain rows): a row without t cannot pass the gate")))
    pb = [k for k in _md_sections("STRATEGIES.md") if k.startswith("Lab results ")]
    if pb and s.get("built") and s["built"] not in pb[0]:
        al.append((L("The Playbook summary is older than the last lab run"), L("degraded"), "warn", f"{pb[0].split(' ')[2]} / {s['built']}"))
    for t in board:
        if t.get("status") == "blocked":
            _ar = _ui_lang() == "ar"
            al.append((t.get("title_ar") if _ar and t.get("title_ar") else t["title"], L("blocked"), "bad", t.get("next_ar") if _ar and t.get("next_ar") else t.get("next", "")))
    if not src.get("Hyperliquid", True):
        al.append((L("Hyperliquid is not answering"), L("down"), "bad", L("gold / oil / index charts stop updating")))
    st.markdown("<div class='xo-row'>" + U.gauge(s.get("passed", 0), s.get("candidates", 0), L("Evidence gate"),
                L("n >= 100 · t > 3 · net > 0 · both halves positive, after 0.1R"), L("groups passed")) +
                U.alerts(L("Alerts"), al[:5]) +
                U.indicators(L("Indicators"), [
                    (L("Detectors in the lab"), s.get("detectors", "-"), f"{s.get('symbols', 0)} " + L("symbols"), None),
                    (L("OFF (no longer decide a trade)"), len(s.get("off", [])), ", ".join(s.get("off", [])), None),
                    (L("Best net avg R (n >= 100)"), f"{b['net']:+.3f}" if b else "-", f"{b.get('key', '')} {b.get('tf', '')} · n {b.get('n', '')}", "ok" if b and b["net"] > 0 else None),
                    (L("Cost per trade"), f"{_OK.COST_R}R", L("planning estimate"), None),
                    (L("Tasks in review"), cnt.get("review", 0), L("waiting for Gemini / owner"), "info"),
                    (L("Open tasks"), cnt.get("open", 0) + cnt.get("waiting", 0), L("work board"), None),
                    (L("Rows with a t-stat"), f"{s.get('det_t', 0)} / {s.get('det_rows', 0)}", L("detector x timeframe; the gate needs t > 3"), "bad" if not s.get("det_t") else None),
                    (L("Holdout tests run"), f"{len(_holdouts())}", L("frozen holdouts on older candles") + " · " + L("passed") + f" {sum(1 for h in _holdouts() if h['pass'])}", None)]) + "</div>", unsafe_allow_html=True)
    _office_charts()
    hl = "ok" if src.get("Hyperliquid") else "bad"
    st.markdown(U.system_map(L("System map"), L("From data to decision to evidence; every node shows its state"), [
        [("OKX", L("crypto · candles, book, trades"), "ok" if src.get("OKX") else "bad"), ("Hyperliquid", L("gold · oil · indices · FX"), hl),
         ("FRED", L("macro data"), "ok" if fred else "off"), (L("News & calendar"), L("Grok watch every 6 h"), "ok")],
        [(L("Detectors") + f" · {s.get('detectors', '-')}", L("OFF") + f": {len(s.get('off', []))}", "ok")],
        [(L("Scanner & Radar"), L("confirmed first, then candidates"), "ok"), (L("Order flow"), L("footprint · book · tape"), hl),
         (L("Backtest"), L("rules + engine, verdict on out-of-sample"), "info"), (L("Strategy import"), L("text / video link -> rules"), "off")],
        [(L("Alerts · Telegram"), L("confirmed only, never orders"), "ok" if tg else "off"), (L("Journal"), L("in the browser · CSV export"), "info"),
         (L("Model inventory"), L("gate verdict per strategy"), "info")]]), unsafe_allow_html=True)
    st.caption(L("Educational, not investment advice. Source: data/strategy_lab.json (weekly lab)."))


def _office_board():
    from modules import office_ui as U
    d = U.load_tasks(); tasks = d.get("tasks", [])
    st.markdown(U.CSS, unsafe_allow_html=True)
    cnt = U.task_counts(tasks)
    st.markdown(U.chips([(L(k), v, U.STATUS_TONE.get(k, "off")) for k, v in sorted(cnt.items())]), unsafe_allow_html=True)
    areas = sorted({t.get("area", "-") for t in tasks})
    pick = st.segmented_control(L("Area"), ["All"] + areas, default="All", format_func=L, key="to_board_area")
    ar = _ui_lang() == "ar"
    tx = lambda t, k: t.get(k + "_ar") if ar and t.get(k + "_ar") else t.get(k, "")
    rows = [[U.badge(t.get("p", "-"), {"P1": "bad", "P2": "warn", "P3": "info"}.get(t.get("p"), "off")), U.esc(t.get("wbs", "")), U.esc(tx(t, "title")), U.esc(L(t.get("area", ""))), U.esc(tx(t, "owner")),
             U.badge(L(t.get("status", "open")), U.STATUS_TONE.get(t.get("status", "open"), "off")), U.esc(t.get("gate", "")), U.esc(tx(t, "next"))]
            for t in tasks if pick in (None, "All") or t.get("area") == pick]
    st.markdown(U.table([L("Priority"), L("WBS"), L("Task"), L("Area"), L("Owner"), L("Status"), L("Gate"), L("Next step")], rows), unsafe_allow_html=True)
    st.caption(L("Work board updated") + f" {d.get('updated', '-')} · data/office_tasks.json · " + L("every change is also written in the meeting room"))


def _office_ops():
    from modules import office_ui as U
    st.markdown(U.CSS, unsafe_allow_html=True)
    wf = U.workflows()
    rows = [[U.esc(L(w["name"])), U.esc(w["file"]), U.esc(w["schedule"] or "-"), "✓" if w["manual"] else "",
             U.badge(L("writes to the repo"), "warn") if w["writes"] else ""] for w in wf]
    st.markdown(U.table([L("Workflow"), L("File"), L("Schedule (UTC cron)"), L("Manual run"), L("Repo writes")], rows), unsafe_allow_html=True)
    st.caption(L("Protecting main is on hold until the workflows that push to main open a pull request instead (owner rule: protect only if nothing breaks)."))


def _office_control():
    """Technical Office > Control room: status, gauge, alerts, charts, system map; under it the work board (left) and the GitHub workflows (right)."""
    _office_overview()
    a, b = st.columns([2, 1])
    with a:
        st.markdown(f"<div class='xo-h' style='margin-top:6px'>{html.escape(L('Work board'))}</div>", unsafe_allow_html=True)
        _office_board()
    with b:
        st.markdown(f"<div class='xo-h' style='margin-top:6px'>{html.escape(L('Operations'))}</div>", unsafe_allow_html=True)
        _office_ops()


def _office_lab_all():
    """Technical Office > Lab results: the Lab Summary on top (was its own page), then one detector's card (left) next to the weekly lab tables (right)."""
    try:
        from modules.lab_summary import render_lab_summary
        render_lab_summary(_scan_store().get("payload") or {})
    except Exception as _ls_exc:
        st.error(L("Lab Summary") + f": {_ls_exc}")
    st.divider()
    a, b = st.columns(2)
    with a:
        _office_detector()
    with b:
        _office_lab()


def _office_strategies():
    """Technical Office > Strategies: scanner presets for the Radar (folded), the strategy map, then the rule builder / backtest."""
    with st.expander(L("Scanner presets -> Radar"), expanded=False):
        _office_scanner()
    _office_strategy_map()
    st.divider()
    st.markdown(f"<div class='xo-h'>{html.escape(L('Backtest your own rules'))}</div>", unsafe_allow_html=True)
    _office_backtest()


def _office_flow():
    """Technical Office > Order flow: the forward-test judge on top, the manual (methods, tools, routine) under it - one tab (2026-11-09)."""
    _office_flow_lab()
    st.divider()
    _office_flow_manual()


def render_lab_page():
    """Technical Office v2: one tab bar, only the open tab runs. Options desk + Macro regime live in Trading > Options & macro (2026-11-09)."""
    tabs = {"Control room": _office_control, "Lab results": _office_lab_all, "Strategies": _office_strategies, "Order flow": _office_flow}   # 2026-11-09: 9 tabs -> 4
    if st.session_state.get("to_tab") not in tabs:   # a tab that moved (Options desk, Macro regime, Flow manual / lab) must not break an open session
        st.session_state.pop("to_tab", None)
    st.markdown(kit_css(), unsafe_allow_html=True)
    pick = st.segmented_control(L("Technical Office"), list(tabs), default="Control room", format_func=L, key="to_tab", label_visibility="collapsed")
    try:
        tabs.get(pick or "Control room", _office_overview)()
    except Exception as e:
        st.error(f"Technical Office: {type(e).__name__}: {e}")


def _page_2():   # lab
    render_lab_page()


def _page_8():   # lab summary (summary on top; the former Validation Lab / Calibration / Class rotation / Evidence summary tabs as collapsed sections)
    try:
        from modules.lab_summary import render_lab_summary
        render_lab_summary(_scan_store().get("payload") or {})
    except Exception as _lab_exc:
        st.error(_xl("ملخص المعمل: ", "Lab Summary: ") + str(_lab_exc))
    st.stop()
