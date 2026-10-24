// MOCK-TESTED ONLY (fake OKX). Opens a chart (column on) + a DOM panel, picks grouping 10 in both, checks rows regroup, saved per symbol, and the toolbar list hides when the column is off.
// Build: python3 -c "from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w',encoding='utf8').write(b(['BTC-USDT','ETH-USDT']))"   Run: NODE_PATH=$(npm root -g) node tests/browser/price_grouping_mock.js /tmp/ws.html /tmp/shot.png
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const ctx = await b.newContext({ viewport: { width: 1500, height: 900 } });
  const hdr = { 'access-control-allow-origin': '*' };
  const candles = () => { const now = Math.floor(Date.now() / 60000) * 60000, rows = []; let c = 67000; for (let i = 0; i < 120; i++) { c += Math.sin(i / 7) * 10; rows.push([String(now - i * 60000), String(c), String(c + 20), String(c - 20), String(c + 2), '10', '10', '10', '1']); } return rows; };
  const book = { asks: Array.from({ length: 40 }, (_, i) => ['' + (67001 + i * 0.5), '' + (1 + i % 5), '0', '1']), bids: Array.from({ length: 40 }, (_, i) => ['' + (67000.5 - i * 0.5), '' + (1 + i % 4), '0', '1']), ts: '' + Date.now() };
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 150)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    const body = /candles/.test(u) ? { code: '0', data: candles() } : /books/.test(u) ? { code: '0', data: [book] } : { code: '0', data: [] };
    return r.fulfill({ status: 200, contentType: 'application/json', headers: hdr, body: JSON.stringify(body) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200);
  await p.evaluate(() => { Ws.build([['chart', { x: 0, y: 0, w: 700, h: 500 }, { sym: 'BTC-USDT', tf: '1m', dcol: true, dom: true }], ['dom', { x: 710, y: 0, w: 380, h: 500 }, { sym: 'BTC-USDT' }]]); Ws.save(); });
  await p.waitForTimeout(6000);
  const info = () => p.evaluate(() => { const ch = Ws.panels.find(x => x.type === 'chart'), dm = Ws.panels.find(x => x.type === 'dom'); const g = ch.gSelTb;
    return { selects: document.querySelectorAll('select.gsel').length, colOn: ch.chart.colOn, colSelVisible: g.style.display !== 'none', colSelVal: g.value, disabledOpts: [...g.options].filter(o => o.disabled).map(o => o.value), domRows: dm.domBox.querySelectorAll('tr').length, domPrices: [...dm.domBox.querySelectorAll('td[style*="center"]')].slice(0, 4).map(x => x.textContent.trim()) }; });
  console.log('A (auto)  ', JSON.stringify(await info()));
  await p.evaluate(() => { const dm = Ws.panels.find(x => x.type === 'dom'); dm.gSel.value = '10'; dm.gSel.onchange(); const ch = Ws.panels.find(x => x.type === 'chart'); ch.gSelTb.value = '10'; ch.gSelTb.onchange(); });
  await p.waitForTimeout(2500);
  console.log('B (10)    ', JSON.stringify(await info()));
  console.log('saved state', JSON.stringify(await p.evaluate(() => Ws.panels.map(x => ({ t: x.type, g: x.state.gstep, o: x.state.ofstep })))));
  await p.evaluate(() => { const ch = Ws.panels.find(x => x.type === 'chart'); ch.chart.colOn = false; ch.chart.draw(); }); await p.waitForTimeout(500);
  console.log('C (col off)', JSON.stringify((await info()).colSelVisible));
  await p.evaluate(() => { const ch = Ws.panels.find(x => x.type === 'chart'); ch.chart.colOn = true; ch.chart.draw(); }); await p.waitForTimeout(1500); console.log('errors', errs.length, errs.slice(0, 2).join(' | '));
  await p.screenshot({ path: process.argv[3] });
  await b.close();
})();
