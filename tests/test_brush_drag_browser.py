"""Browser test (Playwright + mocked OKX): a brush stroke can be moved whole and one of its handles dragged.
Mock-tested only: no real market data, no keys, no network. Run: python3 tests/test_brush_drag_browser.py
Needs: pip install playwright && python3 -m playwright install chromium (skips with exit 0 if missing)."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("SKIP: playwright not installed"); sys.exit(0)
from modules.workspace import build_workspace_html

URL = "http://app.test/ws.html"
HTML = build_workspace_html(["BTC-USDT-SWAP"], [], "en")


def candles(n=300, bar_ms=3600_000):
    now = int(time.time() * 1000) // bar_ms * bar_ms
    rows, p = [], 100.0
    for i in range(n):
        t = now - (n - 1 - i) * bar_ms; o = p; p = p + (1 if i % 7 < 4 else -0.8); c = p
        rows.append([str(t), str(o), str(max(o, c) + 0.5), str(min(o, c) - 0.5), str(c), "10", "10", "10", "1"])
    return list(reversed(rows))  # OKX returns newest first


def route(r):
    u = r.request.url
    if u == URL:
        r.fulfill(body=HTML, content_type="text/html")
    elif "/api/v5/market/candles" in u or "/api/v5/market/history-candles" in u:
        r.fulfill(body=json.dumps({"code": "0", "data": [] if "history" in u else candles()}), content_type="application/json")
    else:
        r.abort()


STORED_JS = "() => { const k = Object.keys(localStorage).find(k => k.includes('_dr_')); return k ? JSON.parse(localStorage.getItem(k)) : null; }"


def main():
    fails = []

    def check(name, ok, info=""):
        print(("PASS " if ok else "FAIL ") + name, info)
        if not ok:
            fails.append(name)
    with sync_playwright() as pw:
        b = pw.chromium.launch(); page = b.new_page(viewport={"width": 1400, "height": 900})
        errs = []; page.on("pageerror", lambda e: errs.append(str(e)))
        page.route("**/*", route); page.goto(URL); page.wait_for_timeout(1000)
        page.locator("select").first.select_option(label="Chart")  # workspace starts blank: add a chart widget
        page.wait_for_selector("canvas", timeout=20000)
        page.locator("button", has_text="▢").first.click(); page.wait_for_timeout(2500)  # maximize so the whole tool column is visible
        btn = page.locator("button[title^='Brush']").first
        check("brush tool button found", btn.count() > 0)
        btn.click()
        cv = page.locator("canvas").first.bounding_box()
        x0, y0 = cv["x"] + cv["width"] * 0.15, cv["y"] + cv["height"] * 0.4
        page.mouse.move(x0, y0); page.mouse.down()
        for i in range(1, 121):
            page.mouse.move(x0 + i * 6, y0 + (i % 10) * 4)
        page.mouse.up(); page.wait_for_timeout(200)
        d = page.evaluate(STORED_JS)
        check("stroke saved with >=10 points", bool(d) and d[0]["type"] == "brush" and len(d[0]["pts"]) >= 10, str(len(d[0]["pts"])) if d else "none")
        page.screenshot(path="/tmp/brush_drawn.png")
        if not d:
            b.close(); sys.exit(1)
        pts0 = d[0]["pts"]
        page.locator("button.dt button[title='Select'], button[title*='ursor'], button:text-is('↖')").first.click()
        # move the whole stroke: 121 points -> a handle every 5th point (0,5,10..); press on point 62 (not a handle), drag by (+80, +60)
        mx, my = x0 + 62 * 6, y0 + (62 % 10) * 4
        page.mouse.move(mx, my); page.mouse.down(); page.mouse.move(mx + 40, my + 30, steps=5); page.mouse.move(mx + 80, my + 60, steps=5); page.mouse.up(); page.wait_for_timeout(200)
        d1 = page.evaluate(STORED_JS)[0]["pts"]
        dt = {round(a["t"] - c["t"]) for a, c in zip(d1, pts0)}; dp = {round(a["p"] - c["p"], 6) for a, c in zip(d1, pts0)}
        check("whole stroke moved (every point shifted)", len(d1) == len(pts0) and 0 not in dp, f"dt={sorted(dt)[:3]} dp={sorted(dp)[:3]}")
        # handle drag: the stroke is selected; its first point is now at (x0+80, y0+60)
        sx, sy = x0 + 80, y0 + 60
        page.mouse.move(sx, sy); page.mouse.down(); page.mouse.move(sx + 25, sy - 25, steps=5); page.mouse.up(); page.wait_for_timeout(200)
        d2 = page.evaluate(STORED_JS)[0]["pts"]
        changed = [i for i, (a, c) in enumerate(zip(d2, d1)) if a != c]
        check("dragging a handle edits only that point", changed == [0], f"changed idx={changed[:5]}")
        check("no page errors", not errs, "; ".join(errs[:3]))
        page.screenshot(path="/tmp/brush_drag.png"); b.close()
    print("FAILED: " + ", ".join(fails) if fails else "ALL PASS")
    sys.exit(1 if fails else 0)


main()
