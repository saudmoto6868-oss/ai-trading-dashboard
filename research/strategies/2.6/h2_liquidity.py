#!/usr/bin/env python3
"""H2 - 2.6 liquidity projection event builder (separate from H1).

The creator's exact rules are still UNKNOWN. Every rule below is an explicit
research assumption, causal by construction (nothing is used before the bar
that reveals it has closed):

1. Pool: two adjacent same-kind confirmed pivots (EQH or EQL) whose prices are
   within eq_tol (fraction of price) and at most pool_bars apart, with no bar
   between them trading beyond the pool. Level = the more extreme of the two.
   The pool is known when the second pivot is confirmed.
2. Sweep: the first later bar (within sweep_bars) whose wick trades through the
   level and closes back inside (EQH: high > level and close < level). A close
   at or beyond the level first is a breakout: the pool is consumed, no event.
3. Projection leg: the latest completed leg in the reversal direction
   (EQH -> SELL -> an H->L leg; EQL -> BUY -> an L->H leg) whose pivots are
   both confirmed by the sweep bar.
4. Zone: EQH -> level + span / ratio (sell above the swept highs);
   EQL -> level - span / ratio. A limit is placed after the sweep bar closes and
   fills when touched within wait_bars (a gap through it fills at the open).

Run: python3 research/strategies/2.6/h2_liquidity.py bars.csv --out DIR
"""
import argparse
import csv
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from event_study import (  # noqa: E402
    RATIOS, confirmed_pivots, find_fill, load_bars, make_legs, measure, summarize,
)


@dataclass
class H2Event:
    ratio: float
    side: str
    pool_kind: str
    pool_level: float
    pool_first: str
    pool_second: str
    sweep_time: str
    leg_start: str
    leg_end: str
    entry_time: str
    entry: float
    leg_range: float
    bars_to_fill: int
    mfe_leg: float
    mae_leg: float
    returns_leg: dict


def liquidity_pools(bars, pivots, eq_tol=0.0005, pool_bars=100):
    """Equal-high / equal-low pools as (kind, level, first, second, known_at)."""
    pools = []
    for kind in ("H", "L"):
        same = sorted((p for p in pivots if p.kind == kind), key=lambda p: p.idx)
        for first, second in zip(same, same[1:]):
            if second.idx - first.idx > pool_bars:
                continue
            if abs(first.price - second.price) > eq_tol * max(first.price, second.price):
                continue
            between = bars[first.idx + 1:second.idx]
            if kind == "H":
                level = max(first.price, second.price)
                if any(bar.high >= level for bar in between):
                    continue
            else:
                level = min(first.price, second.price)
                if any(bar.low <= level for bar in between):
                    continue
            pools.append((kind, level, first, second, max(first.known_at, second.known_at)))
    pools.sort(key=lambda pool: (pool[4], pool[0]))
    return pools


def find_sweep(bars, kind, level, known_at, sweep_bars):
    """Index of the sweep bar, or None (breakout or no sweep within sweep_bars)."""
    for idx in range(known_at + 1, min(len(bars), known_at + 1 + sweep_bars)):
        bar = bars[idx]
        if kind == "H":
            if bar.close >= level:
                return None
            if bar.high > level:
                return idx
        else:
            if bar.close <= level:
                return None
            if bar.low < level:
                return idx
    return None


