// MOCK-TESTED ONLY (mocked OKX candles). A saved manual price-scale lock that the price has left by more than the lock's whole height is dropped on the first data load (back to automatic);
// a lock the price is still near (or only slightly outside) is kept. Owner 2026-11-05: lock saved at ~4020-4065 (wrong PC clock), gold now ~4127 -> candles off screen with an "Auto" chip.
// Run: NODE_PATH=$(npm root -g) node tests/browser/stale_manual_lock_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  const H = 3600000, T0 = Math.floor(Date.now() / H) * H - 120 * H, bars = [];
  for (let i = 0; i < 120; i++) { const c = 4125 + Math.sin(i / 7) * 3; bars.push([String(T0 + i * H), String(c), String(c + 1), String(c - 1), String(c + 0.3), '10', '0', '0', '1']); }
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    const data = /candles/.test(u) ? bars.slice().reverse() : []; return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', msg: '', data }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000);
  const r = await p.evaluate(async () => {
    Ws.build([['chart', { x: 10, y: 10, w: 700, h: 420 }, { sym: 'BTC-USDT', tf: '1H', group: 0 }]]); await new Promise(r => setTimeout(r, 2500));
    const ch = Ws.panels.find(q => q.type === 'chart').chart, rows = ch.data.slice(), out = {};
    ch.lockR = [4020, 4065]; ch.setData(rows, true); out.stale = ch.lockR;            // price 4125 is 60 above a 45-wide lock: stale
    ch.lockR = [4100, 4140]; ch.setData(rows, true); out.near = ch.lockR && ch.lockR.slice();   // price inside: kept
    ch.lockR = [4000, 4120]; ch.setData(rows, true); out.slightly = ch.lockR && ch.lockR.slice();   // 5 above a 120-wide lock: kept
    ch.lockR = [4020, 4065]; ch.setData(rows, false); out.noFit = ch.lockR && ch.lockR.slice();   // a live update does not drop a deliberate lock
    return out; });
  const ok = r.stale === null && r.near && r.near[0] === 4100 && r.slightly && r.slightly[0] === 4000 && r.noFit && r.noFit[0] === 4020 && errs.length === 0;
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
