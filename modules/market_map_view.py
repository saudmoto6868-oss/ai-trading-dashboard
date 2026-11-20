"""Market map (خانة الأسواق): Hyperliquid TradFi change tiles, breadth and strength by class.

Moved out of main.py (2026-11-17) so Technical Office / Spot and TIA's Markets tab render the same view.
"""
import streamlit as st

from modules.i18n import L


def render_market_map():
    """Market map of the Hyperliquid TradFi markets (xyz): change tiles, breadth, and strength by asset class."""
    from modules.hl_feed import markets as _hl_markets
    from modules.market_map import board, breadth, by_class
    try:
        rows = _hl_markets()
    except Exception as e:
        st.warning(L("Market map: Hyperliquid did not answer") + f" ({type(e).__name__})")
        return
    df = board(rows)
    if df.empty:
        st.caption(L("Market map: no markets with a reference price right now."))
        return
    from modules.market_map import apply_filters as _mm_filter
    _all = df
    fc = st.columns([2.4, 0.8, 1, 1, 1.2, 1.2])
    _cls_opts = sorted(_all["cls"].unique())
    sel_cls = fc[0].pills(L("Class"), _cls_opts, selection_mode="multi", key="hm_cls", label_visibility="collapsed") or []
    top_n = int(fc[1].number_input(L("Top N by volume"), 0, 300, 0, 10, key="hm_top", help=L("0 = all markets")))
    direction = fc[2].selectbox(L("Direction"), ["all", "up", "down"], key="hm_dir", format_func=lambda k: {"all": L("All"), "up": L("Up"), "down": L("Down")}[k])
    min_abs = float(fc[3].number_input(L("Min |change| %"), 0.0, 50.0, 0.0, 0.5, key="hm_abs"))
    q = fc[4].text_input(L("Search"), key="hm_q", label_visibility="collapsed", placeholder=L("Search"))
    sort = fc[5].selectbox(L("Sort"), ["vol", "chg", "chg_abs", "rel"], key="hm_sort", format_func=lambda k: {"vol": L("Volume"), "chg": L("Change"), "chg_abs": L("Biggest move"), "rel": L("vs class")}[k])
    df = _mm_filter(_all, sel_cls, top_n, direction, min_abs, q, sort)
    if df.empty:
        st.info(f"{L('No markets match these filters.')} ({len(_all)} {L('markets')})")
        return
    bd = breadth(df)
    st.markdown(f"**{L('Market map')}** · {L('markets')}: {bd['n']} · {L('up')}: {bd['up_share']*100:.0f}% · "
                f"{L('down')}: {bd['down_share']*100:.0f}% · {L('median change')}: {bd['median_chg']:+.2f}%")
    st.caption(L("Tile colour = change vs the previous day; tile size = 24h volume (no market cap is available for these markets). "
                 "Breadth and strength describe the move, they do not predict it."))
    tiles = []
    for _, r in df.iterrows():
        g = max(-8.0, min(8.0, r["chg"])) / 8.0
        bg = f"rgba(14,203,129,{abs(g)*0.85+0.1:.2f})" if g >= 0 else f"rgba(246,70,93,{abs(g)*0.85+0.1:.2f})"
        size = 0.7 + 0.6 * (r["vol"] / df["vol"].max()) ** 0.5
        tiles.append(f"<div title='{r['name']} · {r['cls']} · {r['chg']:+.2f}% · vs class {r['rel']:+.2f}%' "
                     f"style='flex:{size:.2f} 1 110px;min-height:56px;background:{bg};border-radius:4px;padding:4px 6px;"
                     f"font:12px ui-monospace,Menlo,monospace;color:#eaecef'><b>{r['name']}</b><br>{r['chg']:+.2f}%</div>")
    st.markdown("<div style='display:flex;flex-wrap:wrap;gap:4px'>" + "".join(tiles) + "</div>", unsafe_allow_html=True)
    cls = by_class(df)
    st.dataframe(cls.rename(columns={"cls": L("Class"), "n": L("Markets"), "avg_chg": L("Avg change %"), "up_share": L("Share up")}).round(3),
                 hide_index=True)
