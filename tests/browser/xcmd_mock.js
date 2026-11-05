// MOCK-TESTED ONLY (mocked OKX candles). window.XCMD (docs/XPIX_BOT_BRIEF.md): state, setSymbol, setTf, toggle, draw, clearDrawings, addPanel/closePanel (allow-list), shot, and refusals.
// Run: NODE_PATH=$(npm root -g) node tests/browser/xcmd_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  const H = 3600000, T0 = Math.floor(Date.now() / H) * H - 120 * H, bars = [];
  for (let i = 0; i < 120; i++) { const c = 100 + Math.sin(i / 7) * 5; bars.push([String(T0 + i * H), String(c), String(c + 1), String(c - 1), String(c + 0.3), '10', '0', '0', '1']); }
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    const data = /candles/.test(u) ? bars.slice().reverse() : []; return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', msg: '', data }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000);
  await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2500);
  const r = await p.evaluate(async () => {
    const X = window.XCMD, o = {}; o.frozen = Object.isFrozen(X); const st = X.state(); o.st = st.ok && st.panels.some(q => q.type === 'chart'); const cp = st.panels.find(q => q.type === 'chart');
    o.list = X.list(); o.lastT = null;
    o.badSym = X.setSymbol('NOPE-USDT'); o.badTf = X.setTf('99x'); o.badType = X.addPanel('web'); o.badType2 = X.addPanel('x;alert(1)'); o.badInd = X.toggle('nope', true);
    o.tf = X.setTf('4H'); await new Promise(r => setTimeout(r, 400));
    o.vw0 = X.toggle('vwap', true); o.vwOn = X.state().panels.find(q => q.id === cp.id).ind.includes('vwap'); o.vw1 = X.toggle('vwap', false); o.vwOff = !X.state().panels.find(q => q.id === cp.id).ind.includes('vwap');
    const before = X.state().panels.find(q => q.id === cp.id).draws;
    o.d1 = X.draw({ kind: 'hline', price: 101.5, color: '#f0b90b', label: 'support' }); o.d2 = X.draw({ kind: 'text', price: 104, text: 'watch here' }); o.d3 = X.draw({ kind: 'trend', points: [{ p: 98 }, { p: 105 }] }); o.dbad = X.draw({ kind: 'cross', price: 1 }); o.dbad2 = X.draw({ kind: 'hline', price: 'abc' });
    o.draws = X.state().panels.find(q => q.id === cp.id).draws - before;
    o.add = X.addPanel('news'); o.close = o.add.ok ? X.closePanel(o.add.id) : null; o.closeBad = X.closePanel('zzz');
    o.shot = await X.shot(1); o.shotOk = o.shot.ok && /^data:image\/png;base64,/.test(o.shot.png) && o.shot.w > 200; delete o.shot.png;
    o.clr = X.clearDrawings(); o.after = X.state().panels.find(q => q.id === cp.id).draws; o.noEval = typeof X.eval === 'undefined' && typeof X.order === 'undefined';
    return o; });
  const ok = r.frozen && r.st && r.list.ok && r.list.ind.includes('vwap') && !r.badSym.ok && !r.badTf.ok && !r.badType.ok && !r.badType2.ok && !r.badInd.ok && r.tf.ok && r.vw0.ok && r.vwOn && r.vw1.ok && r.vwOff
    && r.d1.ok && r.d2.ok && r.d3.ok && !r.dbad.ok && !r.dbad2.ok && r.draws === 3 && r.add.ok && r.close.ok && !r.closeBad.ok && r.shotOk && r.clr.ok && r.clr.removed >= 3 && r.after === 0 && r.noEval && errs.length === 0;
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
