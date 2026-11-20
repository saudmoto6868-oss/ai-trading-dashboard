// Browser check of the "Day candle" indicator (mock-tested only: OKX candles are faked with page.route, no live data).
//   NODE_PATH=$(npm root -g) node tests/e2e/day_candle_check.js
const { chromium } = require('playwright');
const { execSync } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const html = path.join(os.tmpdir(), 'ws_day_candle.html');
fs.writeFileSync(html, execSync(`python3 -c "from modules.workspace import build_workspace_html as b; print(b(['BTC-USDT','ETH-USDT'], [], 'en'))"`, { cwd: ROOT, env: { ...process.env, PYTHONPATH: ROOT }, maxBuffer: 1 << 28 }));
const fail = [];
const ok = (c, m) => { if (!c) fail.push(m); console.log((c ? 'ok   ' : 'FAIL ') + m); };
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  const errors = []; page.on('pageerror', e => errors.push(e.message.slice(0, 160)));
  const now = Math.floor(Date.now() / 3600000) * 3600000;
  const rows = []; let px = 100;
  for (let i = 0; i < 400; i++) { const t = now - i * 3600000; const o = px, c = px + Math.sin(i / 5); px = c; rows.push([String(t), String(o), String(Math.max(o, c) + 1), String(Math.min(o, c) - 1), String(c), '10', '10', '10', '1']); }
  const body = JSON.stringify({ code: '0', msg: '', data: rows });
  await page.route(/okx\.com\/api\/v5\/market\/(history-)?candles/, r => r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body }));
  await page.route(/^https?:\/\/(?!localhost|127\.0\.0\.1).*/, r => /okx\.com\/api\/v5\/market\/(history-)?candles/.test(r.request().url()) ? r.fallback() : r.abort());
  await page.goto('file://' + html, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => typeof Ws !== 'undefined' && Ws.panels.some(p => p.chart && p.chart.data.length > 50), null, { timeout: 30000 }).catch(() => {});
  const have = await page.evaluate(() => typeof Ws !== 'undefined' && Ws.panels.some(p => p.chart && p.chart.data.length > 50));
  ok(have, 'a chart panel loaded mocked candles');
  const r = await page.evaluate(() => {
    const P = Ws.panels.find(p => p.chart && p.chart.data.length > 50), ch = P.chart, out = {};
    const spy = () => { const fr = [], tx = [], f0 = ch.ctx.fillRect.bind(ch.ctx), t0 = ch.ctx.fillText.bind(ch.ctx);
      ch.ctx.fillRect = (x, y, w, h) => { fr.push([x, y, w, h]); return f0(x, y, w, h); }; ch.ctx.fillText = (s, x, y) => { tx.push(String(s)); return t0(s, x, y); };
      return { fr, tx, done: () => { ch.ctx.fillRect = f0; ch.ctx.fillText = t0; } }; };
    const run = () => { const s = spy(); ch._paint(); s.done(); return s; };
    ch.tf = '1H'; ch.dcOn = false; let s = run(); out.offBig = s.fr.filter(a => a[2] === 26).length; out.offTag = s.tx.filter(t => /1D/.test(t)).length;
    ch.dcOn = true; s = run(); const big = s.fr.filter(a => a[2] === 26); out.onBig = big.length; out.onTag = s.tx.filter(t => /1D/.test(t));
    out.x = big[0] && big[0][0]; out.expectX = ch.W - ch.PR - 26 - 8; out.h = big[0] && big[0][3];
    const DAY = 86400000, day = Math.floor(Date.now() / DAY), keep = ch.data, r0 = ch.r; ch.r = 1;   // the view must point inside the 2 synthetic bars
    ch.data = [{ t: day * DAY + 5 * 3600000, o: 1, h: 3, l: .5, c: 2, v: 1 }, { t: day * DAY + 6 * 3600000, o: 2, h: 4, l: 1.5, c: 3, v: 1 }];
    s = run(); out.partialTag = s.tx.filter(t => /1D/.test(t));
    ch.data = [{ t: day * DAY, o: 1, h: 3, l: .5, c: 2, v: 1 }, { t: day * DAY + 3600000, o: 2, h: 4, l: 1.5, c: 3, v: 1 }];
    s = run(); out.fullTag = s.tx.filter(t => /1D/.test(t));
    ch.data = keep; ch.r = r0; ch.tf = '1D'; s = run(); out.dailyBig = s.fr.filter(a => a[2] === 26).length;
    ch.tf = '1H'; ch.dcOn = false; return out; });
  ok(r.offBig === 0 && r.offTag === 0, 'indicator off: nothing is drawn');
  ok(r.onBig === 1 && r.onTag.includes('1D'), 'indicator on: one big candle body and the 1D tag');
  ok(Math.abs(r.x - r.expectX) < 0.5 && r.h >= 2, 'the candle is fixed at the right edge of the plot (x ' + r.x + ', expected ' + r.expectX + ')');
  ok(r.partialTag.includes('~1D'), 'history that starts inside the day is tagged ~1D');
  ok(r.fullTag.includes('1D') && !r.fullTag.includes('~1D'), 'history that covers the day start is tagged 1D (no ~)');
  ok(r.dailyBig === 0, 'nothing is drawn on a daily chart');
  const menu = await page.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /ƒx/.test(x.textContent)); if (!b) return 'no-button'; b.click(); return 'clicked'; });
  await page.waitForTimeout(400);
  const listed = await page.evaluate(() => document.body.innerText.includes('Day candle (today as one big candle)'));
  ok(menu === 'clicked' && listed, 'the indicator menu lists "Day candle (today as one big candle)"');
  ok(errors.length === 0, 'no JavaScript page errors' + (errors.length ? ': ' + errors[0] : ''));
  await browser.close();
  if (fail.length) { console.log('FAILED: ' + fail.length); process.exit(1); } else console.log('ALL OK');
})().catch(e => { console.error('ERROR', e.message.slice(0, 300)); process.exit(1); });
