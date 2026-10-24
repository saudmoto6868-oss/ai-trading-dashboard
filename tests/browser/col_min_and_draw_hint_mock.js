// MOCK-TESTED ONLY. (1) the candle area keeps >= 35 % of the chart even with a huge saved column width; (2) the default column is slimmer on 4H+ ; (3) a drawing click inside the column / pane is NOT silent: a hint is set and logged.
// Run: NODE_PATH=$(npm root -g) node tests/browser/col_min_and_draw_hint_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = [], logs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160))); p.on('console', m => { if (/\[XPIX\] drawing/.test(m.text())) logs.push(m.text().slice(0, 160)); });
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 60000) * 60000, o = []; let c = 100; for (let i = 0; i < 300; i++) { c += Math.sin(i / 5) * 2; o.push([String(now - i * 60000), String(c), String(c + 2), String(c - 2), String(c + (i % 2 ? 1 : -1)), '10', '0', '0', '1']); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3500);
  const res = await p.evaluate(async () => { const ch = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length).chart, out = {}; const wait = ms => new Promise(r => setTimeout(r, ms));
    ch.colOn = true; ch.colW = 99999; ch.resize(); out.candleShare = +(ch.PR/ch.W).toFixed(2);
    ch.colW = 0; ch.tf = '1H'; const w1 = ch.cw(); ch.tf = '4H'; const w4 = ch.cw(); ch.tf = '1D'; const w1d = ch.cw(); out.defaultCol = { h1: w1, h4: w4, d1: w1d, slimmerOnBig: w4 < w1 && w1d < w1 };
    ch.tf = '1H'; ch.setTool('trend'); const rc = ch.cv.getBoundingClientRect(); const x = rc.left + (ch.PR + 20)*ch.S, y = rc.top + 80*ch.S; ch.cv.dispatchEvent(new PointerEvent('pointerdown', { clientX: x, clientY: y, pointerId: 1, bubbles: true, button: 0 })); ch.cv.dispatchEvent(new PointerEvent('pointerup', { clientX: x, clientY: y, pointerId: 1, bubbles: true, button: 0 })); await wait(100);
    out.hintSet = !!(ch._hint && /Drawing|الرسم/.test(ch._hint.s)); out.draws = ch.draws.length; return out; });
  console.log(JSON.stringify(res), 'logged', logs.length, 'errors', errs.length, errs[0] || ''); await b.close();
})();
