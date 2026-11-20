"""Pre-registered test (docs/PREREG_2026-11-20_HTF_AND_RISK.md): real higher-timeframe alignment and risk per trade.

Signals = every strategy-lab detector on 1h (strategy_lab.walk: same entry, 1.5 ATR stop, 1.5R target, horizon, 0.10R cost).
Each event is tagged with the state of a REAL higher timeframe (1D primary, 4H secondary), from the last HTF bar that
closed before the signal bar (no look-ahead):
  trend    = sign of the return over the last 20 closed HTF bars; "flat" when |return| < 1 x ATR(14) of the HTF
  location = position in the range of the last 20 closed HTF bars (discount <= 1/3, premium >= 2/3)
Arms for a signal of direction d: W (with the HTF trend), A_ext (against, long in discount / short in premium),
A_mid (against, elsewhere), F (HTF flat).
Then a bootstrap of the R series at 0.25% / 0.5% / tiered risk (drawdown and prop-limit breach odds).

Run from the repo root:  python -m research.htf_arms.run_htf_arms  (needs network: OKX + Hyperliquid)."""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from modules.strategy_lab import COST_R, SYMBOLS, _fetch, walk

LTF, LTF_BARS = "1h", 4000
HTFS = {"1d": 400, "4h": 2000}
N_HTF, FLAT_ATR = 20, 1.0
OUT = Path(__file__).with_name("results.json")


