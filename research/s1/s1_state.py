#!/usr/bin/env python3
"""Persistent send-state for S1: cooldown, cluster cap, session cap, same-zone skip.
Runtime file only (not committed). Written after a successful Telegram send."""
from __future__ import annotations
import json, os
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
STATE = Path(os.environ.get('S1_STATE', HERE / 'state' / 'sent.json'))
CAIRO = 'Africa/Cairo'
CLUSTER = {'GOLD': 'usd_metals', 'SILVER': 'usd_metals', 'EURUSD': 'usd_metals',
           'NDX': 'us_equity', 'SPX': 'us_equity', 'BTC': 'crypto', 'ETH': 'crypto'}
COOL_MIN = 90
SESSION_CAP = 3
ZONE_ATR = 0.25

def _load():
    if not STATE.exists():
        return {'sent': []}
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {'sent': []}

def _save(obj):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str))
    tmp.replace(STATE)

def _ts(x):
    t = pd.Timestamp(x)
    if t.tzinfo is None:
        t = t.tz_localize('UTC')
    return t

def reasons_blocked(key, side, entry, atr, sess, now, ignore=False):
    """-> list of Arabic blocker strings, empty if clear."""
    if ignore:
        return []
    recs = _load().get('sent') or []
    now = _ts(now)
    out = []
    cluster = CLUSTER[key]
    recent = []
    for r in recs:
        t = _ts(r['t'])
        age = (now - t).total_seconds() / 60.0
        if age < 0:
            continue
        recent.append((age, r))
    for age, r in recent:
        if age > COOL_MIN:
            continue
        if r.get('key') == key and int(r.get('side', 0)) == int(side):
            out.append(f'تبريد 90 دقيقة على {key} نفس الاتجاه (آخر إشارة من {age:.0f} د)')
            break
    for age, r in recent:
        if age > COOL_MIN:
            continue
        if r.get('cluster') == cluster and not (r.get('key') == key and int(r.get('side', 0)) == int(side)):
            out.append(f'تبريد 90 دقيقة على المجموعة {cluster} (آخرها {r.get("key")} من {age:.0f} د)')
            break
    # same zone, even a bit longer (4h) so we don't re-fire the same pocket
    for age, r in recent:
        if age > 240:
            continue
        if r.get('key') == key and int(r.get('side', 0)) == int(side):
            prev = float(r.get('entry', 0) or 0)
            a = float(atr or r.get('atr') or 0) or 1e-9
            if abs(prev - float(entry)) <= ZONE_ATR * a:
                out.append('نفس منطقة الدخول اتبعتت قبل كده')
                break
    # session cap: same Cairo day + same kill-zone name
    day = now.tz_convert(CAIRO).strftime('%Y-%m-%d')
    n_sess = 0
    for age, r in recent:
        rt = _ts(r['t']).tz_convert(CAIRO)
        if rt.strftime('%Y-%m-%d') == day and r.get('session') == sess:
            n_sess += 1
    if n_sess >= SESSION_CAP:
        out.append(f'وصلنا لحد {SESSION_CAP} إشارات في جلسة {sess} النهاردة')
    # unique
    seen, uniq = set(), []
    for b in out:
        if b not in seen:
            seen.add(b); uniq.append(b)
    return uniq

def record(key, side, entry, atr, sess, now, klass=None, det=None, telegram=None):
    obj = _load()
    obj.setdefault('sent', []).append(dict(
        t=str(_ts(now)), key=key, side=int(side), cluster=CLUSTER[key],
        session=sess, entry=float(entry), atr=float(atr or 0),
        klass=klass, det=det, telegram=telegram,
    ))
    # keep last 400
    obj['sent'] = obj['sent'][-400:]
    _save(obj)
