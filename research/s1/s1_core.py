#!/usr/bin/env python3
"""S1 scalp engine (draft). Pure pandas/numpy on candles from the dashboard data layer only:
modules.market_cache (Hyperliquid TradFi perps) and modules.data_fetcher OKX pages (the same OKX endpoint market_cache uses).
No yfinance / Yahoo. No probabilities. Rules are labelled 'approved' only if n>=100 and t>3 (lab rule), else 'experimental'."""
from __future__ import annotations
import os, sys, time
import numpy as np, pandas as pd
sys.path.insert(0, os.environ.get('XPIX_REPO', '/workspace/ai-trading-dashboard'))  # dashboard repo root (for modules.market_cache)
from modules.market_cache import get_klines
from modules import data_fetcher as DF

# ---------------------------------------------------------------- universe & point convention
# point size = the repo convention in modules/ws/24b_tclass.js TCE.pointSize: forex = pip (0.0001), gold 0.1,
# silver/oil 0.01, indices 1, crypto by price (>=1000 -> 1). So GOLD 100 pts = $10.00 (NOT the MT5 0.01 convention).
UNIVERSE = {
    'GOLD':   dict(feed='HL:xyz:GOLD',   pt=0.1,    spread=0.50,    tick=0.10,    dec=1),
    'SILVER': dict(feed='HL:xyz:SILVER', pt=0.01,   spread=0.025,   tick=0.005,   dec=3),
    'NDX':    dict(feed='HL:xyz:XYZ100', pt=1.0,    spread=1.0,     tick=0.10,    dec=1),
    'SPX':    dict(feed='HL:xyz:SP500',  pt=1.0,    spread=0.50,    tick=0.10,    dec=1),
    'EURUSD': dict(feed='HL:xyz:EUR',    pt=0.0001, spread=0.00012, tick=0.00001, dec=5),
    'BTC':    dict(feed='BTC-USDT',      pt=1.0,    spread=5.0,     tick=0.10,    dec=1),
    'ETH':    dict(feed='ETH-USDT',      pt=1.0,    spread=0.50,    tick=0.01,    dec=2),
}
TFMIN = {'1m': 1, '5m': 5, '15m': 15, '1h': 60}

