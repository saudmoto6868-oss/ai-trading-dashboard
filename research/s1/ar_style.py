"""Arabic 4:5 card style (XPiX, same look as lessons_ar). Shared by scalp_now.py and prep_day.py."""
import re, sys
sys.path.insert(0, "/tmp/pwvenv/lib/python3.13/site-packages")
from PIL import Image
N = 9
def LB(s): return re.sub(r'\[\[(.+?)\]\]', r'<bdi class=n>\1</bdi>', s)
RUN = re.compile(r"[~+\-−]?[A-Za-z0-9&][A-Za-z0-9&.,:/%+\-−→–≥>=_~ ]*[A-Za-z0-9%&]|[A-Za-z0-9]")
def L(s):
    s = s.replace('[[', '').replace(']]', '')
    s = re.sub(r'([\u0600-\u06FF])([A-Za-z0-9])', r'\1 \2', s)
    return RUN.sub(lambda m: f'<bdi class=n>{m.group(0)}</bdi>', s)
def f(v, d): return f"{v:,.{d}f}"
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1350px;overflow:hidden;font-family:Cairo,'Noto Kufi Arabic',sans-serif;color:#e9e6e4;direction:rtl;
 background:radial-gradient(120% 80% at 80% 0%,#24262b 0%,#141518 45%,#0b0b0d 100%)}
.bg-dots{position:absolute;left:0;top:0;width:1080px;height:700px;background-image:radial-gradient(rgba(255,255,255,.10) 1.4px,transparent 1.6px);background-size:26px 26px;-webkit-mask-image:linear-gradient(#000 0%,rgba(0,0,0,.6) 55%,transparent 100%)}
.streak{position:absolute;right:-180px;top:-260px;width:220px;height:2000px;transform:rotate(-28deg);background:linear-gradient(90deg,transparent,rgba(255,196,170,.09) 40%,rgba(255,214,190,.16) 50%,rgba(255,196,170,.07) 60%,transparent);filter:blur(6px)}
.wrap{position:absolute;inset:0;padding:30px 44px 0}
.top{display:flex;align-items:center;justify-content:space-between;direction:ltr}
.brand{display:flex;align-items:center;gap:14px}
.mark{width:48px;height:48px;border-radius:10px;background:linear-gradient(145deg,#f3c9a8,#b9785a 55%,#6e3f2c);display:flex;align-items:center;justify-content:center;font:700 24px Oswald;color:#1a0f0a;box-shadow:0 0 18px rgba(240,170,130,.35)}
.bname{font:600 27px Oswald;letter-spacing:7px;color:#efe2da}
.badge{font:700 21px Inter;color:#111;background:#efe9e6;border-radius:9px;padding:4px 13px}
.prog{margin-top:14px;height:4px;border-radius:3px;background:rgba(255,255,255,.08);overflow:hidden;direction:ltr}
.prog i{display:block;height:100%;background:linear-gradient(90deg,#f5c6a8,#d98f6c);box-shadow:0 0 10px #f0a888}
.caps{margin-top:12px;font:700 20px Cairo;color:#e8a988}
.hrow{display:flex;align-items:center;justify-content:space-between;gap:14px}
.title{font:800 52px/1.25 Cairo;background:linear-gradient(100deg,#fbe1cf 0%,#e8a988 35%,#c77b5a 60%,#f6cdb2 100%);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 0 12px rgba(240,160,120,.28))}
.title .en{font-family:Oswald;font-weight:700;margin-inline-start:12px;font-size:40px}
.pills{display:flex;gap:10px}
.st{font:800 22px Cairo;padding:4px 14px;border-radius:11px;white-space:nowrap}
.n{direction:ltr;unicode-bidi:isolate;font-family:Inter,Roboto,sans-serif;font-weight:700}
.chart{margin-top:8px;border-radius:14px;border:1px solid rgba(255,255,255,.10);background:#0d0f12;overflow:hidden}
.chart img{display:block;width:992px;height:auto}
.pos{display:flex;gap:8px;margin-top:8px;direction:rtl}
.pc{flex:1;border-radius:10px;border:1px solid rgba(255,255,255,.09);background:rgba(20,22,26,.9);padding:4px 10px;text-align:center}
.pc .k{font:700 15px Cairo;color:#9a938f}.pc .v{font:700 22px Inter;color:#fff;direction:ltr}
.hap{margin-top:8px;font:600 18px/1.45 Cairo;color:#d8d2ce;background:rgba(255,255,255,.04);border-radius:10px;padding:6px 12px;border-right:4px solid #a7a19d}
.sec{margin-top:8px;border-radius:12px;border:1px solid rgba(255,255,255,.09);background:rgba(20,22,26,.92);padding:6px 14px 8px}
.sec h4{font:800 19px Cairo;margin-bottom:1px}
.sec p{font:500 18.5px/1.5 Cairo;color:#e4dfdb}
.sec.m h4{color:#ff7d8f}.sec.s h4{color:#f0c27b}.sec.v h4{color:#46e0ae}.sec.r h4{color:#8fc8ff}
.sec.v{border-color:rgba(47,214,160,.35);background:rgba(20,60,48,.30)}
.lv{margin-top:7px;font:500 16px/1.45 Cairo;color:#b9b2ae;border:1px dashed rgba(255,255,255,.18);border-radius:10px;padding:5px 12px}
.lv b{color:#f0c27b}
.foot{position:absolute;left:44px;right:44px;bottom:14px;font:500 14px Cairo;color:#8d8682;text-align:center}
"""
FOOT = "<div class=foot>محتوى تعليمي وليس نصيحة مالية · البيانات: AI Trading Dashboard (Hyperliquid/OKX) · بدون ادعاء احتمالات · ما بعد الحدث = توضيح على [[7]] عينات وليس دليلاً</div>"
COL = {'grey': ('#a7a19d', 'rgba(255,255,255,.07)'), 'red': ('#ff5d73', 'rgba(255,93,115,.16)'), 'green': ('#2fd6a0', 'rgba(47,214,160,.16)'), 'gold': ('#f0c27b', 'rgba(240,194,123,.14)')}
def head(n, total, caps, extra_css=''):
    return f"""<!doctype html><html lang=ar dir=rtl><head><meta charset=utf-8><style>{CSS}{extra_css}</style></head><body><div class=bg-dots></div><div class=streak></div><div class=wrap>
<div class=top><div class=brand><div class=mark>X</div><div class=bname>XPiX</div></div><div class=badge>{n}/{total}</div></div>
<div class=prog><i style="width:{n/total*100:.1f}%"></i></div><div class=caps>{LB(caps)}</div>"""
def foot(): return "</div>" + LB(FOOT) + "</body></html>"
def shoot(page, h, path):
    hp = path.with_suffix('.html'); hp.write_text(h)
    page.goto('file://' + str(hp), wait_until='load'); page.evaluate("document.fonts.ready"); page.wait_for_timeout(350)
    ov = page.evaluate("() => { const w=document.querySelector('.wrap'); return Math.max(...[...w.querySelectorAll('*')].map(e=>e.getBoundingClientRect().bottom)); }")
    page.screenshot(path=str(path), type='png'); hp.unlink(); return round(ov)
