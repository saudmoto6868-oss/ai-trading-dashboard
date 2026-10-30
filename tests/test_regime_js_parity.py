"""The Workspace regime chip (JS block REGIME-BEGIN..END in workspace_app.html) gives the SAME label and numbers as modules/regime.py on the same candles (node, no browser).
Run: PYTHONPATH=. python tests/test_regime_js_parity.py"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from modules.regime import classify  # noqa: E402

html = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf8").read()
m = re.search(r"/\* REGIME-BEGIN.*?\*/\n(.*?)/\* REGIME-END \*/", html, re.S)
assert m, "regime block not found"


def frame(close, spread=0.3, vol=None, seed=1):
    close = np.asarray(close, float); n = len(close); r = np.random.default_rng(seed)
    sp = np.full(n, spread) if np.isscalar(spread) else np.asarray(spread, float)
    o = np.concatenate([[close[0]], close[:-1]])
    return pd.DataFrame({"open": o, "high": np.maximum(o, close) + sp, "low": np.minimum(o, close) - sp, "close": close, "volume": r.uniform(80, 120, n) if vol is None else vol})


g = np.random.default_rng(7); n = 220
cases = {}
cases["trend"] = frame(100 * np.exp(np.cumsum(0.004 + g.normal(0, 0.003, n))), 0.2)
cases["chop"] = frame(100 + 0.6 * np.sin(np.arange(n) / 2.0) + g.normal(0, 0.05, n))
cl = 100 + np.cumsum(g.normal(0, 0.3, n)); cl[-5:] = cl[-6] * np.array([.99, .975, .96, .945, .93]); cases["crash"] = frame(cl)
sp = np.full(n, 0.3); sp[-5:] = 6.0; cases["hivol"] = frame(100 + np.cumsum(g.normal(0, 0.3, n)), sp)
sq = 100 + np.cumsum(g.normal(0, 1.0, n)); sq[-30:] = sq[-31] + g.normal(0, 0.02, 30); cases["squeeze"] = frame(sq, np.concatenate([np.full(n - 30, 0.3), np.full(30, 0.05)]))
v = np.full(n, 100.0) + g.uniform(-10, 10, n); v[-1] = 5.0; cases["thin"] = frame(100 + np.cumsum(g.normal(0, 0.3, n)), vol=v)
cases["novol"] = frame(100 + np.cumsum(g.normal(0, 0.3, n)), vol=np.zeros(n))
for i in range(6):
    cases[f"walk{i}"] = frame(100 + np.cumsum(g.normal(0, 0.5, n)), seed=i)
cases["short"] = frame(100 + np.arange(30) * 1.0)
payload = {k: [{"t": i, "o": float(r.open), "h": float(r.high), "l": float(r.low), "c": float(r.close), "v": float(r.volume)} for i, r in enumerate(df.itertuples())] for k, df in cases.items()}
script = "const Regime=(()=>{" + m.group(1).replace("const Regime = {", "return {", 1).rstrip().rstrip(";") + "})();\nconst P=JSON.parse(require('fs').readFileSync(0,'utf8'));const out={};for(const k in P)out[k]=Regime.of(P[k]);console.log(JSON.stringify(out));"
res = subprocess.run(["node", "-e", script], input=json.dumps(payload), capture_output=True, text=True, timeout=60)
assert res.returncode == 0, res.stderr[:400]
js = json.loads(res.stdout)
for k, df in cases.items():
    py, j = classify(df), js[k]
    assert (py["regime"] or None) == (j["regime"] or None), (k, py, j)
    for a, b in (("adx", "adx"), ("atr_ratio", "atrRatio"), ("ret_z", "retZ")):
        if py.get(a) is not None:
            assert j[b] is not None and abs(j[b] - py[a]) < 0.06 * max(1, abs(py[a])), (k, a, py[a], j[b])
    if py.get("bb_pct") is not None:
        assert abs(j["bbPct"] - py["bb_pct"]) <= 1.01, (k, py["bb_pct"], j["bbPct"])
    assert (py.get("vol_pct") is None) == (j.get("volPct") is None), (k, py, j)
print("ok JS regime == python regime on", len(cases), "series:", {k: js[k]["regime"] for k in cases if not k.startswith("walk")})
