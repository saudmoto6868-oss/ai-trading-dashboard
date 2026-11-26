#!/usr/bin/env python3
"""S1 confluence / veto layer. Reuses dashboard modules when they are importable
(modules.harmonic, modules.signals, modules.elliott_lab, modules.gann_lab).
X77 is the Workspace paintLL reading: EMA 77/144 cross and a nearby level target.

Weights (experimental, not a probability):
  veto (block send): opposing Harmonic PRZ or X77 cluster within 0.8R in front of entry
  harmonic PRZ agree +0.35 / oppose -0.35
  X77 aligned        +0.30 / oppose -0.30
  OB 15m             +0.20 / oppose -0.20
  FVG 15m            +0.20 / oppose -0.20
  MSB/BOS-CHoCH      +0.20 / oppose -0.20
  Elliott            +0.15 / oppose -0.15
  Gann level         +0.10
  EMA 9/21 15m       +0.10 / oppose -0.10
  volume/displacement +0.10
  kill zone          already a hard filter; tagged +0.05

Missing modules are reported as 'غير متاح' and do not veto.
"""
from __future__ import annotations
import os, sys
import numpy as np
import pandas as pd

# Prefer the dashboard repo; fall back to a local cache of the same modules.
for _root in (
    os.environ.get('XPIX_REPO', '/workspace/ai-trading-dashboard'),
    '/workspace/src_cache/atd',
    '/workspace/charts/smc/proj_pkg',
):
    if _root and os.path.isdir(_root) and _root not in sys.path:
        sys.path.append(_root)

STRONG = {'harmonic', 'x77', 'ob', 'fvg', 'msb'}

def _ohlc(d):
    if 'close' in d.columns:
        return d
    return pd.DataFrame({
        'open': d.o, 'high': d.h, 'low': d.l, 'close': d.c,
        'volume': d.v if 'v' in d.columns else 0,
    }, index=d.index)

def _try(name, fn):
    try:
        return fn(), None
    except Exception as e:
        return None, f'{name}: {type(e).__name__}: {e}'

def _x77_read(d, side, entry, R, atr):
    """Port of Workspace X77 (EMA 77/144 cross + nearby level as target)."""
    if d is None or len(d) < 150:
        return None
    c = d.c if 'c' in d.columns else d['close']
    e77 = c.ewm(span=77, adjust=False).mean()
    e144 = c.ewm(span=144, adjust=False).mean()
    xi, xd = -1, 0
    ev, av = e77.values, e144.values
    cv = c.values
    for i in range(len(d) - 1, 40, -1):
        if ev[i - 1] <= av[i - 1] and ev[i] > av[i]:
            xi, xd = i, 1; break
        if ev[i - 1] >= av[i - 1] and ev[i] < av[i]:
            xi, xd = i, -1; break
    if xi < 40:
        return dict(ok=False, ema77=float(e77.iloc[-1]), ema144=float(e144.iloc[-1]))
    ent = float(cv[xi])
    # target: nearest of the two EMAs at the cross, in the 70–170 point-ish band of the move
    band = max(0.8 * atr, abs(float(e77.iloc[-1]) - float(e144.iloc[-1])), 1e-9)
    target = ent + xd * 1.2 * band
    levels = [float(ev[xi]), float(av[xi]), float(e77.iloc[-1]), float(e144.iloc[-1]), target]
    return dict(ok=True, dir=xd, cross_i=xi, target=target, levels=levels,
                ema77=float(e77.iloc[-1]), ema144=float(e144.iloc[-1]))

def _cluster_beyond(levels, entry, side, R, atr):
    """True if 2+ levels sit together just in front of entry (0–0.8R profit path)."""
    if not R or R <= 0:
        return False, []
    near = []
    for lv in levels:
        dist = (lv - entry) * side
        if 0 < dist <= 0.8 * R:
            near.append(lv)
    if len(near) < 2:
        return False, near
    near = sorted(near)
    # cluster = two within 0.4 ATR
    for i in range(len(near) - 1):
        if abs(near[i + 1] - near[i]) <= 0.4 * max(atr, 1e-9):
            return True, near
    return len(near) >= 3, near

