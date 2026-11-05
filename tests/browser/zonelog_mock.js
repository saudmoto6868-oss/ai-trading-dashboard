// MOCK-TESTED ONLY (mocked OKX book / trades). ZoneLog side tracker (ported from feat/orderflow-zonetest): it runs on the live book without errors, builds its own tracker (the heat-map flashes / limits list / sync lights are untouched),
// keeps a log in the browser, and the settings entry exports it as JSON. The zone rules themselves are tested in tests/test_flow_read.py (node, 37 checks). Run: NODE_PATH=$(npm root -g) node tests/browser/zonelog_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const ctx = await b.newContext({ viewport: { width: 1500, height: 900 }, acceptDownloads: true }); const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  let MID = 100, k = 0;
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100; let data = [];
    if (/candles/.test(u)) { for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2; o.push([String(now - (300 - i) * 3600000), String(c - 0.5), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); } MID = c; o.reverse(); data = o; }
    else if (/books/.test(u)) { k++; const bids = [], asks = []; for (let i = 0; i < 40; i++) { bids.push([String((MID - 0.1 - i * 0.1).toFixed(2)), String(i === 5 ? 900 + (k % 3) * 40 : 1 + (i * 7) % 11), '0', '1']); asks.push([String((MID + 0.1 + i * 0.1).toFixed(2)), String(1 + (i * 5) % 13), '0', '1']); } data = [{ bids, asks, ts: String(Date.now()) }]; }
    else if (/trades/.test(u)) { for (let i = 0; i < 50; i++) data.push({ instId: 'BTC-USDT', tradeId: String(1e6 - i - k * 100), px: String((MID - 0.6 + Math.sin(i) * 0.1).toFixed(2)), sz: String(0.5 + (i % 5)), side: 'sell', ts: String(Date.now() - i * 800) }); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data }) }); });
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3000);
  await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length).chart; ch.colOn = true; ch.domOn = true; ch.draw(); }); await p.waitForTimeout(9000);
  const out = await p.evaluate(() => { const ch = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length).chart; return { tracker: !!ch.zfr, walls: ch.zfr ? (ch.zfr.ev || []).length : -1, log: !!ch.zlog, recs: ch.zlog ? ch.zlog.recs.length : -1, hasExport: typeof exportZoneLog === 'function', ZoneLog: typeof ZoneLog }; });
  const [dl] = await Promise.all([p.waitForEvent('download', { timeout: 10000 }), p.evaluate(() => exportZoneLog(Ws.panels.find(q => q.type === 'chart' && q.chart.data.length).chart))]);
  out.exportName = dl.suggestedFilename();
  const ok = out.tracker && out.log && out.hasExport && /^zone_log_/.test(out.exportName) && !errs.length;
  console.log(JSON.stringify(out), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
