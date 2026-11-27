"""M1 phase 2 / P5: the lite Workspace (WS_LITE) must look and behave like the classic st.iframe page. Both are booted with the same
page data (default layout, English and Arabic, full Workspace and chart-only) in fresh browser profiles, and compared: widgets built,
body classes, top bar text, element count, no error box. Real headless Chromium, local server, network blocked (MOCK-TESTED ONLY)."""
import functools
import http.server
import json
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
site = tempfile.mkdtemp()
shutil.copy(os.path.join(src, "index.html"), site)
shutil.copy(os.path.join(src, js_name), site)

CASES = [("en", ""), ("ar", ""), ("en", "chart")]
for i, (lang, solo) in enumerate(CASES):
    open(os.path.join(site, "classic%d.html" % i), "w", encoding="utf-8").write(W.build_workspace_html(["BTC-USDT", "ETH-USDT"], None, lang, solo=solo))
PARENT = """<!doctype html><html><body style="margin:0"><iframe id="f" src="%s" style="width:1400px;height:860px;border:0"></iframe><script>
const f = document.getElementById("f");
addEventListener("message", ev => { const d = ev.data || {}; if (d.type === "streamlit:componentReady") f.contentWindow.postMessage({type:"streamlit:render", args:{cfg:window.__cfg, stamp:"a", height:860}}, "*"); });
</script></body></html>"""
for i in range(len(CASES)):
    open(os.path.join(site, "p_classic%d.html" % i), "w").write(PARENT % ("classic%d.html" % i))
open(os.path.join(site, "p_lite.html"), "w").write(PARENT % "index.html")


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=site))
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = "http://127.0.0.1:%d/" % srv.server_address[1]

SNAP = """() => ({ok: typeof Ws === 'object', err: !!document.getElementById('wsErrBox'), types: Ws.panels.map(p => p.type).join(','),
  body: [...document.body.classList].sort().join(' '), lang: document.documentElement.lang,
  bar: ((document.getElementById('bar') || {}).innerText || '').replace(/\\d/g, '#').replace(/\\s+/g, ' ').slice(0, 400),
  els: [...document.querySelectorAll('body *')].filter(e => e.tagName !== 'SCRIPT').length})"""


def boot(pw_b, kind, i):
    ctx = pw_b.new_context(viewport={"width": 1500, "height": 950})   # fresh storage: a saved layout must not leak between runs
    p = ctx.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)[:160]))
    p.route("**/*", lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
    lang, solo = CASES[i]
    p.add_init_script("window.__cfg = %s;" % json.dumps(W.workspace_cfg(["BTC-USDT", "ETH-USDT"], None, lang, solo=solo)))
    p.goto(base + ("p_classic%d.html" % i if kind == "classic" else "p_lite.html"))
    snap = None
    for _ in range(120):
        fh = p.locator("#f").element_handle().content_frame()
        try:
            if fh and fh.evaluate("typeof Ws === 'object' && Ws.panels.length > 0"):
                p.wait_for_timeout(2500)   # let the widgets finish building
                snap = fh.evaluate(SNAP)
                break
        except Exception:
            pass
        p.wait_for_timeout(100)
    ctx.close()
    assert snap, (kind, CASES[i], "did not boot", errs)
    assert not errs, (kind, CASES[i], errs)
    return snap


with sync_playwright() as pw:
    b = pw.chromium.launch()
    for i, case in enumerate(CASES):
        a, l_ = boot(b, "classic", i), boot(b, "lite", i)
        assert a["ok"] and l_["ok"] and not a["err"] and not l_["err"], (case, a, l_)
        for k in ("types", "body", "lang", "bar"):
            assert a[k] == l_[k], (case, k, a[k], l_[k])
        assert abs(a["els"] - l_["els"]) <= max(5, a["els"] // 100), (case, "element count", a["els"], l_["els"])   # live clocks / tooltips may differ a little
        print("same", case, "widgets", a["types"].count(",") + 1, "elements", a["els"], l_["els"])
    b.close()
srv.shutdown()
print("ok ws lite parity:", len(CASES), "cases")
