// MOCK-TESTED ONLY (mocked OKX, real Chromium). A journal trade gets its chain layers + grade (Chain.tag, async from the setup's candles); the Journal stats show the grade / location tables; CSV has the new columns.
// Run: NODE_PATH=$(npm root -g) node tests/browser/journal_chain_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100;
    for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2 + 0.05; o.push([String(now - (300 - i) * 3600000), String(c - 0.5), String(c + 1), String(c - 1), String(c), String(10 + (i % 5)), '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: o }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1500);
  const res = await p.evaluate(async () => {
    Journal.list = []; const px = 100;
    const e = { symbol: 'BTC-USDT', direction: 'bullish', ttype: 'Scalp', tfk: '1h', score: 9, max: 10, tags: [['ob']], plan: { entry: px, stop: px - 2, tps: [px + 4, px + 6] } };
    CFG.ready = [e]; Journal.cfg.min = 0; Journal.cfg.rr = 0; Journal.ingest(); await new Promise(r => setTimeout(r, 2500));
    const rec = Journal.list[0]; const out = { logged: Journal.list.length, chain: rec && rec.chain || null };
    // a second, already closed trade so the stats tables have rows
    Journal.list.push(Object.assign({}, rec, { id: 'x2', key: 'x2', status: 'tp', r: 1.5, t1: Date.now(), chain: { htf: true, loc: false, vol: false, reg: true, time: true, g: 'A' } }));
    const st = Journal.stats(0, 0); out.closed = st.closed.length;
    const rows = Journal.list.filter(t => t.chain).map(t => t.chain.g); out.grades = rows;
    Ws.add('journal'); await new Promise(r => setTimeout(r, 800)); const txt = document.body.innerText; out.ui = /chain grade|درجة السلسلة/i.test(txt) && /location layer|طبقة الموقع/i.test(txt);
    return out; });
  const ok = res.logged === 1 && res.chain && ['A+++', 'A+', 'A', 'B', 'C'].includes(res.chain.g) && 'htf' in res.chain && 'loc' in res.chain && res.ui && !errs.length;
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
