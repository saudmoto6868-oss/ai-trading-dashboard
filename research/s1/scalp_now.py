#!/usr/bin/env python3
"""S1 scalp scanner (on demand). Live dashboard data only (modules.market_cache: Hyperliquid / OKX).
Usage:  python3 scalp_now.py <GOLD|SILVER|NDX|SPX|EURUSD|BTC|ETH|all> [--send] [--force] [--ignore-state]
  default        : scan, rank, write JSON + Arabic package for QUALIFIED setups only (no network sends)
  --force        : also render the best NON-qualified candidate as a 'watch only' package
  --send         : one Telegram media group (caption only, no second sendMessage) to the owner
  --ignore-state : skip 90-min cooldown / session cap / same-zone (debug or replay)
Status of S1: EXPERIMENTAL. Not advice, no probabilities.
Routine command: python3 /workspace/templates/S1/scalp_now.py all --send
"""
import os, sys, json, html, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
import s1_core as S, ar_style as A, s1_tools as T, s1_state as ST
CLUSTER = ST.CLUSTER
DET_AR = {'kzs': 'Kill Zone Sniper', 'sweep_rej': 'سحب سيولة + ذيل رفض',
          'lvl_sweep': 'سحب مستوى مهم (PDH/PDL/قمة-قاع الساعة)',
          'vwap2': 'رجوع من حزام VWAP ±2σ', 'zn': 'Scalp Zones (Stoch+RSI)',
          'psar_trend': 'قلب PSAR مع اتجاه الساعة'}
# prior is no longer used to pick a standalone PSAR send; kept as a weak tie-break among core triggers
PRIOR = {'kzs': 0.40, 'sweep_rej': 0.21, 'lvl_sweep': -0.02, 'vwap2': 0.10, 'zn': 0.12, 'psar_trend': 0.11}
CAIRO = 'Africa/Cairo'

def closed(df, tf_min):
    now = pd.Timestamp.now(tz='UTC'); return df[df.index + pd.Timedelta(minutes=tf_min) <= now]

def _setup_type(side, b, e9, e21):
    # With the 1h-bias filter every send is with the hourly trend.
    # A liquidity sweep is a short-term reversal inside that trend.
    if np.sign(e9 - e21) != side:
        return 'عكس قصير (مع اتجاه الساعة)'
    return 'استمرار مع اتجاه الساعة'

def _entry_state(c):
    drift = c['drift_R']; d = c['dec']
    zone = f"{c['entry']:.{d}f}"
    if drift < -0.05:
        return 'wait', f'انتظر وصول السعر للمنطقة {zone}'
    return 'now', 'ادخل الآن'

def _asof(df, t, tf_min):
    """Bars known at time t (bar close must be <= t)."""
    t = pd.Timestamp(t)
    if t.tzinfo is None: t = t.tz_localize('UTC')
    if df.index.tz is None: df = df.copy(); df.index = df.index.tz_localize('UTC')
    return df[df.index + pd.Timedelta(minutes=tf_min) <= t]

