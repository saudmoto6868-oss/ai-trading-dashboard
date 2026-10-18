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
GZ_BARS = {"15m": 5000, "1h": 5000, "4h": 3000, "1d": 1500}   # longer history for the Gann zone out-of-sample test (more trades)
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


def _outcome(hi, lo, cl, i, d, stop_d, H, rr=None, be=False):
    """R result of a trade opened at close i in direction d (+1 / -1).
    rr = reward multiple of the target (default RR); be = move the stop to entry once price has gone 1R in favour."""
    rr = RR if rr is None else rr
    e = cl[i]; sl = e - d * stop_d; tp = e + d * rr * stop_d; moved = False
    for j in range(i + 1, min(len(cl), i + 1 + H)):
        if (lo[j] <= sl) if d > 0 else (hi[j] >= sl):
            return 0.0 if moved else -1.0
        if (hi[j] >= tp) if d > 0 else (lo[j] <= tp):
            return rr
        if be and not moved and ((hi[j] - e) if d > 0 else (e - lo[j])) >= stop_d:
            sl, moved = e, True
    j = min(len(cl) - 1, i + H)
    return float(np.clip(d * (cl[j] - e) / stop_d, -1.0, rr))


# exit variants tested on the SAME entries: target multiple and break-even stop (the question: which RR / exit gives the best expectancy)
VARIANTS = {"rr1.0": (1.0, False), "rr1.5": (1.5, False), "rr2.0": (2.0, False), "rr3.0": (3.0, False), "rr1.5_be": (1.5, True), "rr2.0_be": (2.0, True)}


LOC_N, VOL_N, REG_N = 50, 20, 100
CHAIN = ("htf", "loc", "vol", "reg", "time")   # institution-style layers checked on top of each detector (docs/PIPELINE.md)


def chain_ctx(hi, lo, cl, vol, natr, i):
    """Context known at close i (no look-ahead): position in the last LOC_N-bar range, relative volume, volatility regime."""
    a = max(0, i + 1 - LOC_N); h, l = hi[a:i + 1].max(), lo[a:i + 1].min()
    pos = (cl[i] - l) / (h - l) if h > l else .5
    v0 = vol[max(0, i - VOL_N):i]; rv = vol[i] / v0.mean() if len(v0) and v0.mean() > 0 else 0.0
    r0 = natr[max(0, i - REG_N):i]; r0 = r0[r0 > 0]
    reg = natr[i] / np.median(r0) if len(r0) else 1.0
    return {"pos": float(pos), "rv": float(rv), "reg": float(reg)}


def chain_layers(ctx, d, tr, ses):
    """Which chain layers agree with a trade in direction d. htf = 100-bar trend on its side; loc = long in the discount third /
    short in the premium third of the 50-bar range; vol = bar volume >= 1.2x its 20-bar mean; reg = volatility not dead
    (ATR% >= 0.8x its 100-bar median); time = London or New York session (daily bars: always)."""
    p = ctx["pos"]
    return {"htf": tr == d, "loc": p <= 1 / 3 if d > 0 else p >= 2 / 3, "vol": ctx["rv"] >= 1.2, "reg": ctx["reg"] >= .8,
            "time": ses is None or ses.startswith(("London", "New York"))}


def grade(layers):
    """A+++ = all 5 layers, A+ = 4, A = 3, B = 2, C = 0-1 (same letters as the Setup Card target)."""
    n = sum(bool(layers.get(k)) for k in CHAIN)
    return "A+++" if n == 5 else "A+" if n == 4 else "A" if n == 3 else "B" if n == 2 else "C"


