// MOCK-TESTED ONLY. Intermarket SMT (CFG.smt) shows as its own chip FIRST on the live-setups strip and as a block on top of the Signals widget; click = the pair on two charts, same timeframe.
// Needs an html built with smt=[chip]:  python3 -c "...build_workspace_html(['BTC-USDT','ETH-USDT'], smt=chips)" > /tmp/ws_smt.html ; node tests/browser/smt_strip_mock.js /tmp/ws_smt.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1600, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(900);
  await p.evaluate(() => { Ws.build([['chart', { x: 10, y: 10, w: 600, h: 400 }, { sym: 'SOL-USDT', tf: '5m', group: 0 }], ['chart', { x: 620, y: 10, w: 600, h: 400 }, { sym: 'SOL-USDT', tf: '5m', group: 0 }], ['signals', { x: 10, y: 420, w: 800, h: 300 }, {}]]); Ws.drawStrip(); }); await p.waitForTimeout(1500);
  const r = await p.evaluate(async () => { const o = {}; const chip = document.querySelector('#strip .chip'); o.chip = chip ? chip.textContent : null; o.chipFirst = !!chip && /Bitcoin\/Ethereum/.test(chip.textContent) && /SMT/.test(chip.textContent) && !/%/.test(chip.textContent);
    o.title = chip && chip.title; chip && chip.click(); await new Promise(r => setTimeout(r, 400)); const cs = Ws.panels.filter(q => q.type === 'chart'); o.syms = cs.map(c => c.state.sym); o.tfs = cs.map(c => c.state.tf);
    const sg = Ws.panels.find(q => q.type === 'signals'); o.block = sg ? /SMT/.test(sg.body.textContent) && /Bitcoin/.test(sg.body.textContent) : null; return o; });
  const ok = r.chipFirst && r.syms[0] === 'BTC-USDT' && r.syms[1] === 'ETH-USDT' && /1h/i.test(r.tfs[0]) && r.tfs[0] === r.tfs[1] && !errs.length;
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
