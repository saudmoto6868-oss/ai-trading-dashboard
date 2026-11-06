"""THE BRAIN's memory: every daily list is logged, graded afterwards with the plan's own exit rules, and summarised per school (owner 2026-11-06: "learn, review, develop itself").

What it does (and does not):
  * record(items): appends today's Top-7 ideas (entry / stop / targets / exit rules / schools) to .brain_log.jsonl (GitHub Actions cache, like .tg_sent.json).
  * grade(...): once an idea is old enough, replays the candles AFTER it with day_plan.simulate_arrays and stores its R in .brain_graded.json.
  * stats(...): n, average R and win % per school, per detector key and overall. Under n = 30 every number is marked NOT EVIDENCE. The brain only REPORTS and SUGGESTS: it never changes weights,
    thresholds or the live scanner by itself; a promotion goes through the weekly lab (docs/academy/DEVELOPMENT_NOTES.md).
Costs: R here is before costs (the lab nets LAB_COST_R per trade)."""
from __future__ import annotations

import json
import os
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd

LOG = Path(os.environ.get("BRAIN_LOG", ".brain_log.jsonl"))
GRADED = Path(os.environ.get("BRAIN_GRADED", ".brain_graded.json"))
MIN_N = 30
MIN_AGE_S, MAX_AGE_S = 6 * 3600, 5 * 86400
TF_SECONDS = {"5m": 300, "15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}


def record(items, now: float | None = None, path: Path | None = None) -> int:
    """Append the list (a plan's `id` is unique per symbol / direction / tf / mode / day)."""
    path = path or LOG
    now = now or time.time()
    day = time.strftime("%Y-%m-%d", time.gmtime(now))
    known = {e["id"] for e in load(path)}
    n = 0
    with path.open("a") as f:
        for r in items:
            rid = f"{r['id']}|{day}"
            if rid in known:
                continue
            f.write(json.dumps({"id": rid, "day": day, "ts": now, "symbol": r["symbol"], "tf": r["tf"], "direction": r["direction"], "mode": r.get("mode", "conf"), "entry": r["entry"], "stop": r["stop"],
                                "tps": r["tps"], "atr": r.get("atr"), "exit": r.get("exit"), "schools": r.get("schools", []), "keys": r.get("keys", []), "points": r.get("points"),
                                "choppy": r.get("choppy")}) + "\n")
            n += 1
    return n


def load(path: Path | None = None) -> list:
    path = path or LOG
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def load_graded(path: Path | None = None) -> dict:
    try:
        return json.loads((path or GRADED).read_text())
    except Exception:
        return {}


def save_graded(g: dict, path: Path | None = None):
    (path or GRADED).write_text(json.dumps(g))


def grade(entries, graded: dict, fetch, now: float | None = None) -> int:
    """Grade every idea that is old enough and not graded yet. fetch(symbol, tf) -> DataFrame(time, high, low, close). -> how many were graded."""
    from modules.day_plan import simulate_arrays
    now = now or time.time()
    n = 0
    for e in entries:
        if e["id"] in graded:
            continue
        age = now - e["ts"]
        if age < MIN_AGE_S or not e.get("exit"):
            continue
        try:
            df = fetch(e["symbol"], e["tf"])
            if df is None or len(df) < 5:
                continue
            t = pd.to_datetime(df["time"])
            t = t.dt.tz_convert("UTC").dt.tz_localize(None) if getattr(t.dt, "tz", None) is not None else t
            ts = (t - pd.Timestamp("1970-01-01")).dt.total_seconds()   # unit-safe (pandas keeps ns / us / s depending on the version)
            after = df[ts.to_numpy() > e["ts"]]
            if len(after) < 3 and age < MAX_AGE_S:
                continue
            ex = e["exit"]
            r = simulate_arrays(after["high"].to_numpy(float), after["low"].to_numpy(float), after["close"].to_numpy(float), e["direction"], e["entry"], e["stop"], ex, e.get("atr"))
            graded[e["id"]] = {"r": r["r"], "closed": r["closed"], "bars": int(len(after)), "t": now}
            n += 1
        except Exception:
            continue
    return n


def stats(entries, graded: dict) -> dict:
    """{'all': row, 'school': {name: row}, 'key': {key: row}}; row = {n, avg_r, win, evidence}. Closed trades and still-open ones both count (open at their last close)."""
    groups = {"all": defaultdict(list), "school": defaultdict(list), "key": defaultdict(list)}
    for e in entries:
        g = graded.get(e["id"])
        if not g:
            continue
        groups["all"]["all"].append(g["r"])
        for s in e.get("schools", []):
            groups["school"][s].append(g["r"])
        for k in e.get("keys", []):
            if k:
                groups["key"][k].append(g["r"])

    def row(rs):
        n = len(rs)
        return {"n": n, "avg_r": round(sum(rs) / n, 3) if n else 0.0, "win": round(100 * sum(1 for x in rs if x > 0) / n, 1) if n else 0.0, "evidence": n >= MIN_N}

    return {"all": row(groups["all"]["all"]), "school": {k: row(v) for k, v in groups["school"].items()}, "key": {k: row(v) for k, v in groups["key"].items()}}


def review_text(entries, graded: dict, day: str | None = None, ar: bool = True) -> str:
    """The daily review message: how the last graded ideas did, per school, with the n<30 warning."""
    import html
    esc = html.escape
    st = stats(entries, graded)
    a = st["all"]
    if not a["n"]:
        return ("🧠 <b>مراجعة المخ</b>\nلسه مفيش أفكار اتقيّمت (بتتقيّم بعد 6 ساعات على الأقل)." if ar else "🧠 <b>Brain review</b>\nNo idea has been graded yet (they are graded 6 h or more after the list).")
    lines = [f"🧠 <b>{'مراجعة المخ' if ar else 'Brain review'}</b> · {a['n']} {'فكرة متقيّمة' if ar else 'graded ideas'} · {'متوسط' if ar else 'avg'} {a['avg_r']:+.2f}R · {a['win']}% {'رابحة' if ar else 'wins'}"]
    rows = sorted(st["school"].items(), key=lambda kv: -kv[1]["n"])[:6]
    for name, r in rows:
        lines.append(f"• {esc(name)}: n={r['n']} · {r['avg_r']:+.2f}R · {r['win']}%" + ("" if r["evidence"] else (" · ⚠ مش دليل (n<30)" if ar else " · ⚠ not evidence (n<30)")))
    lines.append("\n<i>R قبل التكاليف. المخ بيسجّل ويقيّم ويقترح بس؛ أي ترقية بتعدي على اللاب الأسبوعي.</i>" if ar else "\n<i>R before costs. The brain logs, grades and suggests only; any promotion goes through the weekly lab.</i>")
    return "\n".join(lines)[:3900]
