"""Every Radar list option (fv_screen.FILTERS, 410) and every scanner condition (chart_scan.ALL_FILTERS, 96) run on 65 fixed synthetic OHLC series: none may crash, and the number that match at least once must not drop.
A condition that never matches on random series is NOT proof of a bug (extreme thresholds, special shapes): the table is printed for review. Run: python tests/test_radar_conditions_sweep.py"""
import sys, math, collections
import os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np, pandas as pd
from modules import fv_screen as F
def series(kind, n=320):
    rng = np.random.default_rng({"up":1,"down":2,"range":3,"spike":4,"gap":5}[kind]); t = np.arange(n); base = 100.0
    if kind == "up": c = base*(1+0.003*t) + 3*np.sin(t/8)
    elif kind == "down": c = base*(1-0.0022*t) + 3*np.sin(t/8)
    elif kind == "range": c = base + 6*np.sin(t/10)
    elif kind == "spike": c = base + 6*np.sin(t/10); c[-1] *= 1.12
    else: c = base*(1+0.002*t) + 2*np.sin(t/7); c[-3:] += 6
    o = np.r_[c[0], c[:-1]] + rng.normal(0, .3, n); 
    if kind == "gap": o[-1] = c[-2]*1.03
    h = np.maximum(o, c) + abs(rng.normal(0.6, .3, n)); l = np.minimum(o, c) - abs(rng.normal(0.6, .3, n)); v = rng.uniform(900, 1100, n); v[-1] *= 3 if kind != "range" else 1
    idx = pd.date_range(end="2026-10-24", periods=n, freq="D")
    return pd.DataFrame({"time": idx, "open": o, "high": h, "low": l, "close": c, "volume": v})

def walk(seed, drift, vol, n=320, last=None, gap=None, vmul=1.0, price0=100.0, volbase=1000):
    rng = np.random.default_rng(seed); r = rng.normal(drift, vol, n); c = price0*np.exp(np.cumsum(r)); o = np.r_[c[0], c[:-1]]*(1+rng.normal(0, vol/4, n))
    if last is not None: c[-1] = c[-2]*(1+last); o[-1] = c[-2]
    if gap is not None: o[-1] = c[-2]*(1+gap); c[-1] = o[-1]*(1+(last or 0.002))
    h = np.maximum(o, c)*(1+abs(rng.normal(0.004, 0.002, n))); l = np.minimum(o, c)*(1-abs(rng.normal(0.004, 0.002, n))); v = rng.uniform(.8, 1.2, n)*volbase; v[-1] *= vmul
    return pd.DataFrame({"time": pd.date_range(end="2026-10-24", periods=n, freq="D"), "open": o, "high": h, "low": l, "close": c, "volume": v})
def candle(df, kind):
    df = df.copy(); i = len(df)-1; c0 = df.close.iloc[i-1]; r = c0*0.01
    o, h, l, c = {"doji": (c0, c0+r, c0-r, c0+r*.02), "hammer": (c0, c0+r*.1, c0-r*3, c0+r*.2), "shooting": (c0, c0+r*3, c0-r*.1, c0-r*.2), "marubozu": (c0, c0+r*2, c0, c0+r*2),
                  "engulf": (c0+r, c0+r*4, c0-r*2, c0-r*3)}[kind]
    df.loc[df.index[i], ["open","high","low","close"]] = [o, h, l, c]; return df
S = {}
for sd in range(40): S[f"w{sd}"] = walk(sd, [0.0015,-0.0015,0.0,0.004,-0.004][sd%5], [0.008,0.015,0.03][sd%3])
for sh in (0.03,0.06,0.12,0.25,-0.03,-0.06,-0.12,-0.25): S[f"shock{sh}"] = walk(100, 0.0, 0.01, last=sh, vmul=4)
for g in (0.01,0.03,0.06,-0.01,-0.03,-0.06): S[f"gap{g}"] = walk(101, 0.0, 0.01, gap=g, vmul=2)
for k in ("doji","hammer","shooting","marubozu","engulf"): S["c_"+k] = candle(walk(102, 0.002 if k in ("shooting",) else -0.002, 0.012), k)
S["lowvol"] = walk(103, 0.0, 0.002, vmul=0.2); S["hivol"] = walk(104, 0.0, 0.05); S["cheap"] = walk(105, 0.0, 0.01, price0=0.5); S["dear"] = walk(106, 0.0, 0.01, price0=20000, volbase=2e5); S["crash"] = walk(107, -0.012, 0.01); S["moon"] = walk(108, 0.012, 0.01)
ref = walk(999, 0.001, 0.01)
M = {}
for k, df in S.items():
    try:
        m = F.metrics(df); m.update(F.relation(df, ref)); M[k] = m
    except Exception as e: print("metrics crash", k, repr(e)[:90]); M[k] = None
print("series", len(S), "metrics ok", sum(v is not None for v in M.values()))
rows = []
for key, grp, name, name_ar, opts in F.FILTERS:
    for code, en, ar in opts:
        hits = []; err = None
        for k, m in M.items():
            if m is None: continue
            try:
                if F.test(key, code, m, {"candles": F.candle_set(S[k]), "flags": set()}): hits.append(k)
            except Exception as e: err = repr(e)[:90]
        rows.append((key, code, en, hits, err))
zero = [r for r in rows if not r[3] and not r[4]]; bad = [r for r in rows if r[4]]
print("TOTAL options", len(rows), "| crash", len(bad), "| match on >=1 series", len(rows)-len(zero)-len(bad), "| never matched", len(zero))
for r in bad: print("CRASH", r[0], r[1], r[4])
by = collections.defaultdict(list)
for r in zero: by[r[0]].append(r[1])
for k, v in by.items(): print("ZERO", k, len(v), v)

print("---- scanner conditions (chart_scan)")
from modules import chart_scan as CS
hits = collections.defaultdict(set); errs = []
for k, df in S.items():
    d = df.reset_index(drop=True)
    try:
        fl = set(CS.features(d)["flags"]); sf, _s = CS.strategy_flags(d); fl |= set(sf); fl |= set(CS.move_flags(d))
    except Exception as e:
        errs.append((k, repr(e)[:80])); continue
    for x in fl: hits[x].add(k)
never_cs = [x for x in CS.ALL_FILTERS if x not in hits]
print("scanner conditions", len(CS.ALL_FILTERS), "| crashes", len(errs), "| matched", len(CS.ALL_FILTERS)-len(never_cs), "| never matched (need targeted fixtures: MA crosses, channel / wedge / triangle shapes, session strategies, SMT peers):", never_cs)
assert not bad and not errs, (bad[:3], errs[:3])
assert len(rows) - len(zero) - len(bad) >= 350, "radar list conditions that match at least once dropped"
assert len(CS.ALL_FILTERS) - len(never_cs) >= 78, "scanner conditions that match at least once dropped"
print("ok radar conditions sweep")
