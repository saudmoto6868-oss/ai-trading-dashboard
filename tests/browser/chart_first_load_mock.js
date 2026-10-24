// MOCK-TESTED ONLY. Pass = every chart has candles within ~3 s using ONE candles request each (history fills later), and a slow/failing OKX history does not blank the chart.
// Build: python3 -c "from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w',encoding='utf8').write(b(['BTC-USDT','ETH-USDT']))"
// Run:   NODE_PATH=$(npm root -g) node tests/browser/chart_first_load_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage();
  const reqs = []; const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  const rows = (n, end, step) => { const o = []; let c = 100; for (let i = 0; i < n; i++) { const t = end - i * step; c += Math.sin(i / 7); o.push([String(t), String(c), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); } return o; };
  await p.route('**/*', async r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    const h = { 'access-control-allow-origin': '*' }; if (!/candles/.test(u)) return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: '{"code":"0","data":[]}' });
    reqs.push(u.replace(/.*v5/, '').slice(0, 70)); const hist = /history-candles/.test(u); if (hist) await new Promise(x => setTimeout(x, 800));
    const after = +(new URL(u).searchParams.get('after')) || Math.floor(Date.now() / 60000) * 60000 + 60000;
    return r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: rows(hist ? 100 : 300, after - 60000, 60000) }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200);
  await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3000);
  const st = () => p.evaluate(() => Ws.panels.filter(q => q.type === 'chart').map(q => q.chart ? q.chart.data.length : -1));
  console.log('t+3s bars per chart', JSON.stringify(await st()), 'candle reqs so far', reqs.length);
  await p.waitForTimeout(12000); console.log('t+15s bars per chart', JSON.stringify(await st()), 'candle reqs', reqs.length, 'errors', errs.length, errs[0] || '');
  await b.close();
})();
