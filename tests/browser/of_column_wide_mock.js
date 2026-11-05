// MOCK-TESTED ONLY (mocked Hyperliquid candles + wide l2Book). WIDE mode of the chart's order-flow column (owner 2026-11-05: the column covered only the chart's few dollars; wants the whole book with
// support / resistance): default ON, own price scale over the whole book (never narrower than the chart), snapshots collected, labelled S/R lines, switch off = old chart-aligned column.
// Run: NODE_PATH=$(npm root -g) node tests/browser/of_column_wide_mock.js /tmp/ws.html [shot.png]
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
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(800);
  await p.evaluate(() => { Ws.build([['chart', { x: 10, y: 10, w: 900, h: 520 }, { sym: 'HL:xyz:GOLD', tf: '5m', group: 0, dcol: true, dom: true, bub: true }]]); Ws.save(); }); await p.waitForTimeout(9000);
  const r = await p.evaluate(async () => { const P = Ws.panels.find(q => q.type === 'chart'), ch = P.chart, out = { wide: ch.colWide, snaps: ch.wom.snaps.length, cov: ch.wom.snaps.length ? ch.wom.snaps[ch.wom.snaps.length-1].cov : 0, cw: ch.cw() };
    const cv = ch.cv; const c2 = cv.getContext('2d'), s = cv.width / (ch.W || cv.width), x0 = Math.round(ch.PR * s), w = Math.round(out.cw * s), d = c2.getImageData(x0 + 4, 20, w - 8, Math.round((ch.PB || 300) * s) - 40).data; let col = 0; for (let i = 0; i < d.length; i += 4 * 9) if (d[i] + d[i+1] + d[i+2] > 150) col++; out.colored = col;
    out.autoR = ch._wideAutoR; { const rc = ch.cv.getBoundingClientRect(); ch.wheel({ clientX: rc.left + ch.PR + 20, clientY: rc.top + 100, deltaY: 400, shiftKey: false, preventDefault(){} }); } out.manualR = ch.colWideR; out.savedR = P.state.cwr; { const rc = ch.cv.getBoundingClientRect(); ch.wheel({ clientX: rc.left + ch.PR + 20, clientY: rc.top + 100, deltaY: 4000, shiftKey: false, preventDefault(){} }); } out.maxR = ch.colWideR;
    out.item = !!(P.indItems && P.indItems.find(i => i.id === 'cwide')); const it = P.indItems.find(i => i.id === 'cwide'); it.set(false); out.off = ch.colWide; out.saved = P.state.cwide; ch.draw(); it.set(true); out.on = ch.colWide; return out; });
  if (process.argv[3]) await p.screenshot({ path: process.argv[3] });
  const ok = r.wide === 1 && r.snaps >= 3 && r.cov > 3 && r.autoR >= 0.09 && r.manualR > r.autoR && r.savedR === r.manualR && r.maxR >= 0.29 && r.colored > 150 && r.item && r.off === 0 && r.saved === false && r.on === 1 && errs.length === 0;
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
