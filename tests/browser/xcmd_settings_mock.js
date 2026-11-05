// MOCK-TESTED ONLY. XCMD step 2: params / setParam (validated, same fields as the gear panel) and layout(standard|blank|save).
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1500);   // default = the standard layout
  const r = await p.evaluate(() => {
    const X = XCMD, o = {}; o.std = X.state().panels.length; const g = X.params('msb'); o.hasParams = g.ok && g.params.some(q => q.key === 'fib' && q.value === 0.237) && g.params.some(q => q.key === 'obuF' && q.type === 'color');
    o.fib = X.setParam('msb', 'fib', 0.5); o.fibV = X.params('msb').params.find(q => q.key === 'fib').value;
    o.bad = [X.setParam('msb', 'fib', 7), X.setParam('msb', 'nope', 1), X.setParam('msb', 'obuF', 'red'), X.setParam('vwap', 'x', 1), X.setParam('msb', 'tx', 99), X.setParam('msb', 'zl', 'abc')].every(q => !q.ok);
    o.sel = X.setParam('msb', 'tx', '12'); o.bool = X.setParam('msb', 'del', 'off'); o.boolV = X.params('msb').params.find(q => q.key === 'del').value; o.col = X.setParam('msb', 'obuF', '#112233');
    o.saved = Ws.panels.find(q => q.type === 'chart').state.st.msb.fib;
    o.blank = X.layout('blank'); o.blankN = X.state().panels.length; o.stdBack = X.layout('standard'); o.stdN = X.state().panels.length; o.save = X.layout('save'); o.badLayout = X.layout('x');
    return o; });
  const ok = r.std === 8 && r.hasParams && r.fib.ok && r.fibV === 0.5 && r.bad && r.sel.ok && r.bool.ok && r.boolV === 0 && r.col.ok && r.saved === 0.5 && r.blank.ok && r.blankN === 0 && r.stdBack.ok && r.stdN === 8 && r.save.ok && !r.badLayout.ok && !errs.length;
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