def _norm(df):
    df = df.copy(); df['time'] = pd.to_datetime(df['time']); df = df.set_index('time').sort_index()
    if df.index.tz is None: df.index = df.index.tz_localize('UTC')
    df = df[~df.index.duplicated()][['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df.rename(columns={'open': 'o', 'high': 'h', 'low': 'l', 'close': 'c', 'volume': 'v'})

def fetch(feed, tf, bars=5000):
    """Hyperliquid: one candleSnapshot (max 5000 most-recent bars). OKX: market_cache (300) + history pages of 100."""
    if feed.startswith('HL:'):
        return _norm(get_klines(feed, tf, min(bars, 5000)))
    bar = DF._OKX_INTERVAL_MAP.get(tf, tf)
    df = _norm(get_klines(feed, tf, 300)); guard = 0
    while len(df) < bars and guard < 120:
        guard += 1
        after = int(df.index[0].timestamp() * 1000)
        for att in range(3):
            try:
                more = DF._okx_frame(feed, bar, 100, after_ms=after, history=True); break
            except Exception:
                time.sleep(1.5 * (att + 1)); more = None
        if more is None or more.empty: break
        df = pd.concat([_norm(more), df]); df = df[~df.index.duplicated()].sort_index(); time.sleep(0.12)
    return df.tail(bars)

# ---------------------------------------------------------------- indicators
def atr(d, n=14):
    tr = pd.concat([d.h - d.l, (d.h - d.c.shift()).abs(), (d.l - d.c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()
def ema(s, n): return s.ewm(span=n, adjust=False).mean()
def rsi(c, n=14):
    dd = c.diff(); up = dd.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-dd.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))
def stoch_k(d, k=5, s=3):
    ll, hh = d.l.rolling(k).min(), d.h.rolling(k).max(); return (100 * (d.c - ll) / (hh - ll).replace(0, np.nan)).rolling(s).mean()
def vwap_bands(d):
    day = d.index.floor('1D'); tp = (d.h + d.l + d.c) / 3; v = d.v.where(d.v > 0, 1.0)
    pv = (tp * v).groupby(day).cumsum(); vv = v.groupby(day).cumsum(); p2 = (tp * tp * v).groupby(day).cumsum()
    vw = pv / vv; sd = np.sqrt((p2 / vv - vw ** 2).clip(lower=0)); return vw, sd
def psar(d, step=0.02, mx=0.2):
    h, l = d.h.values, d.l.values; n = len(d); sar_v = np.full(n, np.nan); tr = np.zeros(n)
    if n < 3: return pd.Series(sar_v, d.index), pd.Series(tr, d.index)
    up = True; af = step; ep = h[0]; sar = l[0]
    for i in range(1, n):
        sar = sar + af * (ep - sar)
        if up:
            sar = min(sar, l[i - 1], l[max(i - 2, 0)])
            if l[i] < sar: up, sar, ep, af = False, ep, l[i], step
            elif h[i] > ep: ep, af = h[i], min(af + step, mx)
        else:
            sar = max(sar, h[i - 1], h[max(i - 2, 0)])
            if h[i] > sar: up, sar, ep, af = True, ep, h[i], step
            elif l[i] < ep: ep, af = l[i], min(af + step, mx)
        sar_v[i] = sar; tr[i] = 1 if up else -1
    return pd.Series(sar_v, d.index), pd.Series(tr, d.index)

def ny_min(idx):
    t = idx.tz_convert('America/New_York'); return t.hour * 60 + t.minute
def session_of(m):
    # Workspace kill zones (NY time): London 02-05, NY AM 07-10, NY PM 13:30-16, Asia 20-24
    if 120 <= m < 300: return 'London KZ'
    if 420 <= m < 600: return 'NY AM KZ'
    if 810 <= m < 960: return 'NY PM'
    if m >= 1200: return 'Asia'
    return 'other'

def add_context(d5, d1h):
    """columns used by the detectors (no look-ahead: 1h values are taken from the last CLOSED 1h bar)."""
    d = d5.copy(); d.index = d.index.as_unit('ns'); d1h = d1h.copy(); d1h.index = d1h.index.as_unit('ns'); d['atr'] = atr(d); d['rsi'] = rsi(d.c); d['k'] = stoch_k(d, 5, 3)
    d['vw'], d['vsd'] = vwap_bands(d); d['sar'], d['sartr'] = psar(d)
    d['hi20'] = d.h.shift(1).rolling(20).max(); d['lo20'] = d.l.shift(1).rolling(20).min()
    d['hi30'] = d.h.rolling(30).max(); d['lo30'] = d.l.rolling(30).min()
    d['vratio'] = d.v / d.v.shift(1).rolling(20).mean()
    h = d1h.copy(); h['e20'] = ema(h.c, 20); h['e50'] = ema(h.c, 50); h['atr1h'] = atr(h)
    h = h[['e20', 'e50', 'atr1h', 'h', 'l']].rename(columns={'h': 'ph1h', 'l': 'pl1h'})
    h.index = h.index + pd.Timedelta(hours=1)          # a 1h bar is known only after it closes
    d = pd.merge_asof(d.sort_index(), h.sort_index(), left_index=True, right_index=True, direction='backward')
    d['bias'] = np.sign(d.e20 - d.e50); d['ext1h'] = (d.c - d.e20) / d.atr1h
    # previous UTC day high/low (known from the day start) and Asia range (NY 20:00-24:00 of the previous evening)
    day = d.index.floor('1D'); dh = d.h.groupby(day).max(); dl = d.l.groupby(day).min()
    d['pdh'] = pd.Series(day, index=d.index).map(dh.shift(1)); d['pdl'] = pd.Series(day, index=d.index).map(dl.shift(1))
    m = ny_min(d.index); d['nym'] = m; d['sess'] = [session_of(x) for x in m]
    return d

# ---------------------------------------------------------------- detectors (signal on the CLOSE of bar i)
def _rej(b, side):
    rg = b.h - b.l
    if not rg > 0: return False
    return ((min(b.o, b.c) - b.l) / rg >= 0.45 and b.c >= b.o - rg * 0.1) if side > 0 else ((b.h - max(b.o, b.c)) / rg >= 0.45 and b.c <= b.o + rg * 0.1)

DETECTORS = {
    'kzs':       'Kill Zone Sniper (Workspace): KZ only, sweep of 20-bar high/low, close back with body >= 0.9 ATR, volume >= 1.5x',
    'sweep_rej': 'Liquidity sweep of 20-bar high/low + rejection wick >= 45% (TCE.rejection), any session',
    'lvl_sweep': 'Sweep of a key level (PDH/PDL, previous 1h high/low) + close back inside',
    'vwap2':     'Close back inside the VWAP +-2 sd band after a close outside (mean reversion)',
    'zn':        'Scalp Zones (Stoch 5,9,3 + RSI14): %K leaves 85+ (sell) / 15- (buy) with RSI14 >= 60 / <= 40',
    'psar_trend':'MT5 pack: 5m PSAR flips in the 1h EMA20/50 direction, price on the same side of VWAP',
}

def signals(d, which=None):
    """-> list of dicts {i, t, det, side, entry, raw_stop, level}"""
    out = []; n = len(d); which = which or list(DETECTORS)
    O, H, L, C, A = d.o.values, d.h.values, d.l.values, d.c.values, d.atr.values
    for i in range(60, n):
        b = d.iloc[i]; a = A[i]
        if not a > 0: continue
        if 'kzs' in which and b.sess in ('London KZ', 'NY AM KZ'):
            vr_ok = (not d.v.iloc[i - 20:i].gt(0).all()) or (b.vratio >= 1.5)
            if vr_ok and b.l < b.lo20 and b.c > b.lo20 and b.c > b.o and b.c - b.o >= 0.9 * a:
                out.append(dict(i=i, det='kzs', side=1, entry=b.c, raw_stop=b.l, level=b.lo20, tp_struct=b.hi30))
            elif vr_ok and b.h > b.hi20 and b.c < b.hi20 and b.c < b.o and b.o - b.c >= 0.9 * a:
                out.append(dict(i=i, det='kzs', side=-1, entry=b.c, raw_stop=b.h, level=b.hi20, tp_struct=b.lo30))
        if 'sweep_rej' in which:
            if b.l < b.lo20 and b.c > b.lo20 and _rej(b, 1): out.append(dict(i=i, det='sweep_rej', side=1, entry=b.c, raw_stop=b.l, level=b.lo20))
            elif b.h > b.hi20 and b.c < b.hi20 and _rej(b, -1): out.append(dict(i=i, det='sweep_rej', side=-1, entry=b.c, raw_stop=b.h, level=b.hi20))
        if 'lvl_sweep' in which:
            for nm in ('pdl', 'pl1h'):
                lv = b[nm]
                if lv == lv and b.l < lv < b.c and d.c.iloc[i - 1] > lv: out.append(dict(i=i, det='lvl_sweep', side=1, entry=b.c, raw_stop=b.l, level=lv, lname=nm)); break
            else:
                for nm in ('pdh', 'ph1h'):
                    lv = b[nm]
                    if lv == lv and b.h > lv > b.c and d.c.iloc[i - 1] < lv: out.append(dict(i=i, det='lvl_sweep', side=-1, entry=b.c, raw_stop=b.h, level=lv, lname=nm)); break
        if 'vwap2' in which and b.vsd > 0:
            p = d.iloc[i - 1]
            if p.c < p.vw - 2 * p.vsd and b.c > b.vw - 2 * b.vsd: out.append(dict(i=i, det='vwap2', side=1, entry=b.c, raw_stop=min(L[i - 2:i + 1]), level=b.vw))
            elif p.c > p.vw + 2 * p.vsd and b.c < b.vw + 2 * b.vsd: out.append(dict(i=i, det='vwap2', side=-1, entry=b.c, raw_stop=max(H[i - 2:i + 1]), level=b.vw))
        if 'zn' in which:
            k0, k1 = d.k.iloc[i - 1], b.k
            if k0 >= 85 and k1 < 85 and b.rsi >= 60: out.append(dict(i=i, det='zn', side=-1, entry=b.c, raw_stop=max(H[i - 4:i + 1]), level=None))
            elif k0 <= 15 and k1 > 15 and b.rsi <= 40: out.append(dict(i=i, det='zn', side=1, entry=b.c, raw_stop=min(L[i - 4:i + 1]), level=None))
        if 'psar_trend' in which:
            t0, t1 = d.sartr.iloc[i - 1], b.sartr
            if t0 < 0 < t1 and b.bias > 0 and b.c > b.vw: out.append(dict(i=i, det='psar_trend', side=1, entry=b.c, raw_stop=min(L[i - 4:i + 1]), level=b.sar))
            elif t0 > 0 > t1 and b.bias < 0 and b.c < b.vw: out.append(dict(i=i, det='psar_trend', side=-1, entry=b.c, raw_stop=max(H[i - 4:i + 1]), level=b.sar))
    for s in out: s['t'] = d.index[s['i']]
    return out

# ---------------------------------------------------------------- stop / targets (S1 rule)
def plan(s, d, ins, tp1=1.0, tp2=2.0):
    """stop = structure extreme + pad; risk floored at max(0.5 ATR, 3 spreads, 5 ticks); skip if > 2.5 ATR.
    TP1 1R (close half, stop to break-even), TP2 2R. None if invalid."""
    a = d.atr.iloc[s['i']]; side = s['side']; E = s['entry']
    pad = max(0.1 * a, 2 * ins['spread'])
    stop = s['raw_stop'] - side * pad
    risk = (E - stop) * side
    floor = max(0.5 * a, 3 * ins['spread'], 5 * ins['tick'])
    if risk < floor: stop = E - side * floor; risk = floor
    if risk > 2.5 * a: return None
    return dict(entry=E, stop=stop, risk=risk, tp1=E + side * tp1 * risk, tp2=E + side * tp2 * risk, atr=a)

def simulate(d, i, side, p, ins, hold=12):
    """bars after the signal bar. Same-bar stop+target = stop first (conservative). After TP1: half closed, stop -> entry.
    Exit at time-stop (close of bar i+hold). Cost = spread + 1 tick per round trip, charged in R."""
    E, S, R = p['entry'], p['stop'], p['risk']; half = False; stop = S; r_real = 0.0; mfe = 0.0
    end = min(len(d) - 1, i + hold); exit_t = None; how = 'time'
    for q in range(i + 1, end + 1):
        b = d.iloc[q]; hi, lo = b.h, b.l
        adverse = lo <= stop if side > 0 else hi >= stop
        if adverse:
            r_real += (0.5 if half else 1.0) * ((stop - E) * side / R); exit_t = d.index[q]; how = 'BE' if half else 'stop'; break
        mfe = max(mfe, ((hi - E) if side > 0 else (E - lo)) / R)
        if not half and (hi >= p['tp1'] if side > 0 else lo <= p['tp1']):
            half = True; r_real += 0.5 * 1.0; stop = E
        if half and (hi >= p['tp2'] if side > 0 else lo <= p['tp2']):
            r_real += 0.5 * 2.0; exit_t = d.index[q]; how = 'tp2'; break
    else:
        q = end; c = d.c.iloc[q]; r_real += (0.5 if half else 1.0) * ((c - E) * side / R); exit_t = d.index[q]
    if q == i: return None
    cost = (ins['spread'] + ins['tick']) / R
    return dict(R_gross=r_real, R=r_real - cost, cost_R=cost, how=how, exit_t=exit_t, bars=q - i, mfe=mfe, tp1_hit=half)

def run(d, ins, which=None, hold=12, filters=('base',), seed=7):
    sigs = signals(d, which); rows = []; busy = {}
    rng = np.random.default_rng(seed)
    for s in sigs:
        key = s['det']
        if busy.get(key, -1) >= s['i']: continue        # one trade at a time per detector
        p = plan(s, d, ins)
        if not p: continue
        r = simulate(d, s['i'], s['side'], p, ins, hold)
        if not r: continue
        # random-direction baseline at the same time with the same risk
        rs = -1 if rng.random() < 0.5 else 1; s2 = dict(s, side=rs, raw_stop=s['entry'] - rs * p['risk'])
        p2 = plan(s2, d, ins); r2 = simulate(d, s['i'], rs, p2, ins, hold) if p2 else None
        b = d.iloc[s['i']]
        rows.append(dict(t=s['t'], det=s['det'], side=s['side'], entry=p['entry'], stop=p['stop'], risk=p['risk'], risk_pts=p['risk'] / ins['pt'],
                         sess=b.sess, bias_ok=(b.bias == s['side']), ext1h=b.ext1h, **r, R_rand=(r2['R'] if r2 else np.nan)))
        busy[key] = s['i'] + r['bars']
    return pd.DataFrame(rows)

def stats(x):
    x = pd.Series(x).dropna(); n = len(x)
    if n == 0: return dict(n=0)
    m = x.mean(); sd = x.std(ddof=1) if n > 1 else np.nan; t = m / (sd / np.sqrt(n)) if n > 1 and sd > 0 else np.nan
    return dict(n=n, win=round(float((x > 0).mean() * 100), 1), avgR=round(float(m), 3), t=round(float(t), 2) if t == t else None,
                verdict='approved' if (n >= 100 and t == t and t > 3) else 'experimental')