def scan_one(key, now=None, ignore_state=False, frames=None):
    ins = S.UNIVERSE[key]; feed = ins['feed']
    now = now or pd.Timestamp.now(tz='UTC')
    if frames is None:
        d5 = closed(S._norm(S.get_klines(feed, '5m', 600)), 5)
        d1h = closed(S._norm(S.get_klines(feed, '1h', 300)), 60)
        d1 = closed(S._norm(S.get_klines(feed, '1m', 200)), 1)
        d15 = closed(S._norm(S.get_klines(feed, '15m', 200)), 15)
    else:
        d5, d1h, d15 = frames['5m'], frames['1h'], frames['15m']
        d1 = frames.get('1m')
    d = S.add_context(d5, d1h); last_px = float(d1.c.iloc[-1]) if (d1 is not None and len(d1)) else float(d.c.iloc[-1])
    window = d.iloc[-120:].copy(); m = len(window)
    # FRESH: only the last closed 5m bar (not the one before it)
    sigs = [s for s in S.signals(window) if s['i'] >= m - 1]
    e9, e21 = S.ema(d15.c, 9).iloc[-1], S.ema(d15.c, 21).iloc[-1]
    sar1, tr1 = S.psar(d1) if (d1 is not None and len(d1) > 30) else (None, None)
    # group by side so tags can attach to a core trigger
    by_side = {}
    for s in sigs:
        by_side.setdefault(s['side'], []).append(s)
    out = []
    for side, group in by_side.items():
        cores = [s for s in group if s['det'] in S.CORE_TRIGGERS]
        tags = [s for s in group if s['det'] in S.CONFLUENCE_TAGS]
        if not cores:
            # never send tag-only (PSAR / zn / vwap2 / lvl_sweep)
            for s in tags:
                p_try = S.plan(s, window, ins)
                if not p_try: continue
                out.append(_pack(key, feed, ins, s, p_try, window, last_px, e9, e21, tr1,
                                 tags=[], tools=None, cores_missing=True,
                                 ignore_state=ignore_state, now=now, d15=d15, d1h=d1h, d5=d))
            continue
        # one package per side: best core (kzs preferred)
        cores.sort(key=lambda s: -PRIOR.get(s['det'], 0))
        primary = cores[0]
        extra_cores = [s for s in cores[1:]]
        # tools first so plan() can use structure stops (need a provisional risk)
        b = window.iloc[primary['i']]
        prov = S.plan(primary, window, ins)
        if not prov:
            continue
        tools = T.read_tools(d5, d15, d1h, ins, side, prov['entry'], prov['risk'], prov['atr'], trigger_bar=b)
        p = S.plan(primary, window, ins, structure_stops=tools.get('structure_stops'))
        if not p:
            continue
        # re-read tools with the final risk (veto distance is in R)
        if abs(p['risk'] - prov['risk']) / max(prov['risk'], 1e-9) > 0.15:
            tools = T.read_tools(d5, d15, d1h, ins, side, p['entry'], p['risk'], p['atr'], trigger_bar=b)
        tag_names = [s['det'] for s in tags] + [s['det'] for s in extra_cores]
        out.append(_pack(key, feed, ins, primary, p, window, last_px, e9, e21, tr1,
                         tags=tag_names, tools=tools, cores_missing=False,
                         ignore_state=ignore_state, now=now, d15=d15, d1h=d1h, d5=d,
                         extra_cores=extra_cores))
    return out, dict(key=key, last=last_px, sess=window.sess.iloc[-1], bar=str(window.index[-1]))

