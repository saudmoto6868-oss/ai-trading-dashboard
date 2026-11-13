#!/usr/bin/env python3
"""Causal event-study harness for two separate 2.6 hypotheses.

This module currently implements H1 (retracement) only. H2 (liquidity
projection) is deliberately not inferred from H1 and remains unimplemented.
A touched limit level is a fill assumption, not proof of executable fills.
"""
import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

RATIOS = (2.5, 2.6, 2.618, 1 / 0.382, 2.7)
HORIZONS = (5, 10, 20, 40)


@dataclass
class Bar:
    dt: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass
class Pivot:
    idx: int
    kind: str
    price: float
    known_at: int


@dataclass
class Event:
    ratio: float
    side: str
    anchor_start: str
    anchor_end: str
    confirmation_time: str
    entry_time: str
    entry: float
    leg_range: float
    bars_to_fill: int
    mfe_leg: float
    mae_leg: float
    returns_leg: dict


def _parse_timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid ISO-8601 datetime: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"Timestamp must include a timezone offset: {value!r}")
    return parsed


def load_bars(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"datetime", "open", "high", "low", "close"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("CSV requires datetime,open,high,low,close")
        for line_number, row in enumerate(reader, start=2):
            try:
                dt = str(row["datetime"]).strip()
                _parse_timestamp(dt)
                bar = Bar(
                    dt, float(row["open"]), float(row["high"]),
                    float(row["low"]), float(row["close"]),
                    float(row.get("volume") or 0),
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid data on CSV line {line_number}: {exc}") from exc
            values = (bar.open, bar.high, bar.low, bar.close, bar.volume)
            if not all(map(lambda x: x == x and abs(x) != float("inf"), values)):
                raise ValueError(f"Non-finite OHLCV value at {bar.dt}")
            if min(bar.open, bar.high, bar.low, bar.close) <= 0 or bar.volume < 0:
                raise ValueError(f"Non-positive price or negative volume at {bar.dt}")
            if not (bar.low <= min(bar.open, bar.close)
                    <= max(bar.open, bar.close) <= bar.high):
                raise ValueError("Invalid OHLC at " + bar.dt)
            rows.append(bar)

    if len(rows) < 100:
        raise ValueError("At least 100 bars required")
    timestamps = [_parse_timestamp(bar.dt) for bar in rows]
    if any(timestamps[i] >= timestamps[i + 1] for i in range(len(rows) - 1)):
        raise ValueError("Rows must have strictly increasing timestamps")
    return rows


def confirmed_pivots(bars, left=3, right=3):
    """Return unique local extrema with the first observable index.

    No retrospective same-side pivot replacement is performed: doing so can
    select a later, more extreme pivot and rewrite an earlier swing.
    """
    if left < 1 or right < 1:
        raise ValueError("left and right must be >= 1")
    out = []
    for idx in range(left, len(bars) - right):
        window = bars[idx - left:idx + right + 1]
        high, low = bars[idx].high, bars[idx].low
        is_high = high == max(bar.high for bar in window) and sum(
            bar.high == high for bar in window
        ) == 1
        is_low = low == min(bar.low for bar in window) and sum(
            bar.low == low for bar in window
        ) == 1
        # OHLC bars do not reveal whether the high or low occurred first.
        # Exclude dual-extreme bars rather than inventing an intrabar sequence.
        if is_high and is_low:
            continue
        if is_high:
            out.append(Pivot(idx, "H", high, idx + right))
        if is_low:
            out.append(Pivot(idx, "L", low, idx + right))
    out.sort(key=lambda pivot: (pivot.known_at, pivot.idx, pivot.kind))
    return out


def make_legs(pivots):
    """Yield adjacent opposite-kind pivots; same-kind pairs are ignored."""
    for first, second in zip(pivots, pivots[1:]):
        if first.kind == "L" and second.kind == "H":
            yield "BUY", first, second, second.price - first.price
        elif first.kind == "H" and second.kind == "L":
            yield "SELL", first, second, first.price - second.price


def _fill_price(bar, side, limit_price):
    # Conservative limit-order gap handling: a gap through the limit fills
    # at the opening price (price improvement), otherwise at the limit.
    if side == "BUY":
        return min(limit_price, bar.open)
    return max(limit_price, bar.open)


def run_event_study(bars, ratios=RATIOS, left=3, right=3, wait_bars=80,
                    horizon_bars=40, cost=0.0):
    if not bars:
        raise ValueError("bars cannot be empty")
    if min(left, right, wait_bars, horizon_bars) < 1:
        raise ValueError("left, right, wait_bars and horizon_bars must be >= 1")
    if not math.isfinite(cost) or cost < 0:
        raise ValueError("cost must be finite and >= 0")
    if not ratios or any(not math.isfinite(r) or r <= 0 for r in ratios):
        raise ValueError("ratios must be finite, positive and non-empty")

    pivots = confirmed_pivots(bars, left, right)
    events = []
    for side, start, end, span in make_legs(pivots):
        if span <= 0:
            continue
        known_at = max(start.known_at, end.known_at)
        if known_at >= len(bars) - 1:
            continue
        for ratio in ratios:
            level = end.price - span / ratio if side == "BUY" else end.price + span / ratio
            stop = min(len(bars) - 1, known_at + wait_bars)
            fill_idx = None
            fill = None
            for idx in range(known_at + 1, stop + 1):
                bar = bars[idx]
                if bar.low <= level <= bar.high:
                    fill_idx = idx
                    fill = _fill_price(bar, side, level)
                    break
            if fill_idx is None or fill_idx + horizon_bars >= len(bars):
                continue

            future = bars[fill_idx + 1:fill_idx + horizon_bars + 1]
            sign = 1 if side == "BUY" else -1
            mfe = max((bar.high - fill) * sign for bar in future)
            mae = min((bar.low - fill) * sign for bar in future)
            returns = {
                str(horizon): round(
                    ((bars[fill_idx + horizon].close - fill) * sign - cost) / span, 8
                )
                for horizon in HORIZONS
                if horizon <= horizon_bars and fill_idx + horizon < len(bars)
            }
            events.append(Event(
                float(ratio), side, bars[start.idx].dt, bars[end.idx].dt,
                bars[known_at].dt, bars[fill_idx].dt, fill, span,
                fill_idx - known_at, mfe / span, mae / span, returns,
            ))

    events.sort(key=lambda event: (event.entry_time, event.ratio, event.side))
    return events, pivots


def _median(values):
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return round(ordered[middle], 5)
    return round((ordered[middle - 1] + ordered[middle]) / 2, 5)


def summarize(events):
    """Descriptive metrics only; event-tail split is not an OOS validation."""
    summary = {}
    for ratio in sorted({event.ratio for event in events}):
        group = sorted(
            (event for event in events if event.ratio == ratio),
            key=lambda event: event.entry_time,
        )
        split = int(len(group) * 0.7)
        partitions = (
            ("all", group),
            ("early_70pct_descriptive", group[:split]),
            ("late_30pct_descriptive_not_oos", group[split:]),
        )
        for label, items in partitions:
            values = [event.returns_leg["20"] for event in items
                      if "20" in event.returns_leg]
            normalized_mfe = [event.mfe_leg for event in items]
            normalized_mae = [event.mae_leg for event in items]
            summary.setdefault(str(ratio), {})[label] = {
                "n_filled": len(items),
                "n_20bar": len(values),
                "positive_20bar_pct": (
                    round(100 * sum(value > 0 for value in values) / len(values), 2)
                    if values else None
                ),
                "mean_20bar_return_leg_units": (
                    round(sum(values) / len(values), 5) if values else None
                ),
                "median_mfe_leg": _median(normalized_mfe),
                "median_mae_leg": _median(normalized_mae),
                "mean_bars_to_fill": (
                    round(sum(event.bars_to_fill for event in items) / len(items), 2)
                    if items else None
                ),
            }
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    parser.add_argument("--left", type=int, default=3)
    parser.add_argument("--right", type=int, default=3)
    parser.add_argument("--wait-bars", type=int, default=80)
    parser.add_argument("--horizon-bars", type=int, default=40)
    parser.add_argument("--cost", type=float, default=0.0,
                        help="absolute price cost per filled event (not pips)")
    parser.add_argument("--out", default="research/strategies/2.6/output")
    args = parser.parse_args()
    if (min(args.left, args.right, args.wait_bars, args.horizon_bars) < 1
            or not math.isfinite(args.cost) or args.cost < 0):
        parser.error("invalid parameters")

    bars = load_bars(args.csv)
    events, pivots = run_event_study(
        bars, left=args.left, right=args.right,
        wait_bars=args.wait_bars, horizon_bars=args.horizon_bars,
        cost=args.cost,
    )
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    fields = list(Event.__dataclass_fields__)
    with (output / "events.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for event in events:
            writer.writerow(asdict(event))

    report = {
        "hypothesis": "H1_retracement_only",
        "bars": len(bars),
        "pivots": len(pivots),
        "events": len(events),
        "parameters": {
            "ratios": list(RATIOS), "left": args.left, "right": args.right,
            "wait_bars": args.wait_bars, "horizon_bars": args.horizon_bars,
            "cost_absolute_price_per_fill": args.cost,
        },
        "metrics": summarize(events),
        "limitations": [
            "H2 liquidity projection is not implemented in this harness",
            "touch-based limit fill is a simulation assumption, not execution proof",
            "no verified stop-loss, take-profit, sizing or full P&L model",
            "70/30 event-tail summaries are descriptive, not out-of-sample validation",
            "overlapping events and dependence require separate statistical treatment",
            "no broker spread, commission or slippage decomposition unless supplied in cost",
        ],
    }
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"bars": len(bars), "pivots": len(pivots), "events": len(events)}, indent=2))


if __name__ == "__main__":
    main()
