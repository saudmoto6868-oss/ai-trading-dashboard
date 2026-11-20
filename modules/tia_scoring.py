"""Director track record: scores logged Director runs (data/tia/director_log.jsonl) against what price did afterwards.

Rules (project honesty rules): only BULLISH BIAS / BEARISH BIAS runs are scored; MIXED / WAIT / UNCONFIRMED / UNAVAILABLE abstain.
A run is scored once `horizon_days` have passed, using the first daily close at or after entry + horizon.
Hit = price moved in the stance's direction. Wilson 95% interval; under MIN_N scored runs the result is "not evidence".
No costs, no slippage and no position sizing are modelled: this is a direction check, not a P&L backtest.
2026-11-20. PR #245 adds modules/forecast_log.py with the same idea; unify with it after that PR is merged.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone

MIN_N = 30
DIRECTION = {"BULLISH BIAS": 1, "BEARISH BIAS": -1}


def load_log(path: str) -> list[dict]:
    rows = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except ValueError:
                        pass   # a half-written line must not break the track record
    except OSError:
        pass
    return rows


def wilson(hits: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    if n <= 0:
        return None
    p = hits / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)


def _parse_time(v) -> datetime | None:
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def _close_at(df, when: datetime):
    """First daily close at or after `when`, or None if that bar does not exist yet."""
    import pandas as pd
    t = df["time"]
    ts = pd.to_datetime(t, unit="ms", utc=True, errors="coerce") if str(t.dtype).startswith(("int", "float")) else pd.to_datetime(t, utc=True, errors="coerce")
    ok = ts >= pd.Timestamp(when)
    if not ok.any():
        return None
    return float(df["close"][ok].iloc[0])


def score_entry(entry: dict, fetch, now: datetime, horizon_days: int = 3) -> dict:
    """-> {"status": "scored"|"abstain"|"pending"|"unscorable", ...}. `fetch(symbol, tf, limit)` returns candles (market_cache.get_klines)."""
    d = DIRECTION.get(str(entry.get("stance")))
    if d is None:
        return {"status": "abstain"}
    t0, px = _parse_time(entry.get("asof_utc")), entry.get("price")
    if t0 is None or not px:
        return {"status": "unscorable", "why": "no entry time or price in the log row"}
    due = t0 + timedelta(days=horizon_days)
    if now < due:
        return {"status": "pending", "due": due.isoformat()}
    try:
        px2 = _close_at(fetch(entry["symbol"], "1d", 200), due)
    except Exception as exc:
        return {"status": "unscorable", "why": str(exc)[:120]}
    if px2 is None:
        return {"status": "pending", "due": due.isoformat()}
    ret = (px2 / float(px) - 1) * 100 * d
    return {"status": "scored", "ret_pct": round(ret, 3), "hit": ret > 0}


def summarize(entries: list[dict], fetch, now: datetime | None = None, horizon_days: int = 3) -> dict:
    now = now or datetime.now(timezone.utc)
    res = [score_entry(e, fetch, now, horizon_days) for e in entries]
    scored = [r for r in res if r["status"] == "scored"]
    n, hits = len(scored), sum(1 for r in scored if r["hit"])
    out = {"horizon_days": horizon_days, "runs": len(entries), "scored": n, "hits": hits,
           "abstain": sum(1 for r in res if r["status"] == "abstain"), "pending": sum(1 for r in res if r["status"] == "pending"),
           "unscorable": sum(1 for r in res if r["status"] == "unscorable"),
           "hit_rate": round(hits / n, 4) if n else None, "wilson95": wilson(hits, n),
           "mean_ret_pct": round(sum(r["ret_pct"] for r in scored) / n, 3) if n else None}
    out["verdict"] = ("not evidence: fewer than %d scored runs" % MIN_N) if n < MIN_N else \
                     ("interval includes 50%: no edge shown" if out["wilson95"][0] <= 0.5 else "hit rate above 50% on this sample (direction only, no costs)")
    return out


_TR_CACHE: dict = {"t": 0.0, "key": None, "val": None}


def track_record(path: str, fetch, ttl: int = 600, horizon_days: int = 3, last: int = 200) -> dict | None:
    """summarize() over the last `last` logged runs, cached `ttl` seconds (one candle fetch per symbol, shared by market_cache)."""
    import time
    key = (path, horizon_days, last)
    if _TR_CACHE["key"] == key and time.time() - _TR_CACHE["t"] < ttl:
        return _TR_CACHE["val"]
    entries = load_log(path)[-last:]
    val = summarize(entries, fetch, horizon_days=horizon_days) if entries else None
    _TR_CACHE.update(t=time.time(), key=key, val=val)
    return val
