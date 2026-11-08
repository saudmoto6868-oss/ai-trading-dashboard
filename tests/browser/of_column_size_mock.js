// MOCK-TESTED ONLY (no data): default order-flow column width (colW = 0) by panel width and timeframe. Owner 2026-11-05: the column was too small.
// Run: NODE_PATH=$(npm root -g) node tests/browser/of_column_size_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(1000);
  await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(1200);
  const r = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart; ch.colOn = true; ch.colW = 0; const out = {};
    for (const [W, tf] of [[400, '1m'], [700, '1m'], [1000, '1m'], [1400, '1m'], [1000, '1D']]) { ch.W = W; ch.tf = tf; ch._axw = 62; out[W + tf] = { cw: ch.cw(), candlesPct: Math.round(100 * (W - 62 - ch.cw()) / W) }; } return out; });
  const ok = r['1000' + '1m'].cw >= 300 && r['1000' + '1D'].cw >= 200 && r['1000' + '1D'].cw < r['1000' + '1m'].cw && r['1400' + '1m'].cw >= 330 && r['700' + '1m'].cw >= 200 && r['400' + '1m'].cw >= 96 && Object.values(r).every(x => x.candlesPct >= 35) && errs.length === 0;
  console.log(JSON.stringify(r), 'errors', errs.length, ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
