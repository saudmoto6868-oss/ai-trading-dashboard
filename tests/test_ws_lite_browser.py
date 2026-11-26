"""M1 phase 2 / P4: the lite Workspace (WS_LITE) boots from a component page, keeps its 1.2 MB script in the browser's Cache API
(fetched once, not again on a page reload), applies new page data in place (Ws.applyCfg, M2 / P6) and reloads itself only when a
layout key (here: the language) changes.
Real headless Chromium against a local server; a fake parent plays Streamlit's component messages (MOCK-TESTED ONLY)."""
import functools
import http.server
import os
import shutil
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import workspace as W  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP: playwright not installed (CI installs it from requirements-dev.txt)")
    sys.exit(0)

W._lite_component()
src = os.path.join(tempfile.gettempdir(), "xpix_ws_lite")
index = open(os.path.join(src, "index.html"), encoding="utf-8").read()
js_name = index.split('const JS = "', 1)[1].split('"', 1)[0]
js = open(os.path.join(src, js_name), encoding="utf-8").read()
tpl = W._template_text()
assert "__CONFIG__" not in js and "window.__WS_CFG__" in js and "__CONFIG__" not in index
assert js.replace("window.__WS_CFG__", "__CONFIG__", 1) in tpl and len(index) < 80_000, "index = style + boot + loader only"

site = tempfile.mkdtemp()
shutil.copy(os.path.join(src, "index.html"), site)
shutil.copy(os.path.join(src, js_name), site)
cfg = W.workspace_cfg(["BTC-USDT"], lang="en")
open(os.path.join(site, "parent.html"), "w").write("""<!doctype html><html><body style="margin:0">
<iframe id="f" src="index.html?blank=1" style="width:1300px;height:300px;border:0"></iframe><script>
window.__stamp = "a"; window.__h = 0; const f = document.getElementById("f");
window.render = () => f.contentWindow.postMessage({type:"streamlit:render", args:{cfg:window.__cfg, stamp:window.__stamp, height:777}}, "*");
addEventListener("message", ev => { const d = ev.data || {}; if (d.type === "streamlit:componentReady") render(); if (d.type === "streamlit:setFrameHeight") window.__h = d.height; });
</script></body></html>""")

hits = []


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache" if self.path.split("?")[0].endswith(".html") else "public")   # what Streamlit sends
        super().end_headers()

    def log_message(self, fmt, *a):
        hits.append(self.path)


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=site))
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = "http://127.0.0.1:%d/" % srv.server_address[1]
n_js = lambda: sum(1 for h in hits if js_name in h)  # noqa: E731

with sync_playwright() as pw:
    b = pw.chromium.launch()
    p = b.new_page(viewport={"width": 1400, "height": 900})
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)[:160]))
    p.route("**/*", lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
    p.add_init_script("window.__cfg = %s;" % __import__("json").dumps(cfg))
    p.add_init_script("""if (window !== window.top){ window.__live = new Set(); const si = setInterval, ci = clearInterval;
      window.setInterval = (f, ms, ...r) => { const id = si(f, ms, ...r); window.__live.add(id); return id; };
      window.clearInterval = id => { window.__live.delete(id); return ci(id); }; }""")

    def fr():
        return next(f for f in p.frames if "index.html" in f.url)

    def booted():   # Ws / CFG are top-level const: visible inside the frame, not as window properties
        for _ in range(150):
            try:
                if fr().evaluate("typeof Ws === 'object' && !!CFG"):
                    break
            except Exception:
                pass
            p.wait_for_timeout(100)
        assert fr().evaluate("typeof Ws === 'object' && !document.getElementById('wsErrBox')"), "lite page did not boot"

    p.goto(base + "parent.html")
    booted()
    assert n_js() == 1, hits
    assert p.evaluate("window.__h") == 777
    assert fr().evaluate("CFG.symbols[0]") == "BTC-USDT"
    p.reload()
    booted()
    assert n_js() == 1, ("second page load must run the script from the Cache API", hits)
    # same page data, new stamp: nothing to do, no reload
    p.evaluate("() => { document.getElementById('f').contentWindow.__old = 1; window.__stamp = 'b'; render(); }")
    p.wait_for_timeout(800)
    assert fr().evaluate("window.__old === 1"), "same data must not reload the frame"
    # only data changed (news): applied in place (Ws.applyCfg), widgets rebuilt, no reload, no timer pile-up
    fr().evaluate("() => { Ws.build(Ws.defaults()); Ws.save(); }")   # ?blank=1 starts empty: give it the standard widgets
    p.wait_for_timeout(1500)
    live0 = fr().evaluate("window.__live.size")
    n0 = fr().evaluate("Ws.panels.length")
    for i, stamp in enumerate("cde"):
        p.evaluate("([s, h]) => { window.__cfg = Object.assign({}, window.__cfg, {news:[{headline:h, source:'x', url:'', summary:'', datetime:''}]}); window.__stamp = s; render(); }", [stamp, "NEWS-%d" % i])
        p.wait_for_timeout(800)
    assert fr().evaluate("window.__old === 1"), "a data-only change must not reload the frame"
    assert fr().evaluate("CFG.news[0].headline") == "NEWS-2"
    assert fr().evaluate("Ws.panels.length") == n0 and n0 > 0
    live1 = fr().evaluate("window.__live.size")
    assert live1 <= live0 + 3, ("rebuilding the widgets must not pile up timers", live0, live1)
    # a layout key changed (language): the frame reloads and boots again
    p.evaluate("() => { window.__cfg = Object.assign({}, window.__cfg, {lang:'ar'}); window.__stamp = 'f'; render(); }")
    for _ in range(100):
        try:
            if not fr().evaluate("window.__old === 1"):
                break
        except Exception:
            pass
        p.wait_for_timeout(100)
    booted()
    assert fr().evaluate("CFG.lang") == "ar" and n_js() == 1, hits
    assert not errs, errs
    b.close()
srv.shutdown()
print("ok ws lite: boots, script fetched once, data applied in place (timers %d -> %d), language change reloads;" % (live0, live1) + " index %d bytes, %s %d bytes" % (len(index), js_name, len(js)))
