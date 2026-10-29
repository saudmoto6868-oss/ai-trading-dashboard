"""HUB TAB 3 - REGIME RADAR: which kind of market is each symbol in right now, and how do regimes behave?

Labels every candle with one regime using ONLY information up to that candle (trailing windows, no look-ahead):
  Crash   5-bar return below -2 sigma of its trailing distribution
  HiVol   ATR(14) above 1.5x its trailing median
  Squeeze Bollinger width in the bottom 20% of its trailing range
  Trend   ADX(14) > 25        Chop  ADX(14) < 20        Mixed  everything else
(first match wins, in that order). It then reports per regime: how many bars, how long it lasts, and what the NEXT bar did
(mean return with a t-stat, mean absolute move). Regimes with n < 30 are shown but flagged "not evidence". It also watches
cross-asset correlation: when the average pair correlation is high, holding several symbols is one bet, not several.
This tab describes the market; it does not claim an edge. Other tabs may SLICE their results by the regime it publishes.
Identity: green, glyph "◉". Pure numpy; render() takes st so the module imports without streamlit."""
from __future__ import annotations

import numpy as np

from modules import hub_core
from modules.regime_lib import REGIMES, WARM, _trailing, _wilder, adx, label, true_range   # the shared definition; re-exported so this tab's API is unchanged

SPEC = hub_core.TabSpec(
    id="regime", title="Regime Radar", glyph="◉", accent="#2FBF71",
    purpose="Labels each symbol's market regime with no look-ahead, and flags when 'diversified' symbols move as one.",
)
MIN_N = 30            # per-regime bars before a number is more than a description
CORR_WIN = 60
CORR_HIGH = 0.7


def regime_stats(labels: list, close) -> dict:
    """Per regime: bars, mean run length, persistence P(next bar same regime), and what the NEXT bar did (label at t, return t->t+1)."""
    close = np.asarray(close, dtype=float)
    nxt = np.concatenate((close[1:] / close[:-1] - 1.0, [np.nan]))
    stats = {}
    for g in REGIMES:
        idx = [i for i, l in enumerate(labels) if l == g]
        runs, cur = [], 0
        for l in labels:
            if l == g:
                cur += 1
            elif cur:
                runs.append(cur)
                cur = 0
        if cur:
            runs.append(cur)
        same = [labels[i + 1] == g for i in idx if i + 1 < len(labels) and labels[i + 1] != ""]
        r = nxt[idx]
        r = r[~np.isnan(r)]
        t = None
        if len(r) >= 2 and r.std(ddof=1) > 0:
            t = float(r.mean() / (r.std(ddof=1) / np.sqrt(len(r))))
        stats[g] = {"bars": len(idx), "mean_run": round(float(np.mean(runs)), 1) if runs else 0.0,
                    "persistence": round(float(np.mean(same)), 3) if same else None,
                    "next_mean": None if not len(r) else float(r.mean()), "next_abs": None if not len(r) else float(np.abs(r).mean()),
                    "t": t, "evidence": len(idx) >= MIN_N}
    return stats


def current(labels: list) -> dict:
    """Latest regime and how many bars it has lasted."""
    last = next((i for i in range(len(labels) - 1, -1, -1) if labels[i]), None)
    if last is None:
        return {"regime": None, "bars_in": 0}
    k = 0
    while last - k >= 0 and labels[last - k] == labels[last]:
        k += 1
    return {"regime": labels[last], "bars_in": k, "stale_bars": len(labels) - 1 - last}


def avg_pair_corr(closes: dict, win: int = CORR_WIN) -> dict:
    """Mean pairwise correlation of the last `win` returns across symbols (aligned from the end). None if < 2 usable series."""
    rets = {}
    for k, c in closes.items():
        c = np.asarray(c, dtype=float)
        if len(c) > win:
            rets[k] = c[-win:] / c[-win - 1:-1] - 1.0
    keys = sorted(rets)
    if len(keys) < 2:
        return {"mean_corr": None, "pairs": [], "high": False}
    M = np.corrcoef(np.array([rets[k] for k in keys]))
    pairs = [(keys[i], keys[j], float(M[i, j])) for i in range(len(keys)) for j in range(i + 1, len(keys)) if not np.isnan(M[i, j])]
    mc = float(np.mean([p[2] for p in pairs])) if pairs else None
    return {"mean_corr": mc, "pairs": pairs, "high": mc is not None and mc > CORR_HIGH}


