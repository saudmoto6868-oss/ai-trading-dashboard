// MOCK-TESTED ONLY (mocked OKX + a mocked recorder at FOOTPRINT_SERVER_URL, real Chromium + real IndexedDB). With a recorder configured the page tops its store up from it:
// 90 minutes of history arrive in ONE request, the recorder's listening range is marked known, edge minutes it heard only in part are not claimed, and the chart shows them as complete candles.
// Run: FOOTPRINT_SERVER_URL=https://rec.example.test python3 -c "import sys; sys.path.insert(0,'.'); from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w').write(b(['BTC-USDT']))" && NODE_PATH=$(npm root -g) node tests/browser/footprint_recorder_client_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 140)));
  const NOW = Date.now(), M = 60000, firstMin = Math.ceil((NOW - 90 * M) / M) * M, lastMin = Math.floor(NOW / M) * M; let recReq = 0, histCalls = 0, recUrl = '';
  const mins = {}; for (let m = firstMin - M; m < lastMin; m += M) mins[String(m)] = [100, 3, 2, 100.1, 1, 1];   // one minute BEFORE firstMin is in the answer too (partly heard: must be ignored)
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue();
    if (/rec\.example\.test\/fp/.test(u)) { recReq++; recUrl = u; return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ sym: 'BTC-USDT', cov: [[firstMin - 30000, NOW - 1000]], mins }) }); }
    if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const h = { 'access-control-allow-origin': '*' }; let data = [];
    if (/\/market\/candles/.test(u)) { const m = Math.floor(NOW / M) * M; for (let i = 0; i < 300; i++) data.push([String(m - i * M), '100', '101', '99', '100', '1', '0', '0', '1']); }
    else if (/history-trades/.test(u)) histCalls++;
    return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(800);
  await p.evaluate(async () => { await new Promise(r => { const q = indexedDB.deleteDatabase('xpix_fp'); q.onsuccess = q.onerror = q.onblocked = r; }); localStorage.clear(); });
  await p.reload(); await p.waitForTimeout(800); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2500);
  const res = await p.evaluate(async () => { const P = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0], ch = P.chart; P.state.tf = '1m'; ch.tf = '1m'; P.tfSel.value = '1m'; ch.fpOn = true; P.state.fp = true; P.resub(); await new Promise(r => setTimeout(r, 4500));
    const o = await FPS.load(P.state.sym, 0); let parts = 0, full = 0; ch.fp.forEach(m => { if (m.part) parts++; else full++; }); return { server: CFG.fpServer, storeMinutes: o ? o.mins.size : -1, cov: o ? o.cov : null, chartCandles: ch.fp.size, parts, full }; });
  const ok = res.server === 'https://rec.example.test' && recReq >= 1 && /sym=BTC-USDT/.test(recUrl) && res.storeMinutes >= 85 && res.cov && res.cov.length >= 1 && res.cov[0][0] === firstMin && res.chartCandles >= 60 && res.full >= 60 && !errs.length;
  console.log(JSON.stringify({ res, recReq, histCalls, firstMin }), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
