#!/usr/bin/env python3
"""Replay the S1 cleanup rules on the 29 signals sent 20–26 Nov 2026.
Uses cached dashboard candles only (no yfinance). Experimental (small n).
Does not send Telegram and does not touch the live state file.
"""
from __future__ import annotations
import os, sys, json, pickle
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).parent
REV = Path('/workspace/s1_review_2026-11-26')
sys.path.insert(0, str(HERE))
os.environ['S1_STATE'] = str(REV / 'replay_state.json')
import s1_core as S, scalp_now as N, s1_state as ST, s1_tools as T

CAIRO = 'Africa/Cairo'

def resample_15(d5):
    x = d5.copy()
    o = x.resample('15min', label='left', closed='left').agg({'o':'first','h':'max','l':'min','c':'last','v':'sum'})
    return o.dropna()

def asof_frames(data, key, t_bar):
    """t_bar = open time of the signal 5m bar; include it as just-closed."""
    t_close = pd.Timestamp(t_bar)
    if t_close.tzinfo is None:
        t_close = t_close.tz_localize('UTC')
    t_asof = t_close + pd.Timedelta(minutes=5)
    d5 = data[key]['5m']
    d1h = data[key]['1h']
    d5 = d5[d5.index + pd.Timedelta(minutes=5) <= t_asof].tail(600)
    d1h = d1h[d1h.index + pd.Timedelta(hours=1) <= t_asof].tail(400)
    d15 = resample_15(d5)
    d15 = d15[d15.index + pd.Timedelta(minutes=15) <= t_asof].tail(300)
    return dict(d5=d5, d1h=d1h, d15=d15, t_asof=t_asof)

def simulate_new(d5, i, side, entry, stop, tp1, tp2, ins, hold=12):
    if isinstance(i, pd.Timestamp):
        loc = d5.index.get_indexer([i], method='nearest')[0]
    else:
        loc = int(i)
    E, ST_, R = entry, stop, (entry - stop) * side
    if not (R > 0):
        return dict(ok=False)
    cost = (ins['spread'] + ins['tick']) / R
    half, stop_px, r_real = False, ST_, 0.0
    end = min(len(d5) - 1, loc + hold)
    how, exit_t = 'time', d5.index[end]
    for q in range(loc + 1, end + 1):
        b = d5.iloc[q]; hi, lo = float(b.h), float(b.l)
        adverse = lo <= stop_px if side > 0 else hi >= stop_px
        if adverse:
            r_real += (0.5 if half else 1.0) * ((stop_px - E) * side / R)
            exit_t, how = d5.index[q], ('BE' if half else 'stop'); break
        if not half and ((hi >= tp1) if side > 0 else (lo <= tp1)):
            half = True; r_real += 0.5; stop_px = E
        if half and ((hi >= tp2) if side > 0 else (lo <= tp2)):
            r_real += 0.5 * 2.0; exit_t, how = d5.index[q], 'tp2'; break
    else:
        c = float(d5.c.iloc[end])
        r_real += (0.5 if half else 1.0) * ((c - E) * side / R)
        how = 'tp1_then_time' if half else ('open_mtm' if end < loc + hold else 'time')
    return dict(ok=True, how=how, R=round(r_real - cost, 3), R_gross=round(r_real, 3),
                cost_R=round(cost, 3), tp1_hit=half, exit_t=str(exit_t))

