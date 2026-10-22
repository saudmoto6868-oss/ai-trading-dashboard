"""Order-flow forward-test logger and judge (owner 2026-10-22, from the flow manual's protocol).

Order-book and tape signals have no long history to backtest, so they are tested FORWARD: a collector polls the public OKX book and
trades, writes one row per symbol per poll with the features, and the judge later fills each row's forward mid-price return at fixed
horizons and tests a FROZEN rule on those rows - after costs, with a random-sign control and the same gate as the weekly lab
(n >= 100 non-overlapping signals, t > 3, both halves positive).

  python -m modules.flow_log collect BTC-USDT,ETH-USDT 900 2     # symbols, seconds, poll every N s  -> .flow_log.jsonl
  python -m modules.flow_log judge                                # evaluate the log with the frozen rules below

Features per row (all from public data, nothing is traded):
  imb   = (B - A) / (B + A) over the top 5 book levels (size at best 5 prices each side)
  ofi   = order-flow imbalance at the best bid / ask between this poll and the previous one (Cont-Kukanov-Stoikov style, coarse: one
          step per poll, not per book event), normalised by the mean top-of-book size
  cvd   = taker-buy minus taker-sell quote volume of the trades since the previous poll, normalised by their total (-1..+1)
  speed = trades per second since the previous poll
  spread_bps = (ask - bid) / mid in basis points
Poll cadence limits what these can see (a 2 s poll misses everything faster); that is stated, not hidden.
Costs: COST_BPS = taker fee both ways + half spread + slippage, a PLANNING number (override with FLOW_COST_BPS), not a quote."""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import requests

BASE = "https://www.okx.com/api/v5/market"
PATH = Path(os.environ.get("FLOW_LOG") or Path(__file__).resolve().parent.parent / ".flow_log.jsonl")   # next to the repo, whatever the working folder
COST_BPS = float(os.environ.get("FLOW_COST_BPS", "10"))   # 5 bps taker per side; spread/slippage come on top, so this is a floor
HORIZONS = (5, 30, 300, 3600)   # seconds
GATE_N, GATE_T = 100, 3.0

# frozen rules: a rule is changed only by adding a new id (every variant tried counts as another trial, see judge()).
# rule id -> (feature, threshold on |feature|, direction: +1 = trade WITH the feature sign, -1 = AGAINST it)
RULES = {
    "imb_with": ("imb", 0.5, +1), "imb_against": ("imb", 0.5, -1),
    "ofi_with": ("ofi", 1.0, +1), "cvd_with": ("cvd", 0.5, +1), "cvd_against": ("cvd", 0.5, -1),
}


def _get(path, params, timeout=8):
    r = requests.get(BASE + path, params=params, timeout=timeout)
    r.raise_for_status()
    j = r.json()
    if j.get("code") != "0":
        raise RuntimeError(j.get("msg") or "okx error")
    return j["data"]


def features(book: dict, prev: dict | None, trades: list, dt: float) -> dict | None:
    """One row of features from a book ({'bids': [[px, sz]...], 'asks': ...}, best first), the previous book, the trades since the
    previous poll ([{'px', 'sz', 'side'}]) and the seconds between polls. None if the book is empty / crossed."""
    if not book["bids"] or not book["asks"]:
        return None
    pb, qb = float(book["bids"][0][0]), float(book["bids"][0][1])
    pa, qa = float(book["asks"][0][0]), float(book["asks"][0][1])
    if pb >= pa:
        return None
    mid = (pb + pa) / 2
    B = sum(float(x[1]) for x in book["bids"][:5]); A = sum(float(x[1]) for x in book["asks"][:5])
    f = {"mid": mid, "spread_bps": round((pa - pb) / mid * 1e4, 3), "imb": round((B - A) / (B + A), 4) if B + A else 0.0,
         "ofi": 0.0, "cvd": 0.0, "speed": 0.0}
    if prev and prev.get("bids") and prev.get("asks"):
        ppb, pqb = float(prev["bids"][0][0]), float(prev["bids"][0][1])
        ppa, pqa = float(prev["asks"][0][0]), float(prev["asks"][0][1])
        e_b = (qb if pb >= ppb else 0.0) - (pqb if pb <= ppb else 0.0)
        e_a = (qa if pa <= ppa else 0.0) - (pqa if pa >= ppa else 0.0)
        scale = (qb + qa + pqb + pqa) / 4 or 1.0
        f["ofi"] = round((e_b - e_a) / scale, 4)
    if trades:
        buy = sum(float(t["px"]) * float(t["sz"]) for t in trades if t["side"] == "buy")
        sell = sum(float(t["px"]) * float(t["sz"]) for t in trades if t["side"] == "sell")
        f["cvd"] = round((buy - sell) / (buy + sell), 4) if buy + sell else 0.0
        f["speed"] = round(len(trades) / dt, 3) if dt > 0 else 0.0
    return f


def _poll(s):
    """One symbol's book and trades (two public calls). Returns (book, trades) or an exception object."""
    try:
        b = _get("/books", {"instId": s, "sz": 5})[0]
        return {"bids": b["bids"], "asks": b["asks"]}, _get("/trades", {"instId": s, "limit": 100})
    except Exception as e:
        return e


