"""Persistent footprint store (FPS in workspace_app.html): the real function text runs in node against an in-memory fake of IndexedDB.
Guards: ranges join/lookup, per-minute per-price sums, candles rebuilt from minutes (+ 'partial' outside known ranges), commits are idempotent across tabs
(no print counted twice), retention prunes old minutes, a failing store switches recording off without throwing. Skipped when node is not installed."""
import json
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = open(os.path.join(ROOT, "modules", "workspace_app.html"), encoding="utf-8").read()

FAKE_IDB = r"""
const DB = new Map(); let FAIL = false;
const keyOf = k => String(k);
class Req { constructor(){ this.onsuccess = null; this.result = undefined; } fire(v){ this.result = v; setTimeout(() => this.onsuccess && this.onsuccess({target: this}), 0); } }
globalThis.IDBKeyRange = {bound: (lo, hi) => ({lo, hi})};
function mkTx(){ const tx = {oncomplete: null, onerror: null, onabort: null, pending: 0}; const done = () => setTimeout(() => { if (FAIL) tx.onerror && tx.onerror(); else tx.oncomplete && tx.oncomplete(); }, 5);
  tx.objectStore = () => ({
    get: k => { const r = new Req(); r.fire(DB.has(keyOf(k)) ? JSON.parse(JSON.stringify(DB.get(keyOf(k)))) : undefined); return r; },
    put: (v, k) => { DB.set(keyOf(k), JSON.parse(JSON.stringify(v))); return new Req(); },
    delete: rg => { for (const k of [...DB.keys()]) if (k >= rg.lo && k <= rg.hi) DB.delete(k); return new Req(); },
    openCursor: rg => { const r = new Req(); const ks = [...DB.keys()].filter(k => k >= rg.lo && k <= rg.hi).sort(); let i = 0;
      const step = () => { if (i >= ks.length) { r.result = null; setTimeout(() => r.onsuccess && r.onsuccess({target: {result: null}}), 0); return; }
        const k = ks[i++]; const c = {key: k, value: DB.get(k), continue: () => setTimeout(step, 0)}; setTimeout(() => r.onsuccess && r.onsuccess({target: {result: c}}), 0); };
      setTimeout(step, 0); return r; }});
  setTimeout(done, 20); return tx; }
globalThis.indexedDB = {open: () => { const r = {onsuccess: null, onerror: null, onupgradeneeded: null}; r.result = {transaction: () => mkTx(), createObjectStore(){}, close(){}}; setTimeout(() => { r.onupgradeneeded && r.onupgradeneeded(); r.onsuccess && r.onsuccess(); }, 0); return r; }};
globalThis.__fail = v => { FAIL = v; }; globalThis.__db = DB;
"""


def _run(body):
    node = shutil.which("node")
    if not node:
        return None
    i = H.index("/* FPS-BEGIN"); j = H.index("/* FPS-END */")
    core = H[i:j]
    js = FAKE_IDB + core + "\n(async () => {\n" + body + "\n})().catch(e => { console.error(e.stack); process.exit(1); });"
    r = subprocess.run([node, "-e", js], capture_output=True)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    return json.loads(r.stdout.decode("utf-8"))


def test_ranges():
    out = _run("""
let c = FPS.join([], 10, 20); c = FPS.join(c, 30, 40); const a = JSON.stringify(c); c = FPS.join(c, 20, 30); const b = JSON.stringify(c); c = FPS.join(c, 5, 8);
console.log(JSON.stringify({a, b, c, inA: !!FPS.span([[10, 20]], 20), edge: !!FPS.span([[10, 20]], 10), has: FPS.has([[10, 40]], 12, 30), hasNot: FPS.has([[10, 20], [30, 40]], 12, 35), empty: FPS.join([[1, 2]], 5, 5)}));""")
    if out is None:
        return
    assert out["a"] == "[[10,20],[30,40]]" and out["b"] == "[[10,40]]"      # touching ranges merge
    assert out["c"] == [[5, 8], [10, 40]]
    assert out["inA"] is True and out["edge"] is False                       # a range is (from, to]
    assert out["has"] is True and out["hasNot"] is False                     # a stretch across a gap is not known
    assert out["empty"] == [[1, 2]]


