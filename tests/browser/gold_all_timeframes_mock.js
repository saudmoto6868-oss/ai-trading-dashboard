// MOCK-TESTED ONLY. HL:xyz:GOLD through hlOkx -> candlesTf for EVERY chart timeframe with a mocked Hyperliquid (fixed candles): which timeframes return candles, which throw.
// Run: NODE_PATH=$(npm root -g) node tests/browser/gold_all_timeframes_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 140))); const asked = new Set();
  await p.route('**/*', async r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); const h = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*' };
    if (r.request().method() === 'OPTIONS') return r.fulfill({ status: 204, headers: h });
    if (/hyperliquid\.xyz\/info/.test(u)) { const body = JSON.parse(r.request().postData() || '{}');
      if (body.type === 'candleSnapshot') { asked.add(body.req.interval); const ms = { '1m': 6e4, '3m': 18e4, '5m': 3e5, '15m': 9e5, '30m': 18e5, '1h': 36e5, '2h': 72e5, '4h': 144e5, '8h': 288e5, '12h': 432e5, '1d': 864e5, '3d': 2592e5, '1w': 6048e5, '1M': 2592e6 }[body.req.interval] || 36e5, end = Math.floor(Date.now() / ms) * ms, o = [];
        for (let i = 0; i < 300; i++) { const t = end - (299 - i) * ms, c = 4100 + Math.sin(i / 9) * 30; o.push({ t, T: t + ms - 1, s: 'xyz:GOLD', i: body.req.interval, o: String(c - 2), c: String(c), h: String(c + 5), l: String(c - 5), v: '100', n: 10 }); }
        return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify(o) }); }
      if (body.type === 'metaAndAssetCtxs') return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify([{ universe: [{ name: 'xyz:GOLD' }] }, [{ midPx: '4100', dayNtlVlm: '9e8', openInterest: '1e6', prevDayPx: '4090' }]]) });
      return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: '[]' }); }
    if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1500); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2500);
  const res = await p.evaluate(async () => { const tfs = ['1m', '3m', '5m', '13m', '15m', '30m', '1H', '2H', '3H', '4H', '6H', '7H', '8H', '12H', '1D', '3D', '1W', '1M'], out = {};
    for (const tf of tfs) { try { const rows = await candlesTf('HL:xyz:GOLD', tf, 'quick'); out[tf] = rows.length; } catch (e) { out[tf] = 'ERR ' + String(e.message || e).slice(0, 70); } } return out; });
  console.log(JSON.stringify(res), 'intervals asked', [...asked].join(','), 'errors', errs.length, errs[0] || ''); await b.close();
})();
