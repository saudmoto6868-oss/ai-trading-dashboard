// MOCK-TESTED ONLY (fake OKX): builds a short chart (narrow layout, card inside the column), finds the sync-card ✕, really clicks it, checks the card is hidden and the choice is saved.
// Build: python3 -c "from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w',encoding='utf8').write(b(['BTC-USDT']))"   Run: NODE_PATH=$(npm root -g) node tests/browser/sync_card_x_mock.js /tmp/ws.html /tmp/shot.png
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const ctx = await b.newContext({ viewport: { width: 1200, height: 700 } });
  const hdr = { 'access-control-allow-origin': '*' };
  const candles = () => { const now = Math.floor(Date.now() / 60000) * 60000, rows = []; let c = 67000; for (let i = 0; i < 120; i++) { c += Math.sin(i / 7) * 10; rows.push([String(now - i * 60000), String(c), String(c + 20), String(c - 20), String(c + 2), '10', '10', '10', '1']); } return rows; };
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 150)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort();
    return r.fulfill({ status: 200, contentType: 'application/json', headers: hdr, body: JSON.stringify(/candles/.test(u) ? { code: '0', data: candles() } : { code: '0', data: [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200);
  for (const h of [330, 620]) {
    await p.evaluate(h => { Ws.build([['chart', { x: 0, y: 0, w: 760, h }, { sym: 'BTC-USDT', tf: '1m', dcol: true, dom: true, sync: true }]]); Ws.save(); }, h);
    await p.waitForTimeout(3500);
    const st = () => p.evaluate(() => { const ch = Ws.panels[0].chart; const X = ch._scX; const r = ch.cv.getBoundingClientRect(); return { x: X ? { x: Math.round(X.x), y: Math.round(X.y) } : null, cx: X ? r.left + (X.x + X.w/2)*ch.S : null, cy: X ? r.top + (X.y + X.h/2)*ch.S : null, scOn: ch.scOn, state: Ws.panels[0].state.ofs }; });
    const a = await st(); console.log('panel h=' + h, 'before click', JSON.stringify(a));
    if (h === 330) await p.screenshot({ path: process.argv[3], clip: { x: 0, y: 40, width: 800, height: 380 } });
    if (a.cx) { await p.mouse.click(a.cx, a.cy); await p.waitForTimeout(600); const z = await st(); console.log('        after click ', JSON.stringify(z)); }
  }
  console.log('errors', errs.length, errs[0] || ''); await b.close();
})();
