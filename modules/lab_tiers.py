"""Tiers + evidence score from the weekly strategy lab (data/strategy_lab.json, real candles, random baseline).

* OFF  = detector with >= OFF_MIN_N lab trades and average R <= OFF_R: it no longer counts toward a trade's direction / stars
         (still drawn on charts as information). Recomputed every time the lab file changes - nothing is hard-coded.
* ev(key, tf) = the detector's lab average R on that timeframe (>= 30 trades), else its all-timeframe average (>= 30), else None.
* evidence(result, tf) = mean ev of the trade's own signals; replaces the family-count "strength", which the owner's journal showed
  was inverted (>= 70 % strength won 17 %). Lab finding 2026-10-17: setups WITH an opposing family lost about -280R in total,
  so an opposing signal costs OPPOSITION_PENALTY.
Without the lab file every function degrades to "no information" (no detector off, evidence None)."""
from __future__ import annotations

import json
import os
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "data" / "strategy_lab.json"
OFF_MIN_N, OFF_R, MIN_N, OPPOSITION_PENALTY = 300, -0.06, 30, 0.10
LAB_TF = {"1m": "1m", "13m": "15m", "15m": "15m", "1h": "1h", "2h": "1h", "3h": "4h", "4h": "4h", "6h": "4h", "7h": "4h", "8h": "4h", "12h": "1d", "1d": "1d"}
_cache = {"mtime": None, "rows": {}, "off": frozenset()}


def _load():
    try:
        m = os.path.getmtime(PATH)
    except OSError:
        return _cache
    if m != _cache["mtime"]:
        rows = {}
        for r in json.loads(PATH.read_text()).get("rows", []):
            if r.get("side") == "all":
                rows[(r["key"], r["tf"])] = r
        off = frozenset(k for (k, tf), r in rows.items() if tf == "all" and r["n"] >= OFF_MIN_N and r["avgR"] <= OFF_R)
        _cache.update(mtime=m, rows=rows, off=off)
    return _cache


def off_keys() -> frozenset:
    return _load()["off"]


def ev(key: str, tf: str):
    rows = _load()["rows"]
    for k in ((key, LAB_TF.get(tf, "")), (key, "all")):
        r = rows.get(k)
        if r and r.get("n", 0) >= MIN_N:
            return float(r["avgR"])
    return None


def evidence(result: dict, tf: str):
    """Average lab R of the trade's own (non-OFF) signals, minus a penalty when any signal points the other way."""
    off = off_keys()
    vals = [v for v in (ev(s.get("key"), tf) for s in result.get("signals", []) if s.get("key") not in off) if v is not None]
    if not vals:
        return None
    return round(sum(vals) / len(vals) - (OPPOSITION_PENALTY if result.get("against") else 0.0), 3)


def card(keys, tf: str) -> list:
    """Backtest beside the signal (owner 2026-11-20, like Flux Charts / OddsMaker): the weekly-lab row of each detector of a
    setup, on its own timeframe when it has >= MIN_N trades, else all timeframes. Net R already includes the lab cost.
    verdict: 'edge' (passed the lab gate), 'too few' (n < MIN_N: not evidence), 'loses' (net <= 0), 'positive, not proven'."""
    rows, out, seen = _load()["rows"], [], set()
    for k in keys:
        if not k or k in seen:
            continue
        seen.add(k)
        r = rows.get((k, LAB_TF.get(tf, ""))) or {}
        scope = LAB_TF.get(tf, "")
        if r.get("n", 0) < MIN_N:
            r, scope = rows.get((k, "all")) or r, "all"
        if not r:
            continue
        n, net = int(r.get("n", 0)), r.get("net")
        if net is None and r.get("avgR") is not None:   # per-detector rows carry gross avgR only; same cost as the lab (LAB_COST_R, 0.10R)
            net = round(float(r["avgR"]) - float(os.environ.get("LAB_COST_R", "0.10")), 3)
        verdict = "edge" if r.get("edge") else "too few" if n < MIN_N else "loses" if (net is None or net <= 0) else "positive, not proven"
        out.append({"key": k, "school": r.get("school", ""), "tf": scope, "n": n, "net": net, "t": r.get("t"),
                    "is": r.get("is_avgR"), "oos": r.get("oos_avgR"), "verdict": verdict})
    return out
