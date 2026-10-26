// MOCK-TESTED ONLY (mocked OKX + Hyperliquid, fixed candles ~4100). For HL:xyz:GOLD and KAU-USDT-SWAP on 15s, 1m, 5m, 1H, 4H, 1D: bars loaded, tf kept (or fallen back), price axis range vs candle range, lock per symbol.
// Run: NODE_PATH=$(npm root -g) node tests/browser/gold_chart_audit_mock.js /tmp/ws.html   (use a page built from a branch that has the per-symbol lock + sub-minute fallback, e.g. #130)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  const IV = { '1s': 1e3, '1m': 6e4, '3m': 18e4, '5m': 3e5, '15m': 9e5, '30m': 18e5, '1H': 36e5, '1h': 36e5, '2H': 72e5, '2h': 72e5, '4H': 144e5, '4h': 144e5, '12h': 432e5, '1D': 864e5, '1d': 864e5, '3d': 2592e5, '1w': 6048e5 }, h = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*' };
  const mk = (ms, n) => { const end = Math.floor(Date.now() / ms) * ms, o = []; for (let i = 0; i < n; i++) { const t = end - (n - 1 - i) * ms, c = 4100 + Math.sin(i / 9) * 30; o.push([t, c - 2, c + 5, c - 5, c]); } return o; };
  await p.route('**/*', async r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (r.request().method() === 'OPTIONS') return r.fulfill({ status: 204, headers: h });
    if (/hyperliquid\.xyz\/info/.test(u)) { const body = JSON.parse(r.request().postData() || '{}');
      if (body.type === 'candleSnapshot') { const ms = IV[body.req.interval] || 36e5; return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify(mk(ms, 300).map(x => ({ t: x[0], T: x[0] + ms - 1, s: 'xyz:GOLD', i: body.req.interval, o: String(x[1]), h: String(x[2]), l: String(x[3]), c: String(x[4]), v: '100', n: 5 }))) }); }
      if (body.type === 'metaAndAssetCtxs') return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify([{ universe: [{ name: 'xyz:GOLD' }] }, [{ midPx: '4100', dayNtlVlm: '9e8', openInterest: '1e6', prevDayPx: '4090' }]]) });
      return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: '[]' }); }
    if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const bar = (/bar=([^&]+)/.exec(u) || [])[1];
    if (/candles/.test(u)) { if (bar === '1s' && /KAU/.test(u)) return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '51000', msg: 'Parameter bar error', data: [] }) });   // assumption: no 1s candles for this swap
      const ms = IV[bar] || 6e4; return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: mk(ms, 300).reverse().map(x => [String(x[0]), String(x[1]), String(x[2]), String(x[3]), String(x[4]), '5', '0', '0', '1']) }) }); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3000);
  const out = []; for (const sym of ['HL:xyz:GOLD', 'KAU-USDT-SWAP']) for (const tf of ['15s', '1m', '5m', '1H', '4H', '1D']) {
    const r = await p.evaluate(async ([sym, tf]) => { const P = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0]; P.state.sym = sym; P.state.tf = tf; P.chart.tf = tf; P.chart.sym = sym; try { P.symSel && (P.symSel.value = sym); P.tfSel.value = tf; } catch (e) {} P.resub();
      await new Promise(z => setTimeout(z, 3500)); const c = P.chart, d = c.data, lo = Math.min(...d.map(k => k.l)), hi = Math.max(...d.map(k => k.h));
      return { bars: d.length, tfNow: P.state.tf, axisLo: Math.round(c._lo || 0), axisHi: Math.round(c._hi || 0), candleLo: Math.round(lo), candleHi: Math.round(hi), axisOk: d.length > 0 && c._lo <= lo + 1 && c._hi >= hi - 1 && c._hi < hi * 1.2 && c._lo > lo * 0.8, locked: !!c.lockR, msg: (P.msg.textContent || '').slice(0, 60) }; }, [sym, tf]);
    out.push([sym, tf, r]); }
  const lock = await p.evaluate(async () => { const P = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0]; P.state.sym = 'HL:xyz:GOLD'; P.state.tf = '1H'; P.chart.tf = '1H'; P.resub(); await new Promise(z => setTimeout(z, 2500)); P.chart.lockR = [4000, 4200]; (P.state.locks = P.state.locks || {})['HL:xyz:GOLD'] = P.chart.lockR;
    P.state.sym = 'KAU-USDT-SWAP'; P.resub(); await new Promise(z => setTimeout(z, 2500)); const kau = !!P.chart.lockR; P.state.sym = 'HL:xyz:GOLD'; P.resub(); await new Promise(z => setTimeout(z, 2500)); return { lockOnOtherSymbol: kau, lockRestoredOnReturn: !!P.chart.lockR, perSymbolStore: !!P.state.locks }; });
  out.forEach(([s, t, r]) => console.log(s, t, JSON.stringify(r))); console.log('LOCK', JSON.stringify(lock), 'errors', errs.length, errs[0] || ''); await b.close();
})();
