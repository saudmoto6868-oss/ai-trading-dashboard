"""Task 4 (CLAUDE_TASKS.md): evaluation protocol for 2.6 events (H1 `Event` or H2 `H2Event`; never pooled).

- decluster: per ratio, keep an event only if its entry bar is after the previous kept event's horizon ends
  (overlapping forward windows share the same price path and inflate n).
- matched controls: same side, same leg span, same horizon, entry at the open of a random bar from the same
  date-split segment, so "edge" is measured against random timing, not against zero.
- block bootstrap: CI of the mean with contiguous blocks (serial dependence between nearby events).
- date split 60/20/20 by bar index with a purge: an event whose forward window crosses a boundary is dropped.
  The final 20 % (test) stays locked: its numbers are only returned with reveal_test=True (owner decision).

Research only. Synthetic tests only so far; no real XAUUSD result, no edge claim.
"""
import math
import random

from event_study import measure

SPLITS = (0.6, 0.2, 0.2)


def _index(bars):
    return {bar.dt: i for i, bar in enumerate(bars)}


def decluster(events, bars, horizon_bars):
    """Per ratio and side-agnostic: drop events whose entry falls inside the previous kept event's forward window."""
    if horizon_bars < 1:
        raise ValueError("horizon_bars must be >= 1")
    idx = _index(bars)
    kept, last = [], {}
    for event in sorted(events, key=lambda e: (e.ratio, idx[e.entry_time])):
        i = idx[event.entry_time]
        if event.ratio in last and i <= last[event.ratio] + horizon_bars:
            continue
        kept.append(event)
        last[event.ratio] = i
    return kept


def split_bounds(n_bars, fracs=SPLITS):
    if len(fracs) != 3 or any(f <= 0 for f in fracs) or abs(sum(fracs) - 1) > 1e-9:
        raise ValueError("fracs must be three positive numbers summing to 1")
    a = int(n_bars * fracs[0]); b = int(n_bars * (fracs[0] + fracs[1]))
    return (0, a), (a, b), (b, n_bars)


def segment_of(i, horizon_bars, bounds):
    """Segment name for an entry at bar i, or None when its forward window crosses a boundary (purged)."""
    for name, (lo, hi) in zip(("train", "validation", "test"), bounds):
        if lo <= i < hi:
            return name if i + horizon_bars < hi else None
    return None


def block_bootstrap_ci(values, block=5, n_boot=2000, alpha=0.05, seed=0):
    """(low, high) percentile CI of the mean using circular contiguous blocks; None for fewer than 2 values."""
    n = len(values)
    if n < 2:
        return None
    if block < 1 or n_boot < 1 or not 0 < alpha < 1:
        raise ValueError("block and n_boot must be >= 1, 0 < alpha < 1")
    block = max(1, min(block, n // 2))   # a block as long as the sample would make every resample identical
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        sample = []
        while len(sample) < n:
            s = rng.randrange(n)
            sample.extend(values[(s + k) % n] for k in range(block))
        means.append(sum(sample[:n]) / n)
    means.sort()
    lo = means[int(math.floor(alpha / 2 * (n_boot - 1)))]
    hi = means[int(math.ceil((1 - alpha / 2) * (n_boot - 1)))]
    return lo, hi


def matched_controls(bars, events, horizon_bars, cost, key, bounds, k=5, seed=0):
    """Per event, k random-timing entries (same side, same span, same segment); returns their `key` horizon returns."""
    idx = _index(bars)
    rng = random.Random(seed)
    out = []
    for event in events:
        seg = segment_of(idx[event.entry_time], horizon_bars, bounds)
        if seg is None:
            continue
        lo, hi = dict(zip(("train", "validation", "test"), bounds))[seg]
        last = hi - horizon_bars - 1
        if last <= lo:
            continue
        for _ in range(k):
            j = rng.randint(lo, last)
            _, _, rets = measure(bars, j, bars[j].open, event.side, event.leg_range, horizon_bars, cost)
            if key in rets:
                out.append(rets[key])
    return out


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def evaluate(bars, events, horizon_bars, cost, key, fracs=SPLITS, reveal_test=False, k=5, block=5, seed=0):
    """Per ratio: raw n, de-clustered n, and for train / validation (test only if reveal_test) the mean `key`-bar
    return, its block-bootstrap CI, and the matched-control mean. One H family per call."""
    kinds = {type(e).__name__ for e in events}
    if len(kinds) > 1:
        raise ValueError(f"do not mix H1 and H2 events: {sorted(kinds)}")
    idx = _index(bars)
    bounds = split_bounds(len(bars), fracs)
    segments = ("train", "validation", "test") if reveal_test else ("train", "validation")
    report = {"key": key, "horizon_bars": horizon_bars, "cost": cost, "test_locked": not reveal_test, "ratios": {}}
    dc = decluster(events, bars, horizon_bars)
    for ratio in sorted({e.ratio for e in events}):
        raw = [e for e in events if e.ratio == ratio]
        mine = [e for e in dc if e.ratio == ratio]
        row = {"n_raw": len(raw), "n_declustered": len(mine), "purged": 0}
        by_seg = {s: [] for s in ("train", "validation", "test")}
        for e in mine:
            seg = segment_of(idx[e.entry_time], horizon_bars, bounds)
            if seg is None:
                row["purged"] += 1
            elif key in e.returns_leg:
                by_seg[seg].append(e)
        for s in segments:
            vals = [e.returns_leg[key] for e in by_seg[s]]
            ctrl = matched_controls(bars, by_seg[s], horizon_bars, cost, key, bounds, k=k, seed=seed)
            m, c = _mean(vals), _mean(ctrl)
            row[s] = {"n": len(vals), "mean": m, "ci": block_bootstrap_ci(vals, block=block, seed=seed),
                      "control_mean": c, "control_n": len(ctrl), "vs_control": None if m is None or c is None else m - c}
        if not reveal_test:
            row["test"] = {"n": len(by_seg["test"]), "locked": True}
        report["ratios"][str(ratio)] = row
    report["note"] = "Research only. n < 30 per cell = not evidence. Ratios compared side by side: picking the best one is a multiple test."
    return report


NEIGHBOURHOOD = {"pivot": (2, 3, 4, 5), "wait_bars": (40, 80, 120)}


def neighbourhood(bars, run, cost, key, horizon_bars, ratio=2.6, grid=NEIGHBOURHOOD, seed=0):
    """Stability check, not a search: re-run one family (`run` = run_event_study or run_h2) for each pivot window
    (left = right) x wait_bars and report the train / validation mean for `ratio`. The test segment is never read.
    An effect that exists only at one setting is curve fit; nothing here may be used to pick parameters for the test."""
    rows = []
    for p in grid["pivot"]:
        for w in grid["wait_bars"]:
            events, _ = run(bars, (ratio,), left=p, right=p, wait_bars=w, horizon_bars=horizon_bars, cost=cost)
            r = evaluate(bars, events, horizon_bars, cost, key, seed=seed)["ratios"].get(str(float(ratio)))
            rows.append({"pivot": p, "wait_bars": w, "n_declustered": r["n_declustered"] if r else 0,
                         "train_mean": r["train"]["mean"] if r else None, "validation_mean": r["validation"]["mean"] if r else None,
                         "validation_n": r["validation"]["n"] if r else 0})
    signs = [x["validation_mean"] > 0 for x in rows if x["validation_mean"] is not None and x["validation_n"] >= 30]
    return {"ratio": ratio, "rows": rows, "settings_with_n30": len(signs), "positive_share": (sum(signs) / len(signs)) if signs else None}
