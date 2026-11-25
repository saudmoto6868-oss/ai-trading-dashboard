"""Spot brain learning loop (owner 2026-11-15: 'everything learns, reviews and improves itself, sustainably').

Three steps, kept apart on purpose:
  1. record(): every verdict the brain gives is appended to a JSONL log (asset, horizon, verdict, price, levels, time).
  2. score(): once a horizon has fully passed, the forward move is measured from the closes after the record time
     (no look-ahead: rows whose horizon is not over yet stay pending). Target / stop are checked on highs and lows when
     they are in the data, otherwise on closes.
  3. summary(): per horizon and verdict group -> n, hit rate, mean signed return, Welch t vs 0.

What it does NOT do: it does not change the brain's weights. A verdict group only gets a label ('works' / 'worse' /
'not evidence') when n >= 30 and |t| >= 3, the same luck guard as the setup lab. Automatic weight changes are a later step
and need the owner's OK, because tuning on a few dozen noisy outcomes is how systems fool themselves.
Storage: an append-only JSONL file (git-ignored data/spot/ by default). Pure functions, no network."""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "data" / "spot" / "brain_log.jsonl"
HORIZON_DAYS = {"day": 3, "week": 28, "month": 90, "year": 365, "4h": 3, "1d": 10, "1w": 56, "1mo": 180}   # brain horizons + setup timeframes (setup lab: 1D 10 days, 1W 8 weeks)
BUY_SIDE = {"buy", "accumulate"}
SELL_SIDE = {"sell", "reduce"}
MIN_N, MIN_T = 30, 3.0


def _now() -> datetime:
    return datetime.now(timezone.utc)


