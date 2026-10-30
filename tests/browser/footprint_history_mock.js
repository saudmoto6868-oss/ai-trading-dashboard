// MOCK-TESTED ONLY (mocked OKX). Footprint: (1) the fill reaches back FP_BARS = 12 candles (it was the newest 3), (2) the newest candle is complete even when the live tape poll missed
// prints (catch-up pages history-trades until a page is fully known), (3) the 12 bars are saved for a refresh. Run: NODE_PATH=$(npm root -g) node tests/browser/footprint_history_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 140)));
  const NOW = Math.floor(Date.now() / 60000) * 60000 + 30000, N = 1500; let extra = 0;   // 1 print every 2 s, newest n = 0 (about 50 min of prints)
  const trade = n => ({ instId: 'BTC-USDT', tradeId: String(1000000 - n), px: String(100 + (n % 5) * 0.1), sz: '1', side: n % 2 ? 'sell' : 'buy', ts: String(NOW - n * 2000) });   // n < 0 = prints that arrive later (extra)
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const h = { 'access-control-allow-origin': '*' }; let data = [];
    if (/\/market\/candles/.test(u)) { const m = Math.floor(NOW / 60000) * 60000; for (let i = 0; i < 300; i++) data.push([String(m - i * 60000), '100', '101', '99', '100', '1', '0', '0', '1']); }
    else if (/history-trades/.test(u)) { const a = (u.match(/after=(\d+)/) || [])[1], start = a ? 1000000 - (+a) + 1 : -extra; for (let n = start; n < Math.min(N, start + 100); n++) data.push(trade(n)); }
    else if (/\/market\/trades/.test(u)) { for (let n = -extra; n < -extra + 3; n++) data.push(trade(n)); }   // the live poll only ever sees the 3 newest prints: a gap
    return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3500);
  const sleepN = ms => new Promise(r => setTimeout(r, ms));
  const ph1 = await p.evaluate(async () => {
    const P = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0], ch = P.chart; ch.fpOn = true; P.state.fp = true; P._fpFilled = null;
    await P.fpFill(); await new Promise(r => setTimeout(r, 300)); const d = ch.data, last = d[d.length - 1], m = ch.fp.get(last.t);
    return { bars: ch.fp.size, lastT: last.t, last: m ? m.b + m.s : 0 }; });
  await sleepN(10500);   // okx() caches the same URL for 10 s (the real catch-up runs every 30 s)
  extra = 10;   // 10 more prints (20 s) happen; the live poll shows only the 3 newest of them
  const ph2 = await p.evaluate(async lastT => {
    const P = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0], ch = P.chart, tot = m => m ? m.b + m.s : 0; const sleep = ms => new Promise(r => setTimeout(r, ms));
    await P.fpCatch(); await sleep(300); P.fpSave(); let saved = 0; try { saved = JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k => /_fp\|/.test(k)))).bars.length; } catch (e) {}
    return { last: tot(ch.fp.get(lastT)), saved }; }, ph1.lastT);
  const expect1 = Math.floor((NOW - ph1.lastT) / 2000) + 1, expect2 = Math.floor((NOW + extra * 2000 - ph1.lastT) / 2000) + 1, res = { ph1, ph2, expect1, expect2 };
  const ok = ph1.bars >= 11 && ph1.last === expect1 && ph2.last === expect2 && expect2 > expect1 && ph2.saved >= 11 && !errs.length;
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
