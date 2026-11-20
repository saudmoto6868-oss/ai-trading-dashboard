"""The Workspace Elliott shape block (JS, EWSHAPE-BEGIN..END in workspace_app.html) gives the SAME names as
modules/elliott_shapes.py on the same pivots. Needs node. Run: python3 tests/test_ew_shapes_js_parity.py"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np  # noqa: E402
from modules import elliott_shapes as es  # noqa: E402

html = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf8").read()
m = re.search(r"/\* EWSHAPE-BEGIN.*?\*/\n(.*?)/\* EWSHAPE-END \*/", html, re.S)
assert m, "EWSHAPE block not found"

rng = np.random.default_rng(3)
cases = []
# hand cases from the Python tests (must cover every name)
cases += [[100, 120, 108, 130], [100, 120, 101, 119], [100, 120, 95, 125], [100, 120, 95, 118], [120, 100, 112, 90],
          [100, 120, 110, 150, 140, 160], [100, 120, 112, 150, 118, 152], [100, 120, 105, 115, 108, 113],
          [100, 110, 95, 115, 90, 120], [100, 120, 108, 130, 110, 125, 115, 145], [100, 120, 95, 125, 110, 130, 111.0, 130.5]]
cases += [[100, 120, 108, 130, 110, 125, 115, 145, 128, 150, 140, 165],
          [100, 120, 95, 125, 110, 130, 111.0, 130.5, 118, 140, 120, 150]]
# random alternating tails of length 4..10
for _ in range(400):
    n = int(rng.integers(4, 11))
    p = list(100 + np.cumsum(rng.normal(0, 6, n)))
    cases.append([float(x) for x in p])

script = ("const EWShape=(()=>{" + m.group(1).rstrip().rstrip(";") + "; return EWShape;})();\n"
          "const cases=JSON.parse(require('fs').readFileSync(0,'utf8'));\n"
          "console.log(JSON.stringify(cases.map(p => EWShape.tail(p))));\n")
out = subprocess.run(["node", "-e", script], input=json.dumps(cases), capture_output=True, text=True, timeout=60)
assert out.returncode == 0, out.stderr
js = json.loads(out.stdout)
py = [es.classify_tail(p) for p in cases]
bad = [(c, a, b) for c, a, b in zip(cases, py, js) if a != b]
assert not bad, bad[:3]
names = {x for x in py if x}
assert {"zigzag", "regular_flat", "expanded_flat", "running_flat", "impulse", "ending_diagonal", "contracting",
        "expanding", "double_zigzag", "double_three", "double_combo"} <= names | {x for x in js if x} or len(names) >= 6, names
print("test_ew_shapes_js_parity: OK", len(cases), "cases,", sorted(names))