def analyse(df, key: str, root=None, publish: bool = True) -> dict:
    """df needs high/low/close. Returns labels, stats, current regime; publishes this key (merged with earlier ones)."""
    lab = label(df["high"].to_numpy(), df["low"].to_numpy(), df["close"].to_numpy())
    st = regime_stats(lab, df["close"].to_numpy())
    cur = current(lab)
    out = {"key": key, "labels": lab, "stats": st, "current": cur, "n_bars": len(lab)}
    if publish and key:
        old = hub_core.read(SPEC.id, root) or {"findings": []}
        keep = [f for f in old["findings"] if f.get("key") != key]
        keep.append({"key": key, "regime": cur["regime"], "bars_in": cur["bars_in"],
                     "persistence": {g: s["persistence"] for g, s in st.items()}, "bars": {g: s["bars"] for g, s in st.items()}})
        fund = old.get("funding")
        hub_core.publish(SPEC.id, keep, len(keep) * len(REGIMES), extra={"funding": fund} if fund else None, root=root)   # one next-bar mean test per regime per series
    return out


# ---- Funding / open interest context (Hyperliquid public /info, no key) ------------------------------------------------------
HL_INFO = "https://api.hyperliquid.xyz/info"
COINS = ("BTC", "ETH", "SOL")
FUND_DAYS = 30
MIN_GAP_S = 900        # readings closer than 15 minutes are noise: no price/OI reading is given
FUND_Z_HOT = 2.0       # |z| above this = funding unusually stretched versus its own last 30 days


def funding_z(history: list, current: float) -> float | None:
    """z-score of the current funding rate against its own history (needs >= 24 points and some spread)."""
    xs = [float(x) for x in history]
    if len(xs) < 24:
        return None
    m = sum(xs) / len(xs)
    sd = (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5
    return None if sd <= 0 else (current - m) / sd


def quadrant(d_price: float, d_oi: float) -> str:
    """Price move x open-interest move since the last reading. Context only, never a signal."""
    if d_oi == 0 or d_price == 0:
        return "flat"
    if d_price > 0:
        return "new longs (price up, OI up)" if d_oi > 0 else "short covering (price up, OI down)"
    return "new shorts (price down, OI up)" if d_oi > 0 else "long liquidation (price down, OI down)"


def fetch_funding(coins=COINS, now_ms: int | None = None, post=None) -> dict:
    """{coin: {funding, premium, mark, oi_usd, history}} from Hyperliquid. `post(payload) -> json` is injectable for tests."""
    if post is None:
        import requests

        def post(payload):
            r = requests.post(HL_INFO, json=payload, timeout=10)
            r.raise_for_status()
            return r.json()
    import time as _t
    now_ms = now_ms or int(_t.time() * 1000)
    meta, ctxs = post({"type": "metaAndAssetCtxs"})
    idx = {u["name"]: i for i, u in enumerate(meta["universe"])}
    out = {}
    for c in coins:
        if c not in idx:
            continue
        x = ctxs[idx[c]]
        hist = post({"type": "fundingHistory", "coin": c, "startTime": now_ms - FUND_DAYS * 86400 * 1000})
        mark = float(x["markPx"])
        out[c] = {"funding": float(x["funding"]), "premium": float(x["premium"]), "mark": mark,
                  "oi_usd": float(x["openInterest"]) * mark, "history": [float(h["fundingRate"]) for h in hist]}
    return out


def funding_context(raw: dict, prev: dict | None = None, now: int | None = None) -> dict:
    """Turn fetched numbers into the table: annualised funding, z vs own history, premium, OI, OI/price change since the last reading."""
    import time as _t
    now = int(now or _t.time())
    ctx = {}
    for c, r in raw.items():
        z = funding_z(r["history"], r["funding"])
        row = {"funding_apr_pct": round(r["funding"] * 24 * 365 * 100, 2), "z": None if z is None else round(z, 2),
               "stretched": z is not None and abs(z) > FUND_Z_HOT, "premium_bps": round(r["premium"] * 1e4, 2),
               "mark": r["mark"], "oi_usd": r["oi_usd"], "ts": now, "since": None, "quadrant": None}
        p = (prev or {}).get(c)
        if p and p.get("oi_usd") and p.get("mark") and p.get("ts") and now > p["ts"]:
            row["since"] = now - p["ts"]
            row["oi_change_pct"] = round(100 * (r["oi_usd"] / p["oi_usd"] - 1), 2)
            row["quadrant"] = quadrant(r["mark"] - p["mark"], r["oi_usd"] - p["oi_usd"]) if row["since"] >= MIN_GAP_S else "too soon (< 15 min)"
        ctx[c] = row
    return ctx


def update_funding(root=None, post=None, now: int | None = None) -> dict:
    """Fetch, compare with the previous reading stored in this tab's snapshot, store the new one (findings are kept)."""
    old = hub_core.read(SPEC.id, root) or {"findings": [], "n_trials": 0}
    ctx = funding_context(fetch_funding(post=post), old.get("funding"), now)
    extra = {k: v for k, v in old.items() if k not in ("asof", "tab", "n_trials", "findings")}
    extra["funding"] = ctx
    hub_core.publish(SPEC.id, old.get("findings", []), old.get("n_trials", 0), extra=extra, root=root)
    return ctx


def _load_df(st, sym: str, tf: str, bars: int = 1000):
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
        return df
    return _fetch(sym, tf, bars)


SYMBOLS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "HL:xyz:GOLD", "HL:xyz:SP500", "HL:xyz:CL"]
_COLOR = {"Crash": "#E5484D", "HiVol": "#F5A524", "Squeeze": "#8E4EC6", "Trend": "#2FBF71", "Chop": "#8B8D98", "Mixed": "#6E7681"}


