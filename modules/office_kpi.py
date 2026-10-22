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
