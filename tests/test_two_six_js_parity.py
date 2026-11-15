"""The Workspace 2.6 indicator (s26Calc in modules/ws, S26-BEGIN/END) must give the same setups as the Python
engine (modules/two_six_chart.setups) on the same candles. Needs node. Run: python3 tests/test_two_six_js_parity.py"""
import json
import os
import random
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import two_six_chart as tc  # noqa: E402

H = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf-8").read()
JS = re.search(r"// S26-BEGIN.*?// S26-END", H, re.S).group(0)
assert '{id:"s26"' in H and 'paintS26(c, py)' in H and '["s26","struct"' in H   # engine, painter and menu entry are all wired


def walk(seed, n=600, p=4000.0, vol=3.0):
    rnd, rows = random.Random(seed), []
    for _ in range(n):
        o = p
        p += rnd.gauss(0, vol)
        rows.append((round(o, 2), round(max(o, p) + abs(rnd.gauss(0, vol / 2)), 2), round(min(o, p) - abs(rnd.gauss(0, vol / 2)), 2), round(p, 2)))
    return rows


KEYS = ("kind", "side", "known", "anchors", "fill", "exit", "status", "tp1_hit")
node = shutil.which("node")
if not node:
    print("SKIP: node not installed")
    sys.exit(0)
cases = [(walk(s), sw, r, h1, h2) for s in range(6) for sw, r, h1, h2 in ((5, 2.6, True, True), (3, 2.618, True, False), (8, 2.6, False, True))]
total = 0
for rows, sw, ratio, h1, h2 in cases:
    py = tc.setups([tc.es.Bar(str(i), *r) for i, r in enumerate(rows)], ratio=ratio, left=sw, right=sw, use_h1=h1, use_h2=h2)
    D = [{"t": i, "o": r[0], "h": r[1], "l": r[2], "c": r[3]} for i, r in enumerate(rows)]
    src = JS + "\nconsole.log(JSON.stringify(s26Calc(%s, %s)));" % (json.dumps(D), json.dumps({"ratio": ratio, "sw": sw, "h1": h1, "h2": h2}))
    js = json.loads(subprocess.run([node, "-e", src], capture_output=True, text=True, check=True).stdout)
    assert len(js) == len(py), (len(js), len(py), sw, ratio)
    for a, b in zip(py, js):
        assert all(a[k] == b[k] for k in KEYS), ({k: a[k] for k in KEYS}, {k: b[k] for k in KEYS})
        assert all(abs(a[k] - b[k]) < 1e-9 for k in ("entry", "stop", "tp1", "tp2")), (a, b)
    total += len(py)
assert total > 100, total
print(f"ok two_six js parity: {total} setups identical over {len(cases)} cases")
