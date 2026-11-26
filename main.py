"""
THE FLOOR MANAGER
Orchestrates every employee module and renders the final dashboard.

Layout (top to bottom):
  title row -> scrolling news ticker -> quick-link buttons ->
  asset tabs. Crypto tab: [scanner watchlist | two stacked TradingView charts |
  Depth-of-Market ladder | Smart time & sales], limit-order tracker underneath.
  Other tabs: [compact watchlist | chart].
The whole page re-runs every few seconds (auto-refresh) so data stays live.
"""

import base64
import html
import json
import os
import time
from pathlib import Path

import pandas as pd
import streamlit as st

from config import (
    CRYPTO_SYMBOLS,
    EXTERNAL_LINKS, FINVIZ_PATTERNS, FINVIZ_PATTERN_URL,
    TRADE_TYPES, AUTO_REFRESH_SECONDS, TV_SYMBOL_MAP,
)
from modules.data_fetcher import get_mt5_data
from modules.scorer import (
    score_symbol, scan_symbol, fetch_tfs,
)
from modules.market_cache import fetch_frames, get_klines
from modules.arabic import (
    trade_name, tags_html, trade_chip_html, tag_for, signal_ar, htf_lines_ar, scenarios_ar, tv_link, chart_svg, n_, dir_name, tf_name,
)
from modules.risk_engine import build_trade_plan
from modules.alerts import check_and_fire_alerts, ALERT_SCORE_THRESHOLD
from modules.workspace import render_workspace
from modules.i18n import L, RTL_CSS, lang as _ui_lang
from modules.page_kit import md_sections as _md_sections, office_bars as _office_bars, kit_css, xl as _xl, has_secret as _has_secret   # moved out of main.py (M7)
from modules.page_playbook import render_playbook_page   # Playbook page moved out of main.py (M7)
from modules.page_academy import render_academy_page   # Academy page moved out of main.py (M7)
from modules import page_options as _pg16   # page 16 moved out of main.py (M7)
from modules import page_alerts as _pg6   # page 6 moved out of main.py (M7)
from modules import page_journal as _pg4   # page 4 moved out of main.py (M7)
from modules import page_hub as _pg9   # page 9 moved out of main.py (M7)
from modules import office_ui as _OUI   # noqa: F401  (registers the Technical Office Arabic keys in i18n.AR at import)
from modules.site_icons import site_icon_b64
from modules.header_bar import render_header_bar
from modules.macro import api_key, fetch_macro
from modules.chart_scan import (ALL_FILTERS, MOVE_FILTERS, PATTERN_FILTERS, RSI_FILTERS, STRATEGY_FILTERS, SHORT as CS_SHORT,
                                features as cs_features, match_filters, mini_chart_svg, move_flags, strategy_flags)
from modules.news_feed import get_latest_news
from modules.crypto_extras import render_order_book, render_time_and_sales
from modules.dom_panel import (
    build_ladder, ladder_html, classify_trades, trades_html,
    LimitTracker, limit_events_html, fmt_price,
    ORDERFLOW_CSS, LEGEND_HTML, TapeMemory, DomMemory, hits_from, mark_absorption,
    tape_stats, stats_html,
)

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:  # package missing: dashboard still works, just not live
    st_autorefresh = None

st.set_page_config(
    page_title="XPiX", layout="wide", page_icon=str(Path(__file__).with_name("modules") / "xpix_icon.png"),
    initial_sidebar_state="collapsed",
)
def _url_pref(name, allowed, default):
    """Choice from the link (?name=...), else the cookie the Workspace keeps (xpix_<name>, so a bare link keeps the last theme), else default."""
    q = st.query_params.get(name)
    if q in allowed:
        return q
    try:
        c = st.context.cookies.get("xpix_" + name)
    except Exception:
        c = None
    return c if c in allowed else default


if "ws_lang" not in st.session_state and _url_pref("lang", ("en", "ar"), None):   # Alt+L / the language list keep the choice in the URL
    st.session_state["ws_lang"] = _url_pref("lang", ("en", "ar"), None)

