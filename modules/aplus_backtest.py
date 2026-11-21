"""A+ setups walk-forward check (owner 2026-11-20: build the sandbox for the A+ setups).

Three setups from docs/research/A_PLUS_SETUPS.md, each with fixed mechanical rules and no tuning:
  pullback  : trend up (EMA50 rising, close above it) -> touch EMA21 -> bullish rejection bar -> long
  retest    : close breaks the 20-bar high in an uptrend -> returns to that level within 10 bars -> closes back above -> long
  trend_bar : (control) plain long at a random bar in an uptrend, same stop / target rules
Shorts are the mirror image and are included.

Rules: entry at the close of the signal bar; stop = 0.5 ATR beyond the level; target = 2R; max hold 48 bars;
stop first when both are touched in the same bar (pessimistic); cost 0.1% round trip, taken from R.
Verdict: "evidence" only if n >= 100, |t| > 3 and both chronological halves (70/30) have a positive mean R.
Otherwise "not evidence". Backtest on past candles only: NOT a forecast, NOT a live result.

Run: python -m modules.aplus_backtest  (GitHub Actions: .github/workflows/aplus-backtest.yml)"""
from __future__ import annotations

import json
import math
import os
import random
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "docs", "research", "aplus_backtest.json")
COST = 0.001          # 0.1% round trip
HOLD = 48
TARGET_R = 2.0
SYMS = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
TFS = ["1H", "4H"]


def ema(vals, n):
    out, k, e = [], 2 / (n + 1), None
    for v in vals:
        e = v if e is None else e + k * (v - e)
        out.append(e)
    return out


def atr(rows, n=14):
    tr = [max(r["h"] - r["l"], abs(r["h"] - rows[i - 1]["c"]), abs(r["l"] - rows[i - 1]["c"])) if i else r["h"] - r["l"] for i, r in enumerate(rows)]
    out, a = [], None
    for i, t in enumerate(tr):
        a = t if a is None else (a * (n - 1) + t) / n
        out.append(a)
    return out


def fetch_okx(sym, tf, pages=40, get=None):
    """Newest-first OKX history pages -> oldest-first rows. `get` is injectable for tests."""
    import requests
    get = get or (lambda url, params: requests.get(url, params=params, timeout=20).json())
    rows, after = [], None
    for _ in range(pages):
        params = {"instId": sym, "bar": tf, "limit": "100"}
        if after:
            params["after"] = after
        js = get("https://www.okx.com/api/v5/market/history-candles", params)
        data = js.get("data") or []
        if not data:
            break
        for d in data:
            rows.append({"t": int(d[0]), "o": float(d[1]), "h": float(d[2]), "l": float(d[3]), "c": float(d[4])})
        after = data[-1][0]
        time.sleep(0.15)
    rows = sorted({r["t"]: r for r in rows}.values(), key=lambda r: r["t"])
    return rows


def signals(rows):
    """-> list of (bar index, side, setup, level). Uses only bars up to the signal bar."""
    c = [r["c"] for r in rows]
    e21, e50, a = ema(c, 21), ema(c, 50), atr(rows)
    out = []
    for i in range(60, len(rows)):
        r = rows[i]
        up = e50[i] > e50[i - 1] and c[i] > e50[i]
        dn = e50[i] < e50[i - 1] and c[i] < e50[i]
        if up and abs(r["l"] - e21[i]) <= 0.2 * a[i] and r["c"] > r["o"] and r["c"] > e21[i]:
            out.append((i, 1, "pullback", e21[i]))
        if dn and abs(r["h"] - e21[i]) <= 0.2 * a[i] and r["c"] < r["o"] and r["c"] < e21[i]:
            out.append((i, -1, "pullback", e21[i]))
        hi20 = max(x["h"] for x in rows[i - 20:i])
        lo20 = min(x["l"] for x in rows[i - 20:i])
        if up and r["c"] > hi20:
            for j in range(i + 1, min(i + 11, len(rows))):
                if rows[j]["l"] <= hi20 + 0.2 * a[i] and rows[j]["c"] > hi20:
                    out.append((j, 1, "retest", hi20))
                    break
        if dn and r["c"] < lo20:
            for j in range(i + 1, min(i + 11, len(rows))):
                if rows[j]["h"] >= lo20 - 0.2 * a[i] and rows[j]["c"] < lo20:
                    out.append((j, -1, "retest", lo20))
                    break
    return out, a


