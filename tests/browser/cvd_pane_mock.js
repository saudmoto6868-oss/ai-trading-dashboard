// MOCK-TESTED ONLY. CVD pane (paintCvd) + footprint coverage notice (paintFp, 2026-11-24): 3 candles get fake footprint trades -> CVD says "real on 3/N",
// the real part is computed from the trades (buy - sell), the rest is the candle-shape estimate; the footprint notice counts the same candles; the hover card names the CVD pane.
// Build: python3 -c "from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w',encoding='utf8').write(b(['BTC-USDT','ETH-USDT']))"
// Run:   NODE_PATH=$(npm root -g) node tests/browser/cvd_pane_mock.js /tmp/ws.html
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
  const r = await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'chart'), ch = P.chart, d = ch.data, n = d.length;
    ch.fp = new Map(); [n - 3, n - 2, n - 1].forEach((i, j) => ch.fp.set(d[i].t, { px: new Map([[d[i].c, { b: 10 + j, s: 4 }]]), b: 10 + j, s: 4 }));
    const it = P.indItems.find(x => x.id === 'cvd'); it.set(true); ch.fpOn = true; ch.paint();
    const i1 = n - 1, i0 = Math.max(0, n - 40), S = ch.cvdSeries(i0, i1), real = S.filter(q => q.real);
    const pane = ch._panes.find(q => q.k === 'cvd'), hit = pane ? ch.ihAt(50, pane.y0 + pane.h / 2) : [];
    // estimate for a candle without trades: v * ((c-l)-(h-c))/(h-l)
    const e = S.find(q => !q.real), k = d[e.i], est = k.v * (((k.c - k.l) - (k.h - k.c)) / (k.h - k.l));
    return { real: real.map(q => q.d), nS: S.length, pane: !!pane, hit, estOk: Math.abs(e.d - est) < 1e-9, fpHave: ch.fpHave, info: ch.indInfo('cvd'), saved: !!P.state.cvd }; });
  chk(JSON.stringify(r.real) === '[6,7,8]', 'real delta = buy - sell on the 3 footprint candles ' + JSON.stringify(r.real));
  chk(r.estOk, 'other candles use the candle-shape estimate');
  chk(r.pane && r.hit[0] === 'cvd', 'CVD pane drawn and named by the hover card ' + JSON.stringify(r.hit));
  chk(r.fpHave && r.fpHave.have === 3 && r.fpHave.tot > 3, 'footprint notice counts 3 real candles ' + JSON.stringify(r.fpHave));
  chk(r.info && /CVD/.test(r.info.label) && r.saved, 'menu row + saved state');
  chk(!errs.length, 'no page errors ' + (errs[0] || ''));
  console.log(bad.length ? 'FAIL' : 'PASS', JSON.stringify({ ok: ok.length, bad }));
  await b.close(); process.exit(bad.length ? 1 : 0);
})();
