// MOCK-TESTED ONLY. Forex / EGX / Tadawul symbols fed by the server-embedded Yahoo candles (Y:*): which chart timeframes return candles in the browser (yfOkx), which throw.
// Run: NODE_PATH=$(npm root -g) node tests/browser/yahoo_classes_tf_mock.js /tmp/ws_yf.html   (page built with yf={...} embedded candles, see tests/yahoo_classes_probe in the PR)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); return r.abort(); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1500); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2000);
  const res = await p.evaluate(async () => { const out = {}; for (const sym of ['Y:EURUSD=X', 'Y:COMI.CA', 'Y:2222.SR', 'Y:^CASE30']) { out[sym] = {}; for (const tf of ['1m', '5m', '15m', '30m', '1H', '2H', '4H', '6H', '1D', '1W']) { try { const r = await candlesTf(sym, tf, 'quick'); out[sym][tf] = r.length; } catch (e) { out[sym][tf] = 'ERR'; } } } return out; });
  Object.entries(res).forEach(([s, v]) => console.log(s, JSON.stringify(v))); console.log('errors', errs.length, errs[0] || ''); await b.close();
})();
