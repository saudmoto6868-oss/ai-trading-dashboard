// MOCK-TESTED ONLY (mocked OKX, real Chromium). Price-scale zoom (wheel over the price axis, Shift + wheel, drag on the axis): anchored at the cursor (the price under it stays put), one event changes the scale by at most 25 %
// (a high-resolution wheel used to zoom 4x+ in one event), the scale stays within 0.05x .. 8x of the auto range (was 0.02x .. 60x: candles flattened into a line), and it is reversible (out N, in N = back).
// Run: NODE_PATH=$(npm root -g) node tests/browser/price_scale_zoom_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100;
    for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2; o.push([String(now - (300 - i) * 3600000), String(c - 0.5), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3500);
  const res = await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length), ch = P.chart; ch.fit(); ch.paint();
    const rect = ch.cv.getBoundingClientRect(), ax = rect.left + (ch.W - ch.axw / 2) * ch.S, at = y => rect.top + y * ch.S, span = () => ch._hi - ch._lo, priceAt = y => ch._hi - (y / ch.PB) * (ch._hi - ch._lo);
    const wheel = (dy, y, shift) => { ch.cv.dispatchEvent(new WheelEvent('wheel', { deltaY: dy, clientX: ax, clientY: at(y), shiftKey: !!shift, bubbles: true, cancelable: true })); ch.paint(); };
    const out = {}; const s0 = span(); const yA = ch.candleY(), pA = priceAt(yA);
    wheel(3000, yA); out.hugeWheelFactor = +(span() / s0).toFixed(3);                         // one huge event: at most ~1.25x
    out.anchorDrift = +Math.abs(priceAt(yA) - pA).toFixed(4);   // anchor = middle of the candles                               // the price under the cursor stayed (in price units; the span is ~10)
    for (let i = 0; i < 80; i++) wheel(120, ch.PB * 0.5); out.maxOut = +(span() / s0).toFixed(2);   // capped
    for (let i = 0; i < 120; i++) wheel(-120, ch.PB * 0.5); out.maxIn = +(span() / s0).toFixed(3);  // capped on the way in too
    ch.fit(); ch.paint(); const s1 = span(); for (let i = 0; i < 6; i++) wheel(100, ch.PB * 0.4); for (let i = 0; i < 6; i++) wheel(-100, ch.PB * 0.4); out.reversible = +(span() / s1).toFixed(3);
    ch.fit(); ch.paint(); const s2 = span(); ch.lockR = null;
    for (let i = 0; i < 5; i++) { ch.cv.dispatchEvent(new PointerEvent('pointerdown', { clientX: ax, clientY: at(100), pointerId: 1, buttons: 1, bubbles: true })); ch.cv.dispatchEvent(new PointerEvent('pointermove', { clientX: ax, clientY: at(100) + 300, pointerId: 1, buttons: 1, bubbles: true })); ch.cv.dispatchEvent(new PointerEvent('pointerup', { clientX: ax, clientY: at(400), pointerId: 1, bubbles: true })); ch.paint(); }
    out.dragFactor = +(span() / s2).toFixed(2); out.yZoom = +ch.yZoom.toFixed(3);
    ch.fit(); ch.paint(); for (let i = 0; i < 25; i++) wheel(-120, ch.PB * 0.9); { let l = 1e9, h = -1e9; for (let i = Math.max(0, Math.floor(ch.idx(0))); i <= Math.min(ch.data.length-1, Math.ceil(ch.r)); i++) { l = Math.min(l, ch.data[i].l); h = Math.max(h, ch.data[i].h); } const mid = (l + h) / 2; out.midInView = mid <= ch._hi && mid >= ch._lo ? 1 : 0; }   // zoomed in hard, wheel far from the candles: their middle is still on screen
    return out; });
  const ok = res.hugeWheelFactor <= 1.26 && res.hugeWheelFactor >= 1.0 && res.anchorDrift < 0.35 && res.maxOut <= 8.1 && res.maxIn >= 0.049 && Math.abs(res.reversible - 1) < 0.02 && res.yZoom <= 8 && res.yZoom >= 0.05 && res.midInView === 1 && !errs.length;
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
