// MOCK-TESTED ONLY (mocked OKX candles, hand-made trades). Journal "Stop test": every finished trade is replayed on the candles after its entry with the same target and a stop k x the original risk;
// the Journal stats show the average R per stop distance and how many STOPPED trades reached the target later. Run: NODE_PATH=$(npm root -g) node tests/browser/journal_stop_test_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  const H = 3600000, T0 = Math.floor((Date.now() - 20 * H) / H) * H;   // entry bar starts 20 h ago
  // hourly candles (oldest..newest): [t, o, h, l, c]. Trade A (long, entry 100, stop 98 = 2, target 103): bar1 dips to 97.5 (1.25 R) then bar2 reaches 103.5 -> stopped at k=1 / 1.25, wins from 1.5 up.
  // Trade B (long): never dips below 99, reaches the target -> wins at every k. Trade C (long): dips to 95 (2.5 R) and never reaches the target -> loses at every k up to its depth, mark-to-close beyond.
  const mk = (t, h, l, c) => [String(t), String(c), String(h), String(l), String(c), '10', '0', '0', '1'];
  const bars = []; for (let i = 0; i < 40; i++) bars.push(mk(T0 + i * H, 100.4, 99.6, 100));
  bars[1] = mk(T0 + 1 * H, 100.5, 97.5, 99); bars[2] = mk(T0 + 2 * H, 103.5, 99, 103);          // A
  bars[6] = mk(T0 + 6 * H, 103.5, 99.7, 103);                                                     // B: reaches the target the bar after its entry bar (index 5), never below 99.7
  bars[11] = mk(T0 + 11 * H, 100.5, 95, 96);                                                      // C: dips to 95 (2.5 R) the bar after its entry bar (index 10), target never comes
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    const data = /candles/.test(u) ? (/bar=1H/.test(u) ? bars.slice().reverse() : []) : []; return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(1500);
  const out = await p.evaluate(async ([T0, H]) => {
    const base = { symbol: 'BTC-USDT', dir: 'bullish', tfk: '1h', ttype: 'Scalp', entry: 100, sl: 98, tp1: 103, rr: 1.5, score: 8, max: 10, pct: 80, tags: [], fill: true, status: 'sl', r: -1, t0: T0, t1: T0 + 3 * H };
    Journal.list = [Object.assign({}, base, { id: 'A', key: 'A' }), Object.assign({}, base, { id: 'B', key: 'B', status: 'tp', r: 1.5, t0: T0 + 5 * H, t1: T0 + 7 * H }),
      Object.assign({}, base, { id: 'C', key: 'C', t0: T0 + 10 * H, t1: T0 + 12 * H })];
    // B / C bars: B stays inside 99.6..100.4 then reaches 103.5; C dips to 95 and never reaches the target
    await Journal.simStops(); const L = Journal.list.map(t => ({ id: t.id, r: t.stk && t.stk.r, rec: t.stk && t.stk.rec, mae: t.stk && t.stk.mae, full: t.stk && t.stk.full }));
    return { L, tab: (() => { const T = Journal.stopTable(Journal.list); return T && { n: T.n, rec: T.rec, stopped: T.stopped, rows: T.rows.map(r => [r.k, +r.avg.toFixed(2), Math.round(r.win)]) }; })() }; }, [T0, H]);
  await p.evaluate(() => Ws.add('journal')); await p.waitForTimeout(900); out.ui = await p.evaluate(() => { const t = document.body.innerText; return /stop test/i.test(t) && /reached the target later|وبعدين وصلت الهدف/i.test(t); });
  const A = out.L[0], B = out.L[1], C = out.L[2]; const ok = B.r && B.r['1'] === 1.5 && B.r['3'] === 1.5 && B.rec === null && C.r && C.r['1'] === -1 && C.r['2'] === -2 && C.r['3'] > -3 && C.rec === 0 && out.ui && out.tab && out.tab.stopped === 2 && out.tab.rec === 1 && A.r && A.r['1'] === -1 && A.r['1.25'] === -1.25 && A.r['1.5'] === 1.5 && A.r['2'] === 1.5 && A.rec === 1 && Math.abs(A.mae - 1.25) < 1e-6 && !errs.length;
  console.log(JSON.stringify(out), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
