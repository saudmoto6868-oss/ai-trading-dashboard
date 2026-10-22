// Run by tests/test_flow_read.py:  node tests/flow_read_cases.js <path to a file containing the FLOWREAD block>
const fs = require("fs");
const src = fs.readFileSync(process.argv[2], "utf8"), a = src.indexOf("/* FLOWREAD:BEGIN"), b = src.indexOf("/* FLOWREAD:END */");
if (a < 0 || b < 0) { console.error("FLOWREAD block not found"); process.exit(2); }
const { FlowRead, ZoneLog } = new Function(src.slice(a, b) + "; return {FlowRead, ZoneLog};")();
let n = 0; const ok = (c, m) => { n++; if (!c) { console.error("FAIL: " + m); process.exit(1); } };
const lad = (mid, step, k, over = {}) => { const bids = [], asks = []; for (let i = 0; i < k; i++) { bids.push({ p: +(mid - step / 2 - i * step).toFixed(6), q: over["b" + i] ?? 10 }); asks.push({ p: +(mid + step / 2 + i * step).toFixed(6), q: over["a" + i] ?? 10 }); } return { bids, asks }; };
const snap = (t, mid, over) => Object.assign({ t }, lad(mid, 1, 30, over));
// 1) a new big wall inside the already-visible ladder is PLACED; the first sight of a wall is not an event when it just entered the window
let st = FlowRead.newState(); FlowRead.update(st, snap(1000, 100), []);
let e = FlowRead.update(st, snap(2000, 100, { a5: 100 }), []);
ok(e.length === 1 && e[0].kind === "PLACED" && e[0].side === "ask" && Math.abs(e[0].p - 105.5) < 1e-9, "placed inside visible window");
// level enters the window because price moved up by 40: not PLACED
st = FlowRead.newState(); FlowRead.update(st, snap(1000, 100), []);
const moved = lad(140, 1, 30); moved.asks[0].q = 100; moved.asks[0].p = 141 + 0; // a wall at the very top of a ladder that was NOT covered before only if outside [lo,hi]
const far = { t: 2000, bids: moved.bids, asks: moved.asks };
e = FlowRead.update(st, far, []); ok(!e.some(x => x.kind === "PLACED"), "a level that entered the window is not a placed order");
// 2) PULLED: wall vanishes and nothing printed at its price
st = FlowRead.newState(); FlowRead.update(st, snap(1000, 100), []); FlowRead.update(st, snap(2000, 100, { a5: 100 }), []);
e = FlowRead.update(st, snap(3000, 100), []);
ok(e.length === 1 && e[0].kind === "PULLED" && e[0].age === 1000 && e[0].dist > 0.05 - 1e-9 && e[0].dist < 0.07, "pulled with age and distance");
// 3) FILLED: wall vanishes and prints hit that price for >= half of it
st = FlowRead.newState(); FlowRead.update(st, snap(1000, 100), []); FlowRead.update(st, snap(2000, 100, { a5: 100 }), []);
e = FlowRead.update(st, snap(3000, 100), [{ t: 2500, p: 105.5, q: 70, side: "Buy" }]);
ok(e.length === 1 && e[0].kind === "FILLED" && e[0].ratio >= 0.7, "filled when prints covered it");
// 4) REGRESSION: old logic called it FILLED whenever price had traded through the level at ANY time in the sample. Prints from BEFORE the previous snapshot must not count.
st = FlowRead.newState(); FlowRead.update(st, snap(1000, 100), []); FlowRead.update(st, snap(2000, 100, { a5: 100 }), [{ t: 500, p: 105.5, q: 500, side: "Buy" }]);
e = FlowRead.update(st, snap(3000, 100), [{ t: 500, p: 105.5, q: 500, side: "Buy" }]);
ok(e.length === 1 && e[0].kind === "PULLED", "old prints at the same price do not make it a fill");
// 5) REFILL: wall is hit hard and its size is back
st = FlowRead.newState(); FlowRead.update(st, snap(1000, 100), []); FlowRead.update(st, snap(2000, 100, { b3: 100 }), []);
e = FlowRead.update(st, snap(14000, 100, { b3: 95 }), [{ t: 13000, p: 96.5, q: 60, side: "Sell" }]);
ok(e.some(x => x.kind === "REFILL" && x.side === "bid"), "refill when hit and size back (price of bid3 = 99.5-3 = 96.5)");
// 6) a wall that only dips under the big bar because the median changed is not an event
st = FlowRead.newState(); FlowRead.update(st, snap(1000, 100), []); FlowRead.update(st, snap(2000, 100, { a5: 100 }), []);
const heavy = snap(3000, 100, { a5: 90 }); heavy.bids.forEach(x => x.q = 40); heavy.asks.forEach((x, i) => { if (i !== 5) x.q = 40; });
e = FlowRead.update(st, heavy, []); ok(e.length === 0, "median change is not a pull / fill");
// 7) read(): pulled-near wall is the top line; stale book is flagged first; quiet fallback
st = FlowRead.newState(); FlowRead.update(st, snap(1000, 100), []); FlowRead.update(st, snap(2000, 100, { a1: 100 }), []);
const ev3 = FlowRead.update(st, snap(12000, 100), []);   // rested 10 s, 1.5 away from mid: dist = 2.5/100 -> not <= 0.002, so use the 'near' branch only if approaching
let R = FlowRead.read(st, { now: 12500, snap: snap(12000, 100), trades: [], events: st.ev });
ok(R.lines.length >= 1 && R.tilt && R.tilt.label.ar, "read returns lines and a tilt");
const nearEv = [{ t: 12000, kind: "PULLED", side: "ask", p: 100.4, q: 500, age: 30000, dist: 0.0006, near: true }];
R = FlowRead.read(st, { now: 12500, snap: snap(12000, 100), trades: [], events: nearEv });
ok(R.lines[0].sev === 4 && /pulled without trading/.test(R.lines[0].en) && /اتسحب/.test(R.lines[0].ar) && R.lines[0].p === 100.4, "pulled-near line first");
R = FlowRead.read(st, { now: 30000, snap: snap(12000, 100), trades: [], events: [] });
ok(R.lines[0].sev === 5 && /old/.test(R.lines[0].en), "stale data flagged on top");
R = FlowRead.read(FlowRead.newState(), { now: 5000, snap: snap(5000, 100), trades: [], events: [] });
ok(R.lines.length === 1 && R.lines[0].sev === 0 && R.tilt.dir === 0, "quiet fallback");
// 8) tilt: book + tape + limits all buying -> dir 1; book buying but tape selling -> mixed label
const buyBook = snap(5000, 100); buyBook.bids.forEach(x => x.q = 30);
const prints = Array.from({ length: 5 }, (_, i) => ({ t: 4000 + i, p: 100, q: 5, side: "Buy" }));
R = FlowRead.read(FlowRead.newState(), { now: 5000, snap: buyBook, trades: prints, events: [{ t: 4900, kind: "PLACED", side: "bid", p: 99, q: 100 }] });
ok(R.tilt.dir === 1 && /buying/.test(R.tilt.label.en), "all three lean buying");
R = FlowRead.read(FlowRead.newState(), { now: 5000, snap: buyBook, trades: prints.map(x => ({ ...x, side: "Sell" })), events: [] });
ok(/disagree/.test(R.tilt.label.en) && R.lines.some(l => /disagree/.test(l.en)), "book vs tape disagreement is reported");
// 9) robustness: empty / crossed books never throw
ok(FlowRead.update(FlowRead.newState(), { t: 1, bids: [], asks: [] }, []).length === 0, "empty book");
ok(FlowRead.update(FlowRead.newState(), { t: 1, bids: [{ p: 101, q: 1 }], asks: [{ p: 100, q: 1 }] }, []).length === 0, "crossed book");
ok(FlowRead.read(FlowRead.newState(), { now: 1, snap: null, trades: [], events: [] }).lines.length >= 0, "no snapshot");

