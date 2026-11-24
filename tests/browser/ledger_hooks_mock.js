// MOCK-TESTED ONLY. Chart strategies -> signal ledger (21f_ledger_hooks.js): payload shape, context snapshot (order flow real / estimate, CVD, regime), one send per plan,
// delivery through a fake journal bridge; the hooks are installed on kzsCalc / paintS26 / gannTrades / paintHarm and a chart with them all on paints without errors.
// Build: python3 -c "from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w',encoding='utf8').write(b(['BTC-USDT','ETH-USDT']))"
// Run:   NODE_PATH=$(npm root -g) node tests/browser/ledger_hooks_mock.js /tmp/ws.html
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
  const r = await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'chart'), ch = P.chart, d = ch.data, n = d.length, got = [];
    Ledger.bridge = () => ({ push: rec => got.push(rec) });
    ch.fp = new Map([[d[n - 1].t, { px: new Map(), b: 30, s: 10 }]]);
    const a1 = ch.ledgerAdd({ src: 'kzs', sub: 'London', tBar: d[n - 2].t, dir: 'long', entry: d[n - 2].c, sl: d[n - 2].c - 1, tps: [d[n - 2].c + 2] });
    const a2 = ch.ledgerAdd({ src: 'kzs', sub: 'London', tBar: d[n - 2].t, dir: 'long', entry: d[n - 2].c, sl: d[n - 2].c - 1, tps: [d[n - 2].c + 2] });   // same plan again
    const a3 = ch.ledgerAdd({ src: 'kzs', sub: 'London', tBar: d[n - 2].t, dir: 'long', entry: d[n - 2].c, sl: d[n - 2].c - 1, tps: [] });   // no target: refused
    const Pr = CandleChart.prototype, hooked = ['kzsCalc', 'paintS26', 'gannTrades', 'paintHarm'].filter(f => /after\.call/.test(String(Pr[f])));
    ch.kzsOn = true; ch.s26On = true; ch.harmOn = true; ch.gannOn = true; ch.paint(); ch.paint();
    return { a1, a2, a3, got, ms: ch.secMs(), last: d[n - 2].t, sym: ch.sym, tf: ch.tf, hooked }; });
  const g = r.got[0] || {};
  chk(r.a1 === true && r.a2 === false && r.a3 === false, 'one send per plan, plans without a target refused ' + JSON.stringify([r.a1, r.a2, r.a3]));
  chk(g.kind === 'sig' && /^sig:/.test(g.id) && g.src === 'kzs' && g.sub === 'London' && g.symbol === r.sym && g.tf === String(r.tf).toLowerCase(), 'payload shape ' + JSON.stringify(g).slice(0, 200));
  chk(g.t0 === r.last + r.ms, 't0 = the next candle after the signal candle (no look-ahead)');
  chk(g.ctx && g.ctx.of_real === true && g.ctx.delta_pct === 75 && g.ctx.of === 'with' && 'cvd' in g.ctx, 'order-flow snapshot: real 75% buy -> with the long ' + JSON.stringify(g.ctx));
  chk(r.hooked.length === 4, 'hooks installed ' + r.hooked);
  chk(r.got.every(x => x.t0 >= r.last), 'every sent plan is forward-only (t0 after the newest closed candle) n=' + r.got.length);
  chk(!errs.length, 'no page errors ' + (errs[0] || ''));
  console.log(bad.length ? 'FAIL' : 'PASS', JSON.stringify({ ok: ok.length, bad, sent: r.got.length }));
  await b.close(); process.exit(bad.length ? 1 : 0);
})();
