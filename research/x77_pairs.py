"""X77 school-pair test, exactly as pre-registered in docs/X77_PREREG_PAIRS_2026-11-21.md (frozen at commit bc6715a).

Stage 1 (history, kill only):  python3 research/x77_pairs.py            -> research/x77_pairs_history.json
Stage 2 (forward, confirm):    python3 research/x77_pairs.py --forward  -> only signals at/after 2026-11-22 00:00 UTC
Reuses the lab's trade outcome (strategy_lab._outcome) and settings; no new detection math.
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modules import pa_patterns as P, signals as S, strategy_lab as L  # noqa: E402

DETECTORS = (S.ma_bull, S.fib_bull, S.ote_bull, S.sweep_signal_bull, S.key_level_bull, S.rsi_div_bull, S.macd_div_bull,
             P.pa_engulf_bull, P.pa_pin_bull)
PAIRS = {
    "P1 sweep+OTE": ({"sweep"}, {"ote"}),
    "P2 sweep+divergence": ({"sweep"}, {"rsi_div", "macd_div"}),
    "P3 candle at level": ({"level"}, {"pa_engulf", "pa_pin"}),
    "P4 trend pullback to Fib": ({"ma_cross", "ema_stack"}, {"fib"}),
}
TF, BARS, LAG, COOLDOWN, H = "1h", 1500, 2, 6, L.HORIZON["1h"]
FORWARD_FROM = pd.Timestamp("2026-11-22", tz="UTC")


def keys_by_bar(df: pd.DataFrame, start: int) -> dict:
    """bar index -> {(key, direction +1/-1)} from the frozen detector subset on the last WIN bars."""
    out = {}
    for i in range(start, len(df) - 1):
        win = df.iloc[max(0, i + 1 - L.WIN):i + 1].reset_index(drop=True)
        sigs, _ = S.detect_all(win, DETECTORS)
        out[i] = {(s["key"], 1 if s["direction"] == S.BULL else -1) for s in sigs}
    return out


def pair_trades(df: pd.DataFrame, kb: dict, seed: int = 0) -> list:
    """Apply the pair rule to per-bar keys -> trades {pair, i, d, day, r_net, base_net}."""
    hi, lo, cl = (df[c].to_numpy(float) for c in ("high", "low", "close"))
    atr = S.atr_series(df, 14).to_numpy(float)
    rng, last, out = np.random.RandomState(seed), {}, []
    for i in sorted(kb):
        if not atr[i] > 0:
            continue
        recent = set().union(*(kb.get(j, set()) for j in range(i - LAG, i + 1)))
        for name, (a, b) in PAIRS.items():
            for d in (1, -1):
                ka, kb_ = {(k, d) for k in a}, {(k, d) for k in b}
                if not (recent & ka and recent & kb_ and kb[i] & (ka | kb_)):
                    continue
                if i - last.get((name, d), -10**9) < COOLDOWN:
                    continue
                last[(name, d)] = i
                r = L._outcome(hi, lo, cl, i, d, L.STOP_ATR * atr[i], H)
                rb = L._outcome(hi, lo, cl, i, 1 if rng.rand() < .5 else -1, L.STOP_ATR * atr[i], H)
                out.append({"pair": name, "i": i, "d": d, "t": str(df["time"].iloc[i]),
                            "day": str(df["time"].iloc[i].date()), "r": r - L.COST_R, "base": rb - L.COST_R})
    return out


def stats(trades: list) -> dict:
    """n, win %, net mean R, day-clustered t, halves, random baseline."""
    n = len(trades)
    if not n:
        return {"n": 0}
    r = np.array([t["r"] for t in trades])
    days = pd.Series(r).groupby([t["day"] for t in trades]).sum()   # cluster by day: sum per day, t on daily sums scaled to trades
    t = float(days.mean() / (days.std(ddof=1) / np.sqrt(len(days)))) if len(days) > 2 and days.std(ddof=1) > 0 else 0.0
    order = np.argsort([x["t"] for x in trades]); h = n // 2
    first, second = r[order[:h]], r[order[h:]]
    return {"n": n, "days": int(len(days)), "win": round(100 * float((r > 0).mean()), 1), "net_mean": round(float(r.mean()), 4),
            "t_day": round(t, 2), "half1": round(float(first.mean()), 4) if h else None, "half2": round(float(second.mean()), 4),
            "base_net_mean": round(float(np.mean([x["base"] for x in trades])), 4)}


def verdict_history(s: dict) -> str:
    if s.get("n", 0) < 30:
        return "KILLED (n < 30)"
    if s["net_mean"] <= 0 or s["half1"] <= 0 or s["half2"] <= 0:
        return "KILLED (net <= 0 overall or in a half)"
    return "SURVIVES -> forward test only (not evidence)"


def one_symbol(sym: str) -> tuple:
    try:
        df = L._fetch(sym, TF, BARS).reset_index(drop=True)
    except Exception as exc:
        return sym, [], f"{type(exc).__name__}: {exc}"
    if df is None or len(df) < 200:
        return sym, [], "not enough bars"
    tr = pair_trades(df, keys_by_bar(df, 150))
    for t in tr:
        t["sym"] = sym
    return sym, tr, None


def main(forward: bool = False):
    with ProcessPoolExecutor(max_workers=min(12, len(L.SYMBOLS))) as ex:
        res = list(ex.map(one_symbol, L.SYMBOLS))
    trades = [t for _s, tr, _e in res for t in tr]
    if forward:
        trades = [t for t in trades if pd.Timestamp(t["t"]) >= FORWARD_FROM]
    by = {name: [t for t in trades if t["pair"] == name] for name in PAIRS}
    out = {"stage": "forward" if forward else "history", "tf": TF, "bars": BARS, "cost_r": L.COST_R,
           "errors": {s: e for s, _t, e in res if e}, "pairs": {}}
    for name, tr in by.items():
        s = stats(tr)
        s["per_market"] = dict(pd.Series([t["sym"] for t in tr]).value_counts()) if tr else {}
        s["verdict"] = verdict_history(s) if not forward else None
        out["pairs"][name] = s
    path = ROOT / "research" / ("x77_pairs_forward.json" if forward else "x77_pairs_history.json")
    path.write_text(json.dumps(out, indent=1, default=int))
    print(json.dumps({k: {x: v[x] for x in v if x != "per_market"} for k, v in out["pairs"].items()}, indent=1))
    print("errors:", out["errors"])


if __name__ == "__main__":
    main(forward="--forward" in sys.argv)
