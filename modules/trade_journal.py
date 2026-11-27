"""THE trade journal: one server-side store for every trade the workspace logs (replaces the per-browser localStorage copy).

Why: a browser's localStorage is per browser, lost when site data is cleared, and invisible to the brain. This file is the
single source of truth; the brain (modules/brain.py) and the meeting-room table read it from here.

Record (dict, key = id):
  id, key, symbol, dir ("bullish" | "bearish"), tfk, ttype, entry, sl, tp1, tp2, tp3, rr, score, max, tags, t0 (ms),
  status: "open" | "part" (tp1 hit, runner still open) | "tp" (final target) | "sl" | "nf" (never filled) | "exp" (time ran out),
  fill: bool, exits: [{level: "tp1"|"tp2"|"tp3"|"sl", t, price, r}], ctx: dict (context at entry), reason: str, notes: str

Rules (kept from the JS journal): a trade that never filled is "nf", not a loss. Same candle touches stop and target: stop counts.
Costs are not included. Under 30 closed trades nothing here is evidence."""
from __future__ import annotations

import json
import os
import time
from collections import defaultdict
from pathlib import Path

PATH = Path(os.environ.get("TRADE_JOURNAL_PATH", "data/journal/trades.json"))
MIN_N = 30
FINAL = {"tp", "sl", "nf", "exp"}
LEVELS = ("tp1", "tp2", "tp3")


def _load(path: Path | None = None) -> dict:
    p = path or PATH
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save(data: dict, path: Path | None = None) -> None:
    p = path or PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)  # atomic: a crash never leaves a half-written journal


def _num(v, name: str) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v:
        raise ValueError(f"{name} must be a finite number")
    return float(v)


def upsert(rec: dict, path: Path | None = None) -> dict:
    """Add a trade (or refresh its entry fields). Exits and final status of an existing trade are never overwritten here."""
    tid = str(rec.get("id") or "")
    if not tid:
        raise ValueError("id required")
    if rec.get("dir") not in ("bullish", "bearish"):
        raise ValueError("dir must be bullish or bearish")
    for k in ("entry", "sl", "tp1"):
        _num(rec.get(k), k)
    data = _load(path)
    cur = data.get(tid, {"exits": [], "status": "open", "fill": rec.get("fill", True)})
    for k, v in rec.items():
        if k not in ("exits", "status"):
            cur[k] = v
    cur["id"] = tid
    cur.setdefault("t0", int(time.time() * 1000))
    data[tid] = cur
    _save(data, path)
    return cur


def add_exit(tid: str, level: str, t: int, price: float, r: float, path: Path | None = None) -> dict:
    """Record one exit. tp1 leaves the trade "part" (runner still open); tp2 / tp3 / sl / nf / exp end it."""
    if level not in ("sl", *LEVELS):
        raise ValueError("level must be sl, tp1, tp2 or tp3")
    data = _load(path)
    tr = data.get(tid)
    if tr is None:
        raise KeyError(tid)
    if tr["status"] in FINAL or any(e["level"] == level for e in tr["exits"]):
        return tr  # already finished or this level already booked: a repeated tracker run does not double-count
    tr["exits"].append({"level": level, "t": int(t), "price": _num(price, "price"), "r": _num(r, "r")})
    if level == "sl":
        tr["status"] = "sl"
    elif level == "tp3" or (level == "tp2" and not tr.get("tp3")):
        tr["status"] = "tp"
    elif level == "tp1":
        tr["status"] = "part" if tr.get("tp2") else "tp"
    _save(data, path)
    return tr


def apply_snapshot(snap: dict, path: Path | None = None) -> dict:
    """Merge one browser snapshot (the JS journal record after a change). Idempotent: re-sending the same snapshot changes nothing."""
    data = _load(path)
    tr = _merge(data, snap)
    _save(data, path)
    return tr