// 10) heat level: defaults unchanged, liquidity filter, colour ceiling, brightness, contrast
const near = (a, b) => Math.abs(a - b) < 1e-9;
ok(near(FlowRead.level(0.25, 1, { dom: 1 }, .5), 0.5), "default level = sqrt");
ok(FlowRead.level(0.25, 1, { dom: 1, hmCut: 30 }, .5) === 0 && FlowRead.level(0.6, 1, { dom: 1, hmCut: 30 }, 1) > 0, "liquidity filter hides small cells");
ok(near(FlowRead.level(0.5, 1, { dom: 1, hmTop: 50 }, 1), 1), "colour ceiling: half of the biggest already brightest");
ok(near(FlowRead.level(0.25, 1, { dom: 1, hmBri: 0.5 }, 1), 0.125), "brightness scales");
ok(FlowRead.level(0.04, 1, { dom: 1, hmGam: 0.3 }, .5) > FlowRead.level(0.04, 1, { dom: 1 }, .5), "lower contrast exponent shows faint cells more");
ok(FlowRead.level(5, 1, { dom: 1 }, .5) === 1 && FlowRead.level(0, 0, { dom: 1 }, .5) === 0, "clamped, no NaN on empty window");
// 11) confluence zone: wall that rested + refill + absorption + big print all at one price -> 4 of 4; a lone wall -> no zone
const snapT = (t, over) => Object.assign({ t }, lad(100, 0.05, 30, over));   // bid3 = 99.825
st = FlowRead.newState(); FlowRead.update(st, snapT(1000), []); FlowRead.update(st, snapT(2000, { b3: 100 }), []);
FlowRead.update(st, snapT(39000, { b3: 100 }), []);
const small = Array.from({ length: 8 }, (_, i) => ({ t: 38000 + i * 100, p: 100, q: 1, side: "Buy" }));
const bigPrint = { t: 39800, p: 99.825, q: 50, side: "Sell" };
const zev = [{ t: 39000, kind: "REFILL", side: "bid", p: 99.825, q: 60, refills: 2, age: 37000 }, { t: 39500, kind: "ABSORB", side: "bid", p: 99.8, q: 80 }];
R = FlowRead.read(st, { now: 40000, snap: snapT(39000, { b3: 100 }), trades: small.concat([bigPrint]), events: zev });
ok(R.zones.length === 1 && R.zones[0].strength === 4 && Math.abs(R.zones[0].p - 99.82) < 0.05, "4-source confluence zone");
ok(R.lines[0].zone && R.lines[0].sev === 4.5 && /Confluence/.test(R.lines[0].en) && /منطقة التقاء/.test(R.lines[0].ar) && /4 of 4/.test(R.lines[0].en), "zone line is first and says 4 of 4");
ok(!R.lines.some(l => !l.zone && l.p != null && Math.abs(l.p - 99.82) < 0.1), "ingredient lines inside the zone are folded into it");
R = FlowRead.read(st, { now: 40000, snap: snapT(39000, { b3: 100 }), trades: small, events: [] });
ok(R.zones.length === 0, "a lone wall is not a zone");
R = FlowRead.read(st, { now: 40000, snap: snapT(39000, { b3: 100 }), trades: small, events: [{ t: 39500, kind: "ABSORB", side: "bid", p: 99.80, q: 80 }] });
ok(R.zones.length === 1 && R.zones[0].strength === 2 && R.lines.some(l => l.sev === 3.5 && /2 of 4/.test(l.en)), "two sources = a weaker zone");
ok(FlowRead.read(st, { now: 40000, snap: snapT(39000, { b3: 100 }), trades: small, events: [{ t: 39500, kind: "ABSORB", side: "bid", p: 95, q: 80 }] }).zones.length === 0, "far apart sources do not merge");

