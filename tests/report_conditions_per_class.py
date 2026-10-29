"""Report (not a test): every Radar list option and scanner condition on synthetic OHLC series shaped like each asset class (price level, volatility, volume available or not),
then a stress suite for the ones that fired nowhere. Prints the counts used in docs/CONDITIONS_PER_CLASS_2026-10-26.md. Run: python tests/report_conditions_per_class.py"""
import sys, collections, json
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np, pandas as pd
from modules import fv_screen as F, chart_scan as CS
# class -> (price0, daily vol, drift options, volume available?, freq)
CLASSES = {"Crypto": (100.0, .028, True), "Metals(HL gold)": (4100.0, .010, True), "Oil(HL CL)": (70.0, .020, True), "Indices(HL SP500)": (7600.0, .009, True),
           "Forex(HL EUR)": (1.12, .004, True), "Forex(Yahoo EURUSD=X)": (1.12, .004, False), "Stocks(HL)": (250.0, .018, True), "Bonds(HL TLT)": (80.0, .006, True),
           "EGX/Tadawul(Yahoo)": (80.0, .012, False)}
def walk(seed, price0, vol, hasvol, n=320, last=None, gap=None):
    rng = np.random.default_rng(seed); drift = [0.0008, -0.0008, 0.0, 0.002, -0.002][seed % 5]*vol/0.01*0.3
    r = rng.normal(drift, vol, n); c = price0*np.exp(np.cumsum(r)); o = np.r_[c[0], c[:-1]]*(1+rng.normal(0, vol/4, n))
    if last is not None: c[-1] = c[-2]*(1+last); o[-1] = c[-2]
    if gap is not None: o[-1] = c[-2]*(1+gap); c[-1] = o[-1]*(1+0.002)
    h = np.maximum(o, c)*(1+abs(rng.normal(vol/3, vol/6, n))); l = np.minimum(o, c)*(1-abs(rng.normal(vol/3, vol/6, n)))
    v = rng.uniform(.8, 1.2, n)*1e4 if hasvol else np.zeros(n)
    if hasvol: v[-1] *= (3 if seed % 3 == 0 else 1)
    return pd.DataFrame({"time": pd.date_range(end="2026-10-24", periods=n, freq="D"), "open": o, "high": h, "low": l, "close": c, "volume": v})
def series(cls, force_vol=False):
    p0, vol, hv = CLASSES[cls]; hv = hv or force_vol; S = []
    for sd in range(30): S.append(walk(sd, p0, vol, hv))
    for sh in (0.04, 0.09, 0.15, -0.04, -0.09, -0.15): S.append(walk(100, p0, vol, hv, last=sh*vol/0.02))
    for g in (0.012, 0.03, -0.012, -0.03): S.append(walk(101, p0, vol, hv, gap=g*vol/0.02))
    return S
ref = walk(999, 100.0, .015, True)
def fire(S):
    fv = collections.Counter(); cs = collections.Counter(); err = 0
    for df in S:
        try:
            m = F.metrics(df); m.update(F.relation(df, ref)); ctx = {"candles": F.candle_set(df), "flags": set()}
        except Exception: err += 1; continue
        for key, g, n, na, opts in F.FILTERS:
            for code, e, a in opts:
                try:
                    if F.test(key, code, m, ctx): fv[(key, code)] += 1
                except Exception: err += 1
        d = df.reset_index(drop=True)
        try:
            fl = set(CS.features(d)["flags"]); sf, _s = CS.strategy_flags(d); fl |= set(sf); fl |= set(CS.move_flags(d))
        except Exception: err += 1; fl = set()
        for x in fl: cs[x] += 1
    return fv, cs, err
allfv = [(k, c) for k, g, n, na, o in F.FILTERS for c, e, a in o]; allcs = list(CS.ALL_FILTERS)
res = {}
for cls in CLASSES:
    S = series(cls); fv, cs, err = fire(S)
    fz = [x for x in allfv if fv[x] == 0]; cz = [x for x in allcs if cs[x] == 0]
    vol_dep = []
    if not CLASSES[cls][2]:
        fv2, cs2, _e = fire(series(cls, force_vol=True)); vol_dep = [x for x in fz if fv2[x] > 0] + [x for x in cz if cs2[x] > 0]
    res[cls] = {"n": len(S), "err": err, "fv_zero": [f"{k}|{c}" for k, c in fz], "cs_zero": cz, "vol_dep": [x if isinstance(x, str) else f"{x[0]}|{x[1]}" for x in vol_dep]}
    print(cls, "series", len(S), "errors", err, "| radar list zero:", len(fz), "/", len(allfv), "| scanner zero:", len(cz), "/", len(allcs), "| zero ONLY because volume is 0:", len(vol_dep))
json.dump(res, open('/tmp/perclass_report.json', 'w'))

