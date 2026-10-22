// Run by tests/test_flow_read.py:  node tests/flow_read_cases.js <path to a file containing the FLOWREAD block>
const fs = require("fs");
const src = fs.readFileSync(process.argv[2], "utf8"), a = src.indexOf("/* FLOWREAD:BEGIN"), b = src.indexOf("/* FLOWREAD:END */");
if (a < 0 || b < 0) { console.error("FLOWREAD block not found"); process.exit(2); }
const FlowRead = new Function(src.slice(a, b) + "; return FlowRead;")();
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
console.log("ok flow_read " + n + " checks");
