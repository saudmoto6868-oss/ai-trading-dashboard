// MOCK-TESTED ONLY (no real OKX). Two pages in ONE browser context (shared localStorage) like two tabs of the dashboard.
// Build the page:  python3 -c "from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w',encoding='utf8').write(b(['BTC-USDT','ETH-USDT']))"
// Run:  NODE_PATH=$(npm root -g) node tests/browser/okx_two_tabs_mock.js /tmp/ws.html p2429   (p2429 = tab 2 is always rate-limited)
// Pass = tab 1 keeps getting fresh candles (ok: seconds-since-last-success stays small, request count grows).
const { chromium } = require('playwright');
const file = 'file://' + process.argv[2];
const mode = process.argv[3] || 'ok';   // ok: both pages get data; p2429: page 2 is always rate-limited
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const ctx = await b.newContext({ viewport: { width: 1500, height: 900 } });
  const log = { p1: 0, p2: 0, p2_429: 0 };
  const candles = () => { const now = Math.floor(Date.now() / 60000) * 60000, rows = []; let c = 100; for (let i = 0; i < 120; i++) { const t = now - i * 60000; c += Math.sin(i / 7); rows.push([String(t), String(c), String(c + 1), String(c - 1), String(c + .2), '10', '10', '10', '1']); } return rows; };
  const mock = (name, rate) => async r => { const u = r.request().url();
    if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    log[name]++;
    if (rate) { log.p2_429++; return r.fulfill({ status: 429, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: '{"code":"50011","msg":"Too Many Requests"}' }); }
    const body = /candles/.test(u) ? { code: '0', data: candles() } : { code: '0', data: [] };
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(body) }); };
  const p1 = await ctx.newPage(); await p1.route('**/*', mock('p1', false));
  const errs = []; p1.on('pageerror', e => errs.push('p1:' + String(e).slice(0, 120)));
  await p1.goto(file); await p1.waitForTimeout(1500);
  await p1.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); });
  await p1.waitForTimeout(6000);
  const state = pg => pg.evaluate(() => Ws.panels.filter(p => p.type === 'chart').map(p => ({ n: p.chart ? p.chart.data.length : -1, ok: p._okAt ? Math.round((Date.now() - p._okAt) / 1000) : null })).slice(0, 4));
  console.log('t=0 p1 charts', JSON.stringify(await state(p1)), 'reqs', log.p1);
  const p2 = await ctx.newPage(); await p2.route('**/*', mock('p2', mode === 'p2429')); p2.on('pageerror', e => errs.push('p2:' + String(e).slice(0, 120)));
  await p2.goto(file); await p2.waitForTimeout(8000);
  console.log('t+8s  p1', JSON.stringify(await state(p1)), ' p2', JSON.stringify(await state(p2)), 'reqs p1', log.p1, 'p2', log.p2, '429s', log.p2_429);
  await p1.waitForTimeout(25000);
  console.log('t+33s p1', JSON.stringify(await state(p1)), 'reqs p1', log.p1, 'shared cool', await p1.evaluate(() => localStorage.getItem('okx_cool_all')), 'now', Date.now());
  console.log('errors', errs.length, errs.slice(0, 3).join(' | '));
  await b.close();
})();
