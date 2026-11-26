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

import streamlit as st

from config import (
    CRYPTO_SYMBOLS,
    EXTERNAL_LINKS, FINVIZ_PATTERNS, FINVIZ_PATTERN_URL,
    TRADE_TYPES, AUTO_REFRESH_SECONDS, TV_SYMBOL_MAP,
)
from modules.data_fetcher import get_mt5_data
from modules.scorer import (
    score_symbol,
)
from modules.market_cache import get_klines
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
from modules import page_radar as _pg1   # page 1 (Radar) moved out of main.py (M7)
from modules.page_radar_filters import _strat_name   # shared
from modules.page_radar_data import _CS_TFS   # shared with the Technical Office / AI pages
from modules import office_ui as _OUI   # noqa: F401  (registers the Technical Office Arabic keys in i18n.AR at import)
from modules.site_icons import site_icon_b64
from modules.header_bar import render_header_bar
from modules.macro import api_key, fetch_macro
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
    scan_crypto_group, _bg, _scan_store, _tg_sent, get_tf_stats, _ws_universe, _dayplan_watch, _dayplan_events, _smt_events, build_ws_payload,
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
_PAGES = ["Workspace", "Radar", "Technical Office", "Playbook", "Journal", "AI", "Alerts", "Academy", "Lab Summary", "Research Hub", "Prop Firms", "Spot", "TIA", "Trading", "Lab", "Learn & AI", "Options & macro", "Trade Intelligence Center", "V7", "2.6 Lab", "RSI Heatmap", "X77", "Preview"]   # 22 = Preview of built-but-unwired items (owner 2026-11-21, Lab hub)   # 21 = X77 (owner 2026-11-20, Lab hub sub-tab)   # 17 = Trade Intelligence Center (2026-11-10, Learn & AI hub; MR !27 renumbered from 13); 13-15 = hub pages, 16 = options + macro regime (2026-11-09); 4 = Journal (was Stats); 11 = Spot desk (2026-11-06, next to the Radar in the bar); 10 = Prop Firms (added 2026-11-04: inactivity timers, rules, links per account); 8 = Lab Summary; Academy is index 7 (the Workspace guide uses fixed indexes)
_HUBS = {13: [10, 16, 4, 6], 14: [2, 9, 3, 19, 21, 22], 15: [5, 7, 17]}   # 8 (Lab Summary) lives in Technical Office > Lab results (owner 2026-11-09)   # owner 2026-11-09: Workspace, Radar, then three hubs; each hub shows its old pages as one row of sub-tabs
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
_PAGE_FN = {0: _page_0, 1: _pg1._page_1, 2: _page_2, 7: _page_7, 3: _page_3, 5: _page_5, 8: _page_8}
_PAGE_FN.update({i: (lambda i=i: _module_page(i)) for i in _MODULE_PAGES})
_PAGE_FN[9] = _pg9.render_page
_PAGE_FN[4] = _pg4.render_page
_PAGE_FN[6] = _pg6.render_page
_PAGE_FN[16] = _pg16.render_page
from types import SimpleNamespace as _NS
st.session_state["_rt"] = _NS(UI_THEME=UI_THEME, UI_BG=UI_BG, UI_MAT=UI_MAT, SCAN_SYMBOLS=SCAN_SYMBOLS, asset_cls=asset_cls,   # per-session values for moved pages (page_kit.rt)
                              market_type=market_type, _ac_msg=_ac_msg)
if PAGE in _PAGE_FN:
    _PAGE_FN[PAGE]()
