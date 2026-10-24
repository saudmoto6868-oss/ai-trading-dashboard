// MOCK-TESTED ONLY. Every drawing tool must create a drawing with a real mouse (pointer events) on the chart canvas. Run: NODE_PATH=$(npm root -g) node tests/browser/drawings_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 60000) * 60000, o = []; let c = 100; for (let i = 0; i < 300; i++) { c += Math.sin(i / 5) * 2; o.push([String(now - i * 60000), String(c), String(c + 2), String(c - 2), String(c + (i % 2 ? 1 : -1)), '10', '0', '0', '1']); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3500);
  const info = await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'chart'), ch = P.chart; const r = ch.cv.getBoundingClientRect(); return { x: r.left, y: r.top, S: ch.S, W: ch.W, H: ch.H, tool: ch.tool, draws: ch.draws.length, setTool: typeof ch.setTool }; });
  console.log('info', JSON.stringify(info));
  const res = {};
  for (const tool of ['trend', 'hline', 'rect', 'fib', 'brush']) {
    await p.evaluate(t => { const ch = Ws.panels.find(q => q.type === 'chart').chart; ch.draws.length = 0; ch.setTool(t); }, tool);
    const x0 = info.x + 200 * info.S, y0 = info.y + 120 * info.S;
    await p.mouse.move(x0, y0); await p.mouse.down(); for (let k = 1; k <= 6; k++) await p.mouse.move(x0 + k * 25, y0 + k * 12); await p.mouse.up();
    await p.mouse.click(x0 + 220, y0 + 100).catch(() => {}); await p.waitForTimeout(150);
    res[tool] = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart; return { n: ch.draws.length, tool: ch.tool }; });
  }
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