def trade(rows, i, side, level, a):
    """Entry = close of bar i, stop 0.5 ATR beyond the level, target 2R, stop first. -> R after cost or None."""
    entry = rows[i]["c"]
    risk = (entry - (level - 0.5 * a[i])) if side > 0 else ((level + 0.5 * a[i]) - entry)
    if risk <= 0 or risk > 0.2 * entry:
        return None
    stop = entry - risk if side > 0 else entry + risk
    tgt = entry + TARGET_R * risk if side > 0 else entry - TARGET_R * risk
    for j in range(i + 1, min(i + 1 + HOLD, len(rows))):
        r = rows[j]
        hit_stop = r["l"] <= stop if side > 0 else r["h"] >= stop
        hit_tgt = r["h"] >= tgt if side > 0 else r["l"] <= tgt
        if hit_stop:
            return -1.0 - COST * entry / risk
        if hit_tgt:
            return TARGET_R - COST * entry / risk
    last = rows[min(i + HOLD, len(rows) - 1)]["c"]
    gain = (last - entry) if side > 0 else (entry - last)
    return gain / risk - COST * entry / risk


def stats(rs):
    n = len(rs)
    if n == 0:
        return {"n": 0, "meanR": None, "winPct": None, "t": None}
    m = sum(rs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in rs) / (n - 1)) if n > 1 else 0.0
    t = m / (sd / math.sqrt(n)) if sd > 0 else 0.0
    return {"n": n, "meanR": round(m, 3), "winPct": round(100 * sum(1 for x in rs if x > 0) / n, 1), "t": round(t, 2)}


def verdict(rs):
    s = stats(rs)
    if s["n"] < 100 or s["t"] is None or abs(s["t"]) <= 3:
        return "not evidence", s
    cut = int(len(rs) * 0.7)
    a, b = rs[:cut], rs[cut:]
    ok = bool(a) and bool(b) and sum(a) > 0 and sum(b) > 0
    return ("evidence (both halves positive)" if ok and s["meanR"] > 0 else "not evidence (halves disagree or negative)"), s


def run_on(rows):
    sig, a = signals(rows)
    res = {"pullback": [], "retest": [], "control": []}
    last = {}   # one open trade per setup + side: a new signal inside the hold window is skipped (no overlapping trades)
    for i, side, name, level in sig:
        if i - last.get((name, side), -10 ** 9) < HOLD:
            continue
        r = trade(rows, i, side, level, a)
        if r is not None:
            res[name].append((i, r))
            last[(name, side)] = i
    # control: same count per setup, random bars in an uptrend-or-downtrend context (same stop / target rules, level = close)
    rnd = random.Random(7)
    cand = [i for i in range(60, len(rows) - HOLD - 1)]
    for name in ("pullback", "retest"):
        k = len(res[name])
        picks = rnd.sample(cand, min(k, len(cand))) if k else []
        for i in sorted(picks):
            side = 1 if rnd.random() < 0.5 else -1
            r = trade(rows, i, side, rows[i]["c"], a)
            if r is not None:
                res["control"].append((i, r))
    return res


def main(get=None, out=OUT_JSON, pages=40):
    report = {"rules": {"hold_bars": HOLD, "target_R": TARGET_R, "cost_pct": COST * 100, "stop": "0.5 ATR beyond level", "entry": "close of signal bar"},
              "results": {}, "note": "Past candles only. Not a forecast, not a live result."}
    for sym in SYMS:
        for tf in TFS:
            rows = fetch_okx(sym, tf, pages=pages, get=get)
            if len(rows) < 120:
                report["results"][f"{sym} {tf}"] = {"error": f"only {len(rows)} candles"}
                continue
            res = run_on(rows)
            cut = int(len(rows) * 0.7)
            entry = {}
            for name, lst in res.items():
                rs = [r for _, r in lst]
                v, s = verdict(rs)
                entry[name] = {**s, "verdict": v, "trainR": round(sum(r for i, r in lst if i < cut) / max(1, sum(1 for i, _ in lst if i < cut)), 3),
                               "testR": round(sum(r for i, r in lst if i >= cut) / max(1, sum(1 for i, _ in lst if i >= cut)), 3)}
            report["results"][f"{sym} {tf}"] = {"bars": len(rows), "from": rows[0]["t"], "to": rows[-1]["t"], "setups": entry}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    return report


if __name__ == "__main__":
    rep = main()
    for k, v in rep["results"].items():
        if "error" in v:
            print(k, v["error"])
            continue
        for name, s in v["setups"].items():
            print(f"{k:14s} {name:10s} n={s['n']:4d} meanR={s['meanR']} t={s['t']} win%={s['winPct']} -> {s['verdict']}")
