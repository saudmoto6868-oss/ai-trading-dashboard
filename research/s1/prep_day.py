#!/usr/bin/env python3
"""S1 daily prep: tomorrow's watchlist + key levels per instrument (dashboard data only: modules.market_cache).
Usage: python3 prep_day.py [YYYY-MM-DD target day, default = tomorrow Cairo] [--cards]
Levels: PDH/PDL for the target day = the high/low of the current UTC day (run in the evening before), plus the day before, week-to-date H/L + previous week H/L, today's closing VWAP, 5m volume-profile POC/VAH/VAL of the last day,
Asia range (forms 03:00-07:00 Cairo, filled live), Gann square-of-9 (±45/90/180°) around last price, unmitigated 1h FVG and last 1h OB (both sides),
kill-zone times in Cairo. Output: out/prep_<day>/levels.json (+ Arabic 4:5 cards with --cards). Local only."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
import s1_core as S, ar_style as A
CAIRO = 'Africa/Cairo'

def vp(d, bins=40):
    lo, hi = d.l.min(), d.h.max(); edges = np.linspace(lo, hi, bins + 1); tp = (d.h + d.l + d.c) / 3
    vol = np.histogram(tp, bins=edges, weights=d.v.where(d.v > 0, 1.0))[0]; mid = (edges[:-1] + edges[1:]) / 2
    poc = int(vol.argmax()); tot = vol.sum(); inc = {poc}; s = vol[poc]; a, b = poc, poc
    while s < 0.7 * tot and (a > 0 or b < bins - 1):
        na = vol[a - 1] if a > 0 else -1; nb = vol[b + 1] if b < bins - 1 else -1
        if nb >= na: b += 1; s += vol[b]
        else: a -= 1; s += vol[a]
    return float(mid[poc]), float(edges[b + 1]), float(edges[a])

def gann9(px):
    r = np.sqrt(px); return {f'{"+" if k > 0 else ""}{k}°': float((r + k / 180) ** 2) for k in (-180, -90, -45, 45, 90, 180)}

def zones_1h(h, last):
    """unmitigated 3-candle FVGs and last OB (opposite candle before a displacement > 1.5 ATR) on 1h."""
    a = S.atr(h); fv = []
    for i in range(2, len(h)):
        if h.l.iloc[i] > h.h.iloc[i - 2]: z = ('FVG+', h.h.iloc[i - 2], h.l.iloc[i], i)
        elif h.h.iloc[i] < h.l.iloc[i - 2]: z = ('FVG-', h.h.iloc[i], h.l.iloc[i - 2], i)
        else: continue
        after = h.iloc[i + 1:]
        filled = (after.l <= z[1]).any() if z[0] == 'FVG+' else (after.h >= z[2]).any()
        if not filled and (z[2] - z[1]) > 0.15 * a.iloc[i]: fv.append(dict(kind=z[0], lo=float(z[1]), hi=float(z[2]), t=str(h.index[i])))
    obs = []
    for i in range(len(h) - 2, 20, -1):
        body = abs(h.c.iloc[i + 1] - h.o.iloc[i + 1])
        if body > 1.5 * a.iloc[i]:
            up = h.c.iloc[i + 1] > h.o.iloc[i + 1]
            if up and h.c.iloc[i] < h.o.iloc[i] and not any(o['kind'] == 'OB+' for o in obs) and (h.l.iloc[i + 2:] > h.l.iloc[i]).all():
                obs.append(dict(kind='OB+', lo=float(h.l.iloc[i]), hi=float(h.h.iloc[i]), t=str(h.index[i])))
            if not up and h.c.iloc[i] > h.o.iloc[i] and not any(o['kind'] == 'OB-' for o in obs) and (h.h.iloc[i + 2:] < h.h.iloc[i]).all():
                obs.append(dict(kind='OB-', lo=float(h.l.iloc[i]), hi=float(h.h.iloc[i]), t=str(h.index[i])))
        if len(obs) == 2: break
    near = sorted(fv, key=lambda z: abs((z['lo'] + z['hi']) / 2 - last))[:3]
    return near, obs

def levels(key):
    ins = S.UNIVERSE[key]; feed = ins['feed']
    d5 = S._norm(S.get_klines(feed, '5m', 1500)); h = S._norm(S.get_klines(feed, '1h', 500))
    last = float(d5.c.iloc[-1]); day = d5.index.floor('1D'); today = day[-1]
    prev = d5[day == today - pd.Timedelta(days=1)]; cur = d5[day == today]
    wk = d5.index.tz_convert(None).to_period('W-SUN'); wcur = d5[wk == wk[-1]]; wprev = h[h.index.tz_convert(None).to_period('W-SUN') == wk[-1] - 1]
    vw, sd = S.vwap_bands(cur) if len(cur) else (pd.Series([np.nan]), pd.Series([np.nan]))
    poc, vah, val = vp(cur if len(cur) > 30 else prev)
    fv, ob = zones_1h(h, last); a1h = float(S.atr(h).iloc[-1]); e20, e50 = S.ema(h.c, 20).iloc[-1], S.ema(h.c, 50).iloc[-1]
    return dict(key=key, feed=feed, last=last, dec=ins['dec'], pt=ins['pt'], atr1h=a1h, atr1h_pts=a1h / ins['pt'],
                bias='صاعد' if e20 > e50 else 'هابط', e20=float(e20), e50=float(e50),
                PDH=float(prev.h.max()) if len(prev) else None, PDL=float(prev.l.min()) if len(prev) else None,
                TDH=float(cur.h.max()) if len(cur) else None, TDL=float(cur.l.min()) if len(cur) else None,
                WH=float(wcur.h.max()), WL=float(wcur.l.min()), PWH=float(wprev.h.max()) if len(wprev) else None, PWL=float(wprev.l.min()) if len(wprev) else None,
                VWAP=float(vw.iloc[-1]), VWAP_sd=float(sd.iloc[-1]), POC=poc, VAH=vah, VAL=val, gann9=gann9(last), fvg=fv, ob=ob)

def plan_text(L):
    d = L['dec']; f = lambda v: '—' if v is None else A.f(v, d)
    up = sorted([v for v in [L['TDH'], L['PDH'], L['WH'], L['VAH'], L['PWH']] if v and v > L['last']])[:2]
    dn = sorted([v for v in [L['TDL'], L['PDL'], L['WL'], L['VAL'], L['PWL']] if v and v < L['last']], reverse=True)[:2]
    s = []
    if up: s.append(f"بيع سكالب فقط بعد سحب {f(up[0])} وإغلاق 5m تحته + ذيل رفض (sweep_rej/KZS) — " + ('مع اتجاه الساعة' if L['bias']=='هابط' else 'ضد اتجاه الساعة: نص الحجم'))
    if dn: s.append(f"شراء سكالب فقط بعد سحب {f(dn[0])} وإغلاق 5m فوقه + ذيل رفض — " + ('مع اتجاه الساعة' if L['bias']=='صاعد' else 'ضد اتجاه الساعة: نص الحجم'))
    s.append(f"ممنوع المطاردة: لو السعر ابتعد > 2.5 ATR-1h ({L['atr1h_pts']*2.5:.0f} نقطة) عن EMA20 الساعة")
    return s

def card(L, k, tot, page, out, day):
    d = L['dec']; f = lambda v: '—' if v is None else A.f(v, d)
    row = lambda items: '<div class=pos>' + ''.join(f"<div class=pc><div class=k>{a}</div><div class=v>{f(b)}</div></div>" for a, b in items) + '</div>'
    g = L['gann9']; fv = ' · '.join(f"{z['kind']} {f(z['lo'])}–{f(z['hi'])}" for z in L['fvg']) or 'لا يوجد قريب'
    ob = ' · '.join(f"{z['kind']} {f(z['lo'])}–{f(z['hi'])}" for z in L['ob']) or 'لا يوجد'
    css = ".pc .v{font-size:30px}.pc{padding:10px 8px}.pc .k{font-size:18px}.sec{margin-top:10px;padding:10px 16px}.sec h4{font-size:23px}.sec p,li{font:500 21px/1.55 Cairo}ul{margin:4px 24px 0 0}.hap{font-size:21px;padding:10px 14px;margin-top:14px}"
    h = A.head(k, tot, f"تحضير يوم {day} · مستويات S1 · بيانات الداشبورد", css) + f"""
