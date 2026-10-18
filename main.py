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
    score_symbol, scan_symbol, fetch_tfs, SCAN_TFS, MAX_SAME_SIDE, ALL_SCAN_TFS, CONTEXT_TFS, TF_LABEL, htf_lines, scenarios,
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
from modules.i18n import L, RTL_CSS, lang as _ui_lang
from modules.site_icons import site_icon_b64
from modules.header_bar import render_header_bar
from modules.macro import api_key, fetch_macro
from modules.calendar_feed import fetch_calendar
from modules.chart_scan import (ALL_FILTERS, EMA_FILTERS, PATTERN_FILTERS, RSI_FILTERS, STRATEGY_FILTERS, SHORT as CS_SHORT,
                                features as cs_features, flag_side, match_filters, mini_chart_svg, strategy_flags)
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
    page_title="XPiX", layout="wide", page_icon=str(Path(__file__).with_name("modules") / "xpix_icon.png"),
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp { background-color: #0b0e11; color: #eaecef; }
    .stTabs [data-baseweb="tab"] { color: #eaecef; }
    .stTabs [aria-selected="true"] { color: #f0b90b; border-bottom-color: #f0b90b; }
    div[data-testid="stMetricValue"] { color: #f0b90b; }
    .block-container { padding-top: 0rem; padding-left: 0.6rem; padding-right: 0.6rem; max-width: 100%; }
    header[data-testid="stHeader"] { background: transparent; height: 1.6rem; }
    div[data-testid="stSelectbox"] { margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

# ---- Login gate (item 22): only active when APP_PASSWORD / APP_USERS is set in Secrets -----------------
from modules.auth import gate as _auth_gate
if not _auth_gate(L):
    st.stop()

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
if _ui_lang() == "ar":   # Arabic: labels, captions and alerts right-to-left (charts, tables and numbers keep their own direction)
    st.markdown(RTL_CSS, unsafe_allow_html=True)
if auto_on and st_autorefresh is not None:
    st_autorefresh(interval=refresh_secs * 1000, key="auto_refresh")
elif auto_on:
    st.sidebar.warning(L("streamlit-autorefresh is not installed - add it to requirements.txt."))

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


def _peer_frames(symbols, tf):
    """Candles (timeframe `tf`) of the correlated markets needed for SMT divergence, fetched once for the whole list."""
    from modules.smt import peers_of
    need = sorted({p for sy in symbols for p, _i in peers_of(sy)})
    if not need:
        return {}
    try:
        fr, _e = fetch_frames(need, [tf])
    except Exception:
        return {}
    return {sy: v.get(tf) for sy, v in fr.items() if v.get(tf) is not None}


def _peers_for(sym, tf, pframes):
    from modules.smt import peers_of
    return {p: (inv, pframes[p]) for p, inv in peers_of(sym) if p in pframes}


@st.cache_data(ttl=300, show_spinner=False)
def _scan_cached(symbols: tuple, tf: str):
    return scan_crypto_group(list(symbols), tf)


def scan_crypto_group(symbols, tf):
    """Multi-timeframe scan: candles for the chosen timeframe PLUS its higher
    context timeframes are fetched in parallel (cached), then scored."""
    frames, fetch_errors = fetch_frames(symbols, fetch_tfs(tf))
    pframes = _peer_frames(symbols, tf)
    results, errors = [], []
    for sym in symbols:
        try:
            results.append(scan_symbol(sym, frames[sym], tf, peers=_peers_for(sym, tf, pframes)))
        except Exception as e:
            if fetch_errors.get(sym) or "not enough" not in str(e):   # a coin with a short history is just skipped, not a "problem"
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
            f"<div>{tags_html(r['signals'], tv_link(r['symbol'], r['timeframe']))}</div></div>",
            unsafe_allow_html=True,
        )
        with st.expander("التحليل"):
            explain_symbol(r)
    with st.expander(L("Trade type filter")):
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


@st.cache_resource
def _bg_store():
    import threading
    return {"lock": threading.Lock(), "val": {}, "busy": set(), "t": {}}


def _bg(name, fn, default, ttl=300, wait=1.5):
    """Never let an outside feed hold up the page: run fn() in a thread, wait at most `wait` s, else draw with the last value
    (or `default`) and pick the fresh one up on the next run. Errors keep the last value."""
    import threading
    S = _bg_store()
    have = name in S["val"]
    if (not have or time.time() - S["t"].get(name, 0) > ttl) and name not in S["busy"]:
        with S["lock"]:
            S["busy"].add(name)

        def job():
            try:
                S["val"][name] = fn()
                S["t"][name] = time.time()
            except Exception:
                S["t"][name] = time.time() - ttl + 60   # retry in a minute
            finally:
                S["busy"].discard(name)
        th = threading.Thread(target=job, daemon=True)
        th.start()
        th.join(wait if not have else 0)
    return S["val"].get(name, default)


@st.cache_resource
def _scan_store():
    import threading
    return {"lock": threading.Lock(), "running": False, "key": None, "payload": None, "built": 0.0, "t0": time.time()}


def _scan_worker(store, ws_tf, ws_key):
    """Heavy OKX scan, run in a background thread so the page renders immediately.
    The chosen timeframe goes first and partial results are published as they arrive."""
    try:
        # just after a (re)start let the first page render before the heavy scan takes the CPU (Streamlit Cloud gives little CPU)
        wait = 45 - (time.time() - store.get("t0", 0))
        if wait > 0:
            time.sleep(wait)
        ws_alerts, ws_scan, ws_seed, ws_mini, ws_errs = [], {}, None, [], []
        syms_ = list(ws_key[2])

        def publish(done):
            store["payload"] = {"key": ws_key, "alerts": list(ws_alerts), "scan": {k_: dict(v_) for k_, v_ in ws_scan.items()}, "seed": ws_seed,
                                "mini": list(ws_mini), "errs": list(ws_errs), "built": time.time(), "loading": not done}

        try:
            ws_seed = seed_from_df(syms_[0], "1h", get_klines(syms_[0], "1h", 300))
        except Exception:
            ws_seed = None
        for tf_ in [ws_tf] + [t for t in SCAN_TFS if t != ws_tf]:
            tf_alerts = []
            try:
                ws_results, _ws_notice = scan_crypto_group(syms_, tf_)
                if _ws_notice:
                    ws_errs.append(f"{tf_}: {_ws_notice[:120]}")
            except Exception as ex_:
                ws_errs.append(f"{tf_}: {ex_}")
                publish(False)
                continue
            for r_ in ws_results:
                try:
                    df_ = get_klines(r_["symbol"], tf_, 300)
                    e_ = scan_entry(r_, df_)
                    if e_:
                        try:
                            from modules.telegram_alerts import quality as _tq
                            e_["q"], e_["qwhy"] = _tq(r_, e_)   # evidence rank 0-100 (used to pick what goes to Telegram)
                        except Exception:
                            e_["q"], e_["qwhy"] = 0, []
                        e_["spark"] = [round(float(x), 6) for x in df_["close"].iloc[-41:-1]]
                except Exception:
                    e_ = None
                if not e_:
                    continue
                if e_.get("plan"):
                    ws_mini.append({k: e_.get(k) for k in ("symbol", "direction", "tfk", "ttype", "trade", "tags", "plan", "score", "max", "tv", "spark")})
                # one entry per symbol AND chart timeframe: the chart only draws the setup that belongs to the timeframe it shows
                _slot = ws_scan.setdefault(r_["symbol"], {})
                if e_["tfc"] not in _slot or e_["score"] > _slot[e_["tfc"]]["score"]:
                    _slot[e_["tfc"]] = ({k: e_[k] for k in ("tfc", "tags", "zones", "plan", "score", "max", "tv", "trade", "spark", "ttype", "ew")}
                                        | {"tf": e_["tfc"], "dir": e_["direction"]})
                if r_["score"] >= ALERT_SCORE_THRESHOLD and (tf_ != "1m" or "1m" in SCAN_TFS) and not r_.get("against"):   # 1m only with SCAN_1M=1; no opposing signal (lab: opposed setups lost ~ -280R)
                    tf_alerts.append(e_ | {"id": f"scan|{r_['symbol']}|{tf_}|{r_['direction']}|{r_['score']}|{ws_key[1]}"})
            for side_ in ("bullish", "bearish"):   # same-direction alerts at one moment are one market-wide bet: keep the best few
                ws_alerts.extend(sorted((a for a in tf_alerts if a.get("direction") == side_), key=lambda a: -(a.get("q") or 0))[:MAX_SAME_SIDE])
            publish(False)
        publish(True)
        store["key"] = ws_key
        store["built"] = time.time()
    except Exception as ex_:
        store["payload"] = {"key": ws_key, "alerts": [], "scan": {}, "seed": None, "mini": [],
                            "errs": [f"scan crashed: {type(ex_).__name__}: {ex_}"], "built": time.time(), "loading": False}
        store["key"] = ws_key
        store["built"] = time.time()
    finally:
        store["running"] = False


@st.cache_resource
def _tg_sent():
    """symbol|side|tf -> (time, quality) of what was already sent to Telegram (shared across reruns)."""
    return {}


@st.cache_resource
def _tfstats_store():
    return {"running": False, "data": None, "t": 0.0}


def _tf_worker(store):
    try:
        from modules import backtest_tf as B
        p = B.run(CRYPTO_SYMBOLS[:6], stride=8)
        B.save(p)
        store["data"] = p
    except Exception:
        pass
    finally:
        store["running"] = False


def get_tf_stats():
    """Per-strategy best-timeframe table (walk-forward TP1 hit-rates). Cached on disk; rebuilt in the background once a day."""
    import threading
    from modules import backtest_tf as B
    store = _tfstats_store()
    d, stale = B.load(max_age=86400*8)
    if d:
        store["data"] = d
    # the walk-forward rebuild is heavy: it runs in GitHub Actions (weekly) and is only READ here, unless TF_STATS_BUILD=1
    if os.environ.get("TF_STATS_BUILD") == "1" and (stale or not store["data"]) and not store["running"] and time.time() - store["t"] > 1800:
        store["running"], store["t"] = True, time.time()
        threading.Thread(target=_tf_worker, args=(store,), daemon=True).start()
    d = store["data"]
    return {"stats": d["stats"], "best": d["best"], "min_n": d["min_n"], "built": d["built"]} if d else {}


@st.cache_data(ttl=300, show_spinner=False)
def _world_news():
    from modules.world_news import fetch_world
    return fetch_world()


def build_ws_payload(symbols=None):
    """Never blocks the page: returns the latest (possibly partial / still-loading) scan and starts a
    background refresh when the 30-minute bucket changes or an empty result is older than 60 s."""
    import threading
    ws_tf = st.session_state.get("scan_tf", "1h")
    ws_key = (ws_tf, str(int(time.time() // 1800)), tuple(symbols or CRYPTO_SYMBOLS))
    store = _scan_store()
    pl = store["payload"]
    stale_empty = bool(pl) and not pl.get("mini") and not pl.get("loading") and time.time() - pl.get("built", 0) > 60
    if store["key"] != ws_key or stale_empty:
        with store["lock"]:
            # also restart a worker that has been silent for 5 minutes (hung)
            hung = store["running"] and time.time() - store.get("started", 0) > 300
            if (not store["running"] or hung) and (store["key"] != ws_key or stale_empty):
                store["running"] = True
                store["started"] = time.time()
                threading.Thread(target=_scan_worker, args=(store, ws_tf, ws_key), daemon=True).start()
    pl = store["payload"]
    if pl is None:
        return {"key": ws_key, "alerts": [], "scan": {}, "seed": None, "mini": [],
                "errs": ["Scanning OKX in the background - results appear here in a few seconds..."],
                "built": time.time(), "loading": True}
    return pl


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


TT_OPTIONS = {"All": "الكل", "Scalp": "سكالب", "Day Trade": "داي تريد", "Swing": "سوينج", "Position": "بوزيشن"}


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
                        for t in e.get("tags", [])[:4]) or "-"
        rows.append(
            "<tr>"
            f"<td><b>{html.escape(e['symbol'])}</b> <span style='color:#848e9c'>{html.escape(str(e.get('tfk', '')))}</span></td>"
            f"<td style='color:{'#0ecb81' if long_ else '#f6465d'};font-weight:700'>{'Long' if long_ else 'Short'}</td>"
            f"<td style='color:#f0b90b'>{html.escape(str(e.get('trade', '')))}</td>"
            f"<td>{strat}</td><td>{_spark_svg(e.get('spark'), pl, long_)}</td>"
            f"<td style='color:#f6465d'>{fmt_price(pl['stop'])}</td>"
            f"<td style='color:#0ecb81'>{fmt_price(pl['tps'][0])}</td>"
            f"<td>{_strength_bar(pct)}</td>"
            f"<td><a href='{html.escape(e.get('tv', '#'), quote=True)}' target='_blank' rel='noopener noreferrer'>TV</a></td></tr>"
        )
        if len(rows) >= n:
            break
    if not rows:
        return "<div class='mini' style='padding:6px;color:#848e9c;font-size:11px'>لا توجد صفقات جاهزة الآن</div>"
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


@st.cache_data(ttl=900, show_spinner=False)
def _calendar_rows():
    return fetch_calendar()


from modules import asset_classes as _AC   # the dropdown options (also used by render_header)


def render_header():
    """ONE header row: XPiX strip (logo | resources menu | news | next event | Cairo + New York clocks | world map) | page tabs |
    language | focus. Focus mode folds the strip away so the Workspace gets the whole screen. Returns the container for the page tabs."""
    focus = bool(st.session_state.get("focus_ws"))
    with st.container(key="hdr"):
        h_main, h_nav, h_lang, h_foc = st.columns([5.6, 4.1, 0.75, 0.3], vertical_alignment="center")
    with h_main:
        if focus:   # folded: only a small mark
            st.markdown("<div class='xpix-mini'><b>X</b><i>Pi</i><b>X</b></div>", unsafe_allow_html=True)
        else:
            links = []
            for name, url in EXTERNAL_LINKS.items():
                dom = url.split("//", 1)[-1].split("/", 1)[0].replace("www.", "")
                if name == "Finviz Patterns":
                    links.append({"name": "Finviz", "url": url, "icon": site_icon_b64_uri("finviz.com"),
                                  "patterns": [{"name": k, "url": FINVIZ_PATTERN_URL.format(signal=v)} for k, v in FINVIZ_PATTERNS.items()]})
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
            render_header_bar(_logo_data_uri(), links, news, cal=cal, ar=_ui_lang() == "ar")
    with h_lang:
        st.radio(L("Language"), ["en", "ar"], horizontal=True, key="ws_lang", label_visibility="collapsed",
                 format_func=lambda k: {"en": "EN", "ar": "ع"}[k])
    with h_foc:
        if st.button("⤡" if focus else "⤢", key="focus_btn", help=L("Fold the header away: the Workspace gets the whole screen (click again to bring it back).")):
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


@st.cache_data(ttl=900, show_spinner=False)
def _cmc_data():
    from modules.cmc import fetch_cmc
    return fetch_cmc()


@st.cache_data(ttl=21600, show_spinner=False)
def _stock_fund(tickers: tuple):
    from modules.stock_fund import fetch_stock_fund
    return fetch_stock_fund(tickers)


def _stock_tickers():
    if asset_cls == "Stocks":
        t = tuple(s.split("-")[0] for s in ACTIVE_SYMBOLS[:10] if s.split("-")[0].isalpha())
        if t:
            return t
    return ()


@st.cache_data(ttl=21600, show_spinner=False)
def _macro_fund():
    from modules.macro_fund import fetch_macro_fund
    return fetch_macro_fund()


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


# ---- One asset-class dropdown for scanner / ready trades / watchlist ---------------
from modules.asset_classes import CLASSES as ASSET_CLASSES, MARKET_TYPES, MEME_BASES, class_symbols
asset_cls = st.session_state.get("asset_cls", "Crypto")      # the two selectors live at the top of the Chart Scanner tab
market_type = st.session_state.get("market_type", "Spot")
SCAN_SYMBOLS, _ac_msg = class_symbols(asset_cls, CRYPTO_SYMBOLS, mtype=MARKET_TYPES.get(market_type, "SPOT"))
if _ac_msg:
    SCAN_SYMBOLS = list(CRYPTO_SYMBOLS)
ACTIVE_SYMBOLS = list(SCAN_SYMBOLS)   # may contain "Y:" (Yahoo) symbols: the Workspace gets their candles embedded in the page (no live book / tape for them)


def render_universe_controls():
    """Asset class / Market for the Chart Scanner (moved here from the top row: the Workspace watchlist has its own selectors)."""
    _u1, _u2, _u3 = st.columns([1.3, 1.0, 6])
    _u1.selectbox(L("Asset class"), _AC.CLASSES, key="asset_cls", format_func=L, help=L("Asset class for the Chart Scanner (and the Workspace scan / ready trades)."))
    _u2.selectbox(L("Market"), list(_AC.MARKET_TYPES), key="market_type", format_func=L, help=L("Spot / Perpetual swap / dated Futures (OKX)."))
    if st.session_state.get("asset_cls", "Crypto") != "Crypto":
        st.query_params["cls"] = st.session_state["asset_cls"]
    elif "cls" in st.query_params:
        del st.query_params["cls"]
    if _ac_msg:
        st.warning(_ac_msg + " - showing Crypto instead.")


# ---- Tabs -------------------------------------------------------------------------
# Page selector instead of st.tabs: st.tabs runs EVERY tab's code on every run (~1100 candle downloads + scans per run, which got
# the app CPU-throttled on Streamlit Cloud). Now only the open page runs. The choice is kept in the URL (?page=) and the session.
# 2026-10-18 (owner): Crypto / Forex / Metals / Stocks / Meme pages removed (the Workspace covers them: watchlist classes, widgets);
# new sections that serve the goal: the honest Lab, the Playbook, and two "soon" sections (AI analyst, alerts & bots).
_PAGES = ["Workspace", "Scanner", "Lab", "Playbook", "Performance", "AI Analyst", "Alerts"]   # the last two = planned (their pages say so)
if "page" not in st.session_state:
    try:
        st.session_state["page"] = min(max(int(st.query_params.get("page", 0)), 0), len(_PAGES) - 1)
    except (TypeError, ValueError):
        st.session_state["page"] = 0
with (NAV_BOX if NAV_BOX is not None else st.container()):
    PAGE = st.radio(L("Page"), list(range(len(_PAGES))), format_func=lambda i: L(_PAGES[i]), horizontal=True, key="page", label_visibility="collapsed")
if str(st.query_params.get("page", "")) != str(PAGE):
    st.query_params["page"] = str(PAGE)
_focus = bool(st.session_state.get("focus_ws"))
try:   # phones: the Workspace frame = about one screen (its widgets scroll inside it); header row wraps into two lines
    _IS_MOBILE = any(k in (st.context.headers.get("User-Agent", "") or "") for k in ("Mobi", "Android", "iPhone"))
except Exception:
    _IS_MOBILE = False
st.markdown(f"""<style>.st-key-page [role="radiogroup"]{{gap:2px 16px;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}}
.st-key-page label{{padding:2px 2px 3px;margin:0;white-space:nowrap}} .st-key-page [data-testid="stRadioOption"] p{{font-size:11px;letter-spacing:.14em;text-transform:uppercase}}
.block-container{{padding-top:{'.35rem' if _focus else '.7rem'}!important}} [data-testid="stHeader"]{{background:transparent;height:2.2rem}}
.st-key-hdr{{padding:0 2.8rem 0 2.6rem;border-bottom:1px solid #1c232b;margin-bottom:2px}}
.xpix-mini{{font:800 18px/1 sans-serif;letter-spacing:.06em;color:#d7dce2}} .xpix-mini i{{font-style:normal;color:{ui_accent}}}
.st-key-focus_btn button{{padding:0 6px;min-height:28px;border:1px solid #1c232b;background:transparent}}
.st-key-ws_lang [role="radiogroup"]{{flex-wrap:nowrap;gap:8px}}
@media (max-width:640px){{.st-key-hdr{{padding:0 .2rem 0 2.4rem}} .st-key-hdr [data-testid="stHorizontalBlock"]{{flex-wrap:wrap!important;gap:4px!important}}
  .st-key-hdr [data-testid="stColumn"]:nth-child(1),.st-key-hdr [data-testid="stColumn"]:nth-child(2){{flex:1 1 100%!important;width:100%!important;min-width:100%!important}}
  .st-key-hdr [data-testid="stColumn"]:nth-child(3),.st-key-hdr [data-testid="stColumn"]:nth-child(4){{flex:0 0 auto!important;width:auto!important;min-width:0!important}}
  .block-container{{padding-left:.4rem!important;padding-right:.4rem!important}} .st-key-page [data-testid="stRadioOption"] p{{font-size:12px}}}} .st-key-ws_lang p{{font-size:11px}}
[data-testid="stExpander"] summary{{background:#0b0f14!important;color:#e6e9ee!important}} [data-testid="stExpander"] summary p{{color:#e6e9ee!important}} .st-key-page [data-testid="stRadioOption"]>div>div:first-child:not([data-testid]){{display:none!important}} .st-key-page [data-testid="stRadioOption"] p{{color:#c3c9d1;opacity:1}} .st-key-page [data-testid="stRadioOption"]{{opacity:1}}
.st-key-page label:has(input:checked){{border-bottom:2px solid {ui_accent}}} .st-key-page label:has(input:checked) p{{color:{ui_accent};font-weight:600}}</style>""",
            unsafe_allow_html=True)

def _md_sections(path):
    """{heading: body} of the '## ' sections of a Markdown file in the repo (empty if missing)."""
    try:
        txt = Path(path).read_text(encoding="utf-8")
    except Exception:
        return {}
    out, cur = {}, None
    for line in txt.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip(); out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def render_lab_page():
    """Strategy lab: weekly walk-forward on real candles (GitHub Actions), random baseline; shows what passed the evidence bar."""
    st.subheader(L("Strategy lab - what the numbers say"))
    st.caption(L("Real OKX / Hyperliquid candles, run weekly by GitHub Actions, every result against a random-direction baseline. "
                 "Evidence bar: n >= 100 and t > 3. Under 30 trades = not evidence. No costs, so real results are worse."))
    lab, flt = _md_sections("STRATEGY_LAB.md"), _md_sections("STRATEGIES.md")
    if not lab:
        st.info(L("No lab results yet - they appear after the first weekly run."))
        return
    first = [k for k in lab if k.startswith("Gann zone trades OUT OF SAMPLE")] + [k for k in lab if k.startswith("Gann time cycles")] + \
            [k for k in lab if k.startswith("Gann astro")] + [k for k in lab if k.startswith("Trend filter")]
    filt = [k for k in flt if k.startswith("Filter on/off backtest")]
    for k in first[:1]:
        with st.expander(k, expanded=True):
            st.markdown(lab[k])
    for k in filt:
        with st.expander(L("Group-A filters ON vs OFF (item 1)"), expanded=True):
            st.markdown(flt[k])
    for k in first[1:]:
        with st.expander(k, expanded=False):
            st.markdown(lab[k])
    rest = [k for k in lab if k not in first]
    if rest:
        pick = st.selectbox(L("More tables"), rest, key="lab_more")
        st.markdown(lab[pick])


def render_playbook_page():
    """The playbook: which schools / rules are used, how quality is kept honest (STRATEGIES.md)."""
    st.subheader(L("Playbook"))
    pb = _md_sections("STRATEGIES.md")
    if not pb:
        st.info(L("STRATEGIES.md not found."))
        return
    keys = list(pb)
    top = [k for k in keys if k.startswith("Schools ranked")] + [k for k in keys if k.startswith("Operating model")] + [k for k in keys if k.startswith("Lab results")]
    for i, k in enumerate(top):
        with st.expander(k, expanded=i == 0):
            st.markdown(pb[k])
    pick = st.selectbox(L("Section"), [k for k in keys if k not in top], key="pb_more")
    if pick:
        st.markdown(pb[pick])


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

@st.cache_data(ttl=300, show_spinner=False)
def _chart_scan_data(symbols: tuple, tf: str, look: int = 3):
    """-> {symbol: {'rsi', 'flags', 'svg', 'price'}} for one timeframe (cached 60 s)."""
    frames, _errs = fetch_frames(list(symbols), [tf], limit=260)
    pfr = _peer_frames(symbols, tf)
    out = {}
    for sym in symbols:
        df = (frames.get(sym) or {}).get(tf)
        if df is None or len(df) < 60:
            continue
        f = cs_features(df, look)
        sflags, ssides = strategy_flags(df, _peers_for(sym, tf, pfr))
        out[sym] = {"rsi": f["rsi"], "flags": sorted(f["flags"] | sflags), "sides": {k: sorted(v) for k, v in ssides.items()}, "svg": mini_chart_svg(df, lines=f.get("lines")), "price": float(df["close"].iloc[-1])}
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


def render_chart_scanner():
    st.markdown("""<style>
.st-key-csf{background:#12161b;border:1px solid #2b3139;border-radius:6px;padding:6px 8px 2px}
.st-key-csf label p,.st-key-csf [data-testid="stWidgetLabel"] p{font-size:10px!important;color:#848e9c!important;margin:0 0 1px 0!important;text-transform:uppercase;letter-spacing:.03em}
.st-key-csf [data-baseweb="select"]>div,.st-key-csf input{min-height:26px!important;font-size:11px!important}
.st-key-csf [data-baseweb="select"] span,.st-key-csf [data-baseweb="tag"]{font-size:11px!important}
.st-key-csf [data-testid="stHorizontalBlock"]{gap:.4rem!important}
.st-key-csf [data-testid="stVerticalBlock"]{gap:.25rem!important}
.st-key-csf [data-testid="stNumberInputContainer"]{min-height:26px!important}
.st-key-csf [data-baseweb="select"] [data-baseweb="tag"]{height:18px!important;margin:1px!important}
.st-key-csf [data-baseweb="select"]>div{max-height:56px;overflow-y:auto}
</style>""", unsafe_allow_html=True)
    qp = st.query_params
    if "cs_strat" not in st.session_state and qp.get("strat"):   # remembered selection (URL param survives reloads / bookmarks)
        st.session_state["cs_strat"] = [k for k in qp["strat"].split(",") if k in STRATEGY_FILTERS]
    rmap = {"above": "above", "below": "below", "crossed above": "xup", "crossed below": "xdn"}
    rels = ["—", "above", "below", "crossed above", "crossed below"]
    with st.expander(L("Filters"), expanded=True), st.container(key="csf"):   # collapse the whole block to give the charts room
        r1 = st.columns([1, 0.7, 1, 1, 1.3, 1.1])
        tf = r1[0].selectbox(L("Timeframe"), ["1m", "5m", "13m", "15m", "30m", "1h", "2h", "3h", "4h", "6h", "7h", "8h", "12h", "1d", "3d", "1w", "1mo"], index=5, key="cs_tf")
        n_show = r1[1].number_input(L("Charts"), min_value=1, max_value=30, value=10, step=1, key="cs_n")
        side_pick = r1[2].selectbox(L("Side"), ["Both", "Buy only", "Sell only"], key="cs_side", format_func=L)
        mode = r1[3].selectbox(L("Match"), ["All selected", "Any selected"], key="cs_mode", format_func=L)
        look = r1[4].selectbox(L("Cross window"), [1, 3, 5, 10], index=1, key="cs_look", format_func=lambda n: f"last {n} candle" + ("s" if n > 1 else ""))
        stack = r1[5].selectbox(L("Trend stack"), ["—", "Bullish (px>9>20>50)", "Bearish (px<9<20<50)", "Above all EMAs", "Below all EMAs"], key="cs_stack", format_func=L)
        r2 = st.columns([1.1, 0.6, 1.1, 0.8, 1.3, 1.3])
        rel_px = r2[0].selectbox(L("Price vs EMA"), rels, key="cs_px_rel", format_func=L)
        len_px = r2[1].selectbox("EMA", [9, 20, 50, 200], index=1, key="cs_px_len")
        rel_ma = r2[2].selectbox(L("EMA vs EMA"), rels, key="cs_ma_rel", format_func=L)
        pair = r2[3].selectbox(L("Pair"), ["9/20", "20/50", "50/200"], index=1, key="cs_ma_pair")
        sel_rsi = r2[4].multiselect("RSI", list(RSI_FILTERS), format_func=RSI_FILTERS.get, key="cs_rsi")
        sel_pat = r2[5].multiselect(L("Patterns"), list(PATTERN_FILTERS), format_func=PATTERN_FILTERS.get, key="cs_pat")
        sel_strat = st.multiselect(L("Strategies / signals (Elliott, SMC, ICT, Harmonic, VWAP ...)"), list(STRATEGY_FILTERS),
                                   format_func=lambda k: STRATEGY_FILTERS[k][0], key="cs_strat")
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
    sel = sel_rsi + sel_ema + sel_pat + sel_strat
    try:
        data = _chart_scan_data(tuple(SCAN_SYMBOLS), tf, look)
    except Exception as e:
        st.warning(f"Could not load candles: {e}")
        return
    want = {"Buy only": "buy", "Sell only": "sell"}.get(side_pick)
    def ok(d):
        return match_filters(d, sel, want, mode == "Any selected")
    shown = [(sym, d) for sym, d in data.items() if ok(d)]
    st.caption(f"{len(shown)} of {len(data)} symbols match" + (f" - showing the first {int(n_show)}" if len(shown) > n_show else "")
               + "  |  lines: EMA 9 (yellow), 21 (blue), 50 (purple), VWAP (white dashed)")
    if not shown:
        st.info(L("No symbols match the selected conditions right now."))
        return
    shown = shown[:int(n_show)]
    per_row = 5
    for r0 in range(0, len(shown), per_row):
        cols = st.columns(per_row)
        for col, (sym, d) in zip(cols, shown[r0:r0 + per_row]):
            with col:
                badges = "".join(f"<span style='background:#2b3139;border-radius:3px;padding:0 4px;margin-right:2px;font-size:10px'>"
                                 f"{html.escape(CS_SHORT.get(k, k))}</span>" for k in d["flags"] if k in ALL_FILTERS and (k in sel or not k.startswith(("px_above", "px_below", "ma_above", "ma_below"))))
                rsi_v = d["rsi"]
                rcol = "#f6465d" if rsi_v is not None and rsi_v >= 70 else "#0ecb81" if rsi_v is not None and rsi_v <= 30 else "#848e9c"
                st.markdown(
                    f"<div style='font-size:12px'><a href='{html.escape(tv_link(sym, tf), quote=True)}' target='_blank' rel='noopener noreferrer' "
                    f"style='color:#eaecef;font-weight:700;text-decoration:none'>{html.escape(sym)}</a> "
                    f"<span style='color:#848e9c'>{fmt_price(d['price'])}</span> "
                    f"<span style='color:{rcol}'>RSI {rsi_v:.0f}</span></div>"
                    f"<img style='width:100%;border:1px solid #2b3139;border-radius:4px' src='{d['svg']}'/>"
                    f"<div style='min-height:18px;margin-top:2px'>{badges}</div>", unsafe_allow_html=True)
                if st.checkbox("التحليل", key=f"cs_an_{sym}_{tf}", help=L("Plain-language Arabic analysis of this setup (same as the Crypto tab)")):
                    try:
                        r_ = _cs_result(sym, tf)
                        if r_:
                            explain_symbol(r_)
                    except Exception as e_:
                        st.caption(f"Analysis unavailable: {e_}")


if PAGE == 0:   # workspace
    _ws_stat = st.empty()   # loading steps shown while the server builds the Workspace (cleared once it is sent)
    try:
        _ws_stat.caption("⏳ Workspace: scan state...")
        ws_lang = st.session_state.get("ws_lang", "en")
        cached_ws = build_ws_payload(ACTIVE_SYMBOLS)
        if tg_on and not cached_ws.get("loading"):
            from modules import telegram_alerts as _tga
            _n, _err = _tga.dispatch(cached_ws.get("alerts") or [], _tg_sent(), int(tg_top), int(tg_min))
            if _err:
                st.sidebar.warning("Telegram: " + _err)
            elif _n:
                st.sidebar.caption(f"Telegram: sent {_n} alert(s).")
        _ws_stat.caption("⏳ Workspace: news / calendar / macro feeds...")
        world_items, world_errs = _bg("world", _world_news, ([], ["world news loading..."]))
        ws_links = [{"name": n, "url": u} for n, u in EXTERNAL_LINKS.items() if n != "Finviz Patterns"]
        ws_links.append({"name": "Finviz", "url": EXTERNAL_LINKS["Finviz Patterns"],
                         "patterns": [{"name": k, "url": FINVIZ_PATTERN_URL.format(signal=v)} for k, v in FINVIZ_PATTERNS.items()]})
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
                         ready=cached_ws.get("mini", []), scanning=bool(cached_ws.get("loading")), cmc=_cmc, macrof=_mac, stockf=_stk, world_errs=world_errs)
        _ws_stat.empty()
        if world_errs:
            st.caption("World Monitor feeds unavailable: " + ", ".join(world_errs[:4]))
        if cached_ws.get("errs"):
            st.caption("Scan problems: " + " | ".join(cached_ws["errs"][:3]))
        st.caption(L("Drag a title bar to move, drag the corner to resize, - minimise, square = maximise (double-click title too). "
                   "Widgets with the same # in the title bar share one symbol. Layout is remembered in your browser. "
                   "Data comes straight from OKX in your browser, no refresh needed."))
    except Exception as _e:
        st.error(f"Workspace error: {type(_e).__name__}: {_e}")

# the Chart Scanner scans the whole universe synchronously (can take minutes on a cold server): it runs AFTER the Workspace,
# otherwise the first tab stays blank until the scan finishes (Streamlit renders in code order, not tab order)
if PAGE == 1:   # cscan
    try:
        render_universe_controls()
        render_chart_scanner()
    except Exception as _e:
        st.error(f"Chart Scanner error: {type(_e).__name__}: {_e}")

# (removed 2026-10-17) a "sleep 5 s + st.rerun()" loop used to run here while the background scan was busy: every rerun rebuilt and
# re-sent the Workspace, so its frame reloaded every 5 s (blank page) and the CPU never rested (the app got throttled).
# The Workspace shows "scanning..." and picks the results up on the next normal run.


if PAGE == 2:   # lab
    render_lab_page()

if PAGE == 3:   # playbook
    render_playbook_page()

if PAGE in (5, 6):   # soon
    render_soon_page(PAGE)

if PAGE == 4:   # perf
    st.subheader(L("Performance report (QuantStats)"))
    st.caption(L("The Workspace journal lives in your browser, so export it first: Journal widget > CSV button. Upload that file here. "
                 "Returns = R x the % of the account you risk per trade. Evidence from the dashboard's own signals only - not a proven edge."))
    import pandas as _pd
    from modules.perf_report import perf_stats, quantstats_html, returns_from_trades
    _up = st.file_uploader(L("Journal CSV (columns: time, r)"), type=["csv"], key="perf_csv")
    _risk = st.number_input(L("Risk per trade (% of account)"), min_value=0.1, max_value=10.0, value=1.0, step=0.1, key="perf_risk")
    if _up is not None:
        try:
            _ret = returns_from_trades(_pd.read_csv(_up), float(_risk))
            if len(_ret) < 5:
                st.warning(L("Need at least 5 closed trades for meaningful statistics."))
            else:
                _st = perf_stats(_ret)
                _c = st.columns(4)
                _c[0].metric(L("Trades"), _st["n"]); _c[1].metric(L("Total return"), f"{_st['total_return']*100:.1f}%")
                _c[2].metric(L("Max drawdown"), f"{_st['max_drawdown']*100:.1f}%"); _c[3].metric(L("Win rate"), f"{_st['win_rate']*100:.0f}%")
                _c = st.columns(3)
                _c[0].metric("Sharpe", f"{_st['sharpe']:.2f}"); _c[1].metric("Sortino", f"{_st['sortino']:.2f}"); _c[2].metric(L("Stats source"), _st["source"])
                st.line_chart((1 + _ret).cumprod().rename("equity"))
                import streamlit.components.v1 as _components
                _html = quantstats_html(_ret)
                if _html:
                    _components.html(_html, height=900, scrolling=True)
                else:
                    st.info(L("QuantStats is not installed here, so only the built-in statistics are shown."))
        except Exception as _e:
            st.error(f"Could not read the file: {type(_e).__name__}: {_e}")