def _pack(key, feed, ins, s, p, dd, last_px, e9, e21, tr1, tags, tools, cores_missing,
          ignore_state, now, d15, d1h, d5, extra_cores=None):
    b = dd.iloc[s['i']]; side = s['side']; R = p['risk']
    cost_R = (ins['spread'] + ins['tick']) / R
    drift = (last_px - p['entry']) * side / R
    agree, against, blockers = [], [], []
    (agree if b.bias == side else against).append('اتجاه الساعة EMA20/50 ' + ('صاعد' if b.bias > 0 else 'هابط'))
    (agree if np.sign(e9 - e21) == side else against).append('EMA 9/21 على 15m')
    (agree if b.sartr == side else against).append('PSAR 5m')
    if tr1 is not None:
        (agree if tr1.iloc[-1] == side else against).append('PSAR 1m (تأكيد الدخول)')
    vw_ok = (b.c < b.vw) if side > 0 else (b.c > b.vw)
    (agree if vw_ok else against).append('مكان السعر من VWAP (' + ('خصم' if b.c < b.vw else 'علاوة') + ')')
    if (side > 0 and b.k < 30) or (side < 0 and b.k > 70):
        agree.append(f'Stoch 5m {b.k:.0f}')
    lv = [nm for nm in ('pdh', 'pdl', 'ph1h', 'pl1h') if b[nm] == b[nm] and abs(b[nm] - s['raw_stop']) <= 0.4 * p['atr']]
    if lv:
        agree.append('السحب عند مستوى ' + '/'.join(x.upper() for x in lv))
    # hard filters (kept)
    if b.sess not in ('London KZ', 'NY AM KZ'):
        blockers.append(f'خارج Kill Zone (الجلسة: {b.sess})')
    if b.bias != side:
        blockers.append('ضد اتجاه الساعة (فلتر bias)')
    if cost_R > 0.08:
        blockers.append(f'التكلفة {cost_R:.2f}R > 0.08R (الوقف صغير قوي بالنسبة للسبريد)')
    if drift > 0.3:
        blockers.append(f'السعر مشي {drift:.2f}R من الدخول (متأخرين)')
    if drift < -0.8:
        blockers.append('السعر قرّب من الوقف')
    if b.ext1h * side > 2.5:
        blockers.append(f'مطاردة: ممتد {b.ext1h:.1f} ATR-1h عن EMA20 في نفس الاتجاه (فلتر المكتب)')
    # freshness is already enforced by scanning only the last closed bar
    if not S.reaction_ok(b, side):
        blockers.append('مفيش رد فعل تأكيدي على شمعة الزناد (ذيل رفض أو إزاحة)')
    if cores_missing:
        blockers.append(f'الكاشف {DET_AR.get(s["det"], s["det"])} مش زناد أساسي — بيتبعتش لوحده')
    # tools
    tool_agree = list((tools or {}).get('agree') or [])
    tool_against = list((tools or {}).get('against') or [])
    tool_veto = list((tools or {}).get('vetoes') or [])
    agree = agree + tool_agree
    against = against + tool_against
    if tool_veto:
        blockers.extend(tool_veto)
    # classification
    tag_ar = [DET_AR[t] for t in (tags or []) if t in DET_AR]
    strong = (tools or {}).get('strong_agree') or 0
    if tag_ar:
        strong += 1  # a same-bar confluence tag counts
    if cores_missing:
        klass, klass_ar = 'tag', 'غير مرسل — تلاقي فقط'
    elif tool_veto:
        klass, klass_ar = 'veto', 'موقوف بفيتو'
    elif strong >= 1:
        klass, klass_ar = 'A', 'أ — زناد أساسي مع تلاقي'
    else:
        klass, klass_ar = 'B', 'ب — زناد أساسي لوحده'
    # state / cooldown
    if not ignore_state and not cores_missing:
        blockers.extend(ST.reasons_blocked(key, side, p['entry'], p['atr'], b.sess, now))
    setup = _setup_type(side, b, e9, e21)
    score = PRIOR.get(s['det'], 0) + 0.1 * len(agree) - 0.1 * len(against) - 0.5 * len(blockers)
    score += (tools or {}).get('score') or 0
    pt = ins['pt']
    rec = dict(key=key, feed=feed, det=s['det'], det_ar=DET_AR[s['det']], side=side,
               t=str(dd.index[s['i']]), sess=b.sess,
               entry=p['entry'], stop=p['stop'], tp1=p['tp1'], tp2=p['tp2'],
               risk=R, risk_pts=R / pt, tp1_pts=R / pt, tp2_pts=2 * R / pt,
               atr5=p['atr'], cost_R=cost_R, last=last_px, drift_R=drift,
               agree=agree, against=against, blockers=blockers,
               qualified=not blockers, score=round(score, 3), dec=ins['dec'], pt=pt,
               level=s.get('level'), ext1h=float(b.ext1h), vwap=float(b.vw), bias=int(b.bias),
               klass=klass, klass_ar=klass_ar, tags=tags or [], tags_ar=tag_ar,
               setup_type=setup, tools=tools or {}, extra_cores=[x['det'] for x in (extra_cores or [])])
    kind, state = _entry_state(rec)
    rec['entry_kind'] = kind
    rec['entry_state'] = state
    tl = pd.Timestamp(rec['t']).tz_convert(CAIRO)
    rec['valid_until'] = (tl + pd.Timedelta(minutes=60)).strftime('%H:%M')
    rec['valid_until_iso'] = str(tl + pd.Timedelta(minutes=60))
    rec['chat_line'] = chat_line(rec)
    return rec