st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    html, body, .stApp, [data-testid="stAppViewContainer"], section.main { overscroll-behavior-y: none; }   /* touch screens: pulling down at the top must not reload the whole app */
    .stTabs [data-baseweb="tab"] { color: #eaecef; }
    .stTabs [aria-selected="true"] { color: #f0b90b; border-bottom-color: #f0b90b; }
    div[data-testid="stMetricValue"] { color: #f0b90b; }
    .block-container { padding-top: 0rem; padding-left: 0.15rem; padding-right: 0.15rem; max-width: 100%; }
    header[data-testid="stHeader"] { background: transparent; height: 1.6rem; }
    div[data-testid="stSelectbox"] { margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

# ---- Login gate (item 22): only active when APP_PASSWORD / APP_USERS is set in Secrets -----------------
from modules.auth import gate as _auth_gate
if not _auth_gate(L):
    st.stop()

# ---- Research Labs (sidebar) -------------------------------------------------
# Monte Carlo lives in Trading > Journal; only Micro · Foundations is opened from here.
with st.sidebar.expander(L("🔬 Research Labs"), expanded=False):
    st.caption(L("Standalone studies — open in full page"))
    _lab_choice = st.radio(
        L("Lab"),
        ["—", "⬡ Micro · Foundations", "2.6 Strategy Intelligence"],
        key="lab_choice",
        label_visibility="collapsed",
    )
    if _lab_choice == "⬡ Micro · Foundations":
        from modules.micro_foundations import render as _mf_render
        _mf_render()
        st.stop()
    if _lab_choice == "2.6 Strategy Intelligence":
        from modules.two_six_lab import render as _two_six_render
        _two_six_render()
        st.stop()

# ---- Build stamp: which commit this running app was built from (so a stale deploy is visible at a glance) ----
@st.cache_resource
def _build_stamp() -> str:
    import subprocess
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%h · %cd", "--date=format:%Y-%m-%d %H:%M"], capture_output=True, text=True, timeout=5,
                             cwd=os.path.dirname(os.path.abspath(__file__))).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    try:
        head = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".git", "HEAD")).read().strip()
        return head[:7] if len(head) >= 40 or not head.startswith("ref:") else "unknown"
    except Exception:
        return "unknown"


st.sidebar.caption(L("Build") + ": " + _build_stamp())

# ---- Settings (sidebar) -----------------------------------------------------
st.sidebar.header(L("Settings"))
# OFF by default: every refresh re-runs the whole app on the server (Streamlit Cloud throttled the app's CPU on 2026-10-17).
# The Workspace is live on its own (prices / book / tape stream in the browser), so it does not need this.
auto_on = st.sidebar.checkbox(L("Auto-refresh (live data)"), value=False, key="w_auto_refresh_live_data",
                              help=L("Re-runs the whole page on the server. The Workspace is already live without it."))
refresh_secs = st.sidebar.slider(L("Refresh every (seconds)"), 60, 600, max(120, AUTO_REFRESH_SECONDS), step=30, key="w_refresh_every_seconds_v2")
play_sound = st.sidebar.checkbox(L("Play sound on NEW strong signals"), value=True, key="w_play_sound_on_new_strong_signals")
with st.sidebar.expander(L("Order Book / Time & Sales"), expanded=False):
    smart_mult = st.slider(
        L("Smart trade = size >= N x median print"), 2.0, 10.0, 4.0, step=0.5,
        help=L("Prints this many times larger than the median trade in the window are flagged SMART; 2.5x that is WHALE."),
        key="w_smart_trade_size_n_x_median_print")
    big_order_mult = st.slider(
        L("Big limit order = N x median level"), 3.0, 15.0, 5.0, step=0.5,
        help=L("Used by the DOM highlight and by Limit Tracking."),
        key="w_big_limit_order_n_x_median_level")
    fast_secs = st.slider(L("DOM / Time&Sales refresh (seconds)"), 1, 10, 3,
                          help=L("How often the two order-flow panels update by themselves (flashes appear on each update)."), key="w_dom_time_sales_refresh_seconds")
    absorb_mult = st.slider(
        L("Absorption = level volume >= N x median level"), 2.0, 8.0, 3.0, step=0.5,
        help=L("Heavy volume trading at one price while the price barely moves."),
        key="w_absorption_level_volume_n_x_median_level")
with st.sidebar.expander(L("Telegram alerts (optional)"), expanded=False):
    tg_on = st.checkbox(L("Send the best alerts to Telegram"), value=False, key="tg_on",
                        help=L("Only the top-ranked alerts (evidence score, not a proven win rate). Needs TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in Secrets."))
    tg_top = st.number_input(L("Max alerts per scan"), 1, 10, 3, key="tg_top")
    tg_min = st.slider(L("Minimum quality (0-100)"), 30, 95, 60, key="tg_min")
    if st.button(L("Send test message"), key="tg_test"):
        from modules import telegram_alerts as _tga
        _err = _tga.send("✅ 6868 X: Telegram connected.")
        st.success(L("Sent.")) if not _err else st.error(_err)
    st.caption(L("Quality = strategy families agreeing + daily bias / premium-discount / killzone + reward:risk. It ranks the evidence; it does not predict success."))
with st.sidebar.expander(L("Chart / Layout"), expanded=False):
    ws_height = st.slider(L("Workspace height (px)"), 500, 6000, 3400, step=20, key="w_workspace_height_px")
    ui_bg = st.color_picker(L("Page background"), "#0b0e11", key="w_page_background")
    ui_accent = st.color_picker(L("Accent colour (tabs, highlights)"), "#f0b90b", key="w_accent_colour_tabs_highlights")
    st.caption(L("Per-widget colours: use the two colour dots in each Workspace widget's title bar."))
st.markdown(f"<style>.stApp{{background-color:{ui_bg}}} .stTabs [aria-selected='true']{{color:{ui_accent};border-bottom-color:{ui_accent}}}</style>", unsafe_allow_html=True)
st.markdown(f"<style>{ORDERFLOW_CSS}</style>", unsafe_allow_html=True)
# compact, square-cornered controls on every page (owner 2026-11-16): small dropdowns, inputs, buttons, tabs and labels
COMPACT_CSS = """<style>
[data-baseweb="select"]>div{min-height:24px!important;height:auto!important;border-radius:4px!important;background:#161a1e!important;border:1px solid #2b3139!important;box-shadow:none!important}
[data-baseweb="select"] *{font-size:11px!important;color:#c9d1d9!important}
[data-baseweb="select"] input{min-height:0!important;padding:0 4px!important}
[data-baseweb="input"],[data-baseweb="base-input"]{background:#161a1e!important;border-radius:4px!important;border:1px solid #2b3139!important;min-height:24px!important}
[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input{font-size:11px!important;padding:2px 6px!important;min-height:22px!important;color:#c9d1d9!important}
[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label{font-size:10px!important;line-height:12px!important;margin:0 0 1px 0!important;color:#848e9c!important}
[data-testid="stPopover"] button,button[kind="secondary"],button[kind="tertiary"]{min-height:24px!important;height:24px!important;padding:0 8px!important;font-size:11px!important;border-radius:4px!important;border:1px solid #2b3139!important;background:#161a1e!important;color:#c9d1d9!important}
button[data-baseweb="tab"]{font-size:12px!important;padding:4px 10px!important;min-height:0!important;height:30px!important}
[data-baseweb="tab-list"]{gap:2px!important}
[data-baseweb="tab-highlight"]{height:2px!important}
[data-testid="stSegmentedControl"] button{min-height:22px!important;height:22px!important;font-size:11px!important;padding:0 8px!important;border-radius:4px!important}
[data-testid="stVerticalBlock"]{gap:.5rem}
[data-testid="stSelectbox"]>div>div,[data-testid="stNumberInput"]>div>div,[data-testid="stTextInput"]>div>div,[data-testid="stMultiSelect"]>div>div{background:#161a1e!important;border:1px solid #2b3139!important;border-radius:4px!important;min-height:24px!important;box-shadow:none!important}
[data-testid="stSelectbox"] span,[data-testid="stSelectbox"] input,[data-testid="stMultiSelect"] span,[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input{color:#c9d1d9!important;font-size:11px!important;background:transparent!important}
[data-testid="stNumberInput"] input{min-height:22px!important;padding:0 6px!important}
[data-testid="stNumberInput"] button{background:#161a1e!important;color:#c9d1d9!important;border-left:1px solid #2b3139!important}
[data-testid="stSegmentedControl"]>div,[data-testid="stSegmentedControl"] [role="radiogroup"]{background:#161a1e!important;border:1px solid #2b3139!important;border-radius:4px!important;padding:2px!important}
[data-testid="stSegmentedControl"] button{background:transparent!important;color:#9aa3ad!important;border:0!important;border-radius:3px!important;font-size:11px!important;min-height:22px!important;height:22px!important;padding:0 8px!important}
[data-testid="stSegmentedControl"] button[aria-checked="true"],[data-testid="stSegmentedControl"] button[aria-pressed="true"]{background:#2b3139!important;color:#eaecef!important}
button[role="tab"]{background:transparent!important;color:#9aa3ad!important;font-size:12px!important;padding:2px 10px!important;border:0!important;border-radius:0!important}
button[role="tab"][aria-selected="true"]{color:#eaecef!important;box-shadow:inset 0 -2px 0 #f0b90b!important}
[data-baseweb="tab-border"]{background:#2b3139!important}
[data-testid="stPills"] button,[data-testid="stPills"] div[role="button"]{background:#161a1e!important;border:1px solid #2b3139!important;color:#9aa3ad!important;font-size:11px!important;min-height:22px!important;padding:0 8px!important;border-radius:4px!important}
[data-testid="stPills"] button[aria-checked="true"],[data-testid="stPills"] div[aria-checked="true"]{background:#2b3139!important;color:#eaecef!important}
[data-testid="stButtonGroup"] button,[role="radio"]{background:#161a1e!important;color:#9aa3ad!important;border:1px solid #2b3139!important;border-radius:3px!important;font-size:11px!important;min-height:22px!important;height:22px!important;padding:0 8px!important;box-shadow:none!important}
[data-testid="stButtonGroup"] button[aria-checked="true"],[role="radio"][aria-checked="true"]{background:#2b3139!important;color:#eaecef!important;border-color:#f0b90b!important}
[data-testid="stButtonGroup"] [role="radiogroup"]{gap:2px!important}
</style>"""
st.markdown(COMPACT_CSS, unsafe_allow_html=True)
if _ui_lang() == "ar":   # Arabic: labels, captions and alerts right-to-left (charts, tables and numbers keep their own direction)
    st.markdown(RTL_CSS, unsafe_allow_html=True)
if auto_on and st_autorefresh is not None:
    st_autorefresh(interval=refresh_secs * 1000, key="auto_refresh")
elif auto_on:
    st.sidebar.warning(L("streamlit-autorefresh is not installed - add it to requirements.txt."))

# ---- Dashboard theme (top bar) ------------------------------------------------------
from modules.workspace import UI_THEMES as _UI_THEMES, ui_theme_bg as _ui_theme_bg, ui_vars as _ui_vars
if "ui_theme" not in st.session_state:
    st.session_state["ui_theme"] = _url_pref("theme", dict(_UI_THEMES), "classic")
_BUILT_THEMES = tuple(k for k, _ in _UI_THEMES)   # every listed theme is built (3-9 run on the palette engine)
if st.session_state["ui_theme"] not in _BUILT_THEMES:   # an empty slot: say so and stay on Classic
    st.toast(L("That theme slot is still empty - send the picture for it and it gets built."))
    st.session_state["ui_theme"] = "classic"
UI_THEME = st.session_state["ui_theme"]
if UI_THEME != "classic":
    st.query_params["theme"] = UI_THEME
elif "theme" in st.query_params:
    del st.query_params["theme"]
UI_BG = _ui_theme_bg(UI_THEME)
# material layer (owner 2026-10-18: "use the material in the theme picture - steel, paper, wood, fabric"): textures on panels, bars and buttons
_MATS = ["auto", "none", "steel", "paper", "wood", "fabric", "glass", "carbon"]
_MAT_AUTO = {"classic": "none", "lux": "glass", "hud": "carbon", "ember": "steel", "sunset": "wood", "emerald": "fabric", "neon": "glass", "mono": "steel", "grafana": "carbon", "blueprint": "paper",
             "slate": "none", "frost": "glass", "gold": "steel", "amber": "carbon", "dusk": "fabric", "cyber": "carbon", "nogray": "steel", "deerflow": "none"}
if "ui_mat" not in st.session_state:
    st.session_state["ui_mat"] = _url_pref("mat", _MATS, "auto")
UI_MAT = _MAT_AUTO.get(UI_THEME, "none") if st.session_state["ui_mat"] == "auto" else st.session_state["ui_mat"]
if st.session_state["ui_mat"] != "auto":
    st.query_params["mat"] = st.session_state["ui_mat"]
elif "mat" in st.query_params:
    del st.query_params["mat"]
_NOISE = "data:image/svg+xml;utf8," + "<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 .55 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>"
_MAT_CSS = {
    "steel": "repeating-linear-gradient(90deg,rgba(255,255,255,.035) 0 1px,rgba(0,0,0,.035) 1px 3px),linear-gradient(180deg,rgba(255,255,255,.06),rgba(0,0,0,.18))",
    "paper": f"url(\"{_NOISE}\"),linear-gradient(180deg,rgba(255,250,235,.05),rgba(120,100,60,.05))",
    "wood": "repeating-linear-gradient(92deg,rgba(120,72,30,.10) 0 2px,rgba(60,32,10,.06) 2px 7px,rgba(150,95,45,.08) 7px 9px,rgba(0,0,0,0) 9px 14px),linear-gradient(180deg,rgba(150,95,40,.10),rgba(40,20,5,.18))",
    "fabric": "repeating-linear-gradient(45deg,rgba(255,255,255,.035) 0 1px,transparent 1px 4px),repeating-linear-gradient(-45deg,rgba(0,0,0,.08) 0 1px,transparent 1px 4px)",
    "glass": "linear-gradient(135deg,rgba(255,255,255,.08),rgba(255,255,255,.01) 40%,rgba(255,255,255,.05))",
    "carbon": "radial-gradient(rgba(255,255,255,.05) 15%,transparent 16%) 0 0/6px 6px,radial-gradient(rgba(0,0,0,.35) 15%,transparent 16%) 3px 3px/6px 6px,linear-gradient(180deg,rgba(255,255,255,.03),rgba(0,0,0,.2))"}
if UI_MAT in _MAT_CSS:
    st.markdown(f"""<style>.st-key-hdr::before{{background-image:{_MAT_CSS[UI_MAT]}!important}}
[data-testid="stSidebar"]>div,[data-testid="stPopoverBody"],.stButton button,[data-testid="stExpander"] details{{background-image:{_MAT_CSS[UI_MAT]}!important}}
{".st-key-hdr::before,[data-testid=stPopoverBody]{backdrop-filter:blur(10px) saturate(1.3)}" if UI_MAT == "glass" else ""}</style>""", unsafe_allow_html=True)
if UI_THEME == "lux":   # theme 1 "Less is More": blurred photo behind the page, warm charcoal + amber, rounded glass
    st.markdown(f"""<style>.stApp{{background:#0d0c0a url({UI_BG}) center/cover fixed no-repeat!important}}
[data-testid="stSidebar"]>div{{background:rgba(18,16,13,.86)}} .stApp p,.stApp label,.stApp span:not([data-testid="stIconMaterial"]){{color:#efe6d6}}
.st-key-page label:has(input:checked){{border-bottom-color:#e0a95a!important}} .st-key-page label:has(input:checked) p{{color:#e0a95a!important}}
[data-testid="stExpander"],[data-testid="stVerticalBlockBorderWrapper"]{{background:rgba(24,21,18,.72);border-radius:14px}}
.st-key-hdr{{--hdr-bg:linear-gradient(180deg,rgba(32,27,22,.92),rgba(18,16,13,.92));--hdr-line:rgba(224,169,90,.22);--hdr-r:14px}} .xpix-mini i{{color:#e0a95a!important}}</style>""", unsafe_allow_html=True)
elif _ui_vars(UI_THEME):   # themes 3-16: one stylesheet from the palette
    _V = _ui_vars(UI_THEME)
    st.markdown(f"""<style>.stApp{{background:{_V['bg']} url({UI_BG}) center/cover fixed no-repeat!important}}
.stApp p,.stApp label,.stApp span:not([data-testid="stIconMaterial"]){{color:{_V['txt']}}} .stApp p,.stApp label,.stApp li,.stApp h1,.stApp h2,.stApp h3,.stApp td,.stApp th{{{("font-family:" + _V['font']) if _V['font'] else ""}}} h1,h2,h3{{text-transform:{_V['tt']};letter-spacing:{_V['ls']}}}
[data-testid="stSidebar"]>div{{background:{_V['solid']}}} .st-key-page label:has(input:checked){{border-bottom-color:{_V['acc']}!important}} .st-key-page label:has(input:checked) p{{color:{_V['acc']}!important}}
[data-testid="stExpander"],[data-testid="stVerticalBlockBorderWrapper"]{{background:{_V['panel']};border-radius:{_V['rad']}px;border:1px solid {_V['line']}}}
.stButton button{{border-radius:{max(0, _V['rad'] // 2)}px}} .st-key-hdr{{--hdr-bg:{_V['panel']};--hdr-line:{_V['line']};--hdr-r:{_V['rad']}px}} .xpix-mini i{{color:{_V['acc']}!important}}{_V.get('extra', '')}</style>""", unsafe_allow_html=True)
elif UI_THEME == "hud":   # theme 2 "Orbit HUD": misty sky behind the page, square frames, orange accent, wide uppercase lettering
    st.markdown(f"""<style>.stApp{{background:#141c22 url({UI_BG}) center/cover fixed no-repeat!important}}
.stApp p,.stApp label,.stApp span:not([data-testid="stIconMaterial"]){{color:#e6ecef}} .stApp p,.stApp label,.stApp li,.stApp h1,.stApp h2,.stApp h3,.stApp td,.stApp th{{font-family:Rajdhani,'Barlow Condensed','Segoe UI',sans-serif}} h1,h2,h3{{text-transform:uppercase;letter-spacing:.12em;font-weight:500}}
[data-testid="stSidebar"]>div{{background:rgba(10,15,20,.75)}} .st-key-page label:has(input:checked){{border-bottom-color:#f0a43c!important}} .st-key-page label:has(input:checked) p{{color:#f0a43c!important}}
[data-testid="stExpander"],[data-testid="stVerticalBlockBorderWrapper"]{{background:rgba(10,15,20,.5);border-radius:0;border:1px solid rgba(225,235,240,.2)}}
.stButton button{{border-radius:0;text-transform:uppercase;letter-spacing:.1em}} .st-key-hdr{{--hdr-bg:rgba(10,15,20,.62);--hdr-line:rgba(225,235,240,.22);--hdr-r:0}} .xpix-mini i{{color:#f0a43c!important}}
.stApp::before,.stApp::after{{content:"";position:fixed;top:80px;bottom:30px;width:12px;pointer-events:none;z-index:0;background:repeating-linear-gradient(180deg,rgba(255,255,255,.35) 0 1px,transparent 1px 38px)}}
.stApp::before{{left:3px}} .stApp::after{{right:3px}}</style>""", unsafe_allow_html=True)

# ---- Header (filled in below once the scanner helpers exist) ----------------------
header_box = st.container()


# ---- Data helpers -------------------------------------------------------------
@st.cache_data(ttl=2, show_spinner=False)
def cached_book(sym: str):
    return render_order_book(sym, limit=50)


@st.cache_data(ttl=2, show_spinner=False)
def cached_trades(sym: str):
    return render_time_and_sales(sym, limit=100)


def score_mt5_group(symbols):
    """Returns (results, notice). MT5 only exists on Windows, so on the cloud
    server this gives ONE friendly notice instead of one warning per symbol."""
    results, errors = [], []
    for sym in symbols:
        try:
            df = get_mt5_data(sym, "H1")
            if df is not None and len(df) > 60:
                res = score_symbol(df, timeframe_label="H1")
                res["symbol"] = sym
                results.append(res)
        except RuntimeError as e:
            if "not available" in str(e):
                return [], ("This watchlist needs MetaTrader 5 (Windows). It is not available on the "
                            "cloud server - run the dashboard locally with MT5 open to fill it. "
                            "The chart on the right still works.")
            errors.append(f"{sym}: {e}")
        except Exception as e:
            errors.append(f"{sym}: {e}")
    return results, ("; ".join(errors) if errors else "")


from modules.page_bg import (   # background scan / workers / caches, moved out of main.py (M7)
    _peer_frames, _peers_for, scan_crypto_group, _bg, _scan_store, _tg_sent, get_tf_stats, _ws_universe, DAY_SYMBOLS, _dayplan_watch, _dayplan_events, _smt_events, build_ws_payload,
)


@st.cache_data(ttl=300, show_spinner=False)
def _scan_cached(symbols: tuple, tf: str):
    return scan_crypto_group(list(symbols), tf)


# ---- Compact watchlist ----------------------------------------------------------
def _nearest(levels, price, below):
    vals = []
    for x in levels or []:
        try:
            vals.append(float(x))
        except (TypeError, ValueError):
            pass
    cand = [v for v in vals if (v < price if below else v > price)]
    if not cand:
        return None
    return max(cand) if below else min(cand)


def watchlist_html(rows):
    out = []
    for r in sorted(rows, key=lambda r: -r["score"]):
        score, mx = int(r["score"]), int(r["max_score"])
        ratio = score / mx if mx else 0
        col = "#0ecb81" if ratio >= 0.75 else ("#f0b90b" if ratio >= 0.5 else "#848e9c")
        stars = "★" * score + "☆" * (mx - score)
        bias = str(r["trend_bias"])
        b = bias.lower()
        arrow, bcol = ("▲", "#0ecb81") if "bull" in b or "up" in b else (
            ("▼", "#f6465d") if "bear" in b or "down" in b else ("◆", "#848e9c"))
        reasons = ", ".join(r["reasons"]) if r["reasons"] else "no signals"
        sup = _nearest(r.get("supports"), r["price"], True)
        res = _nearest(r.get("resistances"), r["price"], False)
        sr = f"S {fmt_price(sup) if sup else '-'} &middot; R {fmt_price(res) if res else '-'}"
        out.append(
            "<div style='border-bottom:1px solid #2b3139;padding:5px 2px'>"
            "<div style='display:flex;justify-content:space-between;font-size:13px'>"
            f"<b>{html.escape(str(r['symbol']))}</b><span>{fmt_price(r['price'])}</span></div>"
            "<div style='display:flex;justify-content:space-between;font-size:12px'>"
            f"<span style='color:{col}'>{stars} {score}/{mx}</span>"
            f"<span style='color:{bcol}'>{arrow} {html.escape(bias)}</span></div>"
            f"<div style='font-size:11px;color:#848e9c'>{trade_chip_html(str(r['trade_type']))}"
            f" &middot; {html.escape(reasons)}</div>"
            f"<div style='font-size:11px;color:#848e9c'>{sr}</div></div>"
        )
    return "".join(out)


def render_watchlist(results, notice, key):
    """Trade-type filter sits right above the list it filters."""
    selected = st.multiselect(L("Trade type"), TRADE_TYPES, default=TRADE_TYPES, key=f"tt_{key}")
    filtered = [r for r in results if r["trade_type"] in selected]
    if notice:
        st.caption(notice)
    elif not filtered:
        st.info(L("No symbols match the current filter."))
    else:
        st.markdown(watchlist_html(filtered), unsafe_allow_html=True)
    return filtered


def _stars(n, mx):
    return "\u2605" * n + "\u2606" * (mx - n)


def render_scanner(results, notice, key):
    """Scanner watchlist. Each coin = one row: FULL SYMBOL first, price, stars,
    direction, trade type, then coloured strategy tag boxes. The Arabic
    analysis sits in a collapsed expander under the row. The trade-type filter
    is tucked away in a collapsed expander at the bottom."""
    selected = st.session_state.get(f"tt_{key}", TRADE_TYPES)
    filtered = [r for r in results if r["trade_type"] in selected]
    if notice:
        st.caption(notice)
    if not filtered and not notice:
        st.info(_xl("لا توجد رموز مطابقة للفلتر الحالي.", "No symbols match the current filter."))
    for r in sorted(filtered, key=lambda r: (-r["score"], r["symbol"])):
        arrow, acol = {"bullish": ("\u25B2", "#0ecb81"), "bearish": ("\u25BC", "#f6465d")}.get(r["direction"], ("\u25C6", "#848e9c"))
        ratio = r["score"] / r["max_score"] if r["max_score"] else 0
        scol = "#0ecb81" if ratio >= 0.57 else ("#f0b90b" if ratio >= 0.28 else "#848e9c")
        st.markdown(
            "<div style='border-top:1px solid #2b3139;padding:6px 2px 2px 2px'>"
            "<div style='display:flex;justify-content:space-between;align-items:baseline'>"
            f"<span style='font-size:15px;font-weight:700'>{html.escape(r['symbol'])}</span>"
            f"<span style='font-size:12px;color:#848e9c'>{fmt_price(r['price'])}</span></div>"
            "<div style='display:flex;justify-content:space-between;align-items:center;margin:2px 0'>"
            f"<span style='color:{scol};font-size:12px'>{_stars(r['score'], r['max_score'])}</span>"
            f"<span style='color:{acol};font-size:12px'>{arrow} {dir_name(r['direction'])}</span>"
            f"<span>{trade_chip_html(r['trade_type'])}</span></div>"
            f"<div>{tags_html(r['signals'], tv_link(r['symbol'], r['timeframe']))}</div></div>",
            unsafe_allow_html=True,
        )
        with st.expander(_xl("التحليل", "Analysis")):
            explain_symbol(r)
    with st.expander(L("Trade type filter")):
        st.multiselect(_xl("نوع الصفقة", "Trade type"), TRADE_TYPES, default=TRADE_TYPES, key=f"tt_{key}")
    st.caption(_xl("النجوم = عدد عائلات الإشارات المتفقة من 7. المربعات الملونة = الاستراتيجية التي أعطت الإشارة.",
                   "Stars = how many of the 7 signal families agree. Coloured boxes = the strategy that gave the signal."))
    return filtered


def _rtl(lines, bullets=True):
    items = "".join(f"<li>{html.escape(x)}</li>" for x in lines) if bullets else "".join(f"<div>{html.escape(x)}</div>" for x in lines)
    body = f"<ul style='margin:2px 0;padding-inline-start:18px'>{items}</ul>" if bullets else items
    d_, a_ = ("rtl", "right") if _ui_lang() == "ar" else ("ltr", "left")
    return f"<div dir='{d_}' style='text-align:{a_};font-size:13px'>{body}</div>"


def explain_symbol(r):
    """The 'why was this flagged' panel - in the page language (Arabic or English)."""
    tf = tf_name(r["timeframe"])
    ar_ = _ui_lang() == "ar"
    d_, a_ = ("rtl", "right") if ar_ else ("ltr", "left")
    st.markdown(
        (f"<div dir='{d_}' style='text-align:{a_}'><b>{html.escape(r['symbol'])}</b> &middot; السعر {fmt_price(r['price'])} "
         f"&middot; فحص {tf} &middot; {dir_name(r['direction'])} &middot; {r['score']}/{r['max_score']} نجوم "
         f"&middot; {trade_chip_html(r['trade_type'])}</div>") if ar_ else
        (f"<div dir='{d_}' style='text-align:{a_}'><b>{html.escape(r['symbol'])}</b> &middot; Price {fmt_price(r['price'])} "
         f"&middot; {tf} scan &middot; {dir_name(r['direction'])} &middot; {r['score']}/{r['max_score']} stars "
         f"&middot; {trade_chip_html(r['trade_type'])}</div>"), unsafe_allow_html=True)
    if not r["signals"]:
        st.markdown(_rtl([_xl("إشارات مختلطة أو غير موجودة حاليا - لا يوجد ما يُنفَّذ.", "Mixed or no signals right now - nothing to act on.") if not r.get("mixed")
                          else _xl("الأدلة الصاعدة والهابطة تلغي بعضها - لا يوجد اتجاه مسيطر.", "The bullish and bearish evidence cancel each other - no dominant direction.")], bullets=False), unsafe_allow_html=True)
    else:
        rows = []
        for s_ in r["signals"]:
            name, detail = signal_ar(s_)
            rows.append(f"[{tag_for(s_)[0]}] {name}: {detail}")
        st.markdown(_rtl(rows), unsafe_allow_html=True)
    if r.get("against"):
        st.markdown(_rtl([_xl("ضد الاتجاه: " + "، ".join(signal_ar(a)[0] for a in r["against"]),
                              "Against the direction: " + ", ".join(signal_ar(a)[0] for a in r["against"]))], bullets=False), unsafe_allow_html=True)
    if r["htf"]:
        st.markdown(f"<div dir='{d_}' style='text-align:{a_}'><b>{_xl('الفريمات الأعلى', 'Higher timeframes')}</b></div>", unsafe_allow_html=True)
        st.markdown(_rtl(htf_lines_ar(r)), unsafe_allow_html=True)
    plan = None
    if r["direction"] in ("bullish", "bearish"):
        plan = build_trade_plan({**r, "trend_bias": r["direction"]})
        side = _xl("شراء" if plan["direction"] == "Long" else "بيع", "Long" if plan["direction"] == "Long" else "Short")
        st.markdown(
            (f"<div dir='{d_}' style='text-align:{a_}'><b>الخطة ({side})</b> - دخول {n_(plan['entry'])} - وقف {n_(plan['stop_loss'])} - "
             f"هدف 1 {n_(plan['take_profits'][0])} / هدف 2 {n_(plan['take_profits'][1])} / هدف 3 {n_(plan['take_profits'][2])}</div>") if ar_ else
            (f"<div dir='{d_}' style='text-align:{a_}'><b>Plan ({side})</b> - entry {plan['entry']} - stop {plan['stop_loss']} - "
             f"target 1 {plan['take_profits'][0]} / target 2 {plan['take_profits'][1]} / target 3 {plan['take_profits'][2]}</div>"),
            unsafe_allow_html=True)
        st.markdown(f"<div dir='{d_}' style='text-align:{a_}'><b>{_xl('السيناريوهات', 'Scenarios')}</b></div>", unsafe_allow_html=True)
        st.markdown(_rtl(scenarios_ar(r)), unsafe_allow_html=True)
    if r["symbol"] in TV_SYMBOL_MAP or "-" in r["symbol"]:
        try:
            svg = chart_svg(get_klines(r["symbol"], r["timeframe"], 300), r, plan)
        except Exception:
            svg = ""
        if svg:
            b64 = base64.b64encode(svg.encode('utf-8')).decode('ascii')
            st.markdown(f"<img style='width:100%;max-width:640px' src='data:image/svg+xml;base64,{b64}'/>", unsafe_allow_html=True)
            st.caption(_xl("رسم تقريبي للسيناريو: الشموع الأخيرة + مناطق الإشارات + الدخول/الوقف/الأهداف (الخط الأصفر = مسار الهدف الأول).",
                           "Rough sketch of the scenario: the latest candles + signal zones + entry/stop/targets (the yellow line = the path to the first target)."))
        st.link_button(_xl("افتح الشارت على TradingView", "Open the chart on TradingView"), tv_link(r["symbol"], r["timeframe"]))
    if r.get("errors"):
        st.caption(_xl("ملاحظات الكواشف: ", "Detector notes: ") + "; ".join(r["errors"]))


def fire_alerts(filtered):
    """Banners show on every refresh; the beep only for signals not alerted before."""
    seen = st.session_state.setdefault("alerted", set())
    strong = {(r["symbol"], r["score"]) for r in filtered if r["score"] >= ALERT_SCORE_THRESHOLD}
    is_new = bool(strong - seen)
    seen |= strong
    check_and_fire_alerts(filtered, play_sound=(play_sound and is_new))


# ---- Crypto order-flow panels ----------------------------------------------------
# st.fragment lets just these panels refresh every few seconds without
# re-running the heavy scanner. Older Streamlit versions fall back to the
# normal page auto-refresh.
_fragment = getattr(st, "fragment", None)


def live_fragment(fn):
    if _fragment is None:
        return fn
    return _fragment(run_every=f"{fast_secs}s")(fn)


def get_tape(sym):
    """Classified trades + 'is_new' flash flags + absorption marks. The DOM and
    Time&Sales panels both call this; calls within 1.5 s share one result so
    the 'new print' flags are consumed only once."""
    cache = st.session_state.setdefault("tape_cache", {})
    hit = cache.get(sym)
    if hit and time.time() - hit[0] < 1.5:
        return hit[1]
    mem = st.session_state.setdefault("tape_mem", {}).setdefault(sym, TapeMemory())
    t = classify_trades(cached_trades(sym), smart_mult=smart_mult, whale_mult=smart_mult * 2.5)
    t = mem.mark(t)
    t = mark_absorption(t, vol_mult=absorb_mult)
    cache[sym] = (time.time(), t)
    return t


@live_fragment
def render_dom(sym):
    st.markdown(f"**Depth of Market** &middot; {html.escape(sym)}", unsafe_allow_html=True)
    try:
        bids, asks = cached_book(sym)
    except Exception as e:
        st.warning(f"Order book unavailable: {e}")
        return None
    try:
        tape = get_tape(sym)
    except Exception:
        tape = None
    ladder = build_ladder(bids, asks, depth=12)
    mem = st.session_state.setdefault("dom_mem", {}).setdefault(sym, DomMemory())
    absorb_prices = set()
    if tape is not None and not tape.empty and "absorb" in tape.columns:
        absorb_prices = {round(float(p), 8) for p in tape.loc[tape["absorb"], "price"]}
    st.markdown(
        ladder_html(ladder, big_mult=big_order_mult, hits=hits_from(tape),
                    changes=mem.changes(ladder), absorb_prices=absorb_prices),
        unsafe_allow_html=True,
    )
    st.caption(L("★ glowing = big resting order (blinks white when trades hit it). "
               "Level flash = just traded. Blue outline = size grew."))
    return bids, asks


@live_fragment
def render_trades(sym):
    st.markdown(L("**Time & Sales** &middot; Smart / Whale / Absorb"), unsafe_allow_html=True)
    try:
        trades = get_tape(sym)
        ab = ""
        if not trades.empty and "absorb" in trades.columns and trades["absorb"].any():
            dirs = trades.loc[trades["absorb"], "absorb_dir"]
            ab = "by " + dirs.mode().iat[0]
        st.markdown(stats_html(tape_stats(trades), ab), unsafe_allow_html=True)
        st.markdown(trades_html(trades, max_rows=20), unsafe_allow_html=True)
        st.markdown(LEGEND_HTML, unsafe_allow_html=True)
        return trades
    except Exception as e:
        st.warning(f"Time & sales unavailable: {e}")
        return None


def render_limit_tracking(sym, book, trades):
    st.markdown(L("**Limit Tracking** &middot; big limit orders placed / pulled / filled"), unsafe_allow_html=True)
    if book is None:
        return
    trackers = st.session_state.setdefault("limit_trackers", {})
    tracker = trackers.get(sym)
    if tracker is None or tracker.big_mult != big_order_mult:
        tracker = trackers[sym] = LimitTracker(big_mult=big_order_mult)
    tracker.update(book[0], book[1], trades)
    st.markdown(limit_events_html(tracker.events_df()), unsafe_allow_html=True)
    st.caption(L("Snapshot based (compares each refresh), so quick spoof-and-cancel "
               "inside one refresh is not seen. PULLED = vanished without trading."))


@st.cache_data(ttl=300, show_spinner=False)
def _world_news():
    from modules.world_news import fetch_world
    return fetch_world()


def _smt_chips(lang):
    try:
        from modules import intermarket as _IM
        return _IM.chips(_smt_events(), ar=(lang == "ar"))
    except Exception:
        return []


MINI_CSS = """<style>
.mini{height:150px;min-height:60px;resize:vertical;overflow:auto;border:1px solid #2b3139;border-radius:6px;background:#161a1e}
.mini table{width:100%;border-collapse:collapse;font-size:11px;font-family:monospace}
.mini th{color:#848e9c;font-weight:400;text-align:left;padding:2px 4px;position:sticky;top:0;background:#161a1e}
.mini td{padding:2px 4px;white-space:nowrap;border-top:1px solid #20262c}
.mini a.tg{display:inline-block;border-radius:3px;padding:0 4px;margin-right:2px;font-size:10px;font-weight:600;font-family:sans-serif;border:0;cursor:help;text-decoration:none}
.mini a{color:#4aa3ff;text-decoration:none;border:1px solid #2b3139;border-radius:3px;padding:0 4px}
div[data-testid="stSelectbox"] div[data-baseweb="select"]>div{min-height:30px;font-size:12px}
div[data-testid="stVerticalBlock"]{gap:.35rem}
</style>"""


def _spark_svg(vals, pl, long_, w=64, h=20):
    """Tiny price-shape picture: recent closes + entry/SL/TP1 lines, as an <img> data URI."""
    if not vals or len(vals) < 5:
        return ""
    lv = list(vals) + [pl["entry"], pl["stop"], pl["tps"][0]]
    lo, hi = min(lv), max(lv)
    span = (hi - lo) or 1.0
    y = lambda v: round(h - 1 - (v - lo) / span * (h - 2), 1)
    pts = " ".join(f"{round(i * (w - 1) / (len(vals) - 1), 1)},{y(v)}" for i, v in enumerate(vals))
    col = "#0ecb81" if long_ else "#f6465d"
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}'>"
           f"<line x1='0' x2='{w}' y1='{y(pl['tps'][0])}' y2='{y(pl['tps'][0])}' stroke='#0ecb81' stroke-dasharray='2 2' stroke-width='.8'/>"
           f"<line x1='0' x2='{w}' y1='{y(pl['stop'])}' y2='{y(pl['stop'])}' stroke='#f6465d' stroke-dasharray='2 2' stroke-width='.8'/>"
           f"<polyline fill='none' stroke='{col}' stroke-width='1.2' points='{pts}'/></svg>")
    return f"<img width='{w}' height='{h}' src='data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}'/>"