def run_h2(bars, ratios=RATIOS, left=3, right=3, eq_tol=0.0005, pool_bars=100,
           sweep_bars=200, wait_bars=80, horizon_bars=40, cost=0.0):
    if not bars:
        raise ValueError("bars cannot be empty")
    if min(left, right, pool_bars, sweep_bars, wait_bars, horizon_bars) < 1:
        raise ValueError("bar-count parameters must be >= 1")
    if not math.isfinite(eq_tol) or eq_tol < 0:
        raise ValueError("eq_tol must be finite and >= 0")
    if not math.isfinite(cost) or cost < 0:
        raise ValueError("cost must be finite and >= 0")
    if not ratios or any(not math.isfinite(r) or r <= 0 for r in ratios):
        raise ValueError("ratios must be finite, positive and non-empty")

    pivots = confirmed_pivots(bars, left, right)
    legs = [(side, a, b, span, max(a.known_at, b.known_at))
            for side, a, b, span in make_legs(pivots) if span > 0]
    pools = liquidity_pools(bars, pivots, eq_tol, pool_bars)
    events, used_sweeps = [], set()
    for kind, level, first, second, known_at in pools:
        sweep = find_sweep(bars, kind, level, known_at, sweep_bars)
        if sweep is None or (kind, sweep) in used_sweeps:
            continue
        used_sweeps.add((kind, sweep))
        side = "SELL" if kind == "H" else "BUY"
        prior = [leg for leg in legs if leg[0] == side and leg[4] <= sweep]
        if not prior:
            continue
        _, a, b, span, _ = max(prior, key=lambda leg: (leg[4], leg[2].idx))
        last = min(len(bars) - 1, sweep + wait_bars)
        for ratio in ratios:
            zone = level + span / ratio if side == "SELL" else level - span / ratio
            fill_idx, fill = find_fill(bars, side, zone, sweep + 1, last)
            if fill_idx is None or fill_idx + horizon_bars >= len(bars):
                continue
            mfe, mae, returns = measure(bars, fill_idx, fill, side, span, horizon_bars, cost)
            events.append(H2Event(
                float(ratio), side, kind, level, bars[first.idx].dt, bars[second.idx].dt,
                bars[sweep].dt, bars[a.idx].dt, bars[b.idx].dt, bars[fill_idx].dt,
                fill, span, fill_idx - sweep, mfe, mae, returns,
            ))
    events.sort(key=lambda event: (event.entry_time, event.ratio, event.side))
    return events, pools


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("csv")
    parser.add_argument("--left", type=int, default=3)
    parser.add_argument("--right", type=int, default=3)
    parser.add_argument("--eq-tol", type=float, default=0.0005,
                        help="max EQH/EQL price gap as a fraction of price")
    parser.add_argument("--pool-bars", type=int, default=100)
    parser.add_argument("--sweep-bars", type=int, default=200)
    parser.add_argument("--wait-bars", type=int, default=80)
    parser.add_argument("--horizon-bars", type=int, default=40)
    parser.add_argument("--cost", type=float, default=0.0,
                        help="absolute price cost per filled event (not pips)")
    parser.add_argument("--out", default="research/strategies/2.6/output")
    args = parser.parse_args()

    bars = load_bars(args.csv)
    try:
        events, pools = run_h2(
            bars, left=args.left, right=args.right, eq_tol=args.eq_tol,
            pool_bars=args.pool_bars, sweep_bars=args.sweep_bars,
            wait_bars=args.wait_bars, horizon_bars=args.horizon_bars, cost=args.cost,
        )
    except ValueError as exc:
        parser.error(str(exc))
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    with (output / "events_h2.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(H2Event.__dataclass_fields__))
        writer.writeheader()
        for event in events:
            writer.writerow(asdict(event))
    report = {
        "hypothesis": "H2_liquidity_projection_only",
        "bars": len(bars),
        "pools": len(pools),
        "events": len(events),
        "parameters": {k: v for k, v in vars(args).items() if k not in ("csv", "out")},
        "metrics": summarize(events),
        "limitations": [
            "pool, sweep, leg and zone rules are research assumptions; creator rules UNKNOWN",
            "touch-based limit fill is a simulation assumption, not execution proof",
            "no verified stop-loss, take-profit, sizing or full P&L model",
            "70/30 event-tail summaries are descriptive, not out-of-sample validation",
            "one sweep can serve several ratios; events are dependent",
        ],
    }
    (output / "report_h2.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"bars": len(bars), "pools": len(pools), "events": len(events)}, indent=2))


if __name__ == "__main__":
    main()
