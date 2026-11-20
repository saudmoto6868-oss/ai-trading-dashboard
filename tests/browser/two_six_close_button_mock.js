// MOCK-TESTED ONLY (no network). Checks the × button on the 2.6 info table: it is drawn when the table shows,
// a real mouse click on it turns the "Info tab" setting off (pos26.info = 0), the table then disappears and the setting is saved.
// Candles come from a seeded random walk served by page.route (OKX shape, newest first). Run:
//   NODE_PATH=$(npm root -g) node tests/browser/two_six_close_button_mock.js /abs/path/to/modules/workspace_app.html
const { chromium } = require('playwright');

function candles(n, endMs, bar) {            // OKX /market/candles rows: [ts, o, h, l, c, vol, ...] as strings, newest first
  let seed = 7, px = 3850;
  const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const rows = [];
  for (let i = 0; i < n; i++) {
    const o = px, c = o + (rnd() - 0.5) * 6, h = Math.max(o, c) + rnd() * 2, l = Math.min(o, c) - rnd() * 2;
    rows.push([String(endMs - i * bar), o.toFixed(2), h.toFixed(2), l.toFixed(2), c.toFixed(2), '100', '0', '0', '1']);
    px = c;
  }
  return rows;
}

(async () => {
  const file = process.argv[2];
  if (!file) { console.log('usage: node two_six_close_button_mock.js <abs path to workspace_app.html>'); process.exit(2); }
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await p.route('**/*', r => {
    const u = r.request().url();
    if (u.startsWith('file:')) return r.continue();
    if (u.includes('okx.com')) {
      const body = u.includes('/market/candles') ? { code: '0', msg: '', data: candles(320, Date.now(), 900000) } : { code: '0', msg: '', data: [] };
      return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'Access-Control-Allow-Origin': '*' }, body: JSON.stringify(body) });
    }
    return r.abort();
  });
  await p.goto('file://' + file);
  await p.waitForTimeout(3000);

  // turn the 2.6 overlay on the first chart and draw it (same flag the settings menu sets)
  await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart; ch.s26On = true; ch.draw(); });
  await p.waitForTimeout(800);

  const before = await p.evaluate(() => {
    const ch = Ws.panels.find(q => q.type === 'chart').chart;
    return { n: ch.data.length, info: ch.st.pos26.info, x: ch._s26X ? { ...ch._s26X } : null,
             cv: (() => { const r = ch.cv.getBoundingClientRect(); return { left: r.left, top: r.top }; })() };
  });
  const okDrawn = before.n >= 30 && before.info && before.x && before.x.w > 0;

  if (okDrawn) {
    await p.mouse.click(before.cv.left + before.x.x + before.x.w / 2, before.cv.top + before.x.y + before.x.h / 2);
    await p.waitForTimeout(600);
  }
  const after = await p.evaluate(() => {
    const pn = Ws.panels.find(q => q.type === 'chart'), ch = pn.chart;
    ch.draw();
    return { info: ch.st.pos26.info, stateInfo: pn.state.st && pn.state.st.pos26 ? pn.state.st.pos26.info : null, x: ch._s26X };
  });
  const okHidden = after.info === 0 && after.stateInfo === 0 && after.x === null;

  console.log(JSON.stringify({ before, after }));
  const pass = okDrawn && okHidden && !errs.length;
  console.log('errors', errs.length, errs[0] || '', pass ? 'PASS' : 'FAIL');
  await b.close();
  process.exit(pass ? 0 : 1);
})();
