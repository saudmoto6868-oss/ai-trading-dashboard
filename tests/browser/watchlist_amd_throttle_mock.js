// MOCK-TESTED ONLY. Pass = with 30 symbols in "My list" the AMD column fetches at most 12 candle series in the first pass, spaced >= ~300 ms, and stops the pass on a 429.
// Run: NODE_PATH=$(npm root -g) node tests/browser/watchlist_amd_throttle_mock.js /tmp/ws.html   (build /tmp/ws.html as in chart_first_load_mock.js)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120))); const amd = [];
  const names = Array.from({ length: 30 }, (_, i) => 'C' + i + '-USDT');
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const h = { 'access-control-allow-origin': '*' };
    if (/market\/tickers/.test(u)) return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: names.map(id => ({ instId: id, last: '100', open24h: '100', bidPx: '1', askPx: '1', high24h: '1', low24h: '1' })) }) });
    const now = Math.floor(Date.now() / 60000) * 60000, o = []; for (let i = 0; i < 100; i++) o.push([String(now - i * 60000), '100', '101', '99', '100', '1', '0', '0', '1']);
    if (/candles\?instId=C\d+-USDT&bar=1H&limit=60/.test(u)) amd.push(Date.now());
    return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200); await p.evaluate(n => { SYMS.length = 0; n.forEach(x => SYMS.push(x)); Ws.build(Ws.defaults()); Ws.save(); }, names); await p.waitForTimeout(1500);
  await p.evaluate(() => { const w = Ws.panels.find(q => q.type === 'watch'); w.state.u = { cat: '__mine' }; w.wDraw(); }); await p.waitForTimeout(9000);
  const gaps = amd.slice(1).map((t, i) => t - amd[i]); console.log(amd.map(t => t - amd[0]).join(","));console.log(JSON.stringify({ amdReqsIn9s: amd.length, minGapMs: gaps.length ? Math.min(...gaps) : null }), 'errors', errs.length, errs[0] || ''); await b.close();
})();
