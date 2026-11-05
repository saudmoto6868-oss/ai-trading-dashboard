// MOCK-TESTED ONLY (mocked OKX books-full + trades). The Order Flow Map panel (type "ofm"): time x price heat map of the wide book, mid line, trade bubbles, current book bars. Counts coloured pixels, snapshots, bubbles,
// the range / window selects, symbol persistence in the saved layout. Run: NODE_PATH=$(npm root -g) node tests/browser/ofm_panel_mock.js /tmp/ws.html [shot.png]
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  let n = 0;
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); n++; let data = [];
    if (/market\/books/.test(u)) { const bids = [], asks = [], mid = 100 + Math.sin(n / 5) * 0.05; for (let i = 0; i < 2000; i++) { const w = (i % 97 === 0 ? 40 : 1) * (1 + (i % 7) / 7); bids.push([(mid - 0.005 - i * 0.005).toFixed(3), String(w), '0', '1']); asks.push([(mid + 0.005 + i * 0.005).toFixed(3), String(w), '0', '1']); } data = [{ bids, asks, ts: String(Date.now()) }]; }
    else if (/market\/trades/.test(u)) { data = Array.from({ length: 30 }, (_, i) => ({ tradeId: String(n * 100 + i), px: String(100 + Math.sin((n + i) / 4) * 0.4), sz: String(1 + (i % 5)), side: i % 2 ? 'buy' : 'sell', ts: String(Date.now() - i * 500) })); }
    else if (/candles/.test(u)) { const H = 3600000, T0 = Math.floor(Date.now() / H) * H - 100 * H; data = Array.from({ length: 100 }, (_, i) => [String(T0 + i * H), '100', '101', '99', '100', '10', '0', '0', '1']).reverse(); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', msg: '', data }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000);
  await p.evaluate(() => { Ws.build([['ofm', { x: 10, y: 10, w: 900, h: 560 }, { sym: 'BTC-USDT', group: 0 }]]); Ws.save(); }); await p.waitForTimeout(9000);
  const r = await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'ofm'), cv = P && P.ofmCv; if (!cv) return { err: 'no panel' }; const c = cv.getContext('2d'), W = cv.width, H = cv.height, d = c.getImageData(0, 0, W - 140, H - 20).data;
    let colored = 0, bright = 0; for (let i = 0; i < d.length; i += 4 * 7) { if (d[i] + d[i+1] + d[i+2] > 120) colored++; if (d[i] > 200 && d[i+1] > 150) bright++; }
    const o = P.om, sel = P.body.querySelectorAll('select').length; return { snaps: o.snaps.length, trades: o.trades.length, cov: o.snaps.length ? o.snaps[o.snaps.length-1].cov : 0, colored, bright, selects: sel, W, H, title: P.ttl.textContent }; });
  if (process.argv[3]) await p.screenshot({ path: process.argv[3] });
  const r2 = await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'ofm'); const rs = P.body.querySelectorAll('select')[1]; rs.value = '0.05'; rs.onchange(); const ws = P.body.querySelectorAll('select')[2]; ws.value = '120000'; ws.onchange(); return { omR: P.state.omR, omW: P.state.omW }; });
  const ok = !r.err && r.snaps >= 2 && r.trades >= 10 && r.cov > 1 && r.colored > 200 && r.selects >= 3 && /Order Flow Map|خريطة/.test(r.title) && r2.omR === 0.05 && r2.omW === 120000 && errs.length === 0;
  console.log(JSON.stringify({ r, r2 }), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
