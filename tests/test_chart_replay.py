"""Chart replay (modules/ws/20_chart_canvas.js): view = first n candles, live data kept aside, a fresh load ends replay. Plain script (node)."""
import json, re, subprocess
from pathlib import Path

src = (Path(__file__).resolve().parent.parent / "modules/ws/20_chart_canvas.js").read_text()
names = ("liveData", "rpStart", "rpStep", "rpStop", "rpView", "setData")
body = {}
for n in names:   # method source "name(args){ ... }" up to the next two-space method start
    m = re.search(r"\n  (" + n + r"\([^)]*\)\{.*?)\n  (?=[a-zA-Z_/])", src, re.S)
    assert m, n
    body[n] = m.group(1)
js = "const C = {" + ",\n".join(body[n] for n in names) + "};\n" + r"""
const o = Object.assign(Object.create(C), {data:[], PR:800, bw:8, r:0, calls:0, calcEma(){}, clampR(){}, draw(){ this.calls++; }, viewGet(){ return null; }, fit(){}, saveView(){}});
const mk = n => Array.from({length:n}, (_, i) => ({t:i, c:i}));
o.setData(mk(200), false);
o.rpStart(); const n0 = o.rp.n;
const out = {started: !!o.rp, view: o.data.length === n0, n0};
o.rpStep(5); out.step = o.data.length === n0 + 5;
o.rpStep(-1000); out.floor = o.data.length === 60;
o.rpStep(10000); out.ceil = o.data.length === 200;
o.rpStep(-50); const shown = o.data.length;
o.liveData().push({t:200, c:200}); out.liveAside = o.data.length === shown && o.liveData().length === 201;
o.setData(mk(205), false); out.refreshKept = o.data.length === shown && o.rp.full.length === 205;
o.rpStop(); out.stop = !o.rp && o.data.length === 205;
o.rpStart(); o.setData(mk(90), true); out.freshEnds = !o.rp && o.data.length === 90;
console.log(JSON.stringify(out));
"""
r = subprocess.run(["node", "-e", js], capture_output=True, text=True)
assert r.returncode == 0, r.stderr
res = json.loads(r.stdout.strip().splitlines()[-1])
assert all(v for k, v in res.items() if k != "n0"), res
print("ok chart replay", res)