def _harmonic(d, max_age=16):
    from modules.harmonic import find_harmonics
    return find_harmonics(_ohlc(d), max_age=max_age)

def _smc_side(d15, want_bull):
    """Order block, FVG, MSB on 15m using dashboard signals.py (bull fn + invert)."""
    from modules import signals as SIG
    frame = _ohlc(d15).reset_index(drop=True)
    if not want_bull:
        frame = SIG.invert(frame)
    out = {'ob': SIG.order_block_bull(frame), 'fvg': SIG.fvg_bull(frame),
           'msb': SIG.msb_ob_bull(frame), 'bos': SIG.structure_breaks(frame)}
    # zones from inverted frame need flipping back
    if not want_bull:
        def flip_sigs(xs):
            res = []
            for s in xs:
                z = s.get('zone') if isinstance(s, dict) else None
                if z is not None:
                    s = dict(s)
                    s['zone'] = (-z[1], -z[0])
                    if 'prices' in s:
                        s['prices'] = {k: -v for k, v in s['prices'].items()}
                res.append(s)
            return res
        out['ob'] = flip_sigs(out['ob'])
        out['fvg'] = flip_sigs(out['fvg'])
        out['msb'] = flip_sigs(out['msb'])
        # structure_breaks on inverted: last event is a bearish break in real prices
    return out

def _elliott(d):
    from modules.elliott_lab import elliott_signals
    return elliott_signals(_ohlc(d).reset_index(drop=True))

def _gann_levels(d):
    from modules.gann_lab import fit, grid, cycles_needed
    o = _ohlc(d)
    h, l, c = o['high'].values, o['low'].values, o['close'].values
    f = fit(h, l, c)
    if not f:
        return None
    lo, hi = float(l.min()), float(h.max())
    lv = grid(f['P'], f['s'], f['d'], cycles_needed(f['P'], f['s'], f['d'], lo, hi))
    return dict(fit=f, levels=[float(x) for x in lv])

