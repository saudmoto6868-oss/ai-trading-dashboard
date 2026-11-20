// MOCK-TESTED ONLY. Pass = with Elliott, Gann, Harmonic and liquidity ON, the chart paints with no page errors, and the new
// Elliott pieces answer: count, shape label, sub-count, frame box rows (1Y..1m), X key toggles the expected-zone box.
// Build: python3 -c "from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w',encoding='utf8').write(b(['BTC-USDT','ETH-USDT']))"
// Run:   NODE_PATH=$(npm root -g) node tests/browser/elliott_features_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  // zig-zag closes: legs of 6-14 % so every swing size finds pivots
  const rows = (n, end, step) => { const o = []; for (let i = 0; i < n; i++) { const t = end - i * step, k = n - i;
    const c = 100 + 12 * Math.sin(k / 9) + 5 * Math.sin(k / 3.3) + k * 0.03; o.push([String(t), String(c), String(c + 0.8), String(c - 0.8), String(c), '10', '10', '10', '1']); } return o; };
  await p.route('**/*', async r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    const h = { 'access-control-allow-origin': '*' }; if (!/candles/.test(u)) return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: '{"code":"0","data":[]}' });
    const bar = new URL(u).searchParams.get('bar') || '1H', stepMs = ({ '1m': 6e4, '5m': 3e5, '15m': 9e5, '1H': 36e5, '4H': 144e5, '1D': 864e5, '1Dutc': 864e5, '1W': 6048e5, '1Wutc': 6048e5, '1M': 2592e6, '1Mutc': 2592e6 })[bar] || 36e5;
    const after = +(new URL(u).searchParams.get('after')) || Math.floor(Date.now() / stepMs) * stepMs + stepMs;
    return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: /history/.test(u) ? [] : rows(300, after - stepMs, stepMs) }) }); });
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(1200);
  await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3500);
  const out = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart' && q.chart && q.chart.data.length).chart;
    ch.ewOn = true; ch.gannOn = true; ch.harmOn = true; ch.liqOn = true; ch.draw();
    const list = ch.ewCount(), sub = ch.ewCount(1.0);
    return { bars: ch.data.length, count: list.length, top: list[0] ? list[0].pts.length + '/' + list[0].abc.length : '-', sub: sub.length,
             shape: ch.ewShapeLabel(), forming: !!ch._ewf, zz: ch.ewZZ().length, projOn: CandleChart.projOn }; });
  console.log('state', JSON.stringify(out));
  await p.waitForTimeout(4000);   // let the frame box fetch its frames
  const box = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart' && q.chart && q.chart.data.length).chart; ch.draw();
    const st = ch._ewMtf || {}; return Object.keys(st).filter(k => st[k] && st[k].v).map(k => k.split('|')[1] + ':' + st[k].v.state); });
  console.log('frame rows', box.length, JSON.stringify(box.slice(0, 9)));
  await p.keyboard.press('x'); const off = await p.evaluate(() => CandleChart.projOn); await p.keyboard.press('x'); const on = await p.evaluate(() => CandleChart.projOn);
  console.log('X toggles', off === false && on === true ? 'ok' : 'FAIL', 'errors', errs.length, errs.slice(0, 3).join(' | '));
  await b.close(); process.exit(errs.length || off !== false || on !== true ? 1 : 0);
})();