def walk(df, tf, stride=4, seed=0):
    """-> list of events {i, key, fam, d, r, base}, plus per-bar groups for conflicts / confluence."""
    rng = np.random.RandomState(seed)
    hi, lo, cl = (df[c].values for c in ("high", "low", "close"))
    atr = atr_series(df, 14).values
    H, last, events, bars = HORIZON[tf], {}, [], []
    vol = df["volume"].values.astype(float) if "volume" in df else np.zeros(len(df))
    natr = atr / np.where(cl > 0, cl, 1)
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
        ts = df["time"].iloc[i]; hr = ts.hour
        ses = None if tf == "1d" else "Asia 00-07" if hr < 7 else "London 07-12" if hr < 12 else "New York 12-20" if hr < 20 else "Late 20-24"
        dow = ts.strftime("%a")
        ctx = chain_ctx(hi, lo, cl, vol, natr, i)
        for k, (d, fam) in here.items():
            if i - last.get(k, -10**9) < COOLDOWN:
                continue
            last[k] = i
            events.append({"key": k, "fam": fam, "d": d, "r": _outcome(hi, lo, cl, i, d, STOP_ATR * atr[i], H), "base": rb,
                           "var": {n: _outcome(hi, lo, cl, i, d, STOP_ATR * atr[i], H, rr=v[0], be=v[1]) for n, v in VARIANTS.items()},
                           "trend": "with" if tr == d else "against" if tr else "flat", "ses": ses, "dow": dow,
                           "chain": chain_layers(ctx, d, tr, ses), "oos": i >= len(df) // 2})
    return events, bars


def _stat(rs):
    x = np.asarray(rs, float); n = len(x)
    if not n:
        return {"n": 0}
    win = float((x >= RR - 1e-9).mean())
    return {"n": n, "win": round(100 * win, 1), "avgR": round(float(x.mean()), 3), "sumR": round(float(x.sum()), 1)}


def chain_row(name, rs, base, ins, oos):
    """One chain-table row: stats, random-direction baseline, paired t vs random, in-sample vs out-of-sample halves."""
    s = _stat(rs); b = _stat(base); d = np.asarray(rs, float) - np.asarray(base, float)
    t = float(d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))) if len(d) > 2 and d.std() > 0 else 0.0
    return {"key": "*CHAIN*", "school": "Chain", "tf": "all", "side": name, **s, "base_win": b.get("win"), "base_avgR": b.get("avgR"),
            "t": round(t, 2), "is_n": len(ins), "is_avgR": _stat(ins).get("avgR"), "oos_n": len(oos), "oos_avgR": _stat(oos).get("avgR"),
            "edge": bool(s["n"] >= 100 and t > 3 and (_stat(oos).get("avgR") or 0) > 0 and (_stat(ins).get("avgR") or 0) > 0)}


def summarize(all_events, all_bars):
    per = defaultdict(list); base = defaultdict(list)
    for tf, sym, ev in all_events:
        for e in ev:
            for g in (((e["key"], "all", "all"), (e["key"], tf, "all"), (e["key"], "all", "long" if e["d"] > 0 else "short"), (e["key"], "all", "trend-" + e["trend"]),
                      ("*ALL*", tf, "trend-" + e["trend"]), ("*ALL*", "all", "trend-" + e["trend"]))
                      + ((("*ALL*", "all", "ses-" + e["ses"]), (e["key"], "all", "ses-" + e["ses"])) if e.get("ses") else ()) + ((("*ALL*", "all", "dow-" + e["dow"]),) if e.get("dow") else ())):
                per[g].append(e["r"]); base[g].append(e["base"])
    chain = defaultdict(lambda: [[], [], [], []])   # r, base, r in-sample half, r out-of-sample half
    for tf, sym, ev in all_events:
        for e in ev:
            if "chain" not in e:
                continue
            g = grade(e["chain"]); gs = ["grade " + g] + ["layer " + k for k in CHAIN if e["chain"][k]] + ["no " + k for k in CHAIN if not e["chain"][k]]
            gs += ["grade " + g + " / " + e["key"]]
            for name in gs + ["all signals"]:
                c = chain[name]; c[0].append(e["r"]); c[1].append(e["base"]); c[3 if e.get("oos") else 2].append(e["r"])
    rows = [chain_row(k, *v) for k, v in chain.items()]
    var = defaultdict(list)
    for tf, sym, ev in all_events:
        for e in ev:
            for n, r in (e.get("var") or {}).items():
                var[(n, "all")].append(r); var[(n, e["key"])].append(r)
    for (n, k), rs in var.items():
        x = np.asarray(rs, float); se = 1.0 / np.sqrt(max(len(x), 1))
        rows.append({"key": "*VAR*" if k == "all" else k, "school": "exit", "tf": "all", "side": n, "n": len(x), "win": round(100 * float((x > 0).mean()), 1),
                     "avgR": round(float(x.mean()), 3), "sumR": round(float(x.sum()), 1), "t": round(float(x.mean() / (x.std(ddof=1) * se)) if len(x) > 2 and x.std() > 0 else 0.0, 2)})
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


