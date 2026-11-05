// MOCK-TESTED ONLY. The Workspace bar shows "build <short commit>" (CFG.build) so the owner sees which build is live. Run: NODE_PATH=$(npm root -g) node tests/browser/build_stamp_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1500);
  const r = await p.evaluate(() => { const e = document.querySelector('#bar .bld'); return { cfg: CFG.build, txt: e ? e.textContent : null }; });
  const ok = (r.cfg === '' && r.txt === null) || (/^[0-9a-f]{6,40}$/.test(r.cfg) && r.txt === 'build ' + r.cfg); console.log(JSON.stringify(r), 'errors', errs.length, ok && !errs.length ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok && !errs.length ? 0 : 1);
})();
