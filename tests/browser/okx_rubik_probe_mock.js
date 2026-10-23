// MOCK-TESTED ONLY: 20 concurrent okx('/rubik/...') calls with the network failing like a CORS block. Before the fix: 20 requests; after: 1.
// Build: python3 -c "from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w',encoding='utf8').write(b(['BTC-USDT']))"   Run: NODE_PATH=$(npm root -g) node tests/browser/okx_rubik_probe_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const ctx = await b.newContext(); let rub = 0;
  const p = await ctx.newPage();
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    if (/\/rubik\//.test(u)) { rub++; return r.abort('failed'); }  // no CORS header, like OKX
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: '{"code":"0","data":[]}' }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1500);
  const coins = ['BTC','ETH','SOL','XRP','DOGE','ADA','AVAX','LINK','DOT','TRX','LTC','BCH','ATOM','NEAR','APT','ARB','OP','INJ','SUI','SEI'];
  const before = rub;
  const res = await p.evaluate(async cs => { const out = await Promise.all(cs.map(c => okx('/rubik/stat/contracts/open-interest-volume?ccy=' + c + '&period=1H').then(() => 'ok', e => String(e.message || e).slice(0, 40)))); return out.reduce((a, x) => (a[x] = (a[x] || 0) + 1, a), {}); }, coins);
  console.log('20 concurrent rubik calls -> network requests:', rub - before, '| outcomes:', JSON.stringify(res));
  const rub2 = rub; const again = await p.evaluate(async () => okx('/rubik/stat/contracts/open-interest-volume?ccy=BTC&period=5m').then(() => 'ok', e => String(e.message || e).slice(0, 60)));
  console.log('a later call -> new requests:', rub - rub2, '|', again);
  await b.close();
})();
