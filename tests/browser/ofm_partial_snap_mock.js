// MOCK-TESTED ONLY (hand-made books). OFM.snap(b, prev): a PARTIAL book (only the near levels came because the coarse ladders timed out) keeps the far walls of the previous full snapshot; without prev they would be an
// empty (black) stripe in the order-flow map. Run: NODE_PATH=$(npm root -g) node tests/browser/ofm_partial_snap_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(800); await p.evaluate(() => { Ws.build(Ws.defaults()); }); await p.waitForTimeout(1000);
  const r = await p.evaluate(() => { const mid = 4127, full = { bids: [], asks: [] }, near = { bids: [], asks: [] };
    for (let i = 0; i < 400; i++) { const d = 0.1 + i * 1.5; full.bids.push({ p: mid - d, q: 2 }); full.asks.push({ p: mid + d, q: 2 }); if (i < 20) { near.bids.push({ p: mid - 0.1 - i * 0.1, q: 1 }); near.asks.push({ p: mid + 0.1 + i * 0.1, q: 1 }); } }
    const f = OFM.snap({ deep: full }), part = OFM.snap({ deep: near }), kept = OFM.snap({ deep: near }, f), idx = (s, price) => Math.floor((price - s.base)/s.step);
    const far = mid + 200, nf = f.arr[idx(f, far)], np = part.arr[idx(part, far)], nk = kept.arr[idx(kept, far)];
    return { fCov: f.cov, partCov: part.cov, keptCov: kept.cov, nf, np, nk, carried: !!kept.carried, nearOk: kept.arr[idx(kept, mid + 1)] > 0 }; });
  const ok = r.nf > 0 && r.np === 0 && r.nk === r.nf && r.carried && r.keptCov === r.fCov && r.nearOk && errs.length === 0;
  console.log(JSON.stringify(r), 'errors', errs.length, ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
