"""Task 5 (CLAUDE_TASKS.md): reproducible 2.6 report from one CSV + its manifest (dataset.py). H1 and H2 kept apart.

python3 report.py FILE.csv FILE.csv.manifest.json [--horizon 40] [--key 20] [--out report.md] [--reveal-test] [--neighbourhood]

Every number comes from the file whose checksum the manifest records; cost = manifest cost_per_event (price units
per filled event). The final 20 % (test) stays locked unless --reveal-test (owner decision). Research only.
"""
import argparse
import json
import sys
from pathlib import Path

from dataset import verify
from evaluation import evaluate, neighbourhood
from event_study import RATIOS, confirmed_pivots, make_legs, run_event_study
from h2_liquidity import run_h2

MIN_EVIDENCE_N = 30


def _f(x, nd=4):
    return "-" if x is None else f"{x:+.{nd}f}" if isinstance(x, float) else str(x)


def _median(xs):
    if not xs:
        return None
    s = sorted(xs); m = len(s) // 2
    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2


def h1_candidates(bars, left=3, right=3):
    """Legs whose anchors are known before the last bar = resting limits placed (per ratio); touch rate denominator."""
    pivots = confirmed_pivots(bars, left, right)
    return sum(1 for _side, s, e, span in make_legs(pivots) if span > 0 and max(s.known_at, e.known_at) < len(bars) - 1)


def describe(events, key):
    """Per ratio x side: n, positive % at `key`, median MFE / MAE (leg units), mean bars to fill. Descriptive only."""
    rows = []
    for ratio in sorted({e.ratio for e in events}):
        for side in ("BUY", "SELL", "all"):
            g = [e for e in events if e.ratio == ratio and (side == "all" or e.side == side)]
            if not g:
                continue
            vals = [e.returns_leg[key] for e in g if key in e.returns_leg]
            rows.append({"ratio": ratio, "side": side, "n": len(g),
                         "pos_pct": round(100 * sum(v > 0 for v in vals) / len(vals), 1) if vals else None,
                         "mfe": _median([e.mfe_leg for e in g]), "mae": _median([e.mae_leg for e in g]),
                         "bars_to_fill": round(sum(e.bars_to_fill for e in g) / len(g), 1)})
    return rows


