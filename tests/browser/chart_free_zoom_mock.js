// MOCK-TESTED ONLY. Pass = (1) live ticks do not re-centre a zoomed / panned chart, (2) the candle under the cursor stays under it while zooming, (3) a vertical drag freezes the price scale (manual) and later horizontal pans do not rescale it, (4) Shift+wheel zooms price.
// Run: NODE_PATH=$(npm root -g) node tests/browser/chart_free_zoom_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 60000) * 60000, o = []; let c = 100; for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2; o.push([String(now - i * 60000), String(c), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3500);
  const res = await p.evaluate(async () => { const P = Ws.panels.find(q => q.type === 'chart'), ch = P.chart, out = {}; const wait = ms => new Promise(r => setTimeout(r, ms));
    out.autoCenterDefault = ch.autoCenter; const rc = ch.cv.getBoundingClientRect(), mx = 300, my = 200, cx = rc.left + mx*ch.S, cy = rc.top + my*ch.S;
    const idx0 = ch.idx(mx); ch.cv.dispatchEvent(new WheelEvent('wheel', { deltaY: -100, clientX: cx, clientY: cy, bubbles: true, cancelable: true })); await wait(60); out.anchorDrift = +(ch.idx(mx) - idx0).toFixed(3);
    const r0 = ch.r; const last = ch.data[ch.data.length - 1]; for (let k = 0; k < 5; k++) { P.liveTick({ t: last.t, o: last.o, h: last.h + 1, l: last.l, c: last.c + k, v: 1 }); await wait(40); } out.rMovedByTicks = +(ch.r - r0).toFixed(3);
    out.lockBefore = !!ch.lockR; ch.cv.dispatchEvent(new PointerEvent('pointerdown', { clientX: cx, clientY: cy, pointerId: 1, bubbles: true, button: 0 })); for (let k = 1; k <= 8; k++) { ch.cv.dispatchEvent(new PointerEvent('pointermove', { clientX: cx, clientY: cy + k*5, pointerId: 1, bubbles: true })); await wait(20); }
    ch.cv.dispatchEvent(new PointerEvent('pointerup', { clientX: cx, clientY: cy + 40, pointerId: 1, bubbles: true })); out.lockAfterVerticalDrag = !!ch.lockR; const rng = ch.lockR && ch.lockR.slice();
    ch.r -= 30; ch.draw(); await wait(80); out.rangeStableAfterPan = !!(rng && ch.lockR && rng[0] === ch.lockR[0] && rng[1] === ch.lockR[1]);
    const yz = ch.yZoom; ch.cv.dispatchEvent(new WheelEvent('wheel', { deltaY: 100, shiftKey: true, clientX: cx, clientY: cy, bubbles: true, cancelable: true })); await wait(60); out.shiftWheelChangedYZoom = ch.yZoom !== yz; return out; });
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
