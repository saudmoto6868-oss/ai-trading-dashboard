// MOCK-TESTED ONLY. Pass = 200 wheel events + 200 pointer moves fired inside one frame cost <= a few draw() calls and ONE localStorage view write.
// Run: NODE_PATH=$(npm root -g) node tests/browser/chart_scroll_draw_mock.js /tmp/ws.html   (build /tmp/ws.html as in chart_first_load_mock.js)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  const rows = () => { const now = Math.floor(Date.now() / 60000) * 60000, o = []; let c = 100; for (let i = 0; i < 300; i++) { c += Math.sin(i / 7); o.push([String(now - i * 60000), String(c), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); } return o; };
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? rows() : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3000);
  const res = await p.evaluate(async () => { const ch = Ws.panels.find(q => q.type === 'chart').chart; let draws = 0, saves = 0; const d0 = ch.draw.bind(ch), s0 = ch.saveView.bind(ch); ch.draw = () => { draws++; return d0(); }; ch.saveView = () => { saves++; return s0(); };
    const r = ch.cv.getBoundingClientRect(); for (let i = 0; i < 200; i++) { ch.cv.dispatchEvent(new WheelEvent('wheel', { deltaY: -40, clientX: r.left + 200, clientY: r.top + 200, bubbles: true, cancelable: true })); ch.cv.dispatchEvent(new PointerEvent('pointermove', { clientX: r.left + 200 + i, clientY: r.top + 200, bubbles: true })); }
    await new Promise(x => setTimeout(x, 500)); return { draws, saves }; });
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
