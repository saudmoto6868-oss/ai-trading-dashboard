// MOCK-TESTED ONLY (mocked Hyperliquid /info, no WebSocket = the worst case). Request load of two charts on the same Hyperliquid symbol, per minute: Hyperliquid limits the REQUEST WEIGHT per minute (~1200; a candle
// snapshot / recent-trades / meta call costs ~20), and four charts polling every 2 s alone used to exceed it (then everything shows "rate limit"). Counts the weight-20 calls over a window.
// Run: NODE_PATH=$(npm root -g) node tests/browser/hl_load_mock.js /tmp/ws.html [windowMs]
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  const cnt = {}, t0 = Date.now(); let start = 0;
  await p.route('**/*', async r => { const rq = r.request(), u = rq.url(); if (u.startsWith('file:')) return r.continue();
    if (/hyperliquid\.xyz\/info/.test(u)) { let body = {}; try { body = JSON.parse(rq.postData() || '{}'); } catch (e) {} const k = body.type + (body.req ? ':' + body.req.interval : '') ; if (start) cnt[k] = (cnt[k] || 0) + 1; let data = [];
      if (body.type === 'metaAndAssetCtxs') data = [{ universe: [{ name: 'xyz:GOLD' }] }, [{ midPx: '3900', dayNtlVlm: '1e9', openInterest: '1e5', prevDayPx: '3880' }]];
      else if (body.type === 'candleSnapshot') { const iv = { '1m': 6e4, '5m': 3e5, '15m': 9e5, '1h': 36e5, '4h': 144e5, '1d': 864e5, '1w': 6048e5 }[body.req.interval] || 36e5, end = body.req.endTime, n = Math.min(300, Math.ceil((end - body.req.startTime) / iv)); data = Array.from({ length: n }, (_, i) => ({ t: Math.floor(end / iv) * iv - (n - 1 - i) * iv, o: 3900 + i % 5, h: 3905 + i % 5, l: 3895 + i % 5, c: 3900 + i % 4, v: 10 })); }
      else if (body.type === 'l2Book') data = { time: Date.now(), levels: [Array.from({ length: 20 }, (_, i) => ({ px: String(3899 - i * .5), sz: '5', n: 2 })), Array.from({ length: 20 }, (_, i) => ({ px: String(3901 + i * .5), sz: '5', n: 2 }))] };
      return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(data) }); }
    if (/okx\.com/.test(u)) { const k = 'OKX:' + (u.split('/api/v5')[1] || '').split('?')[0]; if (start) cnt[k] = (cnt[k] || 0) + 1; return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: [] }) }); }
    return r.abort(); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2000);
  await p.evaluate(() => { const cs = Ws.panels.filter(q => q.type === 'chart'); const tfs = ['15m', '4h', '1h', '15m']; cs.forEach((P, i) => { P.state.sym = 'HL:xyz:GOLD'; P.state.tf = tfs[i % 4]; P.state.tfk = tfs[i % 4]; if (P.resub) P.resub(); }); });
  await p.waitForTimeout(8000); const types = await p.evaluate(() => Ws.panels.map(q => q.type + ':' + (q.state.sym || '') + ':' + (q.state.tf || '')).join(' | ')); console.log(types);
  start = Date.now(); await p.waitForTimeout(+process.argv[3] || 60000);
  const secs = (Date.now() - start) / 1000; console.log('window s', secs.toFixed(0)); Object.entries(cnt).sort((a, b) => b[1] - a[1]).forEach(([k, v]) => console.log(String(v).padStart(4), (v / secs * 60).toFixed(1).padStart(7) + '/min', k));
  const per = k => (cnt[k] || 0) / secs * 60, weight = per('candleSnapshot:15m') * 25 + per('candleSnapshot:4h') * 25 + per('candleSnapshot:1h') * 25 + per('recentTrades') * 20 + per('metaAndAssetCtxs') * 20 + per('l2Book') * 2;
  const ok = per('candleSnapshot:15m') <= 12 && per('recentTrades') <= 18 && per('metaAndAssetCtxs') <= 9 && weight < 900 && !errs.length;
  console.log('weight/min ~', weight.toFixed(0), 'errs', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
