"""Price alarms (modules/ws/21d_price_alarms.js, PALARM-PURE block) run with node: every TradingView condition, the four
trigger modes, expiry, message placeholders, and the chart / menu hooks being wired. Plain script; skipped without node."""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(ROOT, "modules", "ws", "21d_price_alarms.js"), encoding="utf-8").read()
PURE = re.search(r"/\* PALARM-PURE-START.*?\*/(.*?)/\* PALARM-PURE-END \*/", SRC, re.S).group(1)

# the hooks into the chart must stay wired (a refactor of 20 / 21 that drops them silently disables the feature)
CH = open(os.path.join(ROOT, "modules", "ws", "20_chart_canvas.js"), encoding="utf-8").read()
DT = open(os.path.join(ROOT, "modules", "ws", "21_drawing_tools.js"), encoding="utf-8").read()
assert "this.alarmDown(e)" in CH and "this.paintAlarms(c, py, PR, PB, dec)" in CH and "this.paintPlus(c, m, PR, PB, dec)" in CH
assert "this.alarmMove(e)" in CH and "this.alarmUp(e)" in CH   # drag an alert line to move it
assert "palarmDialog({sym:this.sym" in DT and "palarmManager(this.sym" in DT

if not shutil.which("node"):
    print("skip price alarms (no node)"); sys.exit(0)

JS = PURE + r"""
const H = (a, p0, p1, c) => palarmHit(Object.assign({v:100}, a), p0, p1, c);
const out = {
  cross: [H({cond:"cross"}, 99, 100), H({cond:"cross"}, 101, 99.5), H({cond:"cross"}, 99, 99.9), H({cond:"cross"}, null, 101)],
  up: [H({cond:"up"}, 99, 101), H({cond:"up"}, 101, 99)], down: [H({cond:"down"}, 101, 99), H({cond:"down"}, 99, 101)],
  gtlt: [H({cond:"gt"}, null, 101), H({cond:"gt"}, null, 100), H({cond:"lt"}, null, 99)],
  ch: [H({cond:"enter", v2:110}, 99, 105), H({cond:"exit", v2:110}, 105, 111), H({cond:"inside", v2:90}, null, 95), H({cond:"outside", v2:110}, null, 95),
       H({cond:"enter", v:110, v2:100}, 111, 108)],
  mv: [H({cond:"mup", v:5, n:2}, null, 106, [100, 101, 106]), H({cond:"mup", v:5, n:2}, null, 104, [100, 101, 104]),
       H({cond:"mdnp", v:2, n:1}, null, 97, [100, 97]), H({cond:"mupp", v:2, n:5}, null, 120, [100, 120])],
};
// trigger modes
const rows = (t, c) => t.map((x, i) => ({t:x, c:c[i]}));
let a = {cond:"cross", v:100, on:true, trig:"once"};
out.once = [palarmCheck(a, {p0:99, p1:101, curT:1, rows:rows([1],[101])}, 1000), a.on, a.status, palarmCheck(a, {p0:99, p1:101, curT:2, rows:[]}, 2000)];
a = {cond:"gt", v:100, on:true, trig:"bar"};
out.bar = [palarmCheck(a, {p0:101, p1:102, curT:5, rows:[]}, 1), palarmCheck(a, {p0:102, p1:103, curT:5, rows:[]}, 2), palarmCheck(a, {p0:103, p1:104, curT:6, rows:[]}, 3), a.on];
a = {cond:"gt", v:100, on:true, trig:"min"};
out.min = [palarmCheck(a, {p1:101, rows:[]}, 1000), palarmCheck(a, {p1:101, rows:[]}, 30000), palarmCheck(a, {p1:101, rows:[]}, 62000)];
a = {cond:"up", v:100, on:true, trig:"close"};   // rows include the running bar last; closed bars decide
out.close = [palarmCheck(a, {p1:105, rows:rows([1,2,3],[98,99,105])}, 1),          // first look: remembers bar 2, no fire
             palarmCheck(a, {p1:99, rows:rows([1,2,3,4],[98,99,101,99])}, 2),       // bar 3 closed 99 -> 101: crossed up
             palarmCheck(a, {p1:99, rows:rows([1,2,3,4],[98,99,101,99])}, 3)];      // same closed bar again: nothing
a = {cond:"gt", v:100, on:true, trig:"bar", exp:500};
out.exp = [palarmCheck(a, {p1:101, rows:[]}, 1000), a.on, a.status];
out.off = palarmCheck({cond:"gt", v:1, on:false}, {p1:5, rows:[]}, 1);
out.txt = [palarmText({sym:"BTC-USDT", cond:"cross", v:100, tf:"1H", msg:"{{ticker}} at {{close}} on {{interval}}"}, 101.5),
           palarmText({sym:"ETH-USDT", cond:"enter", v:1, v2:2}, 1.5)];
console.log(JSON.stringify(out));
"""
r = subprocess.run([shutil.which("node"), "-e", JS], capture_output=True, text=True)
assert r.returncode == 0, r.stderr
o = json.loads(r.stdout)
assert o["cross"] == [True, True, False, False], o["cross"]
assert o["up"] == [True, False] and o["down"] == [True, False]
assert o["gtlt"] == [True, False, True]
assert o["ch"] == [True, True, True, True, True], o["ch"]   # channel bounds work in either order
assert o["mv"] == [True, False, True, False], o["mv"]       # too few bars -> no fire
assert o["once"] == [101, False, "triggered", None], o["once"]
assert o["bar"] == [102, None, 104, True], o["bar"]
assert o["min"] == [101, None, 101], o["min"]
assert o["close"] == [None, 101, None], o["close"]
assert o["exp"] == [None, False, "expired"] and o["off"] is None
assert o["txt"][0] == "BTC-USDT at 101.5 on 1H", o["txt"]
assert o["txt"][1] == "ETH-USDT Entering Channel 1 / 2", o["txt"]
print("ok price alarms")