TT_OPTIONS = {"All": ("All", "الكل"), "Scalp": ("Scalp", "سكالب"), "Day Trade": ("Day trade", "داي تريد"), "Swing": ("Swing", "سوينج"), "Position": ("Position", "بوزيشن")}   # (English, Arabic): pick with _ui_lang()


def _strength_bar(pct):
    col = "#0ecb81" if pct >= 60 else ("#f0b90b" if pct >= 40 else "#848e9c")
    return (f"<span style='display:inline-block;width:34px;height:6px;background:#2b3139;border-radius:3px;vertical-align:middle'>"
            f"<span style='display:block;width:{pct}%;height:6px;background:{col};border-radius:3px'></span></span> <b style='color:{col}'>{pct}%</b>")


def mini_scanner_html(mini, side="All", ttype="All", n=7):
    rows, seen = [], set()
    for e in sorted(mini, key=lambda x: (-x.get("score", 0), x.get("symbol", ""))):
        if side != "All" and e["direction"] != ("bullish" if side == "Long" else "bearish"):
            continue
        if ttype != "All" and e.get("ttype") != ttype:
            continue
        pl = e["plan"]
        key = (e["symbol"], e["direction"], e.get("tfk"))
        if key in seen:
            continue
        seen.add(key)
        long_ = e["direction"] == "bullish"
        pct = round(100 * e.get("score", 0) / max(1, e.get("max", 7)))
        strat = "".join(f"<a class='tg' href='{html.escape(e.get('tv', '#'), quote=True)}' target='_blank' rel='noopener noreferrer' "
                        f"title='{html.escape(t[3] if len(t) > 3 else '', quote=True)}' style='background:{html.escape(t[1])};color:{html.escape(t[2])}'>{html.escape(t[0])}</a>"
                        for t in (e.get("tags") if _ui_lang() == "ar" else (e.get("tags_en") or []))[:4]) or "-"   # tags_en: English text + tooltip (the payload itself is Arabic)
        rows.append(
            "<tr>"
            f"<td><b>{html.escape(e['symbol'])}</b> <span style='color:#848e9c'>{html.escape(str(e.get('tfk', '')))}</span></td>"
            f"<td style='color:{'#0ecb81' if long_ else '#f6465d'};font-weight:700'>{'Long' if long_ else 'Short'}</td>"
            f"<td style='color:#f0b90b'>{html.escape(str(e.get('trade', '')) if _ui_lang() == 'ar' else trade_name(str(e.get('ttype', '')), False))}</td>"
            f"<td>{strat}</td><td>{_spark_svg(e.get('spark'), pl, long_)}</td>"
            f"<td style='color:#f6465d'>{fmt_price(pl['stop'])}</td>"
            f"<td style='color:#0ecb81'>{fmt_price(pl['tps'][0])}</td>"
            f"<td>{_strength_bar(pct)}</td>"
            f"<td><a href='{html.escape(e.get('tv', '#'), quote=True)}' target='_blank' rel='noopener noreferrer'>TV</a></td></tr>"
        )
        if len(rows) >= n:
            break
    if not rows:
        return f"<div class='mini' style='padding:6px;color:#848e9c;font-size:11px'>{'لا توجد صفقات جاهزة الآن' if _ui_lang() == 'ar' else 'No ready trades right now'}</div>"
    return ("<div class='mini'><table><tr><th>Pair</th><th>Side</th><th>Type</th><th>Setup</th><th>Shape</th><th>SL</th><th>TP1</th><th>Strength</th><th></th></tr>"
            + "".join(rows) + "</table></div>")


def site_icon_b64_uri(domain):
    d = site_icon_b64(domain)
    return f"data:image/x-icon;base64,{d}" if d else ""


def _logo_data_uri():
    import mimetypes
    for pth in (Path("assets/logo.png"), Path("assets/logo.jpg"), Path("assets/logo.svg")):
        if pth.exists():
            mt = mimetypes.guess_type(str(pth))[0] or "image/png"
            return f"data:{mt};base64," + base64.b64encode(pth.read_bytes()).decode()
    return ""


from modules.context_feeds import calendar_rows as _calendar_rows   # moved to modules/context_feeds.py (2026-11-20, shared with TIA)


from modules import asset_classes as _AC   # the dropdown options (also used by render_header)


try:   # the main logo (barcode) for the folded header
    _LOGO_SVG = (Path(__file__).with_name("modules") / "xpix_barcode.svg").read_text(encoding="utf-8").strip()
except Exception:
    _LOGO_SVG = "<b>XP<i>i</i>X</b>"


def render_header():
    """ONE header row: XPiX strip (logo | resources menu | news | next event | Cairo + New York clocks | world map) | page tabs |
    language | focus. Focus mode folds the strip away so the Workspace gets the whole screen. Returns the container for the page tabs."""
    focus = bool(st.session_state.get("focus_ws"))
    with st.container(key="hdr"):
        h_main, h_nav, h_set, h_foc = st.columns([5.4, 4.2, 0.62, 0.32], vertical_alignment="center", gap="small")
    with h_main:
        if focus:   # folded: only a small mark
            st.markdown("<div class='xpix-mini'>" + _LOGO_SVG + "</div>", unsafe_allow_html=True)   # the same barcode logo, just smaller
        else:
            links = []
            for name, url in EXTERNAL_LINKS.items():
                dom = url.split("//", 1)[-1].split("/", 1)[0].replace("www.", "")
                if name == "Finviz Patterns":
                    links.append({"name": "Finviz", "url": url, "icon": site_icon_b64_uri("finviz.com"),
                                  "patterns": [{"name": L(k), "url": FINVIZ_PATTERN_URL.format(signal=v)} for k, v in FINVIZ_PATTERNS.items()]})
                else:
                    links.append({"name": name, "url": url, "icon": site_icon_b64_uri(dom)})
            try:
                news = get_latest_news(category="general", limit=15)
            except Exception:
                news = []
            try:
                cal = _calendar_rows()
            except Exception:
                cal = []   # the strip then tries to fetch the calendar itself in the browser
            render_header_bar(_logo_data_uri(), links, news, cal=cal, ar=_ui_lang() == "ar", theme=UI_THEME, theme_vars=_ui_vars(UI_THEME))
    with h_set:   # ONE small button for theme + language (a popover); Alt+T / Alt+L cycle them
        from modules.i18n import LANGS as _LANGS
        _lng = st.session_state.get("ws_lang", "en")
        _dot = {"classic": "◐", "lux": "◑", "hud": "◒"}.get(UI_THEME, "◓")
        with st.popover(f"{_dot} {_LANGS.get(_lng, ('', 'EN'))[1]}", help=L("Theme and language (Alt+T / Alt+L)")):
            st.caption(L("Theme"))
            st.radio(L("Theme"), [k for k in _BUILT_THEMES], key="ui_theme", format_func=lambda k: L(dict(_UI_THEMES)[k]), label_visibility="collapsed")
            st.caption(L("Material"))
            st.selectbox(L("Material"), _MATS, key="ui_mat", label_visibility="collapsed",
                         format_func=lambda k: L({"auto": "Auto (from the theme)", "none": "None", "steel": "Brushed steel", "paper": "Paper", "wood": "Wood", "fabric": "Fabric", "glass": "Glass", "carbon": "Carbon fibre"}[k]))
            st.caption(L("Language"))
            _ok = [k for k, v in _LANGS.items() if v[2]]
            _pick = st.radio(L("Language"), _ok, index=_ok.index(_lng) if _lng in _ok else 0, format_func=lambda k: _LANGS[k][0], label_visibility="collapsed", key="lang_pick")
            if _pick != _lng:
                st.session_state["ws_lang"] = _pick
                st.query_params["lang"] = _pick
                st.rerun()
            st.caption(L("Coming") + ": " + " · ".join(v[0] for v in _LANGS.values() if not v[2]))
            st.toggle(L("Info strip"), value=True, key="info_strip", help=L("The thin line under the header: educational note, data sources, last lab run"))
    with h_foc:
        if st.button("⤡" if focus else "⤢", key="focus_btn", help=L("Fold the header away: the Workspace gets the whole screen (Alt+F)")):
            st.session_state["focus_ws"] = not focus
            st.rerun()
    return h_nav
    # the ready-trades table now lives inside the Workspace (movable widget); macro watchlist is in the sidebar
    with st.sidebar.expander(L("Macro watchlist"), expanded=False):
        st.markdown(macro_html(), unsafe_allow_html=True)
    with st.sidebar.expander(L("US economy (FRED)"), expanded=False):
        st.caption(L("Monthly/daily official data, not live prices. Needs FRED_API_KEY in Secrets."))
        for r_ in _fred_rows():
            st.write(f"**{r_['label']}**: {r_['value'] if r_['value'] is not None else 'n/a'}  {r_['date']} {('- ' + r_['note']) if r_['note'] else ''}")


@st.cache_data(ttl=3600, show_spinner=False)
def _fred_rows():
    from modules.fred_feed import snapshot
    return snapshot()


from modules.context_feeds import cmc_data as _cmc_data, stock_fund as _stock_fund   # moved to modules/context_feeds.py


def _stock_tickers():
    if asset_cls == "Stocks":
        t = tuple(s.split("-")[0] for s in ACTIVE_SYMBOLS[:10] if s.split("-")[0].isalpha())
        if t:
            return t
    return ()


from modules.context_feeds import macro_fund as _macro_fund   # moved to modules/context_feeds.py


@st.cache_data(ttl=30, show_spinner=False)
def _macro_rows():
    return fetch_macro()


def macro_html():
    box = "border:1px solid #2b3139;border-radius:6px;background:#161a1e;padding:4px 8px;font-size:11px"
    key = api_key()
    hint = (f"<div style='{box};color:#848e9c'><b style='color:#eaecef'>Macro watchlist</b> "
            "(Gold / Oil / EURUSD / DXY): add a free TwelveData key as <code>TWELVEDATA_API_KEY</code> in config.py or Streamlit secrets.</div>")
    try:
        rows = _macro_rows()
        if not key and not rows:
            return hint
    except Exception as e:
        return f"<div style='{box};color:#f6465d'>Macro watchlist unavailable: {html.escape(str(e))}</div>"
    cells = []
    for r in rows:
        if not r["ok"]:
            cells.append(f"<tr><td>{html.escape(r['name'])}</td><td colspan='2' style='color:#848e9c'>n/a</td></tr>")
            continue
        col = "#0ecb81" if (r["pct"] or 0) >= 0 else "#f6465d"
        pct_txt = "" if r["pct"] is None else f"{r['pct']:+.2f}%"
        cells.append(f"<tr><td>{html.escape(r['name'])}</td><td style='text-align:right'>{fmt_price(r['price'])}</td>"
                     f"<td style='text-align:right;color:{col}'>{pct_txt}</td></tr>")
    return f"<div style='{box}'><table style='width:100%;border-collapse:collapse;font-family:monospace'>" + "".join(cells) + "</table></div>"


from modules.asset_classes import CLASSES as ASSET_CLASSES
if "asset_cls" not in st.session_state and st.query_params.get("cls") in ASSET_CLASSES:
    st.session_state["asset_cls"] = st.query_params["cls"]

with header_box:
    try:
        NAV_BOX = render_header()
    except Exception as _e:   # never let a header problem hide the rest of the page
        NAV_BOX = None
        st.error(f"Header error: {type(_e).__name__}: {_e}")


from modules import hot_reload as _hot   # a redeploy can leave OLD copies of modules in memory: reload the stale ones before anything imports from them
try:
    import importlib as _il0
    if _hot.compiled_from_older_source(_hot):   # the helper itself can be an old copy
        _il0.reload(_hot)
    _hot.refresh_changed()
    _hot.refresh()
