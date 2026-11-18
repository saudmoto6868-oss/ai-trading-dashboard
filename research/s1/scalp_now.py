#!/usr/bin/env python3
"""S1 scalp scanner (on demand). Live dashboard data only (modules.market_cache: Hyperliquid / OKX).
Usage:  python3 scalp_now.py <GOLD|SILVER|NDX|SPX|EURUSD|BTC|ETH|all> [--send] [--force]
  default : scan, rank, write JSON + Arabic package for QUALIFIED setups only (no network sends)
  --force : also render the best NON-qualified candidate as a 'watch only' package (for testing / study)
  --send  : send the package to Telegram (env XPIX_BOT_TOKEN, XPIX_OWNER_CHAT_ID). Send-only API calls; never getUpdates.
Status of S1: EXPERIMENTAL (backtest 18 Nov: no rule reached n>=100 & t>3 net of costs). Not advice, no probabilities."""
import os, sys, json, html, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
import s1_core as S, ar_style as A
CLUSTER = {'GOLD': 'usd_metals', 'SILVER': 'usd_metals', 'EURUSD': 'usd_metals', 'NDX': 'us_equity', 'SPX': 'us_equity', 'BTC': 'crypto', 'ETH': 'crypto'}
DET_AR = {'kzs': 'Kill Zone Sniper', 'sweep_rej': 'سحب سيولة + ذيل رفض', 'lvl_sweep': 'سحب مستوى مهم (PDH/PDL/قمة-قاع الساعة)',
          'vwap2': 'رجوع من حزام VWAP ±2σ', 'zn': 'Scalp Zones (Stoch+RSI)', 'psar_trend': 'قلب PSAR مع اتجاه الساعة'}
# backtest 18 Nov (5m, bias+KZ, gross avg R before costs) -> prior weight only, NOT a probability
PRIOR = {'kzs': 0.40, 'sweep_rej': 0.21, 'lvl_sweep': -0.02, 'vwap2': 0.10, 'zn': 0.12, 'psar_trend': 0.11}
CAIRO = 'Africa/Cairo'

def closed(df, tf_min):
    now = pd.Timestamp.now(tz='UTC'); return df[df.index + pd.Timedelta(minutes=tf_min) <= now]

def scan_one(key):
    ins = S.UNIVERSE[key]; feed = ins['feed']
    d5 = closed(S._norm(S.get_klines(feed, '5m', 600)), 5); d1h = closed(S._norm(S.get_klines(feed, '1h', 300)), 60)
    d1 = closed(S._norm(S.get_klines(feed, '1m', 200)), 1); d15 = closed(S._norm(S.get_klines(feed, '15m', 200)), 15)
    d = S.add_context(d5, d1h); n = len(d); last_px = float(d1.c.iloc[-1]) if len(d1) else float(d.c.iloc[-1])
    sigs = [s for s in S.signals(d.iloc[-120:].copy()) ]
    # signals() indexes are relative to the slice; keep only the last 2 closed 5m bars
    m = len(d.iloc[-120:]); sigs = [s for s in sigs if s['i'] >= m - 2]
    dd = d.iloc[-120:]; out = []
    e9, e21 = S.ema(d15.c, 9).iloc[-1], S.ema(d15.c, 21).iloc[-1]
    sar1, tr1 = S.psar(d1) if len(d1) > 30 else (None, None)
    for s in sigs:
        p = S.plan(s, dd, ins)
        if not p: continue
        b = dd.iloc[s['i']]; side = s['side']; R = p['risk']; cost_R = (ins['spread'] + ins['tick']) / R
        drift = (last_px - p['entry']) * side / R
        agree, against, blockers = [], [], []
        (agree if b.bias == side else against).append('اتجاه الساعة EMA20/50 ' + ('صاعد' if b.bias > 0 else 'هابط'))
        (agree if np.sign(e9 - e21) == side else against).append('EMA 9/21 على 15m')
        (agree if b.sartr == side else against).append('PSAR 5m')
        if tr1 is not None: (agree if tr1.iloc[-1] == side else against).append('PSAR 1m (تأكيد الدخول)')
        vw_ok = (b.c < b.vw) if side > 0 else (b.c > b.vw)
        (agree if vw_ok else against).append('مكان السعر من VWAP (' + ('خصم' if b.c < b.vw else 'علاوة') + ')')
        if side > 0 and b.k < 30 or side < 0 and b.k > 70: agree.append(f'Stoch 5m {b.k:.0f}')
        lv = [nm for nm in ('pdh', 'pdl', 'ph1h', 'pl1h') if b[nm] == b[nm] and abs(b[nm] - s['raw_stop']) <= 0.4 * p['atr']]
        if lv: agree.append('السحب عند مستوى ' + '/'.join(x.upper() for x in lv))
        if b.sess not in ('London KZ', 'NY AM KZ'): blockers.append(f'خارج Kill Zone (الجلسة: {b.sess})')
        if b.bias != side: blockers.append('ضد اتجاه الساعة (فلتر bias)')
        if cost_R > 0.08: blockers.append(f'التكلفة {cost_R:.2f}R > 0.08R (الوقف صغير قوي بالنسبة للسبريد)')
        if drift > 0.3: blockers.append(f'السعر مشي {drift:.2f}R من الدخول (متأخرين)')
        if drift < -0.8: blockers.append('السعر قرّب من الوقف')
        if b.ext1h * side > 2.5: blockers.append(f'مطاردة: ممتد {b.ext1h:.1f} ATR-1h عن EMA20 في نفس الاتجاه (فلتر المكتب)')
        score = PRIOR.get(s['det'], 0) + 0.1 * len(agree) - 0.1 * len(against) - 0.5 * len(blockers)
        pt = ins['pt']
        out.append(dict(key=key, feed=feed, det=s['det'], det_ar=DET_AR[s['det']], side=side, t=str(dd.index[s['i']]), sess=b.sess,
                        entry=p['entry'], stop=p['stop'], tp1=p['tp1'], tp2=p['tp2'], risk=R, risk_pts=R / pt, tp1_pts=R / pt, tp2_pts=2 * R / pt,
                        atr5=p['atr'], cost_R=cost_R, last=last_px, drift_R=drift, agree=agree, against=against, blockers=blockers,
                        qualified=not blockers, score=round(score, 3), dec=ins['dec'], pt=pt, level=s.get('level'),
                        ext1h=float(b.ext1h), vwap=float(b.vw), bias=int(b.bias)))
    return out, dict(key=key, last=last_px, sess=dd.sess.iloc[-1], bar=str(dd.index[-1]))

