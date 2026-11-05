// MOCK-TESTED ONLY (hand-made book snapshots, no network). The wide order-flow map must STRETCH sideways: a resting wall seen in sparse snapshots (40-60 s apart, the browser was rate-limited or in a background tab)
// is drawn as one continuous horizontal band until the next book, not as thin vertical slices with black stripes between them (owner 2026-11-05).
// (x >= 70 is measured: the left part of the wall row carries the S/R label box.) Run: NODE_PATH=$(npm root -g) node tests/browser/ofm_stretch_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(800); await p.evaluate(() => { Ws.build(Ws.defaults()); }); await p.waitForTimeout(1000);
  const r = await p.evaluate(() => { const mid = 4127, NB = OFM.NB, base = mid*(1 - OFM.SPAN), step = mid*2*OFM.SPAN/NB, now = nowS(), mk = t => { const arr = new Float32Array(NB).fill(1); const wi = Math.floor((mid + 20 - base)/step); for (let k = -1; k <= 1; k++) arr[wi + k] = 60; return { t, mid, bb: mid - .05, ba: mid + .05, base, step, arr, cov: 5 }; };
    const snaps = [mk(now - 110000), mk(now - 50000), mk(now - 8000)], cv = document.createElement('canvas'), W = 300, H = 300; cv.width = W; cv.height = H; const c = cv.getContext('2d'), opt = { compact: true, win: 120000 };
    OFM.render(c, { snaps, trades: [] }, {}, W, H, opt); const R = opt.outR, hi = mid*(1 + R), lo = mid*(1 - R), ph = H - 14, pw = W - 50 - 40, y = Math.round((hi - (mid + 20))/(hi - lo)*ph), x0 = Math.round((now - 110000 - (now - 120000))/120000*pw);
    const px = (x, yy) => { const d = c.getImageData(x, yy, 1, 1).data; return d[0] + d[1] + d[2]; }; let lit = 0, tot = 0; for (let x = 70; x < pw - 3; x++){ tot++; let m = 0; for (let dy = -2; dy <= 2; dy++) m = Math.max(m, px(x, y + dy)); if (m > 330) lit++; }
    return { R, y, x0, pw, lit, tot }; });
  const ok = r.tot > 100 && r.lit/r.tot > 0.95 && errs.length === 0;
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
