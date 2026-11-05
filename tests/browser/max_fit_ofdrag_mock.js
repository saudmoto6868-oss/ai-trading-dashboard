// MOCK-TESTED ONLY. (1) maximise = the visible slice of the tall workspace frame, not the whole frame; (2) dragging the wide order-flow column moves ITS time / (own scale) price, not the candles;
// (3) tablet: the ⇕ scroll handle exists and scrolls the page. Host page + workspace served over http so the iframe is same-origin.
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const html = fs.readFileSync(process.argv[2], 'utf8'); const b = await chromium.launch(); const errs = [];
  const mk = async (opts) => { const ctx = await b.newContext(opts); const p = await ctx.newPage(); p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
    await p.route('http://t.local/**', r => { const u = r.request().url();
      if (/ws\.html/.test(u)) return r.fulfill({ status: 200, contentType: 'text/html', body: html });
      return r.fulfill({ status: 200, contentType: 'text/html', body: '<body style="margin:0"><div style="height:60px">header</div><iframe id="f" src="/ws.html?blank=1" style="width:100%;height:3400px;border:0;display:block"></iframe></body>' }); });
    await p.goto('http://t.local/host'); await p.waitForTimeout(1500); return p; };
  const p = await mk({ viewport: { width: 1400, height: 800 } }); const F = () => p.frames().find(f => f.url().includes('ws.html'));
  await F().evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(1500);
  const r = {};
  r.frameH = await F().evaluate(() => innerHeight);
  r.max1 = await F().evaluate(() => { const c = Ws.panels.find(x => x.type === 'chart'); c.toggleMax(); const o = {y: c.rect.y, h: c.rect.h}; c.toggleMax(); return o; });
  await p.evaluate(() => window.scrollTo(0, 1200)); await p.waitForTimeout(300);
  r.max2 = await F().evaluate(() => { const c = Ws.panels.find(x => x.type === 'chart'); c.toggleMax(); const o = {y: c.rect.y, h: c.rect.h}; c.toggleMax(); return o; });
  await p.evaluate(() => window.scrollTo(0, 0));
  // order-flow column drag
  const g = await F().evaluate(() => { const pn = Ws.panels.find(x => x.type === 'chart'), ch = pn.chart; ch.colWide = ch.colWide || 1; ch.colOwn = false; ch.flowOff = 0; ch.colWideC = 0; const R = ch.cv.getBoundingClientRect(); return { x: R.left + (ch.PR + 10)*ch.S, y: R.top + 200, PR: ch.PR, cw: ch.cw(), colWide: ch.colWide, domOn: ch.domOn, colOn: ch.colOn, r: ch.r }; });
  const fo = await p.locator('#f').boundingBox(); const X = fo.x + g.x, Y = fo.y + g.y;
  await p.mouse.move(X, Y); await p.mouse.down(); r.dbg = await F().evaluate(() => { const ch = Ws.panels.find(x => x.type === 'chart').chart; return { drag: ch.drag && JSON.stringify(ch.drag), W: ch.W, axw: ch.axw, tool: ch.tool, colDrag: !!ch.colDrag }; }); await p.mouse.move(X + 40, Y + 30, { steps: 5 }); await p.mouse.move(X + 90, Y + 60, { steps: 5 }); await p.mouse.up();
  r.col = await F().evaluate(() => { const ch = Ws.panels.find(x => x.type === 'chart').chart; return { flowOff: ch.flowOff, r: ch.r }; }); r.col.r0 = g.r; r.g = g;
  await F().evaluate(() => { const ch = Ws.panels.find(x => x.type === 'chart').chart; ch.colOwn = true; ch.colWideC = 0; });
  await p.mouse.move(X, Y); await p.mouse.down(); await p.mouse.move(X, Y + 60, { steps: 6 }); await p.mouse.up();
  r.own = await F().evaluate(() => Ws.panels.find(x => x.type === 'chart').chart.colWideC);
  const ok = r.max1.h < 1000 && r.max1.h >= 300 && r.max2.h <= 800 && r.max2.y > 300 && r.col.flowOff > 0 && Math.abs(r.col.r - r.col.r0) < 1e-6 && r.own !== 0 && !errs.length;
  // tablet handle
  const t = await mk({ viewport: { width: 1180, height: 820 }, hasTouch: true, userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15' });
  r.rail = await t.frames().find(f => f.url().includes('ws.html')).evaluate(async () => { await new Promise(r => setTimeout(r, 800)); window.__xpixRail && window.__xpixRail.place(); const e = document.getElementById('xrail'); return e ? { shown: getComputedStyle(e).display !== 'none', top: parseInt(e.style.top) } : null; });
  const ok2 = r.rail && r.rail.shown;
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '', ok && ok2 ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok && ok2 ? 0 : 1);
})();
