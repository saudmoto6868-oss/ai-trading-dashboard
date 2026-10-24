// MOCK-TESTED ONLY. Pass = when OKX book / trades start failing (HTTP 500), the DOM and Time & Sales panels keep showing the last good data for a while
// (no "Cannot reach OKX" at once), and the error finally shows (with the reason) only after many failed polls. Candle 429 pause must not block the book poll.
// Run: NODE_PATH=$(npm root -g) node tests/browser/flow_panels_keep_last_good_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  let fail = false, bookCalls = 0; const J = d => ({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: d }) });
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    const now = Math.floor(Date.now() / 60000) * 60000;
    if (/candles/.test(u)) { const o = []; for (let i = 0; i < 100; i++) o.push([String(now - (99 - i) * 60000), '60000', '60100', '59900', '60050', '10', '10', '600000', '1']); return r.fulfill(J(o.reverse())); }
    if (/market\/books/.test(u)) { bookCalls++; if (fail) return r.fulfill({ status: 500, headers: { 'access-control-allow-origin': '*' }, body: '{}' }); const lv = (b0, s) => Array.from({ length: 60 }, (_, i) => [String(b0 + s * i), String(1 + i % 5), '0', '1']); return r.fulfill(J([{ bids: lv(60000, -1), asks: lv(60001, 1), ts: String(Date.now()) }])); }
    if (/market\/trades/.test(u)) { if (fail) return r.fulfill({ status: 500, headers: { 'access-control-allow-origin': '*' }, body: '{}' }); return r.fulfill(J(Array.from({ length: 30 }, (_, i) => ({ tradeId: String(1000 + i), ts: String(Date.now() - i * 800), px: String(60000 + i), sz: '0.5', side: i % 2 ? 'buy' : 'sell' })))); }
    return r.fulfill(J([])); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000);
  await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(4000);
  const st = () => p.evaluate(() => { const o = {}; Ws.panels.filter(q => q.type === 'dom' || q.type === 'tape').forEach(q => { o[q.type] = { err: !!q.root.querySelector('.err'), rows: q.root.querySelectorAll('tr').length, txt: (q.root.querySelector('.err') || {}).textContent || '' }; }); return o; });
  const okS = await st(); fail = true; await p.waitForTimeout(5500); const early = await st(); await p.waitForTimeout(14000); const late = await st();
  console.log(JSON.stringify({ okS, afterFewFails: early, afterManyFails: late }), 'errors', errs.length, errs[0] || ''); await b.close();
})();
