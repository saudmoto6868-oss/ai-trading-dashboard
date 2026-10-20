"""
THE ALERT OFFICER
Watches scored signals; when one crosses the alert threshold, fires a
sound, colored banner, and full trade plan (entry, stop loss, 3 staged
take profits). This is also the hook point for a future Telegram bot.
"""

import streamlit as st
from modules.risk_engine import build_trade_plan

ALERT_SCORE_THRESHOLD = 4

STRENGTH_COLORS = {
    "strong": "#1f9d55",
    "medium": "#d4a72c",
    "weak": "#9aa0a6",
}


def classify_strength(score: int, max_score: int) -> str:
    ratio = score / max_score
    if ratio >= 0.75:
        return "strong"
    if ratio >= 0.5:
        return "medium"
    return "weak"


_BEEP_HTML = """
<audio autoplay>
  <source src="data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQQAAAAAAAAA" type="audio/wav">
</audio>
"""


def fire_alert(symbol: str, score_result: dict, play_sound: bool = True):
    strength = classify_strength(score_result["score"], score_result["max_score"])
    color = STRENGTH_COLORS[strength]
    plan = build_trade_plan(score_result)

    st.markdown(
        f"""
        <div style="border-left: 6px solid {color}; background-color: #1a1a1a;
                    padding: 12px 16px; border-radius: 6px; margin-bottom: 8px;">
            <span style="color:{color}; font-weight:bold; font-size:16px;">
                {symbol} - {strength.upper()} SIGNAL ({score_result['trade_type']})
            </span><br>
            <span style="color:#ddd;">
                Direction: {plan['direction']} | Entry: {plan['entry']} | Stop Loss: {plan['stop_loss']}<br>
                TP1: {plan['take_profits'][0]} | TP2: {plan['take_profits'][1]} | TP3: {plan['take_profits'][2]}<br>
                Reasons: {', '.join(score_result['reasons'])}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if play_sound:
        st.markdown(_BEEP_HTML, unsafe_allow_html=True)

    return plan


def check_and_fire_alerts(results: list, play_sound: bool = True):
    fired = []
    for res in results:
        if res["score"] >= ALERT_SCORE_THRESHOLD:
            plan = fire_alert(res["symbol"], res, play_sound=play_sound)
            fired.append({**res, "plan": plan})
    return fired