def read_tools(d5, d15, d1h, ins, side, entry, risk, atr, trigger_bar=None):
    """-> dict(agree, against, vetoes, structure_stops, score, available, notes)."""
    agree, against, vetoes, notes = [], [], [], []
    structure_stops = []
    score = 0.0
    available = {}
    R = risk if risk and risk > 0 else None
    side = int(np.sign(side) or 1)

    # --- EMA 9/21 on 15m (always, from the candles themselves)
    if d15 is not None and len(d15) > 21:
        c = d15.c if 'c' in d15.columns else d15['close']
        e9 = c.ewm(span=9, adjust=False).mean().iloc[-1]
        e21 = c.ewm(span=21, adjust=False).mean().iloc[-1]
        available['ema1521'] = True
        if np.sign(e9 - e21) == side:
            agree.append('EMA 9/21 على 15m مع الصفقة'); score += 0.10
        else:
            against.append('EMA 9/21 على 15m ضد الصفقة'); score -= 0.10
    else:
        available['ema1521'] = False; notes.append('EMA 9/21 غير متاح')

    # --- sessions / kill zone: already a hard gate; tag only
    if trigger_bar is not None and getattr(trigger_bar, 'sess', None) in ('London KZ', 'NY AM KZ'):
        agree.append(f"جلسة {trigger_bar.sess}"); score += 0.05
        available['kz'] = True

    # --- volume / displacement proxy on the 5m trigger (not tick T&S)
    if trigger_bar is not None:
        available['volume'] = True
        vr = float(getattr(trigger_bar, 'vratio', 0) or 0)
        body = (trigger_bar.c - trigger_bar.o) * side
        a = float(getattr(trigger_bar, 'atr', atr) or atr or 0)
        if vr >= 1.5 or (a > 0 and body >= 0.9 * a):
            agree.append('حجم/إزاحة على شمعة الزناد (تقريب من الشموع، مش Time & Sales)')
            score += 0.10
        elif vr > 0 and vr < 0.7:
            against.append('حجم ضعيف على شمعة الزناد')

    # --- X77 on 15m and 1h
    x_levels = []
    x_dirs = []
    def collect_x77(df, label):
        r, err = _try(f'x77-{label}', lambda: _x77_read(df, side, entry, R or atr, atr))
        if err:
            notes.append(err); return
        if not r or not r.get('ok'):
            return
        x_levels.extend(r.get('levels') or [])
        x_dirs.append(r['dir'])
        if r['dir'] == side:
            agree.append(f"X77 {label} في اتجاه الصفقة (هدف {r['target']:.5g})")
        else:
            against.append(f"X77 {label} عكس اتجاه الصفقة")
    if d15 is not None:
        collect_x77(d15, '15m'); available['x77'] = True
    if d1h is not None:
        collect_x77(d1h, '1h'); available['x77'] = True
    if x_dirs:
        if all(x == side for x in x_dirs):
            score += 0.30
        elif all(x != side for x in x_dirs):
            score -= 0.30
        else:
            score += 0.05  # mixed
        if R:
            clustered, near = _cluster_beyond(x_levels, entry, side, R, atr)
            if clustered:
                vetoes.append('تجمّع خطوط X77 قريب قدام الدخول (فيتو)')
    else:
        available.setdefault('x77', False); notes.append('X77: مفيش تقاطع 77/144 قريب')

    # --- Harmonic PRZ (15m + 1h)
    harm_ok = False
    def collect_harm(df, label):
        nonlocal harm_ok
        r, err = _try(f'harmonic-{label}', lambda: _harmonic(df))
        if err:
            notes.append(err); return
        if not r:
            return
        harm_ok = True
        for h in r:
            d_px = float(h['pts'][4][1])
            hdir = 1 if h['dir'] == 'bull' else -1
            name = h.get('name', 'harmonic')
            forming = h.get('forming')
            tag = f"هارمونيك {name} {label} ({'قيد الاكتمال' if forming else 'مكتمل'}) عند {d_px:.5g}"
            # support/resistance at D
            if hdir == side:
                # PRZ in our direction: support under a buy / resistance above a sell
                dist_stop = (entry - d_px) * side  # positive if D is on the stop side
                dist_front = (d_px - entry) * side
                if abs(d_px - entry) <= 1.2 * (R or atr or 1):
                    agree.append(tag + ' يدعم منطقة الدخول')
                    score += 0.35
                    if dist_stop > 0:
                        structure_stops.append(d_px)
                else:
                    agree.append(tag)
                    score += 0.15
            else:
                # opposing PRZ
                dist_front = (d_px - entry) * side
                if R and 0 < dist_front <= 0.8 * R:
                    vetoes.append(tag + ' قدام الدخول (فيتو PRZ معاكس)')
                    score -= 0.35
                else:
                    against.append(tag + ' عكس الاتجاه')
                    score -= 0.20
    if d15 is not None:
        collect_harm(d15, '15m')
    if d1h is not None:
        collect_harm(d1h, '1h')
    available['harmonic'] = harm_ok
    if not harm_ok and not any('harmonic' in (n.lower()) for n in notes):
        notes.append('هارمونيك: مفيش نمط قريب أو الوحدة غير متاحة')

    # --- OB + FVG + MSB/BOS on 15m
    def add_smc():
        smc, err = _try('smc-15m', lambda: _smc_side(d15, want_bull=(side > 0)))
        if err:
            notes.append(err); available['ob'] = available['fvg'] = available['msb'] = False
            return
        available['ob'] = available['fvg'] = available['msb'] = True
        # same-direction call already used invert for sells, so hits support the trade
        if smc['ob']:
            agree.append('أوردر بلوك 15m مع الصفقة'); score += 0.20
            z = smc['ob'][0].get('zone') if isinstance(smc['ob'][0], dict) else None
            if z:
                structure_stops.append(z[0] if side > 0 else z[1])
        # opposing: run the other side
        opp, _ = _try('smc-opp', lambda: _smc_side(d15, want_bull=(side < 0)))
        if opp and opp['ob']:
            z = opp['ob'][0].get('zone') if isinstance(opp['ob'][0], dict) else None
            if z and R:
                mid = 0.5 * (z[0] + z[1])
                dist = (mid - entry) * side
                if 0 < dist <= 0.8 * R:
                    against.append('أوردر بلوك معاكس قريب قدام الدخول')
                    score -= 0.20
                else:
                    # if opposing OB is on the stop side, use it as a structure stop
                    if dist < 0:
                        structure_stops.append(z[0] if side > 0 else z[1])
        if smc['fvg']:
            agree.append('FVG 15m مع الصفقة'); score += 0.20
            z = smc['fvg'][0].get('zone') if isinstance(smc['fvg'][0], dict) else None
            if z:
                structure_stops.append(z[0] if side > 0 else z[1])
        elif opp and opp['fvg'] and R:
            z = opp['fvg'][0].get('zone')
            if z and 0 < (0.5 * (z[0] + z[1]) - entry) * side <= 0.8 * R:
                against.append('FVG معاكس قريب قدام الدخول'); score -= 0.20
        # BOS / MSB: last structure break on 15m
        bos = smc.get('bos') or []
        if bos:
            # last break in the (possibly inverted) frame: if we asked want_bull, it's with us
            agree.append('MSB/BOS على 15m مع الصفقة'); score += 0.20
        if smc['msb']:
            agree.append('MSB + إعادة اختبار أوردر بلوك 15m'); score += 0.05
    if d15 is not None and len(d15) >= 60:
        add_smc()
    else:
        available['ob'] = available['fvg'] = available['msb'] = False
        notes.append('SMC 15m: شموع مش كفاية')

    # --- Elliott on 1h
    if d1h is not None and len(d1h) >= 80:
        ew, err = _try('elliott', lambda: _elliott(d1h))
        if err:
            notes.append(err); available['elliott'] = False
        else:
            available['elliott'] = True
            if ew:
                # direction field is 'bullish' / 'bearish'
                dirs = [1 if (s.get('direction') or '').startswith('bull') else -1 for s in ew]
                if any(x == side for x in dirs) and not any(x != side for x in dirs):
                    agree.append('Elliott: نهاية موجة 4 / اندفاع مع الصفقة'); score += 0.15
                elif any(x != side for x in dirs) and not any(x == side for x in dirs):
                    against.append('Elliott عكس اتجاه الصفقة'); score -= 0.15
                else:
                    notes.append('Elliott: قراءات مختلطة')
            else:
                notes.append('Elliott: مفيش إشارة واضحة على الساعة')
    else:
        available['elliott'] = False

    # --- Gann on 1h
    if d1h is not None and len(d1h) >= 80:
        g, err = _try('gann', lambda: _gann_levels(d1h))
        if err:
            notes.append(err); available['gann'] = False
        elif g and g.get('levels'):
            available['gann'] = True
            near = [lv for lv in g['levels'] if abs(lv - entry) <= 0.6 * (R or atr or 1)]
            if near:
                agree.append(f"مستوى جان قريب من الدخول ({near[0]:.5g})")
                score += 0.10
                # if a gann level sits on the stop side, use it
                for lv in g['levels']:
                    if (entry - lv) * side > 0 and (entry - lv) * side <= 2 * (R or atr or 1):
                        structure_stops.append(lv)
            else:
                notes.append('جان: مفيش مستوى ملاصق للدخول')
        else:
            available['gann'] = False
            notes.append('جان: ما اتضبطش على الساعة')
    else:
        available['gann'] = False

    return dict(agree=agree, against=against, vetoes=vetoes, notes=notes,
                structure_stops=structure_stops, score=round(score, 3),
                available=available, strong_agree=sum(1 for a in agree if any(k in a for k in
                    ('هارمونيك', 'X77', 'أوردر بلوك', 'FVG', 'MSB', 'BOS'))))