GANN_CYC, GANN_TOL, PIV_K = (30, 45, 60, 90, 120, 144, 180), 2, 5


def gann_cycles(hi, lo):
    """Gann time cycles: from every swing pivot (extreme of +-PIV_K bars), is there another pivot within +-GANN_TOL bars of
    pivot + 30/45/60/90/120/144/180 bars MORE often than at ordinary offsets (25..185 bars, away from the Gann numbers)?
    Returns hit counts {gann: [hits, tries], control: [hits, tries]}."""
    hi, lo = np.asarray(hi, float), np.asarray(lo, float); n = len(hi); K = PIV_K
    piv = np.zeros(n, bool)
    for i in range(K, n - K):
        w_h, w_l = hi[i - K:i + K + 1], lo[i - K:i + K + 1]
        piv[i] = hi[i] == w_h.max() or lo[i] == w_l.min()
    cum = np.concatenate([[0], np.cumsum(piv)])
    ctrl = [o for o in range(25, 186) if all(abs(o - g) > 2 * GANN_TOL for g in GANN_CYC)]
    rng = np.convolve(hi - lo, np.ones(14) / 14, mode="same")   # ATR proxy (mean range of 14 bars)
    # shapes with 3..9 sides on the 360-degree cycle: points where >= 3 shapes meet (120 / 180 / 240 / 360 degrees);
    # cycle length = price of one Square-of-9 turn / ATR (the indicator's auto mode), clamped 30..720 bars
    frac = {}
    for sides in range(3, 10):
        for k in range(1, sides + 1):
            f = round(k / sides, 6); frac[f] = frac.get(f, 0) + 1
    strong = [f for f, c in frac.items() if c >= 3]
    out = {"gann": [0, 0], "control": [0, 0], "shapes": [0, 0], "shapes_ctrl": [0, 0]}
    anchors = np.flatnonzero(piv)
    cyc = []
    for a in anchors:
        pa = hi[a] if hi[a] == hi[max(0, a - K):a + K + 1].max() else lo[a]
        turn = abs((np.sqrt(pa) + 2) ** 2 - pa); cyc.append(int(min(720, max(30, round(turn / max(rng[a], 1e-12))))))
    # control = the SAME shape points but with the cycle length of another (random) swing: identical spread of distances,
    # so it only tests whether THIS swing's price-time square matters (a fixed set of other offsets was biased: self-test +2 sigma)
    perm = np.random.default_rng(7).permutation(len(cyc)) if cyc else []
    for ai, a in enumerate(anchors):
        bars, bars_c = cyc[ai], cyc[perm[ai]]
        sh = sorted({int(round(f * bars)) for f in strong})
        sh_ctrl = sorted({int(round(f * bars_c)) for f in strong})
        for grp, offs in (("gann", GANN_CYC), ("control", ctrl), ("shapes", sh), ("shapes_ctrl", sh_ctrl)):
            for o in offs:
                j0, j1 = a + o - GANN_TOL, a + o + GANN_TOL
                if j1 >= n - K:
                    continue
                out[grp][0] += int(cum[j1 + 1] - cum[j0] > 0); out[grp][1] += 1
    return out


SYNODIC, NEW_MOON_REF = 29.530588853, 947182440.0   # mean synodic month (days); a new moon on 2000-01-06 18:14 UTC (unix seconds)