<div class=hrow><div class=title>{L['key']} <span class=en>{f(L['last'])}</span></div>
<div class=pills><div class=st style="color:{'#46e0ae' if L['bias']=='صاعد' else '#ff5d73'};border:2px solid currentColor">الساعة {L['bias']}</div></div></div>
<div class=hap>{A.L(f"ATR-1h = {L['atr1h_pts']:.0f} نقطة (النقطة {L['pt']}) · EMA20 {f(L['e20'])} · EMA50 {f(L['e50'])}")}</div>
<div class="sec v"><h4>سيولة اليوم والأسبوع</h4>{row([('PDH بكرة (قمة اليوم)', L['TDH']), ('PDL بكرة (قاع اليوم)', L['TDL']), ('قمة أمس', L['PDH']), ('قاع أمس', L['PDL'])])}{row([('قمة الأسبوع', L['WH']), ('قاع الأسبوع', L['WL']), ('PWH', L['PWH']), ('PWL', L['PWL'])])}</div>
<div class="sec s"><h4>القيمة: VWAP / Volume Profile</h4>{row([('VWAP', L['VWAP']), ('POC', L['POC']), ('VAH', L['VAH']), ('VAL', L['VAL'])])}</div>
<div class="sec r"><h4>Gann مربع 9 حول السعر</h4>{row([('−90°', g['-90°']), ('−45°', g['-45°']), ('+45°', g['+45°']), ('+90°', g['+90°'])])}</div>
<div class="sec m"><h4>مناطق 1H مفتوحة</h4><p>{A.L('FVG: ' + fv)}</p><p>{A.L('OB: ' + ob)}</p></div>
<div class="sec v"><h4>خطة السكالب</h4><ul>{''.join(f'<li>{A.L(x)}</li>' for x in plan_text(L))}</ul></div>
""" + A.foot()
    p = out / f"{k:02d}_{L['key']}_ar.png"; A.shoot(page, h, p); return p

def cover(rows, tot, page, out, day):
    def one(r): return f"{r['key']}: الساعة {r['bias']} · ATR-1h {r['atr1h_pts']:.0f} نقطة · PDH {A.f(r['TDH'], r['dec'])} / PDL {A.f(r['TDL'], r['dec'])}"
    li = ''.join(f"<li>{A.L(one(r))}</li>" for r in rows)
    css = "li{font:500 23px/1.75 Cairo}ul{margin:6px 24px 0 0}.sec{margin-top:16px;padding:14px 18px}.sec h4{font-size:25px}.sec p{font:500 22px/1.6 Cairo}"
    h = A.head(1, tot, f"تحضير يوم {day} · S1 سكالب", css) + f"""