def record(brain: dict, path: Path | None = None, when: datetime | None = None) -> int:
    """Append one row per horizon of a spot_brain.run() result. Returns the number of rows written."""
    p = Path(path or LOG)
    p.parent.mkdir(parents=True, exist_ok=True)
    t = (when or _now()).replace(microsecond=0).isoformat()
    rows = []
    for key, h in (brain.get("horizons") or {}).items():
        rows.append({"time": t, "asset": brain.get("asset"), "horizon": key, "verdict": h.get("verdict"), "score": h.get("score"),
                     "price": brain.get("price"), "entry": h.get("entry"), "stop": h.get("stop"), "target": h.get("target")})
    with open(p, "a", encoding="utf8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(rows)


def record_setups(brain: dict, path: Path | None = None, when: datetime | None = None) -> int:
    """Log EVERY live setup the desk shows for this market (not only the brain's verdict), so every option is kept and
    compared over time. Buy setups score as 'buy', exit setups as 'sell'. Nothing here changes any weight."""
    p = Path(path or LOG)
    p.parent.mkdir(parents=True, exist_ok=True)
    t = (when or _now()).replace(microsecond=0).isoformat()
    n = 0
    with open(p, "a", encoding="utf8") as f:
        for x in brain.get("setups") or []:
            row = {"time": t, "asset": brain.get("asset"), "id": x.get("id"), "horizon": x.get("tf"), "verdict": "buy" if x.get("side") == "buy" else "sell",
                   "price": brain.get("price"), "entry": x.get("entry"), "stop": x.get("stop"), "target": x.get("target"), "kind": "setup"}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    return n


def load(path: Path | None = None) -> list[dict]:
    p = Path(path or LOG)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue   # a torn line must not break the whole log
    return out


def _sign(verdict: str | None) -> int:
    if verdict in BUY_SIDE:
        return 1
    if verdict in SELL_SIDE:
        return -1
    return 0


def score(rows: list[dict], bars: dict, now: datetime | None = None) -> list[dict]:
    """bars: {asset: [{'time': iso, 'high': f, 'low': f, 'close': f}, ...]} oldest first.
    Returns the scored rows (horizon over). Rows with no price series, or whose horizon has not passed, are skipped."""
    now = now or _now()
    out = []
    for r in rows:
        series = bars.get(r.get("asset")) or []
        t0 = datetime.fromisoformat(r["time"])
        days = HORIZON_DAYS.get(r.get("horizon"))
        if days is None or not r.get("price") or not series:
            continue
        end = t0 + timedelta(days=days)
        if end > now:
            continue                                   # horizon not over: pending, never scored early
        path = [b for b in series if t0 < datetime.fromisoformat(b["time"]) <= end]
        if not path:
            continue
        sg = _sign(r.get("verdict"))
        if sg == 0:
            continue                                   # wait / no view: nothing to score
        px = float(r["price"])
        last = float(path[-1]["close"])
        ret = sg * (last / px - 1)                     # positive = the verdict helped
        outcome = "time"
        tgt, stp = r.get("target"), r.get("stop")
        for b in path:                                 # first touch decides (buy side: target above, stop below)
            hi, lo = b.get("high", b["close"]), b.get("low", b["close"])
            if sg > 0:
                if stp is not None and lo <= stp:
                    outcome = "stop"
                    ret = stp / px - 1
                    break
                if tgt is not None and hi >= tgt:
                    outcome = "target"
                    ret = tgt / px - 1
                    break
            else:
                if stp is not None and hi >= stp:
                    outcome = "stop"
                    ret = -(stp / px - 1)
                    break
                if tgt is not None and lo <= tgt:
                    outcome = "target"
                    ret = -(tgt / px - 1)
                    break
        out.append({**r, "ret": ret, "outcome": outcome, "scored_at": now.replace(microsecond=0).isoformat()})
    return out


def _welch_t(xs: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    if var <= 0:
        return None
    return m / math.sqrt(var / n)                      # one-sample t vs 0 (the verdict's own sign already applied)


def summary(scored: list[dict]) -> dict:
    """{'horizon|verdict': {n, hit_pct, mean_pct, t, label}} - the label is the only thing the brain may read."""
    groups: dict[str, list[dict]] = {}
    for r in scored:
        groups.setdefault(r.get("id") or f"{r['horizon']}|{r['verdict']}", []).append(r)
    res = {}
    for k, rs in sorted(groups.items()):
        rets = [float(x["ret"]) for x in rs]
        n = len(rets)
        t = _welch_t(rets)
        if n < MIN_N:
            label = f"مش دليل (n {n})"
        elif t is not None and t >= MIN_T:
            label = f"اشتغل (n {n}, t {t:+.1f})"
        elif t is not None and t <= -MIN_T:
            label = f"كان أسوأ (n {n}, t {t:+.1f})"
        else:
            label = f"مفيش فرق واضح (n {n})"
        res[k] = {"n": n, "hit_pct": 100 * sum(1 for x in rets if x > 0) / n, "mean_pct": 100 * sum(rets) / n, "t": t, "label": label,
                  "targets": sum(1 for x in rs if x["outcome"] == "target"), "stops": sum(1 for x in rs if x["outcome"] == "stop")}
    return res


def report_ar(res: dict) -> str:
    if not res:
        return "🧠 سجل قرارات المخ: لسه مفيش قرارات اتقاست (لازم الأفق يخلص الأول)."
    lines = ["🧠 سجل قرارات المخ (ما بيغيّرش الأوزان لحد n ≥ 30 و t ≥ 3):"]
    for k, v in res.items():
        h, verdict = k.split("|")
        lines.append(f"• {h} / {verdict}: {v['label']} · نجاح {v['hit_pct']:.0f}% · متوسط {v['mean_pct']:+.2f}%")
    return "\n".join(lines)


def stability(scored: list[dict]) -> dict:
    """Does a group hold up over time? Splits each group's outcomes by scoring time into an earlier and a later half.
    Same sign and both halves with n >= 10 -> 'holds'; sign flip -> 'flips'; too few -> 'not yet'. Labels only, no weights."""
    groups: dict[str, list[dict]] = {}
    for r in scored:
        groups.setdefault(r.get("id") or f"{r['horizon']}|{r['verdict']}", []).append(r)
    out = {}
    for k, rs in groups.items():
        rs = sorted(rs, key=lambda x: x["time"])
        mid = len(rs) // 2
        a, b = [float(x["ret"]) for x in rs[:mid]], [float(x["ret"]) for x in rs[mid:]]
        if len(a) < 10 or len(b) < 10:
            out[k] = "not yet"
            continue
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        out[k] = "holds" if (ma > 0) == (mb > 0) else "flips"
    return out
