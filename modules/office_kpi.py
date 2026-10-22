"""Technical Office control-room numbers, read from the weekly lab file (data/strategy_lab.json).

Only numbers the lab really produced; nothing estimated. Costs follow the owner's rule: net = avg R - 0.1R per trade.
Gate (meeting room): n >= 100, t > 3, net > 0, and both halves (in-sample / out-of-sample) positive when the lab has them.
"""
import json
import time
from pathlib import Path

COST_R = 0.10
GATE_N, GATE_T = 100, 3.0
OFF_MIN_N, OFF_R = 300, -0.06   # same rule as modules/lab_tiers.py
LAB_FILE = Path(__file__).resolve().parent.parent / "data" / "strategy_lab.json"

# trading styles -> lab timeframes (the lab runs 1m, 15m, 1h, 4h, 1d); see the Playbook artboard
STYLES = [("Scalp", ("1m",)), ("Day", ("15m", "1h")), ("Swing", ("4h", "1d")), ("Position", ("1d",))]

# Playbook by trading style (owner 2026-10-22). Timeframes step by ~4-6x (Elder's triple screen): trend from the higher one,
# setup from the middle one, entry from the lower one. Text is guidance; the numbers next to it come from the lab file.
STYLE_INFO = {
    "Scalp": {"hold": "minutes, closed in the same session", "stack": ("15m / 1H", "5m", "1m"),
              "rules": "session liquidity (Judas, sweep, CRT on the 1H / 4H candle), only inside the kill zones, stop behind the sweep, target >= 2R because of costs",
              "goal": "100 forward trades on 5m inside the kill zones with net >= +0.05R before any scalp alert", "status": "paused until evidence"},
    "Day": {"hold": "hours, closed before the day ends", "stack": ("4H", "1H", "15m"),
            "rules": "session AMD, CISD after a sweep, RSI divergence for timing, no entry +-1 h around a strong news event",
            "goal": "grade A+++ (5 context layers) passes t > 3 with both halves positive after costs within 4 weeks", "status": "candidate for testing"},
    "Swing": {"hold": "days to weeks", "stack": ("1W", "1D", "4H"),
              "rules": "daily levels and liquidity lines, break of a daily level, MACD divergence on the daily, stop 1.5 ATR, size by volatility",
              "goal": "liqline 1d (the only daily detector with n >= 100) gets the first frozen out-of-sample backtest; verdict within a week", "status": "first backtest"},
    "Position": {"hold": "weeks to months", "stack": ("1M", "1W", "1D"),
                 "rules": "time-series momentum (the strongest published evidence), wide stop, small size by volatility, spread over markets",
                 "goal": "add symbols until n >= 100 and compare with the random baseline before any verdict", "status": "needs more symbols"},
}


def style_top(d: dict, style: str, top: int = 5, min_n: int = 30) -> list:
    """Best detector x timeframe rows for one style (lab timeframes of that style), by net avg R, n >= min_n."""
    tfs = dict(STYLES)[style]
    rows = [r for r in _detector_rows(d) if r.get("side") == "all" and r.get("tf") in tfs and r["n"] >= min_n]
    rows.sort(key=net, reverse=True)
    return [{"key": r["key"], "tf": r["tf"], "n": r["n"], "win": r.get("win"), "avgR": r["avgR"], "net": net(r),
             "vs_random": round(r["avgR"] - (r.get("base_avgR") or 0.0), 3), "school": r.get("school")} for r in rows[:top]]


def load(path=LAB_FILE) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {}


def _detector_rows(d: dict) -> list:
    return [r for r in d.get("rows", []) if r.get("key") not in ("*CHAIN*", "*ALL*") and r.get("school") != "exit"]


def net(r: dict) -> float:
    return round((r.get("avgR") or 0.0) - COST_R, 3)


def passes_gate(r: dict) -> bool:
    if (r.get("n") or 0) < GATE_N or net(r) <= 0:
        return False
    if r.get("t") is None or r["t"] <= GATE_T:
        return False
    for k in ("is_avgR", "oos_avgR"):
        if k in r and (r[k] is None or r[k] - COST_R <= 0):
            return False
    return True


def summary(d: dict) -> dict:
    """Headline numbers for the control room; empty dict when the lab file is missing."""
    if not d:
        return {}
    rows = _detector_rows(d)
    per_tf = [r for r in rows if r.get("side") == "all" and r.get("tf") != "all"]
    keys = sorted({r["key"] for r in rows})
    off = sorted({r["key"] for r in rows if r.get("tf") == "all" and r.get("side") == "all" and r["n"] >= OFF_MIN_N and r["avgR"] <= OFF_R})
    chain = [r for r in d.get("rows", []) if r.get("key") == "*CHAIN*"]
    passed = [r for r in per_tf + chain if passes_gate(r)]
    big = [r for r in per_tf if r["n"] >= GATE_N]
    best = max(big, key=net) if big else None
    built = (d.get("meta") or {}).get("built")
    return {
        "detectors": len(keys), "off": off, "passed": len(passed),
        "candidates": len(per_tf) + len(chain),
        "best": None if not best else {"key": best["key"], "tf": best["tf"], "n": best["n"], "net": net(best),
                                       "vs_random": round(best["avgR"] - (best.get("base_avgR") or 0.0), 3)},
        "built": time.strftime("%Y-%m-%d", time.gmtime(built)) if built else None,
        "symbols": len((d.get("meta") or {}).get("symbols", [])),
    }


def pooled(d: dict, by: str) -> list:
    """Trade-weighted avg R per timeframe ('tf') or per school ('school'): [{label, n, avgR, net}]."""
    rows = [r for r in _detector_rows(d) if r.get("side") == "all"]
    rows = [r for r in rows if (r.get("tf") != "all") == (by == "tf")]
    acc = {}
    for r in rows:
        a = acc.setdefault(r[by], [0, 0.0]); a[0] += r["n"]; a[1] += r["n"] * (r.get("avgR") or 0.0)
    out = [{"label": k, "n": v[0], "avgR": round(v[1] / v[0], 3), "net": round(v[1] / v[0] - COST_R, 3)} for k, v in acc.items() if v[0]]
    order = {"1m": 0, "15m": 1, "1h": 2, "4h": 3, "1d": 4}
    return sorted(out, key=lambda x: order.get(x["label"], 9)) if by == "tf" else sorted(out, key=lambda x: -x["avgR"])


def styles(d: dict) -> list:
    """Per trading style: the strongest detector x timeframe with n >= 100, by net avg R (None when there is none)."""
    rows = [r for r in _detector_rows(d) if r.get("side") == "all"]
    out = []
    for name, tfs in STYLES:
        c = [r for r in rows if r.get("tf") in tfs and r["n"] >= GATE_N]
        b = max(c, key=net) if c else None
        out.append({"style": name, "tfs": "/".join(tfs), "key": b["key"] if b else None, "tf": b["tf"] if b else None,
                    "n": b["n"] if b else 0, "net": net(b) if b else None,
                    "vs_random": round(b["avgR"] - (b.get("base_avgR") or 0.0), 3) if b else None})
    return out