def collect(symbols, seconds: int = 900, every: float = 2.0, path: Path = PATH, log=print) -> int:
    """Poll the OKX book and trades of every symbol (in parallel) each `every` s for `seconds` s and append rows to `path`. Returns
    rows written. Failed polls are skipped and counted, never retried in a tight loop. Real cadence = max(every, request time)."""
    from concurrent.futures import ThreadPoolExecutor
    prev, seen, t_prev, rows, bad, loops = {}, {}, {}, 0, 0, 0
    end = time.time() + seconds
    with open(path, "a", encoding="utf-8") as fh, ThreadPoolExecutor(max(1, len(symbols))) as pool:
        while time.time() < end:
            t0 = time.time(); loops += 1
            for s, res in zip(symbols, pool.map(_poll, symbols)):
                if isinstance(res, Exception):
                    bad += 1
                    log(f"{s}: {type(res).__name__}: {res}")
                    continue
                book, tr = res
                new = [t for t in tr if int(t["tradeId"]) > seen.get(s, 0)] if s in seen else []   # first poll only sets the marker
                seen[s] = max([int(t["tradeId"]) for t in tr] + [seen.get(s, 0)])
                dt = t0 - t_prev.get(s, t0)
                f = features(book, prev.get(s), new, dt) if s in t_prev else None
                prev[s], t_prev[s] = book, t0
                if f:
                    fh.write(json.dumps({"t": round(t0, 3), "sym": s, **f}) + "\n"); rows += 1
            fh.flush()
            time.sleep(max(0.0, every - (time.time() - t0)))
    log(f"wrote {rows} rows in {loops} polls, {bad} failed requests -> {path}")
    return rows


def load(path: Path = PATH) -> list:
    out = []
    try:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    except OSError:
        return []
    return sorted(out, key=lambda r: (r["sym"], r["t"]))


def label(rows: list, horizons=HORIZONS, tol: float = 0.5) -> list:
    """Adds ret_<h> (forward mid return in bps) to each row: the first later row of the same symbol at least h seconds ahead and no
    more than h*(1+tol)+poll gap ahead; rows with no such future row get None for that horizon."""
    by = {}
    for r in rows:
        by.setdefault(r["sym"], []).append(r)
    for rs in by.values():
        ptr = {h: 0 for h in horizons}   # one monotonic pointer per horizon: the first later row at least h seconds ahead
        for i, r in enumerate(rs):
            for h in horizons:
                k = max(ptr[h], i + 1)
                while k < len(rs) and rs[k]["t"] - r["t"] < h:
                    k += 1
                ptr[h] = k
                r[f"ret_{h}"] = (round((rs[k]["mid"] / r["mid"] - 1) * 1e4, 3)
                                 if k < len(rs) and rs[k]["t"] - r["t"] <= h * (1 + tol) + 5 else None)
    return rows


def _t_stat(x):
    n = len(x)
    if n < 3:
        return 0.0
    m = sum(x) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in x) / (n - 1))
    return m / (sd / math.sqrt(n)) if sd > 0 else 0.0


def evaluate(rows: list, rule_id: str, horizon: int, cost_bps: float = COST_BPS, seed: int = 0) -> dict:
    """Test one frozen rule at one horizon on labelled rows. Signals are NON-OVERLAPPING (next signal of a symbol only after `horizon`
    s), cost is charged once per trade, the control re-draws the SIGN at random on the same signal bars. verdict uses the lab's gate."""
    import random
    feat, thr, d = RULES[rule_id]
    rng = random.Random(seed)
    sig = []
    last = {}
    for r in rows:
        v, fr = r.get(feat), r.get(f"ret_{horizon}")
        if v is None or fr is None or abs(v) < thr:
            continue
        if r["t"] - last.get(r["sym"], -1e18) < horizon:
            continue
        last[r["sym"]] = r["t"]
        sign = (1 if v > 0 else -1) * d
        sig.append((r["t"], sign * fr, rng.choice((1, -1)) * fr))
    n = len(sig)
    gross = [g for _t, g, _c in sig]; net = [g - cost_bps for g in gross]; ctl = [c - cost_bps for _t, _g, c in sig]
    half = n // 2
    h1, h2 = net[:half], net[half:]
    out = {"rule": rule_id, "horizon": horizon, "n": n, "gross_bps": round(sum(gross) / n, 3) if n else None,
           "net_bps": round(sum(net) / n, 3) if n else None, "t": round(_t_stat(net), 2), "control_net_bps": round(sum(ctl) / n, 3) if n else None,
           "half1": round(sum(h1) / len(h1), 3) if h1 else None, "half2": round(sum(h2) / len(h2), 3) if h2 else None}
    out["pass"] = bool(n >= GATE_N and out["t"] > GATE_T and out["net_bps"] > 0 and (out["half1"] or 0) > 0 and (out["half2"] or 0) > 0)
    return out


def judge(rows: list, cost_bps: float = COST_BPS) -> dict:
    """Every frozen rule at every horizon. 'trials' = how many were tried (the multiple-testing count shown next to the verdicts)."""
    label(rows)
    res = [evaluate(rows, rid, h, cost_bps) for rid in RULES for h in HORIZONS]
    span = (rows[-1]["t"] - rows[0]["t"]) if rows else 0
    return {"rows": len(rows), "symbols": sorted({r["sym"] for r in rows}), "hours": round(span / 3600, 2), "cost_bps": cost_bps,
            "trials": len(res), "results": res, "passed": [r for r in res if r["pass"]]}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["collect"]:
        collect(a[1].split(","), int(a[2]) if len(a) > 2 else 900, float(a[3]) if len(a) > 3 else 2.0)
    elif a[:1] == ["judge"]:
        j = judge(load())
        print(f"{j['rows']} rows, {j['symbols']}, {j['hours']} h, cost {j['cost_bps']} bps, trials {j['trials']}, passed {len(j['passed'])}")
        for r in j["results"]:
            if r["n"]:
                print(f"{r['rule']:12s} {r['horizon']:>5}s n={r['n']:>5} gross={r['gross_bps']:>8} net={r['net_bps']:>8} t={r['t']:>6} ctl={r['control_net_bps']:>8} {'PASS' if r['pass'] else ''}")
    else:
        print(__doc__)
