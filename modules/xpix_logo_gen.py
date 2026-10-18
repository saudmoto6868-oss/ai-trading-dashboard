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
# XPiX letters drawn as shapes (heavy geometric, angled cuts - same style as the barcode logo); cap height 100, stroke 22
def letters(x0, top, cap, white=W, gold=G):
    k = cap/100
    X = lambda x: f'<path fill="{white}" d="M{x} 0 H{x+26} L{x+92} 100 H{x+66} Z M{x+66} 0 H{x+92} L{x+26} 100 H{x} Z"/>'
    P = lambda x: f'<path fill="{white}" fill-rule="evenodd" d="M{x} 0 H{x+52} A30 30 0 0 1 {x+52} 60 H{x+22} V100 H{x} Z M{x+22} 20 H{x+50} A10 10 0 0 1 {x+50} 40 H{x+22} Z"/>'
    I = lambda x: f'<path fill="{gold}" d="M{x} 32 H{x+22} V100 H{x} Z M{x} 0 H{x+22} V20 H{x} Z"/>'
    body = X(0) + P(104) + I(198) + X(232)
    return f'<g transform="translate({x0},{top}) scale({k})">{body}</g>'
word = letters(198, 92, 58)
open('lockup.svg','w').write(svg(mark()+[word], '22 2 400 236'))
open('lockup_mid.svg','w').write(svg(mark("mid")+[word], '22 2 400 236'))
# 3) app icon (chunky, rounded square)
icon = [f'<rect x="0" y="0" width="200" height="200" rx="46" fill="#0a0a0a"/>', '<g transform="translate(0,-20) translate(100,120) scale(.78) translate(-100,-120)">'] + mark(False) + ['</g>']
open('icon.svg','w').write(svg(icon, '0 0 200 200'))
# 4) gold small icon
icon2 = [f'<rect x="0" y="0" width="200" height="200" rx="46" fill="{G}"/>', '<g transform="translate(0,-20) translate(100,120) scale(.78) translate(-100,-120)">'] + mark(False, '#0a0a0a', '#f2f2f2', '#0a0a0a') + ['</g>']
open('icon_gold.svg','w').write(svg(icon2, '0 0 200 200'))