except Exception:
    pass
# ---- One asset-class dropdown for scanner / ready trades / watchlist ---------------
from modules.asset_classes import CLASSES as ASSET_CLASSES, MARKET_TYPES, MEME_BASES, class_symbols
asset_cls = st.session_state.get("asset_cls", "Crypto")      # the two selectors live at the top of the Chart Scanner tab
market_type = st.session_state.get("market_type", "Spot")
SCAN_SYMBOLS, _ac_msg = class_symbols(asset_cls, CRYPTO_SYMBOLS, mtype=MARKET_TYPES.get(market_type, "SPOT"))
if _ac_msg:
    SCAN_SYMBOLS = list(CRYPTO_SYMBOLS)
ACTIVE_SYMBOLS = list(SCAN_SYMBOLS)   # may contain "Y:" (Yahoo) symbols: the Workspace gets their candles embedded in the page (no live book / tape for them)


def render_universe_controls(_u1, _u2, _u3):
    """Asset class / Market / Universe size: drawn in the ONE Radar filter line (the caller passes the three columns)."""
    _u1.selectbox(L("Asset class"), _AC.CLASSES, key="asset_cls", format_func=L, help=L("Asset class for the Chart Scanner (and the Workspace scan / ready trades)."))
    _u2.selectbox(L("Market"), list(_AC.MARKET_TYPES), key="market_type", format_func=L, help=L("Spot / Perpetual swap / dated Futures (OKX)."))
    _u3.number_input(L("Universe size"), min_value=10, max_value=150, value=24, step=2, key="uni_n", help=L("How many symbols the Radar scans (biggest 24h volume first). More symbols = a longer first load."))
    if st.session_state.get("asset_cls", "Crypto") != "Crypto":
        st.query_params["cls"] = st.session_state["asset_cls"]
    elif "cls" in st.query_params:
        del st.query_params["cls"]
    if _ac_msg:
        st.warning(_ac_msg + " - showing Crypto instead.")


# ---- Filters keep their values when you switch page / tab (owner 2026-10-23: "filters sometimes stop working"): Streamlit deletes the state of widgets
# that are not drawn in a run, so the non-button filter keys are written back at the top of every run.
_KEEP_PREFIX = ("cs_", "fv_f_", "hm_", "perf_", "sm_", "bt_", "sc_", "to_", "lab_", "ac_", "acq_", "fl_", "uni_n", "asset_cls", "market_type", "radar_view")
_BUTTON_KEYS = {"cs_preset_save", "cs_preset_del", "ac_mark", "ac_next", "ac_prev", "ac_undo", "ac_sprev", "ac_snext", "bt_agent_go", "bt_agent_reset", "bt_agent_run", "bt_agent_save", "bt_run", "bt_save", "cs_clear_top", "fl_go", "sc_apply"}   # buttons cannot be set from session state
for _k in list(st.session_state.keys()):
    if isinstance(_k, str) and _k.startswith(_KEEP_PREFIX) and _k not in _BUTTON_KEYS and not _k.startswith(("acc_", "sm_run_", "ac_done")):
        try:
            st.session_state[_k] = st.session_state[_k]
        except Exception:
            pass


# ---- Tabs -------------------------------------------------------------------------
# Page selector instead of st.tabs: st.tabs runs EVERY tab's code on every run (~1100 candle downloads + scans per run, which got
# the app CPU-throttled on Streamlit Cloud). Now only the open page runs. The choice is kept in the URL (?page=) and the session.
# 2026-10-18 (owner): Crypto / Forex / Metals / Stocks / Meme pages removed (the Workspace covers them: watchlist classes, widgets);
# new sections that serve the goal: the honest Lab, the Playbook, and two "soon" sections (AI analyst, alerts & bots).
_PAGES = ["Workspace", "Radar", "Technical Office", "Playbook", "Journal", "AI", "Alerts", "Academy", "Lab Summary", "Research Hub", "Prop Firms", "Spot", "TIA", "Trading", "Lab", "Learn & AI", "Options & macro", "Trade Intelligence Center", "V7", "2.6 Lab", "RSI Heatmap", "X77", "Preview", "Strategy Ledger"]   # 22 = Preview of built-but-unwired items (owner 2026-11-21, Lab hub)   # 23 = Strategy Ledger (owner 2026-11-24, Trading hub next to the Journal)   # 21 = X77 (owner 2026-11-20, Lab hub sub-tab)   # 17 = Trade Intelligence Center (2026-11-10, Learn & AI hub; MR !27 renumbered from 13); 13-15 = hub pages, 16 = options + macro regime (2026-11-09); 4 = Journal (was Stats); 11 = Spot desk (2026-11-06, next to the Radar in the bar); 10 = Prop Firms (added 2026-11-04: inactivity timers, rules, links per account); 8 = Lab Summary; Academy is index 7 (the Workspace guide uses fixed indexes)
_HUBS = {13: [10, 16, 4, 23, 6], 14: [2, 9, 3, 19, 21, 22], 15: [5, 7, 17]}   # 8 (Lab Summary) lives in Technical Office > Lab results (owner 2026-11-09)   # owner 2026-11-09: Workspace, Radar, then three hubs; each hub shows its old pages as one row of sub-tabs
_HUB_OF = {c: h for h, cs in _HUBS.items() for c in cs}
_PAGE_ORDER = [0, 1, 11, 12, 18, 20, 13, 14, 15]   # owner 2026-11-21: V7 (18) back on the top bar with all its parts, next to TIA   # 2026-11-17 sync with main: V7 (18) and 2.6 Lab (19) are sub-tabs of the Lab hub (owner 2026-11-15: fewer top tabs); RSI Heatmap (20) stays on top  #   # 20 = RSI Heatmap (MR !68, 2026-11-14); 19 = 2.6 Lab (own tab, owner 2026-11-13); 18 = V7 (own tab next to TIA, owner 2026-11-12)   # the top bar: Workspace, Radar, Spot (11, its own page with its own tabs: owner 2026-11-09 - keep them, only add / improve), TIA (12, its own page: reviewer decision 2026-11-09), Trading, Lab, Learn & AI


def _nav_to(i):
    """Open page i (an old page index opens its hub with that sub-page selected)."""
    if i == 8:   # Lab Summary now sits on top of Technical Office > Lab results (owner 2026-11-09)
        i = 2
        st.session_state["to_tab"] = "Lab results"
    h = _HUB_OF.get(i)
    st.session_state["page"] = h if h is not None else (i if i in _PAGE_ORDER else 0)
    if h is not None:
        st.session_state[f"hub_{h}"] = i


if "page" not in st.session_state:
    try:
        _nav_to(int(st.query_params.get("page", 0)))
    except (TypeError, ValueError):
        _nav_to(0)
elif st.session_state["page"] not in _PAGE_ORDER:   # a session opened before the hubs existed
    _nav_to(st.session_state["page"])
with (NAV_BOX if NAV_BOX is not None else st.container()):
    PAGE = st.radio(L("Page"), _PAGE_ORDER, format_func=lambda i: L(_PAGES[i]), horizontal=True, key="page", label_visibility="collapsed")
if PAGE in _HUBS:   # one compact row of sub-tabs; PAGE becomes the old page index, so every `if PAGE == N` block below is unchanged
    _hk = f"hub_{PAGE}"
    if st.session_state.get(_hk) not in _HUBS[PAGE]:   # Streamlit drops an undrawn widget's value: come back to the last sub-page used
        st.session_state[_hk] = st.session_state.get("last_" + _hk) if st.session_state.get("last_" + _hk) in _HUBS[PAGE] else _HUBS[PAGE][0]
    with st.container(key="hubnav"):
        PAGE = st.radio(L(_PAGES[PAGE]), _HUBS[PAGE], format_func=lambda i: L(_PAGES[i]), horizontal=True, key=_hk, label_visibility="collapsed")
    st.session_state["last_" + _hk] = PAGE
if str(st.query_params.get("page", "")) != str(PAGE):
    st.query_params["page"] = str(PAGE)
try:   # screen recorder + quick editor: lives in the parent page, so it follows you to every page (owner 2026-11-06)
    from modules.screen_recorder import render as _render_rec
    _render_rec()
except Exception:
    pass
_focus = bool(st.session_state.get("focus_ws"))
try:   # phones: the Workspace frame = about one screen (its widgets scroll inside it); header row wraps into two lines
    _IS_MOBILE = any(k in (st.context.headers.get("User-Agent", "") or "") for k in ("Mobi", "Android", "iPhone"))
except Exception:
    _IS_MOBILE = False
st.markdown(f"""<style>.st-key-page [role="radiogroup"]{{gap:2px 16px;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}}
.st-key-page label{{padding:2px 2px 3px;margin:0;white-space:nowrap}} .st-key-page [data-testid="stRadioOption"] p{{font-size:11px;letter-spacing:.1em;text-transform:uppercase}}
.block-container{{padding-top:{'2.4rem' if _focus else '2.6rem'}!important;padding-bottom:0!important}}   /* clears the Streamlit corner buttons (sidebar >> and the menu) */
[data-testid="stMainBlockContainer"] [data-testid="stElementContainer"]:has(style),[data-testid="stMainBlockContainer"] [data-testid="stElementContainer"]:has(>[data-testid="stEmpty"]){{display:none}}
@keyframes xTabIn{{from{{opacity:0;transform:translateY(-10px);filter:blur(4px)}}to{{opacity:1;transform:none;filter:none}}}}
@keyframes xTabSweep{{from{{background-position:-120% 0}}to{{background-position:220% 0}}}}
.st-key-page label{{animation:xTabIn .65s cubic-bezier(.2,.7,.2,1) both}}
.st-key-page label:nth-child(2){{animation-delay:.08s}} .st-key-page label:nth-child(3){{animation-delay:.16s}} .st-key-page label:nth-child(4){{animation-delay:.24s}}
.st-key-page label:nth-child(5){{animation-delay:.32s}} .st-key-page label:nth-child(6){{animation-delay:.4s}} .st-key-page label:nth-child(7){{animation-delay:.48s}}
.st-key-page [role="radiogroup"]{{background:linear-gradient(100deg,transparent 40%,rgba(240,185,11,.16) 50%,transparent 60%) no-repeat;background-size:60% 100%;animation:xTabSweep 1.6s .5s ease-out both}}
@media (prefers-reduced-motion:reduce){{.st-key-page label,.st-key-page [role="radiogroup"]{{animation:none}}}}
.st-key-gbridge,[data-testid="stElementContainer"]:has(.st-key-gbridge){{position:absolute!important;width:0!important;height:0!important;overflow:hidden!important;margin:0!important}}
[data-testid="stMainBlockContainer"]>div>[data-testid="stVerticalBlock"],[data-testid="stMainBlockContainer"]>[data-testid="stVerticalBlock"]{{gap:.3rem!important}} [data-testid="stMainBlockContainer"] iframe{{display:block}} [data-testid="stHeader"]{{background:transparent;height:2.2rem}}
.st-key-hdr{{margin:0;width:100%!important;box-sizing:border-box;padding:0 6px 0 0;position:relative;background:transparent;border:0}}
.st-key-hdr::before{{content:"";position:absolute;left:0;right:0;top:0;height:{'38px' if _focus else '50px'};background:var(--hdr-bg,linear-gradient(180deg,#0a0d11,#06080b));border:1px solid var(--hdr-line,#1c232b);border-radius:var(--hdr-r,10px);pointer-events:none;z-index:0}}
.st-key-hdr [data-testid="stHorizontalBlock"]{{align-items:flex-start!important;position:relative;z-index:1}}
.st-key-hdr [data-testid="stColumn"]:not(:first-child){{min-height:{'38px' if _focus else '50px'};display:flex;align-items:center}}

.st-key-hdr [data-testid="stColumn"]+[data-testid="stColumn"]{{border-inline-start:1px solid var(--hdr-line,#1c232b);padding-inline-start:8px}}
[data-testid="stPopover"] button{{padding:0 8px;min-height:28px;border:0!important;background:transparent!important;font-size:13px}}
.st-key-focus_btn button{{padding:0 6px;min-height:28px;border:0!important;background:transparent!important;font-size:13px}}
.xpix-mini{{display:flex;align-items:center;height:38px;padding-left:8px}} .xpix-mini svg{{height:26px;width:auto;display:block}}
.xpix-mini rect{{transform-box:fill-box;transform-origin:50% 100%;animation:bcWave 3.2s cubic-bezier(.45,0,.25,1) infinite}}
@keyframes bcWave{{0%,40%,100%{{transform:scaleY(1);fill:#e3e4e8}}12%{{transform:scaleY(.55);fill:#f0b90b}}24%{{transform:scaleY(1.04);fill:#ffe9a3}}}} .xpix-mini i{{font-style:normal;color:{ui_accent}}}

.st-key-ws_lang [role="radiogroup"]{{flex-wrap:nowrap;gap:8px}}
.st-key-ui_theme [role="group"]{{background:transparent!important;border:1px solid var(--hdr-line,#2b3139)!important;min-height:30px;border-radius:6px}}
.st-key-ui_theme [role="group"] *{{color:#c3c9d1!important;font-size:11px}} .st-key-ui_theme svg{{fill:#8a9099}} .st-key-ui_theme [data-baseweb="select"] *{{color:#c3c9d1!important;font-size:11px}}
@media (max-width:640px){{.st-key-hdr{{margin:0;width:100%!important}} .st-key-hdr::before{{height:100%}} .st-key-hdr [data-testid="stHorizontalBlock"]{{flex-wrap:wrap!important;gap:4px!important}}
  .st-key-hdr [data-testid="stColumn"]:nth-child(1),.st-key-hdr [data-testid="stColumn"]:nth-child(2){{flex:1 1 100%!important;width:100%!important;min-width:100%!important}}
  .st-key-hdr [data-testid="stColumn"]:nth-child(3),.st-key-hdr [data-testid="stColumn"]:nth-child(4){{flex:0 0 auto!important;width:auto!important;min-width:0!important}}
  .block-container{{padding-left:.4rem!important;padding-right:.4rem!important}} .st-key-page [data-testid="stRadioOption"] p{{font-size:12px}}}} .st-key-ws_lang p{{font-size:11px}}
[data-testid="stExpander"] summary{{background:#0b0f14!important;color:#e6e9ee!important}} [data-testid="stExpander"] summary p{{color:#e6e9ee!important}} .st-key-page [data-testid="stRadioOption"]>div>div:first-child:not([data-testid]){{display:none!important}} .st-key-page [data-testid="stRadioOption"] p{{color:#c3c9d1;opacity:1}} .st-key-page [data-testid="stRadioOption"]{{opacity:1}}
.st-key-page label:has(input:checked){{border-bottom:2px solid {ui_accent}}} .st-key-page label:has(input:checked) p{{color:{ui_accent};font-weight:600}}</style>""",
            unsafe_allow_html=True)
if PAGE != 0:   # every page after the Workspace (owner 2026-11-09): full width, tight spacing, small framed metrics, hub sub-tabs as one row
    st.markdown(f"""<style>.block-container{{max-width:100%!important;padding-left:1rem!important;padding-right:1rem!important}}
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"]{{gap:.45rem}} [data-testid="stHorizontalBlock"]{{gap:.5rem!important}}
[data-testid="stMetric"]{{background:rgba(255,255,255,.02);border:1px solid #1c232b;border-radius:6px;padding:4px 10px}} [data-testid="stMetricValue"]{{font-size:1.15rem!important}} [data-testid="stMetricLabel"] p{{font-size:11px!important}}
.stApp h1{{font-size:1.35rem}} .stApp h2{{font-size:1.15rem}} .stApp h3{{font-size:1rem}} [data-testid="stButtonGroup"] button{{min-height:26px;padding:0 10px}} [data-testid="stButtonGroup"] button p{{font-size:12px}}
.st-key-hubnav [role="radiogroup"]{{gap:2px 4px;flex-wrap:wrap;border-bottom:1px solid #1c232b}} .st-key-hubnav label{{padding:3px 12px;margin:0;border-radius:6px 6px 0 0;white-space:nowrap}}
.st-key-hubnav [data-testid="stRadioOption"]>div>div:first-child:not([data-testid]){{display:none!important}} .st-key-hubnav [data-testid="stRadioOption"] p{{font-size:12px;color:#c3c9d1}}
.st-key-hubnav label:has(input:checked){{background:rgba(240,185,11,.10);border-bottom:2px solid {ui_accent}}} .st-key-hubnav label:has(input:checked) p{{color:{ui_accent};font-weight:600}}</style>""", unsafe_allow_html=True)