def fmt(v, d): return f"{v:,.{d}f}"

def text_ar(c):
    d = c['dec']; side = 'شراء' if c['side'] > 0 else 'بيع'; tl = pd.Timestamp(c['t']).tz_convert(CAIRO)
    ts = (tl + pd.Timedelta(minutes=65)).strftime('%H:%M')
    st = 'مؤهلة حسب S1' if c['qualified'] else 'مراقبة فقط — مش مؤهلة'
    L = [f"⚡ سكالب S1 · {c['key']} · {side} · {st}",
         f"الإشارة: {c['det_ar']} على شمعة 5m الساعة {tl.strftime('%H:%M')} القاهرة ({c['sess']})",
         f"الدخول: {fmt(c['entry'], d)} · السعر دلوقتي {fmt(c['last'], d)}",
         f"الوقف: {fmt(c['stop'], d)} ({c['risk_pts']:.0f} نقطة = 1R)",
         f"T1: {fmt(c['tp1'], d)} (+{c['tp1_pts']:.0f} نقطة، 1R) — اقفل النص وحرّك الوقف للدخول",
         f"T2: {fmt(c['tp2'], d)} (+{c['tp2_pts']:.0f} نقطة، 2R)",
         f"وقف زمني: لو ما وصلش T1 لحد {ts} القاهرة (60 دقيقة) اخرج بسعر السوق",
         f"الإلغاء: إغلاق 5m ورا {fmt(c['stop'], d)}، أو لو السعر مشي أكتر من 0.3R قبل ما تدخل",
         f"النقطة = {c['pt']} (اصطلاح الداشبورد TCE.pointSize)",
         "مع الصفقة: " + ('، '.join(c['agree']) or '—'),
         "ضدها: " + ('، '.join(c['against']) or '—')]
    if c['blockers']: L.append("موانع: " + '، '.join(c['blockers']))
    L += ["تأكيد لايف (يدوي): دلتا/CVD في اتجاه الصفقة وامتصاص عند مستوى الوقف — مش مختبر.",
          "أخبار: اتأكد من الأجندة؛ ما ندخلش قبل خبر قوي بـ 15 دقيقة.",
          "مخاطرة: ≤0.5% للصفقة، ومجموعة مترابطة أقصاها 2R، وحد يومي −2R.",
          "حالة S1: تجريبي (باك تست 18 نوفمبر: مفيش قاعدة عدّت n≥100 و t>3 بعد التكاليف). تعليمي، مش نصيحة مالية، ومفيش احتمالات."]
    return '\n'.join(L)

