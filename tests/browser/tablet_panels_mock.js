// MOCK-TESTED ONLY (Chromium touch emulation, iPad-like). Workspace panels on a tablet: a finger on the title bar moves a panel, the corner grip resizes it, the page itself never scrolls under the finger.
// Run: NODE_PATH=$(npm root -g) node tests/browser/tablet_panels_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const ctx = await b.newContext({ viewport: { width: 1180, height: 820 }, hasTouch: true, userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15' });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100;
    for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2; o.push([String(now - (300 - i) * 3600000), String(c - 0.5), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: o }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2500);
  const cdp = await ctx.newCDPSession(p), sleep = ms => new Promise(r => setTimeout(r, ms));   // real touch events (the browser makes the pointer events itself, so pointer capture works like on a tablet)
  const touch = async (pts, steps) => { await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: pts[0][0], y: pts[0][1], id: 1 }] });
    for (const [x, y] of steps) { await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x, y, id: 1 }] }); await sleep(16); }
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); await sleep(60); };
  const geo = () => p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'chart'), r = P.root.getBoundingClientRect(), h = P.head.getBoundingClientRect(), g = P.rz.getBoundingClientRect();
    return { l: r.left, t: r.top, w: r.width, h: r.height, hx: h.left + 60, hy: h.top + h.height / 2, gx: g.left + g.width / 2, gy: g.top + g.height / 2, grip: g.width, n: Ws.panels.length, drag: P.root.classList.contains('drag'), sy: document.scrollingElement.scrollTop }; });
  const out = {}; let a = await geo(); out.panels = a.n; out.gripPx = Math.round(a.grip);
  await touch([[a.hx, a.hy]], Array.from({ length: 8 }, (_, i) => [a.hx + (i + 1) * 10, a.hy + (i + 1) * 6]));
  let b2 = await geo(); out.moved = Math.round(b2.l - a.l) + ',' + Math.round(b2.t - a.t); out.movedOk = Math.abs(b2.l - a.l) > 40 && Math.abs(b2.t - a.t) > 20;
  await touch([[b2.gx, b2.gy]], Array.from({ length: 8 }, (_, i) => [b2.gx - (i + 1) * 8, b2.gy - (i + 1) * 6]));
  let c2 = await geo(); out.resized = Math.round(c2.w - b2.w) + ',' + Math.round(c2.h - b2.h); out.resizedOk = Math.abs(c2.w - b2.w) > 30;
  out.dragCleared = !c2.drag; out.scrollY = c2.sy;
  // the chart itself with REAL touch events: one finger pans, two fingers pinch (time), the browser sends no pointercancel (touch-action none) and the page does not scroll
  await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart; window.__cancels = 0; ch.cv.addEventListener('pointercancel', () => window.__cancels++); ch.fit(); ch.paint(); });
  const cg = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart, r = ch.cv.getBoundingClientRect(); return { x: r.left + r.width * 0.4, y: r.top + r.height * 0.4 }; });
  const st0 = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart; return { r: ch.r, bw: ch.bw }; });
  await touch([[cg.x, cg.y]], Array.from({ length: 10 }, (_, i) => [cg.x + (i + 1) * 12, cg.y + (i + 1) * 14]));   // drag right and DOWN: used to pull-to-refresh
  const st1 = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart; return { r: ch.r, bw: ch.bw, y: document.scrollingElement.scrollTop, c: window.__cancels }; });
  out.realPanMoved = Math.abs(st1.r - st0.r) > 3; out.realCancels = st1.c; out.realScrollY = st1.y;
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: cg.x - 20, y: cg.y, id: 1 }, { x: cg.x + 20, y: cg.y, id: 2 }] });
  for (let i = 1; i <= 8; i++) { await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: cg.x - 20 - i * 12, y: cg.y, id: 1 }, { x: cg.x + 20 + i * 12, y: cg.y, id: 2 }] }); await sleep(16); }
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); await sleep(60);
  const st2 = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart; return { bw: ch.bw, c: window.__cancels }; });
  out.realPinch = +(st2.bw / st1.bw).toFixed(2); out.realCancels = st2.c;
  const res = out;
  const ok = res.panels > 1 && res.movedOk && res.resizedOk && res.gripPx >= 28 && res.dragCleared && res.scrollY === 0 && res.realPanMoved && res.realCancels === 0 && res.realScrollY === 0 && res.realPinch > 1.3 && !errs.length;
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
