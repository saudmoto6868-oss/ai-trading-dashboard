"""Speed baseline (maintenance plan M0, steps 0.3 / 0.5 / 0.6): same numbers, same way, before and after every speed PR.

Prints: code size facts, browser timers, then per top-bar page the offline Python run time (AppTest, network blocked)
and how many network calls the page tried. Offline numbers are NOT the deployed server's time; they show change, not truth.
Run: python3 scripts/perf_baseline.py [--pages 0,1,11] [--json out.json]
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="0,1,11,12,18,20,13,14,15", help="page indexes (default: the top bar, _PAGE_ORDER)")
    ap.add_argument("--json", help="also write the result to this file")
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
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
