// MOCK-TESTED ONLY (fake canvas, hand-made wave count). Elliott auto count: the Fib % labels must sit on the CORRECTIVE waves 2 and 4
// (retracement of the impulse leg before them), not on impulse legs. Pivots 100,110,104,125,117,130 -> wave 2 = 60.0 %, wave 4 = 38.1 %.
// Run: NODE_PATH=$(npm root -g) node tests/browser/elliott_fib_labels_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(1000);
  await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(1500);
  const labels = await p.evaluate(() => {
    const ch = Ws.panels.find(q => q.type === 'chart').chart, P = [100, 110, 104, 125, 117, 130];
    if (!ch.data.length) ch.data = Array.from({ length: 60 }, (_, i) => ({ t: i * 6e4, o: 100, h: 131, l: 99, c: 100, v: 1 }));
    ch.ewCount = () => [{ up: true, rec: true, abc: [], pts: P.map((v, i) => ({ i: 10 + i * 5, p: v, txt: i ? String(i) : '', up: i % 2 === 1 })) }];
    const out = [], ctx = new Proxy({}, { get: (t, k) => k === 'measureText' ? () => ({ width: 10 }) : k === 'fillText' ? (s) => out.push(String(s)) : (typeof t[k] === 'undefined' ? () => {} : t[k]), set: (t, k, v) => { t[k] = v; return true; } });
    ch.paintEWauto(ctx, v => v, 2); return out;
  });
  const pct = labels.filter(s => /%$/.test(s) && !/^OTE/.test(s));
  const ok = pct.length === 2 && pct.includes('60.0%') && pct.includes('38.1%') && errs.length === 0;
  console.log(JSON.stringify(pct), 'errors', errs.length, ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
