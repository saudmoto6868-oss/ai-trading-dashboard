"""Render official Workspace CandleChart panels (one PNG per timeframe) with the S1 position box, current candle centred."""
import sys, socketserver, threading, http.server
from pathlib import Path
sys.path.insert(0, "/tmp/pwvenv/lib/python3.13/site-packages")
from playwright.sync_api import sync_playwright
from PIL import Image
WS = Path(__file__).parent / '_ws'
IND = {'1m': ["ma", "sbox", "volume", "vwap", "kz", "psar", "kzs"], '5m': ["ma", "sbox", "volume", "vwap", "kz", "psar", "kzs", "zn"],
       '15m': ["ma", "sbox", "volume", "vwap", "kz", "msb"], '1H': ["ma", "sbox", "volume", "vwap", "gann", "msb"]}
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def __init__(self, *a, **k): super().__init__(*a, directory=str(WS), **k)

def render(feed, tfs, plan, side, outdir, t0_ms=None, W=1000, H=900):
    sock = socketserver.TCPServer(("127.0.0.1", 0), Q); port = sock.server_address[1]
    threading.Thread(target=sock.serve_forever, daemon=True).start(); out = {}
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"])
            page = b.new_context(viewport={"width": W, "height": H}, device_scale_factor=2).new_page()
            for tf in tfs:
                job = {"url": f"http://127.0.0.1:{port}/workspace.html?blank=1", "sym": feed, "dir": "bullish" if side > 0 else "bearish",
                       "tfs": [tf], "header": 0, "chrome": "", "plan": plan, "indicators": IND.get(tf, IND['5m'])}
                if t0_ms: job['t0'] = t0_ms
                page.goto(job['url'], wait_until='domcontentloaded', timeout=60000)
                page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch(e){} }")
                page.reload(wait_until='domcontentloaded', timeout=60000)
                page.wait_for_function("() => !!(window.runCard && window.Ws && window.XCMD)", timeout=20000)
                info = page.evaluate("job => window.runCard(job)", job)
                if not (info and info.get('ok')): out[tf] = None; print('chart fail', tf, info); continue
                page.evaluate("""(keep) => { Ws.panels.filter(p=>p.chart).forEach(p=>{ const c=p.chart;
                    ['ew','harm'].concat(keep ? [] : ['gann']).forEach(id=>{ try{ const it=p.indItems&&p.indItems.find(x=>x.id===id); if(it&&it.set) it.set(false);}catch(e){} });
                    c.ewOn=false; c.harmOn=false; if(!keep) c.gannOn=false; try{ c.centerNow && c.centerNow(); c.draw(); }catch(e){} }); }""", tf == '1H')
                page.wait_for_timeout(500)
                p = Path(outdir) / f"_chart_{tf}.png"; page.locator('#ws').screenshot(path=str(p))
                im = Image.open(p); im.crop((76, 108, im.size[0], im.size[1])).save(p); out[tf] = str(p)
            b.close()
    finally:
        sock.shutdown()
    return out
