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
// ---- deliberation rules ----
const base = {tf:{bias:"1H", setup:"15m", entry:"5m"}, ps:1, atr:1, levels:[], bias:{available:true, bias:"bull"}, setupB:{available:true, bias:"bull"}, trig:"rejection candle", confl:["VP"], vpAt:"POC", hist:{n:40, hitPct:0.6, p75:10}, late:0, regime:null, news:"", openSame:false, openOpp:false, classOpen:0, jr:null, scalp:false, ses:"NY AM KZ"};
const idea = {det:"bounce", side:1, entry:100, stop:98, tps:[104, 106], now:true, level:99.5};
const J = (o, i) => TCE.judge(Object.assign({}, idea, i || {}), Object.assign({}, base, o || {}));
out.jTake = J().verdict; out.jNews = J({news:"USD CPI"}).verdict; out.jOpen = J({openSame:true}).verdict; out.jOpp = J({openOpp:true}).verdict;
out.jLimit = J({}, {now:false}).verdict; out.jBias = J({bias:{available:true, bias:"bear"}}).cons.some(c => c[0] === 2.5);
const cutJ = J({levels:[{p:103.5, src:"resistance"}]}); out.cut = {t:cutJ.plan.tps[0], sec:cutJ.second.length};
const blk = J({levels:[{p:100.6, src:"resistance"}]}); out.blk = {rrPro:blk.pros.some(p => /^R:R/.test(p[1])), con:blk.cons.some(c => c[0] === 2)};
out.down = J({levels:[{p:100.6, src:"resistance"}], confl:["a","b","c"]}).verdict;
out.kz = J({scalp:true, ses:"off-KZ"}).pros.some(p => /kill zone/.test(p[1]));
// structure: a swing high at 110 then a close above it -> BOS / MSS up
const up = []; for (let i = 0; i < 80; i++){ const c = i < 50 ? 100 + 10*Math.sin(i/5) : 100 + (i - 50)*0.6; up.push({o:c, h:c + .3 + 0.05*Math.abs(Math.sin(i*7.3)), l:c - .3 - 0.05*Math.abs(Math.sin(i*3.1)), c}); }
out.brk = TCE.structure(up, 40).map(x => x.side+x.kind);
out.vp = TCE.vpNodes({bins:[1,2,9,2,1,1,6,1,1,1], lo:0, st:1, poc:2.5, vah:3, val:2}).map(x => x.src);
// ---- indicators, session levels, user rules ----
const D = 864e5, day0 = 20000*D;   // a Monday 00:00 UTC is day 20000+? (checked via wopen below)
const ir = []; for (let i = 0; i < 300; i++){ const t = day0 + i*3600e3, c = 20000 + 40*Math.sin(i/6) + (i >= 290 ? -(i - 289)*20 : 0); ir.push({t, o:c, h:c + 5, l:c - 5, c, v:10}); }
const I = TCE.indicators(ir), li = ir.length - 1;
out.vw = {last:I.vwap[li], u2:I.vwapU2[li] > I.vwap[li], l2:I.vwapL2[li] < I.vwap[li]};
const DL = TCE.dayLevels(ir); out.dl = {pdh:DL.pdh, pdl:DL.pdl, has:DL.dopen != null && DL.wopen != null};
// owner's Nasdaq idea: close < vwap - 25 pts (ps 1)
out.nq = TCE.rulesOk([{a:"close", op:"<", b:"vwap", off:-25}], I, li, 1);
out.nqNo = TCE.rulesOk([{a:"close", op:"<", b:"vwap", off:-25}], I, 100, 1) === (I.close[100] < I.vwap[100] - 25);
out.xa = (() => { const J = {a:[1, 3], b:[2, 2]}; return [TCE.rule({a:"a", op:"xa", b:"b"}, J, 1, 1), TCE.rule({a:"a", op:"xb", b:"b"}, J, 1, 1), TCE.rule({a:"a", op:">", b:"value", v:2.5}, J, 1, 1)]; })();
out.empty = TCE.rulesOk([], I, li, 1);
out.rsi = [TCE.rsi([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16], 14)[15], TCE.sma([1,2,3,4], 2)[3]];
const hourly = []; for (let i = 0; i < 48; i++) hourly.push({t:day0 + i*3600e3, o:i, h:i + 1, l:i - 1, c:i, v:1});
out.dl2 = TCE.dayLevels(hourly);
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
assert o["jTake"] == "TAKE" and o["jNews"] == "SKIP" and o["jOpen"] == "SKIP" and o["jOpp"] == "SKIP", o
assert o["jLimit"] == "WAIT" and o["jBias"], o
assert abs(o["cut"]["t"] - 103.4) < 1e-9 and o["cut"]["sec"] >= 1, o["cut"]       # obstacle at 103.5: target cut to 103.4, R:R 1.7 still ok
assert o["blk"]["rrPro"] is False and o["blk"]["con"], o["blk"]                       # obstacle at 100.6 cannot be cut around: R:R is not a reason FOR
assert o["down"] == "WAIT", o["down"]                                                  # strong case, heavy objection -> second look downgrades TAKE to WAIT
assert o["kz"] is False                                                                # "off-KZ" is not a kill zone
assert any(x.startswith("1") for x in o["brk"]), o["brk"]
assert o["vp"][:3] == ["POC", "VAH", "VAL"] and "HVN" in o["vp"], o["vp"]
assert o["vw"]["u2"] and o["vw"]["l2"], o["vw"]
assert o["nq"] is True and o["nqNo"] is True, (o["nq"], o["nqNo"])          # last bars fall ~200 pts under the session VWAP: the Nasdaq rule fires
assert o["xa"] == [True, False, True] and o["empty"] is False, o["xa"]
assert o["rsi"][0] == 100 and o["rsi"][1] == 3.5, o["rsi"]
assert o["dl2"]["pdh"] == 24 and o["dl2"]["pdl"] == -1 and o["dl2"]["dopen"] == 24, o["dl2"]   # hours 0-23 = yesterday (high 23+1, low 0-1), today opens at 24
print("ok tclass engine: %d events (%d long / %d short), median bounce %.2f, auto target %s pts" % (o["n"], o["longs"], o["shorts"], o["st"]["median"], c[0]["autoPts"]))
