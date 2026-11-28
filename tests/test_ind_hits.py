"""Pure geometry of the chart "what is this?" card (modules/ws/21e_ind_hits.js: ihDist / ihPick), run in node. Mock data only.
Run: python3 tests/test_ind_hits.py"""
import os
import subprocess

SRC = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modules", "ws", "21e_ind_hits.js"), encoding="utf8").read()
fns = SRC[SRC.index("/* pure geometry"):SRC.index("Object.assign(CandleChart.prototype")]
js = fns + r"""
const L0 = [["box","r",0,0,200,100], ["ma","l",0,50,200,50], ["sig","t",90,40,60,11], ["dot","o",20,20,3], ["big","r",0,0,400,400]];
const eq = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) { console.log("FAIL", m, JSON.stringify(a)); process.exit(1); } };
eq(ihPick(L0, 100, 47), ["sig","ma","box","big"], "text first, then line, small box, big box");
eq(ihPick(L0, 20, 21), ["dot","box","big"], "dot");
eq(ihPick(L0, 150, 80), ["box","big"], "inside boxes only");
eq(ihPick(L0, 500, 500), [], "nothing");
eq(ihPick(L0, 10, 53), ["ma","box","big"], "line within 4 px");
eq(ihPick(L0, 10, 56), ["box","big"], "line too far");
eq(Math.round(ihDist(5, 5, 0, 0, 10, 0)), 5, "dist");
console.log("ok ind_hits");
"""
out = subprocess.run(["node", "-e", js], capture_output=True, text=True)
print(out.stdout.strip() or out.stderr.strip())
assert out.returncode == 0 and "ok ind_hits" in out.stdout
