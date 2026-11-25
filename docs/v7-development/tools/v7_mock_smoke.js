// V7 live tab: mock-browser smoke test (Playwright + page.route; no real network).
// 1) build the page:   PYTHONPATH=. python3 -c "from modules import v7_page as V;h,e=V.live_html();assert not e,e;open('/tmp/v7_built.html','w').write(h)"
// 2) run (from repo root, playwright installed):  node docs/v7-development/tools/v7_mock_smoke.js   -> prints extra panel, MTF chips, localStorage keys, console errors; writes live_shot7.png next to this script.
// MOCK ONLY: OKX / Hyperliquid replies are synthetic, so this proves the page runs and the toggles work, not that real feeds behave.
const { chromium } = require('playwright'); const S = __dirname + '/';
function candles(n, sec, last) { const out = []; let c = 73000; for (let i = n - 1; i >= 0; i--) { c += Math.sin(i / 7) * 40 + (i % 5 - 2) * 8 + Math.sin(i / 31) * 90; out.push({ t: last - i * sec, o: c - 5 + (i % 3) * 3, h: c + 20, l: c - 20, c }); } return out; }
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1900, height: 950 } }); const errs = [];
  p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.addInitScript(() => { try { localStorage.setItem('v7lang', 'en'); } catch (e) {} });
  await p.route('**/api/v5/market/tickers**', r => r.fulfill({ contentType: 'application/json', body: '{"code":"0","data":[]}' }));
  await p.route('**/api/v5/market/candles**', r => { const u = new URL(r.request().url()); const sec = { '1m': 60, '5m': 300, '15m': 900, '1H': 3600 }[u.searchParams.get('bar')] || 900; const now = Math.floor(Date.now() / 1000), last = now - now % sec;
    r.fulfill({ contentType: 'application/json', body: JSON.stringify({ code: '0', data: candles(300, sec, last).map((k, i, a) => [String(k.t * 1000), String(k.o), String(k.h), String(k.l), String(k.c), String(50 + i % 7), '1', '1', i === a.length - 1 ? '0' : '1']).reverse() }) }); });
  await p.route('**/api.hyperliquid.xyz/info', r => r.fulfill({ contentType: 'application/json', body: '{"universe":[]}' }));
  await p.goto('file:///tmp/v7_built.html'); await p.waitForTimeout(1800);
  for (const [m, k] of [[1, 'Liquidity sweeps'], [1, 'CISD higher TF'], [1, 'Trend line'], [1, 'Liquidity pools'], [1, 'Divergence'], [2, 'Fibonacci']]) { await p.click('.mn:nth-child(' + m + ')>button'); await p.locator('.pop.open label', { hasText: k }).locator('input').check(); await p.mouse.click(1000, 500); }
  await p.waitForTimeout(700); await p.screenshot({ path: __dirname + '/live_shot7.png' });
  const out = { extra: (await p.textContent('#extra')).slice(0, 330), mtf: await p.textContent('#mtf'), ls: await p.evaluate(() => Object.keys(localStorage).filter(k => k.startsWith('v7c_'))), errors: errs.slice(0, 5) };
  console.log(JSON.stringify(out, null, 1)); await b.close();
})();
