"""Playbook page (index 3): one playbook per trading style. Moved from main.py unchanged (maintenance plan M7 / 4.2)."""

import streamlit as st

from modules.i18n import L, lang as _ui_lang
from modules.page_kit import md_sections, office_bars


def _playbook_doc():
    """The playbook: which schools / rules are used, how quality is kept honest (STRATEGIES.md)."""
    pb = md_sections("STRATEGIES.md")
    if not pb:
        st.info(L("STRATEGIES.md not found."))
        return
    keys = list(pb)
    top = [k for k in keys if k.startswith("Schools ranked")] + [k for k in keys if k.startswith("Operating model")] + [k for k in keys if k.startswith("Lab results")]
    from modules import office_ui as _OU
    _pa = _ui_lang() == "ar"
    _cl = (lambda x: x) if _pa else _OU.en_only   # English page: no quoted Arabic term from the source document
    for i, k in enumerate(top):
        with st.expander(_cl(_OU.lab_title(k, _pa)), expanded=i == 0):
            st.markdown(_cl(_OU.lab_md(pb[k], _pa, L)))
    pick = st.selectbox(L("Section"), [k for k in keys if k not in top], key="pb_more", format_func=lambda k_: _cl(_OU.lab_title(k_, _pa)))
    if pick:
        st.markdown(_cl(_OU.lab_md(pb[pick], _pa, L)))


def _playbook_styles():
    """Playbook by trading style: timeframe stack, principles, goal, and the lab's strongest detectors for that style."""
    from modules import office_kpi as _OK, office_ui as U
    d = _OK.load()
    st.markdown(U.CSS, unsafe_allow_html=True)
    tone = {"Scalp": "warn", "Day": "info", "Swing": "ok", "Position": "info"}
    cards = []
    for name, _tfs in _OK.STYLES:
        info = _OK.STYLE_INFO[name]
        stack = "".join(f"<div class='xo-tile' style='text-align:center'><div class='xo-sub'>{L(lbl)}</div><b style=\"font-family:'JetBrains Mono',monospace\">{U.esc(v)}</b></div>"
                        for lbl, v in zip(("Trend", "Setup", "Entry"), info["stack"]))
        rows = "".join(f"<div style='display:flex;justify-content:space-between;gap:8px;font-size:12px'><span>{U.esc(r['key'])} {U.esc(r['tf'])} · n {r['n']}{(' · ' + L('not evidence')) if r['n'] < 100 else ''} · {L('vs random')} {r['vs_random']:+.2f}</span>"
                       f"<b style='color:{U.TONE['ok'] if r['net'] > 0 else U.TONE['bad']};font-family:monospace'>{L('net')} {r['net']:+.3f}</b></div>" for r in _OK.style_top(d, name, 4))
        cards.append(f"<div class='xo-card' style='flex:1 1 300px'><div style='display:flex;justify-content:space-between;align-items:center;gap:8px'>"
                     f"<div class='xo-h' style='font-size:18px;margin:0'>{L(name if name != 'Day' else 'Day trade')}</div>{U.badge(L(info['status']), tone[name])}</div>"
                     f"<div class='xo-sub' style='margin:4px 0 10px'>{L('Holding time')}: {L(info['hold'])}</div>"
                     f"<div class='xo-grid' style='grid-template-columns:repeat(3,minmax(0,1fr));margin-bottom:10px'>{stack}</div>"
                     f"<div style='font-size:13px;line-height:21px;margin-bottom:10px'><b>{L('Principles')}:</b> {L(info['rules'])}</div>"
                     f"<div style='background:#232a33;border-radius:10px;padding:10px;display:flex;flex-direction:column;gap:4px;margin-bottom:10px'>{rows or U.esc(L('no lab data'))}</div>"
                     f"<div style='font-size:13px'><b>{L('Goal')}:</b> {L(info['goal'])}</div></div>")
    st.markdown("<div class='xo-row'>" + "".join(cards) + "</div>", unsafe_allow_html=True)
    st.caption(L("Timeframes step by about 4-6x (trend from the higher one, setup from the middle, entry from the lower). Numbers: weekly lab, net = avg R - 0.1R costs. Educational, not investment advice."))


def _playbook_schools():
    from modules import office_kpi as _OK
    d = _OK.load()
    if not d:
        st.info(L("No lab results yet - they appear after the first weekly run."))
        return
    office_bars(_OK.pooled(d, "school"), L("avg R by school (dashed = 0.1R cost)"))
    pb = md_sections("STRATEGIES.md")
    k = [x for x in pb if x.startswith("Schools ranked")]
    if k:
        from modules import office_ui as _OU
        with st.expander(_OU.lab_title(k[0], _ui_lang() == "ar"), expanded=True):
            st.markdown(_OU.lab_md(pb[k[0]], _ui_lang() == "ar", L))


def _playbook_rules():
    from modules import office_kpi as _OK, office_ui as U
    s = _OK.summary(_OK.load()) or {}
    st.markdown(U.CSS, unsafe_allow_html=True)
    lab = md_sections("STRATEGY_LAB.md")
    tod = next((lab[x] for x in lab if x.startswith("Time of day")), "")
    st.markdown("<div class='xo-row'>" + U.indicators(L("Rules every strategy must pass"), [
        (L("Evidence gate"), "n ≥ 100", "t > 3 · " + L("both halves positive"), None),
        (L("Cost per trade"), f"{_OK.COST_R}R", L("planning estimate"), None),
        (L("OFF (no longer decide a trade)"), len(s.get("off", [])), ", ".join(s.get("off", [])), None),
        (L("Last lab run"), s.get("built") or "-", f"{s.get('symbols', 0)} " + L("symbols"), "info")]) + "</div>", unsafe_allow_html=True)
    if tod:
        st.markdown(f"**{L('Timing from the lab (UTC session and weekday, every detector pooled)')}**")
        st.markdown(U.lab_md(tod, _ui_lang() == "ar", L))


def render_playbook_page():
    """Playbook (owner 2026-10-22): one tab bar - by trading style, schools, rules and timing, the full document."""
    tabs = {"Styles & rules": (_playbook_styles, _playbook_rules), "Schools & document": (_playbook_schools, _playbook_doc)}   # 2026-11-09: 4 tabs -> 2 (owner approved)
    if st.session_state.get("pb_tab") not in tabs:
        st.session_state.pop("pb_tab", None)
    pick = st.segmented_control(L("Playbook"), list(tabs), default="Styles & rules", format_func=L, key="pb_tab", label_visibility="collapsed")
    try:
        for _i, _fn in enumerate(tabs.get(pick or "Styles & rules", tabs["Styles & rules"])):
            if _i:
                st.divider()
            _fn()
    except Exception as e:
        st.error(f"Playbook: {type(e).__name__}: {e}")