def fmt(v, d): return f"{v:,.{d}f}"

def text_ar(c):
    """Telegram caption (keep under 1024). Fixed layout."""
    d = c['dec']; side = 'شراء' if c['side'] > 0 else 'بيع'
    tl = pd.Timestamp(c['t']).tz_convert(CAIRO)
    L = [
        f"س1 · فئة {c['klass']} · {c['key']} {side}",
        f"الحالة: {c['entry_state']}",
        f"الدخول: {fmt(c['entry'], d)} · الوقف: {fmt(c['stop'], d)} ({c['risk_pts']:.0f} نقطة = 1R)",
        f"T1: {fmt(c['tp1'], d)} (1R) · T2: {fmt(c['tp2'], d)} (2R)",
        f"الصلاحية حتى {c['valid_until']} القاهرة",
        f"الزناد: {c['det_ar']} · النوع: {c['setup_type']}",
    ]
    conf = c.get('tags_ar') or []
    conf += [x for x in (c.get('tools') or {}).get('agree') or [] if x not in conf]
    if conf:
        L.append('التلاقي: ' + '؛ '.join(conf[:5]))
    why = (c.get('agree') or [])[:3]
    for i, w in enumerate(why, 1):
        L.append(f'- {w}')
    if not why:
        L.append('- —')
    veto = (c.get('blockers') or []) + (c.get('against') or [])[:2]
    L.append('ضد/فيتو: ' + ('؛ '.join(veto[:3]) if veto else '—'))
    L.append('S1 تجريبي · تعليمي، مش نصيحة مالية · بيانات الداشبورد فقط')
    txt = '\n'.join(L)
    return txt[:1000]

def chat_line(c):
    side = 'شراء' if c['side'] > 0 else 'بيع'
    d = c['dec']
    return (f"س1 {c['klass']} · {c['key']} {side} · {c['entry_state']} @ {fmt(c['entry'], d)}"
            f" · وقف {fmt(c['stop'], d)} · T1 {fmt(c['tp1'], d)} · حتى {c['valid_until']}"
            f" · {c['det_ar']}")