def htf_state(htf: pd.DataFrame) -> pd.DataFrame:
    """Per closed HTF bar: trend (+1 / -1 / 0) and range position over the last N_HTF bars. Indexed by bar CLOSE time."""
    h, l, c = htf["high"], htf["low"], htf["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    ret = c - c.shift(N_HTF)
    trend = np.where(ret.abs() < FLAT_ATR * atr, 0, np.sign(ret))
    hh, ll = h.rolling(N_HTF).max(), l.rolling(N_HTF).min()
    pos = ((c - ll) / (hh - ll)).where(hh > ll, 0.5)
    step = htf["time"].diff().median()
    out = pd.DataFrame({"close_time": htf["time"] + step, "trend": trend, "pos": pos})
    return out.dropna().reset_index(drop=True)


def arm(d: int, trend: int, pos: float) -> str:
    if trend == 0:
        return "F"
    if trend == d:
        return "W"
    at_ext = pos <= 1 / 3 if d > 0 else pos >= 2 / 3
    return "A_ext" if at_ext else "A_mid"


def tag(events, ltf_times_ms, st: pd.DataFrame, name: str):
    """Attach the HTF arm to each event using the last HTF bar closed at or before the signal bar time."""
    ct = st["close_time"].values.astype("datetime64[ms]").astype(np.int64)
    for e in events:
        k = np.searchsorted(ct, e["ts"], side="right") - 1
        e[name] = None if k < 0 else arm(e["d"], int(st["trend"].iloc[k]), float(st["pos"].iloc[k]))


def stats(rows):
    if not rows:
        return {"n": 0}
    r = np.array([x["r"] for x in rows]) - COST_R
    dif = np.array([x["r"] - x["base"] for x in rows])
    t = dif.mean() / (dif.std(ddof=1) / np.sqrt(len(dif))) if len(dif) > 2 and dif.std() > 0 else 0.0
    half = {}
    for h in (False, True):
        rr = np.array([x["r"] for x in rows if x["oos"] == h]) - COST_R
        half["oos" if h else "is"] = {"n": int(len(rr)), "net": round(float(rr.mean()), 4) if len(rr) else None}
    return {"n": int(len(r)), "net": round(float(r.mean()), 4), "win": round(float((r > 0).mean()), 3),
            "t_vs_random": round(float(t), 2), **half}


def diff_t(a, b):
    """Welch t of mean net R, arm a minus arm b."""
    if len(a) < 3 or len(b) < 3:
        return None
    x, y = np.array([e["r"] for e in a]), np.array([e["r"] for e in b])
    se = np.sqrt(x.var(ddof=1) / len(x) + y.var(ddof=1) / len(y))
    return round(float((x.mean() - y.mean()) / se), 2) if se > 0 else None


def bootstrap(rs, risk, n_paths=10000, n_trades=200, seed=7):
    """rs = net R per trade; risk = fraction of equity per 1R. -> median return, DD quantiles, breach odds."""
    rng = np.random.default_rng(seed)
    rs = np.asarray(rs, float)
    if len(rs) < 30:
        return None
    draws = rng.choice(rs, size=(n_paths, n_trades), replace=True) * (risk if np.isscalar(risk) else 1)
    eq = np.cumprod(1 + draws, axis=1)
    peak = np.maximum.accumulate(np.concatenate([np.ones((n_paths, 1)), eq], axis=1), axis=1)[:, 1:]
    dd = 1 - eq / peak
    mdd = dd.max(axis=1)
    return {"median_ret_pct": round(float((np.median(eq[:, -1]) - 1) * 100), 2),
            "mdd_p50_pct": round(float(np.percentile(mdd, 50) * 100), 2), "mdd_p95_pct": round(float(np.percentile(mdd, 95) * 100), 2),
            "p_mdd_ge_5": round(float((mdd >= .05).mean()), 4), "p_mdd_ge_10": round(float((mdd >= .10).mean()), 4)}


def main(symbols=SYMBOLS, log=print):
    all_ev, meta = [], []
    for sym in symbols:
        t0 = time.time()
        try:
            df = _fetch(sym, LTF, LTF_BARS).reset_index(drop=True)
            states = {tf: htf_state(_fetch(sym, tf, n).reset_index(drop=True)) for tf, n in HTFS.items()}
        except Exception as e:   # one market failing must not stop the run
            log(f"skip {sym}: {type(e).__name__} {e}")
            continue
        if len(df) < 300:
            log(f"skip {sym}: {len(df)} candles"); continue
        ev, _ = walk(df, LTF)
        for tf, st in states.items():
            tag(ev, None, st, "htf_" + tf)
        for e in ev:
            e["sym"] = sym
            e.pop("var", None); e.pop("stop", None); e.pop("mirror", None)
        all_ev += ev
        meta.append({"sym": sym, "bars": len(df), "from": str(df["time"].iloc[0]), "to": str(df["time"].iloc[-1]), "events": len(ev),
                     "sec": round(time.time() - t0, 1)})
        log(f"{sym}: {len(df)} bars, {len(ev)} events, {meta[-1]['sec']} s")

    res = {"meta": meta, "cost_r": COST_R, "n_events": len(all_ev), "arms": {}, "diff_t": {}, "by_school": {}, "same_tf_trend": {},
           "risk": {}}
    for tf in HTFS:
        k = "htf_" + tf
        groups = {a: [e for e in all_ev if e.get(k) == a] for a in ("W", "A_ext", "A_mid", "F")}
        res["arms"][tf] = {a: stats(g) for a, g in groups.items()}
        res["diff_t"][tf] = {"W-A_ext": diff_t(groups["W"], groups["A_ext"]), "W-A_mid": diff_t(groups["W"], groups["A_mid"]),
                             "A_ext-A_mid": diff_t(groups["A_ext"], groups["A_mid"])}
        sch = {}
        for e in all_ev:
            if e.get(k):
                sch.setdefault(e["fam"], {}).setdefault(e[k], []).append(e)
        res["by_school"][tf] = {f: {a: stats(g) for a, g in d.items()} for f, d in sch.items()}
    res["same_tf_trend"] = {t: stats([e for e in all_ev if e["trend"] == t]) for t in ("with", "against", "flat")}

    net_all = [e["r"] - COST_R for e in sorted(all_ev, key=lambda x: x["ts"])]
    res["risk"]["all_signals"] = {f"{r * 100:.2f}%": bootstrap(net_all, r) for r in (0.0025, 0.005)}
    for tf in HTFS:
        for a in ("W", "A_ext"):
            rs = [e["r"] - COST_R for e in all_ev if e.get("htf_" + tf) == a]
            res["risk"][f"{tf}_{a}"] = {f"{r * 100:.2f}%": bootstrap(rs, r) for r in (0.0025, 0.005)}
    OUT.write_text(json.dumps(res, indent=1, default=str))
    keep = ("ts", "sym", "key", "fam", "d", "r", "base", "oos", "trend", "htf_1d", "htf_4h")   # per-event rows for robustness checks
    pd.DataFrame([{k: e.get(k) for k in keep} for e in all_ev]).to_csv(OUT.with_name("events.csv.gz"), index=False)
    log(f"wrote {OUT} ({len(all_ev)} events)")
    return res


if __name__ == "__main__":
    main(tuple(sys.argv[1:]) or SYMBOLS)
