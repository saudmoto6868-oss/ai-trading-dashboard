// MOCK-TESTED ONLY (no network). The STANDARD layout (owner 2026-11-05): a fresh browser / any automation opens the workspace with the watch list, four linked charts (5m / 15m / 4H / 1D) with the order-flow column
// open (no auto-centre since 2026-11-09: the chart moves only when you move it), DOM / Limit tracking / Time & Sales on the right, no tall strip on top - never an empty workspace. "Blank" stays blank after a reload; "Save current layout as my standard" replaces it.
// Build the page with symbols that include HL:xyz:GOLD. Run: NODE_PATH=$(npm root -g) node tests/browser/standard_layout_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  const URL = 'file://' + process.argv[2], snap = () => p.evaluate(() => ({ types: Ws.panels.map(q => q.type), tfs: Ws.panels.filter(q => q.type === 'chart').map(q => q.state.tf), syms: Ws.panels.filter(q => q.type === 'chart').map(q => q.state.sym),
    of: Ws.panels.filter(q => q.type === 'chart').every(q => q.chart.colOn && q.chart.domOn), noAc: Ws.panels.filter(q => q.type === 'chart').every(q => q.state.ac === undefined), tops: Ws.panels.map(q => q.rect.y), hs: Ws.panels.filter(q => q.type === 'chart').map(q => q.rect.h),
    ws: Ws.panels.filter(q => q.type === 'chart').map(q => q.rect.w), opts: [...document.querySelectorAll('#bar select option')].map(o => o.value).filter(v => v.startsWith('@')), x: window.XCMD ? XCMD.state().panels.length : 0 }));
  await p.goto(URL); await p.waitForTimeout(2500); const A = await snap();                                   // 1) fresh browser
  await p.evaluate(() => { const o = document.querySelector('#bar select'); o.value = '@blank'; o.onchange(); }); await p.waitForTimeout(500); await p.goto(URL); await p.waitForTimeout(1500); const B = await snap();   // 2) blank stays blank
  await p.evaluate(() => { const o = document.querySelector('#bar select'); o.value = '@std'; o.onchange(); }); await p.waitForTimeout(800); const C = await snap();   // 3) "Standard" brings it back
  p.on('dialog', d => d.accept());
  await p.evaluate(() => { Ws.panels.find(q => q.type === 'tape').close(); const o = document.querySelector('#bar select'); o.value = '@save'; o.onchange(); }); await p.waitForTimeout(500);   // 4) my own standard: 7 panels
  await p.evaluate(() => { localStorage.removeItem('ai_ws_v5'); try { sessionStorage.clear(); } catch(e){} }); await p.goto(URL); await p.waitForTimeout(1500); const D = await snap();
  await p.evaluate(() => { localStorage.removeItem('ai_ws_v5_std'); }); await p.evaluate(() => { const o = document.querySelector('#bar select'); o.value = '@std'; o.onchange(); }); await p.waitForTimeout(500); const E = await snap();   // 5) no saved standard: the built-in one again
  const okA = A.types.length === 8 && A.types[0] === 'watch' && A.types.filter(t => t === 'chart').length === 4 && !A.types.includes('signals') && ['dom', 'limits', 'tape'].every(t => A.types.includes(t)) && JSON.stringify(A.tfs) === JSON.stringify(['5m', '15m', '4H', '1D']) && A.of && A.noAc && A.tops.every(y => y === 0 || y > 100) && Math.min(...A.hs) >= 300 && A.x === 8 && A.syms.every(s => s === 'HL:xyz:GOLD');
  const okB = B.types.length === 0, okC = C.types.length === 8, okD = D.types.length === 7 && !D.types.includes('tape') && D.types.filter(t => t === 'chart').length === 4, okE = E.types.length === 8, okO = A.opts.includes('@std') && A.opts.includes('@save') && A.opts.includes('@blank');
  console.log(JSON.stringify({ A, B: B.types.length, C: C.types.length, D: D.types.length, E: E.types.length }), 'errors', errs.length, errs[0] || '', okA && okB && okC && okD && okE && okO && !errs.length ? 'PASS' : 'FAIL', JSON.stringify({ okA, okB, okC, okD, okE, okO })); await b.close(); process.exit(okA && okB && okC && okD && okE && okO && !errs.length ? 0 : 1);
})();
