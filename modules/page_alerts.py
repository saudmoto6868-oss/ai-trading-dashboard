"""Alerts page (index 6). Moved from main.py unchanged (maintenance plan M7 / 4.2)."""
import html

import streamlit as st

from modules.i18n import L
from modules.page_kit import has_secret as _has_secret


def render_alerts_page():
    """Alerts (owner 2026-10-22): control-room cards for every alert source with its real state, the Telegram link,
    and the plan for Radar alerts (task 17). Nothing here sends an order."""
    from modules import office_ui as U
    from modules.alerts import WATCH_SCORE_MIN, CALL_SCORE_MIN
    st.markdown(U.CSS, unsafe_allow_html=True)
    tg = _has_secret("TELEGRAM_BOT_TOKEN") and _has_secret("TELEGRAM_CHAT_ID")
    wf = {w["file"]: w for w in U.workflows()}
    tgw = wf.get("telegram-alerts.yml", {})
    st.markdown(U.chips([(L("Telegram"), L("key set") if tg else L("no key"), "ok" if tg else "off"),
                             (L("Telegram workflow"), tgw.get("schedule") or "-", "ok" if tgw else "off"),
                             (L("Dashboard banners"), L("on"), "ok"),
                             (L("1m alerts"), L("off"), "warn")]), unsafe_allow_html=True)
    _al, _ar_ = st.columns([3, 2])   # 2026-11-09: one page, sources left, Telegram + Radar plan right (was 3 tabs)
    with _al:
        st.markdown("<div class='xo-row'>" + U.tools(L("Alert sources"), [
            (L("Scanner alerts (Workspace)"), L("WATCH ≥") + f" {WATCH_SCORE_MIN} · " + L("CALL ≥") + f" {CALL_SCORE_MIN} + " + L("trigger"), L("on: banners + sound"), "ok"),
            (L("Telegram (sidebar)"), L("top alerts while the dashboard is open"), L("key set") if tg else L("needs TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID"), "ok" if tg else "warn"),
            (L("Telegram (GitHub Actions)"), L("runs without the dashboard open"), (L("every 30 min") if tgw else L("missing")), "ok" if tgw else "bad"),
            (L("1m alerts"), L("switched off: -147R of -150R in the journal"), L("off"), "warn"),
            (L("Radar confirmed setups"), L("every chosen condition holds, with entry / stop"), L("task 17, after the ranking"), "off"),
            (L("Order-flow sync alerts"), L("book + tape agree with the setup"), L("waiting for the order-flow sync fix"), "off"),
            (L("News alarm"), L("strong news event: blinking light, short Arabic summary, source"), L("chat item 24.1, open"), "off"),
            (L("Paper-trading bot"), L("follows only rules that passed the lab, own track record"), L("planned, never real orders"), "off")]) + "</div>", unsafe_allow_html=True)
    with _ar_:
        st.markdown(f"<div class='xo-h'>{html.escape(L('Telegram'))}</div>", unsafe_allow_html=True)
        st.caption(L("Telegram alerts go out two ways: from the sidebar while the dashboard is open, and from the GitHub Actions workflow every 30 minutes without it."))
        st.markdown(U.table([L("Setting"), L("Where"), L("Value")], [
            [L("Bot token and chat id"), "Streamlit secrets / GitHub secrets", U.badge(L("key set") if tg else L("no key"), "ok" if tg else "warn")],
            [L("Schedule"), ".github/workflows/telegram-alerts.yml", U.esc(tgw.get("schedule") or "-")],
            [L("Timeframes / top / minimum quality"), "TG_TFS · TG_TOP · TG_MIN_Q · TG_MIN_STARS", "1h,1d · 3 · 60 · 4"],
            [L("Already-sent memory"), ".tg_sent.json (actions/cache)", L("no repeats")]]), unsafe_allow_html=True)
        st.caption(L("Use the sidebar > Telegram alerts > Send test message to check the link. The keys never go into the code or the chat."))
        st.markdown(f"<div class='xo-h' style='margin-top:8px'>{html.escape(L('Radar alerts (task 17)'))}</div>", unsafe_allow_html=True)
        st.caption(L("Planned (task 17, owner decision 2026-10-22): an alert only for Radar setups marked confirmed (every chosen condition holds), "
                      "with the entry, stop and target from the existing rules, the detector's lab evidence, and the Radar mark. Suggestion only - no orders."))
        st.markdown(U.table([L("Field"), L("Source")], [[L("Symbol, timeframe, strategy"), "Radar"], [L("Entry / stop / target"), L("existing scanner rules")],
                                                      [L("Evidence"), "data/strategy_lab.json (net avg R, n)"], [L("Invalidation"), L("stop level")], [L("Status"), L("confirmed only")]]), unsafe_allow_html=True)
    st.caption(L("Educational, not investment advice. No automatic orders."))


def render_page():   # alerts (owner 2026-10-22: built as a real page)
    render_alerts_page()
