# Generates the XPiX logo files (owner design 2026-10-18): python3 modules/xpix_logo_gen.py writes mark / lockup / icon SVGs in the current folder.
import math
W='#f2f2f2'; G='#d4a537'
def bars(cx, base, fine=True, col_l=W, col_r=W):
    out=[]
    if fine == "mid": n, sp, bw, H, D, tl, tr = 12, 5.2, 3.0, 78, 54, 17, 15
    elif fine: n, sp, bw, H, D, tl, tr = 26, 2.6, 1.3, 78, 54, 17, 15
    else:   # icon: Fibonacci steps (1 2 3 5 8 13 ... -> the golden ratio), tallest next to the centre
        FL, FR = [68, 42, 26, 16, 10, 6], [52, 32, 20, 12, 8]
        for k, h in enumerate(FL, 1): out.append(f'<rect x="{cx-9-k*11:.2f}" y="{base-h}" width="8.5" height="{h}" fill="{col_l}"/>')
        for k, h in enumerate(FR, 1): out.append(f'<rect x="{cx+0.5+k*11:.2f}" y="{base}" width="8.5" height="{h}" fill="{col_r}"/>')
        return out
    for k in range(1, n+1):
        d = k*sp
        h = max(1.6, H*math.exp(-(d-sp)/tl)); x = cx - 4 - d
        out.append(f'<rect x="{x:.2f}" y="{base-h:.2f}" width="{bw}" height="{h:.2f}" fill="{col_l}"/>')
        dd = max(1.6, D*math.exp(-(d-sp)/tr)); x2 = cx + 6 + d - sp + (0 if fine else 1)
        out.append(f'<rect x="{x2:.2f}" y="{base:.2f}" width="{bw}" height="{dd:.2f}" fill="{col_r}"/>')
    return out
def mark(fine=True, white=W, gold=G, bars_col=W):
    cx, base = 100, 120
    s = bars(cx, base, fine, bars_col, bars_col)
    if fine == "mid":
        s.append(f'<rect x="{cx-3.4}" y="{base-80}" width="3.4" height="195" fill="{white}"/>')
        s.append(f'<rect x="{cx+0.8}" y="{base-110}" width="3.0" height="190" fill="{gold}"/>')
    elif fine:
        s.append(f'<rect x="{cx-2.6}" y="{base-80}" width="2.4" height="195" fill="{white}"/>')
        s.append(f'<rect x="{cx+0.8}" y="{base-110}" width="2.0" height="190" fill="{gold}"/>')
    else:
        s.append(f'<rect x="{cx-8}" y="{base-82}" width="8" height="160" fill="{white}"/>')
        s.append(f'<rect x="{cx+1.5}" y="{base-105}" width="8" height="160" fill="{gold}"/>')
    return s
def svg(body, vb):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'+''.join(body)+'</svg>'
# 1) mark alone (fine)
open('mark.svg','w').write(svg(mark(), '20 0 160 240'))
# 2) lockup: mark + XPiX (header)
word = ('<g font-family="Inter,\'Helvetica Neue\',Arial,sans-serif" font-weight="400" font-size="92" letter-spacing="2">'
        f'<text x="196" y="153" fill="{W}">XP<tspan fill="{G}">i</tspan>X</text></g>')
open('lockup.svg','w').write(svg(mark()+[word], '22 2 420 236'))
open('lockup_mid.svg','w').write(svg(mark("mid")+[word], '22 2 420 236'))
# 3) app icon (chunky, rounded square)
icon = [f'<rect x="0" y="0" width="200" height="200" rx="46" fill="#0a0a0a"/>', '<g transform="translate(0,-20) translate(100,120) scale(.78) translate(-100,-120)">'] + mark(False) + ['</g>']
open('icon.svg','w').write(svg(icon, '0 0 200 200'))
# 4) gold small icon
icon2 = [f'<rect x="0" y="0" width="200" height="200" rx="46" fill="{G}"/>', '<g transform="translate(0,-20) translate(100,120) scale(.78) translate(-100,-120)">'] + mark(False, '#0a0a0a', '#f2f2f2', '#0a0a0a') + ['</g>']
open('icon_gold.svg','w').write(svg(icon2, '0 0 200 200'))
