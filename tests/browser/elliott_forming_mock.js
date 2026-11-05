// MOCK-TESTED ONLY (hand-made pivots, fake canvas). Elliott "forming": the impulse in progress (waves 1-4 so far) is drawn dashed with the next wave number;
// a longer count cancelled by a rule (wave 2 past the start, wave 3 not past wave 1, wave 4 overlapping wave 1) falls back to the shorter one and says why.
// Run: NODE_PATH=$(npm root -g) node tests/browser/elliott_forming_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(1000);
  await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(1500);
  const r = await p.evaluate(() => {
    const ch = Ws.panels.find(q => q.type === 'chart').chart, mk = a => a.map(([k, pr], i) => ({ k, p: pr, i: 10 + i * 5 })), sum = f => f && { up: f.up, next: f.next, n: f.pts.length, broke: !!f.broke };
    const A = ch.ewForming(mk([['L', 100], ['H', 110], ['L', 104], ['H', 125]]), []);          // waves 1-3 fine -> next 4
    const B = ch.ewForming(mk([['L', 100], ['H', 110], ['L', 104], ['H', 108]]), []);          // wave 3 short of wave 1 -> falls back to 1-2, says why
    const C = ch.ewForming(mk([['L', 100], ['H', 110], ['L', 98]]), []);                       // wave 2 past the start -> nothing
    const D = ch.ewForming(mk([['L', 100], ['H', 110], ['L', 104], ['H', 125]]), [{ abc: [{ i: 1, p: 1 }], pts: [] }]);   // finished impulse still in its A-B-C -> nothing
    if (!ch.data.length) ch.data = Array.from({ length: 60 }, (_, i) => ({ t: i * 6e4, o: 100, h: 131, l: 99, c: 100, v: 1 }));
    ch._ewf = A; const out = [], ctx = new Proxy({}, { get: (t, k) => k === 'measureText' ? () => ({ width: 10 }) : k === 'fillText' ? s => out.push(String(s)) : (typeof t[k] === 'undefined' ? () => {} : t[k]), set: (t, k, v) => { t[k] = v; return true; } });
    ch.H = 600; ch.W = 900; ch.infoOpen = true; ch.paintEWforming(ctx, v => v);
    return { A: sum(A), B: sum(B), C: C, D: D, drawn: out };
  });
  const ok = r.A && r.A.next === 4 && r.A.up && r.A.n === 4 && !r.A.broke && r.B && r.B.next === 3 && r.B.broke && r.C === null && r.D === null && r.drawn.includes('3') && r.drawn.some(s => /forming|بيتكوّن/.test(s)) && errs.length === 0;
  console.log(JSON.stringify(r), 'errors', errs.length, ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
