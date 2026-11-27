"""Radar filter bar (asset class, market, timeframe, detectors...). Split from page_radar.py (M7)."""
import os

import streamlit as st

from modules.i18n import L, lang as _ui_lang
from modules.page_kit import kit_css, rt
from modules import asset_classes as _AC
from modules.chart_scan import (MOVE_FILTERS, PATTERN_FILTERS, RSI_FILTERS, STRATEGY_FILTERS)
from modules.page_radar_data import _CS_TFS, _CX


def render_universe_controls(_u1, _u2, _u3):
    """Asset class / Market / Universe size: drawn in the ONE Radar filter line (the caller passes the three columns)."""
    _u1.selectbox(L("Asset class"), _AC.CLASSES, key="asset_cls", format_func=L, help=L("Asset class for the Chart Scanner (and the Workspace scan / ready trades)."))
    _u2.selectbox(L("Market"), list(_AC.MARKET_TYPES), key="market_type", format_func=L, help=L("Spot / Perpetual swap / dated Futures (OKX)."))
    _u3.number_input(L("Universe size"), min_value=10, max_value=150, value=24, step=2, key="uni_n", help=L("How many symbols the Radar scans (biggest 24h volume first). More symbols = a longer first load."))
    if st.session_state.get("asset_cls", "Crypto") != "Crypto":
        st.query_params["cls"] = st.session_state["asset_cls"]
    elif "cls" in st.query_params:
        del st.query_params["cls"]
    if rt()._ac_msg:
        st.warning(rt()._ac_msg + " - showing Crypto instead.")


def _strat_name(k):
    """Detector / strategy filter name in the page language (Arabic short names from chart_explain.FLAG_AR)."""
    from modules.chart_scan import STRATEGY_FILTERS as _SF
    return _CX.FLAG_AR.get(k, _SF[k][0]) if _ui_lang() == "ar" and k in _CX.FLAG_AR else _SF[k][0]


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
    _store = _decl("xpix_preset_store", path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modules", "preset_store"))
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
