// MOCK-TESTED ONLY. Pass = when the OKX ticker call starts failing (429) or a candle 429 pause is active, the watchlist rows keep the LAST GOOD price (never "–"), marked with a small delayed sign; fresh prices clear the sign.
// Run: NODE_PATH=$(npm root -g) node tests/browser/watchlist_last_good_price_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120))); let fail = false; const h = { 'access-control-allow-origin': '*' };
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    if (/market\/tickers/.test(u)) { if (fail) return r.fulfill({ status: 429, headers: h, body: '{}' }); const d = ['BTC-USDT', 'ETH-USDT'].map((id, i) => ({ instId: id, last: String(1000 * (i + 1) + 0.5), open24h: '1000', bidPx: '1', askPx: '1', high24h: '1', low24h: '1' })); return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: d }) }); }
    const now = Math.floor(Date.now() / 60000) * 60000, o = []; for (let i = 0; i < 100; i++) o.push([String(now - i * 60000), '100', '101', '99', '100', '1', '0', '0', '1']);
    return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(5000);
  await p.evaluate(() => { const w = Ws.panels.find(q => q.type === 'watch'); w.state.u = { cat: '__mine' }; w.wDraw(); }); await p.waitForTimeout(3500);
  const row = () => p.evaluate(() => { const w = Ws.panels.find(q => q.type === 'watch'), tr = [...w.root.querySelectorAll('tr.wr')].find(x => /BTC/.test(x.dataset.s)); return tr ? { price: tr.children[2].textContent.trim(), stale: !!tr.querySelector('span.m[title]') && /⏱/.test(tr.children[2].textContent) } : null; });
  const fresh = await row(); fail = true; await p.waitForTimeout(9000); const afterFail = await row(); fail = false; await p.waitForTimeout(9000); const recovered = await row();
  console.log(JSON.stringify({ fresh, afterFail, recovered }), 'errors', errs.length, errs[0] || ''); await b.close();
})();
