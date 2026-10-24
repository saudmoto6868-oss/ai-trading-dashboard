// MOCK-TESTED ONLY. Per timeframe: how long a window the order-flow column's AUTO mode shows, how many saved 1-minute buckets fall inside it and how many price rows they hold,
// with 3 h of synthetic recorded book history (and with only 5 min recorded). Old behaviour: window = live session only, max 10 min, whatever the timeframe.
// Run: NODE_PATH=$(npm root -g) node tests/browser/orderflow_tf_window_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 140)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 60000) * 60000, h = { 'access-control-allow-origin': '*' }, o = [];
    for (let i = 0; i < 300; i++) o.push([String(now - i * 60000), '100', '101', '99', '100', '1', '0', '0', '1']);
    return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(4000);
  const table = await p.evaluate(() => { const ch = Ws.panels.filter(q => q.type === 'chart' && q.chart)[1].chart, out = {}; const now = Date.now();
    const seed = mins => { ch.hmInit(); ch.hm.b.clear(); ch.hm.step = 10; for (let m = 0; m < mins; m++){ const o = { w: 60000, m: 60000, c: new Map() }; for (let k = 0; k < 40; k++) o.c.set(6000 + k, 1 + (k % 7)); ch.hm.b.set(Math.floor((now - m * 60000) / 60000) * 60000, o); } ch._hmOldN = -1; ch.flowSpan = 0; ch.st.of.hmm = 'fix'; };
    for (const rec of [180, 5]) { out['rec' + rec + 'min'] = {}; seed(rec); for (const tf of ['1m', '5m', '15m', '1H', '4H', '1D']) { ch.tf = tf; const w = ch.fspan(now); let nb = 0, rows = new Set(); ch.hm.b.forEach((o, t) => { if (t >= now - w) { nb++; o.c.forEach((q, k) => rows.add(k)); } }); out['rec' + rec + 'min'][tf] = { windowMin: +(w / 60000).toFixed(1), buckets: nb, rows: rows.size }; } }
    ch.tf = '4H'; seed(5); ch.paint(); return out; });
  console.log(JSON.stringify(table), 'errors', errs.length, errs[0] || ''); await b.close();
})();