def _office_control_room():
    """Technical Office v2 header (control-room layout, owner's reference images 2026-10-22): gate, headline KPIs, best per
    trading style, warnings. Every number comes from data/strategy_lab.json (modules/office_kpi.py); nothing is estimated."""
    from modules import office_kpi as _OK
    d = _OK.load(); s = _OK.summary(d)
    if not s:
        return
    b = s["best"] or {}
    c = st.columns(6)
    c[0].metric(L("Passed the evidence gate"), f"{s['passed']} / {s['candidates']}", help=L("n >= 100, t > 3, net > 0 and both halves positive after 0.1R costs"))
    c[1].metric(L("Detectors in the lab"), s["detectors"])
    c[2].metric(L("OFF (no longer decide a trade)"), len(s["off"]), help=", ".join(s["off"]) or "-")
    c[3].metric(L("Best net avg R (n >= 100)"), f"{b.get('net', 0):+.3f}" if b else "-", help=(f"{b['key']} {b['tf']} · n {b['n']} · vs random {b['vs_random']:+.3f}" if b else None))
    c[4].metric(L("Cost per trade"), f"{_OK.COST_R}R")
    c[5].metric(L("Last lab run"), s["built"] or "-", help=f"{s['symbols']} symbols")
    sty = _OK.styles(d)
    lbl = {"Scalp": L("Scalp"), "Day": L("Day trade"), "Swing": L("Swing"), "Position": L("Position")}
    st.markdown("| " + " | ".join([L("Style"), L("Lab timeframes"), L("Strongest detector (n >= 100)"), "n", L("net avg R"), L("vs random")]) + " |\n|---|---|---|---|---|---|\n"
                + "\n".join(f"| {lbl[x['style']]} | {x['tfs']} | {(x['key'] + ' ' + x['tf']) if x['key'] else '-'} | {x['n'] or '-'} | "
                            f"{'' if x['net'] is None else format(x['net'], '+.3f')} | {'' if x['vs_random'] is None else format(x['vs_random'], '+.3f')} |" for x in sty))
    warn = []
    pb_dates = [k for k in _md_sections("STRATEGIES.md") if k.startswith("Lab results ")]
    if pb_dates and s["built"] and s["built"] not in pb_dates[0]:
        warn.append(L("The Playbook summary is older than the last lab run") + f" ({pb_dates[0].split(' ')[2]} / {s['built']})")
    if not s["passed"]:
        warn.append(L("Nothing has passed the evidence gate yet: every signal is a suggestion, not evidence."))
    for w in warn:
        st.warning(w)
    st.caption(L("Educational, not investment advice. Source: data/strategy_lab.json (weekly lab)."))
    st.divider()


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
    for p in sorted((Path(__file__).resolve().parent / "data").glob("holdout_*.json")):
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


def _bt_agent(sym, tf):
    """Backtest agent (owner 2026-10-22): explain the idea in words, the agent turns it into rules, the dashboard tests them."""
    import json
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


def _office_ops():
    from modules import office_ui as U
    st.markdown(U.CSS, unsafe_allow_html=True)
    wf = U.workflows()
    rows = [[U.esc(L(w["name"])), U.esc(w["file"]), U.esc(w["schedule"] or "-"), "✓" if w["manual"] else "",
             U.badge(L("writes to the repo"), "warn") if w["writes"] else ""] for w in wf]
    st.markdown(U.table([L("Workflow"), L("File"), L("Schedule (UTC cron)"), L("Manual run"), L("Repo writes")], rows), unsafe_allow_html=True)
    st.caption(L("Protecting main is on hold until the workflows that push to main open a pull request instead (owner rule: protect only if nothing breaks)."))


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


def _strat_name(k):
    """Detector / strategy filter name in the page language (Arabic short names from chart_explain.FLAG_AR)."""
    from modules.chart_scan import STRATEGY_FILTERS as _SF
    return _CX.FLAG_AR.get(k, _SF[k][0]) if _ui_lang() == "ar" and k in _CX.FLAG_AR else _SF[k][0]


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
        ho = _json.loads((Path(__file__).resolve().parent / "data" / f"holdout_{k}_1d.json").read_text(encoding="utf-8"))
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


def render_soon_page(i):
    if i == 5:
        st.subheader(L("AI Analyst (planned)"))
        st.markdown(L("- Explains each setup in plain words (why, risk, what cancels it), reads it aloud - phase 1 (read-aloud) is already in the Workspace.\n"
                      "- Answers questions about the open chart using the stored short analysis, not raw candles (token budget: cached per setup, daily cap).\n"
                      "- Weekly summary of your journal: what works for YOU, by school / timeframe / session."))
    else:
        st.subheader(L("Alerts & Bots (planned)"))
        st.markdown(L("- One place for every alert rule: scanner, order-flow sync, Gann zones, liquidations - with on/off and minimum quality.\n"
                      "- Delivery: Telegram (already working from the sidebar), browser push, e-mail.\n"
                      "- Paper-trading bot that follows only the rules that passed the lab, with its own honest track record."))
    st.caption(L("Not built yet - this page shows the plan. Tell me which part to build first."))


TV_INTERVALS = {"1": "1 min", "5": "5 min", "15": "15 min", "60": "1 hour", "240": "4 hour", "D": "1 day", "W": "1 week"}
CHART_H = 225  # two stacked charts ~ the height of the DOM ladder

# Radar setups (team task 17): a suggestion only; nothing here places an order
RADAR_TAG = "<span title='Radar setup: suggestion only, no automatic orders' style='color:#f0b90b;font-weight:700;font-size:10px;margin-right:4px;cursor:help'>◆ RADAR</span>"

_CS_TFS = ["1m", "5m", "13m", "15m", "30m", "1h", "2h", "3h", "4h", "6h", "7h", "8h", "12h", "1d", "3d", "1w", "1mo"]

def _screen_cols(df):
    """Finviz-style screener numbers for one candle frame (Radar > Screener): last-candle and 20-bar change, volume vs its
    20-bar average, ATR as % of price, trend vs EMA 20/50. Plain arithmetic on the candles already downloaded."""
    import numpy as np
    c, h, l, v = (df[k].astype(float) for k in ("close", "high", "low", "volume"))
    last, prev = float(c.iloc[-1]), float(c.iloc[-2])
    tr = np.maximum(h - l, np.maximum((h - c.shift()).abs(), (l - c.shift()).abs()))
    e20, e50 = float(c.ewm(span=20, adjust=False).mean().iloc[-1]), float(c.ewm(span=50, adjust=False).mean().iloc[-1])
    va = float(v.iloc[-21:-1].mean() or 0)
    return {"chg": round((last / prev - 1) * 100, 2) if prev else None,
            "chg20": round((last / float(c.iloc[-21]) - 1) * 100, 2) if len(c) > 21 and float(c.iloc[-21]) else None,
            "volx": round(float(v.iloc[-1]) / va, 2) if va > 0 else None,
            "atrp": round(float(tr.iloc[-14:].mean()) / last * 100, 2) if last else None,
            "trend": "up" if last > e20 > e50 else "down" if last < e20 < e50 else "mixed"}


from modules import chart_explain as _CX


@st.cache_data(ttl=300, show_spinner=False)
def _last_ts(df):
    """Open time of the last candle as 'MM-DD HH:MM' (UTC), or ''."""
    try:
        import pandas as _p
        v = df["time"].iloc[-1]
        t = _p.to_datetime(v, unit="ms", utc=True) if isinstance(v, (int, float)) or str(getattr(v, "dtype", "")).startswith("int") else _p.to_datetime(v, utc=True)
        return t.strftime("%m-%d %H:%M")
    except Exception:
        return ""


def _fv_with_ref(df, sym, ref_sym, ref_df):
    """Finviz-style metrics + beta / correlation against the reference symbol (none for the reference itself or when no reference is in the universe)."""
    from modules import fv_screen as _FV
    m = _FV.metrics(df)
    if m is not None and ref_df is not None and sym != ref_sym:
        m.update(_FV.relation(df, ref_df))
    return m


@st.cache_data(ttl=120, show_spinner=False)   # speed: every Radar rerun / page switch used to refetch all candles
def _plines_ms(df, pl):
    """Pattern lines in bar indices -> {pattern id: [[t0 ms, p0, t1 ms, p1], ...]} so the Radar's Workspace chart can draw them."""
    try:
        ts = pd.to_datetime(df.reset_index(drop=True)["time"])
        ms = lambda i: int(ts.iloc[int(i)].timestamp() * 1000)   # noqa: E731
        return {k: [[ms(a), float(p), ms(b), float(q)] for a, p, b, q in v] for k, v in (pl or {}).items()}
    except Exception:   # extra drawing data: never break the scan
        return {}


def _chart_scan_data(symbols: tuple, tf: str, look: int = 3):
    """-> {symbol: {'rsi', 'flags', 'svg', 'price'}} for one timeframe (cached 60 s)."""
    from modules import fv_screen as _FV
    from modules import radar_context as _RC
    frames, _errs = fetch_frames(list(symbols), [tf], limit=260, workers=8)
    pfr = _peer_frames(symbols, tf)
    out = {}
    _ref_sym = next((x for x in ("BTC-USDT", "BTC-USDT-SWAP", "HL:xyz:SP500", "Y:^GSPC", "HL:BTC") if (frames.get(x) or {}).get(tf) is not None), None)   # beta / correlation reference: BTC for crypto, the S&P 500 for TradFi
    _ref_df = (frames.get(_ref_sym) or {}).get(tf) if _ref_sym else None
    for sym in symbols:
        df = (frames.get(sym) or {}).get(tf)
        if df is None or len(df) < 60:
            continue
        f = cs_features(df, look)
        sflags, ssides = strategy_flags(df, _peers_for(sym, tf, pfr))
        flags = sorted(f["flags"] | sflags | move_flags(df))
        try:
            expl = _CX.explain_both(df, flags)   # hover text (both languages, this result is cached): chart pattern, candle psychology, EMAs
        except Exception:
            expl = {}
        out[sym] = {"plines": _plines_ms(df, f.get("plines")), "rsi": f["rsi"], "regime": f.get("regime"), "flags": flags, "explain": expl, "sides": {k: sorted(v) for k, v in ssides.items()}, "svg": mini_chart_svg(df, lines=f.get("lines")), "ctx": _RC.context(df), "price": float(df["close"].iloc[-1]),
                    "t": time.time(), "ts": _last_ts(df), "fv": _fv_with_ref(df, sym, _ref_sym, _ref_df), "cn": sorted(_FV.candle_set(df)), **_screen_cols(df)}
    return out


_CS_KEY = {"1m": "1m", "5m": "1m", "15m": "1m", "30m": "1h", "1h": "1h", "1d": "1d", "1w": "1w", "4h": "1h",
           "13m": "13m", "2h": "2h", "3h": "3h", "6h": "6h", "7h": "7h", "8h": "8h", "12h": "12h", "3d": "3d", "1mo": "1mo"}   # scorer knows 1m/1h/1d/1w; the rest borrow the nearest


@st.cache_data(ttl=120, show_spinner=False)
def _cs_result(sym: str, tf: str):
    """Full scanner result for one chart (signals, higher-timeframe view, scenarios) so it can be explained in Arabic."""
    key = _CS_KEY.get(tf, "1h")
    frames, _e = fetch_frames([sym], sorted({tf, key} | set(fetch_tfs(key))))
    fr = dict(frames.get(sym) or {})
    if tf not in fr:
        return None
    fr[key] = fr[tf]
    r = scan_symbol(sym, fr, key, peers=_peers_for(sym, tf, _peer_frames([sym], tf)))
    r["timeframe"] = tf
    return r


from modules.market_map_view import render_market_map  # noqa: E402  (moved 2026-11-17; same view for the desk and TIA)


def _clear_cs_filters():
    """Callback of 'Clear all filters': reset the Radar filter widgets, the Scanner-control preset and the saved URL filter (runs before the rerun)."""
    ss = st.session_state
    for k in ("cs_strat", "cs_rsi", "cs_pat", "cs_mom", "cs_mom_a", "cs_mom_v", "cs_quick"):
        ss[k] = []
    ss["cs_preset"] = "— none —"
    for k in ("cs_px_rel", "cs_ma_rel", "cs_stack"):
        ss[k] = "—"
    for k in list(ss.keys()):
        if isinstance(k, str) and k.startswith("fv_f_"):
            ss[k] = "Any"
    ss.pop("radar_def", None)
    try:
        if "strat" in st.query_params:
            del st.query_params["strat"]
    except Exception:
        pass


def _radar_state(tf, data):
    """Radar strip (design board 'Radar'): daily market state, strong news in the next hour, data age. Never blocks the page."""
    out = {"regime": "-", "regime_sub": "", "news": "", "age": "-"}
    try:
        tr = list(_htf_trend(tuple(SCAN_SYMBOLS), "1d").values())   # candles + EMA 20/50 only (the old full daily scan doubled the first load)
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


_LADDER = {"1m": ("1h", "15m"), "3m": ("1h", "15m"), "5m": ("4h", "1h"), "13m": ("4h", "1h"), "15m": ("4h", "1h"), "30m": ("1d", "4h"),
           "1h": ("1d", "4h"), "2h": ("1w", "1d"), "3h": ("1w", "1d"), "4h": ("1w", "1d"), "6h": ("1w", "1d"), "8h": ("1w", "1d"),
           "12h": ("1w", "1d"), "1d": ("1w",), "3d": ("1w",)}   # Elder's triple screen: each step ~4-6x the one below


@st.cache_data(ttl=600, show_spinner=False)
def _htf_trend(symbols: tuple, tf: str):
    """Trend per symbol on a higher timeframe for the hover ladder: up (close > EMA 20 > EMA 50), down, or mixed."""
    frames, _e = fetch_frames(list(symbols), [tf], limit=120, workers=8)
    out = {}
    for s in symbols:
        df = (frames.get(s) or {}).get(tf)
        if df is not None and len(df) >= 50:
            c = df["close"].astype(float)
            last, e20, e50 = float(c.iloc[-1]), float(c.ewm(span=20, adjust=False).mean().iloc[-1]), float(c.ewm(span=50, adjust=False).mean().iloc[-1])
            out[s] = "up" if last > e20 > e50 else "down" if last < e20 < e50 else "mixed"
    return out


_TREND_AR = {"up": "صاعد ↑", "down": "هابط ↓", "mixed": "مختلط ↔"}
_TREND_EN = {"up": "Up ↑", "down": "Down ↓", "mixed": "Mixed ↔"}


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


_QUICK_CHIPS = [   # (filter key, icon, short name): the same keys as the dropdown filters, one click each (owner 2026-10-23: shapes and colours, not only buttons)
    ("rsi_lt30", "🟢", "RSI<30"), ("rsi_gt70", "🔴", "RSI>70"), ("chan_up", "📈", "Channel ↑"), ("chan_dn", "📉", "Channel ↓"),
    ("tl_up", "🔺", "Trendline ↑"), ("tl_dn", "🔻", "Trendline ↓"), ("dbl_bottom", "🟦", "Double bottom"), ("dbl_top", "🟧", "Double top"),
    ("chg_up2", "🚀", "+2%"), ("chg_dn2", "💥", "−2%"), ("vol_2x", "🔊", "Vol 2×"), ("vol_3x", "⚡", "Vol 3×"),
    ("stack_bull", "🐂", "Bull stack"), ("stack_bear", "🐻", "Bear stack"), ("above_all", "☁️", "Above EMAs"), ("below_all", "🌧️", "Below EMAs"),
    ("st_elliott", "🌊", "Elliott"), ("st_msb", "🧱", "SMC MSB+OB"), ("st_unicorn", "🦄", "Unicorn"), ("st_ob", "📦", "Order block"),
]
_QUICK_NAME = {k: (i, n) for k, i, n in _QUICK_CHIPS}


def _quick_lbl(k):
    i, n = _QUICK_NAME[k]
    return f"{i} {L(n)}"

_RADAR_CSS = """<style>
.xr-tile{position:relative}
.xr-tile img{display:block}
.xr-tip{display:none;position:absolute;left:0;right:0;top:0;z-index:30;max-height:340px;overflow-y:auto;background:rgba(18,22,27,.97);
 border:1px solid #2dd4bf66;border-radius:6px;padding:8px 10px;font-size:11.5px;line-height:18px;color:#e6e9ee;text-align:right;
 box-shadow:0 6px 24px rgba(0,0,0,.5)}
.xr-tip hr{border:0;border-top:1px solid #2b3139;margin:6px 0}
.xr-tile:hover .xr-tip,.xr-tile:focus-within .xr-tip{display:block}
.xr-hint{font-size:10px;color:#848e9c}
</style>"""


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


@st.cache_data(ttl=300, show_spinner=False)
def _radar_closes(symbols: tuple, tf: str = "1h"):
    """Close prices of the Radar universe on one timeframe (one download, cached 5 min) for Performance / Correlation."""
    import pandas as _pd
    frames, _e = fetch_frames(list(symbols), [tf], limit=260)
    cols = {}
    for s in symbols:
        df = (frames.get(s) or {}).get(tf)
        if df is not None and len(df) > 30:
            t = df["time"]
            t = _pd.to_datetime(t, unit="ms") if _pd.api.types.is_numeric_dtype(t) else _pd.to_datetime(t)
            cols[s] = _pd.Series(df["close"].astype(float).values, index=t.values)
    return _pd.DataFrame(cols).sort_index()   # aligned on candle time, so returns compare the same hours


@st.cache_data(ttl=300, show_spinner=False)
def _fv_frames(symbols: tuple, tf: str):
    """Candle frames of the Radar universe on one timeframe (up to 300 bars, cached 5 min) for the Finviz-style screener and Similar charts."""
    frames, _e = fetch_frames(list(symbols), [tf], limit=300)
    return {s: f[tf] for s, f in frames.items() if f.get(tf) is not None and len(f[tf]) >= 30}


