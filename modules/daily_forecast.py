"""Daily baseline calls + automatic scoring. Honest by design: one call per symbol per day, written BEFORE the outcome.

Rule v0 (a BASELINE to beat, not a strategy): take the last completed zig-zag leg. If it went up, call long; if down, short.
Entry = last close, stop = the start of that leg, target = entry + 1.5 x risk, horizon = 5 daily bars.
Every number is recorded in data/forecasts/ before the outcome is known. Scoring walks later candles (stop first on a same-bar tie).
Results: data/forecasts/outcomes.jsonl and docs/forecasts/SUMMARY.md. Labels only, no claim of edge.
Run: python -m modules.daily_forecast --record | --score   (tests inject a fake candle loader; no network in tests).
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "forecast_symbols.json"
FDIR = ROOT / "data" / "forecasts"
OUT = FDIR / "outcomes.jsonl"
SUMMARY = ROOT / "docs" / "forecasts" / "SUMMARY.md"
HORIZON = 5
RISK_MULT = 1.5
TF = "1d"          # the loader's daily name. "1D" was a bug (2026-11-21..24): OKX fell back to 1-hour bars and Hyperliquid refused it.


def symbols():
    cfg = json.loads(CONFIG.read_text(encoding="utf8"))
    return {k: v for k, v in cfg.items() if not k.startswith("_")}


def baseline_call(rows):
    """rows: list of dicts {h, l, c}, oldest first. -> dict(side, entry, stop, target) or None."""
    from modules.harmonic import zigzag, vol_dev
    import pandas as pd
    df = pd.DataFrame(rows).rename(columns={"h": "high", "l": "low", "c": "close"})
    zz = zigzag(df["high"].to_numpy(float), df["low"].to_numpy(float), vol_dev(df, 2.5, 0.001, 0.025))
    if len(zz) < 2:
        return None
    (_, p0, _), (_, p1, _) = zz[-2], zz[-1]
    if p1 == p0:
        return None
    side = "long" if p1 > p0 else "short"
    entry = float(rows[-1]["c"])
    stop = float(p0)
    risk = abs(entry - stop)
    if risk <= 0:
        return None
    target = entry + RISK_MULT * risk if side == "long" else entry - RISK_MULT * risk
    if (side == "long" and not stop < entry) or (side == "short" and not stop > entry):
        return None   # the last close already broke the leg start: no clean call today
    return {"side": side, "entry": entry, "stop": stop, "target": target}


def record_day(fetch, today=None, folder=None):
    """One call per symbol. Returns list of written records. fetch(symbol, tf, limit) -> rows (dicts with h, l, c, t)."""
    from modules import forecast_log
    today = today or dt.date.today().isoformat()
    written = []
    for cls, syms in symbols().items():
        for s in syms:
            try:
                rows = fetch(s, TF, 200)
            except Exception as e:  # a missing feed is not a call
                print(f"skip {s}: {type(e).__name__}", file=sys.stderr)
                continue
            if rows is None or len(rows) < 40:
                continue
            c = baseline_call(rows)
            if not c:
                continue
            rec = {"id": f"{s}|{today}", "symbol": s, "class": cls, "tf": TF, **c, "made_at": today,
                   "horizon_bars": HORIZON, "rule": "baseline v0: last zig-zag leg continuation"}
            forecast_log.record(rec, folder=folder or FDIR)
            written.append(rec)
    return written


def _load_jsonl(p):
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf8").splitlines() if x.strip()]


def score_due(fetch, today=None, folder=None):
    """Score every recorded call whose horizon has passed and that has no outcome yet. Returns new outcome rows."""
    from modules import forecast_log
    today = today or dt.date.today().isoformat()
    base = folder or FDIR
    done = {o["id"] for o in _load_jsonl(base / "outcomes.jsonl")}
    new = []
    for p in base.glob("*.jsonl"):
        if p.name == "outcomes.jsonl":
            continue
        for fc in _load_jsonl(p):
            if fc["id"] in done or fc.get("tf") != TF:   # calls from the 1D bug are never scored
                continue
            rows = fetch(fc["symbol"], TF, 300) or []
            after = [r for r in rows if str(r.get("day", "")) > fc["made_at"]]
            if len(after) < fc["horizon_bars"]:
                continue   # not enough bars yet
            outcome, R = forecast_log.score(fc, after)
            new.append({"id": fc["id"], "symbol": fc["symbol"], "class": fc.get("class", ""), "side": fc["side"],
                        "outcome": outcome, "R": round(R, 3), "scored_on": today})
    if new:
        with (base / "outcomes.jsonl").open("a", encoding="utf8") as f:
            for r in new:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return new


def valid_ids(folder=None):
    """Ids of calls recorded on real daily bars (tf == TF). Calls from the 2026-11-21..24 '1D' bug are left out."""
    base = folder or FDIR
    ids = set()
    for p in base.glob("*.jsonl"):
        if p.name == "outcomes.jsonl":
            continue
        ids.update(fc["id"] for fc in _load_jsonl(p) if fc.get("tf") == TF)
    return ids


def scored(folder=None):
    """Outcome rows of valid calls only."""
    ok = valid_ids(folder)
    return [r for r in _load_jsonl((folder or FDIR) / "outcomes.jsonl") if r["id"] in ok]


def class_summary(folder=None):
    """[(class, summary dict)] from the scored calls, for screens (brain view). Empty list when nothing is scored yet."""
    from modules import forecast_log
    res = scored(folder)
    by = {}
    for r in res:
        by.setdefault(r.get("class") or "all", []).append((r["outcome"], r["R"]))
    return [(k, forecast_log.summarise(v)) for k, v in sorted(by.items())]


def write_summary(folder=None, out=None):
    from modules import forecast_log
    base = folder or FDIR
    res = scored(base)
    dropped = len(_load_jsonl(base / "outcomes.jsonl")) - len(res)
    lines = ["# Baseline calls: summary (auto)", "", "Rule v0 is a baseline to beat, not a strategy. n < 30 is not evidence; n < 100 is too small.", ""]
    if dropped:
        lines += [f"Left out: {dropped} early outcomes (2026-11-21..24) whose calls were made on 1-hour bars by a timeframe bug.", ""]
    by = {}
    for r in res:
        by.setdefault(r.get("class") or "all", []).append((r["outcome"], r["R"]))
    lines += ["| class | n | wins | losses | timeouts | win rate | 95% CI | avg R | verdict |", "|---|---|---|---|---|---|---|---|---|"]
    for cls in sorted(by):
        s = forecast_log.summarise(by[cls])
        lines.append(f"| {cls} | {s['n']} | {s['wins']} | {s['losses']} | {s['timeouts']} | {s['win_rate']} | {s['ci95']} | {s['avg_R']} | {s['verdict']} |")
    if not by:
        lines.append("| — | 0 | | | | | | | no scored calls yet |")
    text = "\n".join(lines) + "\n"
    (out or SUMMARY).parent.mkdir(parents=True, exist_ok=True)
    (out or SUMMARY).write_text(text, encoding="utf8")
    return text


def _default_fetch(symbol, tf, limit):   # the server's own loader (OKX / Yahoo / Hyperliquid routing)
    from modules import market_cache
    df = market_cache.get_klines(symbol, tf, limit)
    rows = []
    for t, h, l, c in zip(df["time"] if "time" in df else range(len(df)), df["high"], df["low"], df["close"]):
        rows.append({"day": str(t)[:10], "h": float(h), "l": float(l), "c": float(c)})
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    if a.record:
        print("recorded", len(record_day(_default_fetch)))
    if a.score:
        print("scored", len(score_due(_default_fetch)))
    write_summary()
