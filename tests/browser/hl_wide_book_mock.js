// MOCK-TESTED ONLY (mocked Hyperliquid l2Book with nSigFigs). The order-flow heat map was a thin strip on Hyperliquid markets because l2Book gives 20 levels a side (gold ~ +-2 USD). hlWideBook stitches
// the native ladder with the nSigFigs 5 / 4 / 3 / 2 ladders (tick 0.1 / 1 / 10 / 100: +-1000 USD walls on gold are in the book) beyond its edge and spreads each coarse level over its range, so the book covers ~+-5 % with a continuous density (a sub-level of the 10-USD ladder is capped at 50 parts, so it carries 2 fine ticks of size: density stays equal).
// No empty band at the junction of two ladders (consecutive levels <= ~1 USD apart over the whole +-47 %).
// Run: NODE_PATH=$(npm root -g) node tests/browser/hl_wide_book_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160))); const calls = {}; let failCoarse = false;
  const ladder = tick => { const bids = [], asks = [], q = tick / 0.1; for (let i = 0; i < 20; i++) { bids.push({ px: (4127 - 0.1 - i * tick).toFixed(4), sz: String(q), n: 1 }); asks.push({ px: (4127 + 0.1 + i * tick).toFixed(4), sz: String(q), n: 1 }); } return { coin: 'xyz:GOLD', time: Date.now(), levels: [bids, asks] }; };
  await p.route('**/*', async r => { const rq = r.request(), u = rq.url(); if (u.startsWith('file:')) return r.continue();
    if (/hyperliquid\.xyz\/info/.test(u)) { let body = {}; try { body = JSON.parse(rq.postData() || '{}'); } catch (e) {} let data = [];
      if (body.type === 'l2Book' && body.nSigFigs && failCoarse) { calls.failed = (calls.failed || 0) + 1; return r.fulfill({ status: 500, contentType: 'text/plain', body: 'timeout' }); }
      if (body.type === 'l2Book') { const t = { 5: 0.1, 4: 1, 3: 10, 2: 100 }[body.nSigFigs] || 0.1; calls[body.nSigFigs || 'native'] = (calls[body.nSigFigs || 'native'] || 0) + 1; data = ladder(t); }
      return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(data) }); }
    return r.abort(); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(800);
  const r = await p.evaluate(async () => { const w = (await hlOkx('/market/books-full?instId=' + encodeURIComponent('HL:xyz:GOLD') + '&sz=2000'))[0], n = (await hlOkx('/market/books?instId=' + encodeURIComponent('HL:xyz:GOLD') + '&sz=20'))[0];
    const B = w.bids.map(x => +x[0]), A = w.asks.map(x => +x[0]), Bq = w.bids.map(x => +x[1]), Aq = w.asks.map(x => +x[1]);
    const mono = (a, d) => a.every((v, i) => i === 0 || (d < 0 ? v < a[i-1] - 1e-9 : v > a[i-1] + 1e-9));
    return { nb: B.length, na: A.length, minB: Math.min(...B), maxA: Math.max(...A), monoB: mono(B, -1), monoA: mono(A, 1), qmin: Math.min(...Bq, ...Aq), qmax: Math.max(...Bq, ...Aq), gapB: Math.max(...B.slice(1).map((v, i) => Math.abs(B[i] - v))), gapA: Math.max(...A.slice(1).map((v, i) => Math.abs(v - A[i]))), firstSame: w.bids.slice(0, 20).every((x, i) => Math.abs(+x[0] - +n.bids[i][0]) < 1e-9) && w.asks.slice(0, 20).every((x, i) => Math.abs(+x[0] - +n.asks[i][0]) < 1e-9), nativeN: n.bids.length }; });
  await p.waitForTimeout(4600); failCoarse = true;   // the coarse ladders time out now: the book must keep its far part from the last good copy
  const r2 = await p.evaluate(async () => { const w = (await hlOkx('/market/books-full?instId=' + encodeURIComponent('HL:xyz:GOLD') + '&sz=2000'))[0], B = w.bids.map(x => +x[0]), A = w.asks.map(x => +x[0]); return { minB: Math.min(...B), maxA: Math.max(...A) }; });
  r.keptFar = r2.minB <= 4127 * 0.6 && r2.maxA >= 4127 * 1.4;
  const ok = r.nativeN === 20 && r.keptFar && calls.failed > 0 && r.minB <= 4127 * 0.6 && r.maxA >= 4127 * 1.4 && r.monoB && r.monoA && r.gapB <= 1.05 && r.gapA <= 1.05 && r.qmin > 0.85 && r.qmax < 9.5 && r.firstSame && r.nb > 100 && errs.length === 0 && calls['4'] && calls['3'] && calls['2'];
  console.log(JSON.stringify({ r, calls }), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
