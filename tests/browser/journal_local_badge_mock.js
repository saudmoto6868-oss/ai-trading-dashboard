// MOCK-TESTED ONLY (mocked OKX, no data): the Journal panel shows a "local / not evidence" note (DECISIONS #1).
// Run: NODE_PATH=$(npm root -g) node tests/browser/journal_local_badge_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); return r.abort(); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000);
  await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(1200);
  await p.evaluate(() => Ws.add('journal')); await p.waitForTimeout(900);
  const txt = await p.evaluate(() => { const e = document.querySelector('.jlocal'); return e ? e.textContent : null; });
  const ok = !!txt && /Local|محلي/.test(txt) && errs.length === 0;
  console.log(JSON.stringify(txt), 'errors', errs.length, ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
