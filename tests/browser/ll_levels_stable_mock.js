// MOCK-TESTED ONLY (mocked OKX, synthetic candles). "MTF Liquidity Levels & Targets": a timeframe's line used to jump between the previous candle's HIGH and LOW (a 200-300 USD jump on BTC 1H / 4H)
// every time the price ticked across the middle of that candle. Now the edge is kept until the price is clearly past the middle; a new previous candle starts over.
// Run: NODE_PATH=$(npm root -g) node tests/browser/ll_levels_stable_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100;
    for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2; o.push([String(now - (300 - i) * 3600000), String(c - 0.5), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: o }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(2500);
  const res = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length).chart; ch._llSide = {}; const t = { ph: 300, pl: 100 }, out = {}; const seq = [];
    // price wobbles around the middle (200) of a 200-wide candle: the OLD rule flipped between 300 and 100 on every tick
    [190, 205, 195, 210, 199, 201, 204, 196, 205].forEach(px => seq.push(ch.llPick('1H', t, px)));
    out.wobbleDistinct = [...new Set(seq)].length; out.wobbleFirst = seq[0];
    out.old = [190, 205, 195, 210, 199, 201].map(px => Math.abs(px - 300) < Math.abs(px - 100) ? 300 : 100).filter((v, i, a) => i && v !== a[i - 1]).length;   // how many flips the old rule would have made
    out.clearlyUp = ch.llPick('1H', t, 262); out.backNearMid = ch.llPick('1H', t, 215); out.clearlyDown = ch.llPick('1H', t, 130); out.aboveRange = ch.llPick('1H', t, 340); out.belowRange = (() => { ch._llSide = {}; return ch.llPick('1H', t, 60); })();
    { const px = ch.data[ch.data.length - 1].c; ch.llOn = true; ch.llD = {}; ['5M', '15M', '1H', '4H', 'D1', 'W1'].forEach(k => { ch.llD[k] = { ph: px + 3, pl: px - 3, cl: px, atr: 2, mom: 0.3 }; }); let e = null; try { ch.paint(); ch.paint(); } catch (x) { e = String(x); } out.paintOk = !e; out.paintErr = e; out.sides = JSON.stringify(Object.keys(ch._llSide || {}).sort()); }
    out.newCandle = (() => { ch._llSide = {}; ch.llPick('1H', t, 150); return ch.llPick('1H', { ph: 400, pl: 300 }, 395); })(); return out; });
  const ok = res.wobbleDistinct === 1 && res.old >= 3 && res.clearlyUp === 300 && res.backNearMid === 300 && res.clearlyDown === 100 && res.aboveRange === 300 && res.belowRange === 100 && res.newCandle === 400 && res.paintOk && /1H/.test(res.sides) && !errs.length;
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