def main():
    data = pickle.load(open(REV / 'data_5m_1h.pkl', 'rb'))
    ev = pd.read_csv(REV / 'signals_evaluated.csv')
    sent = ev[ev.telegram.isin(['sent', 'sent_chat'])].copy()
    # reset replay state
    stpath = Path(os.environ['S1_STATE'])
    if stpath.exists():
        stpath.unlink()
    rows = []
    for _, rec in sent.iterrows():
        key, side = rec['key'], int(rec['side'])
        bar = pd.Timestamp(rec['bar_cairo'])
        if bar.tzinfo is None:
            bar = bar.tz_localize(CAIRO)
        t_utc = bar.tz_convert('UTC')
        fr = asof_frames(data, key, t_utc)
        try:
            cands, st = N.scan_one(key, now=fr['t_asof'], ignore_state=True,
                                   frames={'5m': fr['d5'], '1h': fr['d1h'], '15m': fr['d15'], '1m': None})
        except Exception as e:
            rows.append(dict(id=rec['id'], key=key, side=side, date=rec['date'], cairo=rec['cairo'],
                             old_det=rec['det'], old_R=rec['imm_R'], survive_filters=False,
                             survive_state=False, reason=f'error: {e}', klass=None, new_R=None,
                             blockers='', entry_state=None)); continue
        # pick candidate matching side (core preferred)
        match = [c for c in cands if c['side'] == side]
        core = [c for c in match if c['det'] in S.CORE_TRIGGERS]
        chosen = (core or match or [None])[0]
        if chosen is None:
            reason = 'مفيش زناد أساسي على آخر شمعة 5m المقفولة'
            if rec['det'] not in S.CORE_TRIGGERS:
                reason = f'الزناد الأصلي {rec["det"]} مش أساسي ومافيش sweep_rej/kzs على الشمعة'
            rows.append(dict(id=rec['id'], key=key, side=side, date=rec['date'], cairo=rec['cairo'],
                             old_det=rec['det'], old_R=rec['imm_R'], survive_filters=False,
                             survive_state=False, reason=reason, klass=None, new_R=None,
                             blockers='', entry_state=None)); continue
        # apply state on top of filter result
        state_block = ST.reasons_blocked(key, side, chosen['entry'], chosen['atr5'], chosen['sess'], fr['t_asof'])
        survive_f = bool(chosen['qualified'])
        # qualified already ignored state; but tools/filters are in chosen.blockers
        # Recompute qualified without state (already ignore_state=True)
        survive_s = survive_f and not state_block
        reason = '—'
        if not survive_f:
            reason = '؛ '.join(chosen['blockers'][:4]) or 'غير مؤهل'
        elif state_block:
            reason = '؛ '.join(state_block)
        new_R = None; how = None
        if survive_s:
            sim = simulate_new(data[key]['5m'], t_utc, side, chosen['entry'], chosen['stop'],
                               chosen['tp1'], chosen['tp2'], S.UNIVERSE[key])
            new_R, how = sim.get('R'), sim.get('how')
            ST.record(key, side, chosen['entry'], chosen['atr5'], chosen['sess'], fr['t_asof'],
                      klass=chosen['klass'], det=chosen['det'], telegram='replay')
        rows.append(dict(
            id=rec['id'], key=key, side=side, date=rec['date'], cairo=rec['cairo'],
            old_det=rec['det'], old_R=rec['imm_R'], old_how=rec['imm_how'],
            new_det=chosen['det'], klass=chosen['klass'], setup=chosen.get('setup_type'),
            entry_state=chosen.get('entry_state'),
            survive_filters=survive_f, survive_state=survive_s, reason=reason,
            blockers='; '.join(chosen.get('blockers') or []),
            agree='; '.join((chosen.get('agree') or [])[:4]),
            vetoes='; '.join(((chosen.get('tools') or {}).get('vetoes') or [])),
            new_entry=chosen['entry'], new_stop=chosen['stop'],
            new_R=new_R, new_how=how, cost_R=round(chosen['cost_R'], 3),
            chat_line=chosen.get('chat_line'),
        ))
        print(f"{rec['id']:22} {key:6} old={rec['det']:10} -> {chosen['det']:10} "
              f"{'PASS' if survive_s else 'DROP'} {reason[:80]}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(REV / 'replay_cleanup.csv', index=False)
    surv = df[df.survive_state == True]
    filt = df[df.survive_filters == True]
    def agg(x):
        if x.empty: return dict(n=0)
        R = pd.to_numeric(x.new_R, errors='coerce').dropna()
        n = len(R)
        if n == 0: return dict(n=0)
        m = float(R.mean()); sd = float(R.std(ddof=1)) if n > 1 else float('nan')
        t = m / (sd / n**0.5) if n > 1 and sd == sd and sd > 0 else None
        return dict(n=int(n), wins=int((R>0).sum()), losses=int((R<0).sum()),
                    sumR=round(float(R.sum()), 2), avgR=round(m, 3),
                    t=None if t is None else round(t, 2),
                    verdict='experimental')
    summary = dict(
        label='S1 cleanup replay 20–26 Nov 2026. Experimental (n small). Dashboard data only.',
        n_original=int(len(df)),
        n_survive_filters=int(filt.shape[0]),
        n_survive_with_state=int(surv.shape[0]),
        dropped=int((~df.survive_state).sum()),
        original_sumR=round(float(pd.to_numeric(df.old_R, errors='coerce').sum()), 2),
        survived_old_R=round(float(pd.to_numeric(surv.old_R, errors='coerce').sum()), 2) if len(surv) else 0,
        survived_new_R=agg(surv),
        by_reason=df.loc[~df.survive_state, 'reason'].value_counts().to_dict(),
        by_old_det_dropped=df.loc[~df.survive_state].groupby('old_det').size().to_dict(),
        by_klass=surv.groupby('klass').size().to_dict() if len(surv) else {},
        rows=rows,
    )
    json.dump(summary, open(REV / 'replay_cleanup.json', 'w'), indent=2, ensure_ascii=False, default=str)
    print('\n==== SUMMARY ====')
    print('original', summary['n_original'], 'sumR', summary['original_sumR'])
    print('survive filters', summary['n_survive_filters'], 'with state', summary['n_survive_with_state'])
    print('new R', summary['survived_new_R'])
    print('dropped reasons', summary['by_reason'])

if __name__ == '__main__':
    main()