def render(st, L=lambda s: s) -> None:
    import pandas as pd
    from modules import hub_ui
    hub_ui.show(st, hub_ui.header(SPEC, L(SPEC.purpose), L(SPEC.title)))
    tf = st.selectbox(L("Timeframe"), ["1d", "1h"], key="hr_tf")
    run = st.button(L("Scan regimes"), key="hr_run")
    if not run:
        snap = hub_core.read(SPEC.id)
        if snap and snap["findings"]:
            st.dataframe([{"series": f["key"], "regime": f["regime"], "bars in regime": f["bars_in"]} for f in snap["findings"]],
                         hide_index=True, use_container_width=True)
        else:
            st.info(L("Press Scan. Labels use only past candles; nothing is estimated until you do."))
        return
    rows, closes, details = [], {}, {}
    for sym in SYMBOLS:
        try:
            df = _load_df(st, sym, tf)
        except Exception as e:
            rows.append({"symbol": sym, "regime": "no data", "bars in regime": 0, "candles": 0, "note": str(e)[:60]})
            continue
        if len(df) <= WARM + MIN_N:
            rows.append({"symbol": sym, "regime": "too short", "bars in regime": 0, "candles": len(df), "note": f"need > {WARM + MIN_N}"})
            continue
        res = analyse(df, f"{sym} {tf}")
        closes[sym] = df["close"].astype(float).to_numpy()
        details[sym] = res
        rows.append({"symbol": sym, "regime": res["current"]["regime"], "bars in regime": res["current"]["bars_in"], "candles": len(df), "note": ""})
    st.dataframe(rows, hide_index=True, use_container_width=True)
    cc = avg_pair_corr(closes)
    if cc["mean_corr"] is not None:
        cur = [(sym, d["current"]["regime"]) for sym, d in details.items()]
        hub_ui.show(st, hub_ui.cards([("R", L("Series scanned"), len(details), L(f"timeframe {tf}"), "", None),
                                      ("c", L(f"Avg correlation ({CORR_WIN} returns)"), f"{cc['mean_corr']:.2f}", L("high: close to one bet") if cc["high"] else L("not high: some real diversification"),
                                       "warn" if cc["high"] else "up", max(0.0, cc["mean_corr"]) * 100)]))
    try:
        fx = update_funding()
        st.markdown("**" + L("Funding and open interest (Hyperliquid)") + "**")
        st.dataframe([{"coin": c, "funding APR %": v["funding_apr_pct"], "z vs 30d": v["z"], "stretched": v["stretched"], "premium bps": v["premium_bps"],
                       "OI $M": round(v["oi_usd"] / 1e6, 1), "OI change %": v.get("oi_change_pct"), "since (s)": v["since"], "reading": v["quadrant"]}
                      for c, v in fx.items()], hide_index=True, use_container_width=True)
        st.caption(L("OI change and the price/OI reading need a previous scan; the first scan only stores the baseline. Context, not a signal."))
    except Exception as e:
        st.caption(L("Funding data unavailable: ") + str(e)[:80])
    if details:
        pick = st.selectbox(L("Detail"), list(details), key="hr_pick")
        s = details[pick]["stats"]
        st.dataframe([{"regime": g, "bars": v["bars"], "avg run (bars)": v["mean_run"], "persistence": v["persistence"],
                       "next-bar mean": v["next_mean"], "next-bar |move|": v["next_abs"], "t": v["t"],
                       "evidence": "n>=30" if v["evidence"] else "not evidence"} for g, v in s.items()],
                     hide_index=True, use_container_width=True)
        st.caption(L("Next-bar numbers describe behaviour inside each regime. They are not a trading edge until they pass the Truth Court."))
