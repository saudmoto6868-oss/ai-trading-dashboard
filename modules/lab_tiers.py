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