print("---- stress suite on the conditions that fired in NO class")
import json as _j
R = _j.load(open('/tmp/perclass_report.json'))
fvz = set.intersection(*[set(v['fv_zero']) for v in R.values()]); csz = set.intersection(*[set(v['cs_zero']) for v in R.values()])
def mk(c, h=None, l=None, o=None, v=None, n=None):
    n = len(c); c = np.array(c, float); o = np.r_[c[0], c[:-1]] if o is None else np.array(o, float)
    h = np.maximum(o, c)*1.004 if h is None else np.array(h, float); l = np.minimum(o, c)*0.996 if l is None else np.array(l, float)
    return pd.DataFrame({"time": pd.date_range(end="2026-10-24", periods=n, freq="D"), "open": o, "high": h, "low": l, "close": c, "volume": np.full(n, 1e4) if v is None else v})
rng = np.random.default_rng(5); t = np.arange(320); ST = []
base = 100 + 4*np.sin(t/9)
ST.append(mk(100*np.exp(np.cumsum(np.r_[np.zeros(250), np.full(70, 0.03)]))))                    # parabolic up: RSI > 90, perf +50, hi
ST.append(mk(100*np.exp(np.cumsum(np.r_[np.zeros(250), np.full(70, -0.03)]))))                   # crash: RSI < 10, perf -50, new lows
ST.append(mk(np.r_[np.linspace(100, 40, 160), np.linspace(40, 140, 160)]))                       # V: MA crosses up (20/50/200)
ST.append(mk(np.r_[np.linspace(40, 140, 160), np.linspace(140, 40, 160)]))                       # inverted V: MA crosses down
c = base.copy(); c[-1] = c[-2]*1.6; ST.append(mk(c))                                              # +60 % last bar
c = base.copy(); c[-1] = c[-2]*0.4; ST.append(mk(c))                                              # -60 % last bar
c = base.copy(); o = np.r_[c[0], c[:-1]]; o[-1] = c[-2]*1.09; c[-1] = o[-1]*1.001; ST.append(mk(c, o=o))   # gap up 9 %
c = base.copy(); o = np.r_[c[0], c[:-1]]; o[-1] = c[-2]*0.91; c[-1] = o[-1]*0.999; ST.append(mk(c, o=o)) # gap down 9 %
ST.append(mk(100 + np.cumsum(rng.normal(0, 6, 320))*0.5 + 40, h=None))                           # very volatile (ATR > 10 %)
vv = np.full(320, 1e4); vv[-1] = 1.2e5; ST.append(mk(base, v=vv))                                # relative volume > 10
vv = np.full(320, 1e4); vv[-1] = 1e3; ST.append(mk(base, v=vv))                                  # relative volume < 0.25
# candles: hammer / inverted hammer / dark cloud / evening star / shooting star after a trend
def tail(kind):
    up = np.linspace(80, 100, 300); dn = np.linspace(120, 100, 300)
    if kind == "hammer": c = list(dn)+[99.5]; o = list(dn[:-1])+[100.6, 100.0]; o = o[:len(c)]; h = [x*1.002 for x in c]; l = [x*0.998 for x in c]; o[-1] = 100.1; c[-1] = 100.3; h[-1] = 100.4; l[-1] = 96.5
    if kind == "invhammer": c = list(dn)+[99.5]; o = [x*1.0 for x in c]; h = [x*1.002 for x in c]; l = [x*0.998 for x in c]; o[-1] = 99.4; c[-1] = 99.6; h[-1] = 103.0; l[-1] = 99.3
    if kind == "dark": c = list(up)+[102.0, 101.0]; o = [x*0.999 for x in c]; o[-2] = 100.0; c[-2] = 102.0; o[-1] = 103.0; c[-1] = 101.0; h = [max(a, b)*1.001 for a, b in zip(o, c)]; l = [min(a, b)*0.999 for a, b in zip(o, c)]
    if kind == "evening": c = list(up)+[103.0, 103.6, 101.0]; o = [x*0.999 for x in c]; o[-3] = 100.0; c[-3] = 103.0; o[-2] = 103.4; c[-2] = 103.6; o[-1] = 103.2; c[-1] = 101.0; h = [max(a, b)*1.001 for a, b in zip(o, c)]; l = [min(a, b)*0.999 for a, b in zip(o, c)]
    return mk(c, h=h, l=l, o=o)
for k in ("hammer", "invhammer", "dark", "evening"): ST.append(tail(k))
fvs, css, e = fire(ST)
still_fv = sorted(f"{k}|{c}" for k, c in [tuple(x.split("|", 1)) for x in fvz] if fvs[(k, c)] == 0)
still_cs = sorted(x for x in csz if css[x] == 0)
print("stress suite errors", e); print("radar conditions still never firing:", len(still_fv), still_fv); print("scanner conditions still never firing:", len(still_cs), still_cs)
