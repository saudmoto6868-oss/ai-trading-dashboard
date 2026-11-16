"""Reversal boxes: Python (modules/reversal_boxes.py) and the Workspace JS (s26Boxes) must agree on the same candles.
Needs node. Run: python3 tests/test_reversal_boxes_js_parity.py"""
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
from modules.reversal_boxes import reversal_boxes  # noqa: E402

H = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf-8").read()
JS = re.search(r"// S26-BEGIN.*?// S26-END", H, re.S).group(0)
assert "function s26Boxes" in JS and 's26Boxes(D' in H   # the box calc and its painter branch are both built in


def walk(seed, n=600, p=4000.0, vol=3.0):
    rnd, rows = random.Random(seed), []
    for _ in range(n):
        o = p
        p += rnd.gauss(0, vol)
        rows.append((round(o, 2), round(max(o, p) + abs(rnd.gauss(0, vol / 2)), 2), round(min(o, p) - abs(rnd.gauss(0, vol / 2)), 2), round(p, 2)))
    return rows


node = shutil.which("node")
if not node:
    print("SKIP: node not installed")
    sys.exit(0)
total = 0
for seed in range(6):
    rows = walk(seed)
    for sw, m in ((3, 2.0), (5, 3.0)):
        bars = [tc.es.Bar(str(i), *r) for i, r in enumerate(rows)]
        py = reversal_boxes(bars, ratio=2.6, left=sw, right=sw, min_atr=m)
        D = [{"t": i, "o": r[0], "h": r[1], "l": r[2], "c": r[3]} for i, r in enumerate(rows)]
        src = JS + "\nconsole.log(JSON.stringify(s26Boxes(%s, %s)));" % (
            json.dumps(D), json.dumps({"ratio": 2.6, "sw": sw, "minAtr": m, "half": 0.25, "wait": 80}))
        js = json.loads(subprocess.run([node, "-e", src], capture_output=True, text=True, check=True).stdout)
        assert len(py) == len(js), (len(py), len(js), seed, sw, m)
        for a, b in zip(py, js):
            assert all(a[k] == b[k] for k in ("dir", "start", "end", "touched")), (a, b)
            assert all(abs(a[k] - b[k]) < 1e-9 for k in ("zone", "top", "bottom")), (a, b)
        total += len(py)
assert total > 30, total
print(f"ok reversal boxes js parity: {total} boxes identical over 12 cases")
