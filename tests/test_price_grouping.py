"""Price grouping: fixed book levels grouped at 1000 / 10 / 0.01 give the expected rows (runs the real functions from workspace_app.html in node)."""
import json, os, re, shutil, subprocess, sys
src = open(os.path.join(os.path.dirname(__file__), "..", "modules", "workspace_app.html"), encoding="utf-8").read()
for name in ("GROUP_STEPS", "tickOfLevels", "groupBook", "groupStepFor"):
    assert name in src, name
if not shutil.which("node"):
    print("SKIP: node not installed (static presence checks passed)"); sys.exit(0)
i = src.index("const GROUP_STEPS"); j = src.index("function groupSelect(")
code = src[i:j] + """
const bids = [{p:67234.5,q:1},{p:67234,q:2},{p:67201,q:3},{p:66990,q:4}], asks = [{p:67235,q:1},{p:67236.5,q:2},{p:67260,q:3},{p:68010,q:4}];
const f = (l, s, side) => groupBook(l, s, side).map(x => x.p + ":" + x.q).join(",");
console.log(JSON.stringify({
  b1000: f(bids, 1000, "bid"), a1000: f(asks, 1000, "ask"), b10: f(bids, 10, "bid"), a10: f(asks, 10, "ask"),
  b001: f([{p:1.234,q:1},{p:1.2349,q:2},{p:1.2251,q:5}], 0.01, "bid"), a001: f([{p:1.231,q:1},{p:1.2349,q:2}], 0.01, "ask"),
  auto: groupBook(bids, 0, "bid") === bids, tick: tickOfLevels([{p:100.5},{p:100.25},{p:100.75},{p:101}]),
  clamp1: groupStepFor(0.001, 0.01), clamp2: groupStepFor(10, 0.01), clamp3: groupStepFor(0, 0.01), total: groupBook(bids, 1000, "bid").reduce((a, x) => a + x.q, 0)
}));
"""
out = json.loads(subprocess.run(["node", "-e", code], capture_output=True, text=True, check=True).stdout)
exp = {"b1000": "67000:6,66000:4", "a1000": "68000:6,69000:4", "b10": "67230:3,67200:3,66990:4", "a10": "67240:3,67260:3,68010:4",
       "b001": "1.23:3,1.22:5", "a001": "1.24:3", "auto": True, "tick": 0.25, "clamp1": 0.01, "clamp2": 10, "clamp3": 0, "total": 10}
bad = {k: (out[k], v) for k, v in exp.items() if out[k] != v}
for k in exp: print(("PASS" if k not in bad else "FAIL") + ": " + k + " = " + str(out[k]))
assert not bad, bad
print("PASS: price grouping (pure functions, node; the dropdown itself is checked in a browser mock)")