// 12) zone forward test: hold / break / control / dedupe / planted effect
const Z = (p, strength = 3) => ({ p, lo: p, hi: p, strength, srcs: ["book", "limits", "tape"].slice(0, strength) });
let zl = { recs: [] };
let r1 = ZoneLog.add(zl, Z(99.9), 100, 1000);               // price came from above (mid 100 > 99.9), control level at 100.1
ok(r1 && r1.from === 1 && Math.abs(r1.ctl - 100.1) < 1e-9, "zone logged with the side price came from and the mirrored control");
ok(ZoneLog.add(zl, Z(99.9), 100, 2000) === null, "same zone within 5 min is not logged twice");
ok(ZoneLog.add(zl, Z(99.9), 100, 1000 + 400000) !== null, "after 5 min it can be logged again");
zl = { recs: [] }; r1 = ZoneLog.add(zl, Z(99.9), 100, 0);
[[100, 1000], [99.95, 2000], [99.9, 3000], [99.96, 4000], [99.97, 5000]].forEach(([m, t]) => ZoneLog.step(zl, m, t));
ok(r1.z.touchT === 1 && r1.z.out === "hold", "touch then 6+ bp back where it came from = hold");
ok(r1.c.out === null || r1.c.out === "break", "control level (100.1) was never touched as support: no hold");
zl = { recs: [] }; r1 = ZoneLog.add(zl, Z(99.9), 100, 0);
[[99.95, 1000], [99.9, 2000], [99.85, 3000], [99.8, 4000]].forEach(([m, t]) => ZoneLog.step(zl, m, t));
ok(r1.z.out === "break", "touch then 6+ bp through = break");
// planted effect: zones always hold, controls never -> the paired t is large and positive; random coin flips -> no effect
zl = { recs: [] }; let tt = 0;
for (let i = 0; i < 60; i++) { const r = ZoneLog.add(zl, Z(99.9 - i * 0.01 * 0), 100, tt); tt += 400000; r.z.touchT = 1; r.z.out = "hold"; r.c.touchT = 1; r.c.out = i % 4 === 0 ? "hold" : "break"; }
let S = ZoneLog.stats(zl); ok(S.pair === 60 && S.z.hold === 60 && S.diff > 0.5 && S.t > 3, "planted zone effect is detected (diff " + S.diff + ", t " + S.t + ")");
zl = { recs: [] }; tt = 0; let seed = 5; const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
for (let i = 0; i < 400; i++) { const r = ZoneLog.add(zl, Z(99.9), 100, tt); tt += 400000; r.z.touchT = 1; r.z.out = rnd() < .5 ? "hold" : "break"; r.c.touchT = 1; r.c.out = rnd() < .5 ? "hold" : "break"; }
S = ZoneLog.stats(zl); ok(S.pair >= 250 && Math.abs(S.t) < 3, "coin flips: no effect (t " + S.t + ")");
ok(ZoneLog.stats({ recs: [] }).n === 0 && ZoneLog.stats({ recs: [] }).t === 0, "empty log");
console.log("ok flow_read " + n + " checks");
