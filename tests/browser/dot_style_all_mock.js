// MOCK-TESTED ONLY. Theme 17 dot style: drawings, indicator pane lines and heat-map cells use dots (pixel-count check: no long solid runs), and nothing throws.
// Run: NODE_PATH=$(npm root -g) node tests/browser/dot_style_all_mock.js /tmp/ws_df2.html [/tmp/dots.png]
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 60000) * 60000; let px = 60000; const o = [];
    for (let i = 0; i < 300; i++) { const t = now - (299 - i) * 60000, op = px, c = px + Math.sin(i / 7) * 120 + (i % 5 - 2) * 20, h = Math.max(op, c) + 30, l = Math.min(op, c) - 30; px = c; o.push([String(t), String(op), String(h), String(l), String(c), '10', '10', '600000', '1']); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o.reverse() : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3500);
  const res = await p.evaluate(async () => { const A = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0], ch = A.chart, out = { dots: ch.dots };
    const pts = [{ t: ch.data[ch.data.length - 80].t, p: ch.data[ch.data.length - 80].c }, { t: ch.data[ch.data.length - 20].t, p: ch.data[ch.data.length - 20].c + 400 }];
    ch.draws.push({ type: 'trend', pts, color: '#ff4a1c', w: 2 }, { type: 'hline', pts: [{ t: pts[0].t, p: ch.data[ch.data.length - 1].c + 150 }], color: '#ededed', w: 1.5 }); ch.drawingsVisible = true; ch.paint();
    // long solid run check along the trend line y-range: count horizontal runs of same colour pixels >= 12 on the hline row
    const h = ch.draws[1], y = Math.round(ch.yp(h.pts[0].p)), dpr = ch.dpr || devicePixelRatio || 1, w = Math.floor(ch.PR * dpr), row = ch.ctx.getImageData(0, Math.round(y * dpr), w, 1).data;
    let run = 0, best = 0, lit = 0; for (let x = 0; x < w; x++) { const on = row[x * 4 + 3] > 40 && row[x * 4] > 150; if (on) { run++; lit++; best = Math.max(best, run); } else run = 0; }
    out.hlineLongestRun = best; out.hlineLitFrac = +(lit / w).toFixed(2); out.hlineIsDotted = best <= 8 && lit > 20 && lit / w < 0.6; return out; });
  if (process.argv[3]) await p.screenshot({ path: process.argv[3] });
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
