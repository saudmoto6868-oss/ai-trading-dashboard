"""Object tree drag-to-reorder (task #2), headless Chromium + real mouse drag, OKX mocked (no network, no keys).
Plain script like the other tests; SKIPs when Playwright or a Chromium binary is missing.
Mock-tested only: not tried on real OKX, touch, or by the owner."""
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from modules.workspace import build_workspace_html

try:
    from playwright.sync_api import sync_playwright
except Exception:
    print("SKIP: playwright not installed")
    sys.exit(0)

exe = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
now = int(time.time() // 60 * 60) * 1000
rows = [[str(now - i * 60000), str(100 + i % 7), str(105 + i % 5), "95", str(100 + (i * 3) % 9), "10", "10", "10", "1"] for i in range(300)]


def route(r):
    u = r.request.url
    if "okx.com" not in u:
        return r.abort()
    r.fulfill(json={"code": "0", "data": rows if ("candles" in u) else []})


fails = []


def check(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name + (" " + str(info) if info else ""))
    if not ok:
        fails.append(name)


with sync_playwright() as p:
    try:
        b = p.chromium.launch(executable_path=exe, args=["--no-sandbox"]) if exe else p.chromium.launch()
    except Exception as e:
        print("SKIP: no browser:", str(e)[:80])
        sys.exit(0)
    pg = b.new_page(viewport={"width": 1400, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/*", route)
    pg.set_content(build_workspace_html(["BTC-USDT-SWAP"]))
    pg.wait_for_timeout(2000)
    pg.evaluate("window.__ws.add('chart')")
    pg.wait_for_timeout(2000)
    pg.evaluate("""() => { const c = window.__ws.panels.find(p => p.type === 'chart').chart; window.__c = c;
      const t = c.data && c.data.length ? c.data[c.data.length - 20].t : Date.now();
      c.draws = [1, 2, 3].map(i => ({id: 'd' + i, type: 'hline', pts: [{t, p: 100 + i}]})); c.saveDraws(); c.draw(); }""")
    order = lambda: pg.evaluate("window.__c.draws.map(d => d.id).join()")
    check("start order", order() == "d1,d2,d3", order())
    pg.locator("button[title='object tree'], button[title='شجرة الكائنات']").first.click()
    pg.wait_for_timeout(300)
    rowsel = pg.locator(".fibpop > div[draggable=true]")
    check("3 rows listed, newest first", rowsel.count() == 3 and "hline" in rowsel.nth(0).inner_text())
    # list is newest first (d3, d2, d1). Dropping d3 onto d1 puts d3 right after d1 in draw order: d1,d3,d2
    pg.evaluate("window.__saves = 0; const o = window.__c.saveDraws.bind(window.__c); window.__c.saveDraws = () => { window.__saves++; o(); }")
    rowsel.nth(0).drag_to(rowsel.nth(2))
    pg.wait_for_timeout(300)
    check("drag changed the draw order", order() == "d1,d3,d2", order())
    check("saveDraws called (the page has no localStorage under set_content, so persistence itself is not tested)", pg.evaluate("window.__saves") >= 1)
    check("list reopened with 3 rows", pg.locator(".fibpop > div[draggable=true]").count() == 3)
    check("no page errors", not errs, errs[:2])
    b.close()

print("FAILED: " + ", ".join(fails) if fails else "ALL OK (mock-tested only)")
sys.exit(1 if fails else 0)
