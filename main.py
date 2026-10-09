"""
THE FLOOR MANAGER
Orchestrates every employee module and renders the final dashboard.

Layout (top to bottom):
  title row -> scrolling news ticker -> quick-link buttons ->
  asset tabs. Each tab: [compact watchlist + trade-type filter | TradingView
  chart | (Crypto only) Depth-of-Market ladder]. Crypto also gets a smart
  time & sales feed and a limit-order tracker underneath.
The whole page re-runs every few seconds (auto-refresh) so data stays live.
"""

import html
from datetime import datetime

import pandas as pd
import streamlit as st

from config import (
    FOREX_SYMBOLS, METALS_SYMBOLS, STOCK_SYMBOLS, CRYPTO_SYMBOLS,
    EXTERNAL_LINKS, QUICK_LINK_ICONS, FINVIZ_PATTERNS, FINVIZ_PATTERN_URL,
    TRADE_TYPES, AUTO_REFRESH_SECONDS,
)
from modules.data_fetcher import get_mt5_data, get_binance_klines
from modules.scorer import score_symbol
from modules.alerts import check_and_fire_alerts, ALERT_SCORE_THRESHOLD
from modules.tv_widget import render_tv_chart
from modules.news_feed import get_latest_news, ticker_html
from modules.crypto_extras import render_order_book, render_time_and_sales, search_dexscreener_pairs
from modules.dom_panel import (
    build_ladder, ladder_html, classify_trades, trades_html,
    LimitTracker, limit_events_html, fmt_price,
)

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:  # package missing: dashboard still works, just not live
    st_autorefresh = None

st.set_page_config(
    page_title="AI Trading Desk", layout="wide", page_icon="\U0001F4CA",
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
if auto_on and st_autorefresh is not None:
    st_autorefresh(interval=refresh_secs * 1000, key="auto_refresh")
elif auto_on:
    st.sidebar.warning("streamlit-autorefresh is not installed - add it to requirements.txt.")

# ---- Header: title, news ticker, quick links --------------------------------
head_l, head_r = st.columns([3, 1])
head_l.title("AI Trading Desk")
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
@st.cache_data(ttl=10, show_spinner=False)
def cached_klines(sym: str):
    return get_binance_klines(sym, interval="1h", limit=300)


@st.cache_data(ttl=5, show_spinner=False)
def cached_book(sym: str):
    return render_order_book(sym, limit=50)


@st.cache_data(ttl=5, show_spinner=False)
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


def score_crypto_group(symbols):
    results, errors = [], []
    for sym in symbols:
        try:
            df = cached_klines(sym)
            res = score_symbol(df, timeframe_label="H1")
            res["symbol"] = sym
            results.append(res)
        except Exception as e:
            errors.append(f"{sym}: {e}")
    return results, ("; ".join(errors) if errors else "")


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
            f"<div style='font-size:11px;color:#848e9c'>{html.escape(str(r['trade_type']))}"
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


def fire_alerts(filtered):
    """Banners show on every refresh; the beep only for signals not alerted before."""
    seen = st.session_state.setdefault("alerted", set())
    strong = {(r["symbol"], r["score"]) for r in filtered if r["score"] >= ALERT_SCORE_THRESHOLD}
    is_new = bool(strong - seen)
    seen |= strong
    check_and_fire_alerts(filtered, play_sound=(play_sound and is_new))


# ---- Crypto order-flow panels ----------------------------------------------------
def render_dom(sym):
    st.markdown(f"**Depth of Market** &middot; {html.escape(sym)}", unsafe_allow_html=True)
    try:
        bids, asks = cached_book(sym)
    except Exception as e:
        st.warning(f"Order book unavailable: {e}")
        return None
    st.markdown(ladder_html(build_ladder(bids, asks, depth=12), big_mult=big_order_mult),
                unsafe_allow_html=True)
    st.caption("★ = big resting order. Bids left, asks right, one ladder.")
    return bids, asks


def render_order_flow(sym, book):
    ts_col, lt_col = st.columns(2)
    trades = None
    with ts_col:
        st.markdown("**Time & Sales** &middot; Smart / Whale prints flagged")
        try:
            trades = classify_trades(cached_trades(sym), smart_mult=smart_mult, whale_mult=smart_mult * 2.5)
            st.markdown(trades_html(trades, max_rows=20), unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Time & sales unavailable: {e}")
    with lt_col:
        st.markdown("**Limit Tracking** &middot; big limit orders placed / pulled / filled")
        if book is not None:
            trackers = st.session_state.setdefault("limit_trackers", {})
            tracker = trackers.get(sym)
            if tracker is None or tracker.big_mult != big_order_mult:
                tracker = trackers[sym] = LimitTracker(big_mult=big_order_mult)
            tracker.update(book[0], book[1], trades)
            st.markdown(limit_events_html(tracker.events_df()), unsafe_allow_html=True)
            st.caption("Snapshot based (compares each refresh), so quick spoof-and-cancel "
                       "inside one refresh is not seen. PULLED = vanished without trading.")


# ---- Tabs -------------------------------------------------------------------------
tab_crypto, tab_forex, tab_metals, tab_stocks, tab_meme = st.tabs(
    ["\U0001FA99 Crypto", "\U0001F4B1 Forex", "\U0001F947 Metals", "\U0001F4C8 Stocks", "\U0001F438 Meme Coins"]
)

with tab_crypto:
    col_watch, col_chart, col_dom = st.columns([1.1, 2.4, 1.5])
    results, notice = score_crypto_group(CRYPTO_SYMBOLS)
    with col_watch:
        st.markdown("**Watchlist**")
        filtered = render_watchlist(results, notice, "crypto")
    with col_chart:
        pick = st.selectbox("Chart symbol", CRYPTO_SYMBOLS, key="crypto_chart_pick")
        render_tv_chart(pick)
    with col_dom:
        book = render_dom(pick)
    st.markdown("---")
    render_order_flow(pick, book)
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
