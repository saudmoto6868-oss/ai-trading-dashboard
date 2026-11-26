"""Workspace page (index 0). Moved from main.py (maintenance plan M7)."""

import streamlit as st

from config import EXTERNAL_LINKS, FINVIZ_PATTERNS, FINVIZ_PATTERN_URL
from modules.i18n import L
from modules.page_kit import rt
from modules.page_bg import _bg, _tg_sent, get_tf_stats, _ws_universe, _dayplan_watch, _dayplan_events, _smt_events, build_ws_payload
from modules.context_feeds import calendar_rows as _calendar_rows
from modules.asset_classes import MEME_BASES
from modules.news_feed import get_latest_news
from modules.workspace import render_workspace
from modules.context_feeds import cmc_data as _cmc_data, stock_fund as _stock_fund, macro_fund as _macro_fund


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


def _stock_tickers():
    if rt().asset_cls == "Stocks":
        t = tuple(s.split("-")[0] for s in rt().ACTIVE_SYMBOLS[:10] if s.split("-")[0].isalpha())
        if t:
            return t
    return ()


def _page_0():   # workspace
    _ws_stat = st.empty()   # loading steps shown while the server builds the Workspace (cleared once it is sent)
    try:
        _ws_stat.caption("⏳ Workspace: scan state...")
        ws_lang = st.session_state.get("ws_lang", "en")
        cached_ws = build_ws_payload(_ws_universe(rt().ACTIVE_SYMBOLS))
        if rt().tg_on and not cached_ws.get("loading"):
            from modules import telegram_alerts as _tga
            _n, _err = _tga.dispatch(cached_ws.get("alerts") or [], _tg_sent(), int(rt().tg_top), int(rt().tg_min))
            try:   # day plan (timeframe confluence): the best new plans, one message each (not repeated for 4 hours)
                from modules import day_plan as _DP
                _tga_n2, _tga_e2 = _DP.dispatch(_dayplan_events(), _tg_sent(), _tga.send, top_n=int(rt().tg_top))
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
        if any(x.startswith("Y:") for x in rt().ACTIVE_SYMBOLS):
            def _yf_job(syms=tuple(rt().ACTIVE_SYMBOLS)):
                from modules.yahoo_feed import embed as _yf_embed
                return _yf_embed(syms)
            _yf = _bg("yf|" + ",".join(rt().ACTIVE_SYMBOLS), _yf_job, {}, ttl=120)
        _cal = _bg("cal", _calendar_rows, [])
        _news = _bg("news", lambda: get_latest_news("general", 15), [])
        _cmc = _bg("cmc", _cmc_data, None)
        _mac = _bg("macro", _macro_fund, None)
        _stk_t = _stock_tickers()
        _stk = _bg("stocks|" + ",".join(_stk_t), lambda: _stock_fund(_stk_t), None)
        _ws_stat.caption("⏳ Workspace: building the page...")
        _tfs = get_tf_stats()
        render_workspace(rt().ACTIVE_SYMBOLS, _news, ws_lang, yf=_yf, cal=_cal, height=min(rt().ws_height, 860) if rt()._IS_MOBILE else rt().ws_height, alerts=cached_ws["alerts"], seed=cached_ws["seed"],
                         scan=cached_ws["scan"], links=ws_links, asset_cls=rt().asset_cls, meme=[b + "-USDT" for b in MEME_BASES], world=world_items, tfstats=_tfs,
                         ready=cached_ws.get("mini", []), smt=_smt_chips(ws_lang), scanning=bool(cached_ws.get("loading")), cmc=_cmc, macrof=_mac, stockf=_stk, world_errs=world_errs,
                         ui_theme="" if rt().UI_THEME == "classic" else rt().UI_THEME, ui_bg=rt().UI_BG, ui_mat=rt().UI_MAT)
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
