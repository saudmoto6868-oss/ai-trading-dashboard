// MOCK-TESTED ONLY. Pass = while prices change every tick the watchlist keeps the SAME symbol-cell DOM nodes (icons not reloaded) and prices still update.
// Run: NODE_PATH=$(npm root -g) node tests/browser/watchlist_patch_mock.js /tmp/ws.html   (build /tmp/ws.html as in chart_first_load_mock.js)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120))); let n = 0;
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const h = { 'access-control-allow-origin': '*' };
    if (/market\/tickers/.test(u)) { n++; const d = ['BTC-USDT', 'ETH-USDT'].map((id, i) => ({ instId: id, last: String(100 * (i + 1) + n * 0.37), open24h: '100', bidPx: '1', askPx: '1', high24h: '1', low24h: '1' })); return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: d }) }); }
    const now = Math.floor(Date.now() / 60000) * 60000, o = []; for (let i = 0; i < 100; i++) o.push([String(now - i * 60000), '100', '101', '99', '100', '1', '0', '0', '1']);
    return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(5000);
  await p.evaluate(() => { const w = Ws.panels.find(q => q.type === 'watch'); w.state.u = { cat: '__mine' }; w.wDraw(); }); await p.waitForTimeout(3500);
    const r1 = await p.evaluate(() => { const c = document.querySelector('table.wt tr.wr td:nth-child(2)'); if (c) c.__mark = 1; const t = document.querySelector('table.wt tr.wr td:nth-child(3)'); return { rows: document.querySelectorAll('table.wt tr.wr').length, price: t && t.textContent }; });
  await p.waitForTimeout(9000);
  const r2 = await p.evaluate(() => { const c = document.querySelector('table.wt tr.wr td:nth-child(2)'), t = document.querySelector('table.wt tr.wr td:nth-child(3)'); return { sameNode: !!(c && c.__mark), price: t && t.textContent }; });
  console.log(JSON.stringify({ r1, r2, tickerReqs: n }), 'errors', errs.length, errs[0] || ''); await b.close();
})();
