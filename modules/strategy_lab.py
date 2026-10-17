"""Strategy lab: every detector tested ON ITS OWN, on real candles, against a random-direction baseline.

Method (one rule for every strategy so they can be compared):
  * walk forward; at every `stride`-th bar run detect_all on the bars known at that moment (last WIN bars);
  * each signal = trade in its own direction: entry = close, stop = 1.5 x ATR14, target = 1.5R (2.25 ATR);
    follow the next bars until stop / target (same bar touching both = STOP, pessimistic) or HORIZON bars (then mark-to-market R);
  * baseline = a random direction at the same bars with the same stop / target (break-even win rate at 1.5R is 40%);
  * one sample per key per COOLDOWN bars (a setup stays 'live' for several bars);
  * conflicts = two detectors pointing opposite ways on the same bar; confluence = how many distinct families agree.
  * 'edge' needs n >= 30, avg R above 0 AND about 3 standard errors above the random baseline (many detectors are tested at once,
    so a looser bar would flag one by pure luck - the random-walk self-test did exactly that at 2 sigma).
No costs / slippage / funding: real results are worse. Small n (< 30) is printed but never ranked.
Run:  python -m modules.strategy_lab [SYMBOLS...]   -> data/strategy_lab.json + STRATEGY_LAB.md
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

from modules.signals import BULL, atr_series, detect_all

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON, OUT_MD = ROOT / "data" / "strategy_lab.json", ROOT / "STRATEGY_LAB.md"
TFS = ("1m", "15m", "1h", "4h", "1d")
HORIZON = {"1m": 60, "15m": 64, "1h": 48, "4h": 30, "1d": 20}
BARS = {"1m": 1200, "15m": 1500, "1h": 1500, "4h": 1200, "1d": 900}
STOP_ATR, RR, WIN, COOLDOWN, MIN_N = 1.5, 1.5, 400, 6, 30
TREND_N = 100   # trend = sign of the return over the last 100 bars (time-series momentum); "with" = signal on the trend side
SYMBOLS = ("BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "BNB-USDT", "DOGE-USDT", "HL:xyz:GOLD", "HL:xyz:SP500")
# analysis school of each detector key (fundamental / macro is a context filter here, not a signal)
SCHOOL = {
    "ma_cross": "Trend (MA)", "ema_stack": "Trend (MA)", "vwap": "Trend (MA)", "donch": "Trend (hedge fund)", "sma1040": "Trend (hedge fund)",
    "turtle55": "Trend (hedge fund)", "ob": "SMC / ICT", "fvg": "SMC / ICT", "breaker": "SMC / ICT", "unicorn": "SMC / ICT", "msb_ob": "SMC / ICT",
    "ote": "Fibonacci", "fib": "Fibonacci", "cisd": "SMC / ICT", "m2022": "SMC / ICT", "sweep": "Liquidity", "liqline": "Liquidity", "zombie": "Liquidity",
    "crt": "Liquidity", "judas": "Time (sessions)", "sess_amd": "Time (sessions)", "orb": "Time (sessions)", "kzs": "Time (sessions)", "po3": "Time (sessions)",
    "ew3": "Elliott wave", "ew5": "Elliott wave", "abc": "Elliott wave", "wavec": "Elliott wave", "rsi_div": "Momentum / divergence",
    "macd_div": "Momentum / divergence", "level": "Levels / breakouts", "breakout": "Levels / breakouts", "ohl_open": "Levels / breakouts",
    "ohl_break": "Levels / breakouts", "tlbreak": "Levels / breakouts", "smt": "Intermarket (SMT)",
}


def _fetch(sym, tf, bars):
    if sym.startswith("HL:"):
        from modules.hl_feed import get_klines
        return get_klines(sym, tf, bars)
    from modules.backtest_tf import _BAR, fetch_long
    _BAR.setdefault("15m", "15m"); _BAR.setdefault("4h", "4H")
    return fetch_long(sym, tf, bars)


def _outcome(hi, lo, cl, i, d, stop_d, H):
    """R result of a trade opened at close i in direction d (+1 / -1)."""
    e = cl[i]; sl = e - d * stop_d; tp = e + d * RR * stop_d
    for j in range(i + 1, min(len(cl), i + 1 + H)):
        if (lo[j] <= sl) if d > 0 else (hi[j] >= sl):
            return -1.0
        if (hi[j] >= tp) if d > 0 else (lo[j] <= tp):
            return RR
    j = min(len(cl) - 1, i + H)
    return float(np.clip(d * (cl[j] - e) / stop_d, -1.0, RR))


def walk(df, tf, stride=4, seed=0):
    """-> list of events {i, key, fam, d, r, base}, plus per-bar groups for conflicts / confluence."""
    rng = np.random.RandomState(seed)
    hi, lo, cl = (df[c].values for c in ("high", "low", "close"))
    atr = atr_series(df, 14).values
    H, last, events, bars = HORIZON[tf], {}, [], []
    for i in range(150, len(df) - 2, stride):
        sigs, _ = detect_all(df.iloc[max(0, i + 1 - WIN):i + 1].reset_index(drop=True))
        if not sigs or not atr[i] > 0:
            continue
        rb = _outcome(hi, lo, cl, i, 1 if rng.rand() < .5 else -1, STOP_ATR * atr[i], H)
        here = {}
        for s in sigs:
            d = 1 if s["direction"] == BULL else -1
            here.setdefault(s["key"], (d, s["family"]))
        if here:
            bars.append({k: v[0] for k, v in here.items()} | {"_fam": {v[1] + ("+" if v[0] > 0 else "-") for v in here.values()},
                                                              "_r": {d: _outcome(hi, lo, cl, i, d, STOP_ATR * atr[i], H) for d in (1, -1)}})
        tr = int(np.sign(cl[i] - cl[i - TREND_N])) if i >= TREND_N else 0
        for k, (d, fam) in here.items():
            if i - last.get(k, -10**9) < COOLDOWN:
                continue
            last[k] = i
            events.append({"key": k, "fam": fam, "d": d, "r": _outcome(hi, lo, cl, i, d, STOP_ATR * atr[i], H), "base": rb,
                           "trend": "with" if tr == d else "against" if tr else "flat"})
    return events, bars


def _stat(rs):
    x = np.asarray(rs, float); n = len(x)
    if not n:
        return {"n": 0}
    win = float((x >= RR - 1e-9).mean())
    return {"n": n, "win": round(100 * win, 1), "avgR": round(float(x.mean()), 3), "sumR": round(float(x.sum()), 1)}


def summarize(all_events, all_bars):
    per = defaultdict(list); base = defaultdict(list)
    for tf, sym, ev in all_events:
        for e in ev:
            for g in ((e["key"], "all", "all"), (e["key"], tf, "all"), (e["key"], "all", "long" if e["d"] > 0 else "short"), (e["key"], "all", "trend-" + e["trend"]),
                      ("*ALL*", tf, "trend-" + e["trend"]), ("*ALL*", "all", "trend-" + e["trend"])):
                per[g].append(e["r"]); base[g].append(e["base"])
    rows = []
    for (k, tf, side), rs in per.items():
        s = _stat(rs); b = _stat(base[(k, tf, side)])
        se = 1.0 / np.sqrt(max(s["n"], 1))          # rough: R std ~ 1.2, so 2*se*1.2 ~ 95% band of avgR
        rows.append({"key": k, "school": SCHOOL.get(k, "Other"), "tf": tf, "side": side, **s, "base_win": b.get("win"), "base_avgR": b.get("avgR"),
                     "edge": bool(s["n"] >= MIN_N and s["avgR"] - b["avgR"] > 3.6 * se and s["avgR"] > 0)})   # ~3 sigma: ~35 detectors are tested at once, a 2-sigma bar would flag one by luck
    # conflicts: detectors pointing opposite ways on the same bar
    conf, co = defaultdict(int), defaultdict(int)
    for tf, sym, bars in all_bars:
        for b in bars:
            ks = sorted(k for k in b if not k.startswith("_"))
            for a, c in itertools.combinations(ks, 2):
                co[(a, c)] += 1
                if b[a] != b[c]:
                    conf[(a, c)] += 1
    conflicts = sorted(({"a": a, "b": c, "together": co[(a, c)], "opposite": n, "rate": round(100 * n / co[(a, c)], 1)}
                        for (a, c), n in conf.items() if co[(a, c)] >= 20), key=lambda r: -r["opposite"])[:25]
    # confluence: does agreement of more families help? (net direction = majority of family votes on that bar)
    cfl = defaultdict(list)
    for tf, sym, bars in all_bars:
        for b in bars:
            up = len({f[:-1] for f in b["_fam"] if f.endswith("+")}); dn = len({f[:-1] for f in b["_fam"] if f.endswith("-")})
            if up == dn:
                continue
            d = 1 if up > dn else -1; agree = max(up, dn); against = min(up, dn)
            cfl[f"{min(agree, 4)}{'+' if agree >= 4 else ''} families" + (" (with opposition)" if against else "")].append(b["_r"][d])
    return rows, conflicts, {k: _stat(v) for k, v in sorted(cfl.items())}


def report(rows, conflicts, cfl, meta):
    ok = [r for r in rows if r["tf"] == "all" and r["side"] == "all" and r["key"] != "*ALL*"]
    ok.sort(key=lambda r: (r["n"] >= MIN_N, r.get("avgR", -9)), reverse=True)
    L = [f"# Strategy lab - real candles ({time.strftime('%Y-%m-%d', time.gmtime(meta['built']))})", "",
         f"Symbols: {', '.join(meta['symbols'])} · timeframes: {', '.join(meta['tfs'])} · stop {STOP_ATR} ATR, target {RR}R, "
         f"break-even win rate {round(100 / (1 + RR))}% · no costs (real results are worse) · n < {MIN_N} = not evidence.", "",
         "## Every detector on its own (all timeframes)", "", "| rank | key | school | n | win % | avg R | random win % | random avg R | edge |", "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(ok, 1):
        L.append(f"| {i} | {r['key']} | {r['school']} | {r['n']} | {r.get('win')} | {r.get('avgR')} | {r.get('base_win')} | {r.get('base_avgR')} | {'YES' if r['edge'] else ''} |")
    L += ["", "## Best timeframe per detector (n >= %d)" % MIN_N, "", "| key | tf | n | win % | avg R |", "|---|---|---|---|---|"]
    for k in sorted({r["key"] for r in rows}):
        c = [r for r in rows if r["key"] == k and r["tf"] != "all" and r["side"] == "all" and r["n"] >= MIN_N]
        if c:
            b = max(c, key=lambda r: r["avgR"]); L.append(f"| {k} | {b['tf']} | {b['n']} | {b['win']} | {b['avgR']} |")
    L += ["", "## Long vs short", "", "| key | long n | long avg R | short n | short avg R |", "|---|---|---|---|---|"]
    for k in sorted({r["key"] for r in rows}):
        lo_ = next((r for r in rows if r["key"] == k and r["side"] == "long"), {}); sh = next((r for r in rows if r["key"] == k and r["side"] == "short"), {})
        L.append(f"| {k} | {lo_.get('n', 0)} | {lo_.get('avgR')} | {sh.get('n', 0)} | {sh.get('avgR')} |")
    L += ["", "## Trend filter: signal WITH vs AGAINST the 100-bar trend (time-series momentum)", "", "| key | with n | with win % | with avg R | against n | against win % | against avg R |", "|---|---|---|---|---|---|---|"]
    for k in ["*ALL*"] + sorted({r["key"] for r in rows if r["key"] != "*ALL*"}):
        w = next((r for r in rows if r["key"] == k and r["tf"] == "all" and r["side"] == "trend-with"), {}); a = next((r for r in rows if r["key"] == k and r["tf"] == "all" and r["side"] == "trend-against"), {})
        L.append(f"| {k} | {w.get('n', 0)} | {w.get('win')} | {w.get('avgR')} | {a.get('n', 0)} | {a.get('win')} | {a.get('avgR')} |")
    L += ["", "## Conflicts (pointing opposite ways on the same bar)", "", "| a | b | together | opposite | % |", "|---|---|---|---|---|"]
    L += [f"| {c['a']} | {c['b']} | {c['together']} | {c['opposite']} | {c['rate']} |" for c in conflicts]
    L += ["", "## Confluence: more agreeing families = better?", "", "| agreeing families | n | win % | avg R |", "|---|---|---|---|"]
    L += [f"| {k} | {v['n']} | {v.get('win')} | {v.get('avgR')} |" for k, v in cfl.items()]
    return "\n".join(L) + "\n"


def run(symbols=SYMBOLS, tfs=TFS, stride=4, fetch=_fetch, log=print):
    evs, brs, done = [], [], []
    for sym in symbols:
        for tf in tfs:
            t0 = time.time()
            try:
                df = fetch(sym, tf, BARS[tf])
            except Exception as e:
                log(f"skip {sym} {tf}: {type(e).__name__} {e}")
                continue
            if df is None or len(df) < 300:
                log(f"skip {sym} {tf}: too few candles"); continue
            ev, br = walk(df.reset_index(drop=True), tf, stride)
            evs.append((tf, sym, ev)); brs.append((tf, sym, br)); done.append(f"{sym} {tf}")
            log(f"{sym} {tf}: {len(df)} bars, {len(ev)} signals, {time.time() - t0:.0f}s")
    rows, conflicts, cfl = summarize(evs, brs)
    meta = {"built": int(time.time()), "symbols": list(symbols), "tfs": list(tfs), "series": done, "stop_atr": STOP_ATR, "rr": RR}
    return {"meta": meta, "rows": rows, "conflicts": conflicts, "confluence": cfl}


if __name__ == "__main__":
    syms = tuple(sys.argv[1:]) or SYMBOLS
    res = run(syms, stride=int(os.environ.get("LAB_STRIDE", "4")))
    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(res, indent=1))
    OUT_MD.write_text(report(res["rows"], res["conflicts"], res["confluence"], res["meta"]))
    print(OUT_MD.read_text()[:3000])
