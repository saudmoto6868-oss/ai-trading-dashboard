// MOCK-TESTED ONLY (TradingView itself is blocked: the test checks what the page sends to the widget). TradingView widget settings are kept: interval, chart type and indicators go into the widget URL on every load,
// are saved with the workspace, and a TradingView widget opened later starts from the last choice. Run: NODE_PATH=$(npm root -g) node tests/browser/tv_settings_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (/tradingview\.com/.test(u)) return r.fulfill({ status: 200, contentType: 'text/html', body: '<html><body>tv</body></html>' }); return r.abort(); });
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(1000);
  const cfg = () => p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'tvc'); const f = P && P.body.querySelector('iframe'); if (!f) return null; const h = JSON.parse(decodeURIComponent(f.src.split('#')[1])); return { interval: h.interval, style: h.style, studies: h.studies, saved: JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k => /_tvset$/.test(k)) || 'x') || 'null') }; });
  await p.evaluate(() => { Ws.clear(); Ws.add('tvc'); }); await p.waitForTimeout(800);
  const r0 = await cfg();
  await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'tvc'); const sel = P.body.querySelectorAll('select'); const tf = [...sel].find(x => [...x.options].some(o => o.value === '60')); tf.value = '60'; tf.dispatchEvent(new Event('change')); });
  await p.waitForTimeout(300);
  await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'tvc'); [...P.body.querySelectorAll('button')].find(x => x.textContent === 'ƒx').click(); });
  await p.waitForTimeout(200);
  await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'tvc'); const pop = P.body.querySelector('.tvpop'); const cbs = [...pop.querySelectorAll('input[type=checkbox]')]; [0, 1].forEach(i => { cbs[i].checked = true; cbs[i].dispatchEvent(new Event('change')); }); const st = pop.querySelector('select'); st.value = '8'; st.dispatchEvent(new Event('change')); });
  await p.waitForTimeout(400);
  const r1 = await cfg();
  // close the widget, open a new one: starts from the last choice
  await p.evaluate(() => { Ws.clear(); Ws.add('tvc'); }); await p.waitForTimeout(800); const r2 = await cfg();
  // reload the page: the workspace (and its widget settings) come back
  await p.evaluate(() => Ws.save()); await p.reload(); await p.waitForTimeout(1500); const r3 = await cfg();
  const ok = r0 && r0.interval === '15' && r0.studies.length === 0 && r1.interval === '60' && r1.style === '8' && r1.studies.length === 2 && r1.saved && r1.saved.tvtf === '60'
    && r2 && r2.interval === '60' && r2.style === '8' && r2.studies.length === 2 && r3 && r3.interval === '60' && r3.studies.length === 2 && !errs.length;
  console.log(JSON.stringify({ r0, r1, r2, r3 }), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
