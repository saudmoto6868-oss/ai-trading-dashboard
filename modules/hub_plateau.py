"""HUB TAB 2 - PLATEAU LAB: is a parameter setting a stable plateau, or one lucky spike that fades out of sample?

Sweeps a moving-average cross (fast x slow) on real candles, costs included, no look-ahead (the position uses only bars before
the one it earns on). It then does what a hindsight backtest cannot:
  * picks the setting from the SMOOTHED surface (median of the 3x3 neighbourhood), not the single best cell;
  * walk-forward: expanding in-sample window, the NEXT block is out of sample; only stitched OOS numbers count;
  * runs the choice through hub_core.promote() and, when the Truth Court has published, its Bonferroni t for the whole N.
The MA cross is a probe for the METHOD (it has no claimed edge); the same plateau/walk-forward code can sweep any rule later.
Identity: blue, glyph "▦". Pure numpy; render() takes st so the module imports without streamlit."""
from __future__ import annotations

import numpy as np

from modules import hub_core

SPEC = hub_core.TabSpec(
    id="plateau", title="Plateau Lab", glyph="▦", accent="#4C8DFF",
    purpose="Tells a stable parameter plateau from a lucky spike using walk-forward, costs and the Truth Court's N.",
    consumes=("truth",),
)
FASTS = (5, 8, 10, 13, 20, 30, 40, 50)
SLOWS = (20, 30, 50, 80, 120, 160, 200)
COST = 0.0005          # per side, fraction of price (5 bps): planning estimate, not measured
MIN_FOLD_BARS = 120
WFE_MIN = 0.5          # OOS Sharpe / IS Sharpe (rule of thumb from the research notes: verify before relying on it)
FOLDS_PROFIT_MIN = 0.6


def _sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if n <= len(x):
        c = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def positions(close: np.ndarray, fast: int, slow: int) -> np.ndarray:
    """+1 / -1 / 0 held DURING each bar, decided from the previous bar's close (no look-ahead)."""
    f, s = _sma(close, fast), _sma(close, slow)
    sig = np.where(np.isnan(f) | np.isnan(s), 0.0, np.sign(f - s))
    return np.concatenate(([0.0], sig[:-1]))


def bar_returns(close: np.ndarray, pos: np.ndarray, cost: float = COST) -> np.ndarray:
    ret = np.concatenate(([0.0], close[1:] / close[:-1] - 1.0))
    turn = np.abs(np.diff(np.concatenate(([0.0], pos))))
    return pos * ret - cost * turn


def sharpe(r: np.ndarray) -> float:
    """Per-bar Sharpe (not annualised). nan when there is no variance."""
    if len(r) < 2:
        return float("nan")
    sd = r.std(ddof=1)
    return float(r.mean() / sd) if sd > 0 else float("nan")


