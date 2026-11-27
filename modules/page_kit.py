"""Small helpers shared by pages that moved out of main.py (maintenance plan M7 / 4.2)."""
import html
import os
from pathlib import Path

import streamlit as st

from modules.i18n import L, lang as _ui_lang
from modules.workspace import ui_vars as _ui_vars


def md_sections(path):
    """{heading: body} of the '## ' sections of a Markdown file in the repo (empty if missing)."""
    try:
        txt = (Path(__file__).resolve().parent.parent / path).read_text(encoding="utf-8")   # repo root, not the working folder
    except Exception:
        return {}
    out, cur = {}, None
    for line in txt.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip(); out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def office_bars(rows, title):
    """Bar chart of avg R before costs; the dashed line is the 0.1R cost, so only bars above it make money after costs."""
    import altair as alt
    import pandas as _pd
    from modules import office_kpi as _OK
    df = _pd.DataFrame(rows)
    if df.empty:
        return
    df["label"] = df["label"].map(L)
    df["after_costs"] = df["net"].apply(lambda v: "above the cost" if v > 0 else "below the cost")
    bars = alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("label:N", sort=None, title=None), y=alt.Y("avgR:Q", title=L("avg R")),
        color=alt.Color("after_costs:N", scale=alt.Scale(domain=["above the cost", "below the cost"], range=["#2dd4bf", "#f87171"]), legend=None),
        tooltip=["label", "n", "avgR", "net"])
    cost = alt.Chart(_pd.DataFrame({"y": [_OK.COST_R]})).mark_rule(strokeDash=[6, 4], color="#f0b429").encode(y="y:Q")
    st.markdown(f"<div class='xo-h' style='margin-top:6px'>{html.escape(title)}</div>", unsafe_allow_html=True)
    st.altair_chart((bars + cost).properties(height=220), width="stretch")


def kit_theme():
    """(tokens, corner radius) of the card kit from the active dashboard theme, so Radar, Technical Office and Academy follow the same Theme menu as the Workspace."""
    UI_THEME = st.session_state.get("ui_theme", "classic")   # main.py sets it before any page runs
    V = _ui_vars(UI_THEME)
    if V:
        return {"bg": V["bg"], "panel": V["solid"], "panel2": V["panel2"], "line": V["line"], "text": V["txt"], "dim": V["mut"], "accent": V["acc"], "accent2": V["up"]}, int(V["rad"])
    if UI_THEME == "lux":
        return {"panel": "#1b1814", "panel2": "#241f19", "line": "#4a3f2e", "text": "#efe6d6", "dim": "#a89c88", "accent": "#e0a95a", "accent2": "#f3cf85"}, 14
    if UI_THEME == "hud":
        return {"panel": "#0f161c", "panel2": "#16202a", "line": "#33414c", "text": "#e6ecef", "dim": "#8fa0aa", "accent": "#f0a43c", "accent2": "#ffd08a"}, 0
    return {}, 14


def kit_css():
    from modules import ui_kit as _K
    t, r = kit_theme()
    return _K.css(t, r)


def xl(ar_text, en_text):
    """One language at a time: the Arabic text on the Arabic site, the English text otherwise."""
    return ar_text if _ui_lang() == "ar" else en_text


def has_secret(name):
    try:
        return bool(os.environ.get(name) or st.secrets.get(name))
    except Exception:
        return bool(os.environ.get(name))


def rt():
    """This session's runtime values (theme, symbols, asset class...), set by main.py before the page runs (M7).
    Moved pages read them here, not from module globals, which every session shares."""
    return st.session_state["_rt"]
