// MOCK-TESTED ONLY (mocked OKX, synthetic candles / book). The order-flow column on 1H / 4H / 1D used to show only a thin strip around the price (the book covers a tiny price range, no saved history):
// share of the column that is lit = how much there is to read. Run: NODE_PATH=$(npm root -g) node tests/browser/orderflow_bigtf_visible_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 4000;
    for (let i = 0; i < 300; i++) { c += Math.sin(i / 9) * 14 + Math.cos(i / 3) * 6; const hi = c + 8 + (i % 7), lo = c - 8 - (i % 5); o.push([String(now - (300 - i) * 3600000), String(c - 2), String(hi), String(lo), String(c), String(50 + (i * 37) % 200), '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3500);
  const res = await p.evaluate(async () => { const P = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length), ch = P.chart, out = {}; ch.colOn = true; ch.domOn = true; ch.bubOn = true;
    const mid = ch.data[ch.data.length - 1].c; for (let k = 0; k < 6; k++) { const bids = [], asks = []; for (let i = 0; i < 40; i++) { bids.push({ p: +(mid - 0.05 - i * 0.1).toFixed(2), q: 1 + ((i * 7 + k) % 11) }); asks.push({ p: +(mid + 0.05 + i * 0.1).toFixed(2), q: 1 + ((i * 5 + k) % 13) }); } ch.domAdd({ bids, asks, deep: null, t: Date.now() - (6 - k) * 500 }); }
    for (const tf of ['1H', '4H', '1D']) { ch.tf = tf; ch.paint(); const k = ch.S || 1, dpr = window.devicePixelRatio || 1, x0 = Math.floor((ch.PR + 8) * k * dpr), w = Math.max(1, Math.floor((ch.cw() - 12) * k * dpr)), h = Math.max(1, Math.floor((ch.PB - 40) * k * dpr)), y0 = Math.floor(30 * k * dpr);
      const d = ch.ctx.getImageData(x0, y0, w, h).data; let lit = 0, n = 0; for (let i = 0; i < d.length; i += 4) { n++; if (d[i] + d[i + 1] + d[i + 2] > 70) lit++; } out[tf] = { litPct: +(100 * lit / n).toFixed(1), vpf: ch.st.of.vpf === undefined ? 'auto' : ch.st.of.vpf }; }
    return out; });
  const ok = ['1H', '4H', '1D'].every(t => res[t].litPct > 8) && !errs.length;
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
