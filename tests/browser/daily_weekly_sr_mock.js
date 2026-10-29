// MOCK-TESTED ONLY. Pass = SR.compute finds the planted support / resistance (touches, strength, kind), the S/R button draws lines on a 1D chart (pixels) and opens the table; the 5m chart has no lines until switched on.
// Run: NODE_PATH=$(npm root -g) node tests/browser/daily_weekly_sr_mock.js /tmp/ws.html [/tmp/sr.png]
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 140)));
  // synthetic market: oscillates between 90 (support, touched 4x) and 110 (resistance, touched 4x) with the last close at 100
  const mk = (n, step) => { const now = Math.floor(Date.now() / step) * step, o = []; for (let i = 0; i < n; i++) { const ph = (n - 1 - i) % 20, hi = ph === 10 ? 110 : 104, lo = ph === 0 ? 90 : 96, cl = 100 + ((n - 1 - i) % 5 - 2); o.push([String(now - i * step), '100', String(hi), String(lo), String(cl), '5', '0', '0', '1']); } return o; };
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const h = { 'access-control-allow-origin': '*' };
    const step = /bar=1W/.test(u) ? 7 * 864e5 : /bar=1D/.test(u) ? 864e5 : 60000; return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? mk(200, step) : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(4000);
  const res = await p.evaluate(async () => { const rows = Array.from({ length: 200 }, (_, i) => { const ph = i % 20; return { t: i * 864e5, o: 100, h: ph === 10 ? 110 : 104, l: ph === 0 ? 90 : 96, c: 100 + (i % 5 - 2), v: 5 }; });
    const lv = SR.compute(rows), r = lv.find(x => Math.abs(x.p - 110) < 1), s = lv.find(x => Math.abs(x.p - 90) < 1); const out = { levels: lv.length, res110: r && { kind: r.kind, touches: r.touches, strength: r.strength }, sup90: s && { kind: s.kind, touches: s.touches, strength: s.strength } };
    const P = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0]; out.tf0 = P.state.tf; out.autoOn5m = P.srAuto();
    const btn = [...P.root.querySelectorAll('button')].find(x => x.textContent === 'S/R'); out.hasBtn = !!btn;
    P.state.tf = '1D'; out.autoOn1D = P.srAuto(); P.state.tf = out.tf0;
    btn.click(); await new Promise(r => setTimeout(r, 1500)); out.lit = P.chart.srOn; out.dataD = (P.chart.srData && P.chart.srData.D || []).length; out.popRows = document.querySelectorAll('.srpop table tr').length; out.popNote = /Not a signal|مش إشارة/.test((document.querySelector('.srpop') || {}).textContent || '');
    const off = document.querySelector('.srpop .srOff'); out.hasOffBtn = !!off; off && off.click(); await new Promise(r => setTimeout(r, 300)); out.offWorks = !P.chart.srOn && P.state.sr === false; out.popClosed = !document.querySelector('.srpop'); out.dataCleared = !P.chart.srData;
    return out; });
  if (process.argv[3]) await p.screenshot({ path: process.argv[3] });
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
