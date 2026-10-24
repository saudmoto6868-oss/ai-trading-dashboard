// MOCK-TESTED ONLY (real Chromium, fake OKX, synthetic order book + prints). Owner rule (ChatGPT record, decision 2/4): NOTHING from order flow (heat map, bubbles, DOM bars, dots) is drawn over the candle area, with the column open or closed.
// Method: paint the same chart with and without order-flow data and compare the pixels of the candle area (x < PR, y < PB): they must be identical.
// Run: NODE_PATH=$(npm root -g) node tests/browser/orderflow_nothing_over_candles_mock.js /tmp/ws.html [screenshot_prefix]
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 60000) * 60000, o = []; let c = 100; for (let i = 0; i < 300; i++) { c += Math.sin(i / 5) * 2; o.push([String(now - i * 60000), String(c), String(c + 2), String(c - 2), String(c + (i % 2 ? 1 : -1)), '10', '0', '0', '1']); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3500);
  const res = await p.evaluate(async () => { const P = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length), ch = P.chart, out = {}; ch.st.vol.delta = 0; ch.volOn = true;
    const hashPlot = () => { ch.paint(); const k = ch.S || 1, dpr = window.devicePixelRatio || 1, w = Math.max(1, Math.floor(ch.PR*k*dpr)), h = Math.max(1, Math.floor(ch.PB*k*dpr)); const d = ch.ctx.getImageData(0, 0, w, h).data; let hh = 0; for (let i = 0; i < d.length; i += 13) hh = (hh*31 + d[i] + d[i+1]*3 + d[i+2]*7) | 0; return hh; };
    const last = ch.data[ch.data.length-1], mid = last.c; const feed = () => { const now = Date.now(); for (let i = 0; i < 400; i++) ch.fpAdd({ t: now - i*500, p: +(mid + Math.sin(i)*3).toFixed(2), q: 1 + (i % 9), side: i % 2 ? 'Buy' : 'Sell', tier: i % 40 === 0 ? 'whale' : 'normal' });
      for (let k = 0; k < 6; k++) { const bids = [], asks = []; for (let i = 0; i < 40; i++){ bids.push({ p: +(mid - 0.05 - i*0.1).toFixed(2), q: 1 + ((i*7 + k) % 11) + (i === 8 ? 40 : 0) }); asks.push({ p: +(mid + 0.05 + i*0.1).toFixed(2), q: 1 + ((i*5 + k) % 13) + (i === 12 ? 40 : 0) }); } ch.domAdd({ bids, asks, deep: null, t: Date.now() }); } };
    const modes = { dom: { domOn: true, bubOn: false, dotOn: false }, bub: { domOn: false, bubOn: true, dotOn: false }, dots3: { domOn: true, bubOn: true, dotOn: true } };
    for (const open of [false, true]) { ch.colOn = open; ch.resize(); for (const [name, m] of Object.entries(modes)) { Object.assign(ch, m); ch.fp.clear(); ch.bub = []; ch.flowT = []; ch.flowB = []; ch.flowE = []; ch.hm = null; ch.paint(); const empty = hashPlot();
        feed(); ch.paint(); const withData = hashPlot(); out[(open ? 'open_' : 'closed_') + name] = { same: empty === withData, empty, withData }; } }
    return out; });
  const bad = Object.entries(res).filter(([, v]) => !v.same).map(([k]) => k); console.log(JSON.stringify(Object.fromEntries(Object.entries(res).map(([k, v]) => [k, v.same]))), 'DRAWN_OVER_CANDLES:', JSON.stringify(bad), 'errors', errs.length, errs[0] || '');
  if (process.argv[3]) { await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length).chart; ch.colOn = true; ch.resize(); ch.paint(); }); await p.waitForTimeout(300); await p.screenshot({ path: process.argv[3] + '_open.png' }); await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length).chart; ch.colOn = false; ch.resize(); ch.paint(); }); await p.waitForTimeout(300); await p.screenshot({ path: process.argv[3] + '_closed.png' }); }
  await b.close();
})();
