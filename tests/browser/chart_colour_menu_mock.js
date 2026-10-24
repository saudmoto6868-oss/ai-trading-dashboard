// MOCK-TESTED ONLY. Pass = the 🎨 menu changes ONE chart's colours (pixel check + saved in the panel state), the other chart and the global theme (TH) stay untouched, Reset goes back.
// Run: NODE_PATH=$(npm root -g) node tests/browser/chart_colour_menu_mock.js /tmp/ws.html [/tmp/colours.png]
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 60000) * 60000, o = []; let c = 100; for (let i = 0; i < 300; i++) { c += Math.sin(i / 5) * 2; o.push([String(now - i * 60000), String(c), String(c + 2), String(c - 2), String(c + (i % 2 ? 1 : -1)), '10', '0', '0', '1']); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3500);
  const res = await p.evaluate(async () => { const cs = Ws.panels.filter(q => q.type === 'chart' && q.chart), A = cs[0], B = cs[1], wait = ms => new Promise(r => setTimeout(r, ms));
    const px = q => { const ch = q.chart; ch.paint(); const d = ch.ctx.getImageData(2, 2, 1, 1).data; return [d[0], d[1], d[2]].join(','); }; const th0 = JSON.stringify(TH), before = px(A), beforeB = px(B);
    const btn = [...A.root.querySelectorAll('button')].find(x => x.textContent === '🎨'); btn.click(); await wait(50); const sel = document.querySelector('.stpop select'); sel.value = '4'; sel.dispatchEvent(new Event('change')); await wait(100);
    const out = { hasButton: !!btn, bgBefore: before, bgNeon: px(A), otherChartSame: px(B) === beforeB, savedPal: !!(A.state.pal && A.state.pal.up === '#00ff9d'), globalThemeUntouched: JSON.stringify(TH) === th0 };
    document.querySelectorAll('.stpop').forEach(x => x.remove()); A.chart.pal = null; out.bgAfterReset = px(A) === before; return out; });
  if (process.argv[3]) { await p.evaluate(() => { const A = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0]; A.chart.pal = { up: '#00ff9d', dn: '#ff3d71', bg: '#05070d', grid: '#101522' }; A.chart.paint(); }); await p.waitForTimeout(200); await p.screenshot({ path: process.argv[3] }); }
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
