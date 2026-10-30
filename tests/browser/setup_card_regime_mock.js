// MOCK-TESTED ONLY (mocked OKX, trending candles). Setup Card checklist has a "Market regime (now, this timeframe)" row: "…" while the candles load, then "TREND · ADX n" (information, "~" icon, never a pass / fail).
// Run: NODE_PATH=$(npm root -g) node tests/browser/setup_card_regime_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100;
    for (let i = 0; i < 300; i++) { c *= 1 + 0.004 + Math.sin(i * 7.3) * 0.002; o.push([String(now - (300 - i) * 3600000), String(c * 0.998), String(c * 1.002), String(c * 0.996), String(c), String(100 + (i * 37) % 40), '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3000);
  const res = await p.evaluate(async () => { const e = { symbol: 'ETH-USDT', tfk: '1h', direction: 'bullish', score: 3, max: 6, ttype: 'Day', q: 0, plan: null, ana: null, tags: [] };
    const text = h => { const d = document.createElement('div'); d.innerHTML = h; return d.innerText || d.textContent; };
    const first = text(setupHtml(e)); await new Promise(r => setTimeout(r, 2500)); const second = text(setupHtml(e));
    const pick = t => (t.match(/Market regime[^\n]*\n?[^\n]*/) || [''])[0].replace(/\s+/g, ' ');
    return { first: pick(first), second: pick(second) }; });
  const ok = /…/.test(res.first) && /TREND/.test(res.second) && !errs.length;
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