def apply_snapshots(snaps: list, path: Path | None = None) -> int:
    """Merge many snapshots with ONE read and ONE write. A bad snapshot is skipped. Returns how many were merged."""
    data = _load(path)
    n = 0
    for s in snaps:
        try:
            _merge(data, s)
            n += 1
        except (ValueError, KeyError, TypeError):
            continue
    if n:
        _save(data, path)
    return n


def _merge(data: dict, snap: dict) -> dict:
    """Status only moves forward: a final status (tp / sl / nf / exp) is never overwritten by a later snapshot."""
    tid = str(snap.get("id") or "")
    if not tid:
        raise ValueError("id required")
    if tid not in data:
        if snap.get("dir") not in ("bullish", "bearish"):
            raise ValueError("dir must be bullish or bearish")
        for k in ("entry", "sl", "tp1"):
            _num(snap.get(k), k)
        data[tid] = {"id": tid, "exits": [], "status": "open", "fill": True, "t0": int(snap.get("t0") or time.time() * 1000)}
    tr = data[tid]
    for k in ("symbol", "dir", "tfk", "ttype", "entry", "sl", "tp1", "tp2", "tp3", "rr", "score", "max", "tags", "ctx", "fill"):
        if k in snap and snap[k] is not None:
            tr[k] = snap[k]
    for e in snap.get("exits") or []:   # partial exits from the browser: one per level, booked once
        lvl = e.get("level") if isinstance(e, dict) else None
        if lvl not in ("sl", *LEVELS) or any(x["level"] == lvl for x in tr["exits"]):
            continue
        tr["exits"].append({"level": lvl, "t": int(e.get("t") or 0), "price": _num(e.get("price", 0.0), "price"), "r": _num(e.get("r", 0.0), "r")})
    if tr["status"] == "open" and any(x["level"] in LEVELS for x in tr["exits"]):
        tr["status"] = "part"   # a target was hit, the runner is still open
    if tr["status"] not in FINAL and snap.get("status") in FINAL:
        tr["status"] = snap["status"]
        tr["r_total"] = _num(snap.get("r") or 0.0, "r")
        tr["t1"] = int(snap.get("t1") or 0)
        if snap.get("status") == "sl" and not any(e["level"] == "sl" for e in tr["exits"]):
            tr["exits"].append({"level": "sl", "t": tr["t1"], "price": _num(tr.get("sl"), "sl"), "r": tr["r_total"]})
    if snap.get("reason"):
        tr["reason"] = str(snap["reason"])[:2000]
    return tr


def finish(tid: str, status: str, t: int, r: float, reason: str = "", path: Path | None = None) -> dict:
    """Close a trade that did not exit through a level (nf / exp), or attach the reason to a closed one."""
    if status not in FINAL:
        raise ValueError("status must be tp, sl, nf or exp")
    data = _load(path)
    tr = data.get(tid)
    if tr is None:
        raise KeyError(tid)
    if tr["status"] not in FINAL:
        tr["status"] = status
        tr["t1"] = int(t)
        tr["r_total"] = _num(r, "r")
    if reason:
        tr["reason"] = str(reason)[:2000]
    _save(data, path)
    return tr


def r_total(tr: dict) -> float:
    """Sum of exit R. Exits are per trade-unit: a partial tp1 counts its own R, the runner counts its own."""
    if tr.get("status") not in FINAL and tr.get("status") != "part":
        return 0.0
    if tr.get("exits"):
        return sum(e["r"] for e in tr["exits"])
    return float(tr.get("r_total") or 0.0)


