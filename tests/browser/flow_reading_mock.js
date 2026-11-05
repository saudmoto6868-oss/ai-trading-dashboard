// MOCK-TESTED ONLY (mocked OKX). FLOW READING in the order-flow column (ported from feat/orderflow-reading): OFF by default, draws a numbered reading when switched on and the column / plot are big enough,
// stays off in a small panel, and a hand-made reading does not throw. Run: NODE_PATH=$(npm root -g) node tests/browser/flow_reading_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100;
    for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2; o.push([String(now - (300 - i) * 3600000), String(c - 0.5), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2500);
  const res = await p.evaluate(async () => { const P = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length), ch = P.chart; P.toggleMax(); await new Promise(r => setTimeout(r, 700)); ch.colOn = true; ch.colWide = 0; ch.domOn = true; ch.colW = 340;
    const mid = ch.data[ch.data.length - 1].c, out = { defaultOff: ch.readOn === true ? false : true };
    ch._rd = { lines: [{ en: 'A bid wall of 120 was pulled 14 s ago, 0.3% below the price', ar: 'حائط شراء 120 اتسحب من 14 ث', sev: 3, side: 'bid', p: mid - 0.3 }, { en: 'Tape agrees with the book: 62% of the last minute was buying', ar: 'الشريط متفق', sev: 2 }], zones: [{ p: mid + 0.2, lo: mid + 0.15, hi: mid + 0.25, strength: 3 }], tilt: { dir: 1, label: { en: 'buyers lead', ar: 'المشترين' } } };
    const texts = []; const c = ch.ctx, orig = c.fillText.bind(c); c.fillText = (t, ...r) => { texts.push(String(t)); return orig(t, ...r); };
    ch.readOn = false; ch.paint(); out.offDraws = texts.some(t => /FLOW READING/.test(t)); texts.length = 0;
    ch.readOn = true; ch.paint(); out.onDraws = texts.some(t => /FLOW READING/.test(t)); out.sentence = texts.some(t => /bid wall of 120/.test(t));
    texts.length = 0; ch.colW = 120; ch.paint(); out.narrowDraws = texts.some(t => /FLOW READING/.test(t));
    c.fillText = orig; return out; });
  const ok = res.defaultOff && !res.offDraws && res.onDraws && res.sentence && !res.narrowDraws && !errs.length;
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
