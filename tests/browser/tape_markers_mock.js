// MOCK-TESTED ONLY. Pass = Time & Sales rows have no filled violet / gold background; whale / smart / absorption are small markers beside the price. Optional 3rd arg = screenshot path.
// Run: NODE_PATH=$(npm root -g) node tests/browser/tape_markers_mock.js /tmp/ws.html [/tmp/tape.png]
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 700, height: 420 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(800);
  const res = await p.evaluate(() => { const rows = [
    { side: 'Buy', p: 80900, q: 0.4, notional: 32000, t: Date.now(), tier: 'normal' }, { side: 'Sell', p: 80899, q: 4.2, notional: 340000, t: Date.now(), tier: 'whale', isNew: true },
    { side: 'Buy', p: 80901, q: 1.9, notional: 150000, t: Date.now(), tier: 'smart' }, { side: 'Sell', p: 80898, q: 3.1, notional: 250000, t: Date.now(), tier: 'normal', absorb: true }];
    const d = document.createElement('div'); d.style.cssText = 'position:fixed;inset:0;background:#0b0e11;z-index:99999;width:520px'; d.innerHTML = renderTape({ state: {} }, rows); document.body.append(d);
    const trs = [...d.querySelectorAll('tr')].slice(1); return { marks: d.querySelectorAll('.mk').length, bgs: trs.map(t => t.style.background) }; });
  if (process.argv[3]) await p.screenshot({ path: process.argv[3] });
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
