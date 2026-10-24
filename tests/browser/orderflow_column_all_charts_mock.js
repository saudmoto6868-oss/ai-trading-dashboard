// MOCK-TESTED ONLY. Old saved charts (dom/bub on, no dcol, absurd colW) must open with the order-flow column ON and a sane width on EVERY chart panel, and still do after a rebuild.
// Run: NODE_PATH=$(npm root -g) node tests/browser/orderflow_column_all_charts_mock.js /tmp/ws.html   (build with: python3 -c "from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w',encoding='utf8').write(b(['BTC-USDT','ETH-USDT']))")
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 60000) * 60000, o = []; let c = 100; for (let i = 0; i < 300; i++) { c += Math.sin(i / 7); o.push([String(now - i * 60000), String(c), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000);
  const res = await p.evaluate(async () => { let L = Ws.defaults().map(([t, r, st]) => { if (t === 'chart') { st = Object.assign({}, st, { dom: true, bub: true, colW: 99999 }); delete st.dcol; } return [t, r, st]; }); const c0 = L.find(x => x[0] === 'chart'); while (L.filter(x => x[0] === 'chart').length < 4) L.push(['chart', Object.assign({}, c0[1]), Object.assign({}, c0[2], { tf: ['5m', '15m', '1H', '4H'][L.length % 4] })]); Ws.build(L);   /* 4 chart panels, different timeframes */ await new Promise(r => setTimeout(r, 2500));
    const cs = Ws.panels.filter(q => q.type === 'chart' && q.chart); return cs.map(q => ({ colOn: !!q.chart.colOn, w: Math.round(q.chart.cw()), W: Math.round(q.chart.W), saved: !!q.state.dcol })); });
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
