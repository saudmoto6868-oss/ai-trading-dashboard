"""Trade classes engine (JS block TCLASS-BEGIN..END in workspace_app.html, source modules/ws/24b_tclass.js), run with node on synthetic candles.
Checks: point sizes, walk-forward events (no future candles), conservative stop-first rule, candidate plans point the right way, styles stacks.
Synthetic data only: this proves the arithmetic, NOT that bounces make money. Run: python3 tests/test_tclass_js.py"""
import json
import math
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf8").read()
m = re.search(r"/\* TCLASS-BEGIN.*?\*/\n(.*?)/\* TCLASS-END \*/", html, re.S)
assert m, "TCLASS block not found in workspace_app.html (run scripts/build_workspace.py)"


def rows_from(close, spread=0.4):
    out, prev = [], close[0]
    for i, c in enumerate(close):
        o = prev
        w = spread * (1 + 0.5 * abs(math.sin(i * 7.31)))   # wick size varies per bar: no ties between neighbours
        out.append({"t": i, "o": o, "h": max(o, c) + w, "l": min(o, c) - w, "c": c, "v": 1})
        prev = c
    return out


# a clean range 100..110 (period 40 bars) that ends near the support
rng = [105 + 5 * math.sin(2 * math.pi * i / 40 - math.pi / 2) + 0.15 * math.sin(i * 12.9898) for i in range(400)]   # small fixed noise: no exact ties
# 400 bars: the last close sits on the support (bottom of the range)
trend = [100 + 0.2 * i + 2 * math.sin(i / 3.0) for i in range(200)]
payload = {"rng": rows_from(rng), "trend": rows_from(trend)}

js = m.group(1) + r"""
const P = JSON.parse(require('fs').readFileSync(0, 'utf8')), out = {};
out.ps = [TCE.pointSize("Y:EURUSD=X", 1.08), TCE.pointSize("Y:USDJPY=X", 150), TCE.pointSize("HL:xyz:GOLD", 2400), TCE.pointSize("BTC-USDT", 60000), TCE.pointSize("HL:xyz:SP500", 5000), TCE.pointSize("DOGE-USDT", 0.15)];
out.nice = [TCE.nicePts(87), TCE.nicePts(130), TCE.nicePts(240), TCE.nicePts(0)];
const R = P.rng, ev = TCE.events(R, {hold:16});
out.n = ev.length; out.longs = ev.filter(e => e.side > 0).length; out.shorts = ev.filter(e => e.side < 0).length;
out.st = TCE.stats(ev, 3);
// no look-ahead: events on a prefix == events of the full series whose window ends inside the prefix
const cut = 300, evp = TCE.events(R.slice(0, cut), {hold:16});
out.prefixOk = JSON.stringify(evp.filter(e => e.i + 16 < cut)) === JSON.stringify(ev.filter(e => e.i + 16 < cut));
// stop-first: a bar that touches both the target and the stop counts as the stop
const fake = R.slice(0, 200).map(r => Object.assign({}, r)); const e0 = TCE.events(fake, {hold:16}).find(e => e.side > 0);
if (e0){ const b = fake[e0.i + 1]; b.h = e0.entry + 100; b.l = e0.stop - 1; const e1 = TCE.events(fake, {hold:16}).find(e => e.i === e0.i); out.stopFirst = e1.stopped && e1.mfe === 0; }
const lv = [{p:100, kind:"S", touches:4}, {p:110, kind:"R", touches:4}];
out.cands = TCE.candidates("BTC-USDT", R, lv, P.trend, null, {targetPts:0, ps:1, hold:16});
out.cands100 = TCE.candidates("BTC-USDT", R, lv, P.trend, null, {targetPts:5, ps:1, hold:16});
out.bias = TCE.bias(P.trend);
out.styles = Object.keys(TCE.STYLES).map(k => [k, TCE.STYLES[k].bias, TCE.STYLES[k].setup, TCE.STYLES[k].entry]);
process.stdout.write(JSON.stringify(out));
"""
r = subprocess.run(["node", "-e", js], input=json.dumps(payload), capture_output=True, text=True, timeout=60)
assert r.returncode == 0, r.stderr
o = json.loads(r.stdout)

assert o["ps"] == [0.0001, 0.01, 0.1, 1, 1, 0.00001], o["ps"]
assert o["nice"] == [100, 100, 250, 0], o["nice"]
assert o["n"] >= 10 and o["longs"] and o["shorts"], o
assert o["prefixOk"], "events changed when future candles were added: look-ahead"
assert o.get("stopFirst") is True, o.get("stopFirst")
assert o["st"]["n"] == o["n"] and 0 <= o["st"]["hitPct"] <= 1
assert o["bias"]["bias"] == "bull" and o["bias"]["trend"] == "up", o["bias"]
c = o["cands"]
assert len(c) >= 1, "price ends next to the support: expected a long candidate"
for x in c + o["cands100"]:
    if x["side"] > 0:
        assert x["stop"] < x["entry"] < x["tps"][0] <= x["tps"][1], x
    else:
        assert x["stop"] > x["entry"] > x["tps"][0] >= x["tps"][1], x
    assert 0 <= x["score"] <= x["max"] == 6
longs = [x for x in c if x["side"] > 0]
assert longs and longs[0]["agree"] == 1, "bias frame trends up: a long at support agrees"
assert o["cands100"][0]["pts"] == 5 and abs(o["cands100"][0]["tps"][0] - o["cands100"][0]["entry"] - 5) < 1e-9
assert o["styles"][0] == ["Scalp", "1H", "15m", "5m"] and o["styles"][2] == ["Swing", "1W", "1D", "4H"], o["styles"]
print("ok tclass engine: %d events (%d long / %d short), median bounce %.2f, auto target %s pts" % (o["n"], o["longs"], o["shorts"], o["st"]["median"], c[0]["autoPts"]))
