// MOCK-TESTED ONLY (offline, seeded). Monte Carlo page: the p-value is a zero-mean-null bootstrap test: zero-edge sample -> p not small, strong edge (n=60) -> p small,
// losing sample -> p large; R units x risk% compound as expected; nothing runs on load; the DEMO/not-evidence banner and the n<30 note exist.
// Run: NODE_PATH=$(npm root -g) node tests/browser/montecarlo_pvalue_mock.js modules/montecarlo_app.html
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await (await b.newContext()).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await p.goto('file://' + path.resolve(process.argv[2])); await p.waitForTimeout(1500);
  const res = await p.evaluate(() => {
    const g = (seed, n, mu) => { let a = seed; const r = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
      return Array.from({ length: n }, () => { let s = 0; for (let i = 0; i < 12; i++) s += r(); return +(mu + (s - 6)).toFixed(3); }); };   // ~N(mu, 1) in R
    window.MC_SEED = 7;
    const zero = runMonteCarlo(g(1, 60, 0), 1000, 10000, 20, null, 1), edge = runMonteCarlo(g(2, 60, 0.6), 1000, 10000, 20, null, 1), lose = runMonteCarlo(g(3, 60, -0.6), 1000, 10000, 20, null, 1);
    const flat = runMonteCarlo([1, 1, 1, 1, 1, 1], 1000, 10000, 20, 10, 1);   // +1R at 1 % risk x 10 trades
    const small = runMonteCarlo(g(4, 12, 0.8), 1000, 10000, 20, null, 1);
    return { pZero: zero.pValue, pEdge: edge.pValue, pLose: lose.pValue, flatFinal: Math.round(flat.mean), expectFlat: Math.round(10000 * Math.pow(1.01, 10)), nSmall: small.nTrades,
      status: document.getElementById('status-badge').textContent, banner: !!document.getElementById('demo-banner'), noAutoRun: document.getElementById('kpi-pval').textContent === '—' };
  });
  const ok = res.pZero > 0.1 && res.pEdge < 0.01 && res.pLose > 0.9 && Math.abs(res.flatFinal - res.expectFlat) <= 1 && res.nSmall === 12 && res.banner && res.noAutoRun && res.status === 'Ready' && !errs.length;
  console.log(JSON.stringify(res), 'errors', errs.length, ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