def render_radar_similar(f):
    """Find similar charts (Finviz, Sep 2026): rank the symbols and past stretches whose recent price path looks like the chosen one."""
    import altair as alt
    import pandas as _pd
    from modules import fv_screen as FV
    ar = _ui_lang() == "ar"
    A = lambda e, a: a if ar else e
    c = st.columns([0.2, 1.2, 1.3, 1.3])
    tf = f["tf"]
    c[0].markdown(f"<div class='uk-chip' style='margin-top:26px'>{html.escape(tf)}</div>", unsafe_allow_html=True)
    with st.spinner(L("Loading the candles of every Radar symbol (the first load can take up to a minute; later loads are cached)")):
        frames = _fv_frames(tuple(_radar_symbols(f)), tf)
    if not frames:
        st.info(L("No candles yet."))
        return
    if st.session_state.get("sm_sym") not in frames:   # the filters changed the list: forget a target that is no longer in it
        st.session_state.pop("sm_sym", None)
    target = c[1].selectbox(A("Chart to match", "الشارت المطلوب مشابهته"), sorted(frames), key="sm_sym")
    win = int(c[2].slider(A("Window (bars)", "النافذة (شموع)"), 10, 120, 40, 5, key="sm_win"))
    ahead = int(c[3].slider(A("Bars to look ahead", "شموع للمتابعة بعدها"), 5, 40, 10, 5, key="sm_ahead"))
    res = FV.similar(frames, target, win, ahead, top=12)
    if not res:
        st.info(A("Not enough candles for this window.", "الشموع مش كفاية للنافذة دي."))
        return
    df = _pd.DataFrame([{A("Symbol", "الرمز"): r["symbol"], A("Match (best stretch)", "التطابق (أحسن فترة)"): r["corr"], A("Match now", "التطابق دلوقتي"): r["corr_now"],
                         A("Ended bars ago", "انتهت من كام شمعة"): r["offset"], A("Window move %", "حركة النافذة %"): r["ret"],
                         A("What followed %", "اللي حصل بعدها %"): r["after"]} for r in res])
    st.dataframe(df, hide_index=True, width="stretch")
    lines = []
    tz = frames[target]["close"].astype(float).tail(win).values
    z = lambda x: (x - x.mean()) / (x.std() or 1)
    for i, v in enumerate(z(tz)):
        lines.append({"x": i, "z": v, "series": A("Chosen: ", "المختار: ") + target})
    for r in res[:3]:
        if r["symbol"] == target and r["offset"] == 0:
            continue
        cl = frames[r["symbol"]]["close"].astype(float).values; n = len(cl); seg = cl[n - r["offset"] - win:n - r["offset"]]
        for i, v in enumerate(z(seg)):
            lines.append({"x": i, "z": v, "series": f"{r['symbol']} ({r['corr']:.2f}, {r['offset']} " + A("bars ago", "شمعة فاتت") + ")"})
    st.altair_chart(alt.Chart(_pd.DataFrame(lines)).mark_line().encode(x=alt.X("x:Q", title=A("bars", "شموع")), y=alt.Y("z:Q", title=A("shape (z-score)", "الشكل (z-score)")), color=alt.Color("series:N", legend=alt.Legend(orient="bottom", title=None))).properties(height=260), width="stretch")
    st.caption(A("Match = Pearson correlation of the two price paths (1 = same shape, -1 = mirror). 'Best stretch' picks the best of every window in the history, so it is always high on noisy prices: compare it with 'Match now'. 'What followed' is history of that look-alike, a description, not a forecast. Educational, not investment advice.",
                 "التطابق = معامل ارتباط بيرسون بين مسارين للسعر (1 = نفس الشكل، -1 = مقلوب). «أحسن فترة» بتختار أحسن نافذة في التاريخ كله فبتطلع عالية دايماً على الأسعار المتذبذبة: قارنها بـ«التطابق دلوقتي». «اللي حصل بعدها» تاريخ الشبيه ده، وصف مش توقع. تعليمي، مش توصية استثمارية."))


def render_radar_perf(f):
    """Finviz 'Performance' view: % change over fixed spans per symbol on the panel's timeframe, for the symbols that pass the panel's filters."""
    import pandas as _pd
    import altair as alt
    tf = f["tf"]
    syms = _radar_symbols(f)
    if not syms:
        st.info(L("No symbol meets ALL the chosen filters right now."))
        return
    px = _radar_closes(tuple(syms), tf)
    if px.empty:
        st.info(L("No candles yet."))
        return
    mins = _tf_bars(tf)
    if mins <= 1440:   # time spans: 1 h, 4 h, 24 h, 3 d, 1 w, 10 d, counted in candles of this timeframe
        spans = {k_: max(1, round(h_ * 60 / mins)) for k_, h_ in (("1 h", 1), ("4 h", 4), ("24 h", 24), ("3 d", 72), ("1 w", 168), ("10 d", 240))}
    else:              # daily and longer: candle counts
        spans = {"1 bar": 1, "5 bars": 5, "20 bars": 20, "60 bars": 60, "120 bars": 120, "250 bars": 250}
    sort_default = "24 h" if "24 h" in spans else "20 bars"
    rows = []
    for s in px.columns:
        c = px[s].dropna()
        r = {"Symbol": s, "Price": float(c.iloc[-1])}
        for k, n in spans.items():
            r[k] = round((c.iloc[-1] / c.iloc[-1 - n] - 1) * 100, 2) if len(c) > n else None
        r["Volatility 24 h %"] = round(float(c.pct_change().tail(24).std() * 100), 2) if len(c) > 25 else None   # last 24 candles of the chosen timeframe
        rows.append(r)
    df = _pd.DataFrame(rows)
    sort_by = st.segmented_control(L("Sort by"), list(spans), default=sort_default, key="perf_sort") or sort_default
    if sort_by not in spans:
        sort_by = sort_default
    df = df.sort_values(sort_by, ascending=False, na_position="last")
    k = st.columns(4)
    v = df[sort_by].dropna()
    k[0].metric(L("Symbols"), len(df)); k[1].metric(L("Up") + f" ({sort_by})", int((v > 0).sum())); k[2].metric(L("Down") + f" ({sort_by})", int((v < 0).sum()))
    k[3].metric(L("Median") + f" ({sort_by})", f"{v.median():+.2f}%" if len(v) else "-")
    pc = {c: st.column_config.NumberColumn(format="%+.2f%%") for c in spans}
    st.dataframe(df.rename(columns={"Symbol": L("Symbol"), "Price": L("Price"), "Volatility 24 h %": L("Volatility 24 h %")}), hide_index=True,
                 width="stretch", column_config={**pc, L("Price"): st.column_config.NumberColumn(format="%.4g")})
    long = df.melt(id_vars="Symbol", value_vars=list(spans), var_name="span", value_name="pct").dropna()
    st.markdown(f"**{L('Change % by period (heat map)')}**")
    st.altair_chart(alt.Chart(long).mark_rect().encode(
        x=alt.X("span:N", sort=list(spans), title=None), y=alt.Y("Symbol:N", sort=list(df["Symbol"]), title=None),
        color=alt.Color("pct:Q", scale=alt.Scale(scheme="redyellowgreen", domainMid=0), title="%"), tooltip=["Symbol", "span", "pct"]
    ).properties(height=max(200, 20 * len(df))), width="stretch")
    st.caption(f"{tf} · {len(df)} / {len(SCAN_SYMBOLS)} " + L("symbols") + " · " + L("Candles from the same source as the charts. Educational, not investment advice."))


def render_radar_corr(f):
    """Correlation of returns on the panel's timeframe, for the symbols that pass the panel's filters: which move together (one trade, not two) and which hedge."""
    import altair as alt
    syms = _radar_symbols(f)
    px = _radar_closes(tuple(syms), f["tf"]) if syms else None
    if px is None:
        st.info(L("No symbol meets ALL the chosen filters right now."))
        return
    if px.shape[1] < 2:
        st.info(L("Need at least two symbols with candles."))
        return
    rets = px.pct_change(fill_method=None).dropna(how="all")
    cm = rets.corr().round(2)
    long = cm.reset_index(names="a").melt(id_vars="a", var_name="b", value_name="corr")
    order = list(cm.columns)
    st.altair_chart(alt.Chart(long).mark_rect().encode(
        x=alt.X("b:N", sort=order, title=None), y=alt.Y("a:N", sort=order, title=None),
        color=alt.Color("corr:Q", scale=alt.Scale(scheme="blueorange", domain=[-1, 1]), title="corr"), tooltip=["a", "b", "corr"]
    ).properties(height=max(260, 22 * len(order))), width="stretch")
    pairs = long[long["a"] < long["b"]].sort_values("corr")
    a, b = st.columns(2)
    a.markdown(f"**{L('Move together (corr >= 0.8): treat as one position')}**")
    a.dataframe(pairs[pairs["corr"] >= 0.8].sort_values("corr", ascending=False).head(12), hide_index=True, width="stretch")
    b.markdown(f"**{L('Lowest correlation (diversify / hedge)')}**")
    b.dataframe(pairs.head(12), hide_index=True, width="stretch")
    st.caption(f"{f['tf']} · " + L("Pearson correlation of returns, last 260 candles. Correlation changes over time; it is not a forecast."))


def render_radar_signals(f):
    """Finviz 'Signal' list: every pattern / strategy signal live now, the symbols it fired on, its side, and the lab's number."""
    import pandas as _pd
    from modules import office_kpi as _OK
    from modules.chart_scan import STRATEGY_FILTERS as _SF, PATTERN_FILTERS as _PF, flag_side
    tf = f["tf"]
    data = _radar_data(f)
    if data is None:
        return
    data = {s_: d_ for s_, d_ in data.items() if _radar_pass(d_, f)}   # only the symbols that pass the shared filters
    lab = _OK.load()
    by = {}
    for sym, d in data.items():
        for k in d["flags"]:
            if k in _SF or k in _PF:
                side = flag_side(k) or "/".join(d.get("sides", {}).get(k, [])) or "-"
                by.setdefault(k, []).append(f"{sym} ({side})" if side != "-" else sym)
    rows = []
    for k, syms in by.items():
        ev = _OK.evidence(lab, _SF[k][1][1], tf) if k in _SF and _SF[k][1][0] == "key" else None
        rows.append({"Signal": _SF[k][0] if k in _SF else _PF[k], "Kind": "Strategy" if k in _SF else "Pattern", "Count": len(syms),
                     "Symbols": ", ".join(sorted(syms)[:12]), "Lab net R": ev["net"] if ev else None, "Lab n": ev["n"] if ev else None,
                     "Lab": ("OFF" if ev["off"] else "passed" if ev["gate"] else "not evidence") if ev else "-"})
    if not rows:
        st.info(L("No signals on this timeframe right now."))
        return
    df = _pd.DataFrame(rows).sort_values(["Count", "Lab net R"], ascending=[False, False], na_position="last")
    k = st.columns(3)
    k[0].metric(L("Signals live"), len(df)); k[1].metric(L("Symbols scanned"), len(data))
    k[2].metric(L("With positive lab net R"), int((df["Lab net R"].fillna(-1) > 0).sum()))
    from collections import Counter as _Cnt
    _rc = _Cnt(d_.get("regime") for d_ in data.values() if d_.get("regime"))
    if _rc:
        st.caption(L("Market regime of the scanned symbols now") + ": " + " · ".join(f"{r_} {n_}" for r_, n_ in _rc.most_common()))
    df["Kind"] = df["Kind"].map(L); df["Lab"] = df["Lab"].map(L)
    st.dataframe(df.rename(columns={c: L(c) for c in df.columns}), hide_index=True, width="stretch",
                 column_config={L("Lab net R"): st.column_config.NumberColumn(format="%+.3f")})
    st.caption(L("Lab net R = the weekly lab's average R after 0.1R costs for that detector on the nearest lab timeframe. A signal is a suggestion, not evidence, until it passes the gate."))


def render_radar_screener(f):
    """Finviz-style table (owner 2026-10-22): one sortable table for the Radar universe, filtered by the SAME panel as the chart grid (no second set of
    options), and a top-movers bar chart. Same candles as the chart grid (cached)."""
    import pandas as _pd
    data = _radar_data(f)
    if data is None:
        return
    rows = []
    for sym, d in data.items():
        sig = [(_CX.FLAG_AR[k] if _ui_lang() == "ar" and k in _CX.FLAG_AR else L(CS_SHORT.get(k, k))) for k in d["flags"] if k in ALL_FILTERS]
        rows.append({"Symbol": sym, "Price": d["price"], "Change %": d.get("chg"), "20-bar %": d.get("chg20"), "RSI": d["rsi"],
                     "Volume ×avg": d.get("volx"), "ATR %": d.get("atrp"), "Trend": d.get("trend"), "Signals": len(sig), "Which": " · ".join(sig[:8])})
    df = _pd.DataFrame(rows)
    if df.empty:
        st.info(L("No symbols match the selected conditions right now."))
        return
    df = df[df["Symbol"].isin([s_ for s_, d_ in data.items() if _radar_pass(d_, f)])]
    k = st.columns(5)
    k[0].metric(L("Matched"), f"{len(df)} / {len(rows)}")
    k[1].metric(L("Trend up"), int((df["Trend"] == "up").sum()))
    k[2].metric(L("Trend down"), int((df["Trend"] == "down").sum()))
    k[3].metric(L("Oversold (RSI ≤ 30)"), int((df["RSI"] <= 30).sum()))
    k[4].metric(L("Overbought (RSI ≥ 70)"), int((df["RSI"] >= 70).sum()))
    shown_df = df.sort_values("20-bar %", ascending=False, na_position="last").assign(Trend=lambda x: x["Trend"].map(L))
    st.dataframe(shown_df.rename(columns={c: L(c) for c in shown_df.columns}), hide_index=True, width="stretch",
                 column_config={L("Price"): st.column_config.NumberColumn(format="%.4g"),
                                L("Change %"): st.column_config.NumberColumn(format="%+.2f%%"), L("20-bar %"): st.column_config.NumberColumn(format="%+.2f%%"),
                                "RSI": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f"),
                                L("Volume ×avg"): st.column_config.NumberColumn(format="%.2f×"), "ATR %": st.column_config.NumberColumn(format="%.2f%%")})
    top = df.dropna(subset=["20-bar %"]).sort_values("20-bar %")
    if len(top):
        import altair as alt
        top = _pd.concat([top.head(8), top.tail(8)]).drop_duplicates("Symbol")
        st.markdown(f"**{L('Top movers over 20 bars')}**")
        st.altair_chart(alt.Chart(top).mark_bar().encode(
            x=alt.X("20-bar %:Q", title="%"), y=alt.Y("Symbol:N", sort="-x", title=None),
            color=alt.condition("datum['20-bar %'] > 0", alt.value("#2dd4bf"), alt.value("#f87171")), tooltip=["Symbol", "20-bar %", "RSI", "Trend"]
        ).properties(height=max(160, 18 * len(top))), width="stretch")
    st.caption(L("Educational, not investment advice. Same candles as the Charts tab; no automatic orders."))


