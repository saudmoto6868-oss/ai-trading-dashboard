// MOCK-TESTED ONLY (mocked OKX). MTF LLT indicator: the higher-timeframe candles are fetched ONCE per symbol for all charts (was 6 requests per chart every 30 s: four gold charts made Hyperliquid rate-limit the whole page),
// a failure keeps the last good levels, and the status line is a small quiet note. Run: NODE_PATH=$(npm root -g) node tests/browser/llt_shared_fetch_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  let llReq = 0, fail = false;
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const isLL = /limit=40/.test(u) && /candles/.test(u); if (isLL) { llReq++; if (fail) return r.abort(); }
    const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100; for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2; o.push([String(now - (300 - i) * 3600000), String(c - 0.5), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2500);
  llReq = 0;
  const r1 = await p.evaluate(async () => { const cs = Ws.panels.filter(q => q.type === 'chart' && q.chart.data.length); cs.forEach(P => { P.chart.llOn = true; P.llT = 0; P.llKick(); }); await new Promise(r => setTimeout(r, 4500));
    return { charts: cs.length, syms: [...new Set(cs.map(P => P.state.sym))].length, withD: cs.filter(P => P.chart.llD).length, keys: cs[0].chart.llD ? Object.keys(cs[0].chart.llD) : null }; });
  const firstReq = llReq;
  // a failure: the shared cache entry is old, the exchange is unreachable -> last good levels stay, the note says "retrying"
  fail = true; await p.waitForTimeout(10500);   // okx() keeps an identical request for 10 s
  const r2 = await p.evaluate(async () => { LLC.forEach(v => { v.t = 0; }); const cs = Ws.panels.filter(q => q.type === 'chart' && q.chart.data.length); cs.forEach(P => P.llKick()); await new Promise(r => setTimeout(r, 2500)); return { kept: cs.filter(P => P.chart.llD).length, err: cs.filter(P => P.chart.llErr).length }; });
  const msg = await p.evaluate(() => ({ rl: offTxt('HL:xyz:GOLD', new Error('Hyperliquid rate limit: waiting before retry')), hl: offTxt('HL:xyz:GOLD', new Error('net')), okx: offTxt('BTC-USDT', new Error('net')), isRL: isRL(new Error('Hyperliquid HTTP 429')) }));
  const ok = /rate-limiting/.test(msg.rl) && /Hyperliquid/.test(msg.hl) && /OKX/.test(msg.okx) && msg.isRL && r1.withD === r1.charts && r1.keys && r1.keys.length >= 5 && firstReq <= 6 * r1.syms && r2.kept === r1.charts && r2.err >= 1 && !errs.length;
  console.log(JSON.stringify({ r1, firstReq, r2, msg }), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
