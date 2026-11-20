#!/usr/bin/env python3
"""Backtest of the 2.6 PROVISIONAL trade plan (the one the Workspace indicator draws) on real candles.

Plan per setup (modules/two_six_chart.setups): u = leg / ratio, limit entry, stop = entry -/+ u,
TP1 = 1R, TP2 = 2R, stop wins a same-candle tie. Scoring without partial exits:
TP2 = +2R, stopped = -1R, TP1 then stop = -1R; setups still waiting / open / expired are left out.
Cost: cost_frac x entry per trade, converted to R. Control: for every closed setup, random bars of the
same file with the same side and the same u, entered at that bar's close and run through the same plan.

Input: JSON list of [t_ms, open, high, low, close] (e.g. Hyperliquid candleSnapshot) or CSV t,o,h,l,c.
Run: python3 research/strategies/2.6/backtest_plan.py gold_1h.json [--ratios 2.5 2.6 2.618 2.7]
"""
import argparse
import csv
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from modules import two_six_chart as tc  # noqa: E402

SCORE = {"TP2": 2.0, "stopped": -1.0, "TP1 then stop": -1.0}


def load(path):
    if path.endswith(".json"):
        rows = json.load(open(path))
    else:
        rows = [[float(x) for x in r[:5]] for r in csv.reader(open(path)) if r and r[0][:1].isdigit()]
    return [tc.es.Bar(str(int(r[0])), *map(float, r[1:5])) for r in rows]


def play_market(bars, i, side, u, cost):
    """Control trade: enter at bar i close, same stop / targets as the plan; R net of cost or None if unresolved."""
    e, sg = bars[i].close, 1 if side == "BUY" else -1
    stop, tp2 = e - sg * u, e + 2 * sg * u
    for b in bars[i + 1:]:
        if (b.low <= stop) if sg > 0 else (b.high >= stop):
            return -1.0 - cost
        if (b.high >= tp2) if sg > 0 else (b.low <= tp2):
            return 2.0 - cost
    return None


def stats(r):
    n = len(r)
    if n < 2:
        return {"n": n}
    m = sum(r) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in r) / (n - 1)) or 1e-12
    return {"n": n, "win_pct": round(100 * sum(x > 0 for x in r) / n, 1), "mean_R": round(m, 3), "t": round(m / sd * math.sqrt(n), 2)}


def run(bars, ratio, cost_frac, sw, wait, seed=7):
    plays = [p for p in tc.setups(bars, ratio=ratio, left=sw, right=sw, wait=wait) if p["status"] in SCORE]
    rnd, res, ctl = random.Random(seed), [], []
    for p in plays:
        u = abs(p["tp2"] - p["tp1"])   # the planned unit (a gap fill can move the entry onto the stop)
        c = cost_frac * p["entry"] / u
        res.append((p["known"], SCORE[p["status"]] - c, p["kind"]))
        for _ in range(20):
            x = play_market(bars, rnd.randrange(0, len(bars) - 2), p["side"], u, c)
            if x is not None:
                ctl.append(x)
    res.sort()
    cut = int(len(res) * 0.7)
    R = [x[1] for x in res]
    return {"ratio": ratio, "all": stats(R), "H1": stats([x[1] for x in res if x[2] == "H1"]),
            "H2": stats([x[1] for x in res if x[2] == "H2"]), "first70": stats(R[:cut]), "last30": stats(R[cut:]),
            "random_control": stats(ctl)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--ratios", nargs="+", type=float, default=[2.5, 2.6, 2.618, 2.7])
    ap.add_argument("--cost", type=float, default=0.0005, help="round-trip cost as a fraction of price")
    ap.add_argument("--sw", type=int, default=5)
    ap.add_argument("--wait", type=int, default=80)
    a = ap.parse_args()
    out = {}
    for f in a.files:
        bars = load(f)
        out[os.path.basename(f)] = {"bars": len(bars), "results": [run(bars, r, a.cost, a.sw, a.wait) for r in a.ratios]}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