def cards(c, charts, outdir, page):
    d = c['dec']; side_ar = 'شراء' if c['side'] > 0 else 'بيع'; col = '#2fd6a0' if c['side'] > 0 else '#ff5d73'
    A.FOOT = "<div class=foot>محتوى تعليمي وليس نصيحة مالية · البيانات: AI Trading Dashboard (Hyperliquid/OKX) · S1 تجريبي (لم يحقق n≥100 و t>3) · بدون احتمالات</div>"
    total = 1 + len([x for x in charts.values() if x]); outs = []
    q = ('مؤهلة', '#46e0ae') if c['qualified'] else ('مراقبة فقط', '#f0c27b')
    tl = pd.Timestamp(c['t']).tz_convert(CAIRO).strftime('%H:%M')
    rows = ''.join(f"<div class=pc><div class=k>{k}</div><div class=v>{v}</div><div class=k>{w}</div></div>" for k, v, w in [
        (f'{side_ar} · دخول', fmt(c['entry'], d), ''), ('وقف', fmt(c['stop'], d), f"{c['risk_pts']:.0f} نقطة"),
        ('T1 · 1R', fmt(c['tp1'], d), f"+{c['tp1_pts']:.0f} نقطة"), ('T2 · 2R', fmt(c['tp2'], d), f"+{c['tp2_pts']:.0f} نقطة")])
    li = lambda xs: ''.join(f"<li>{A.L(x)}</li>" for x in xs) or '<li>—</li>'
    css = "ul{margin:6px 24px 0 0}li{font:500 23px/1.6 Cairo;color:#e4dfdb}.pc{padding:12px 10px}.pc .v{font-size:34px}.pc .k{font-size:18px}.sec{margin-top:14px;padding:12px 16px}.sec h4{font-size:24px}.sec p{font-size:22px}.hap{font-size:21px;padding:10px 14px}"
    h = A.head(1, total, f"سكالب S1 · إشارة {tl} القاهرة · {c['sess']}", css) + f"""
<div class=hrow><div class=title>{c['key']} <span class=en>{side_ar}</span></div>
<div class=pills><div class=st style="color:{q[1]};border:2px solid {q[1]}">{q[0]}</div></div></div>
<div class=hap style="border-right-color:{col}"><b>الإشارة:</b> {A.L(c['det_ar'])} · السعر الآن {A.L(fmt(c['last'], d))} · ATR5 {A.L(fmt(c['atr5'], d))} · النقطة {A.L(str(c['pt']))}</div>
<div class=pos>{rows}</div>
<div class="sec v"><h4>مدارس مع الصفقة</h4><ul>{li(c['agree'])}</ul></div>
<div class="sec m"><h4>ضدها / موانع</h4><ul>{li(c['against'] + c['blockers'])}</ul></div>
<div class="sec s"><h4>الإدارة</h4><p>{A.L('نص الكمية عند T1 ثم الوقف على الدخول · T2 عند 2R · وقف زمني 60 دقيقة · الإلغاء بإغلاق 5m ورا الوقف')}</p></div>
<div class="sec r"><h4>مخاطرة وأخبار</h4><p>{A.L('≤0.5% للصفقة · المجموعة المترابطة ≤2R · ما ندخلش قبل خبر قوي بـ 15 دقيقة · Order Flow تأكيد لايف بس')}</p></div>
""" + A.foot()
    p = Path(outdir) / '01_plan_ar.png'; A.shoot(page, h, p); outs.append(p)
    k = 1
    for tf, cp in charts.items():
        if not cp: continue
        k += 1
        h = A.head(k, total, f"{c['key']} · فريم {tf} · المربع = الدخول/الوقف/الأهداف", ".chart img{width:992px}.pc .v{font-size:30px}.hap{font-size:21px;margin-top:12px}") + f"""
<div class=hrow><div class=title>{c['key']} <span class=en>{tf}</span></div><div class=pills><div class=st style="color:{col};border:2px solid {col}">{side_ar}</div></div></div>
<div class=chart><img src="file://{cp}"></div>
<div class=pos>{rows}</div>
<div class=hap><b>ليه الفريم ده:</b> {A.L({'1m': 'تأكيد الدخول: PSAR 1m وشمعة رفض قبل التنفيذ', '5m': 'فريم الإشارة: السحب/الرفض وزونات السكالب وPSAR', '15m': 'الهيكل القريب: EMA 9/21 وMSB/OB', '1H': 'الاتجاه: EMA20/50 ومستويات Gann وVWAP'}[tf])}</div>
""" + A.foot()
        p = Path(outdir) / f"{k:02d}_{tf}_ar.png"; A.shoot(page, h, p); outs.append(p)
    return outs

