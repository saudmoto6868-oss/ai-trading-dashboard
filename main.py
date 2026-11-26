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
from modules.i18n import L, RTL_CSS, lang as _ui_lang
from modules.page_kit import md_sections as _md_sections, xl as _xl   # moved out of main.py (M7)
from modules.page_playbook import render_playbook_page   # Playbook page moved out of main.py (M7)
from modules.page_academy import render_academy_page   # Academy page moved out of main.py (M7)
from modules import page_options as _pg16   # page 16 moved out of main.py (M7)
from modules import page_alerts as _pg6   # page 6 moved out of main.py (M7)
from modules import page_journal as _pg4   # page 4 moved out of main.py (M7)
from modules import page_hub as _pg9   # page 9 moved out of main.py (M7)
from modules import page_radar as _pg1   # page 1 (Radar) moved out of main.py (M7)
from modules import page_workspace as _pg0, page_lab as _pg2, page_ai as _pg5   # pages 0, 2, 5, 8 moved out of main.py (M7)
from modules.page_lab import _source_ping, _office_charts   # still used by the info strip / control room
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
    scan_crypto_group, _bg,
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
from modules.asset_classes import CLASSES as ASSET_CLASSES, MARKET_TYPES, class_symbols
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

# (removed 2026-10-17) a "sleep 5 s + st.rerun()" loop used to run here while the background scan was busy: every rerun rebuilt and
# re-sent the Workspace, so its frame reloaded every 5 s (blank page) and the CPU never rested (the app got throttled).
# The Workspace shows "scanning..." and picks the results up on the next normal run.


def _page_7():   # academy (owner 2026-10-23): lessons from the team's research, each with a status and a review verdict
    render_academy_page()

def _page_3():   # playbook
    render_playbook_page()

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
_PAGE_FN = {0: _pg0._page_0, 1: _pg1._page_1, 2: _pg2._page_2, 7: _page_7, 3: _page_3, 5: _pg5._page_5, 8: _pg2._page_8}
_PAGE_FN.update({i: (lambda i=i: _module_page(i)) for i in _MODULE_PAGES})
_PAGE_FN[9] = _pg9.render_page
_PAGE_FN[4] = _pg4.render_page
_PAGE_FN[6] = _pg6.render_page
_PAGE_FN[16] = _pg16.render_page
from types import SimpleNamespace as _NS
st.session_state["_rt"] = _NS(UI_THEME=UI_THEME, UI_BG=UI_BG, UI_MAT=UI_MAT, SCAN_SYMBOLS=SCAN_SYMBOLS, asset_cls=asset_cls,   # per-session values for moved pages (page_kit.rt)
                              market_type=market_type, _ac_msg=_ac_msg, ACTIVE_SYMBOLS=ACTIVE_SYMBOLS, _IS_MOBILE=_IS_MOBILE,
                              tg_on=tg_on, tg_top=tg_top, tg_min=tg_min, ws_height=ws_height)
if PAGE in _PAGE_FN:
    _PAGE_FN[PAGE]()