def postmortem(tr: dict) -> dict:
    """Why a stopped (or partly stopped) trade lost, what was already against it at entry, and the next step. Pure."""
    long_ = tr.get("dir") == "bullish"
    ctx = tr.get("ctx") or {}
    why: list[tuple[str, bool]] = []  # (text, is_warning)
    if ctx.get("of") == "against":
        why.append(("order flow was against the trade at entry", True))
    if ctx.get("news"):
        why.append(("news was active on the symbol at entry", True))
    if ctx.get("fund") == ("crowded longs" if long_ else "crowded shorts"):
        why.append(("funding was crowded on the trade side", True))
    if ctx.get("oi") in (("shorts", "closing") if long_ else ("longs", "cover")):
        why.append(("open interest did not back the trade", True))
    if tr.get("score") is not None and tr.get("max") and 100 * tr["score"] / tr["max"] < 70:
        why.append(("setup score was weak (under 70%)", True))
    exits = {e["level"] for e in tr.get("exits", [])}
    if "sl" in exits and "tp1" in exits:
        why.append(("tp1 hit, then the runner was stopped: the trailing rule gave back the profit", False))
    if tr.get("mfe_r") is not None and "sl" in exits and tr["mfe_r"] < 1:
        why.append(("price never moved 1R in favour: entry was early", False))
    warns = sum(1 for _, w in why if w)
    if warns:
        nxt = f"skip or wait: {warns} warning(s) were already on at entry"
    elif "tp1" in exits and "sl" in exits:
        nxt = "exit runner earlier at tp1 or move stop to entry after tp1"
    elif "sl" in exits:
        nxt = "entry came early: wait for a confirming close before entering"
    else:
        nxt = "no stop: nothing to review"
    if not why:
        why.append(("no warning was recorded at entry", False))
    return {"why": [t for t, _ in why], "next": nxt, "warnings": warns}


def analyze(tr: dict) -> dict:
    """Full review of one trade: when it was set and fired, which exits hit (with UTC time), the post-mortem and the
    targets it never reached. Pure. Times are UTC, from the saved records (no candles needed)."""
    t0 = int(tr.get("t0") or 0)
    exits = sorted(tr.get("exits", []), key=lambda e: e["t"])
    hit = {e["level"] for e in exits}
    out = {
        "id": tr.get("id"), "symbol": tr.get("symbol"), "side": "long" if tr.get("dir") == "bullish" else "short",
        "setup": tr.get("ttype"), "tf": tr.get("tfk"), "status": tr.get("status"), "fill": tr.get("fill") is not False,
        "set_utc": _utc(t0), "closed_utc": _utc(tr.get("t1")) if tr.get("t1") else None,
        "exits": [{"level": e["level"], "utc": _utc(e["t"]), "r": round(e["r"], 2)} for e in exits],
        "r_total": round(r_total(tr), 2), "missed": [lv for lv in LEVELS if lv not in hit and tr.get("status") in ("sl", "part", "tp")],
        "postmortem": postmortem(tr) if tr.get("status") == "sl" else None,
        "tags": tr.get("tags") or [],
    }
    return out


def _utc(ms) -> str:
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(int(ms) / 1000)) if ms else ""


def stats(path: Path | None = None) -> dict:
    """Win rate and average R per setup type and per timeframe, closed trades only. n < MIN_N is marked not evidence."""
    closed = [t for t in _load(path).values() if t.get("status") in ("tp", "sl", "exp")]
    out: dict = {"n": len(closed), "evidence": len(closed) >= MIN_N, "groups": {}}
    groups: dict = defaultdict(list)
    for t in closed:
        groups[("ttype", t.get("ttype"))].append(t)
        groups[("tfk", t.get("tfk"))].append(t)
    for (kind, name), ts in groups.items():
        rs = [r_total(t) for t in ts]
        out["groups"].setdefault(kind, {})[str(name)] = {
            "n": len(ts), "win_pct": round(100 * sum(1 for r in rs if r > 0) / len(rs), 1), "avg_r": round(sum(rs) / len(rs), 3),
            "evidence": len(ts) >= MIN_N}
    return out


def all_trades(path: Path | None = None) -> list:
    return sorted(_load(path).values(), key=lambda t: t.get("t0", 0), reverse=True)
