// MOCK-TESTED ONLY. Pass = after one normal visit, a reload paints the charts from the browser cache within ~2 s even while the OKX candle request is stalled for 8 s; the real answer then replaces it.
// (second-level charts like 15s are not cached: their candles go stale in seconds.)
// Run: NODE_PATH=$(npm root -g) node tests/browser/chart_cached_first_paint_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120))); let slow = false;
  await p.route('**/*', async r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const h = { 'access-control-allow-origin': '*' };
    if (/candles/.test(u)) { if (slow) await new Promise(z => setTimeout(z, 8000)); const now = Math.floor(Date.now() / 60000) * 60000, o = []; for (let i = 0; i < 300; i++) o.push([String(now - i * 60000), '100', '101', '99', String(100 + (i % 7)), '1', '0', '0', '1']); return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: o }) }); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(4500);
  const n0 = await p.evaluate(() => Ws.panels.filter(q => q.type === 'chart' && q.chart && !/s$/.test(q.state.tf || '')).map(q => q.chart.data.length)); const cached = await p.evaluate(() => Object.keys(localStorage).filter(k => /_cc\|/.test(k)).length);
  slow = true; await p.reload(); await p.waitForTimeout(2500);
  const n1 = await p.evaluate(() => Ws.panels.filter(q => q.type === 'chart' && q.chart && !/s$/.test(q.state.tf || '')).map(q => q.chart.data.length));
  await p.waitForTimeout(9000); const n2 = await p.evaluate(() => Ws.panels.filter(q => q.type === 'chart' && q.chart && !/s$/.test(q.state.tf || '')).map(q => q.chart.data.length));
  console.log(JSON.stringify({ firstVisit: n0, cachedEntries: cached, after2sStalledReload: n1, afterAnswer: n2, instant: n1.every(x => x >= 100) }), 'errors', errs.length, errs[0] || ''); await b.close();
})();
