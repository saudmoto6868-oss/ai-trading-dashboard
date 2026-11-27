"""Forecast log: write a call BEFORE the outcome, score it later from the candles. Honest bookkeeping, no edge claims.

A forecast = {id, symbol, tf, side ('long'|'short'), entry, stop, target, made_at (ISO), horizon_bars, note}.
Scoring walks the candles after `made_at`: the first of stop / target to trade decides; neither inside the horizon = timeout.
Summary shows n, wins, win rate with a Wilson 95 % interval, and a verdict: n < 30 is 'not evidence', n < 100 is 'too small'.
Data lives in data/forecasts/ (one JSONL file per symbol). No network. Run tests: python3 tests/test_forecast_log.py
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "data" / "forecasts"


def _path(symbol):
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in symbol)
    return DIR / f"{safe}.jsonl"


def record(fc, folder=None):
    """Append one forecast. Refuses incomplete or impossible levels."""
    need = ("id", "symbol", "tf", "side", "entry", "stop", "target", "made_at", "horizon_bars")
    miss = [k for k in need if k not in fc]
    if miss:
        raise ValueError("missing: " + ", ".join(miss))
    if fc["side"] not in ("long", "short"):
        raise ValueError("side must be long or short")
    if fc["side"] == "long" and not (fc["stop"] < fc["entry"] < fc["target"]):
        raise ValueError("long needs stop < entry < target")
    if fc["side"] == "short" and not (fc["target"] < fc["entry"] < fc["stop"]):
        raise ValueError("short needs target < entry < stop")
    base = Path(folder) if folder else DIR
    base.mkdir(parents=True, exist_ok=True)
    p = base / (_path(fc["symbol"]).name)
    with p.open("a", encoding="utf8") as f:
        f.write(json.dumps(fc, ensure_ascii=False) + "\n")
    return p


def score(fc, candles):
    """candles: list of dicts {t, h, l} oldest first, starting at or after made_at. -> (outcome, R)."""
    risk = abs(fc["entry"] - fc["stop"]) or 1e-12
    long_ = fc["side"] == "long"
    for k, c in enumerate(candles[: int(fc["horizon_bars"])]):
        hit_stop = c["l"] <= fc["stop"] if long_ else c["h"] >= fc["stop"]
        hit_tgt = c["h"] >= fc["target"] if long_ else c["l"] <= fc["target"]
        if hit_stop and hit_tgt:
            return "loss", -1.0            # same bar: count the stop first (pessimistic)
        if hit_stop:
            return "loss", -1.0
        if hit_tgt:
            return "win", abs(fc["target"] - fc["entry"]) / risk
    return "timeout", 0.0


def wilson(wins, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = wins / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def verdict(n):
    if n < 30:
        return "not evidence (n < 30)"
    if n < 100:
        return "too small to judge (n < 100)"
    return "sample is big enough to test; check the interval and costs"


def summarise(results):
    """results: list of (outcome, R) for scored forecasts. Timeouts count in n, not in wins."""
    n = len(results)
    wins = sum(1 for o, _ in results if o == "win")
    losses = sum(1 for o, _ in results if o == "loss")
    timeouts = n - wins - losses
    avg_r = (sum(r for _, r in results) / n) if n else 0.0
    lo, hi = wilson(wins, n - timeouts) if (n - timeouts) else (0.0, 0.0)
    return {"n": n, "wins": wins, "losses": losses, "timeouts": timeouts,
            "win_rate": round(wins / (n - timeouts), 3) if (n - timeouts) else None,
            "ci95": (round(lo, 3), round(hi, 3)), "avg_R": round(avg_r, 3), "verdict": verdict(n)}
