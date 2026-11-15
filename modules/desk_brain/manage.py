"""5-minute paper trade management: fills, breakeven after T1, ATR trailing stop, T2 exit.
Paper only: nothing here talks to a broker."""
from __future__ import annotations

import json
import logging
import time

import pandas as pd

from . import config, journal
from .config import UNIVERSE
from .data import sources
from .tools.indicators import atr

log = logging.getLogger("desk.manage")
TRAIL_ATR = 1.5
PENDING_TTL = pd.Timedelta(hours=24)
LAST: dict = {"ts": None, "checked": 0, "changed": 0, "skipped": 0, "events": 0, "error": None}


def _ts(v) -> pd.Timestamp | None:
    if v in (None, ""):
        return None
    t = pd.Timestamp(v)
    return t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")


def _idx(df: pd.DataFrame) -> pd.DatetimeIndex:
    i = pd.DatetimeIndex(df.index)
    return i.tz_localize("UTC") if i.tz is None else i.tz_convert("UTC")


def manage(trade: dict, bars: pd.DataFrame) -> dict:
    """Walk 5m bars after the trade's last check and return its new state.
    Conservative: a bar that touches both the stop and a target counts as stop first."""
    d = 1 if trade["direction"] > 0 else -1
    entry, stop0, t1, t2 = float(trade["entry"]), float(trade["stop"]), float(trade["t1"]), float(trade["t2"])
    risk = abs(entry - stop0) or 1e-12
    r_of = lambda p: round(d * (p - entry) / risk, 4)  # noqa: E731
    status = trade.get("status", "open")
    stop = float(trade.get("current_stop") or stop0)
    partial = bool(trade.get("partial"))
    r_t1 = trade.get("r_t1")
    filled, closed, result = trade.get("filled"), trade.get("closed"), trade.get("result_r")
    events = list(json.loads(trade["events"])) if isinstance(trade.get("events"), str) else list(trade.get("events") or [])
    managed_at = trade.get("managed_at")
    out = lambda: {"status": status, "current_stop": stop, "partial": partial, "r_t1": r_t1,  # noqa: E731
                   "filled": filled, "closed": closed, "result_r": result, "events": events,
                   "managed_at": managed_at, "new_events": len(events) - n0}
    n0 = len(events)
    if status not in ("pending", "open") or bars is None or len(bars) == 0:
        return out()

    created = _ts(trade.get("created"))
    start = _ts(managed_at) or _ts(filled) or created
    idx = _idx(bars)
    atrs = pd.Series(atr(bars).values, index=idx)
    mask = (idx > start) if start is not None else slice(None)
    ev = lambda typ, price, t: events.append({"type": typ, "price": round(float(price), 6), "time": t.isoformat()})  # noqa: E731

    for t, (_, b) in zip(idx[mask], bars[mask].iterrows()):
        hi, lo, cl = float(b["High"]), float(b["Low"]), float(b["Close"])
        managed_at = t.isoformat()
        if status == "pending":
            if created is not None and t > created + PENDING_TTL:
                status, closed = "expired", t.isoformat()
                break
            if not (lo <= entry <= hi):
                continue
            status, filled = "open", t.isoformat()
            ev("filled", entry, t)
            # On the fill bar the order of events is unknown: only the stop is honoured.
            if (lo <= stop) if d > 0 else (hi >= stop):
                status, closed, result = "loss", t.isoformat(), -1.0
                ev("stop", stop, t)
                break
            continue
        hit_stop = (lo <= stop) if d > 0 else (hi >= stop)
        if hit_stop:
            result = r_of(stop)
            status = "win" if result > 0 else ("loss" if result < 0 else "be")
            closed = t.isoformat()
            ev("stop", stop, t)
            break
        if (hi >= t2) if d > 0 else (lo <= t2):
            status, closed, result = "win", t.isoformat(), r_of(t2)
            if not partial:
                ev("t1", t1, t)
            ev("t2", t2, t)
            break
        if not partial and ((hi >= t1) if d > 0 else (lo <= t1)):
            partial, r_t1 = True, r_of(t1)
            ev("t1", t1, t)
            if (entry > stop) if d > 0 else (entry < stop):
                stop = entry
                ev("be", stop, t)
            continue
        if partial:
            a = atrs.loc[t]
            if pd.notna(a):
                cand = cl - d * TRAIL_ATR * float(a)
                if (cand > stop) if d > 0 else (cand < stop):  # only ever tighten
                    stop = cand
                    ev("trail", stop, t)
    return out()


def run_once() -> dict:
    """Manage every open/pending journal row on 5m bars. Never places orders."""
    global LAST
    t0 = time.time()
    checked = changed = skipped = nev = 0
    for r in [x for x in journal.rows(500) if x["status"] in ("pending", "open")]:
        try:
            if "demo" in (r.get("data_source") or "") or r["symbol"] not in UNIVERSE:
                skipped += 1
                continue
            df, src = sources.prices(UNIVERSE[r["symbol"]]["yf"], "5m")
            if src == "demo" or df is None or df.empty:
                skipped += 1  # demo data is never journaled as a real result
                continue
            checked += 1
            st = manage(r, df)
            nev += st.pop("new_events")
            if st["managed_at"] and st["managed_at"] != r.get("managed_at"):
                journal.save_managed(r["id"], st)
                changed += 1
        except Exception:
            log.exception("manage failed for trade %s", r.get("id"))
    LAST = {"ts": pd.Timestamp.now(tz="UTC").isoformat(), "checked": checked, "changed": changed,
            "skipped": skipped, "events": nev, "error": None, "secs": round(time.time() - t0, 2)}
    return LAST
