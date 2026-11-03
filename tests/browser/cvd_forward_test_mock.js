// MOCK-TESTED ONLY (mocked OKX, hand-made candles + footprint). CVD divergence v1 forward test: a divergence on the bar that has JUST closed is logged once (type "div"), kept separate from the
// Flow-confluence rows in the log and in the stats. Description + evidence gate, not a signal. Run: NODE_PATH=$(npm root -g) node tests/browser/cvd_forward_test_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100;
    for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2; o.push([String(now - (300 - i) * 3600000), String(c - 0.5), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: o }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2500);
  const res = await p.evaluate(() => { const P = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length), ch = P.chart; FlowTest.clear();
    // 30 bars: highs climb, delta +10 per bar (CVD climbs); the bar BEFORE the live one (i = n-2) makes a new high with delta -100 -> CVD below its previous peak = bearish divergence on a closed bar
    const n = 30, t0 = ch.data[ch.data.length - 1].t - n * 3600000; ch.data = Array.from({ length: n }, (_, i) => ({ t: t0 + i * 3600000, o: 100 + i, h: 101 + i + (i === n - 2 ? 5 : 0), l: 99 + i, c: 100.5 + i, v: 10 }));
    ch.fp = new Map(); ch.data.forEach((d, i) => ch.fp.set(d.t, { px: new Map(), b: i === n - 2 ? 0 : 20, s: i === n - 2 ? 100 : 10 })); ch.fpOn = true;
    const A = ch.cvdAn(ch.data, ch.fp, 12), seen = A.div.map(x => x.i + ':' + x.side).join(',');
    document.hidden && Object.defineProperty(document, 'hidden', { value: false, configurable: true });
    return { seen, n };
  });
  // the tick runs every 5 s; wait for two ticks and look at the stored log
  await p.waitForTimeout(11000);
  const out = await p.evaluate(() => { const L = FlowTest.log(); return { log: L.map(e => [e.ty, e.dir, e.parts]), nDiv: L.filter(e => e.ty === 'div').length, nConf: L.filter(e => (e.ty || 'conf') === 'conf').length, statDiv: FlowTest.stats('m5', 'div'), statConf: FlowTest.stats('m5', 'conf'), stored: (JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k => /_ft$/.test(k)) || 'x') || '[]')).length }; });
  const ok = /28:bear/.test(res.seen) && out.nDiv === 1 && out.log[0][0] === 'div' && out.log[0][1] === -1 && out.log[0][2] === 'cvd-div' && out.statDiv.n === 0 && out.stored >= 1 && !errs.length;
  console.log(JSON.stringify({ res, out }), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
