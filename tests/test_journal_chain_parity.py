"""Journal chain layers (JS `Chain.layers` in workspace_app.html) give the SAME layers + grade as modules/strategy_lab.py chain_layers/grade on the same candles (node, no browser).
Run: PYTHONPATH=. python tests/test_journal_chain_parity.py"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from modules import strategy_lab as sl  # noqa: E402
from modules.signals import atr_series  # noqa: E402

html = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf8").read()
m = re.search(r"const Chain = \{.*?\n\};\n", html, re.S)
assert m, "Chain block not found"
rng = np.random.default_rng(7)
js = "const out = [];\n" + m.group(0) + "\n"
cases = []
for k in range(40):
    n = 260
    c = 100 + np.cumsum(rng.normal(0.05 * (k % 3 - 1), 0.8 + 0.3 * (k % 4), n))
    o = c + rng.normal(0, .2, n); h = np.maximum(o, c) + abs(rng.normal(0, .5, n)); l = np.minimum(o, c) - abs(rng.normal(0, .5, n))
    v = rng.uniform(10, 40, n) * (1 + 2 * (rng.random(n) > .85))
    hour = [3, 9, 15, 22][k % 4]; ms = int(pd.Timestamp(f"2026-03-0{1 + k % 7} {hour:02d}:00", tz="UTC").timestamp() * 1000)
    d = 1 if k % 2 else -1; tf = "1d" if k % 9 == 0 else "1h"
    rows = [dict(t=i, o=float(o[i]), h=float(h[i]), l=float(l[i]), c=float(c[i]), v=float(v[i])) for i in range(n)]
    cases.append((rows, d, tf, ms))
    # python side
    df = pd.DataFrame({"high": h, "low": l, "close": c})
    natr = atr_series(df, 14).values / np.where(c > 0, c, 1)
    i = n - 1
    ctx = sl.chain_ctx(h, l, c, v, natr, i)
    tr = int(np.sign(c[i] - c[i - sl.TREND_N]))
    hr = pd.Timestamp(ms, unit="ms", tz="UTC").hour
    ses = None if tf == "1d" else "Asia 00-07" if hr < 7 else "London 07-12" if hr < 12 else "New York 12-20" if hr < 20 else "Late 20-24"
    cases[-1] = cases[-1] + (sl.chain_layers(ctx, d, tr, ses),)
js += "const cases = " + json.dumps([[r, d, tf, ms] for r, d, tf, ms, _ in cases]) + ";\nconsole.log(JSON.stringify(cases.map(([r, d, tf, ms]) => Chain.layers(r, d, tf, ms))));\n"
js = "const Regime = {};\n" + js
import tempfile
with tempfile.TemporaryDirectory() as td:
    fp = os.path.join(td, "chain.js"); open(fp, "w", encoding="utf8").write(js)
    res = subprocess.run(["node", fp], capture_output=True, text=True, timeout=60)
assert res.returncode == 0, res.stderr[:500]
got = json.loads(res.stdout)
bad = 0
for (rows, d, tf, ms, exp), g in zip(cases, got):
    for key in sl.CHAIN:
        if bool(g[key]) != bool(exp[key]):
            bad += 1; print("mismatch", key, tf, d, g, exp)
    assert g["g"] == sl.grade(exp), (g, exp)
assert bad == 0, bad
assert len({tuple(g[k] for k in sl.CHAIN) for g in got}) > 4, "test cases too uniform"
print("ok journal chain parity", len(got), "cases")
