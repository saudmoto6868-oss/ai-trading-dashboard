"""Outcome measurement for the Spot ideas log (owner 2026-11-25: win / loss is decided by what the price did later).

Reads docs/spot/ideas_log.jsonl (written daily by spot_snapshot.append_log) and walks DAILY candles after each
idea's day. This file only MEASURES; it never changes an idea and never tells the owner to trade.

Measurement rule (default, stated so it can be changed):
  - a long idea is "filled" when a daily bar's range touches the entry zone [lo, hi] (first such bar);
  - from the fill bar on, the first of the stop or the first target is taken; if both fall in one bar, the stop counts first;
  - result R = +(target1 - entry_mid) / risk or -1 at the stop; risk = entry_mid - stop; cost 0.1% taken from R;
  - no fill, or neither stop nor target within 30 daily bars -> "open" (not counted in the win rate);
  - ideas whose asset has no price feed here (metals, oil, forex on Hyperliquid / Yahoo) -> "no feed" (not measured).
Verdict per idea kind: "not evidence" under n = 30 closed trades, as in the rest of the project.

Run: python -m modules.spot_outcomes   (GitHub Actions: spot-ideas.yml, after the daily log)."""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "docs", "spot", "ideas_log.jsonl")
OUT = os.path.join(ROOT, "docs", "spot", "outcomes.json")
OKX_INST = {"BTC": "BTC-USDT", "ETH": "ETH-USDT", "SOL": "SOL-USDT"}   # crypto only: the feed we can reach from the runner
COST = 0.001
OPEN_BARS = 30
MIN_N = 30


def measure(idea: dict, bars: list[dict]) -> dict:
    """bars: daily candles {t (ms), h, l, c}, oldest first, starting AFTER the idea's day."""
    ent = idea.get("entry") or []
    stop = idea.get("stop")
    tgts = idea.get("targets") or []
    if len(ent) != 2 or stop is None or not tgts:
        return {"status": "skipped", "why": "no entry / stop / target"}
    lo, hi = float(min(ent)), float(max(ent))
    mid, stop, tp = (lo + hi) / 2, float(stop), float(tgts[0])
    if not (stop < mid < tp):
        return {"status": "skipped", "why": "not a long with stop below and target above"}
    risk = mid - stop
    cost_r = COST * mid / risk
    fill = None
    for k, b in enumerate(bars[:OPEN_BARS + 40]):
        if fill is None:
            if b["l"] <= hi and b["h"] >= lo:
                fill = k
                if b["l"] <= stop:          # filled and stopped in the same bar: stop first
                    return {"status": "closed", "result": "loss", "R": round(-1 - cost_r, 3), "bars": 1}
                if b["h"] >= tp:
                    return {"status": "closed", "result": "win", "R": round((tp - mid) / risk - cost_r, 3), "bars": 1}
            continue
        if k - fill >= OPEN_BARS:
            break
        if b["l"] <= stop:
            return {"status": "closed", "result": "loss", "R": round(-1 - cost_r, 3), "bars": k - fill + 1}
        if b["h"] >= tp:
            return {"status": "closed", "result": "win", "R": round((tp - mid) / risk - cost_r, 3), "bars": k - fill + 1}
    return {"status": "open", "result": "no fill" if fill is None else "still open"}


def summarize(rows: list[dict]) -> dict:
    by = {}
    for r in rows:
        if r.get("status") != "closed":
            continue
        by.setdefault(r.get("kind") or "?", []).append(r["R"])
    out = {}
    for kind, rs in by.items():
        n = len(rs)
        out[kind] = {"n": n, "winPct": round(100 * sum(1 for x in rs if x > 0) / n, 1), "meanR": round(sum(rs) / n, 3),
                     "verdict": "not evidence (n < 30)" if n < MIN_N else "n >= 30: read the numbers, still not a forecast"}
    return out


def run(log_path: str = LOG, out_path: str = OUT, fetch=None, pages: int = 6) -> dict:
    from modules import aplus_backtest as AB
    ideas = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                try:
                    ideas.append(json.loads(line))
                except ValueError:
                    continue
    cache, rows = {}, []
    for idea in ideas:
        base = {"day": idea.get("day"), "asset": idea.get("asset"), "kind": idea.get("kind"), "entry": idea.get("entry"), "stop": idea.get("stop"), "targets": idea.get("targets")}
        inst = OKX_INST.get(idea.get("asset"))
        if not inst:
            rows.append({**base, "status": "no feed"})
            continue
        if inst not in cache:
            cache[inst] = AB.fetch_okx(inst, "1D", pages=pages, get=fetch)
        day_ms = _day_ms(idea.get("day"))
        after = [b for b in cache[inst] if b["t"] >= day_ms + 86_400_000]
        rows.append({**base, **measure(idea, after)})
    rep = {"rule": {"open_bars": OPEN_BARS, "min_n": MIN_N, "cost_pct": COST * 100}, "rows": rows, "summary": summarize(rows),
           "note": "Measured from the log, not decided here. Past prices only; not a forecast."}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    return rep


def _day_ms(day: str | None) -> int:
    import datetime as dt
    d = dt.datetime.strptime(day or "1970-01-01", "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
    return int(d.timestamp() * 1000)


if __name__ == "__main__":
    rep = run()
    print(json.dumps(rep["summary"], ensure_ascii=False, indent=1) or "no closed trades yet")
    print("rows:", len(rep["rows"]), "| no feed:", sum(1 for r in rep["rows"] if r.get("status") == "no feed"))