def trade_returns(pos: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Return of each trade = sum of bar returns while the position stays the same non-zero value."""
    out, acc, cur = [], 0.0, 0.0
    for p, x in zip(pos, r):
        if p != cur:
            if cur != 0.0:
                out.append(acc)
            acc, cur = 0.0, p
        acc += x
    if cur != 0.0:
        out.append(acc)
    return np.array(out)


def surface(close: np.ndarray, lo: int, hi: int, fasts=FASTS, slows=SLOWS) -> np.ndarray:
    """Sharpe of every (fast, slow) cell on bars [lo, hi). Cells with fast >= slow are nan."""
    Z = np.full((len(fasts), len(slows)), np.nan)
    for i, f in enumerate(fasts):
        for j, s in enumerate(slows):
            if f < s:
                r = bar_returns(close, positions(close, f, s))[lo:hi]
                Z[i, j] = sharpe(r)
    return Z


def smooth(Z: np.ndarray) -> np.ndarray:
    """Median of each cell's 3x3 neighbourhood, ignoring nan: a spike next to bad cells gets pulled down."""
    out = np.full_like(Z, np.nan)
    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            if np.isnan(Z[i, j]):
                continue
            blk = Z[max(0, i - 1):i + 2, max(0, j - 1):j + 2]
            blk = blk[~np.isnan(blk)]
            out[i, j] = np.median(blk)
    return out


def _argbest(Z: np.ndarray):
    if np.all(np.isnan(Z)):
        return None
    return np.unravel_index(np.nanargmax(Z), Z.shape)


def neighbour_stability(Z: np.ndarray, ij) -> float:
    """Share of the chosen cell's neighbours that have the same sign as it (1.0 = a flat plateau, ~0 = isolated spike)."""
    i, j = ij
    c = Z[i, j]
    nb = [Z[a, b] for a in range(max(0, i - 1), min(Z.shape[0], i + 2)) for b in range(max(0, j - 1), min(Z.shape[1], j + 2))
          if (a, b) != (i, j) and not np.isnan(Z[a, b])]
    if np.isnan(c) or not nb:
        return 0.0
    return float(np.mean([np.sign(v) == np.sign(c) and v != 0 for v in nb]))


def walk_forward(close: np.ndarray, n_folds: int = 5, fasts=FASTS, slows=SLOWS, cost: float = COST) -> dict | None:
    """Expanding window: blocks 0..k train, block k+1 tests. Chooses by the smoothed surface (plateau) and, for comparison,
    by the raw best cell (peak). None when the series is too short for MIN_FOLD_BARS per block."""
    n = len(close)
    blk = n // (n_folds + 1)
    if blk < MIN_FOLD_BARS:
        return None
    folds = []
    oos_pl, oos_pk = [], []
    pos_cache: dict = {}

    def full_ret(f, s):
        if (f, s) not in pos_cache:
            p = positions(close, f, s)
            pos_cache[(f, s)] = (p, bar_returns(close, p, cost))
        return pos_cache[(f, s)]

    tr_all = []
    for k in range(n_folds):
        tr_hi, te_lo, te_hi = blk * (k + 1), blk * (k + 1), (blk * (k + 2) if k < n_folds - 1 else n)
        Z = surface(close, 0, tr_hi, fasts, slows)
        S = smooth(Z)
        pl, pk = _argbest(S), _argbest(Z)
        if pl is None or pk is None:
            continue
        fp, sp = fasts[pl[0]], slows[pl[1]]
        fk, sk = fasts[pk[0]], slows[pk[1]]
        pp, rp = full_ret(fp, sp)
        pkp, rk = full_ret(fk, sk)
        is_sh, oos_sh = Z[pl], sharpe(rp[te_lo:te_hi])
        pk_oos = sharpe(rk[te_lo:te_hi])
        folds.append({"fold": k + 1, "plateau": (fp, sp), "peak": (fk, sk), "is_sharpe": round(float(is_sh), 4),
                      "oos_sharpe": None if np.isnan(oos_sh) else round(oos_sh, 4),
                      "peak_is_sharpe": round(float(Z[pk]), 4), "peak_oos_sharpe": None if np.isnan(pk_oos) else round(pk_oos, 4),
                      "stability": round(neighbour_stability(S, pl), 2)})
        oos_pl.append(rp[te_lo:te_hi])
        oos_pk.append(rk[te_lo:te_hi])
        tr_all.append(trade_returns(pp[te_lo:te_hi], rp[te_lo:te_hi]))
    if not folds:
        return None
    stitched = np.concatenate(oos_pl)
    trades = np.concatenate(tr_all) if tr_all else np.array([])
    ok_f = [f for f in folds if f["oos_sharpe"] is not None and f["is_sharpe"] == f["is_sharpe"]]
    is_mean = float(np.mean([f["is_sharpe"] for f in ok_f])) if ok_f else float("nan")
    oos_mean = float(np.mean([f["oos_sharpe"] for f in ok_f])) if ok_f else float("nan")
    t = None
    if len(trades) >= 2 and trades.std(ddof=1) > 0:
        t = float(trades.mean() / (trades.std(ddof=1) / np.sqrt(len(trades))))
    return {
        "folds": folds, "n_oos_bars": int(len(stitched)), "n_trades": int(len(trades)),
        "oos_sharpe": sharpe(stitched), "peak_oos_sharpe": sharpe(np.concatenate(oos_pk)),
        "is_mean_sharpe": is_mean, "oos_mean_sharpe": oos_mean,
        "wfe": (oos_mean / is_mean) if is_mean and is_mean > 0 else float("nan"),
        "pct_folds_profitable": float(np.mean([(f["oos_sharpe"] or 0) > 0 for f in folds])),
        "trade_mean": float(trades.mean()) if len(trades) else float("nan"), "t": t,
        "equity": np.cumsum(stitched).tolist(),
    }


def verdict(wf: dict | None, truth_bonferroni_t: float | None = None) -> tuple[bool, list]:
    """Gate for the walk-forward result: hub_core.promote() + WFE + share of profitable folds + the Truth Court's t for all N."""
    if wf is None:
        return False, ["series too short for walk-forward"]
    n_is = [f["is_sharpe"] for f in wf["folds"]]
    cand = {"n": wf["n_trades"], "t": wf["t"],
            "is_avgR": float(np.mean(n_is)) if n_is else None,
            "oos_avgR": wf["trade_mean"] if wf["n_trades"] else None,
            "net_avgR": wf["trade_mean"] if wf["n_trades"] else None}   # trade returns already carry costs
    ok, why = hub_core.promote(cand)
    wfe = wf["wfe"]
    if not (wfe == wfe) or wfe < WFE_MIN:
        ok, why = False, why + [f"walk-forward efficiency {'n/a' if wfe != wfe else f'{wfe:.2f}'} < {WFE_MIN}"]
    if wf["pct_folds_profitable"] < FOLDS_PROFIT_MIN:
        ok, why = False, why + [f"only {wf['pct_folds_profitable']:.0%} of folds profitable (< {FOLDS_PROFIT_MIN:.0%})"]
    if truth_bonferroni_t is not None and (wf["t"] is None or abs(wf["t"]) < truth_bonferroni_t):
        ok, why = False, why + [f"|t| below the Truth Court's {truth_bonferroni_t} for all counted trials"]
    return ok, why


def evaluate(close, key: str = "", root=None, publish: bool = True) -> dict:
    """Full run for one series: surface, plateau vs peak, walk-forward, verdict. Publishes this key into the tab's snapshot
    (merged with earlier keys; n_trials = every cell of every swept series, so the Truth Court can count them)."""
    close = np.asarray(close, dtype=float)
    Z = surface(close, 0, len(close))
    S = smooth(Z)
    pl, pk = _argbest(S), _argbest(Z)
    wf = walk_forward(close)
    truth = hub_core.read("truth", root)
    bt = truth.get("bonferroni_t") if truth else None
    ok, why = verdict(wf, bt)
    out = {"key": key, "Z": Z, "S": S, "plateau": None if pl is None else (FASTS[pl[0]], SLOWS[pl[1]]),
           "peak": None if pk is None else (FASTS[pk[0]], SLOWS[pk[1]]),
           "peak_vs_plateau": None if pl is None else {"peak_sharpe": float(Z[pk]), "plateau_smoothed": float(S[pl])},
           "stability": None if pl is None else neighbour_stability(S, pl),
           "spike": bool(pk is not None and S[pk] < 0.5 * Z[pk]) if pk is not None and Z[pk] > 0 else False,
           "wf": wf, "promote": ok, "why_not": why, "truth_t": bt}
    if publish and key:
        old = hub_core.read(SPEC.id, root) or {"findings": [], "n_trials": 0}
        keep = [f for f in old["findings"] if f.get("key") != key]
        cells = int(np.sum(~np.isnan(Z)))
        keep.append({"key": key, "promote": ok, "why_not": why[:3], "plateau": out["plateau"],
                     "n_trades": 0 if wf is None else wf["n_trades"], "t": None if wf is None else wf["t"], "cells": cells})
        hub_core.publish(SPEC.id, keep, sum(f.get("cells", 0) for f in keep), root=root)
    return out


def _load_close(st, sym: str, tf: str, bars: int = 2500) -> np.ndarray:
    """Close prices, oldest first. OKX symbols are paged from the history endpoint (the app's own fetch_long);
    Hyperliquid symbols come from the app's cached feed, which holds fewer candles (the page then says so)."""
    @st.cache_data(ttl=600, show_spinner="Loading candles...")
    def _fetch(sym, tf, bars):
        if sym.startswith("HL:"):
            from modules import market_cache
            df = market_cache.get_klines(sym, tf, 1000)
        else:
            from modules import backtest_tf
            df = backtest_tf.fetch_long(sym, tf, bars)
        if df is None or df.empty:
            raise RuntimeError("empty candle response")
        return df["close"].astype(float).to_numpy()
    return _fetch(sym, tf, bars)


def render(st, L=lambda s: s) -> None:
    import pandas as pd
    st.markdown(f"<div style='border-left:4px solid {SPEC.accent};padding-left:10px'><b>{SPEC.glyph} {L(SPEC.title)}</b><br>"
                f"<span style='opacity:.75'>{L(SPEC.purpose)}</span></div>", unsafe_allow_html=True)
    c = st.columns(3)
    sym = c[0].selectbox(L("Symbol"), ["BTC-USDT", "ETH-USDT", "SOL-USDT", "HL:xyz:GOLD", "HL:xyz:SP500", "HL:xyz:CL"], key="hp_sym")
    tf = c[1].selectbox(L("Timeframe"), ["1h", "1d"], key="hp_tf")
    run = c[2].button(L("Run walk-forward"), key="hp_run")
    st.caption(L(f"Probe rule: moving-average cross, {COST * 1e4:.0f} bps per side, no look-ahead. It tests the METHOD, not a claimed edge."))
    if not run:
        snap = hub_core.read(SPEC.id)
        if snap and snap["findings"]:
            st.dataframe([{"series": f["key"], "pass": f["promote"], "trades": f["n_trades"], "t": f["t"], "why not": "; ".join(f["why_not"])}
                          for f in snap["findings"]], hide_index=True, use_container_width=True)
        else:
            st.info(L("Pick a symbol and press Run. Nothing is estimated until you do."))
        return
    try:
        close = _load_close(st, sym, tf)
        st.caption(L(f"{len(close)} candles. Walk-forward needs at least {MIN_FOLD_BARS * 6}."))
    except Exception as e:
        st.error(L("No candles: ") + str(e))
        return
    res = evaluate(close, key=f"{sym} {tf}")
    wf = res["wf"]
    (st.success if res["promote"] else st.warning)(L("Passes every gate" if res["promote"] else "Not promotable: ") + "; ".join(res["why_not"][:3]))
    m = st.columns(4)
    m[0].metric(L("Plateau choice (fast, slow)"), str(res["plateau"]))
    m[1].metric(L("Raw peak (fast, slow)"), str(res["peak"]), delta=L("spike") if res["spike"] else None, delta_color="inverse")
    m[2].metric(L("Neighbour stability"), "n/a" if res["stability"] is None else f"{res['stability']:.0%}")
    m[3].metric(L("Walk-forward efficiency"), "n/a" if not wf or wf["wfe"] != wf["wfe"] else f"{wf['wfe']:.2f}")
    import altair as alt
    rows = [{"fast": str(f), "slow": str(s), "sharpe": None if np.isnan(res["S"][i, j]) else float(res["S"][i, j])}
            for i, f in enumerate(FASTS) for j, s in enumerate(SLOWS)]
    st.altair_chart(alt.Chart(pd.DataFrame(rows)).mark_rect().encode(
        x=alt.X("slow:O", sort=[str(s) for s in SLOWS]), y=alt.Y("fast:O", sort=[str(f) for f in FASTS]),
        color=alt.Color("sharpe:Q", scale=alt.Scale(scheme="redyellowgreen", domainMid=0)), tooltip=["fast", "slow", "sharpe"]
    ).properties(height=260, title=L("Smoothed Sharpe surface (median of 3x3 neighbours)")), use_container_width=True)
    if wf:
        st.dataframe(wf["folds"], hide_index=True, use_container_width=True)
        st.line_chart(pd.DataFrame({"stitched OOS equity (sum of bar returns)": wf["equity"]}))
