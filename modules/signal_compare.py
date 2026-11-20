"""Compare every measured signal family side by side, on the same real-candle lab run.

Reads data/strategy_lab.json (written by modules/strategy_lab.py from real candles). Only the pooled rows are used:
tf == "all" and side == "all", one row per detector. Nothing is fetched and nothing is re-optimised here.

The verdict is the OWNER's bar, stricter than the lab's own 'edge' flag:
  n >= 100, t > 3, average R above 0 in BOTH halves (in-sample and out-of-sample), AND still above 0 after costs (net).
The lab's 'edge' column does not subtract costs, so a detector can show YES there and still fail here (fvg does).

Run:  python3 -m modules.signal_compare            (prints the table, sorted by net R)
      python3 -m modules.signal_compare --json     (the same rows as JSON, for a page or an artifact)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1] / "data" / "strategy_lab.json"
MIN_N = 100
MIN_T = 3.0

# one colour per school, so the chart / table reads at a glance
SCHOOL_COLOUR = {
    "Trend (MA)": "#4da3ff", "Trend (hedge fund)": "#1f6feb",
    "Harmonic: Gartley": "#f0b429", "Harmonic: Bat": "#f59e0b", "Harmonic: Butterfly": "#e0a526",
    "Harmonic: Crab": "#d97706", "Harmonic: Cypher": "#b45309",
    "Elliott wave": "#a371f7", "Fibonacci": "#8957e5",
    "SMC / ICT": "#2ea043", "Liquidity": "#3fb950", "Wyckoff": "#56d364",
    "Momentum / divergence": "#db61a2", "Price action": "#ff7b72",
    "Levels / breakouts": "#79c0ff", "Time (sessions)": "#58a6ff",
    "Intermarket (SMT)": "#6e7681", "Chart patterns (range)": "#8b949e",
}
DEFAULT_COLOUR = "#8b949e"
COST_R = 0.1          # the lab's planning estimate: 0.1 R per trade (same as the 'net' column in STRATEGY_LAB.md)


def _num(x):
    return None if x is None else float(x)


def verdict(row: dict) -> bool:
    """The owner's bar (see module docstring). Missing numbers never pass."""
    n, t = row.get("n") or 0, _num(row.get("t"))
    oos, ins, net = _num(row.get("oos_avgR")), _num(row.get("is_avgR")), net_r(row)
    if None in (t, oos, ins, net):
        return False
    return n >= MIN_N and t > MIN_T and oos > 0 and ins > 0 and net > 0


def net_r(row: dict):
    """avg R after the planning cost. Pooled rows carry no 'net' field, so it is avgR - 0.1 (the lab's own rule)."""
    if row.get("net") is not None:
        return float(row["net"])
    avg = _num(row.get("avgR"))
    return None if avg is None else round(avg - COST_R, 3)


def compare(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        if r.get("tf") != "all" or r.get("side") != "all":
            continue
        out.append({
            "key": r["key"], "school": r["school"], "colour": SCHOOL_COLOUR.get(r["school"], DEFAULT_COLOUR),
            "n": r["n"], "win": r.get("win"), "avgR": r.get("avgR"), "net": net_r(r),
            "base_avgR": r.get("base_avgR"), "t": r.get("t"),
            "is_avgR": r.get("is_avgR"), "oos_avgR": r.get("oos_avgR"),
            "lab_edge": bool(r.get("edge")), "owner_pass": verdict(r),
        })
    out.sort(key=lambda x: (x["net"] is None, -(x["net"] or 0)))
    return out


def load(path: Path = LAB) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))["rows"]


def table(rows: list[dict]) -> str:
    head = ["key", "school", "n", "win %", "avg R", "net R", "t", "IS R", "OOS R", "lab edge", "owner bar"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        lines.append("| " + " | ".join([
            r["key"], r["school"], str(r["n"]), str(r["win"]), str(r["avgR"]), str(r["net"]), str(r["t"]),
            str(r["is_avgR"]), str(r["oos_avgR"]), "YES" if r["lab_edge"] else "", "PASS" if r["owner_pass"] else "no",
        ]) + " |")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    rows = compare(load())
    if "--json" in argv:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        print(table(rows))
        passed = [r["key"] for r in rows if r["owner_pass"]]
        print(f"\n{len(rows)} detectors · owner bar passed by: {', '.join(passed) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
