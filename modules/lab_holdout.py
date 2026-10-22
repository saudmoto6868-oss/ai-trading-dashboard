"""Frozen out-of-sample holdout for ONE lab detector on ONE timeframe (owner 2026-10-22: the first formal backtest = liqline 1d).

Why a holdout: liqline 1d (net +0.257R, n 115) was the best of 407 detector x timeframe groups in the weekly lab, so its number is
biased upward (winner's curse). The only honest check is data the lab selection never saw. The weekly lab reads the newest
`LAB_BARS` (900) daily candles of each symbol; this module tests the SAME detector with the SAME procedure on the candles
OLDER than those, for a longer crypto universe (long daily history exists on OKX).

Procedure (frozen BEFORE the run, see FROZEN and the meeting-room entry):
  * detector / procedure = modules.strategy_lab.walk (stride 4, cooldown 6, stop 1.5 ATR, target 1.5R, horizon 20 bars, random-direction
    baseline per signal); costs 0.10R per trade; only signals of the detector `KEY`;
  * each symbol's holdout series is cut into two time halves that are walked separately, so 'both halves positive' is a real time split;
  * pass = n >= 100 and paired t vs the random baseline > 3 and net avg R > 0 and net avg R > 0 in BOTH halves.
One hypothesis, one run. If it fails it is closed as 'not evidence'; parameters are never re-tuned and re-run on this data.

  python modules/lab_holdout.py            -> data/holdout_liqline_1d.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FROZEN = {
    "key": "liqline", "tf": "1d", "lab_bars": 900, "fetch_bars": 4000, "min_holdout_bars": 700, "stride": 4, "cost_r": 0.10,
    "symbols": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "LTC-USDT", "BNB-USDT", "LINK-USDT", "AVAX-USDT",
                "DOT-USDT", "TRX-USDT", "BCH-USDT", "ETC-USDT", "ATOM-USDT"],
    "gate": {"n": 100, "t": 3.0, "net": 0.0, "halves": "both > 0"},
}
OUT = ROOT / "data" / "holdout_liqline_1d.json"


def holdout_halves(df, lab_bars: int = FROZEN["lab_bars"], min_bars: int = FROZEN["min_holdout_bars"]):
    """The candles older than the lab's window, cut into two time halves -> (first, second) or None when too short."""
    old = df.iloc[:-lab_bars].reset_index(drop=True) if len(df) > lab_bars else None
    if old is None or len(old) < min_bars:
        return None
    m = len(old) // 2
    return old.iloc[:m].reset_index(drop=True), old.iloc[m:].reset_index(drop=True)


def _t(x):
    x = np.asarray(x, float)
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 2 and x.std() > 0 else 0.0


def judge(halves: dict, cost_r: float = FROZEN["cost_r"], gate: dict = FROZEN["gate"]) -> dict:
    """halves = {'h1': [(r, base), ...], 'h2': [...]} pooled over symbols -> stats and the gate verdict."""
    allp = halves["h1"] + halves["h2"]
    r = np.array([a for a, _b in allp], float); b = np.array([c for _a, c in allp], float)
    n = len(r)
    net = r - cost_r
    h = {k: (np.array([a for a, _b in v], float) - cost_r) for k, v in halves.items()}
    out = {"n": n, "gross_avgR": round(float(r.mean()), 3) if n else None, "net_avgR": round(float(net.mean()), 3) if n else None,
           "random_avgR": round(float(b.mean()), 3) if n else None, "win_pct": round(100 * float((r >= 1.5 - 1e-9).mean()), 1) if n else None,
           "t_vs_random": round(_t(r - b), 2) if n else 0.0, "t_net_vs_zero": round(_t(net), 2) if n else 0.0,
           "h1": {"n": len(h["h1"]), "net_avgR": round(float(h["h1"].mean()), 3) if len(h["h1"]) else None},
           "h2": {"n": len(h["h2"]), "net_avgR": round(float(h["h2"].mean()), 3) if len(h["h2"]) else None}}
    out["pass"] = bool(n >= gate["n"] and out["t_vs_random"] > gate["t"] and out["net_avgR"] > gate["net"]
                       and (out["h1"]["net_avgR"] or -1) > 0 and (out["h2"]["net_avgR"] or -1) > 0)
    return out


def run(symbols=FROZEN["symbols"], fetch=None, log=print) -> dict:
    from modules import strategy_lab as SL
    fetch = fetch or SL._fetch
    pools, per = {"h1": [], "h2": []}, {}
    for sym in symbols:
        t0 = time.time()
        try:
            df = fetch(sym, FROZEN["tf"], FROZEN["fetch_bars"])
        except Exception as e:
            log(f"skip {sym}: {type(e).__name__} {e}"); continue
        hv = holdout_halves(df) if df is not None else None
        if hv is None:
            log(f"skip {sym}: holdout too short ({0 if df is None else len(df)} candles in total)"); continue
        got = {}
        for name, part in zip(("h1", "h2"), hv):
            ev, _bars = SL.walk(part, FROZEN["tf"], FROZEN["stride"])
            got[name] = [(e["r"], e["base"]) for e in ev if e["key"] == FROZEN["key"]]
            pools[name] += got[name]
        per[sym] = {"holdout_bars": sum(len(p) for p in hv), "from": str(df["time"].iloc[0].date()), "holdout_to": str(df["time"].iloc[len(df) - FROZEN["lab_bars"] - 1].date()),
                    "n": len(got["h1"]) + len(got["h2"])}
        log(f"{sym}: {len(df)} candles, holdout {per[sym]['holdout_bars']} bars, {per[sym]['n']} {FROZEN['key']} signals, {time.time() - t0:.0f}s")
    res = judge(pools)
    return {"frozen": FROZEN, "built": int(time.time()), "result": res, "per_symbol": per}


if __name__ == "__main__":
    out = run()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["result"], indent=1))
