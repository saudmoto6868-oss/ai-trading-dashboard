// MOCK-TESTED ONLY (mocked OKX). The order-flow column header (title + "pulled / filled" key) does not run over itself in a narrow column: title shrinks, then the key is dropped.
// Run: NODE_PATH=$(npm root -g) node tests/browser/of_header_narrow_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100;
    for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2; o.push([String(now - (300 - i) * 3600000), String(c - 0.5), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: o }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2500);
  await p.evaluate(() => { Ws.panels.find(q => q.type === 'chart' && q.chart.data.length).toggleMax(); }); await p.waitForTimeout(800);
  const res = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length).chart; ch.colOn = true; ch.domOn = true; const out = {};
    const texts = []; const c = ch.ctx, orig = c.fillText.bind(c); c.fillText = (t, x, y, ...r) => { if (y === 10) texts.push([String(t), x]); return orig(t, x, y, ...r); };
    for (const w of [400, 150, 100]) { ch.colW = w; ch.paint(); texts.length = 0; ch.paint(); const gw = ch.cw() - 12; const hdr = texts.filter(t => /ORDER FLOW|OF ·|pulled|filled|أوردر/.test(t[0])); const title = hdr.find(t => /ORDER FLOW|OF ·|أوردر/.test(t[0])); const key = hdr.filter(t => /pulled|filled/.test(t[0]));
      c.font = "9px sans-serif"; out['w' + w] = { gw, title: title && title[0].slice(0, 40), tw: title ? Math.round(c.measureText(title[0]).width) : null, key: key.length }; }
    c.fillText = orig; return out; });
  const ok = res.w400.key === 2 && res.w400.tw <= res.w400.gw && res.w150.tw <= res.w150.gw && (res.w150.key === 0 || res.w150.tw + 100 <= res.w150.gw + 2) && res.w100.key === 0 && !errs.length;
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