def cards(c, charts, outdir, page):
    d = c['dec']; side_ar = 'شراء' if c['side'] > 0 else 'بيع'
    col = '#2fd6a0' if c['side'] > 0 else '#ff5d73'
    A.FOOT = "<div class=foot>محتوى تعليمي وليس نصيحة مالية · البيانات: AI Trading Dashboard (Hyperliquid/OKX) · S1 تجريبي · بدون احتمالات</div>"
    total = 1 + len([x for x in charts.values() if x]); outs = []
    q = ('مؤهلة', '#46e0ae') if c['qualified'] else ('مراقبة فقط', '#f0c27b')
    tl = pd.Timestamp(c['t']).tz_convert(CAIRO).strftime('%H:%M')
    rows = ''.join(f"<div class=pc><div class=k>{k}</div><div class=v>{v}</div><div class=k>{w}</div></div>" for k, v, w in [
        (f'{side_ar} · دخول', fmt(c['entry'], d), ''), ('وقف', fmt(c['stop'], d), f"{c['risk_pts']:.0f} نقطة"),
        ('T1 · 1R', fmt(c['tp1'], d), f"+{c['tp1_pts']:.0f} نقطة"), ('T2 · 2R', fmt(c['tp2'], d), f"+{c['tp2_pts']:.0f} نقطة")])
    li = lambda xs: ''.join(f"<li>{A.L(x)}</li>" for x in xs) or '<li>—</li>'
    css = "ul{margin:6px 24px 0 0}li{font:500 21px/1.5 Cairo;color:#e4dfdb}.pc{padding:10px 8px}.pc .v{font-size:32px}.pc .k{font-size:17px}.sec{margin-top:10px;padding:10px 14px}.sec h4{font-size:22px}.sec p{font-size:20px}.hap{font-size:20px;padding:8px 12px}"
    h = A.head(1, total, f"سكالب S1 · فئة {c['klass']} · {tl} القاهرة · {c['sess']}", css) + f"""
<div class=hrow><div class=title>{c['key']} <span class=en>{side_ar}</span></div>
<div class=pills><div class=st style="color:{q[1]};border:2px solid {q[1]}">{q[0]}</div>
<div class=st style="color:#f0c27b;border:2px solid #f0c27b">فئة {c['klass']}</div></div></div>
<div class=hap style="border-right-color:{col}"><b>الحالة:</b> {A.L(c['entry_state'])} · صلاحية حتى {A.L(c['valid_until'])} · {A.L(c['det_ar'])} · {A.L(c['setup_type'])}</div>
<div class=pos>{rows}</div>
<div class="sec v"><h4>مدارس مع الصفقة</h4><ul>{li((c['agree'] or [])[:8])}</ul></div>
<div class="sec m"><h4>ضدها / موانع</h4><ul>{li((c['against'] or []) + (c['blockers'] or []))}</ul></div>
<div class="sec s"><h4>الإدارة</h4><p>{A.L('نص الكمية عند T1 ثم الوقف على الدخول · T2 عند 2R · وقف زمني 60 دقيقة · الإلغاء بإغلاق 5m ورا الوقف')}</p></div>
""" + A.foot()
    pth = Path(outdir) / '01_plan_ar.png'; A.shoot(page, h, pth); outs.append(pth)
    k = 1
    for tf, cp in charts.items():
        if not cp: continue
        k += 1
        h = A.head(k, total, f"{c['key']} · فريم {tf} · المربع = الدخول/الوقف/الأهداف", ".chart img{width:992px}.pc .v{font-size:30px}.hap{font-size:21px;margin-top:12px}") + f"""
<div class=hrow><div class=title>{c['key']} <span class=en>{tf}</span></div><div class=pills><div class=st style="color:{col};border:2px solid {col}">{side_ar}</div></div></div>
<div class=chart><img src="file://{cp}"></div>
<div class=pos>{rows}</div>
<div class=hap><b>ليه الفريم ده:</b> {A.L({'1m': 'تأكيد الدخول: PSAR 1m وشمعة رفض قبل التنفيذ', '5m': 'فريم الإشارة: السحب/الرفض وزونات السكالب وPSAR', '15m': 'الهيكل القريب: EMA 9/21 وMSB/OB وFVG', '1H': 'الاتجاه: EMA20/50 ومستويات Gann وX77 والهارمونيك'}[tf])}</div>
""" + A.foot()
        pth = Path(outdir) / f"{k:02d}_{tf}_ar.png"; A.shoot(page, h, pth); outs.append(pth)
    return outs

