"""
Item 25 — A+++ Pipeline Report (step 2)
Reads data/strategy_lab.json and prints a ranked summary:
  - tier distribution
  - IS vs OOS gap (overfit flag)
  - top keys by avgR (with evidence gate)
  - chain layer breakdown (when grade/layer fields exist after real lab run)

Usage:
    python -m modules.pipeline_report
    python -m modules.pipeline_report --json   # machine-readable
    python -m modules.pipeline_report --md     # markdown for docs
"""

import json
import sys
import argparse
from pathlib import Path

LAB_PATH = Path(__file__).parent.parent / "data" / "strategy_lab.json"
MIN_N = 30
GATE_N = 100
GATE_T = 3.0
OFF_MIN_N = 300
OFF_MAX_R = -0.06
GAP_WARN = 0.05  # IS-OOS gap > 0.05R => overfit warning

TIER_ORDER = ["edge", "positive", "neutral", "negative", "off", "weak"]


def _tier(row: dict) -> str:
    n, avgR, edge = row.get("n", 0), row.get("avgR", 0), row.get("edge", "")
    if edge == "off" or (n >= OFF_MIN_N and avgR <= OFF_MAX_R):
        return "off"
    if n < MIN_N:
        return "weak"
    if edge == "edge":
        return "edge"
    if avgR > 0.05:
        return "positive"
    if avgR < -0.03:
        return "negative"
    return "neutral"


def _gap_flag(row: dict) -> str:
    is_r = row.get("is_avgR")
    oos_r = row.get("oos_avgR")
    if is_r is None or oos_r is None:
        return ""
    gap = abs(is_r - oos_r)
    return "⚠️ overfit" if gap > GAP_WARN else ""


def load_rows(side: str = "all") -> list:
    try:
        data = json.loads(LAB_PATH.read_text())
        rows = data.get("rows", data) if isinstance(data, dict) else data
        if side:
            rows = [r for r in rows if r.get("side") == side]
        return rows
    except Exception as e:
        print(f"ERROR loading lab: {e}", file=sys.stderr)
        return []


def tier_distribution(rows: list) -> dict:
    counts: dict = {t: 0 for t in TIER_ORDER}
    for r in rows:
        counts[_tier(r)] += 1
    return counts


def top_by_avgr(rows: list, n_top: int = 20) -> list:
    """Rows passing MIN_N gate, sorted by avgR desc."""
    eligible = [r for r in rows if r.get("n", 0) >= MIN_N]
    return sorted(eligible, key=lambda r: r.get("avgR", -99), reverse=True)[:n_top]


def gate_passed(rows: list) -> list:
    """Rows passing the strict A+++ gate: n>=100, t>3, avgR>0 in both IS and OOS."""
    out = []
    for r in rows:
        n = r.get("n", 0)
        t = r.get("t", 0)
        avgR = r.get("avgR", 0)
        is_r = r.get("is_avgR", 0) or 0
        oos_r = r.get("oos_avgR", 0) or 0
        if n >= GATE_N and t > GATE_T and avgR > 0 and is_r > 0 and oos_r > 0:
            out.append(r)
    return sorted(out, key=lambda r: r.get("avgR", 0), reverse=True)


def chain_breakdown(rows: list) -> dict:
    """Breakdown by grade/layer fields — only meaningful after real lab run."""
    layers = ["reg", "htf", "loc", "vol", "time"]
    result: dict = {"grades": {}, "layers": {}}
    for r in rows:
        g = r.get("grade")
        if g:
            bucket = result["grades"].setdefault(g, {"n": 0, "avgR_sum": 0})
            bucket["n"] += 1
            bucket["avgR_sum"] += r.get("avgR", 0)
        for lyr in layers:
            if lyr in r:
                bucket = result["layers"].setdefault(lyr, {"with": 0, "without": 0,
                                                            "with_r": 0, "without_r": 0})
                if r[lyr]:
                    bucket["with"] += 1
                    bucket["with_r"] += r.get("avgR", 0)
                else:
                    bucket["without"] += 1
                    bucket["without_r"] += r.get("avgR", 0)
    # averages
    for g, d in result["grades"].items():
        d["avg_avgR"] = round(d["avgR_sum"] / d["n"], 4) if d["n"] else 0
    for lyr, d in result["layers"].items():
        d["avg_with"] = round(d["with_r"] / d["with"], 4) if d["with"] else None
        d["avg_without"] = round(d["without_r"] / d["without"], 4) if d["without"] else None
    return result


