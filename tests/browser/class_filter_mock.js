// MOCK-TESTED ONLY. Class filter on ALREADY scanned setups (no fetch): symClass(), FILT.cls in readyList() (Ready / Signals / Setup Card) and "Best of all" = top 2 per class.
// Run: NODE_PATH=$(npm root -g) node tests/browser/class_filter_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; let fetches = 0; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); fetches++; return r.abort(); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(800);
  const res = await p.evaluate(async () => { const mk = (symbol, score) => ({ symbol, direction: 'bullish', ttype: 'Day Trade', tfk: '1h', score, max: 10, tags: [], plan: { entry: 100, stop: 99, tps: [102, 103, 104], dir: 'bullish' } });
    const syms = { 'BTC-USDT': 9, 'ETH-USDT': 8, 'SOL-USDT': 7, 'HL:xyz:GOLD': 9, 'HL:xyz:SILVER': 6, 'HL:xyz:SP500': 7, 'Y:EURUSD=X': 8, 'Y:AAPL': 5, 'HL:xyz:CL': 6 };
    CFG.ready = Object.entries(syms).map(([s, sc]) => mk(s, sc)); const cls = Object.fromEntries(Object.keys(syms).map(s => [s, symClass(s)])); const out = { cls };
    const n = c => { FILT.cls = c; return readyList().map(e => e.symbol); }; out.all = n('All').length; out.metals = n('Metals'); out.crypto = n('Crypto').length; out.best = n('__best'); FILT.cls = 'All'; out.counts = clsCounts(); out.all_after = readyList(true).length; return out; });
  console.log(JSON.stringify(res), 'fetches', fetches, 'errors', errs.length, errs[0] || ''); await b.close();
})();
