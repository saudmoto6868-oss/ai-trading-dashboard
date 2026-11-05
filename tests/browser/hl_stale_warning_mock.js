// MOCK-TESTED ONLY (mocked Hyperliquid answering 429, old candles in the browser's candle cache). Owner 2026-11-05: after a reload the gold charts showed SAVED candles (~90 below the live price) with only a small
// "rate-limiting" line. Now the chart says how old the last candle is and that the price is NOT live; and the Hyperliquid candle poll slows down on bigger timeframes.
// Run: NODE_PATH=$(npm root -g) node tests/browser/hl_stale_warning_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (/hyperliquid\.xyz/.test(u)) return r.fulfill({ status: 429, contentType: 'text/plain', body: 'rate limited' }); return r.abort(); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000);
  const r = await p.evaluate(async () => {
    const poll = { m5: hlPoll('5m'), m15: hlPoll('15m'), h1: hlPoll('1H'), h4: hlPoll('4H'), d1: hlPoll('1D'), m1: hlPoll('1m') };
    const H = 300000, T0 = Math.floor((Date.now() - 3 * 3600000) / H) * H - 100 * H, rows = Array.from({ length: 100 }, (_, i) => ({ t: T0 + i * H, o: 4040, h: 4042, l: 4038, c: 4041, v: 1 }));
    CandleCache.put('HL:xyz:GOLD', '5m', rows);
    Ws.build([['chart', { x: 10, y: 10, w: 700, h: 420 }, { sym: 'HL:xyz:GOLD', tf: '5m', group: 0 }]]); Ws.save();
    await new Promise(r => setTimeout(r, 4500)); const P = Ws.panels.find(q => q.type === 'chart');
    return { poll, msg: P ? P.msg.textContent : null, bars: P ? P.chart.data.length : null }; });
  const ok = r.poll.m1 === 6000 && r.poll.m5 === 6000 && r.poll.m15 === 10000 && r.poll.h1 === 20000 && r.poll.h4 === 30000 && r.poll.d1 === 45000 && /NOT live|مش حي/.test(r.msg || '') && /⚠/.test(r.msg || '') && r.bars > 0 && errs.length === 0;
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
