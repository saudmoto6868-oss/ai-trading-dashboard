"""Technical Office control-room numbers, read from the weekly lab file (data/strategy_lab.json).

Only numbers the lab really produced; nothing estimated. Costs follow the owner's rule: net = avg R - 0.1R per trade.
Gate (meeting room): n >= 100, t > 3, net > 0, and both halves (in-sample / out-of-sample) positive when the lab has them.
"""
from __future__ import annotations

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
              "goal": "liqline 1d (the best net among the 11 daily detectors with n >= 100, so its number is biased upward) gets a frozen holdout on older candles; see lab_holdout", "status": "first backtest"},
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
        "det_rows": len(per_tf), "det_t": sum(1 for r in per_tf if r.get("t") is not None),   # detector x timeframe rows and how many have a t-stat (the lab gives none)
        "chain_rows": len(chain), "chain_t": sum(1 for r in chain if r.get("t") is not None),   # chain-grade rows, which do carry a t-stat
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


def top_rows(d: dict, min_n: int = GATE_N, top: int = 15) -> list:
    """Stats page: strongest detector x timeframe rows (side 'all') with n >= min_n, by net avg R, with the gate verdict."""
    rows = [r for r in _detector_rows(d) if r.get("side") == "all" and r.get("tf") != "all" and r["n"] >= min_n]
    rows.sort(key=net, reverse=True)
    return [{"key": r["key"], "tf": r["tf"], "school": r.get("school"), "n": r["n"], "win": r.get("win"), "avgR": r["avgR"],
             "net": net(r), "vs_random": round(r["avgR"] - (r.get("base_avgR") or 0.0), 3), "t": r.get("t"),
             "gate": passes_gate(r)} for r in rows[:top]]


LAB_TF = {"1m": "1m", "3m": "1m", "5m": "15m", "13m": "15m", "15m": "15m", "30m": "1h", "1h": "1h", "2h": "1h", "3h": "4h", "4h": "4h",
          "6h": "4h", "7h": "4h", "8h": "4h", "12h": "1d", "1d": "1d", "3d": "1d", "1w": "1d", "1mo": "1d"}


def evidence(d: dict, key: str, tf: str) -> dict | None:
    """Radar card line: the lab row of one detector on the chart's timeframe (nearest lab timeframe), else its all-timeframe row."""
    rows = {(r["key"], r.get("tf")): r for r in _detector_rows(d) if r.get("side") == "all"}
    a = rows.get((key, "all"))
    r = rows.get((key, LAB_TF.get(tf, tf))) or a
    if not r:
        return None
    return {"key": key, "tf": r["tf"], "n": r["n"], "net": net(r), "gate": passes_gate(r),
            "off": bool(a) and a["n"] >= OFF_MIN_N and a["avgR"] <= OFF_R}


def detector_card(d: dict, key: str) -> dict:
    """Technical Office > Detector analysis: every lab row of one detector (per timeframe and side), its best timeframe,
    OFF status and which trading styles it belongs to."""
    rows = [r for r in _detector_rows(d) if r["key"] == key]
    per_tf = [r for r in rows if r.get("side") == "all" and r.get("tf") != "all"]
    a = next((r for r in rows if r.get("side") == "all" and r.get("tf") == "all"), None)
    big = [r for r in per_tf if r["n"] >= GATE_N]
    best = max(big or per_tf, key=net) if per_tf else None
    fmt = lambda r: {"tf": r["tf"], "side": r.get("side"), "n": r["n"], "win": r.get("win"), "avgR": r["avgR"], "net": net(r),
                     "vs_random": round(r["avgR"] - (r.get("base_avgR") or 0.0), 3), "t": r.get("t"), "gate": passes_gate(r)}
    return {"key": key, "school": (rows[0].get("school") if rows else None), "rows": [fmt(r) for r in rows],
            "all": fmt(a) if a else None, "best": fmt(best) if best else None, "best_is_evidence_size": bool(big),
            "off": bool(a) and a["n"] >= OFF_MIN_N and a["avgR"] <= OFF_R,
            "styles": [s for s, tfs in STYLES if any(r["tf"] in tfs for r in per_tf)]}


def detector_keys(d: dict) -> list:
    return sorted({r["key"] for r in _detector_rows(d)})


def lab_avg(d: dict) -> float | None:
    """Trade-weighted avg R of every detector x timeframe row (side 'all'): the backtest side of 'live vs backtest'."""
    rows = pooled(d, "tf")
    n = sum(r["n"] for r in rows)
    return round(sum(r["n"] * r["avgR"] for r in rows) / n, 3) if n else None


def journal_kpis(rs) -> dict:
    """KPIs of closed trades in R: n, win rate, avg R, net (after 0.1R), profit factor, max drawdown in R, t-stat."""
    rs = [float(x) for x in rs if x == x]   # drops NaN
    n = len(rs)
    if not n:
        return {"n": 0}
    avg = sum(rs) / n
    gain, loss = sum(x for x in rs if x > 0), -sum(x for x in rs if x < 0)
    eq = peak = dd = 0.0
    for x in rs:
        eq += x; peak = max(peak, eq); dd = min(dd, eq - peak)
    sd = (sum((x - avg) ** 2 for x in rs) / (n - 1)) ** 0.5 if n > 1 else 0.0
    return {"n": n, "win": round(sum(x > 0 for x in rs) / n, 3), "avgR": round(avg, 3), "net": round(avg - COST_R, 3),
            "pf": round(gain / loss, 2) if loss else None, "maxdd": round(dd, 2), "total": round(sum(rs), 2),
            "t": round(avg / (sd / n ** 0.5), 2) if sd else None}


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
