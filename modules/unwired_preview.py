"""Preview (owner 2026-11-21): everything that is BUILT but was not reachable from any page, in one place so the owner can look at
each item and decide: keep (wire it properly), change, or delete. Read-only: nothing here sends orders or writes files.

Sections:
  * pages built as standalone iframes (Edge Map, Robustness Matrix, Execution Cycle, Veles Robustness Lab) - the first three
    carry their own "example data" banner; their numbers are demo numbers, not results.
  * small tools that only had tests: signal comparison (real lab file), Wyckoff phases (one symbol, real candles on request),
    cross-sectional momentum (a few symbols, real candles on request), Gann square of nine (pure math).
  * libraries with no screen (TIA risk engine parts, zone collector): name + what the module says it does.
"""
from __future__ import annotations

import importlib
from pathlib import Path

_IFRAMES = [("Edge Map", "quant_edgemap"), ("Robustness Matrix", "quant_robustness"),
            ("Execution Cycle", "quant_execution"), ("Veles Robustness Lab", "veles_robustness")]
_LIBS = ["tia_knowledge_router", "tia_market_risk_context", "tia_options_risk_context", "tia_risk_ledger",
         "tia_risk_reconciliation", "tia_risk_shadow", "tia_unified_market_risk", "zone_collector"]
_MOM_DEFAULT = "BTC-USDT, ETH-USDT, SOL-USDT, XRP-USDT, BNB-USDT, DOGE-USDT"


def _doc(mod: str) -> str:
    """First paragraph of the module docstring, read from the file (no import: some libraries pull heavy deps)."""
    import ast
    src = (Path(__file__).with_name(mod + ".py")).read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(src)) or ""
    return doc.split("\n\n")[0].replace("\n", " ").strip()


def _signal_compare(st, L):
    from modules import signal_compare as SC
    try:
        rows = SC.compare(SC.load())
    except Exception as e:
        st.info(L("No lab file yet") + f" ({type(e).__name__})")
        return
    st.caption(L("Every detector from the last lab run on real candles (data/strategy_lab.json), pooled rows only."))
    st.dataframe([{k: r[k] for k in ("key", "school", "n", "win", "avgR", "net", "t", "is_avgR", "oos_avgR", "lab_edge", "owner_pass")}
                  for r in rows], hide_index=True, width="stretch")
    passed = [r["key"] for r in rows if r["owner_pass"]]
    st.caption(f"{len(rows)} detectors · owner bar passed by: {', '.join(passed) or 'none'}")


def _wyckoff(st, L):
    from modules import wyckoff_phases as W
    c1, c2 = st.columns([3, 1])
    sym = c1.text_input(L("Symbol"), "BTC-USDT", key="pv_wy_sym")
    tf = c2.selectbox(L("Timeframe"), ["1d", "4h", "1h"], key="pv_wy_tf")
    if st.button(L("Read the phase"), key="pv_wy_go"):
        try:
            from modules.market_cache import get_klines
            r = W.analyze(get_klines(sym.strip(), tf, 300))
        except Exception as e:
            st.error(f"{type(e).__name__}: {e}")
            return
        if not r:
            st.info(L("No accumulation structure on these candles."))
        else:
            st.write(f"Phase **{r['phase']}** · range {r['S']:.6g} - {r['R']:.6g}")
            st.dataframe([{"event": n, "bars ago": i, "price": p} for n, i, p in r["events"]], hide_index=True, width="stretch")
    st.caption(L("Textbook labelling, not a signal and not validated."))


def _momentum(st, L):
    from modules import momentum as M
    syms = st.text_input(L("Symbols (comma separated)"), _MOM_DEFAULT, key="pv_mo_syms")
    if st.button(L("Rank"), key="pv_mo_go"):
        uni = {s.strip(): s.strip() for s in syms.split(",") if s.strip()}
        closes, errs = M.fetch_closes(uni)
        for e in errs:
            st.warning(e)
        st.dataframe(M.rank(closes), hide_index=True, width="stretch")
    st.caption(L("12-1 month relative strength ranking on daily closes."))


def _gann(st, L):
    from modules import gann_geom as G
    p = st.number_input(L("Pivot price"), min_value=0.0001, value=100.0, key="pv_gn_p")
    st.dataframe([{"level": round(x, 6)} for x in G.square_of_nine_levels(p)], hide_index=True, width="stretch")
    st.caption(L("Square of nine: (sqrt(P) ± 0.25 k)², pure math, no data."))


_TOOLS = {"Signal comparison": _signal_compare, "Wyckoff phases": _wyckoff, "Momentum ranking": _momentum, "Gann square of nine": _gann}


def render(st, L=lambda s: s) -> None:
    st.markdown("### " + L("Preview: built but not shown"))
    st.info(L("Everything here was built and tested but had no page. Look at each one and decide: keep, change or delete."))
    pick = st.segmented_control(L("Preview"), [n for n, _ in _IFRAMES] + list(_TOOLS) + ["Libraries (no screen)"],
                                default=_IFRAMES[0][0], format_func=L, key="pv_pick", label_visibility="collapsed")
    pick = pick or _IFRAMES[0][0]
    mods = dict(_IFRAMES)
    if pick in mods:
        st.caption(f"modules/{mods[pick]}.py")
        importlib.import_module("modules." + mods[pick]).render()
    elif pick in _TOOLS:
        _TOOLS[pick](st, L)
    else:
        st.dataframe([{"module": f"modules/{m}.py", "what it says it does": _doc(m)} for m in _LIBS], hide_index=True, width="stretch")
        st.caption(L("Each has its own test in tests/. None is called by the app."))