def _radar_filters(view):
    """ONE filter panel for every Radar view (owner 2026-10-23): universe, timeframe, side, indicators, strategies, patterns and the Finviz-style technical lists.
    Rendered on every run so its choices survive switching tabs; returns the settings dict."""
    st.markdown("""<style>
.st-key-csf{background:#12161b;border:1px solid #2b3139;border-radius:5px;padding:3px 6px 1px}
.st-key-csf label p,.st-key-csf [data-testid="stWidgetLabel"] p{font-size:10px!important;color:#848e9c!important;margin:0 0 1px 0!important;text-transform:uppercase;letter-spacing:.03em}
.st-key-csf [data-baseweb="select"]>div,.st-key-csf input{min-height:22px!important;font-size:10px!important;padding-top:0!important;padding-bottom:0!important}
.st-key-csf [data-baseweb="select"] span,.st-key-csf [data-baseweb="tag"]{font-size:11px!important}
.st-key-csf [data-testid="stHorizontalBlock"]{gap:.4rem!important}
.st-key-csf [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;overflow-x:auto;align-items:center!important}.st-key-csf{font-size:10px}
.st-key-csf [data-testid="stPopover"] button{min-height:22px!important;height:22px!important;padding:0 6px!important;font-size:10px!important}
.st-key-csf [data-testid="stElementContainer"]{margin-bottom:0!important}
.st-key-csf [data-testid="stVerticalBlock"]{gap:.25rem!important}
.st-key-csf [data-testid="stNumberInputContainer"]{min-height:26px!important}
.st-key-csf [data-baseweb="select"] [data-baseweb="tag"]{height:18px!important;margin:1px!important}
.st-key-csf [data-baseweb="select"]>div{max-height:56px;overflow-y:auto}
.st-key-csf [data-testid="stPopover"]{width:100%}.st-key-csf [data-testid="stPopover"] button{width:100%;min-height:30px;background:#161a1e!important;border:1px solid #2b3139!important;border-radius:4px!important;color:#eaecef!important;font-size:11px!important;padding:0 6px!important}.st-key-csf [data-testid="stPopover"] button:hover{border-color:#4a5568!important}
.st-key-cs_clear_top button{background:#161a1e!important;color:#eaecef!important;border:1px solid #2b3139!important;min-height:30px!important;font-size:11px!important}
.st-key-csf [data-testid="stWidgetLabel"]:not([data-testid="stPopoverBody"] *){display:none!important}
.st-key-csf{padding:2px 6px!important}
</style>""", unsafe_allow_html=True)   # owner 2026-11-21: the filters are ONE thin line (no labels over the boxes; each box shows its value, the ? help stays in the menus)
    qp = st.query_params
    if "cs_strat" not in st.session_state and qp.get("strat"):   # remembered selection (URL param survives reloads / bookmarks)
        st.session_state["cs_strat"] = [k for k in qp["strat"].split(",") if k in STRATEGY_FILTERS]
    rmap = {"above": "above", "below": "below", "crossed above": "xup", "crossed below": "xdn"}
    rels = ["—", "above", "below", "crossed above", "crossed below"]
    fold = view in ("Heat map",)   # owner 2026-11-21: no separate "Hide filters" line; the heat map hides the filter block (widgets stay rendered so selections are kept)
    if fold:
        st.markdown("<style>.st-key-csfw{display:none!important}</style>", unsafe_allow_html=True)
    from modules import fv_screen as _FV
    from modules import radar_presets as _RP
    _ar = _ui_lang() == "ar"
    _mom_k, _vol_k = _RP.split_moves(MOVE_FILTERS)
    _FVL = {f_[0]: f_ for f_ in _FV.FILTERS}
    ss = st.session_state

    def _n(*keys):   # active choices of a group, shown in its button: "Trend (2)"
        c = 0
        for k_ in keys:
            v_ = ss.get(k_)
            c += len(v_) if isinstance(v_, list) else (1 if v_ not in (None, "—", "Any", "Both", "All selected") else 0)
        return f" ({c})" if c else ""

    import uuid as _uuid
    from streamlit.components.v1 import declare_component as _decl
    _store = _decl("xpix_preset_store", path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules", "preset_store"))
    _bv = _store(cmd=ss.get("rp_last_cmd"), key="rp_store", default=None)   # the user's own presets live in THIS browser (localStorage); {presets, ok} comes back
    _browser = (_bv or {}).get("presets") if isinstance(_bv, dict) else None

    def _on_preset():
        nm = ss.get("cs_preset")
        if nm and nm != _RP.NONE:
            _RP.apply(ss, nm, _RP.all_presets(extra=ss.get("rp_browser")))

    def _cmd(action, name, data=None):   # one command per click (new id), picked up by the store component on the next render
        ss["rp_last_cmd"] = {"id": _uuid.uuid4().hex, "action": action, "name": name, "data": data}

    def _on_save():
        nm = (ss.get("cs_preset_name") or "").strip()[:40]
        snap = _RP.snapshot(ss)
        ss["rp_msg"] = ("warn", "Give the preset a name") if not nm else ("warn", "Nothing selected to save") if not snap else ("ok", "Saved in this browser")
        if nm and snap:
            _cmd("save", nm, snap)

    def _on_del():
        cur = ss.get("cs_preset", "")
        if isinstance(cur, str) and cur.startswith("★"):
            _cmd("delete", cur[1:].strip())
            _RP.delete_user(cur)

    def _fvbox(container, key):
        f_ = _FVL.get(key)
        if not f_:
            return None
        _key, _g, _en, _arn, _opts = f_
        _lab = {c_: (a_ if _ar else e_) for c_, e_, a_ in _opts}
        pk = container.selectbox(_arn if _ar else _en, ["Any"] + [o[0] for o in _opts], format_func=lambda x, _lab=_lab: L("Any") if x == "Any" else _lab.get(x, x), key="fv_f_" + _key)
        return (_key, pk) if pk != "Any" else None

    fv = {}
    with st.container(key="csfw"), st.container(key="csf"):
        rd = ss.get("radar_def", {})   # set from Technical Office > Scanner control
        _def_tf = rd["tf"] if rd.get("tf") in _CS_TFS else "1h"
        _sides, _modes = ["Both", "Buy only", "Sell only"], ["All selected", "Any selected"]
        # ONE compact row (owner 2026-10-24): preset by strategy name, then plain grouped dropdowns, no icons
        if _browser is not None:
            ss["rp_browser"] = _browser
        _pres = _RP.all_presets(extra=ss.get("rp_browser"))
        _grid = view == "Chart grid"   # owner 2026-11-21: the grid's Summary / Open setups / grid size sit on THIS line too (render_chart_scanner fills them)
        top = st.columns([0.6, 0.9, 0.8, 0.6, 1.1, 0.5, 0.8, 0.9, 0.8, 0.8, 0.8, 0.8, 0.8] + ([0.9, 1.0, 0.8] if _grid else []), vertical_alignment="center")
        st.markdown(kit_css(), unsafe_allow_html=True)
        render_universe_controls(top[1], top[2], top[3])   # Asset class / Market / Universe size, same line
        tf = top[0].selectbox(L("Timeframe"), _CS_TFS, index=_CS_TFS.index(_def_tf), key="cs_tf", label_visibility="collapsed") or _def_tf   # one timeframe for EVERY Radar view, first item of the single filter line
        top[4].selectbox(L("Preset (strategy)"), [_RP.NONE] + list(_pres), key="cs_preset", on_change=_on_preset, format_func=lambda x: L("— choose a strategy —") if x == _RP.NONE else x)
        with top[5].popover(L("Save")):
            _nm = st.text_input(L("Name of my preset"), key="cs_preset_name", max_chars=40)
            st.button(L("Save current filters"), key="cs_preset_save", on_click=_on_save)
            _m = ss.pop("rp_msg", None)
            if _m:
                (st.success if _m[0] == "ok" else st.warning)(L(_m[1]))
            _cur = ss.get("cs_preset", "")
            if isinstance(_cur, str) and _cur.startswith("★"):
                st.button(L("Delete") + f" {_cur}", key="cs_preset_del", on_click=_on_del)
            st.caption(L("Saved in this browser only (not shared with other browsers or people)."))
        with top[6].popover(L("Trend") + _n("cs_stack", "cs_px_rel", "cs_ma_rel", "fv_f_sma20", "fv_f_sma50", "fv_f_sma200", "fv_f_adx", "fv_f_sar", "fv_f_dist20", "fv_f_ichi")):
            look = st.selectbox(L("Cross window"), [1, 3, 5, 10], index=1, key="cs_look", format_func=lambda n: f"last {n} candle" + ("s" if n > 1 else ""))
            stack = st.selectbox(L("Trend stack"), ["—", "Bullish (px>9>20>50)", "Bearish (px<9<20<50)", "Above all EMAs", "Below all EMAs"], key="cs_stack", format_func=L)
            c_ = st.columns([1.3, 0.7])
            rel_px = c_[0].selectbox(L("Price vs EMA"), rels, key="cs_px_rel", format_func=L)
            len_px = c_[1].selectbox("EMA", [9, 20, 50, 200], index=1, key="cs_px_len")
            c_ = st.columns([1.3, 0.7])
            rel_ma = c_[0].selectbox(L("EMA vs EMA"), rels, key="cs_ma_rel", format_func=L)
            pair = c_[1].selectbox(L("Pair"), ["9/20", "20/50", "50/200"], index=1, key="cs_ma_pair")
            for k_ in ("sma20", "sma50", "sma200", "adx", "sar", "dist20", "ichi"):
                r_ = _fvbox(st, k_)
                if r_:
                    fv[r_[0]] = r_[1]
        with top[7].popover(L("Momentum") + _n("cs_rsi", "cs_mom_a", "fv_f_perf", "fv_f_perf2", "fv_f_chg", "fv_f_chgopen", "fv_f_macd", "fv_f_stoch", "fv_f_cci", "fv_f_willr")):
            sel_rsi = st.multiselect("RSI", list(RSI_FILTERS), format_func=RSI_FILTERS.get, key="cs_rsi")
            sel_mom_a = st.multiselect(L("Price move (last candle)"), _mom_k, format_func=MOVE_FILTERS.get, key="cs_mom_a")
            for k_ in ("perf", "perf2", "chg", "chgopen", "macd", "stoch", "cci", "willr"):
                r_ = _fvbox(st, k_)
                if r_:
                    fv[r_[0]] = r_[1]
        with top[8].popover(L("Volume") + _n("cs_mom_v", "fv_f_vol", "fv_f_relvol", "fv_f_turnover", "fv_f_obv")):
            sel_mom_v = st.multiselect(L("Volume (last candle)"), _vol_k, format_func=MOVE_FILTERS.get, key="cs_mom_v")
            for k_ in ("vol", "relvol", "turnover", "obv"):
                r_ = _fvbox(st, k_)
                if r_:
                    fv[r_[0]] = r_[1]
        with top[9].popover(L("Pattern") + _n("cs_pat", "cs_strat", "fv_f_candle", "fv_f_range")):
            sel_pat = st.multiselect(L("Chart patterns"), list(PATTERN_FILTERS), format_func=PATTERN_FILTERS.get, key="cs_pat")
            sel_strat = st.multiselect(L("Strategies / signals (Elliott, SMC, ICT, Harmonic, VWAP ...)"), list(STRATEGY_FILTERS), format_func=_strat_name, key="cs_strat")
            for k_ in ("candle", "range"):
                r_ = _fvbox(st, k_)
                if r_:
                    fv[r_[0]] = r_[1]
        with top[10].popover(L("Market") + _n("fv_f_hl20", "fv_f_hl50", "fv_f_hl52", "fv_f_hlall", "fv_f_gap", "fv_f_atr", "fv_f_bb", "fv_f_price", "fv_f_beta", "fv_f_corr")):
            for k_ in ("hl20", "hl50", "hl52", "hlall", "gap", "atr", "bb", "price", "beta", "corr"):
                r_ = _fvbox(st, k_)
                if r_:
                    fv[r_[0]] = r_[1]
        with top[11].popover(L("Symbol") + _n("cs_side", "cs_mode", "cs_regime")):
            ss.setdefault("cs_n", int(rd.get("n", 20)))   # the chart count / columns / height widgets live on the grid's own top line (render_chart_scanner)
            n_show, ncols = int(ss.get("cs_n") or 20), int(ss.get("cs_cols") or 4)
            side_pick = st.selectbox(L("Side"), _sides, index=_sides.index(rd.get("side", "Both")), key="cs_side", format_func=L)
            mode = st.selectbox(L("Match"), _modes, index=_modes.index(rd.get("mode", "All selected")), key="cs_mode", format_func=L)
            from modules.regime import REGIMES as _RG
            sel_regime = st.multiselect(L("Market regime"), _RG, key="cs_regime", help=L("Trend / Chop / Hi-Vol / Crash / Squeeze / Thin, from the candles of the chosen timeframe. A description of now, not a signal."))
        top[12].button(L("Clear all filters"), key="cs_clear_top", on_click=_clear_cs_filters)
    sel_mom = list(sel_mom_a) + list(sel_mom_v)
    quick = []

    if sel_strat:
        qp["strat"] = ",".join(sel_strat)
    elif "strat" in qp:
        del qp["strat"]
    sel_ema = []
    if rel_px != "—":
        sel_ema.append(f"px_{rmap[rel_px]}_{len_px}")
    if rel_ma != "—":
        sel_ema.append(f"ma_{rmap[rel_ma]}_{pair.replace('/', '_')}")
    sel_ema += {"Bullish (px>9>20>50)": ["stack_bull"], "Bearish (px<9<20<50)": ["stack_bear"],
                "Above all EMAs": ["above_all"], "Below all EMAs": ["below_all"]}.get(stack, [])
    sel = list(dict.fromkeys(sel_rsi + sel_ema + sel_pat + sel_strat + sel_mom + list(quick or [])))
    want = {"Buy only": "buy", "Sell only": "sell"}.get(side_pick)
    return {"cols": ncols, "tf": tf, "n": int(n_show), "want": want, "any": mode == "Any selected", "look": look, "sel": sel, "fv": fv, "regime": list(sel_regime),
            "slots": tuple(top[13:16]) if _grid else None}


def _radar_hits(d, f):
    """(conditions met, conditions chosen) for one chart: indicator / pattern / strategy flags plus the Finviz-style technical lists."""
    from modules import fv_screen as _FV
    hits = sum(1 for k in f["sel"] if match_filters(d, [k], f["want"], False))
    if f["fv"] and d.get("fv"):
        ctx = {"candles": set(d.get("cn", ())), "flags": set(d["flags"])}
        hits += sum(1 for k, c in f["fv"].items() if _FV.test(k, c, d["fv"], ctx))
    return hits, len(f["sel"]) + len(f["fv"])


def _radar_pass(d, f):
    if f.get("regime") and d.get("regime") not in f["regime"]:   # market-regime filter (Radar panel): symbols in another regime drop out
        return False
    h, n = _radar_hits(d, f)
    if not n:
        return match_filters(d, [], f["want"], False)
    return h > 0 if f["any"] else h == n


def _radar_symbols(f):
    """Symbols of the universe that pass the shared panel (all of them when no filter is set). Every Radar view uses this, so the filters work everywhere."""
    if not (f["sel"] or f["fv"] or f["want"]):
        return list(SCAN_SYMBOLS)
    data = _radar_data(f)
    return [s_ for s_, d_ in (data or {}).items() if _radar_pass(d_, f)]


def _tf_bars(tf):
    """Candle length of a timeframe label in minutes (for the performance spans)."""
    import re as _re
    m = _re.match(r"(\d+)(m|h|d|w|mo)$", tf)
    n, u = (int(m.group(1)), m.group(2)) if m else (1, "h")
    return n * {"m": 1, "h": 60, "d": 1440, "w": 10080, "mo": 43200}[u]


def _radar_data(f):
    """Scan data of the universe on the panel's timeframe (cached), or None after a message."""
    try:
        with st.spinner(L("Loading the candles of every Radar symbol (the first load can take up to a minute; later loads are cached)")):
            return _chart_scan_data(tuple(SCAN_SYMBOLS), f["tf"], f["look"])
    except Exception as e:
        st.warning(f"Could not load candles: {e}")
        return None


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
    _symt = tuple(SCAN_SYMBOLS)
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
    key = json.dumps([items, per_row, ch_h, _ui_lang(), UI_THEME, os.path.getmtime(os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules", "workspace_app.html"))], sort_keys=True, default=str)   # a new build of the chart app = a new page
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
                                   ui_theme="" if UI_THEME == "classic" else UI_THEME, ui_bg=UI_BG, ui_mat=UI_MAT)
        ss["radar_ws_doc"] = (key, doc, time.time())
    rows = -(-len(items) // per_row)
    st.iframe(doc, height=rows * ch_h + 40, alt="Radar charts")   # + the "indicators on ALL charts" bar


_PT_IND = {   # Radar flag -> the Workspace chart's indicator (its ƒx menu id) that draws it
    "st_elliott": "ew", "st_ew3": "ew", "sch_elliott": "ew", "st_harm": "harm", "sch_harmonic": "harm",
    "st_msb": "msb", "st_ob": "msb", "st_breaker": "msb", "st_mss": "msb", "st_mit": "msb", "st_unicorn": "msb", "sch_ict": "msb",
    "st_ote": "ote", "st_fib": "ote", "sch_fib": "ote", "st_fvg": "sig", "st_ifvg": "sig", "st_judas": "sig", "st_silver": "sig", "st_m2022": "sig", "st_pd": "sig",
    "st_smt": "smt", "sch_smt": "smt", "st_kzs": "kzs", "st_sessamd": "kz", "st_orb": "kz", "st_po3": "kz", "sch_session": "kz",
    "st_donch": "don", "st_turtle55": "don", "st_sma1040": "ma", "st_ma": "ma", "sch_trend": "don", "st_vwap": "vwap", "st_bvd": "bvd",
    "st_rsidiv": "rsi", "st_macddiv": "macd", "sch_mom": "rsi", "st_sweep": "ll", "sch_liq": "ll", "vol_2x": "volume", "vol_3x": "volume",
}
_PT_ORDER = ["ew", "harm", "msb", "ote", "sig", "smt", "kzs", "kz", "ll", "bvd", "don", "vwap", "ma", "rsi", "macd", "volume"]   # main tools first: point 1 opens by itself
_PT_SR = {"st_rect", "st_dbl", "st_crt", "st_wyck", "sch_level", "sch_rect", "sch_wyck", "dbl_top", "dbl_bottom", "chan_up", "chan_dn", "tl_up", "tl_dn"}


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

def render_info_strip():
    """Item 44: one thin line under the header - 'educational, not advice' plus whether each data source answers and the
    date of the last lab run. Off switch: Theme & language menu > 'Info strip'. Hidden in Workspace focus mode."""
    if not st.session_state.get("info_strip", True) or st.session_state.get("focus_ws"):
        return
    src = _bg("srcping", _source_ping, {}, ttl=60, wait=1.0)   # never holds the page up when a source is down (4 s timeouts)
    from modules import office_kpi as _OK
    built = (_OK.summary(_OK.load()) or {}).get("built") or "-"
    dot = lambda ok: f"<span style='display:inline-block;width:7px;height:7px;border-radius:50%;background:{'#2dd4bf' if ok else '#f87171' if ok is False else '#848e9c'};margin:0 4px'></span>"
    items = [f"<b style='color:#f0b429'>{html.escape(L('Educational, not investment advice'))}</b>"]
    items += [f"{dot(src.get(n))}{n} {html.escape(L('live') if src.get(n) else L('down') if src.get(n) is False else L('checking'))}" for n in ("OKX", "Hyperliquid")]
    items.append(f"{html.escape(L('Last lab run'))} {html.escape(str(built))}")
    items.append(html.escape(L("No automatic orders")))
    st.markdown("<div style='display:flex;flex-wrap:wrap;gap:14px;align-items:center;font-size:11px;color:#a3adba;background:#161a1e;"
                "border:1px solid #2b3139;border-radius:6px;padding:3px 10px;margin:0 0 6px'>" + "".join(f"<span>{x}</span>" for x in items) + "</div>",
                unsafe_allow_html=True)


render_info_strip()

def _page_0():   # workspace
    global _DP, _JSYNC, _cal, _cmc, _e, _err, _mac, _n, _news, _stk, _stk_t, _tfs, _tga, _tga_e2, _tga_n2, _ws_stat, _yf, _yf_job, cached_ws, render_bridge, world_errs, world_items, ws_lang, ws_links   # M7: same module-level names as before the page became a function
    _ws_stat = st.empty()   # loading steps shown while the server builds the Workspace (cleared once it is sent)
    try:
        _ws_stat.caption("⏳ Workspace: scan state...")
        ws_lang = st.session_state.get("ws_lang", "en")
        cached_ws = build_ws_payload(_ws_universe(ACTIVE_SYMBOLS))
        if tg_on and not cached_ws.get("loading"):
            from modules import telegram_alerts as _tga
            _n, _err = _tga.dispatch(cached_ws.get("alerts") or [], _tg_sent(), int(tg_top), int(tg_min))
            try:   # day plan (timeframe confluence): the best new plans, one message each (not repeated for 4 hours)
                from modules import day_plan as _DP
                _tga_n2, _tga_e2 = _DP.dispatch(_dayplan_events(), _tg_sent(), _tga.send, top_n=int(tg_top))
                if _tga_e2:
                    st.sidebar.warning("Telegram day plan: " + _tga_e2)
                _DP.dispatch(_dayplan_watch(), _tg_sent(), _tga.send, top_n=2, resend_after_s=2 * 3600, fmt=lambda it_: _DP.format_watch(it_))   # heads-ups: context setups that agree with the 1D + 4H bias
            except Exception:
                pass
            if _err:
                st.sidebar.warning("Telegram: " + _err)
            elif _n:
                st.sidebar.caption(f"Telegram: sent {_n} alert(s).")
        _ws_stat.caption("⏳ Workspace: news / calendar / macro feeds...")
        world_items, world_errs = _bg("world", _world_news, ([], ["world news loading..."]))
        ws_links = [{"name": n, "url": u} for n, u in EXTERNAL_LINKS.items() if n != "Finviz Patterns"]
        ws_links.append({"name": "Finviz", "url": EXTERNAL_LINKS["Finviz Patterns"],
                         "patterns": [{"name": L(k), "url": FINVIZ_PATTERN_URL.format(signal=v)} for k, v in FINVIZ_PATTERNS.items()]})
        _yf = {}
        if any(x.startswith("Y:") for x in ACTIVE_SYMBOLS):
            def _yf_job(syms=tuple(ACTIVE_SYMBOLS)):
                from modules.yahoo_feed import embed as _yf_embed
                return _yf_embed(syms)
            _yf = _bg("yf|" + ",".join(ACTIVE_SYMBOLS), _yf_job, {}, ttl=120)
        _cal = _bg("cal", _calendar_rows, [])
        _news = _bg("news", lambda: get_latest_news("general", 15), [])
        _cmc = _bg("cmc", _cmc_data, None)
        _mac = _bg("macro", _macro_fund, None)
        _stk_t = _stock_tickers()
        _stk = _bg("stocks|" + ",".join(_stk_t), lambda: _stock_fund(_stk_t), None)
        _ws_stat.caption("⏳ Workspace: building the page...")
        _tfs = get_tf_stats()
        render_workspace(ACTIVE_SYMBOLS, _news, ws_lang, yf=_yf, cal=_cal, height=min(ws_height, 860) if _IS_MOBILE else ws_height, alerts=cached_ws["alerts"], seed=cached_ws["seed"],
                         scan=cached_ws["scan"], links=ws_links, asset_cls=asset_cls, meme=[b + "-USDT" for b in MEME_BASES], world=world_items, tfstats=_tfs,
                         ready=cached_ws.get("mini", []), smt=_smt_chips(ws_lang), scanning=bool(cached_ws.get("loading")), cmc=_cmc, macrof=_mac, stockf=_stk, world_errs=world_errs,
                         ui_theme="" if UI_THEME == "classic" else UI_THEME, ui_bg=UI_BG, ui_mat=UI_MAT)
        _ws_stat.empty()
        try:   # mounted AFTER the workspace (like the guide bridge): mounted before it, the hidden iframe could miss Streamlit's 60 s ready window on a slow load and show a yellow warning
            from modules import journal_sync as _JSYNC   # browser journal -> server store (one journal, see modules/trade_journal.py)
            _JSYNC.sync()
        except Exception:
            pass
        try:
            from modules.guide_ai import render_bridge
            render_bridge()   # hidden: lets the guide character ask Claude without the key reaching the browser
        except Exception:
            pass
        if world_errs:
            st.caption(L("World Monitor feeds unavailable:") + " " + ", ".join(world_errs[:4]))
        if cached_ws.get("errs"):
            st.caption(L("Scan problems:") + " " + " | ".join(L(x_) for x_ in cached_ws["errs"][:3]))
        st.caption(L("Drag a title bar to move, drag the corner to resize, - minimise, square = maximise (double-click title too). "
                   "Widgets with the same # in the title bar share one symbol. Layout is remembered in your browser. "
                   "Data comes straight from OKX in your browser, no refresh needed."))
    except Exception as _e:
        st.error(f"Workspace error: {type(_e).__name__}: {_e}")

# the Chart Scanner scans the whole universe synchronously (can take minutes on a cold server): it runs AFTER the Workspace,
# otherwise the first tab stays blank until the scan finishes (Streamlit renders in code order, not tab order)
def render_day_plan(scan_symbols):
    """Radar > Day plan: today's trades by session and timeframe confluence (modules/day_plan.py). Standard = confluence; option = scalp on one timeframe."""
    from modules import day_plan as _DP, day_plan_ui as _DPU
    ar = _ui_lang() == "ar"
    st.markdown(_DPU.timeline_html(_DP.session_clock(), ar=ar), unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.3, 1, 1.4, 1])
    mode_lbl = c1.radio(L("Mode"), ["Timeframe confluence (standard)", "Scalp (one timeframe)"], key="dp_mode")
    mode = "conf" if mode_lbl.startswith("Timeframe") else "scalp"
    trig = None
    if mode == "scalp":
        trig = (c2.selectbox(L("Trigger timeframe"), ["5m", "15m", "1h"], key="dp_tf"),)
    mv = c3.selectbox(L("Minimum possible move (points)"), ["Any", 100, 150, 200, 300, 1000], key="dp_pts")
    stars = c4.slider(L("Min stars"), 1, 4, 2, key="dp_stars")
    schools = st.multiselect(L("Only these schools (empty = all)"), ["SMC / ICT", "Elliott wave", "Fibonacci", "Liquidity", "Trend (MA)", "Levels / breakouts", "Time (sessions)", "Price action", "Chart patterns (range)", "Wyckoff", "Momentum / divergence", "Harmonic"], key="dp_sch")
    uni = st.radio(L("Universe"), ["Day-plan list", "Current Radar universe"], horizontal=True, key="dp_uni")
    tr = st.number_input(L("Stop starts moving after (points)"), 10, 5000, 100, 10, key="dp_trail", help=L("Standard mode: once a trade is this many points in profit the stop moves to break-even, then trails."))
    syms = tuple(DAY_SYMBOLS if uni == "Day-plan list" else (scan_symbols or CRYPTO_SYMBOLS)[:20])

    @st.cache_data(ttl=300, show_spinner=False)
    def _run(syms_t, mode_, trig_, sch_t, mv_, stars_, tr_):
        return _DP.scan(list(syms_t), lambda s_, t_: get_klines(s_, t_, 300), mode=mode_, trigger_tfs=trig_, schools=list(sch_t) or None,
                        min_points=(0 if mv_ == "Any" else float(mv_)), min_stars=stars_, trail_start_points=float(tr_))

    with st.spinner(L("Building the day plan...")):
        plans = _run(syms, mode, trig, tuple(schools), mv, int(stars), float(tr))
    st.caption(L("Higher timeframes (1D + 4H) set the bias, the trigger timeframes give the entry; a plan is listed only when enough timeframes agree. Stars = the scanner's evidence count, not a win rate; new schools are context until the lab measures them. Not financial advice."))
    if not plans:
        st.info(L("No plan matches right now. Loosen the filters or wait for the next session."))
        return
    for p in plans[:30]:
        st.markdown(_DPU.card_html(p, ar=ar), unsafe_allow_html=True)
    if st.button(L("Send the top plans to Telegram"), key="dp_send"):
        from modules import telegram_alerts as _tga
        _n, _e = _DP.dispatch(plans, {}, _tga.send, top_n=3)
        st.success(f"Telegram: {_n} sent") if not _e else st.warning(_e)


def render_smt_board():
    """Radar > SMT pairs: every correlated pair on the chosen timeframes; each event shows BOTH markets side by side."""
    from modules import intermarket as _IM, intermarket_ui as _IMU
    ar = _ui_lang() == "ar"
    c1, c2 = st.columns([3, 1])
    tfs = c1.multiselect(L("Timeframes"), list(_IM.TF_ORDER[:7])[::-1], default=[t for t in ("15m", "1h", "4h", "1d")], key="smt_tfs")
    if c2.button(L("Rescan now"), key="smt_rescan"):
        st.cache_data.clear()

    @st.cache_data(ttl=300, show_spinner=False)
    def _run(tfs_t):
        return _IM.scan_pairs(lambda s_, t_: get_klines(s_, t_, 300), tfs=tfs_t)

    with st.spinner(L("Comparing the correlated pairs...")):
        ev = _run(tuple(tfs or ("1h",)))
    st.caption(L("SMT = two correlated markets disagree at a swing (one makes a new low / high, the other refuses). A hint of reversal, not a trade by itself; no win rate is claimed here. Pairs that stopped moving together are skipped."))
    if not ev:
        st.info(L("No SMT between the correlated pairs on these timeframes right now."))
        return
    for e in ev[:40]:
        st.markdown(_IMU.event_card(e, ar=ar), unsafe_allow_html=True)


def _page_1():   # cscan
    global SCAN_SYMBOLS, _IMU, _OLD_RV, _ac_msg2, _acm, _disp, _e, _il, _o, _rf, _rv, _x77_send, _xe   # M7: same module-level names as before the page became a function
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
        SCAN_SYMBOLS, _ac_msg2 = _acm.class_symbols(asset_cls, CRYPTO_SYMBOLS, top=int(st.session_state.get("uni_n", 24)), mtype=MARKET_TYPES.get(market_type, "SPOT"), wide=True)
        SCAN_SYMBOLS = (SCAN_SYMBOLS or list(CRYPTO_SYMBOLS))[:int(st.session_state.get("uni_n", 24))]
        _rf = _radar_filters(_disp) if _rv not in ("SMT pairs", "Day plan") else None
        if _disp == "SMT pairs":
            render_smt_board()
        elif _disp == "Day plan":
            render_day_plan(SCAN_SYMBOLS)
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
            _x77_send(SCAN_SYMBOLS)
        except Exception as _xe:
            st.caption(f"X77: {type(_xe).__name__}")
    except Exception as _e:
        st.error(f"Chart Scanner error: {type(_e).__name__}: {_e}")

# (removed 2026-10-17) a "sleep 5 s + st.rerun()" loop used to run here while the background scan was busy: every rerun rebuilt and
# re-sent the Workspace, so its frame reloaded every 5 s (blank page) and the CPU never rested (the app got throttled).
# The Workspace shows "scanning..." and picks the results up on the next normal run.


def _page_2():   # lab
    render_lab_page()

def _page_7():   # academy (owner 2026-10-23): lessons from the team's research, each with a status and a review verdict
    render_academy_page()

def _page_3():   # playbook
    render_playbook_page()

def _page_5():   # AI (owner 2026-10-22): Mr X, the backtest agent, and the agent desk in one tab bar
    global _U, _adx, _ai_tab, _c, render_ai_page   # M7: same module-level names as before the page became a function
    if st.session_state.get("ai_tab") not in ("Mr X", "Backtest agent"):   # 2026-11-09: Agent desk folded under Mr X (owner approved)
        st.session_state.pop("ai_tab", None)
    _ai_tab = st.segmented_control(L("AI"), ["Mr X", "Backtest agent"], default="Mr X", format_func=L, key="ai_tab", label_visibility="collapsed")
    if _ai_tab == "Backtest agent":
        _c = st.columns([1.2, 0.8, 4])
        _bt_agent(_c[0].text_input(L("Symbol"), "BTC-USDT", key="ai_bt_sym"), _c[1].selectbox(L("Timeframe"), ["1h", "4h", "1d"], index=2, key="ai_bt_tf"))
    else:
        from modules.ai_page import render_ai_page
        render_ai_page(ACTIVE_SYMBOLS, L)
        from modules import office_ui as _U
        st.markdown(_U.CSS, unsafe_allow_html=True)
        _adx = st.expander(L("Agent desk"), expanded=False)
        _adx.markdown(L("The agent desk turns what you say into a task for the meeting room (goal, owner, files, acceptance, gate, expected cost) and hands it to the right account. It never merges, never runs a paid job and never trades."))
        _adx.markdown(_U.table([L("Needs"), L("Status")], [
            [L("A model key (OpenAI or the free Gemini key)"), _U.badge(L("key set") if (_has_secret("OPENAI_API_KEY") or _has_secret("GEMINI_API_KEY")) else L("no key"), "ok" if (_has_secret("OPENAI_API_KEY") or _has_secret("GEMINI_API_KEY")) else "warn")],
            [L("A GitHub token limited to this repository (write the meeting room, open an @claude request)"), _U.badge(L("key set") if _has_secret("GITHUB_TOKEN_DESK") else L("no key"), "ok" if _has_secret("GITHUB_TOKEN_DESK") else "warn")],
            [L("A daily spending cap"), _U.badge(L("owner decision"), "off")]]), unsafe_allow_html=True)
        _adx.caption(L("Until these are set, write tasks in the meeting room; the site manager distributes them."))

def _stats_lab():
    """Stats > Lab evidence: what the weekly lab really measured, in the control-room style; nothing estimated."""
    from modules import office_kpi as _OK, office_ui as U
    d = _OK.load(); s = _OK.summary(d) or {}
    st.markdown(U.CSS, unsafe_allow_html=True)
    if not s:
        st.info(L("No lab file yet (data/strategy_lab.json)."))
        return
    b = s.get("best") or {}; la = _OK.lab_avg(d)
    st.markdown("<div class='xo-row'>" + U.gauge(s.get("passed", 0), s.get("candidates", 0), L("Evidence gate"),
                L("n >= 100 · t > 3 · net > 0 · both halves positive, after 0.1R"), L("groups passed")) +
                U.indicators(L("Indicators"), [
                    (L("Detectors in the lab"), s.get("detectors", "-"), f"{s.get('symbols', 0)} " + L("symbols"), None),
                    (L("Last lab run"), s.get("built") or "-", L("weekly"), "info"),
                    (L("Best net avg R (n >= 100)"), f"{b['net']:+.3f}" if b else "-", f"{b.get('key', '')} {b.get('tf', '')} · n {b.get('n', '')}", "ok" if b and b["net"] > 0 else None),
                    (L("All detectors, avg R"), f"{la:+.3f}" if la is not None else "-", L("net") + f" {la - _OK.COST_R:+.3f}" if la is not None else "", "ok" if la and la > _OK.COST_R else "bad"),
                    (L("OFF (no longer decide a trade)"), len(s.get("off", [])), ", ".join(s.get("off", [])), None),
                    (L("Cost per trade"), f"{_OK.COST_R}R", L("planning estimate"), None)]) + "</div>", unsafe_allow_html=True)
    _office_charts()
    rows = _OK.top_rows(d)
    fmt = lambda v, p="+.3f": "-" if v is None else format(v, p)
    st.markdown(f"<div class='xo-h' style='margin-top:6px'>{html.escape(L('Strongest detector x timeframe (n >= 100), by net avg R'))}</div>", unsafe_allow_html=True)
    st.markdown(U.table([L("Detector"), L("Timeframe"), L("School"), "n", L("Win rate"), L("avg R"), L("net"), L("vs random"), "t", L("Gate")],
                        [[U.esc(r["key"]), U.esc(r["tf"]), U.esc(L(r["school"] or "-")), r["n"], "-" if r["win"] is None else f"{r['win']:.0f}%",   # the lab stores win as a percent
                          fmt(r["avgR"]), fmt(r["net"]), fmt(r["vs_random"]), fmt(r["t"], ".2f"),
                          U.badge(L("passed") if r["gate"] else (L("no t yet") if r["t"] is None else L("not yet")), "ok" if r["gate"] else "warn")]
                         for r in rows]), unsafe_allow_html=True)
    st.caption(L("vs random = avg R minus the random-entry baseline on the same bars. 'no t yet' = the lab has not measured the t-stat for this row, so it cannot pass the gate."))


def _page_8():   # lab summary (summary on top; the former Validation Lab / Calibration / Class rotation / Evidence summary tabs as collapsed sections)
    global _lab_exc, render_lab_summary   # M7: same module-level names as before the page became a function
    try:
        from modules.lab_summary import render_lab_summary
        render_lab_summary(_scan_store().get("payload") or {})
    except Exception as _lab_exc:
        st.error(_xl("ملخص المعمل: ", "Lab Summary: ") + str(_lab_exc))
    st.stop()
# Pages that are one module call (M7 / 4.2): index -> (error label, module, function, comment). The page imports its module only when opened.
_MODULE_PAGES = {
    10: ("Prop Firms", "modules.prop_firms", "render_prop_firms", "prop firm account tracker (added 2026-11-04)"),
    12: ("TIA", "modules.tia_page", "render_tia", "TIA institutional intelligence terminal (new standalone parent-company workspace)"),
    11: ("Spot", "modules.spot_page", "render", "Spot desk: crypto + metals, ledger / invoices, alerts (added 2026-11-06)"),
    17: ("Trade Intelligence Center", "modules.intelligence_center_ui", "render", "knowledge + meeting journal, read-only over Lab / Radar / Spot (MR !27)"),
    18: ("V7 Research", "modules.v7_page", "render", "read-only view of data/v7; conditions in docs/V7_NEXT_STEP_REPLY_2026-11-10.md"),
    19: ("2.6 Lab", "modules.two_six_lab", "render", "2.6 Strategy Intelligence (owner 2026-11-13): research status only, no orders / prices"),
    22: ("Preview", "modules.unwired_preview", "render", "built-but-unwired pages / tools / libraries for the owner to review; read-only (owner 2026-11-21)"),
    21: ("X77", "modules.x77_page", "render", "saved items + chart labels by school; saves / labels only, no orders (owner 2026-11-20)"),
    20: ("RSI Heatmap", "modules.rsi_heatmap", "render", "additive market-wide research map (MR !68)"),
    23: ("Strategy Ledger", "modules.ledger_page", "render", "every strategy's plans replayed on the candles, explained and ranked; read-only (owner 2026-11-24)"),
}


def _module_page(i):
    label, mod, fn, _ = _MODULE_PAGES[i]
    try:
        import importlib
        f = getattr(importlib.import_module(mod), fn)
        if i == 22:   # Preview takes (st, L); statements, not one expression (Streamlit magic would print its None)
            f(st, L)
        else:
            f()
    except Exception as e:
        st.error(f"{label}: {type(e).__name__}: {e}")
    st.stop()

# M7 (maintenance plan 4.1): one function per page, exactly one runs (the old `if PAGE == N:` blocks, same order of indexes).
_PAGE_FN = {0: _page_0, 1: _page_1, 2: _page_2, 7: _page_7, 3: _page_3, 5: _page_5, 8: _page_8}
_PAGE_FN.update({i: (lambda i=i: _module_page(i)) for i in _MODULE_PAGES})
_PAGE_FN[9] = _pg9.render_page
_PAGE_FN[4] = _pg4.render_page
_PAGE_FN[6] = _pg6.render_page
_PAGE_FN[16] = _pg16.render_page
if PAGE in _PAGE_FN:
    _PAGE_FN[PAGE]()
