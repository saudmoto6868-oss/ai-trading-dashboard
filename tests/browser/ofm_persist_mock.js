// MOCK-TESTED ONLY (mocked Hyperliquid candles + wide l2Book). The WIDE order-flow column keeps its book history across a Reload (IndexedDB, per symbol, last 60 min): saved books come back in front of the new ones,
// the time in between stays a gap; a new symbol starts without the old symbol's books; wheel zoom goes down to 10 s. Run: NODE_PATH=$(npm root -g) node tests/browser/ofm_persist_mock.js /tmp/ws.html
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
  const URL = 'file://' + process.argv[2], build = sym => p.evaluate(s => { Ws.build([['chart', { x: 10, y: 10, w: 900, h: 520 }, { sym: s, tf: '5m', group: 0, dcol: true, dom: true, bub: true }]]); }, sym);
  await p.goto(URL); await p.waitForTimeout(800); await build('HL:xyz:GOLD'); await p.waitForTimeout(11000);
  const A = await p.evaluate(async () => { const ch = Ws.panels.find(q => q.type === 'chart').chart, sn = ch.wom.snaps; await OFM.save('HL:xyz:GOLD', sn); return { n: sn.length, first: sn[0].t, last: sn[sn.length-1].t }; });
  await p.waitForTimeout(500); await p.goto(URL); await p.waitForTimeout(800); await build('HL:xyz:GOLD'); await p.waitForTimeout(3500);
  const B = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart, sn = ch.wom.snaps; return { n: sn.length, first: sn[0] ? sn[0].t : 0, restored: ch.wom.restored || 0 }; });
  const C = await p.evaluate(async () => { const P = Ws.panels.find(q => q.type === 'chart'); P.setSymbol('HL:xyz:SILVER'); await new Promise(r => setTimeout(r, 1500)); return { n: P.chart.wom.snaps.length, restored: P.chart.wom.restored || 0 }; });
  const D = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart').chart; ch.flowSpan = 0; const rc = ch.cv.getBoundingClientRect(); for (let i = 0; i < 12; i++) ch.wheel({ clientX: rc.left + ch.PR + 30, clientY: rc.top + 100, deltaY: -400, shiftKey: false, preventDefault(){} }); return { span: ch.flowSpan }; });
  const ok = A.n >= 3 && B.restored >= 3 && B.first <= A.first + 1000 && B.n >= B.restored && C.restored === 0 && C.n < B.n && D.span <= 10001 && errs.length === 0;
  console.log(JSON.stringify({ A, B, C, D }), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
