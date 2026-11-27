"""M1 1.3: repaint-only timers skip while the browser tab is hidden and catch up once when it is shown again; price alarms keep ticking hidden.
Real headless Chromium, network blocked (MOCK-TESTED ONLY: document.hidden is faked). Run: python3 tests/test_vis_timers_browser.py"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules.workspace import build_workspace_html  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP: playwright not installed (CI installs it from requirements-dev.txt)")
    sys.exit(0)

src = open(os.path.join(ROOT, "modules", "ws", "10_feeds_charts_math.js"), encoding="utf-8").read()
assert "visOnly = fn =>" in src and "VIS_MISSED" in src
html = build_workspace_html(["BTC-USDT"], lang="en")
path = os.path.join(tempfile.mkdtemp(), "ws.html")
open(path, "w", encoding="utf-8").write(html)

with sync_playwright() as pw:
    b = pw.chromium.launch()
    p = b.new_page(viewport={"width": 1400, "height": 900})
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)[:160]))
    p.route("**/*", lambda r: r.continue_() if r.request.url.startswith("file:") else r.abort())
    p.add_init_script("""window.__hid = false; Object.defineProperty(Document.prototype, 'hidden', {get(){ return window.__hid; }, configurable: true});""")
    p.goto("file://" + path + "?blank=1")
    p.wait_for_timeout(1500)
    p.evaluate("""() => { window.__n = 0; const o = Ws.drawStrip; Ws.drawStrip = function(){ window.__n++; return o.apply(this, arguments); };
                          window.__a = 0; const t = PAlarm.tick; PAlarm.tick = function(){ window.__a++; return t.apply(this, arguments); }; PAlarm.start && PAlarm.start(); }""")
    p.wait_for_timeout(5600)
    visible = p.evaluate("window.__n")
    assert visible >= 1, ("strip should repaint every 5 s while visible", visible)
    p.evaluate("() => { window.__hid = true; document.dispatchEvent(new Event('visibilitychange')); window.__n = 0; window.__a = 0; }")
    p.wait_for_timeout(11000)
    hidden, alarms = p.evaluate("[window.__n, window.__a]")
    assert hidden == 0, ("no strip repaint while hidden", hidden)
    assert alarms >= 1, ("price alarms must keep ticking in a hidden tab", alarms)
    p.evaluate("() => { window.__hid = false; document.dispatchEvent(new Event('visibilitychange')); }")
    p.wait_for_timeout(200)
    back = p.evaluate("window.__n")
    assert back == 1, ("one catch-up repaint when shown again", back)
    assert not errs, errs
    b.close()
print("ok vis timers: visible", visible, "hidden", hidden, "alarms hidden", alarms, "catch-up", back)
