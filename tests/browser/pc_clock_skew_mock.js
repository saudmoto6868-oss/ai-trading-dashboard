// MOCK-TESTED ONLY (mocked OKX /public/time + Hyperliquid /info). A PC clock that is hours BEHIND the real time (owner 2026-11-05: Windows showed 2:10 PM on 11/4 when it was ~4:30 AM on 11/5) used to make the
// Hyperliquid candle requests end in the past: gold charts showed old candles ~90 below the live price. Now the request ends at the exchange time (PC clock + measured skew) and a red banner names the clock error.
// Run: NODE_PATH=$(npm root -g) node tests/browser/pc_clock_skew_mock.js /tmp/ws.html
const { chromium } = require('playwright');
async function run(offsetMs) {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = [], ends = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', async r => { const rq = r.request(), u = rq.url(); if (u.startsWith('file:')) return r.continue();
    if (/okx\.com\/api\/v5\/public\/time/.test(u)) return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: [{ ts: String(Date.now() + offsetMs) }] }) });
    if (/hyperliquid\.xyz\/info/.test(u)) { let body = {}; try { body = JSON.parse(rq.postData() || '{}'); } catch (e) {}
      if (body.type === 'candleSnapshot') ends.push(body.req.endTime);
      const data = body.type === 'metaAndAssetCtxs' ? [{ universe: [{ name: 'xyz:GOLD' }] }, [{ midPx: '4126', dayNtlVlm: '1e9', openInterest: '1e5', prevDayPx: '3940' }]] : [];
      return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(data) }); }
    return r.abort(); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(800);
  await p.evaluate(() => { Ws.build([['chart', { x: 10, y: 10, w: 700, h: 420 }, { sym: 'HL:xyz:GOLD', tf: '5m', group: 0 }]]); }); await p.waitForTimeout(4000);
  const banner = await p.evaluate(() => { const e = document.getElementById('clkw'); return e ? e.textContent : null; });
  await b.close(); return { ends, banner, errs, now: Date.now() };
}
(async () => {
  const H14 = 14 * 3600000, A = await run(H14), B = await run(0);
  const okA = A.ends.length > 0 && A.ends.every(e => Math.abs(e - (A.now + H14)) < 15 * 60000) && /BEHIND/.test(A.banner || '') && /14 hours/.test(A.banner || '');
  const okB = B.ends.length > 0 && B.ends.every(e => Math.abs(e - B.now) < 15 * 60000) && B.banner === null;
  console.log(JSON.stringify({ behind14h: { n: A.ends.length, banner: A.banner }, normal: { n: B.ends.length, banner: B.banner }, errs: A.errs.concat(B.errs).length }), okA && okB && !A.errs.length && !B.errs.length ? 'PASS' : 'FAIL');
  process.exit(okA && okB ? 0 : 1);
})();
