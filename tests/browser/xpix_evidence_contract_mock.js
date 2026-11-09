// XPIX Intelligence evidence contract regression.
// Verifies shared Hub payload metadata, exchange-vs-received timestamps, and explicit Yahoo unsupported capability.
// Run: NODE_PATH=$(npm root -g) node tests/browser/xpix_evidence_contract_mock.js /tmp/ws.html
const { chromium } = require('playwright');
const fs = require('fs');
const bundle = fs.readFileSync(process.argv[2], 'utf8');
const tradeDedupeGuard = bundle.includes('if (seen.size > 6000){ const it=seen.values(); for(let i=0;i<2000;i++){const v=it.next();if(v.done)break;seen.delete(v.value);} }') && !bundle.includes('if (seen.size > 6000){ seen.clear(); }');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 180)));
  const J = d => ({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: d }) });
  await p.route('**/*', r => {
    const u = r.request().url();
    if (u.startsWith('file:')) return r.continue();
    if (!u.includes("okx.com/api/v5")) return r.abort();
    if (u.includes("/market/books-full") || u.includes("/market/books?")) {
      const lv = (px, step) => Array.from({length: 60}, (_, i) => [String(px + i * step), String(2 + i % 4), '0', '1']);
      return r.fulfill(J([{ bids: lv(60000, -1), asks: lv(60001, 1), ts: String(Date.now() - 250) }]));
    }
    if (u.includes("/market/trades")) return r.fulfill(J(Array.from({length: 12}, (_, i) => ({
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
  out.tabContract = await p.evaluate(() => {
    const intel = Ws.panels.find(x => x.type === "intel");
    const labels = intel ? [...intel.root.querySelectorAll(".seg button")].map(x => x.textContent.trim()) : [];
    const en = ["Overview", "Order Flow", "Liquidity", "Auction / Volume", "Setups", "Indicators"];
    const ar = ["نظرة عامة", "الأوردر فلو", "السيولة", "المزاد والحجم", "الفرص", "المؤشرات"];
    return JSON.stringify(labels) === JSON.stringify(en) || JSON.stringify(labels) === JSON.stringify(ar);
  });
  const fpLink = await p.evaluate(() => {
    const intel = Ws.panels.find(x => x.type === "intel");
    const flowTab = intel && [...intel.root.querySelectorAll(".seg button")].find(x => /Order Flow|الأوردر فلو/.test(x.textContent));
    if (!flowTab) return false;
    flowTab.click();
    const button = intel.root.querySelector("[data-enable-footprint]");
    if (!button) return false;
    button.click();
    const chart = Ws.panels.find(x => x.type === "chart" && x.state.sym === intel.state.sym);
    return !!chart && !!chart.chart && chart.chart.fpOn === true && chart.state.fp === true;
  });
  out.footprintLink = fpLink;
  const liquidityPreview = await p.evaluate(() => {
    const intel = Ws.panels.find(x => x.type === "intel");
    const tab = intel && [...intel.root.querySelectorAll(".seg button")].find(x => /Liquidity|السيولة/.test(x.textContent));
    if (!tab) return false;
    tab.click();
    const table = intel.root.querySelector("table.rdt");
    return !!table && table.querySelectorAll("tr").length >= 2 &&
      /OKX public venue snapshot|لقطة دفتر OKX العامة/.test(intel.root.textContent);
  });
  out.liquidityPreview = liquidityPreview;
  const downstream = await p.evaluate(() => {
    const intel = Ws.panels.find(x => x.type === "intel");
    if (!intel) return { auction: false, indicators: false, waitState: false };
    // Inject deterministic source-panel fixtures; the UI still renders through its real panel readers.
    Ws.panels.push({
      type: "valuelv", state: { sym: intel.state.sym },
      levelsData: { "5m": { vp: { vah: 60200, poc: 60000, val: 59800 }, px: 60300 } }
    });
    const chart = Ws.panels.find(x => x.type === "chart" && x.state.sym === intel.state.sym);
    if (chart) chart.indItems = [
      { id: "fixture", label: "Contract Fixture <safe>", get: () => true, set: () => {} }
    ];
    const clickTab = re => {
      const btn = [...intel.root.querySelectorAll(".seg button")].find(x => re.test(x.textContent));
      if (!btn) return false;
      btn.click();
      return true;
    };
    const auctionTab = clickTab(/Auction|المزاد/);
    const auction = auctionTab && /60[,]?000/.test(intel.root.textContent) &&
      /Above value|فوق القيمة/.test(intel.root.textContent);
    const indicatorsTab = clickTab(/Indicators|المؤشرات/);
    const indicators = indicatorsTab && /Contract Fixture/.test(intel.root.textContent) &&
      /ON|مفعّل/.test(intel.root.textContent) && !intel.root.innerHTML.includes("<safe>");
    const setupsTab = clickTab(/Setups|الفرص/);
    const waitState = setupsTab && /WAIT|انتظار/.test(intel.root.textContent) &&
      !/\b(?:BUY|SELL)\s*[:=]/.test(intel.root.textContent);
    Ws.panels = Ws.panels.filter(x => x.type !== "valuelv");
    return { auction, indicators, waitState };
  });
  Object.assign(out, downstream);
  await p.evaluate(() => { [window.__xpixBook, window.__xpixTape, window.__xpixYahoo].forEach(f => f && f()); });
  await b.close();
  out.tradeDedupeGuard = tradeDedupeGuard;
  const pass = tradeDedupeGuard && out.book && out.tape && out.unsupported && out.tabContract && out.footprintLink &&
    out.liquidityPreview && out.auction && out.indicators && out.waitState && !errs.length;
  console.log(JSON.stringify({out, errors: errs}), pass ? 'PASS' : 'FAIL');
  process.exit(pass ? 0 : 1);
})();
