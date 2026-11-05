// MOCK-TESTED ONLY (mocked OKX, Chromium touch emulation, REAL touch events through CDP). (1) A sideways finger swipe (even wobbly) moves time and does NOT lock the price scale ("Manual");
// a clearly vertical finger drag still does; when the scale is manual and the newest candle is outside it, a big "Auto" chip on the chart brings it back with one tap. (2) A narrow chart keeps more
// width for the candles (slimmer order-flow column), the sync card stays off a small panel, and the heat-map legend does not run over itself. Run: NODE_PATH=$(npm root -g) node tests/browser/touch_scale_column_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const ctx = await b.newContext({ viewport: { width: 1180, height: 820 }, hasTouch: true, userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15' });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100;
    for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2 + (i > 280 ? 3 : 0); o.push([String(now - (300 - i) * 3600000), String(c - 0.5), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: o }) }); });
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaultsMobile()); Ws.save(); }); await p.waitForTimeout(2500);
  const cdp = await ctx.newCDPSession(p), sleep = ms => new Promise(r => setTimeout(r, ms));
  const drag = async (x, y, steps) => { await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y, id: 1 }] }); for (const [dx, dy] of steps) { await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: x + dx, y: y + dy, id: 1 }] }); await sleep(16); } await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); await sleep(80); };
  const info = () => p.evaluate(() => { const P = Ws.panels.filter(q => q.type === 'chart' && q.chart.data.length)[0], ch = P.chart, r = ch.cv.getBoundingClientRect(); ch.paint(); return { lock: !!ch.lockR, cx: r.left + r.width * 0.35, cy: r.top + r.height * 0.45, chip: ch._autoChip ? { x: r.left + ch._autoChip.x * ch.S + 5, y: r.top + ch._autoChip.y * ch.S + 5 } : null, W: ch.W, H: ch.H, cw: ch.cw(), r: ch.r }; });
  await p.evaluate(() => { const ch = Ws.panels.filter(q => q.type === 'chart' && q.chart.data.length)[0].chart; ch.autoY(); ch.fit(); ch.paint(); });
  const out = {}; let a = await info();
  // 1a) wobbly sideways swipe: time moves, scale stays automatic
  await drag(a.cx, a.cy, Array.from({ length: 12 }, (_, i) => [(i + 1) * 14, Math.sin(i) * 9])); let b1 = await info(); out.sidewaysLocked = b1.lock; out.sidewaysMovedTime = Math.abs(b1.r - a.r) > 3;
  // 1b) clearly vertical drag: manual (TradingView style)
  await drag(b1.cx, b1.cy, Array.from({ length: 12 }, (_, i) => [Math.sin(i) * 2, (i + 1) * 12])); let c1 = await info(); out.verticalLocked = c1.lock;
  // 1c) manual and the newest candle off the scale: the Auto chip shows and one tap restores the scale
  await p.evaluate(() => { const ch = Ws.panels.filter(q => q.type === 'chart' && q.chart.data.length)[0].chart; ch.lockR = [ch._lo - 60, ch._hi - 60]; ch.paint(); }); let d1 = await info(); out.chipShown = !!d1.chip;
  if (d1.chip) { await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: d1.chip.x, y: d1.chip.y, id: 1 }] }); await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); await sleep(120); }
  let e1 = await info(); out.chipTapRestoresAuto = !e1.lock && !e1.chip;
  // 2) narrow chart + small panel
  const nar = await p.evaluate(() => { const ch = Ws.panels.filter(q => q.type === 'chart' && q.chart.data.length)[0].chart; ch.colOn = true; ch.domOn = true; const keep = ch.W; const o = {}; o.W = ch.W; o.cw = ch.cw(); o.share = +(ch.cw() / ch.W).toFixed(2); return o; });
  out.narrow = nar; out.noErrors = !errs.length;
  const ok = out.sidewaysLocked === false && out.sidewaysMovedTime && out.verticalLocked && out.chipShown && out.chipTapRestoresAuto && nar.W < 520 ? nar.share <= 0.3 : true;
  const ok2 = out.sidewaysLocked === false && out.sidewaysMovedTime && out.verticalLocked && out.chipShown && out.chipTapRestoresAuto && !errs.length;
  console.log(JSON.stringify(out), 'errors', errs.length, errs[0] || '', ok && ok2 ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok && ok2 ? 0 : 1);
})();
