// XPIX Intelligence evidence contract regression.
// Verifies shared Hub payload metadata, exchange-vs-received timestamps, and explicit Yahoo unsupported capability.
// Run: NODE_PATH=$(npm root -g) node tests/browser/xpix_evidence_contract_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 180)));
  const J = d => ({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: d }) });
  await p.route('**/*', r => {
    const u = r.request().url();
    if (u.startsWith('file:')) return r.continue();
    if (!/okx\\.com\\/api\\/v5/.test(u)) return r.abort();
    if (/market\\/books-full/.test(u) || /market\\/books\\?/.test(u)) {
      const lv = (px, step) => Array.from({length: 60}, (_, i) => [String(px + i * step), String(2 + i % 4), '0', '1']);
      return r.fulfill(J([{ bids: lv(60000, -1), asks: lv(60001, 1), ts: String(Date.now() - 250) }]));
    }
    if (/market\\/trades/.test(u)) return r.fulfill(J(Array.from({length: 12}, (_, i) => ({
      tradeId: String(9000 + i), ts: String(Date.now() - i * 500), px: String(60000 + i),
      sz: '0.25', side: i % 2 ? 'buy' : 'sell'
    }))));
    return r.fulfill(J([]));
  });
  await p.goto('file://' + process.argv[2] + '?blank=1');
  await p.waitForTimeout(600);
  await p.evaluate(() => {
    window.__xpixBook = Hub.sub('book', 'BTC-USDT', () => {});
    window.__xpixTape = Hub.sub('trades', 'BTC-USDT', () => {});
    window.__xpixYahoo = Hub.sub('book', 'Y:SPY', () => {});
  });
  await p.waitForTimeout(2600);
  const out = await p.evaluate(() => {
    const book = Hub.last['book|BTC-USDT'], tape = Hub.last['trades|BTC-USDT'], yahoo = Hub.last['book|Y:SPY'];
    return {
      book: !!book && book.symbol === 'BTC-USDT' && book.venue === 'OKX' && book.source === 'OKX REST' &&
        Number.isFinite(book.receivedAt) && Number.isFinite(book.t) && Number.isFinite(book.exchangeTs) &&
        Array.isArray(book.bids) && Array.isArray(book.asks),
      tape: !!tape && tape.symbol === 'BTC-USDT' && tape.venue === 'OKX' && tape.source === 'OKX REST' &&
        Number.isFinite(tape.receivedAt) && Number.isFinite(tape.t) && Number.isFinite(tape.exchangeTs) &&
        Array.isArray(tape.rows) && !!tape.stats,
      unsupported: !!yahoo && yahoo.capability === 'unsupported' && yahoo.error === 'unsupported_market_feed' &&
        yahoo.venue === 'Yahoo' && Number.isFinite(yahoo.receivedAt)
    };
  });
  await p.evaluate(() => { Ws.add("intel"); });
  await p.waitForTimeout(300);
  const fpLink = await p.evaluate(() => {
    const intel = Ws.panels.find(x => x.type === "intel");
    const button = intel && intel.root.querySelector("[data-enable-footprint]");
    if (!button) return false;
    button.click();
    const chart = Ws.panels.find(x => x.type === "chart" && x.state.sym === intel.state.sym);
    return !!chart && !!chart.chart && chart.chart.fpOn === true && chart.state.fp === true;
  });
  out.footprintLink = fpLink;
  await p.evaluate(() => { [window.__xpixBook, window.__xpixTape, window.__xpixYahoo].forEach(f => f && f()); });
  await b.close();
  const pass = out.book && out.tape && out.unsupported && out.footprintLink && !errs.length;
  console.log(JSON.stringify({out, errors: errs}), pass ? 'PASS' : 'FAIL');
  process.exit(pass ? 0 : 1);
})();
