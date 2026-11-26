"""AI page (index 5): Mr X, the backtest agent and the agent desk. Moved from main.py (maintenance plan M7)."""

import streamlit as st

from modules.i18n import L
from modules.page_kit import rt, has_secret as _has_secret
from modules.page_lab_tabs import _bt_agent


def _page_5():   # AI (owner 2026-10-22): Mr X, the backtest agent, and the agent desk in one tab bar
    if st.session_state.get("ai_tab") not in ("Mr X", "Backtest agent"):   # 2026-11-09: Agent desk folded under Mr X (owner approved)
        st.session_state.pop("ai_tab", None)
    _ai_tab = st.segmented_control(L("AI"), ["Mr X", "Backtest agent"], default="Mr X", format_func=L, key="ai_tab", label_visibility="collapsed")
    if _ai_tab == "Backtest agent":
        _c = st.columns([1.2, 0.8, 4])
        _bt_agent(_c[0].text_input(L("Symbol"), "BTC-USDT", key="ai_bt_sym"), _c[1].selectbox(L("Timeframe"), ["1h", "4h", "1d"], index=2, key="ai_bt_tf"))
    else:
        from modules.ai_page import render_ai_page
        render_ai_page(rt().ACTIVE_SYMBOLS, L)
        from modules import office_ui as _U
        st.markdown(_U.CSS, unsafe_allow_html=True)
        _adx = st.expander(L("Agent desk"), expanded=False)
        _adx.markdown(L("The agent desk turns what you say into a task for the meeting room (goal, owner, files, acceptance, gate, expected cost) and hands it to the right account. It never merges, never runs a paid job and never trades."))
        _adx.markdown(_U.table([L("Needs"), L("Status")], [
            [L("A model key (OpenAI or the free Gemini key)"), _U.badge(L("key set") if (_has_secret("OPENAI_API_KEY") or _has_secret("GEMINI_API_KEY")) else L("no key"), "ok" if (_has_secret("OPENAI_API_KEY") or _has_secret("GEMINI_API_KEY")) else "warn")],
            [L("A GitHub token limited to this repository (write the meeting room, open an @claude request)"), _U.badge(L("key set") if _has_secret("GITHUB_TOKEN_DESK") else L("no key"), "ok" if _has_secret("GITHUB_TOKEN_DESK") else "warn")],
            [L("A daily spending cap"), _U.badge(L("owner decision"), "off")]]), unsafe_allow_html=True)
        _adx.caption(L("Until these are set, write tasks in the meeting room; the site manager distributes them."))
