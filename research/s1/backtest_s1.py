#!/usr/bin/env python3
"""S1 backtest on dashboard data only. Usage: python3 backtest_s1.py [--refresh]"""
import json, sys, pickle
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
import s1_core as S
OUT = Path(__file__).parent / 'results'; OUT.mkdir(exist_ok=True)
CACHE = OUT / '_data.pkl'

def load(refresh=False):
    if CACHE.exists() and not refresh: return pickle.load(open(CACHE, 'rb'))
    data = {}
    for k, ins in S.UNIVERSE.items():
        data[k] = {}
        for tf, bars in (('5m', 5000), ('1m', 5000), ('1h', 2000)):
            try: data[k][tf] = S.fetch(ins['feed'], tf, bars); print(k, tf, len(data[k][tf]), data[k][tf].index[0], '->', data[k][tf].index[-1], flush=True)
            except Exception as e: print(k, tf, 'ERR', e, flush=True)
    pickle.dump(data, open(CACHE, 'wb')); return data

def main():
    data = load('--refresh' in sys.argv); allr = []; meta = {}
    for k, ins in S.UNIVERSE.items():
        for tf, hold in (('5m', 12), ('1m', 30)):          # time-stop = 60 min on 5m, 30 min on 1m
            if tf not in data[k] or '1h' not in data[k]: continue
            d = S.add_context(data[k][tf], data[k]['1h'])
            r = S.run(d, ins, hold=hold)
            if r.empty: continue
            r['ins'] = k; r['tf'] = tf; allr.append(r)
            meta[f'{k}_{tf}'] = dict(bars=len(d), start=str(d.index[0]), end=str(d.index[-1]), feed=ins['feed'])
            print(k, tf, len(r), 'trades', flush=True)
    R = pd.concat(allr, ignore_index=True); R['kz'] = R.sess.isin(['London KZ', 'NY AM KZ'])
    R['t'] = R.t.astype(str); R['exit_t'] = R.exit_t.astype(str)
    R.to_csv(OUT / 's1_trades.csv', index=False)
    half = R.groupby(['tf']).t.transform(lambda s: s.rank(pct=True)) <= 0.5
    rows = []
    for tf in ('5m', '1m'):
        for det in S.DETECTORS:
            for flt, m in (('base', True), ('bias', 'bias_ok'), ('kz', 'kz'), ('bias+kz', 'both')):
                x = R[(R.tf == tf) & (R.det == det)]
                if m == 'bias_ok': x = x[x.bias_ok]
                elif m == 'kz': x = x[x.kz]
                elif m == 'both': x = x[x.bias_ok & x.kz]
                st = S.stats(x.R); rb = S.stats(x.R_rand)
                h1 = S.stats(x[half.loc[x.index]].R); h2 = S.stats(x[~half.loc[x.index]].R)
                rows.append(dict(tf=tf, det=det, filter=flt, **st, gross_avgR=round(float(x.R_gross.mean()), 3) if len(x) else None,
                                 rand_avgR=rb.get('avgR'), rand_t=rb.get('t'), first_half_avgR=h1.get('avgR'), second_half_avgR=h2.get('avgR'),
                                 med_risk_pts=None, tp1_hit=round(float(x.tp1_hit.mean() * 100), 1) if len(x) else None))
    T = pd.DataFrame(rows); T.to_csv(OUT / 's1_summary_rules.csv', index=False)
    by_ins = []
    for (tf, ins), x in R.groupby(['tf', 'ins']):
        pt = S.UNIVERSE[ins]['pt']; reach = lambda P: round(float(((x.mfe * x.risk) / pt >= P).mean() * 100), 1)
        by_ins.append(dict(tf=tf, ins=ins, **S.stats(x.R), med_risk_pts=round(float(x.risk_pts.median()), 1),
                           reach100=reach(100), reach150=reach(150), reach200=reach(200)))
    by_sess = [dict(tf=tf, sess=s, **S.stats(x.R)) for (tf, s), x in R.groupby(['tf', 'sess'])]
    pd.DataFrame(by_ins).to_csv(OUT / 's1_by_instrument.csv', index=False); pd.DataFrame(by_sess).to_csv(OUT / 's1_by_session.csv', index=False)
    res = dict(label='S1 draft backtest: dashboard data only (Hyperliquid via market_cache, OKX pages via data_fetcher). Lab rule: approved only if n>=100 and t>3.',
               costs='spread + 1 tick per round trip, charged in R', management='TP1 1R (half) -> BE, TP2 2R, time-stop 60 min (5m) / 30 min (1m); same-bar stop+target = stop',
               data=meta, rules=rows, by_instrument=by_ins, by_session=by_sess, total=dict(**{tf: S.stats(R[R.tf == tf].R) for tf in ('5m', '1m')}))
    json.dump(res, open(OUT / 's1_backtest.json', 'w'), indent=1, default=str)
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 200)
    print(T.to_string()); print(pd.DataFrame(by_ins).to_string()); print(pd.DataFrame(by_sess).to_string()); print(res['total'])
if __name__ == '__main__': main()
