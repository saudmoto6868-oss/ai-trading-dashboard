// MOCK-TESTED ONLY (no network). The 2.6 shape toggles: zn (zone box per setup), arw (dotted arrow to the box), trd (trade boxes, default on).
// Checks: defaults draw trade boxes and no zone / arrow; turning zn / arw on draws them (counted in chart._s26Stat); trd=0 hides trade boxes without errors.
// Candles: seeded random walk served by page.route (OKX shape). Build the page first:
//   python3 -c "import sys; sys.path.insert(0,'.'); from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w').write(b(['BTC-USDT-SWAP']))"
// Run: NODE_PATH=$(npm root -g) node tests/browser/two_six_shapes_mock.js /tmp/ws.html
const { chromium } = require('playwright');
function candles(n, endMs, bar) {
  let seed = 7, px = 3850; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647; const rows = [];
  for (let i = 0; i < n; i++) { const o = px, c = o + (rnd() - 0.5) * 6, h = Math.max(o, c) + rnd() * 2, l = Math.min(o, c) - rnd() * 2;
    rows.push([String(endMs - i * bar), o.toFixed(2), h.toFixed(2), l.toFixed(2), c.toFixed(2), '100', '0', '0', '1']); px = c; }
  return rows;
}
(async () => {
  const file = process.argv[2];
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue();
    if (u.includes('okx.com')) { const body = u.includes('/market/candles') ? { code: '0', msg: '', data: candles(320, Date.now(), 900000) } : { code: '0', msg: '', data: [] };
      return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'Access-Control-Allow-Origin': '*' }, body: JSON.stringify(body) }); }
    return r.abort(); });
  await p.goto('file://' + file); await p.waitForTimeout(3000);
  const draw = async (cfg) => { await p.evaluate(cfg => { const ch = Ws.panels.find(q => q.type === 'chart').chart; ch.s26On = true; Object.assign(ch.st.pos26, cfg); ch._s26 = null; ch._s26Stat = null; ch.draw(); }, cfg);
    await p.waitForTimeout(500);   // the chart paints on the next frame
    return p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart; return { n: ch.data.length, stat: ch._s26Stat ? { ...ch._s26Stat } : null, trd: ch.st.pos26.trd, zn: ch.st.pos26.zn, arw: ch.st.pos26.arw }; }); };
  const def = await draw({});
  const on = await draw({ zn: 1, arw: 1 });
  const off = await draw({ trd: 0, zn: 0, arw: 0 });
  const back = await draw({ trd: 1, zn: 0, arw: 0 });
  console.log(JSON.stringify({ def, on, off, back }));
  const pass = def.n >= 30 && def.stat && def.stat.zones === 0 && def.stat.arrows === 0 && def.trd === 1
    && on.stat.zones > 0 && on.stat.arrows > 0 && on.stat.zones === on.stat.arrows
    && off.trd === 0 && off.stat.trades === 0 && def.stat.trades > 0 && on.stat.trades > 0 && back.stat.trades > 0 && back.stat.zones === 0 && !errs.length;
  console.log('errors', errs.length, errs[0] || '', pass ? 'PASS' : 'FAIL');
  await b.close(); process.exit(pass ? 0 : 1);
})();
