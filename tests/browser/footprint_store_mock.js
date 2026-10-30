// MOCK-TESTED ONLY (mocked OKX, real Chromium + real IndexedDB). Footprint store: (1) a first session fills 12 candles and stores them, (2) the page is closed and reopened 5 minutes later:
// the older candles come from the store, only the 5 new minutes are fetched, nothing is counted twice, and the known range is one piece.
// Run: python3 -c "import sys; sys.path.insert(0,'.'); from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w').write(b(['BTC-USDT']))" && NODE_PATH=$(npm root -g) node tests/browser/footprint_store_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const ctx = await b.newContext({ viewport: { width: 1600, height: 900 } }), p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 140)));
  let NOW = Math.floor(Date.now() / 60000) * 60000 + 30000, nowOff = 0, calls = 0; const N = 1500;   // 1 print every 2 s
  const trade = n => ({ instId: 'BTC-USDT', tradeId: String(1000000 + nowOff - n), px: String(100 + (n % 5) * 0.1), sz: '1', side: n % 2 ? 'sell' : 'buy', ts: String(NOW - n * 2000) });
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const h = { 'access-control-allow-origin': '*' }; let data = [];
    if (/\/market\/candles/.test(u)) { const m = Math.floor(NOW / 60000) * 60000; for (let i = 0; i < 300; i++) data.push([String(m - i * 60000), '100', '101', '99', '100', '1', '0', '0', '1']); }
    else if (/history-trades/.test(u)) { calls++; const a = (u.match(/after=(\d+)/) || [])[1], start = a ? (1000000 + nowOff) - (+a) + 1 : 0; for (let n = start; n < Math.min(N, start + 100); n++) data.push(trade(n)); }
    else if (/\/market\/trades/.test(u)) { for (let n = 0; n < 3; n++) data.push(trade(n)); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data }) }); });
  const url = 'file://' + process.argv[2];
  await p.goto(url); await p.waitForTimeout(800);
  await p.evaluate(async () => { await new Promise(r => { const q = indexedDB.deleteDatabase('xpix_fp'); q.onsuccess = q.onerror = q.onblocked = r; }); localStorage.clear(); });
  const setup = async () => { await p.reload(); await p.waitForTimeout(800); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2500);
    await p.evaluate(async () => { const P = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0]; P.state.tf = '1m'; P.chart.tf = '1m'; P.tfSel.value = '1m'; P.resub(); await new Promise(r => setTimeout(r, 3500)); }); };
  const probe = () => p.evaluate(async () => { const P = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0], ch = P.chart; ch.fpOn = true; P.state.fp = true; P._fpFilled = null;
    await P.fpFill(); await new Promise(r => setTimeout(r, 500)); let tot = 0, parts = 0; ch.fp.forEach(m => { tot += m.b + m.s; if (m.part) parts++; });
    const o = await FPS.load(P.state.sym, 0); let st = 0; o.mins.forEach(a => { for (let j = 0; j + 2 < a.length; j += 3) st += a[j + 1] + a[j + 2]; }); return { candles: ch.fp.size, tot, parts, cov: o.cov, storedTotal: st }; });
  await setup(); const s1 = await probe(), c1 = calls;
  nowOff = 150; NOW += 300000;   // the app was closed for 5 minutes: 150 more prints
  await setup(); const s2 = await probe(), c2 = calls - c1;
  const ok = s1.tot > 200 && s1.tot === s1.storedTotal && s2.tot === s2.storedTotal && s2.storedTotal === s1.storedTotal + 150 && s2.cov.length === 1 && s2.parts === 0 && s2.candles > s1.candles && c2 < c1 && !errs.length;
  console.log(JSON.stringify({ s1, s2, callsFirst: c1, callsSecond: c2 }), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
