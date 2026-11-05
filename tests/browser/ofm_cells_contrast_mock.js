// MOCK-TESTED ONLY (hand-made dense book, no network). Owner 2026-11-05 (BTC screenshot): the wide order-flow map looked compressed - 1 px rows and columns like static, and almost everything orange because a dense book has
// many similar sizes. Now: (1) the map is drawn in 4 px CELLS (every 4x4 block has one colour, like ATAS / Bookmap); (2) colour = size relative to the TYPICAL resting size (log2): a uniform dense book stays dark, only walls are bright.
// Run: NODE_PATH=$(npm root -g) node tests/browser/ofm_cells_contrast_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(800); await p.evaluate(() => { Ws.build(Ws.defaults()); }); await p.waitForTimeout(1000);
  const r = await p.evaluate(() => { const mid = 80500, NB = OFM.NB, base = mid*(1 - OFM.SPAN), step = mid*2*OFM.SPAN/NB, now = nowS(), fbase = mid*(1 - OFM.FSPAN), fstep = mid*2*OFM.FSPAN/OFM.NF, wallP = mid + 120;
    const mk = (t, seed) => { const arr = new Float32Array(NB), fine = new Float32Array(OFM.NF); for (let i = 0; i < NB; i++) arr[i] = 10 + ((i*7 + seed) % 5);   // a dense, noisy but UNIFORM book (sizes 10-14)
      for (let j = 0; j < OFM.NF; j++) fine[j] = 0.8 + ((j*5 + seed) % 5)*0.1; const wi = Math.floor((wallP - base)/step), wj = Math.floor((wallP - fbase)/fstep); for (let k = -1; k <= 1; k++) arr[wi + k] = 140; { const hi0 = Math.floor((mid - 220 - base)/step), hi1 = Math.floor((mid - 180 - base)/step), fj0 = Math.floor((mid - 220 - fbase)/fstep), fj1 = Math.floor((mid - 180 - fbase)/fstep); for (let i = hi0; i <= hi1; i++) arr[i] *= 4; for (let j = fj0; j <= fj1; j++) fine[j] *= 4; } for (let k = -2; k <= 2; k++) fine[wj + k] = 14;   // one real wall (~12x the usual)
      return { t, mid, bb: mid - .5, ba: mid + .5, base, step, arr, fine, fbase, fstep, cov: 5 }; };
    const snaps = []; for (let k = 0; k < 40; k++) snaps.push(mk(now - 120000 + k*3000, k));
    const cv = document.createElement('canvas'), W = 340, H = 300; cv.width = W; cv.height = H; const c = cv.getContext('2d'), opt = { compact: true, ylink: [mid - 300, mid + 300], win: 120000 }; OFM.render(c, { snaps, trades: [] }, {}, W, H, opt);
    const pw = W - 50 - 40, ph = H - 14, yOf = v => Math.round((mid + 300 - v)/600*ph), data = c.getImageData(0, 0, pw, ph).data, px = (x, y) => { const o = (y*pw + x)*4; return data[o] + data[o+1] + data[o+2]; };
    // (1) cells: inside a 4x4 block (cell origin multiples of 4) every pixel has the same colour (away from the mid line / S-R overlays: sample the lower part, rows far from the wall)
    let same = 0, tot = 0; for (let cx = 5; cx < 40; cx++) for (let cy = 38; cy < 53; cy++){ const x0 = cx*4, y0 = cy*4; tot++; if (px(x0, y0 + 1) === px(x0 + 3, y0 + 1) && (px(x0 + 1, y0 + 1) === px(x0 + 1, y0 + 2) || px(x0 + 1, y0 + 2) === px(x0 + 1, y0 + 3))) same++; }   // a thin grid line may cross one row of a block, never the whole block
    // (2) contrast: ordinary rows stay dark, the wall is bright; and a region 4x bigger than the rest is clearly brighter (colour = size relative to the typical size)
    const ord = []; for (let y = 160; y < 270; y += 3) for (let x = 60; x < pw - 5; x += 9) ord.push(px(x, y)); ord.sort((u, v) => u - v); const medOrd = ord[Math.floor(ord.length/2)], p90Ord = ord[Math.floor(ord.length*0.9)], wallB = Math.max(...[-2, -1, 0, 1, 2].map(dy => px(Math.round(pw*0.7), yOf(wallP) + dy)));
    const yHi = yOf(mid - 200), brHi = (() => { let m = 0; for (let k = 0; k < 20; k++) m += px(60 + k*7, yHi + 4); return m/20; })(), brLo = (() => { let m = 0; for (let k = 0; k < 20; k++) m += px(60 + k*7, yOf(mid - 60)); return m/20; })();
    return { brHi, brLo, sameBlocks: same/tot, medOrd, p90Ord, wallB }; });
  const ok = r.sameBlocks > 0.9 && r.medOrd < 330 && r.brLo < 330 && r.wallB > 450 && r.brHi > r.brLo + 120 && errs.length === 0;
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
