// MOCK-TESTED ONLY. Pass = after a drag-pan + zoom + price-scale drag the view is auto-saved (no wheel needed) and a page reload opens with the same zoom, position and price scale.
// Run: NODE_PATH=$(npm root -g) node tests/browser/chart_view_autosave_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 60000) * 60000; let px = 60000; const o = [];
    for (let i = 0; i < 300; i++) { const t = now - (299 - i) * 60000, op = px, c = px + Math.sin(i / 7) * 120, h = Math.max(op, c) + 30, l = Math.min(op, c) - 30; px = c; o.push([String(t), String(op), String(h), String(l), String(c), '10', '10', '600000', '1']); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o.reverse() : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3500);
  const info = () => p.evaluate(() => { const A = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0], c = A.chart, r = c.cv.getBoundingClientRect(); return { bw: +c.bw.toFixed(3), back: +((c.data.length - 1) - c.r).toFixed(2), lock: !!c.lockR, lockR: c.lockR && c.lockR.map(v => Math.round(v)), x: r.left + r.width * .4, y: r.top + r.height * .4 }; });
  const a0 = await info();
  await p.mouse.move(a0.x, a0.y); await p.mouse.down(); await p.mouse.move(a0.x + 120, a0.y + 40, { steps: 8 }); await p.mouse.up();   // pan + vertical drag (price scale -> manual)
  await p.mouse.move(a0.x, a0.y); await p.mouse.wheel(0, -300); await p.waitForTimeout(1500);
  const a1 = await info(); const stored = await p.evaluate(() => Object.keys(localStorage).filter(k => /_view\|/.test(k)).map(k => JSON.parse(localStorage.getItem(k))));
  await p.reload(); await p.waitForTimeout(4500); const a2 = await info();
  const res = { moved: a1.back !== a0.back || a1.bw !== a0.bw, savedViews: stored.length, same: Math.abs(a2.bw - a1.bw) < 0.01 && Math.abs(a2.back - a1.back) < 1, lockKept: a2.lock === a1.lock, before: a0, afterAction: a1, afterReload: a2 };
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
