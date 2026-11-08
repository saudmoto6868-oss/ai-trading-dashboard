// MOCK-TESTED ONLY (no network). Order-flow heat map row size (owner 2026-11-05: chunky ~2 USD blocks on gold after the wide Hyperliquid book of #208): bucketBook must size rows from the +-1 % around the price,
// not from the whole +-5 % book. Gold 4127, levels every 0.1 over +-200: step <= 0.25, buckets only inside +-1 %.
// Run: NODE_PATH=$(npm root -g) node tests/browser/of_heat_rows_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(800); await p.evaluate(() => { Ws.build(Ws.defaults()); }); await p.waitForTimeout(1200);
  const r = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart, bids = [], asks = []; for (let i = 0; i < 2000; i++) { bids.push({ p: 4126.9 - i * 0.1, q: 1 }); asks.push({ p: 4127.1 + i * 0.1, q: 1 }); }
    const out = ch.bucketBook(bids, asks), ps = out.map(x => x[0]); return { n: out.length, bk: ch.bk, lo: Math.min(...ps), hi: Math.max(...ps) }; });
  const ok = r.bk <= 0.25 && r.n > 100 && r.lo >= 4127 * 0.989 && r.hi <= 4127 * 1.011 && errs.length === 0;
  console.log(JSON.stringify(r), 'errors', errs.length, ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
