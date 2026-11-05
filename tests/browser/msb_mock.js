// MSB indicator (port of EmreKb MSB-OB): synthetic zigzag -> must produce bull + bear breaks with OB/BB boxes; chart paints without errors (mock-tested only)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1400, height: 800 } })).newPage(); const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(800);
  const r = await p.evaluate(() => {
    const D = []; let px = 100; const legs = [[30,1],[30,-1.1],[30,1.2],[30,-1.3],[30,1.4],[30,-2.8],[30,1.5],[30,-1.7],[30,1.9],[30,-2],[30,4],[14,-2]];
    let t = 1.7e9, k = 0; legs.forEach(([len, sl]) => { for (let i = 0; i < len; i++){ const o = px; px += sl + Math.sin(k*1.7)*.4; k++; D.push({t: t += 300, o, c: px, h: Math.max(o, px) + .3, l: Math.min(o, px) - .3, v: 1}); } });
    const R = msbCalc(D, 9, 0.33);
    Ws.build([['chart', {x:10,y:10,w:1000,h:600}, {sym:'BTC-USDT', tf:'5m', group:0, msb:true}]]);
    const ch = Ws.panels[0].chart; ch.data = D; ch.resize && ch.resize(); ch.paint();
    const S = ch.st.msb; ch.st.msb.fib = 0.9; ch.paint(); const k1 = ch._msb.k; ch.st.msb.fib = 0.237; ch.st.msb.del = 0; ch.st.msb.zz = 0; ch.paint();
    return {def: S.fib === 0.237 && S.zl === 9, recalc: k1 !== ch._msb.k, ev: R.ev.length, bull: R.ev.filter(e => e.bull).length, bear: R.ev.filter(e => !e.bull).length, boxes: R.boxes.length, labels: [...new Set(R.boxes.map(x => x.lbl))], zz: R.zz.length, on: ch.msbOn, painted: !!ch._msb};
  });
  console.log(JSON.stringify(r), 'errors', errs.length, (r.ev >= 2 && r.bull >= 1 && r.bear >= 1 && r.boxes >= 4 && r.on && r.painted && r.def && r.recalc && !errs.length) ? 'PASS' : 'FAIL', errs[0] || ''); await b.close();
})();
