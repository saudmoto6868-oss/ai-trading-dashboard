"""HTF candles indicator (modules/ws/21_drawing_tools.js htfBars): UTC buckets, weekly from Monday, OHLC aggregation, no output
when the timeframe is not higher than the chart. Plain script (node)."""
import json, re, subprocess
from pathlib import Path

src = (Path(__file__).resolve().parent.parent / "modules/ws/21_drawing_tools.js").read_text()
m = re.search(r"\n  (htfBars\(tf\)\{.*?)\n  (?=paintHtfc)", src, re.S)
assert m, "htfBars not found"
js = "const TFSEC = {'1H':3600,'4H':14400,'1D':86400,'1W':604800};\nconst C = {" + m.group(1).rstrip().rstrip(",") + "};\n" + r"""
const H = 3600e3, t0 = Date.UTC(2026, 10, 16, 0);   // Monday 2026-11-16 00:00 UTC
const data = Array.from({length: 24*9}, (_, i) => ({t: t0 + i*H, o: 100+i, h: 101+i, l: 99+i, c: 100.5+i}));   // 9 days of 1H candles
const o = Object.assign(Object.create(C), {data, tf: "1H"});
const d = o.htfBars("1D"), w = o.htfBars("1W"), same = o.htfBars("1H"), f4 = o.htfBars("4H");
console.log(JSON.stringify({nd: d.length, d0: d[0], d0n: d[0].n, nw: w.length, w0n: w[0].n, w1n: w[1].n, same: same.length, n4: f4.length,
  endOk: d[0].end === t0 + 24*H, wEndOk: w[0].end === t0 + 7*24*H}));
"""
r = subprocess.run(["node", "-e", js], capture_output=True, text=True)
assert r.returncode == 0, r.stderr
x = json.loads(r.stdout)
assert x["nd"] == 9 and x["d0n"] == 24 and x["d0"]["o"] == 100 and x["d0"]["c"] == 123.5 and x["d0"]["h"] == 124 and x["d0"]["l"] == 99, x
assert x["nw"] == 2 and x["w0n"] == 168 and x["w1n"] == 48, x   # Monday-start weeks
assert x["same"] == 0 and x["n4"] == 54 and x["endOk"] and x["wEndOk"], x
print("ok htf candles")
