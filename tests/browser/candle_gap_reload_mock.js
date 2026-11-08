// MOCK-TESTED ONLY (mocked OKX candles). Old candles (saved / stale) followed by a fresh live poll used to leave a HOLE in the chart (owner 2026-11-05: 15m gold with a gap, the 1m chart fine).
// Now a poll whose first candle is more than 2 bars after the last one drops the old candles and reloads the whole history; at most 2 such reloads per 10 min per chart.
// Run: NODE_PATH=$(npm root -g) node tests/browser/candle_gap_reload_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  const H = 3600000, T0 = Math.floor(Date.now() / H) * H - 199 * H, bars = [];
  for (let i = 0; i < 200; i++) { const c = 100 + Math.sin(i / 9) * 4; bars.push([String(T0 + i * H), String(c), String(c + 1), String(c - 1), String(c + 0.3), '10', '0', '0', '1']); }
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    let data = []; if (/candles/.test(u)) { const lim = +(/limit=(\d+)/.exec(u) || [0, 300])[1], after = /after=(\d+)/.exec(u); let arr = bars; if (after) arr = bars.filter(x => +x[0] < +after[1]); data = arr.slice(-lim).reverse(); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', msg: '', data }) }); });
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(800);
  const r = await p.evaluate(async () => {
    Ws.build([['chart', { x: 10, y: 10, w: 700, h: 420 }, { sym: 'BTC-USDT', tf: '1H', group: 0 }]]); await new Promise(r => setTimeout(r, 2500));
    const P = Ws.panels.find(q => q.type === 'chart'), ch = P.chart, out = { loaded: ch.data.length };
    const gaps = d => { let g = 0; for (let i = 1; i < d.length; i++) if (d[i].t - d[i-1].t > 2*3600000) g++; return g; };
    ch.data = ch.data.slice(0, 100); ch.setData(ch.data, false); out.stale = ch.data.length; P.kick(); await new Promise(r => setTimeout(r, 3500));
    out.after = ch.data.length; out.gaps = gaps(ch.data); out.last = ch.data.length ? ch.data[ch.data.length-1].t : 0; out.fresh = Date.now() - out.last < 2*3600000; return out; });
  const ok = r.loaded >= 150 && r.stale === 100 && r.after >= 150 && r.gaps === 0 && r.fresh && errs.length === 0;
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
