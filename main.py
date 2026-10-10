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
import time
from datetime import datetime

import pandas as pd
import streamlit as st

from config import (
    FOREX_SYMBOLS, METALS_SYMBOLS, STOCK_SYMBOLS, CRYPTO_SYMBOLS,
    EXTERNAL_LINKS, QUICK_LINK_ICONS, FINVIZ_PATTERNS, FINVIZ_PATTERN_URL,
    TRADE_TYPES, AUTO_REFRESH_SECONDS, TV_SYMBOL_MAP,
)
from modules.data_fetcher import get_mt5_data
from modules.scorer import (
    score_symbol, scan_symbol, SCAN_TFS, CONTEXT_TFS, TF_LABEL, htf_lines, scenarios,
)
from modules.market_cache import fetch_frames, get_klines
from modules.arabic import (
    tags_html, trade_chip_html, tag_for, signal_ar, htf_lines_ar, scenarios_ar, tv_link, chart_svg, DIR_AR, TF_AR, TRADE_AR, n_, scan_entry,
)
from modules.risk_engine import build_trade_plan
from modules.signals import FAMILY_ICONS
from modules.alerts import check_and_fire_alerts, ALERT_SCORE_THRESHOLD
from modules.tv_widget import render_tv_chart
from modules.workspace import render_workspace, seed_from_df
from modules.news_feed import get_latest_news, ticker_html
from modules.crypto_extras import render_order_book, render_time_and_sales, search_dexscreener_pairs
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
    page_title="6868 X", layout="wide", page_icon="\U0001F4CA",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    .stTabs [data-baseweb="tab"] { color: #eaecef; }
    .stTabs [aria-selected="true"] { color: #f0b90b; border-bottom-color: #f0b90b; }
    div[data-testid="stMetricValue"] { color: #f0b90b; }
    .block-container { padding-top: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# ---- Settings (sidebar) -----------------------------------------------------
st.sidebar.header("Settings")
auto_on = st.sidebar.checkbox("Auto-refresh (live data)", value=True)
refresh_secs = st.sidebar.slider("Refresh every (seconds)", 10, 60, AUTO_REFRESH_SECONDS, step=5)
play_sound = st.sidebar.checkbox("Play sound on NEW strong signals", value=True)
smart_mult = st.sidebar.slider(
    "Smart trade = size >= N x median print", 2.0, 10.0, 4.0, step=0.5,
    help="Prints this many times larger than the median trade in the window are flagged SMART; 2.5x that is WHALE.",
)
big_order_mult = st.sidebar.slider(
    "Big limit order = N x median level", 3.0, 15.0, 5.0, step=0.5,
    help="Used by the DOM highlight and by Limit Tracking.",
)
st.sidebar.markdown("**Order-flow effects**")
fast_secs = st.sidebar.slider("DOM / Time&Sales refresh (seconds)", 1, 10, 3,
                              help="How often the two order-flow panels update by themselves (flashes appear on each update).")
absorb_mult = st.sidebar.slider(
    "Absorption = level volume >= N x median level", 2.0, 8.0, 3.0, step=0.5,
    help="Heavy volume trading at one price while the price barely moves.",
)
st.markdown(f"<style>{ORDERFLOW_CSS}</style>", unsafe_allow_html=True)
if auto_on and st_autorefresh is not None:
    st_autorefresh(interval=refresh_secs * 1000, key="auto_refresh")
elif auto_on:
    st.sidebar.warning("streamlit-autorefresh is not installed - add it to requirements.txt.")

# ---- Header: title, news ticker, quick links --------------------------------
head_l, head_r = st.columns([3, 1])
head_l.title("6868 X")
head_r.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
               + (f"  \nLive: every {refresh_secs}s" if auto_on else "  \nLive: off"))

try:
    st.markdown(ticker_html(get_latest_news(category="general", limit=15)), unsafe_allow_html=True)
except Exception as e:  # the ticker must never take the page down
    st.caption(f"News ticker unavailable: {e}")


def render_quick_links():
    names = list(EXTERNAL_LINKS)
    cols = st.columns(len(names))
    for col, name in zip(cols, names):
        label = f"{QUICK_LINK_ICONS.get(name, '')} {name}".strip()
        with col:
            if name == "Finviz Patterns":
                with st.popover(label):
                    st.caption("Pick a chart pattern - opens Finviz in a new tab")
                    for pat, signal in FINVIZ_PATTERNS.items():
                        st.link_button(pat, FINVIZ_PATTERN_URL.format(signal=signal))
                    st.link_button("All charts (no filter)", EXTERNAL_LINKS[name])
            else:
                st.link_button(label, EXTERNAL_LINKS[name])


render_quick_links()


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


def scan_crypto_group(symbols, tf):
    """Multi-timeframe scan: candles for the chosen timeframe PLUS its higher
    context timeframes are fetched in parallel (cached), then scored."""
    frames, fetch_errors = fetch_frames(symbols, [tf] + CONTEXT_TFS[tf])
    results, errors = [], []
    for sym in symbols:
        try:
            results.append(scan_symbol(sym, frames[sym], tf))
        except Exception as e:
            errors.append(f"{sym}: {fetch_errors.get(sym) or e}")
    return results, "; ".join(errors)


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
    selected = st.multiselect("Trade type", TRADE_TYPES, default=TRADE_TYPES, key=f"tt_{key}")
    filtered = [r for r in results if r["trade_type"] in selected]
    if notice:
        st.caption(notice)
    elif not filtered:
        st.info("No symbols match the current filter.")
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
        st.info("لا توجد رموز مطابقة للفلتر الحالي.")
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
            f"<span style='color:{acol};font-size:12px'>{arrow} {DIR_AR.get(r['direction'], '')}</span>"
            f"<span>{trade_chip_html(r['trade_type'])}</span></div>"
            f"<div>{tags_html(r['signals'])}</div></div>",
            unsafe_allow_html=True,
        )
        with st.expander("التحليل"):
            explain_symbol(r)
    with st.expander("فلتر نوع الصفقة"):
        st.multiselect("نوع الصفقة", TRADE_TYPES, default=TRADE_TYPES, key=f"tt_{key}")
    st.caption("النجوم = عدد عائلات الإشارات المتفقة من 7. المربعات الملونة = الاستراتيجية التي أعطت الإشارة.")
    return filtered


def _rtl(lines, bullets=True):
    items = "".join(f"<li>{html.escape(x)}</li>" for x in lines) if bullets else "".join(f"<div>{html.escape(x)}</div>" for x in lines)
    body = f"<ul style='margin:2px 0;padding-inline-start:18px'>{items}</ul>" if bullets else items
    return f"<div dir='rtl' style='text-align:right;font-size:13px'>{body}</div>"


def explain_symbol(r):
    """The 'why was this flagged' panel - written in Arabic."""
    tf = TF_AR.get(r["timeframe"], r["timeframe"])
    st.markdown(
        f"<div dir='rtl' style='text-align:right'><b>{html.escape(r['symbol'])}</b> &middot; السعر {fmt_price(r['price'])} "
        f"&middot; فحص {tf} &middot; {DIR_AR.get(r['direction'], '')} &middot; {r['score']}/{r['max_score']} نجوم "
        f"&middot; {trade_chip_html(r['trade_type'])}</div>", unsafe_allow_html=True)
    if not r["signals"]:
        st.markdown(_rtl(["إشارات مختلطة أو غير موجودة حاليا - لا يوجد ما يُنفَّذ." if not r.get("mixed")
                          else "الأدلة الصاعدة والهابطة تلغي بعضها - لا يوجد اتجاه مسيطر."], bullets=False), unsafe_allow_html=True)
    else:
        rows = []
        for s_ in r["signals"]:
            name, detail = signal_ar(s_)
            rows.append(f"[{tag_for(s_)[0]}] {name}: {detail}")
        st.markdown(_rtl(rows), unsafe_allow_html=True)
    if r.get("against"):
        st.markdown(_rtl(["ضد الاتجاه: " + "، ".join(signal_ar(a)[0] for a in r["against"])], bullets=False), unsafe_allow_html=True)
    if r["htf"]:
        st.markdown("<div dir='rtl' style='text-align:right'><b>الفريمات الأعلى</b></div>", unsafe_allow_html=True)
        st.markdown(_rtl(htf_lines_ar(r)), unsafe_allow_html=True)
    plan = None
    if r["direction"] in ("bullish", "bearish"):
        plan = build_trade_plan({**r, "trend_bias": r["direction"]})
        side = "شراء" if plan["direction"] == "Long" else "بيع"
        st.markdown(
            f"<div dir='rtl' style='text-align:right'><b>الخطة ({side})</b> - دخول {n_(plan['entry'])} - وقف {n_(plan['stop_loss'])} - "
            f"هدف 1 {n_(plan['take_profits'][0])} / هدف 2 {n_(plan['take_profits'][1])} / هدف 3 {n_(plan['take_profits'][2])}</div>",
            unsafe_allow_html=True)
        st.markdown("<div dir='rtl' style='text-align:right'><b>السيناريوهات</b></div>", unsafe_allow_html=True)
        st.markdown(_rtl(scenarios_ar(r)), unsafe_allow_html=True)
    if r["symbol"] in TV_SYMBOL_MAP or "-" in r["symbol"]:
        try:
            svg = chart_svg(get_klines(r["symbol"], r["timeframe"], 300), r, plan)
        except Exception:
            svg = ""
        if svg:
            b64 = base64.b64encode(svg.encode('utf-8')).decode('ascii')
            st.markdown(f"<img style='width:100%;max-width:640px' src='data:image/svg+xml;base64,{b64}'/>", unsafe_allow_html=True)
            st.caption("رسم تقريبي للسيناريو: الشموع الأخيرة + مناطق الإشارات + الدخول/الوقف/الأهداف (الخط الأصفر = مسار الهدف الأول).")
        st.link_button("افتح الشارت على TradingView", tv_link(r["symbol"], r["timeframe"]))
    if r.get("errors"):
        st.caption("ملاحظات الكواشف: " + "; ".join(r["errors"]))


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
    st.caption("★ glowing = big resting order (blinks white when trades hit it). "
               "Level flash = just traded. Blue outline = size grew.")
    return bids, asks


@live_fragment
def render_trades(sym):
    st.markdown("**Time & Sales** &middot; Smart / Whale / Absorb", unsafe_allow_html=True)
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
    st.markdown("**Limit Tracking** &middot; big limit orders placed / pulled / filled", unsafe_allow_html=True)
    if book is None:
        return
    trackers = st.session_state.setdefault("limit_trackers", {})
    tracker = trackers.get(sym)
    if tracker is None or tracker.big_mult != big_order_mult:
        tracker = trackers[sym] = LimitTracker(big_mult=big_order_mult)
    tracker.update(book[0], book[1], trades)
    st.markdown(limit_events_html(tracker.events_df()), unsafe_allow_html=True)
    st.caption("Snapshot based (compares each refresh), so quick spoof-and-cancel "
               "inside one refresh is not seen. PULLED = vanished without trading.")


# ---- Tabs -------------------------------------------------------------------------
tab_workspace, tab_crypto, tab_forex, tab_metals, tab_stocks, tab_meme = st.tabs(
    ["\U0001F9E9 Workspace", "\U0001FA99 Crypto", "\U0001F4B1 Forex", "\U0001F947 Metals", "\U0001F4C8 Stocks", "\U0001F438 Meme Coins"]
)

TV_INTERVALS = {"1": "1 min", "5": "5 min", "15": "15 min", "60": "1 hour", "240": "4 hour", "D": "1 day", "W": "1 week"}
CHART_H = 225  # two stacked charts ~ the height of the DOM ladder

with tab_workspace:
    ws_lang = st.radio("Language / اللغة", ["en", "ar"], horizontal=True, key="ws_lang",
                       format_func=lambda k: {"en": "English", "ar": "العربية"}[k],
                       help="Starting language of the workspace. You can also switch inside it with the EN/ع button.")
    ws_height = st.sidebar.slider("Workspace height (px)", 500, 1400, 860, step=20)
    # The payload is rebuilt only when a new candle closes, so the Workspace page
    # (an iframe) is not re-created - and zoom/pan not reset - on every refresh.
    ws_tf = st.session_state.get("scan_tf", "1h")
    try:
        _ref = get_klines(CRYPTO_SYMBOLS[0], ws_tf, 300)
        ws_key = (ws_tf, str(_ref["time"].iloc[-2]), tuple(CRYPTO_SYMBOLS))
    except Exception:
        ws_key = None
    cached_ws = st.session_state.get("ws_payload")
    if cached_ws is None or cached_ws["key"] != ws_key or ws_key is None:
        ws_alerts, ws_scan, ws_seed = [], {}, None
        try:
            ws_results, _ws_notice = scan_crypto_group(CRYPTO_SYMBOLS, ws_tf)
            for r_ in ws_results:
                try:
                    e_ = scan_entry(r_, get_klines(r_["symbol"], ws_tf, 300))
                except Exception:
                    e_ = None
                if not e_:
                    continue
                ws_scan[r_["symbol"]] = {k: e_[k] for k in ("tfc", "tags", "zones", "plan")} | {"tf": e_["tfc"], "dir": e_["direction"]}
                if r_["score"] >= ALERT_SCORE_THRESHOLD:
                    ws_alerts.append(e_ | {"id": f"scan|{r_['symbol']}|{ws_tf}|{r_['direction']}|{r_['score']}|{ws_key[1] if ws_key else ''}"})
        except Exception:
            pass
        try:
            ws_seed = seed_from_df(CRYPTO_SYMBOLS[0], "1h", get_klines(CRYPTO_SYMBOLS[0], "1h", 300))
        except Exception:
            ws_seed = None
        cached_ws = st.session_state["ws_payload"] = {"key": ws_key, "alerts": ws_alerts, "scan": ws_scan, "seed": ws_seed}
    ws_links = [{"name": n, "url": u} for n, u in EXTERNAL_LINKS.items() if n != "Finviz Patterns"]
    ws_links.append({"name": "Finviz", "url": EXTERNAL_LINKS["Finviz Patterns"],
                     "patterns": [{"name": k, "url": FINVIZ_PATTERN_URL.format(signal=v)} for k, v in FINVIZ_PATTERNS.items()]})
    render_workspace(CRYPTO_SYMBOLS, get_latest_news("general", 15), ws_lang, height=ws_height, alerts=cached_ws["alerts"], seed=cached_ws["seed"],
                     scan=cached_ws["scan"], links=ws_links)
    st.caption("Drag a title bar to move, drag the corner to resize, - minimise, square = maximise (double-click title too). "
               "Widgets with the same # in the title bar share one symbol. Layout is remembered in your browser. "
               "Data comes straight from OKX in your browser, no refresh needed.")

with tab_crypto:
    col_watch, col_chart, col_dom, col_ts = st.columns([1.25, 2.3, 1.05, 1.4])
    with col_watch:
        st.markdown("**Scanner**")
        scan_tf = st.radio("Scan timeframe", SCAN_TFS, index=1, horizontal=True, key="scan_tf",
                           format_func=lambda t: {"1m": "1 min", "1h": "1 hour", "1d": "1 day", "1w": "1 week"}[t])
        results, notice = scan_crypto_group(CRYPTO_SYMBOLS, scan_tf)
        filtered = render_scanner(results, notice, "crypto")
    with col_chart:
        c_sym, c_top, c_bot = st.columns([1.3, 1, 1])
        pick = c_sym.selectbox("Symbol", CRYPTO_SYMBOLS, key="crypto_chart_pick")
        tf_top = c_top.selectbox("Top chart", list(TV_INTERVALS), index=3, key="tv_top",
                                 format_func=lambda k: TV_INTERVALS[k])
        tf_bot = c_bot.selectbox("Bottom chart", list(TV_INTERVALS), index=2, key="tv_bot",
                                 format_func=lambda k: TV_INTERVALS[k])
        render_tv_chart(pick, height=CHART_H, interval=tf_top, key="top")
        render_tv_chart(pick, height=CHART_H, interval=tf_bot, key="bottom")
    with col_dom:
        book = render_dom(pick)
    with col_ts:
        trades = render_trades(pick)
    st.markdown("---")
    render_limit_tracking(pick, book, trades)
    fire_alerts(filtered)


def simple_tab(key, symbols):
    col_watch, col_chart = st.columns([1.1, 3.4])
    results, notice = score_mt5_group(symbols)
    with col_watch:
        st.markdown("**Watchlist**")
        filtered = render_watchlist(results, notice, key)
    with col_chart:
        pick = st.selectbox("Chart symbol", symbols, key=f"{key}_chart_pick")
        render_tv_chart(pick)
    fire_alerts(filtered)


with tab_forex:
    simple_tab("forex", FOREX_SYMBOLS)

with tab_metals:
    simple_tab("metals", METALS_SYMBOLS)

with tab_stocks:
    simple_tab("stocks", STOCK_SYMBOLS)

with tab_meme:
    st.subheader("Meme coin / whale tracking (DEXScreener)")
    query = st.text_input("Search token (name or contract address)", value="")
    if query:
        pairs = search_dexscreener_pairs(query)
        if not pairs:
            st.info("No pairs found, or DEXScreener rate limit hit — try again shortly.")
        for p in pairs[:10]:
            with st.container(border=True):
                # "\$" so the two dollar signs are not read as a LaTeX formula
                st.markdown(
                    f"**{p.get('baseToken', {}).get('symbol', '?')}/"
                    f"{p.get('quoteToken', {}).get('symbol', '?')}** "
                    f"on {p.get('chainId', '?')} — "
                    f"Price: \\${p.get('priceUsd', '?')} — "
                    f"24h volume: \\${p.get('volume', {}).get('h24', '?')}"
                )
                st.markdown(f"[View on DEXScreener]({p.get('url', '#')})")
    else:
        st.info("Enter a token name or contract address above to search live DEXScreener pairs.")
