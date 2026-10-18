# Main header logo (owner design 2026-10-18): slanted panel with XPiX + barcode; widths / tops seeded with 6868. Run next to xpix_logo_gen.py (as gen.py).
import random, re
src = open("gen.py").read(); exec(src.split("word = letters(")[0].replace("open('mark.svg'", "(lambda *a: None)('mark.svg'").replace(".write(svg(mark(), '20 0 160 240'))", ""))   # bars(), mark(), letters()
H, PW, PB = 172, 139, 57          # panel: height, top width, bottom width (slanted right edge)
FG = '#e3e4e8'
out = [f'<path fill="{FG}" d="M0 0 H{PW} L{PB} {H} H0 Z"/>']
out.append(letters(20, 50, 25, '#0b0b0c', '#0b0b0c').replace('scale(0.25)', 'scale(0.235)'))
# barcode: widths from the digits 6 8 6 8 and Fibonacci (deterministic), tops at 0 or a step down
rnd = random.Random(6868); x = 149; fib = [1, 1, 2, 3, 5, 8]; seq = [6, 8, 6, 8]
while x < 542:
    w = [1.6, 2.2, 3.2, 5.0, 7.5][rnd.randrange(5)]
    top = rnd.choice([0, 0, 0, 22, 45, 60, 32, 14])
    out.append(f'<rect x="{x:.1f}" y="{top}" width="{w}" height="{H-top}" fill="{FG}"/>')
    x += w + [2.0, 3.0, 4.5, 6.8][rnd.randrange(4)]
open('barcode.svg', 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x:.0f} {H}">' + ''.join(out) + '</svg>')
