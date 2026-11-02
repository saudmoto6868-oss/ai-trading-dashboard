// MOCK-TESTED ONLY (mocked OKX, Chromium with touch emulation, iPad-like viewport + Mac user agent like iPadOS). Tablet touch on the chart: the browser must not take the gesture
// (canvas touch-action none, no overscroll chaining), one finger moves the chart (time + price), two fingers spread horizontally = time zoom, vertically = price zoom (bounded, no fly-away),
// a drag on the price axis zooms the price. Run: NODE_PATH=$(npm root -g) node tests/browser/tablet_touch_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const ctx = await b.newContext({ viewport: { width: 1180, height: 820 }, hasTouch: true, isMobile: false, userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15' });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100;
    for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2; o.push([String(now - (300 - i) * 3600000), String(c - 0.5), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: o }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2500);
  const res = await p.evaluate(async () => {
    const P = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length), ch = P.chart; ch.fit(); ch.paint();
    const out = { tch: document.body.classList.contains('tch'), tab: document.body.classList.contains('tab'), mob: document.body.classList.contains('mob'),
      touchAction: getComputedStyle(ch.cv).touchAction, overscroll: getComputedStyle(document.body).overscrollBehaviorY };
    const rect = ch.cv.getBoundingClientRect(), X = x => rect.left + x * ch.S, Y = y => rect.top + y * ch.S;
    const ev = (type, id, x, y) => ch.cv.dispatchEvent(new PointerEvent(type, { pointerId: id, pointerType: 'touch', isPrimary: id === 1, clientX: x, clientY: y, buttons: type === 'pointerup' ? 0 : 1, bubbles: true, cancelable: true }));
    const wait = ms => new Promise(r => setTimeout(r, ms));
    // 1) one-finger drag: moves time (r) and, since the price scale unlocks, the price too
    const r0 = ch.r, ys0 = ch.yShift; ev('pointerdown', 1, X(300), Y(200)); for (let i = 1; i <= 8; i++) { ev('pointermove', 1, X(300) + i * 15, Y(200) + i * 8); await wait(16); } ev('pointerup', 1, X(420), Y(264));
    out.panMovedTime = Math.abs(ch.r - r0) > 3; out.panMovedPrice = !!ch.lockR || Math.abs(ch.yShift - ys0) > 1e-6;
    // 2) two-finger horizontal spread = time zoom
    ch.fit(); ch.paint(); const bw0 = ch.bw; ev('pointerdown', 1, X(300), Y(200)); ev('pointerdown', 2, X(340), Y(200)); for (let i = 1; i <= 8; i++) { ev('pointermove', 1, X(300) - i * 15, Y(200)); ev('pointermove', 2, X(340) + i * 15, Y(200)); await wait(16); } ev('pointerup', 1, X(180), Y(200)); ev('pointerup', 2, X(460), Y(200));
    out.timeZoom = +(ch.bw / bw0).toFixed(2);
    // 3) two-finger vertical spread = price zoom (magnify): span gets smaller, bounded, candles stay on screen
    ch.fit(); ch.paint(); ch.lockR = null; const sp0 = ch._hi - ch._lo; ev('pointerdown', 1, X(400), Y(180)); ev('pointerdown', 2, X(400), Y(220)); for (let i = 1; i <= 10; i++) { ev('pointermove', 1, X(400), Y(180) - i * 10); ev('pointermove', 2, X(400), Y(220) + i * 10); await wait(16); ch.paint(); } ev('pointerup', 1, X(400), Y(80)); ev('pointerup', 2, X(400), Y(320)); ch.paint();
    out.priceZoomSpan = +((ch._hi - ch._lo) / sp0).toFixed(3); out.priceZoomBounded = ch.yZoom >= 0.05 && ch.yZoom <= 8;
    { let l = 1e9, h = -1e9; for (let i = Math.max(0, Math.floor(ch.idx(0))); i <= Math.min(ch.data.length - 1, Math.ceil(ch.r)); i++) { l = Math.min(l, ch.data[i].l); h = Math.max(h, ch.data[i].h); } const mid = (l + h) / 2; out.midInView = mid <= ch._hi && mid >= ch._lo; }
    // 4) pinch back in (fingers together) = price scale zooms out again
    const sp1 = ch._hi - ch._lo; ev('pointerdown', 1, X(400), Y(80)); ev('pointerdown', 2, X(400), Y(320)); for (let i = 1; i <= 10; i++) { ev('pointermove', 1, X(400), Y(80) + i * 10); ev('pointermove', 2, X(400), Y(320) - i * 10); await wait(16); ch.paint(); } ev('pointerup', 1, X(400), Y(180)); ev('pointerup', 2, X(400), Y(220)); ch.paint();
    out.priceZoomOut = (ch._hi - ch._lo) > sp1 * 1.5;
    // 5) drag on the price axis with a finger
    ch.fit(); ch.paint(); ch.lockR = null; const sp2 = ch._hi - ch._lo, ax = ch.W - ch.axw / 2; ev('pointerdown', 1, X(ax), Y(100)); for (let i = 1; i <= 10; i++) { ev('pointermove', 1, X(ax), Y(100) + i * 12); await wait(16); } ev('pointerup', 1, X(ax), Y(220)); ch.paint();
    out.axisDragFactor = +((ch._hi - ch._lo) / sp2).toFixed(2);
    return out; });
  const ok = res.tch && res.tab && res.touchAction === 'none' && /none/.test(res.overscroll) && res.panMovedTime && res.panMovedPrice && res.timeZoom > 1.3 && res.priceZoomSpan < 0.7 && res.priceZoomBounded && res.midInView && res.priceZoomOut && res.axisDragFactor !== 1 && !errs.length;
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
