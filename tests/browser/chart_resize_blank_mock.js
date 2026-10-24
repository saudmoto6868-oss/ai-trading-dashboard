// MOCK-TESTED ONLY. Pass = right after the chart's own ResizeObserver callback the canvas is NOT blank (a blank canvas at that point is shown for one frame = a blink).
// Run: NODE_PATH=$(npm root -g) node tests/browser/chart_resize_blank_mock.js /tmp/ws.html   (build /tmp/ws.html as in chart_first_load_mock.js)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 60000) * 60000, o = []; let c = 100; for (let i = 0; i < 300; i++) { c += Math.sin(i / 7); o.push([String(now - i * 60000), String(c), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3500);
  const res = await p.evaluate(async () => { const ch = Ws.panels.find(q => q.type === 'chart').chart; let blank = 0, seen = 0;
    const ro = new ResizeObserver(() => { seen++; const d = ch.ctx.getImageData(0, 0, ch.cv.width, ch.cv.height).data; let any = 0; for (let i = 3; i < d.length; i += 4) if (d[i]) { any = 1; break; } if (!any) blank++; }); ro.observe(ch.host);
    for (let k = 0; k < 6; k++) { ch.host.style.width = (ch.host.clientWidth - 17 - k) + 'px'; await new Promise(r => setTimeout(r, 120)); } return { roCallbacks: seen, blankAfterResize: blank }; });
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
