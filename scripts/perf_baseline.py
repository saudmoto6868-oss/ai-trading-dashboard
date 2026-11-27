"""Speed baseline (maintenance plan M0, steps 0.3 / 0.5 / 0.6): same numbers, same way, before and after every speed PR.

Prints: code size facts, browser timers, then per top-bar page the offline Python run time (AppTest, network blocked)
and how many network calls the page tried. Offline numbers are NOT the deployed server's time; they show change, not truth.
Run: python3 scripts/perf_baseline.py [--pages 0,1,11] [--json out.json] [--browser]
--browser (step 0.2): the Workspace page in headless Chromium (standard layout, network blocked): script parse, CPU time and long tasks
in the first 10 s. Headless on this machine, not the owner's laptop; compare runs, not devices.
"""
import argparse
import json
import os
import pathlib
import re
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
CALLS = {"n": 0}


def _block_network():
    import requests

    def fail(*a, **k):
        CALLS["n"] += 1
        raise requests.exceptions.ConnectionError("blocked in perf baseline")
    requests.get = requests.post = requests.Session.request = fail


def code_facts():
    ws = ROOT / "modules" / "ws"
    js = "".join(p.read_text(encoding="utf-8") for p in ws.glob("*.js"))
    main = (ROOT / "main.py").read_text(encoding="utf-8")
    return {
        "main_py_lines": main.count("\n"),
        "modules_py_files": len(list((ROOT / "modules").glob("*.py"))),
        "workspace_app_kb": round((ROOT / "modules" / "workspace_app.html").stat().st_size / 1024),
        "largest_parts_kb": {p.name: round(p.stat().st_size / 1024) for p in sorted(ws.glob("*.js"), key=lambda p: -p.stat().st_size)[:5]},
        "js_setInterval": len(re.findall(r"\bsetInterval\(", js)),
        "js_new_WebSocket": len(re.findall(r"new WebSocket\(", js)),
        "main_threads": len(re.findall(r"threading\.Thread\(", main)),
    }


def page_runs(pages):
    from streamlit.testing.v1 import AppTest
    names = re.search(r"^_PAGES = (\[.*?\])", (ROOT / "main.py").read_text(encoding="utf-8"), re.M)
    names = json.loads(names.group(1)) if names else []
    out = []
    for p in pages:
        CALLS["n"] = 0
        at = AppTest.from_file(str(ROOT / "main.py"), default_timeout=300)
        at.session_state["page"] = p
        t0 = time.perf_counter()
        at.run()
        first = time.perf_counter() - t0
        t0 = time.perf_counter()
        at.run()
        rerun = time.perf_counter() - t0
        out.append({"page": p, "name": names[p] if p < len(names) else str(p), "first_s": round(first, 2),
                    "rerun_s": round(rerun, 2), "net_calls": CALLS["n"], "errors": len(at.exception)})
    return out


def browser_run(secs=10):
    """Workspace page, standard layout, network blocked: parse cost of the script, CPU split (CDP Performance.getMetrics), long tasks (>50 ms)."""
    import tempfile
    from playwright.sync_api import sync_playwright
    from modules.workspace import build_workspace_html, _template_text
    tpl = _template_text()
    i = tpl.index("__CONFIG__")
    js = tpl[tpl.rindex("<script>", 0, i) + 8:tpl.rindex("</script>")]
    path = os.path.join(tempfile.mkdtemp(), "ws.html")
    open(path, "w", encoding="utf-8").write(build_workspace_html(["BTC-USDT", "ETH-USDT"], None, "en"))
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={"width": 1500, "height": 950})
        p.route("**/*", lambda r: r.continue_() if r.request.url.startswith("file:") else r.abort())
        p.add_init_script("window.__lt = []; new PerformanceObserver(l => l.getEntries().forEach(e => window.__lt.push(e.duration))).observe({type:'longtask', buffered:true});")
        cdp = p.context.new_cdp_session(p)
        cdp.send("Performance.enable")
        t0 = time.perf_counter()
        p.goto("file://" + path)
        p.wait_for_function("typeof Ws === 'object' && Ws.panels.length > 0", timeout=30000)
        boot = time.perf_counter() - t0
        p.wait_for_timeout(secs * 1000)
        m = {x["name"]: x["value"] for x in cdp.send("Performance.getMetrics")["metrics"]}
        lt = p.evaluate("window.__lt")
        parse = p.evaluate("code => { const t = performance.now(); new Function(code); return performance.now() - t; }", js.replace("__CONFIG__", "{}", 1))
        b.close()
    return {"script_kb": round(len(js.encode()) / 1024), "parse_ms": round(parse, 1), "boot_s": round(boot, 2),
            "script_s": round(m.get("ScriptDuration", 0), 2), "layout_s": round(m.get("LayoutDuration", 0), 2), "task_s": round(m.get("TaskDuration", 0), 2),
            "heap_mb": round(m.get("JSHeapUsedSize", 0) / 1e6, 1), "longtasks": len(lt), "longtask_max_ms": round(max(lt or [0])), "longtask_sum_ms": round(sum(lt))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="0,1,11,12,18,20,13,14,15", help="page indexes (default: the top bar, _PAGE_ORDER)")
    ap.add_argument("--json", help="also write the result to this file")
    ap.add_argument("--browser", action="store_true", help="step 0.2: also measure the Workspace page in headless Chromium (needs playwright)")
    a = ap.parse_args()
    os.environ.setdefault("PERF_BASELINE", "1")
    _block_network()
    t0 = time.perf_counter()
    import pandas  # noqa: F401  (cold import cost, paid once per server process)
    res = {"pandas_import_s": round(time.perf_counter() - t0, 2), **code_facts()}
    res["pages"] = page_runs([int(x) for x in a.pages.split(",") if x.strip()])
    for k, v in res.items():
        if k != "pages":
            print(f"{k}: {v}")
    print("\n| page | name | first run s | rerun s | network calls | errors |\n|---|---|---|---|---|---|")
    for r in res["pages"]:
        print(f"| {r['page']} | {r['name']} | {r['first_s']} | {r['rerun_s']} | {r['net_calls']} | {r['errors']} |")
    if a.browser:
        res["browser"] = browser_run()
        print("\nbrowser (Workspace, %(script_kb)d KB script, first 10 s): parse %(parse_ms)s ms, boot %(boot_s)s s, script %(script_s)s s, layout %(layout_s)s s, all tasks %(task_s)s s, heap %(heap_mb)s MB, long tasks %(longtasks)s (max %(longtask_max_ms)s ms, sum %(longtask_sum_ms)s ms)" % res["browser"])
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
