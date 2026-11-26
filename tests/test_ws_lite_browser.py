"""M1 phase 2 / P4: the lite Workspace (WS_LITE) boots from a component page, keeps its 1.2 MB script in the browser's Cache API
(fetched once, not again on a page reload), and reloads itself when Streamlit sends new page data (a new stamp).
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
    p.evaluate("() => { window.__stamp = 'b'; document.getElementById('f').contentWindow.__old = 1; render(); }")
    p.wait_for_function("() => { try { return !document.getElementById('f').contentWindow.__old; } catch(e){ return false; } }", timeout=10000)
    booted()
    assert n_js() == 1, hits
    assert not errs, errs
    b.close()
srv.shutdown()
print("ok ws lite: boots, script fetched once over 3 loads, new stamp reloads; index %d bytes, %s %d bytes" % (len(index), js_name, len(js)))
