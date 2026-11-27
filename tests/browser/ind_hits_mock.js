// MOCK-TESTED ONLY. "What is this?" on the chart (21e_ind_hits.js): a scanner plan is put on the chart, the mouse rests on its label -> card names "Signals (SIG)"
// with the scanner source; a click on the card / a double-click on the label opens the Indicators window on that row and flashes it. MA line + RSI pane are named too.
// Build: python3 -c "from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w',encoding='utf8').write(b(['BTC-USDT','ETH-USDT']))"
// Run:   NODE_PATH=$(npm root -g) node tests/browser/ind_hits_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  const rows = (n, end, step) => { const o = []; let c = 100; for (let i = 0; i < n; i++) { const t = end - i * step; c += Math.sin(i / 7); o.push([String(t), String(c), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); } return o; };
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    const h = { 'access-control-allow-origin': '*' }; if (!/candles/.test(u)) return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: '{"code":"0","data":[]}' });
    const after = +(new URL(u).searchParams.get('after')) || Math.floor(Date.now() / 60000) * 60000 + 60000;
    return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: /history/.test(u) ? [] : rows(300, after - 60000, 60000) }) }); });
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(1200);
  await p.evaluate(() => { const L = Ws.defaults(); Ws.build(L); Ws.save(); }); await p.waitForTimeout(3500);
  const ok = [], bad = [], chk = (c, m) => (c ? ok : bad).push(m);
  // a short plan whose entry is above the last close (pending -> "possible SHORT" label), boxed mode; MA 20 on; RSI pane on
  const g = await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'chart'), ch = P.chart, d = ch.data, last = d[d.length - 1].c, a = ch.avgRange();
    P.setOverlay({ tf: P.state.tf, dir: 'bearish', score: 7, max: 10, ttype: 'day', tags: ['BOS', 'FVG'], plan: { entry: last + 3 * a, stop: last + 5 * a, tps: [last + a, last - a, last - 3 * a], rr: 1 } });
    ch.setupMode = 'box'; ch.mkOn = false; ch.rsiOn = true; ch.maL.forEach((m, j) => m.on = j === 0); ch.calcEma(); ch.resize(); ch.paint();
    const r = ch.cv.getBoundingClientRect(), free = (x, y) => document.elementFromPoint(r.left + x*ch.S, r.top + y*ch.S) === ch.cv;   // a point not covered by a toolbar button
    const log = ch.ihRecord(), lab = log.find(x => x[0] === 'sig' && x[1] === 't' && free(x[2] + x[4]/2, x[3] + x[5]/2)), ma = log.find(x => x[0] === 'ma' && x[1] === 'l' && free((x[2] + x[4])/2, (x[3] + x[5])/2)), pane = (ch._panes || []).find(q => q.k === 'rsi');
    return { S: ch.S, x: r.left, y: r.top, lab, ma, pane, ids: [...new Set(log.map(x => x[0]))] }; });
  chk(g.lab, 'scanner label logged under sig'); chk(g.ma, 'MA line logged under ma'); chk(g.pane, 'RSI pane exists');
  if (!g.lab || !g.ma) { console.log('FAIL', JSON.stringify(g.ids), errs); await b.close(); process.exit(1); }
  const at = (x, y) => [g.x + x * g.S, g.y + y * g.S];
  const [lx, ly] = at(g.lab[2] + g.lab[4] / 2, g.lab[3] + g.lab[5] / 2);
  // 1) rest the mouse: nothing before 3 s, the card after
  await p.evaluate(() => { CFG.ledger = { scanner: { n: 12, sig: 15, lvl: 'lean', win: 58.3, avg: 0.31, style: 'split' } }; });   // the strategy's ledger record shows on the card
  await p.mouse.move(lx - 40, ly + 30); await p.mouse.move(lx, ly, { steps: 4 }); await p.waitForTimeout(1500);
  chk(!(await p.$('.ihtip')), 'no card before the dwell time');
  await p.waitForTimeout(2000); const tip = await p.$('.ihtip'); const tt = tip ? await tip.innerText() : '';
  chk(/SIG/.test(tt) && /scanner|سكانر/i.test(tt) && /BOS/.test(tt) && /Ledger record: 12 trades · win 58.3% · \+0.31R · lean/.test(tt), 'card names Signals (SIG) + scanner source + tags: ' + tt.replace(/\s+/g, ' ').slice(0, 160));
  // 2) click the card -> Indicators window open on the sig row, flashing
  if (tip) { await p.click('.ihtip .ihrow'); await p.waitForTimeout(200); }
  const fl = await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'chart'), row = P.indPop.querySelector('[data-ind="sig"]'); return { open: P.indPop.style.display !== 'none', flash: !!row && row.classList.contains('iflash'), card: !!document.querySelector('.ihtip') }; });
  chk(fl.open && fl.flash && !fl.card, 'card click opens the window + flashes the row ' + JSON.stringify(fl));
  await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'chart'); P.indPop.style.display = 'none'; P.indUI.pin = false; });
  // 3) double-click the MA line -> ma row flashes and the view is NOT re-fitted
  const [mx, my] = at((g.ma[2] + g.ma[4]) / 2, (g.ma[3] + g.ma[5]) / 2);
  const r0 = await p.evaluate(() => Ws.panels.find(q => q.type === 'chart').chart.r);
  await p.mouse.dblclick(mx, my); await p.waitForTimeout(250);
  const d2 = await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'chart'), row = P.indPop.querySelector('[data-ind="ma"]'); return { open: P.indPop.style.display !== 'none', flash: !!row && row.classList.contains('iflash'), r: P.chart.r }; });
  chk(d2.open && d2.flash, 'double-click on the MA line flashes the MA row ' + JSON.stringify(d2)); chk(d2.r === r0, 'view not re-fitted');
  // 4) RSI pane by position
  const rp = await p.evaluate(pn => Ws.panels.find(q => q.type === 'chart').chart.ihAt(50, pn.y0 + pn.h / 2), g.pane); chk(rp[0] === 'rsi', 'RSI pane -> rsi ' + rp);
  // 5) empty area: nothing, and double-click still fits
  const e0 = await p.evaluate(() => Ws.panels.find(q => q.type === 'chart').chart.ihAt(3, 3)); chk(!e0.length || !e0.includes('sig'), 'empty corner -> no sig ' + e0);
  chk(!errs.length, 'no page errors ' + (errs[0] || ''));
  console.log(bad.length ? 'FAIL' : 'PASS', JSON.stringify({ ok: ok.length, bad }));
  await b.close(); process.exit(bad.length ? 1 : 0);
})();