def send_telegram(files, text):
    """ONE media group with caption. No second sendMessage."""
    import requests
    tok, chat = os.environ.get('XPIX_BOT_TOKEN'), os.environ.get('XPIX_OWNER_CHAT_ID')
    if not tok or not chat:
        return 'missing XPIX_BOT_TOKEN / XPIX_OWNER_CHAT_ID'
    base = f"https://api.telegram.org/bot{tok}"
    media = [{'type': 'photo', 'media': f'attach://f{i}'} for i in range(len(files))]
    media[0]['caption'] = text[:1024]
    fh = {f'f{i}': open(f, 'rb') for i, f in enumerate(files)}
    r1 = requests.post(base + '/sendMediaGroup', data={'chat_id': chat, 'media': json.dumps(media)}, files=fh, timeout=60)
    return f'sendMediaGroup {r1.status_code}'

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; which = (args[0] if args else 'all').upper()
    keys = list(S.UNIVERSE) if which == 'ALL' else [which]
    ignore_state = '--ignore-state' in sys.argv
    stamp = pd.Timestamp.now(tz=CAIRO).strftime('%Y%m%d_%H%M'); outdir = HERE / 'out' / stamp; outdir.mkdir(parents=True, exist_ok=True)
    now = pd.Timestamp.now(tz='UTC')
    cands, states = [], []
    for k in keys:
        try:
            c, st = scan_one(k, now=now, ignore_state=ignore_state); cands += c; states.append(st)
        except Exception as e:
            states.append(dict(key=k, error=str(e)))
    cands.sort(key=lambda c: (-c['qualified'], -c['score']))
    seen = set(); cands = [c for c in cands if not ((c['key'], c['det'], c['side']) in seen or seen.add((c['key'], c['det'], c['side'])))]
    picks, used = [], {}
    for c in cands:
        if c['qualified'] and used.get(CLUSTER[c['key']], 0) < 1:
            picks.append(c); used[CLUSTER[c['key']]] = 1
    if not picks and '--force' in sys.argv and cands:
        picks = [cands[0]]
    # max 2 packages still, but cluster cap already limits this
    summary = dict(time_cairo=stamp, scanned=states, candidates=cands,
                   qualified=[c for c in cands if c['qualified']], packaged=[],
                   chat_lines=[])
    if picks:
        from playwright.sync_api import sync_playwright
        import chart_render as CR
        for c in picks[:2]:
            od = outdir / f"{c['key']}_{c['det']}"; od.mkdir(exist_ok=True)
            plan = dict(entry=c['entry'], sl=c['stop'], tp1=c['tp1'], tp2=c['tp2'], tp3=None)
            t0 = int(pd.Timestamp(c['t']).timestamp() * 1000)
            charts = CR.render(c['feed'], ['1m', '5m', '15m', '1H'], plan, c['side'], od, t0_ms=t0)
            with sync_playwright() as pw:
                b = pw.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True,
                                       args=["--no-sandbox", "--disable-gpu"])
                page = b.new_context(viewport={"width": 1080, "height": 1350}, device_scale_factor=2).new_page()
                files = cards(c, charts, od, page); b.close()
            txt = text_ar(c); (od / 'message_ar.txt').write_text(txt)
            (od / 'chat_line.txt').write_text(c['chat_line'])
            sent = 'not sent (no --send, or not qualified)'
            if '--send' in sys.argv and c['qualified']:
                sent = send_telegram([str(f) for f in files], txt)
                if str(sent).startswith('sendMediaGroup 200'):
                    ST.record(c['key'], c['side'], c['entry'], c['atr5'], c['sess'], now,
                              klass=c['klass'], det=c['det'], telegram=sent)
            summary['packaged'].append(dict(key=c['key'], det=c['det'], klass=c['klass'],
                                            qualified=c['qualified'], entry_state=c['entry_state'],
                                            files=[str(f) for f in files], message=str(od / 'message_ar.txt'),
                                            telegram=sent, chat_line=c['chat_line']))
            summary['chat_lines'].append(c['chat_line'])
    json.dump(summary, open(outdir / 'scan.json', 'w'), indent=1, ensure_ascii=False, default=str)
    print(f"scan {stamp} Cairo · {len(cands)} candidates · {len(summary['qualified'])} qualified · out: {outdir}")
    for st in states:
        print('  ', st)
    for c in cands[:10]:
        flag = 'QUALIFIED' if c['qualified'] else 'blocked: ' + '; '.join(c['blockers'])
        print(f"  {c['key']:6} {c['klass']:4} {c['det']:10} {'BUY ' if c['side']>0 else 'SELL'} entry {c['entry']:.{c['dec']}f} stop {c['stop']:.{c['dec']}f} score {c['score']:+.2f} {flag}")
    for p in summary['packaged']:
        print('  package', p['key'], p['det'], p.get('klass'), p['telegram'])
        print('    CHAT:', p.get('chat_line'))
        print('   ', *p['files'], p['message'])

if __name__ == '__main__':
    main()
