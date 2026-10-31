// MOCK-TESTED ONLY (real Chromium + real IndexedDB, no network). Book heat-map history: (1) legacy history that only exists in localStorage is saved to IndexedDB on the next save,
// (2) the localStorage copy is removed only after IndexedDB confirmed the write, (3) after a reload the history comes back from IndexedDB.
// Run: python3 -c "import sys; sys.path.insert(0,'.'); from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w').write(b(['BTC-USDT']))" && NODE_PATH=$(npm root -g) node tests/browser/book_store_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1600, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 140)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  const url = 'file://' + process.argv[2]; await p.goto(url); await p.waitForTimeout(800);
  await p.evaluate(async () => { await new Promise(r => { const q = indexedDB.deleteDatabase('xpix_fp'); q.onsuccess = q.onerror = q.onblocked = r; }); localStorage.clear();
    const now = Date.now(), M = 60000, base = Math.floor(now / M) * M, bk = {}; for (let i = 120; i >= 1; i--) bk[base - i * M] = { w: 60000, m: 100, c: [[1000, 5], [1001, 9], [1002, 2]] };
    localStorage.setItem('ai_ws_v5_hm_BTC-USDT', JSON.stringify({ step: 0.1, b: bk })); });
  const open = async () => { await p.reload(); await p.waitForTimeout(800); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2500); };
  await open();
  const r1 = await p.evaluate(async () => { const ch = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0].chart; ch.hmSym = null; ch.sym = 'BTC-USDT'; ch.hmInit(); await new Promise(r => setTimeout(r, 300));
    const before = ch.hm.b.size; ch.hmSave(Date.now()); await new Promise(r => setTimeout(r, 800)); const idb = await FPS.getHm('BTC-USDT');
    return { before, idb: idb ? Object.keys(idb.b).length : 0, lsLeft: localStorage.getItem('ai_ws_v5_hm_BTC-USDT') !== null }; });
  await open();
  const r2 = await p.evaluate(async () => { const ch = Ws.panels.filter(q => q.type === 'chart' && q.chart)[0].chart; ch.hmSym = null; ch.sym = 'BTC-USDT'; ch.hmInit(); await new Promise(r => setTimeout(r, 600)); return { restored: ch.hm.b.size, step: ch.hm.step }; });
  const ok = r1.before === 120 && r1.idb === 120 && !r1.lsLeft && r2.restored === 120 && r2.step === 0.1 && !errs.length;
  console.log(JSON.stringify({ r1, r2 }), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