def fmt_r(v) -> str:
    if v is None:
        return "—"
    return f"+{v:.3f}R" if v >= 0 else f"{v:.3f}R"


def report_text(rows: list) -> str:
    lines = ["# A+++ Pipeline Report", f"lab rows (side=all): {len(rows)}", ""]

    # tier distribution
    dist = tier_distribution(rows)
    lines.append("## Tier distribution")
    icons = {"edge": "⭐", "positive": "✅", "neutral": "➖",
              "negative": "⚠️", "off": "🚫", "weak": "🔘"}
    for t in TIER_ORDER:
        lines.append(f"  {icons[t]} {t}: {dist[t]}")
    lines.append("")

    # gate passed
    passed = gate_passed(rows)
    lines.append(f"## Strict gate (n≥{GATE_N}, t>{GATE_T}, avgR>0 IS+OOS): {len(passed)} keys")
    if passed:
        lines.append("| key | tf | n | avgR | IS | OOS | gap |")
        lines.append("|-----|-----|---|------|-----|-----|-----|")
        for r in passed:
            gap = _gap_flag(r)
            lines.append(
                f"| {r['key']} | {r.get('tf','')} | {r.get('n','')} "
                f"| {fmt_r(r.get('avgR'))} | {fmt_r(r.get('is_avgR'))} "
                f"| {fmt_r(r.get('oos_avgR'))} | {gap} |"
            )
    else:
        lines.append("  _(no key passes the strict gate yet — lab run on real candles needed)_")
    lines.append("")

    # top 10 by avgR (with MIN_N)
    top = top_by_avgr(rows, 10)
    lines.append(f"## Top 10 by avgR (n≥{MIN_N})")
    lines.append("| key | tf | n | avgR | IS | OOS | gap |")
    lines.append("|-----|-----|---|------|-----|-----|-----|")
    for r in top:
        gap = _gap_flag(r)
        lines.append(
            f"| {r['key']} | {r.get('tf','')} | {r.get('n','')} "
            f"| {fmt_r(r.get('avgR'))} | {fmt_r(r.get('is_avgR'))} "
            f"| {fmt_r(r.get('oos_avgR'))} | {gap} |"
        )
    lines.append("")

    # chain breakdown
    chain = chain_breakdown(rows)
    if chain["grades"]:
        lines.append("## Chain grades (A+++ / A+ / A / B / C)")
        for g in sorted(chain["grades"]):
            d = chain["grades"][g]
            lines.append(f"  {g}: n={d['n']}, avg_avgR={fmt_r(d['avg_avgR'])}")
        lines.append("")
    if chain["layers"]:
        lines.append("## Layer impact (with vs without)")
        for lyr, d in chain["layers"].items():
            lines.append(
                f"  {lyr}: with={fmt_r(d['avg_with'])} (n={d['with']})"
                f" | without={fmt_r(d['avg_without'])} (n={d['without']})"
            )
        lines.append("")
    else:
        lines.append("## Chain / layer data")
        lines.append("  _(not available — lab run with chain tagging needed)_")
        lines.append("")

    lines.append("> ⚠️ No costs modelled. Real results after spread/fee are worse.")
    lines.append("> Under n=30 = not evidence.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--md", action="store_true")
    args = parser.parse_args()

    rows = load_rows(side="all")
    if not rows:
        print("No rows loaded.")
        sys.exit(1)

    if args.json:
        out = {
            "n": len(rows),
            "tier_dist": tier_distribution(rows),
            "gate_passed": gate_passed(rows),
            "top10": top_by_avgr(rows, 10),
            "chain": chain_breakdown(rows),
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(report_text(rows))


if __name__ == "__main__":
    main()