def _family(title, events, ev, key, touch=None):
    L = [f"## {title}", ""]
    if touch is not None:
        L += [f"Resting limits placed per ratio: {touch}. Touch rate = filled / placed (per ratio below).", ""]
    if not events:
        return L + ["No filled events.", ""]
    L += ["### Descriptive (all filled events, overlapping windows included)", "",
          f"| ratio | side | n | touch % | positive % @{key} | median MFE | median MAE | mean bars to fill |", "|---|---|---|---|---|---|---|---|"]
    for r in describe(events, key):
        tr = round(100 * r["n"] / touch, 1) if touch and r["side"] == "all" else "-"
        L.append(f"| {r['ratio']:.5g} | {r['side']} | {r['n']} | {tr} | {_f(r['pos_pct'])} | {_f(r['mfe'], 3)} | {_f(r['mae'], 3)} | {r['bars_to_fill']} |")
    L += ["", f"### Evaluation (de-clustered, purged 60/20/20 by date, matched random-timing controls, block-bootstrap 95 % CI; return @{key} bars in leg units after cost)", "",
          "| ratio | raw n | de-clustered n | purged | segment | n | mean | 95 % CI | control mean | vs control | evidence? |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for ratio, row in ev["ratios"].items():
        for seg in ("train", "validation", "test"):
            c = row.get(seg, {})
            if c.get("locked"):
                L.append(f"| {float(ratio):.5g} | {row['n_raw']} | {row['n_declustered']} | {row['purged']} | test | {c['n']} | locked | - | - | - | - |")
                continue
            ci = c.get("ci"); ci_s = "-" if not ci else f"{ci[0]:+.4f} .. {ci[1]:+.4f}"
            evid = "not evidence (n < %d)" % MIN_EVIDENCE_N if c.get("n", 0) < MIN_EVIDENCE_N else ("CI above 0" if ci and ci[0] > 0 else "no")
            L.append(f"| {float(ratio):.5g} | {row['n_raw']} | {row['n_declustered']} | {row['purged']} | {seg} | {c.get('n', 0)} | {_f(c.get('mean'))} | {ci_s} | {_f(c.get('control_mean'))} | {_f(c.get('vs_control'))} | {evid} |")
    return L + [""]


def build(csv_path, manifest, horizon=40, key="20", reveal_test=False, seed=0, with_neighbourhood=False):
    bars = verify(csv_path, manifest)
    cost = float(manifest["cost_per_event"])
    h1, _ = run_event_study(bars, RATIOS, horizon_bars=horizon, cost=cost)
    h2, _ = run_h2(bars, RATIOS, horizon_bars=horizon, cost=cost)
    e1 = evaluate(bars, h1, horizon, cost, key, reveal_test=reveal_test, seed=seed)
    e2 = evaluate(bars, h2, horizon, cost, key, reveal_test=reveal_test, seed=seed)
    m = manifest
    L = ["# 2.6 research report (research only - not a trading signal)", "",
         f"- Data: `{m['file']}` sha256 `{m['sha256'][:16]}` · {m['provider']} · {m['symbol']} ({m['asset_class']}) · {m['timeframe']} · {m['bars']} bars · {m['utc_first']} .. {m['utc_last']}",
         f"- Gaps: {m['gaps']['weekend_closes']} weekend closes, {m['gaps']['other_gaps']} other",
         f"- Cost per filled event: {cost} price units ({json.dumps(m['costs'])}) - assumption from the manifest, not measured fills",
         f"- Horizon {horizon} bars, headline return @{key} bars; ratios {', '.join(f'{r:.5g}' for r in RATIOS)} (picking the best one is a multiple test)",
         f"- Test segment: {'REVEALED (owner decision)' if reveal_test else 'locked'}",
         "- Creator SL / TP / session rules: UNKNOWN - returns are forward price moves in leg units, not a P&L backtest.", ""]
    L += _family("H1 retracement", h1, e1, key, touch=h1_candidates(bars))
    L += _family("H2 liquidity projection (rules are assumptions)", h2, e2, key)
    if with_neighbourhood:
        for title, run in (("H1", run_event_study), ("H2", run_h2)):
            nb = neighbourhood(bars, run, cost, key, horizon, seed=seed)
            share = "-" if nb["positive_share"] is None else f"{100 * nb['positive_share']:.0f} %"
            L += [f"## {title} parameter neighbourhood (ratio 2.6; train / validation only, test untouched)", "",
                  f"Settings with validation n >= 30: {nb['settings_with_n30']}; positive in {share} of them. A stable effect is positive across most settings.", "",
                  "| pivot window | wait bars | de-clustered n | train mean | validation n | validation mean |", "|---|---|---|---|---|---|"]
            L += [f"| {r['pivot']} | {r['wait_bars']} | {r['n_declustered']} | {_f(r['train_mean'])} | {r['validation_n']} | {_f(r['validation_mean'])} |" for r in nb["rows"]]
            L += [""]
    L += [f"n < {MIN_EVIDENCE_N} in a cell = not evidence. No edge claim unless the validation CI is above 0 AND above the control, then confirmed once on the locked test."]
    return "\n".join(L) + "\n", {"h1": e1, "h2": e2}


def main(argv=None):
    p = argparse.ArgumentParser(description="2.6 report from CSV + manifest")
    p.add_argument("csv"); p.add_argument("manifest"); p.add_argument("--horizon", type=int, default=40); p.add_argument("--key", default="20")
    p.add_argument("--out"); p.add_argument("--reveal-test", action="store_true"); p.add_argument("--neighbourhood", action="store_true")
    a = p.parse_args(argv)
    md, _ = build(a.csv, json.loads(Path(a.manifest).read_text(encoding="utf-8")), a.horizon, a.key, a.reveal_test, with_neighbourhood=a.neighbourhood)
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