def send_telegram(files, text):
    import requests
    tok, chat = os.environ.get('XPIX_BOT_TOKEN'), os.environ.get('XPIX_OWNER_CHAT_ID')
    if not tok or not chat: return 'missing XPIX_BOT_TOKEN / XPIX_OWNER_CHAT_ID'
    base = f"https://api.telegram.org/bot{tok}"
    media = [{'type': 'photo', 'media': f'attach://f{i}'} for i in range(len(files))]
    media[0]['caption'] = text[:1000]
    fh = {f'f{i}': open(f, 'rb') for i, f in enumerate(files)}
    r1 = requests.post(base + '/sendMediaGroup', data={'chat_id': chat, 'media': json.dumps(media)}, files=fh, timeout=60)
    r2 = requests.post(base + '/sendMessage', data={'chat_id': chat, 'text': text[:4000]}, timeout=30)
    return f'sendMediaGroup {r1.status_code}, sendMessage {r2.status_code}'

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; which = (args[0] if args else 'all').upper()
    keys = list(S.UNIVERSE) if which == 'ALL' else [which]
    stamp = pd.Timestamp.now(tz=CAIRO).strftime('%Y%m%d_%H%M'); outdir = HERE / 'out' / stamp; outdir.mkdir(parents=True, exist_ok=True)
    cands, states = [], []
    for k in keys:
        try: c, st = scan_one(k); cands += c; states.append(st)
        except Exception as e: states.append(dict(key=k, error=str(e)))
    cands.sort(key=lambda c: (-c['qualified'], -c['score']))
    seen = set(); cands = [c for c in cands if not ((c['key'], c['det'], c['side']) in seen or seen.add((c['key'], c['det'], c['side'])))]
    picks, used = [], {}
    for c in cands:   # correlation cap: one qualified pick per cluster
        if c['qualified'] and used.get(CLUSTER[c['key']], 0) < 1: picks.append(c); used[CLUSTER[c['key']]] = 1
    if not picks and '--force' in sys.argv and cands: picks = [cands[0]]
    summary = dict(time_cairo=stamp, scanned=states, candidates=cands, qualified=[c for c in cands if c['qualified']], packaged=[])
    if picks:
        from playwright.sync_api import sync_playwright
        import chart_render as CR
        for c in picks[:2]:
            od = outdir / f"{c['key']}_{c['det']}"; od.mkdir(exist_ok=True)
            plan = dict(entry=c['entry'], sl=c['stop'], tp1=c['tp1'], tp2=c['tp2'], tp3=None)
            t0 = int(pd.Timestamp(c['t']).timestamp() * 1000)
            charts = CR.render(c['feed'], ['1m', '5m', '15m', '1H'], plan, c['side'], od, t0_ms=t0)
            with sync_playwright() as pw:
                b = pw.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox", "--disable-gpu"])
                page = b.new_context(viewport={"width": 1080, "height": 1350}, device_scale_factor=2).new_page()
                files = cards(c, charts, od, page); b.close()
            txt = text_ar(c); (od / 'message_ar.txt').write_text(txt)
            sent = send_telegram([str(f) for f in files], txt) if ('--send' in sys.argv and c['qualified']) else 'not sent (no --send, or not qualified)'
            summary['packaged'].append(dict(key=c['key'], det=c['det'], qualified=c['qualified'], files=[str(f) for f in files], message=str(od / 'message_ar.txt'), telegram=sent))
    json.dump(summary, open(outdir / 'scan.json', 'w'), indent=1, ensure_ascii=False, default=str)
    print(f"scan {stamp} Cairo · {len(cands)} candidates · {len(summary['qualified'])} qualified · out: {outdir}")
    for st in states: print('  ', st)
    for c in cands[:8]: print(f"  {c['key']:6} {c['det']:10} {'BUY ' if c['side']>0 else 'SELL'} entry {c['entry']:.{c['dec']}f} stop {c['stop']:.{c['dec']}f} score {c['score']:+.2f} {'QUALIFIED' if c['qualified'] else 'blocked: ' + '; '.join(c['blockers'])}")
    for p in summary['packaged']: print('  package', p['key'], p['det'], p['telegram'], *p['files'], p['message'], sep='\n    ')
if __name__ == '__main__': main()