def lunar_split(times, closes):
    """Dichev & Janes (2001) style: daily close-to-close returns of the 15 days around new moons vs the 15 days around full moons.
    -> {"new": [sum, sumsq, n], "full": [...]} (log returns). Phase from the mean synodic month (error < ~0.6 day, fine for 15-day windows)."""
    t = np.asarray([pd_ts.timestamp() for pd_ts in times], float); c = np.asarray(closes, float)
    r = np.diff(np.log(c)); age = ((t[1:] - NEW_MOON_REF) / 86400.0) % SYNODIC
    near_new = (age < SYNODIC / 4) | (age >= 3 * SYNODIC / 4)
    out = {}
    for k, m in (("new", near_new), ("full", ~near_new)):
        x = r[m]; out[k] = [float(x.sum()), float((x ** 2).sum()), int(len(x))]
    return out


def report(rows, conflicts, cfl, meta, gann=None, lunar=None, gzone=None):
    ch = [r for r in rows if r["key"] == "*CHAIN*"]; vr = [r for r in rows if r["school"] == "exit"]
    rows = [r for r in rows if r["key"] != "*CHAIN*" and r["school"] != "exit"]
    ok = [r for r in rows if r["tf"] == "all" and r["side"] == "all" and r["key"] != "*ALL*"]
    ok.sort(key=lambda r: (r["n"] >= MIN_N, r.get("avgR", -9)), reverse=True)
    L = [f"# Strategy lab - real candles ({time.strftime('%Y-%m-%d', time.gmtime(meta['built']))})", "",
         f"Symbols: {', '.join(meta['symbols'])} · timeframes: {', '.join(meta['tfs'])} · stop {STOP_ATR} ATR, target {RR}R, "
         f"break-even win rate {round(100 / (1 + RR))}% · no costs (real results are worse) · n < {MIN_N} = not evidence.", "",
         "## Every detector on its own (all timeframes)", "", "| rank | key | school | n | win % | avg R | random win % | random avg R | edge |", "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(ok, 1):
        L.append(f"| {i} | {r['key']} | {r['school']} | {r['n']} | {r.get('win')} | {r.get('avgR')} | {r.get('base_win')} | {r.get('base_avgR')} | {'YES' if r['edge'] else ''} |")
    sch = {}
    for r in ok:
        a = sch.setdefault(r["school"], [0, 0.0]); a[0] += r["n"]; a[1] += r["n"] * (r.get("avgR") or 0)
    L += ["", "## Schools of analysis (all their detectors pooled)", "", "| rank | school | n | avg R |", "|---|---|---|---|"]
    L += [f"| {i} | {k} | {v[0]} | {round(v[1] / v[0], 3)} |" for i, (k, v) in enumerate(sorted(sch.items(), key=lambda kv: -kv[1][1] / max(kv[1][0], 1)), 1)]
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
    L += ["", "## Time of day (UTC session, intraday bars) and weekday - every detector pooled", "", "| when | n | win % | avg R |", "|---|---|---|---|"]
    for r in sorted((r for r in rows if r["key"] == "*ALL*" and r["side"].startswith(("ses-", "dow-"))), key=lambda r: r["side"]):
        L.append(f"| {r['side'][4:]} | {r['n']} | {r.get('win')} | {r.get('avgR')} |")
    if ch:
        L += ["", "## Chain grades (docs/PIPELINE.md): every detector signal tagged with 5 context layers - htf trend, location (discount/premium), "
              "volume, volatility regime, session", "",
              "Gate for a grade to count: n >= 100, t > 3 vs random direction, avg R > 0 in BOTH halves (first half = in-sample, second half = out-of-sample).", "",
              "| group | n | win % | avg R | random avg R | t | 1st half n | 1st half avg R | 2nd half n | 2nd half avg R | passes gate |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        order = ["all signals"] + [f"grade {g}" for g in ("A+++", "A+", "A", "B", "C")] + [f"layer {k}" for k in CHAIN] + [f"no {k}" for k in CHAIN]
        top = sorted((r for r in ch if " / " in r["side"] and r["n"] >= MIN_N), key=lambda r: -r["avgR"])[:15]
        for r in [next((r for r in ch if r["side"] == o), None) for o in order] + top:
            if r:
                L.append(f"| {r['side']} | {r['n']} | {r.get('win')} | {r.get('avgR')} | {r.get('base_avgR')} | {r['t']:+.2f} | {r['is_n']} | {r['is_avgR']} | "
                         f"{r['oos_n']} | {r['oos_avgR']} | {'YES' if r['edge'] else ''} |")
    L += ["", "## Conflicts (pointing opposite ways on the same bar)", "", "| a | b | together | opposite | % |", "|---|---|---|---|---|"]
    L += [f"| {c['a']} | {c['b']} | {c['together']} | {c['opposite']} | {c['rate']} |" for c in conflicts]
    L += ["", "## Confluence: more agreeing families = better?", "", "| agreeing families | n | win % | avg R |", "|---|---|---|---|"]
    L += [f"| {k} | {v['n']} | {v.get('win')} | {v.get('avgR')} |" for k, v in cfl.items()]
    if gann:
        L += ["", f"## Gann time cycles: another swing pivot within +-{GANN_TOL} bars of pivot + {'/'.join(map(str, GANN_CYC))} bars vs ordinary offsets", "",
              "| tf | Gann hit % | Gann tries | ordinary hit % | ordinary tries | difference (sigma) |", "|---|---|---|---|---|---|"]
        for tf, g in gann.items():
            (h1, n1), (h0, n0) = g["gann"], g["control"]
            if not n1 or not n0:
                continue
            p1, p0 = h1 / n1, h0 / n0; se = np.sqrt(p0 * (1 - p0) / n1) or 1
            L.append(f"| {tf} | {100 * p1:.1f} | {n1} | {100 * p0:.1f} | {n0} | {(p1 - p0) / se:+.1f} |")
            if g.get("shapes") and g["shapes"][1] and g.get("shapes_ctrl") and g["shapes_ctrl"][1]:
                (h2, n2), (h3, n3) = g["shapes"], g["shapes_ctrl"]; q2, q3 = h2 / n2, h3 / n3; se2 = np.sqrt(q3 * (1 - q3) / n2) or 1
                L.append(f"| {tf} shapes 120/180/240/360 deg | {100 * q2:.1f} | {n2} | {100 * q3:.1f} | {n3} | {(q2 - q3) / se2:+.1f} |")
        L.append(""); L.append("Rough sigma (overlapping tries). Above +3 on several timeframes would be evidence for Gann timing; around 0 = ordinary offsets. Random-walk self-tests: fixed counts -1.2; shapes (control = same points with the cycle length of another swing) +0.4 to +2.5 over 4 seeds, so only > +3 on several timeframes counts.")
    if gzone:
        L += ["", "## Gann zone trades OUT OF SAMPLE (walk-forward: grid refitted on everything before each 10 % slice of the last half, traded only in that slice; Workspace rule incl. time stop)", "",
              "| tf | trades | win % | avg R | random-direction avg R | difference (t) |", "|---|---|---|---|---|---|"]
        for tf, rs in sorted(gzone.items()):
            if not rs:
                continue
            a = np.asarray(rs, float); r1, r0 = a[:, 0], a[:, 1]; dlt = r1 - r0; t = dlt.mean() / (dlt.std(ddof=1) / np.sqrt(len(dlt))) if len(dlt) > 1 and dlt.std() > 0 else 0.0
            L.append(f"| {tf} | {len(a)} | {100 * (r1 > 0).mean():.1f} | {r1.mean():+.3f} | {r0.mean():+.3f} | {t:+.2f} |")
        L.append("")
        L.append("Random-walk self-test (walk-forward, 6 x 5000 bars): +0.07R vs random -0.02R, t +0.65 (198 trades) - so only t > +3 with n >= 100 on several timeframes counts as evidence. No costs.")
    if lunar and lunar.get("new", [0, 0, 0])[2] and lunar.get("full", [0, 0, 0])[2]:
        (s1, q1, n1), (s2, q2, n2) = lunar["new"], lunar["full"]; m1, m2 = s1 / n1, s2 / n2
        v1, v2 = max(q1 / n1 - m1 ** 2, 1e-18), max(q2 / n2 - m2 ** 2, 1e-18); t = (m1 - m2) / np.sqrt(v1 / n1 + v2 / n2)
        L += ["", "## Gann astro: lunar phase (daily bars, all symbols pooled; Dichev & Janes 2001 found new-moon days about twice the full-moon days)", "",
              "| window | days | mean daily return % |", "|---|---|---|",
              f"| 15 days around new moon | {n1} | {100 * m1:.3f} |", f"| 15 days around full moon | {n2} | {100 * m2:.3f} |",
              "", f"Difference t = {t:+.2f} (|t| > 2 would be a hint, > 3 evidence; overlapping symbols are correlated, so this is generous)."]
    if vr:
        L += ["", "## Exit variants on the SAME entries (RR and break-even stop)", "",
              "Which target / exit gives the best expectancy. Break-even break = win rate needed = 1/(1+RR). t = mean R vs 0 (paired across the same entries, roughly). "
              "Only the totals below are for the whole pool; per-detector rows are in the JSON.", "",
              "| exit | n | win % | avg R | total R | t |", "|---|---|---|---|---|---|"]
        L += [f"| {r['side']} | {r['n']} | {r['win']} | {r['avgR']} | {r['sumR']} | {r['t']:+.2f} |" for r in vr if r["key"] == "*VAR*"]
    return "\n".join(L) + "\n"


def run(symbols=SYMBOLS, tfs=TFS, stride=4, fetch=_fetch, log=print):
    evs, brs, done, gann, lunar, gzone = [], [], [], {}, {"new": [0.0, 0.0, 0], "full": [0.0, 0.0, 0]}, {}
    from modules.gann_lab import trade_test
    grng = np.random.default_rng(11)
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
            g = gann_cycles(df["high"].values, df["low"].values); acc = gann.setdefault(tf, {"gann": [0, 0], "control": [0, 0], "shapes": [0, 0], "shapes_ctrl": [0, 0]})
            for k in acc:
                acc[k][0] += g[k][0]; acc[k][1] += g[k][1]
            if tf in GZ_BARS:
                try:
                    dz = df
                    try:
                        dz = fetch(sym, tf, GZ_BARS[tf]) if GZ_BARS[tf] > len(df) else df
                    except Exception as e:
                        log(f"gann zone long fetch {sym} {tf}: {type(e).__name__} - using {len(df)} bars")
                    gzone.setdefault(tf, []).extend(trade_test(dz.reset_index(drop=True), grng))
                except Exception as e:
                    log(f"gann zone {sym} {tf}: {type(e).__name__} {e}")
            if tf == "1d":
                lu = lunar_split(list(df["time"]), df["close"].values)
                for k in lunar:
                    lunar[k] = [lunar[k][j] + lu[k][j] for j in range(3)]
            log(f"{sym} {tf}: {len(df)} bars, {len(ev)} signals, {time.time() - t0:.0f}s")
    rows, conflicts, cfl = summarize(evs, brs)
    meta = {"built": int(time.time()), "symbols": list(symbols), "tfs": list(tfs), "series": done, "stop_atr": STOP_ATR, "rr": RR}
    return {"meta": meta, "rows": rows, "conflicts": conflicts, "confluence": cfl, "gann": gann, "lunar": lunar, "gzone": gzone}


if __name__ == "__main__":
    syms = tuple(sys.argv[1:]) or SYMBOLS
    res = run(syms, stride=int(os.environ.get("LAB_STRIDE", "4")))
    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(res, indent=1))
    OUT_MD.write_text(report(res["rows"], res["conflicts"], res["confluence"], res["meta"], res.get("gann"), res.get("lunar"), res.get("gzone")))
    print(OUT_MD.read_text()[:3000])