def test_minutes_and_candles():
    out = _run("""
const T0 = 1700000100000 - (1700000100000 % 300000);   // a 5m boundary
const tr = [[T0 + 1000, 100, 1, "Buy"], [T0 + 2000, 100, 2, "Sell"], [T0 + 61000, 101, 3, "Buy"], [T0 + 301000, 100, 4, "Buy"]];
const g = FPS.group(tr); const mins = new Map([...g].map(([k, m]) => [k, FPS.flat(m)]));
const ch = {data: [{t: T0}, {t: T0 + 300000}], fp: new Map()}; FPS.fold(mins, ch, 300000, [[T0 - 1, T0 + 600000]], 0);
const c0 = ch.fp.get(T0), c1 = ch.fp.get(T0 + 300000);
const ch2 = {data: [{t: T0}, {t: T0 + 300000}], fp: new Map()}; FPS.fold(mins, ch2, 300000, [[T0 + 60000, T0 + 600000]], 0);
console.log(JSON.stringify({k: [...g.keys()].length, b0: c0.b, s0: c0.s, p0: [...c0.px.entries()], b1: c1.b, part0: c0.part, part1: c1.part, part0b: ch2.fp.get(T0).part,
  merged: FPS.merge([100, 1, 1], new Map([[100, [2, 3]], [105, [1, 0]]])), sub: FPS.fold(mins, {data: [{t: T0}], fp: new Map()}, 5000, [], 0)}));""")
    if out is None:
        return
    assert out["k"] == 3
    assert out["b0"] == 4 and out["s0"] == 2                                  # minutes 0 and 1 land in the first 5m candle
    assert dict((k, v) for k, v in out["p0"]) == {100: {"b": 1, "s": 2}, 101: {"b": 3, "s": 0}}
    assert out["b1"] == 4 and out["part0"] is False and out["part1"] is False
    assert out["part0b"] is True                                              # known range starts inside the candle: it says partial
    assert out["merged"] == [100, 3, 4, 105, 1, 0]
    assert out["sub"] == 0                                                     # candles under 1m cannot be built from minutes


def test_commit_is_idempotent_and_loads_back():
    out = _run("""
const N = Date.now(), M = Math.floor(N/60000)*60000 - 10*60000;
const tr = []; for (let i = 0; i < 50; i++) tr.push([M + i*7000, 100 + (i % 3), 1, i % 2 ? "Buy" : "Sell"]);
const to1 = M + 49*7000;
const ok1 = await FPS.commit("X", tr, M - 1, to1);
const ok2 = await FPS.commit("X", tr, M - 1, to1);                 // the same prints again (a second tab / panel): must not double
const more = tr.slice(); more.push([to1 + 1000, 100, 5, "Buy"]);
const ok3 = await FPS.commit("X", more, M - 1, to1 + 1000);        // overlaps the known range: only the new print is added
const o = await FPS.load("X", M - 3600000);
let b = 0, s = 0; o.mins.forEach(a => { for (let j = 0; j + 2 < a.length; j += 3){ b += a[j+1]; s += a[j+2]; } });
const empty = await FPS.load("NOPE", 0);
console.log(JSON.stringify({ok1, ok2, ok3, cov: o.cov, b, s, to1, M, empty: empty.cov.length + "|" + empty.mins.size}));""")
    if out is None:
        return
    assert out["ok1"] and out["ok2"] and out["ok3"]
    assert out["cov"] == [[out["M"] - 1, out["to1"] + 1000]]
    assert out["b"] == 25 + 5 and out["s"] == 25                              # 25 buys + 25 sells counted ONCE, plus the one new buy of 5
    assert out["empty"] == "0|0"


def test_retention_and_failing_store():
    out = _run("""
const N = Date.now(), old = N - FPS.KEEP - 3*3600000, newer = N - 600000;
await FPS.commit("Y", [[old, 1, 1, "Buy"]], old - 1, old + 1);
await FPS.commit("Y", [[newer, 2, 1, "Sell"]], newer - 1, newer + 1);
const o = await FPS.load("Y", 0);
__fail(true); const bad = await FPS.commit("Y", [[N, 3, 1, "Buy"]], N - 1, N + 1); const off = FPS.off; const after = await FPS.load("Y", 0);
console.log(JSON.stringify({minutes: [...o.mins.keys()].length, cov: o.cov.length, bad, off, after}));""")
    if out is None:
        return
    assert out["minutes"] == 1 and out["cov"] == 1                            # the minute and range older than the retention were pruned
    assert out["bad"] is False and out["off"] is True and out["after"] is None