<div class=hrow><div class=title>قائمة مراقبة <span class=en>{day}</span></div></div>
<div class="sec v"><h4>الأدوات</h4><ul>{li}</ul></div>
<div class="sec s"><h4>مواعيد Kill Zones (القاهرة)</h4><p>{A.L('آسيا 03:00–07:00 (نطاق آسيا = سيولة لندن) · لندن 09:00–12:00 · نيويورك AM 14:00–17:00 · نيويورك PM 20:30–23:00')}</p></div>
<div class="sec r"><h4>قواعد اليوم (من دروس 18 نوفمبر)</h4><ul>
<li>{A.L('دخول فقط بعد سحب مستوى + إغلاق 5m رجوع + ذيل رفض — مش عند لمس المستوى')}</li>
<li>{A.L('الوقف ورا ذيل السحب + 0.1 ATR، وأقل من 0.5 ATR ممنوع')}</li>
<li>{A.L('نص عند 1R ثم الوقف على الدخول · وقف زمني 60 دقيقة')}</li>
<li>{A.L('صفقة واحدة لكل مجموعة مترابطة (معادن+EURUSD / مؤشرات / كريبتو)')}</li>
<li>{A.L('ما ندخلش قبل خبر قوي بـ 15 دقيقة · حد يومي −2R')}</li></ul></div>
<div class="sec m"><h4>الحالة</h4><p>{A.L('S1 تجريبي: باك تست 18 نوفمبر ما عدّاش n≥100 و t>3 بعد التكاليف. تعليمي فقط، بدون احتمالات.')}</p></div>
""" + A.foot()
    p = out / '01_cover_ar.png'; A.shoot(page, h, p); return p

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    day = args[0] if args else (pd.Timestamp.now(tz=CAIRO) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    out = HERE / 'out' / f'prep_{day}'; out.mkdir(parents=True, exist_ok=True)
    rows = []
    for k in S.UNIVERSE:
        try: rows.append(levels(k))
        except Exception as e: print('ERR', k, e)
    json.dump(dict(day=day, built_cairo=str(pd.Timestamp.now(tz=CAIRO)), levels=rows), open(out / 'levels.json', 'w'), indent=1, ensure_ascii=False, default=str)
    for r in rows: print(f"{r['key']:6} last {r['last']:.{r['dec']}f} bias {r['bias']} PDH {r['PDH']} PDL {r['PDL']} POC {r['POC']:.{r['dec']}f} VWAP {r['VWAP']:.{r['dec']}f} FVG {len(r['fvg'])} OB {len(r['ob'])}")
    if '--cards' in sys.argv:
        from playwright.sync_api import sync_playwright
        A.FOOT = "<div class=foot>محتوى تعليمي وليس نصيحة مالية · البيانات: AI Trading Dashboard (Hyperliquid/OKX) · مستويات تحضير وليست إشارات · بدون احتمالات</div>"
        with sync_playwright() as pw:
            b = pw.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox", "--disable-gpu"])
            page = b.new_context(viewport={"width": 1080, "height": 1350}, device_scale_factor=2).new_page()
            tot = len(rows) + 1; files = [cover(rows, tot, page, out, day)]
            files += [card(r, i + 2, tot, page, out, day) for i, r in enumerate(rows)]; b.close()
        print(*files, sep='\n')
    print('out:', out)
if __name__ == '__main__': main()
