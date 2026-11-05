// (Also: ofm_vertical below.) MOCK-TESTED ONLY (mocked Hyperliquid candles + wide l2Book). WIDE mode of the chart's order-flow column (owner 2026-11-05: the column covered only the chart's few dollars; wants the whole book with
// support / resistance): default ON, own price scale over the whole book; default = the CHART's price scale (candles, yellow price line and map stretch together, Shift + wheel = vertical zoom), wheel = time (horizontal stretch); own-scale mode = Shift + wheel is the column's range (never narrower than the chart), snapshots collected, labelled S/R lines, switch off = old chart-aligned column.
// Run: NODE_PATH=$(npm root -g) node tests/browser/ofm_vertical_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 800 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  let n = 0;
  const ladder = (tick, mid) => { const bids = [], asks = [], q = tick / 0.1; for (let i = 0; i < 20; i++) { const w = (i % 6 === 0 ? 6 : 1) * q; bids.push({ px: (mid - 0.1 - i * tick).toFixed(4), sz: String(w), n: 3 }); asks.push({ px: (mid + 0.1 + i * tick).toFixed(4), sz: String(w), n: 3 }); } return { coin: 'xyz:GOLD', time: Date.now(), levels: [bids, asks] }; };
  await p.route('**/*', async r => { const rq = r.request(), u = rq.url(); if (u.startsWith('file:')) return r.continue();
    if (/hyperliquid\.xyz\/info/.test(u)) { n++; let body = {}; try { body = JSON.parse(rq.postData() || '{}'); } catch (e) {} let data = []; const mid = 4127 + Math.sin(n / 9);
      if (body.type === 'l2Book') data = ladder({ 5: 0.1, 4: 1, 3: 10, 2: 100 }[body.nSigFigs] || 0.1, mid);
      else if (body.type === 'candleSnapshot') { const iv = { '1m': 6e4, '5m': 3e5, '15m': 9e5, '1h': 36e5 }[body.req.interval] || 9e5, end = body.req.endTime, cnt = Math.min(300, Math.ceil((end - body.req.startTime) / iv)); data = Array.from({ length: cnt }, (_, i) => { const t = Math.floor(end / iv) * iv - (cnt - 1 - i) * iv, c = 4120 + Math.sin(i / 8) * 6; return { t, T: t + iv - 1, s: 'xyz:GOLD', i: body.req.interval, o: String(c), c: String(c + .4), h: String(c + 1.5), l: String(c - 1.5), v: '10', n: 5 }; }); }
      else if (body.type === 'metaAndAssetCtxs') data = [{ universe: [{ name: 'xyz:GOLD' }] }, [{ midPx: String(mid), dayNtlVlm: '1e9', openInterest: '1e5', prevDayPx: '3940' }]];
      else if (body.type === 'recentTrades') data = Array.from({ length: 10 }, (_, i) => ({ coin: 'xyz:GOLD', side: i % 2 ? 'B' : 'A', px: String(mid + (i - 5) * .1), sz: String(1 + i), time: Date.now() - i * 800, hash: 'h' + n + i, tid: n * 100 + i }));
      return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(data) }); }
    if (/okx\.com\/api\/v5\/public\/time/.test(u)) return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: [{ ts: String(Date.now()) }] }) });
    return r.abort(); });
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(800);
  await p.evaluate(() => { Ws.build([['chart', { x: 10, y: 10, w: 900, h: 520 }, { sym: 'HL:xyz:GOLD', tf: '5m', group: 0, dcol: true, dom: true, bub: true }]]); Ws.save(); }); await p.waitForTimeout(8000);
  const info = () => p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart, rc = ch.cv.getBoundingClientRect(), cw = ch.cw(); return { visR: ch._hi - ch._lo, lock: ch.lockR ? ch.lockR.slice() : null, yZoom: ch.yZoom, span: ch.flowSpan || 0, hi: ch._hi - ch._lo, mapX: rc.left + ch.PR + 40, stripX: rc.left + ch.PR + cw - OFM.CAX - OFM.CDP + 25, y: rc.top + 180 }; });
  const rng = a => a.lock ? a.lock[1] - a.lock[0] : null;
  const a0 = await info();
  // (1) REAL wheel on the MAP = time only
  await p.mouse.move(a0.mapX, a0.y); await p.mouse.wheel(0, -300); await p.waitForTimeout(300); const a1 = await info();
  // (2) REAL wheel on the PRICE STRIP = price only (the vertical stretch), no Shift needed
  await p.mouse.move(a0.stripX, a0.y); await p.mouse.wheel(0, 300); await p.waitForTimeout(300); const a2 = await info();
  // (3) Shift + wheel on Windows arrives as a SIDEWAYS wheel (deltaX): must zoom the price as well
  await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart; ch.autoY(); ch.draw(); }); await p.waitForTimeout(200); const b0 = await info();
  await p.evaluate(({ x, y }) => { const ch = Ws.panels.find(q => q.type === 'chart').chart; ch.wheel({ clientX: x, clientY: y, deltaX: 300, deltaY: 0, shiftKey: true, preventDefault(){} }); }, { x: a0.mapX, y: a0.y }); await p.waitForTimeout(300); const b1 = await info();
  // (4) REAL drag on the price strip = vertical zoom like dragging the chart's price axis
  await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart; ch.autoY(); ch.draw(); }); await p.waitForTimeout(200); const c0 = await info();
  await p.mouse.move(c0.stripX, c0.y); await p.mouse.down(); for (let k = 1; k <= 8; k++) await p.mouse.move(c0.stripX, c0.y - k*10); await p.mouse.up(); await p.waitForTimeout(300); const c1 = await info();
  const ok1 = a1.span > 0 && a1.span !== a0.span && !a1.lock && a1.yZoom === 1;
  const ok2 = !!a2.lock && a2.span === a1.span;
  const ok3 = !b0.lock && !!b1.lock && Math.abs(b1.hi - b0.hi) > 0.5;   // the visible price range really changed (deltaX counted)
  const ok4 = !c0.lock && !!c1.lock && Math.abs(c1.hi - c0.hi) > 0.5;
  console.log(JSON.stringify({ a0, a1, a2, b1, c1 }), 'errors', errs.length, errs[0] || '', ok1 && ok2 && ok3 && ok4 && !errs.length ? 'PASS' : 'FAIL', JSON.stringify({ ok1, ok2, ok3, ok4 })); await b.close(); process.exit(ok1 && ok2 && ok3 && ok4 && !errs.length ? 0 : 1);
})();