def test_wired_into_the_panel():
    for k in ("FPS.span(fcov, r.t)", "this.fpInit", "this.fpSync", "fcommit(r.from, r.to)", "FPS.mark(ch", "Footprint recorded without gaps since", "_fpRdy"):
        assert k in H, k
    assert "if (seenF.has(x.tradeId) || +x.ts < d[0].t) return;" not in H     # the old catch-up loop is gone


def test_book_history_gaps():
    out = _run("""
const M = 60000, T = 1700000000000, tol = 4*M;
const solid = [0, 1, 2, 3, 4].map(i => [T + i*M, M]);                           // 5 minutes, no hole
const holey = solid.concat([[T + 30*M, M], [T + 31*M, M]]);                    // app closed for 25 min, then recorded again
const old5 = [[T, 5*M], [T + 5*M, 5*M], [T + 10*M, 5*M]];                      // compacted 5-min buckets are touching
console.log(JSON.stringify({a: FPS.cover(solid, T + 5*M, tol), b: FPS.cover(holey, T + 32*M, tol), c: FPS.cover(holey, T + 60*M, tol), d: FPS.cover(old5, T + 15*M, tol), e: FPS.cover([], T, tol)}));""")
    if out is None:
        return
    T = 1700000000000
    assert out["a"] == {"oldest": T, "runFrom": T, "gaps": 0, "gapMs": 0}
    assert out["b"]["gaps"] == 1 and out["b"]["runFrom"] == T + 30 * 60000 and out["b"]["gapMs"] == 25 * 60000   # one hole, the unbroken run starts after it
    assert out["c"]["gaps"] == 2 and out["c"]["runFrom"] == 0                  # nothing recorded for the last 28 min: no unbroken run to now
    assert out["d"]["gaps"] == 0
    assert out["e"]["oldest"] == 0


def test_book_history_merge_and_store():
    out = _run("""
const T = 1700000000000, cut = T - 1000;
const H = {step: 0.1, b: new Map([[T, {w: 60000, m: 1, c: new Map([[5, 10], [6, 3]])}]])};
const o = {step: 0.1, b: {[T]: {w: 60000, m: 1, c: [[5, 4], [6, 9], [7, 2]]}, [T + 60000]: {w: 60000, m: 1, c: [[5, 1]]}, [T - 99999]: {w: 60000, m: 1, c: [[5, 1]]}}};
const n = FPS.hmMerge(H, o, cut);
const diff = FPS.hmMerge({step: 0.2, b: new Map([[T, {w: 1, m: 1, c: new Map()}]])}, o, cut);
const empty = {step: 0, b: new Map()}; FPS.hmMerge(empty, o, cut);
const ok = await FPS.putHm("Z", o), back = await FPS.getHm("Z"), none = await FPS.getHm("NOPE");
__fail(true); const bad = await FPS.putHm("Z", o);
console.log(JSON.stringify({n, cells: [...H.b.get(T).c.entries()], buckets: H.b.size, diff, emptyStep: empty.step, emptyN: empty.b.size, ok, same: JSON.stringify(back) === JSON.stringify(o), none, bad}));""")
    if out is None:
        return
    assert out["n"] == 2 and out["buckets"] == 2                               # the bucket older than the cut is ignored, the new minute is added
    assert dict((k, v) for k, v in out["cells"]) == {5: 10, 6: 9, 7: 2}         # larger size wins per cell, new rows are added
    assert out["diff"] == 0                                                     # a different price grid is never mixed in
    assert out["emptyStep"] == 0.1 and out["emptyN"] == 2                       # an empty history adopts the saved grid
    assert out["ok"] is True and out["same"] is True and out["none"] is None
    assert out["bad"] is False                                                  # a failing store reports it: the caller keeps the localStorage copy


def test_new_candle_is_not_flagged_and_rate_limit_pauses():
    out = _run("""
const T = 1700000100000 - (1700000100000 % 60000), ms = 60000;
const ch = {data: [], fp: new Map([[T - ms, {}], [T, {}], [T + ms, {}]])};
FPS.mark(ch, ms, [[T - 1, T + 30000]], T + 30000);     // verified up to half-way through candle T; candle T+1m has not started
console.log(JSON.stringify({prev: ch.fp.get(T - ms).part, cur: ch.fp.get(T).part, next: ch.fp.get(T + ms).part}));""")
    if out is None:
        return
    assert out["prev"] is True       # before the known range starts: partial
    assert out["cur"] is False       # the forming candle is complete up to the verified end
    assert out["next"] is False      # a candle that just opened has nothing missing yet
    assert "this._fpBackoff = Date.now() + 60000" in H and "Date.now() < (this._fpBackoff || 0)" in H
