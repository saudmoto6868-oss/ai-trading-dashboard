// Browser check of the "HTF candles" indicator (the Day candle, with a choice of timeframe). Mock-tested only: OKX candles are faked with page.route.
//   NODE_PATH=$(npm root -g) node tests/e2e/day_candle_check.js
const { chromium } = require('playwright');
const { execSync } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const html = path.join(os.tmpdir(), 'ws_day_candle.html');
fs.writeFileSync(html, execSync(`python3 -c "from modules.workspace import build_workspace_html as b; print(b(['BTC-USDT','ETH-USDT'], [], 'en'))"`, { cwd: ROOT, env: { ...process.env, PYTHONPATH: ROOT }, maxBuffer: 1 << 28 }));
const fail = [];
const ok = (c, m) => { if (!c) fail.push(m); console.log((c ? 'ok   ' : 'FAIL ') + m); };
const STEP = { '1m': 6e4, '5m': 3e5, '15m': 9e5, '30m': 18e5, '1H': 36e5, '2H': 72e5, '4H': 144e5, '6Hutc': 216e5, '12Hutc': 432e5, '1D': 864e5, '1W': 6048e5 };
const mk = bar => { const st = STEP[bar] || 36e5, DAY = 864e5, W = 6048e5; let now = Math.floor(Date.now() / st) * st;
  if (bar === '1W') now = Math.floor((Date.now() - 4 * DAY) / W) * W + 4 * DAY;   // Monday 00:00 UTC
  const rows = []; let px = 100; for (let i = 0; i < 300; i++) { const t = now - i * st, o = px, c = px + Math.sin(i / 5) * (bar === '1W' ? 6 : 1); px = c; rows.push([String(t), String(o), String(Math.max(o, c) + 1), String(Math.min(o, c) - 1), String(c), '10', '10', '10', '1']); }
  return JSON.stringify({ code: '0', msg: '', data: rows }); };
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  const errors = []; page.on('pageerror', e => errors.push(e.message.slice(0, 160)));
  const asked = []; await page.route(/okx\.com\/api\/v5\/market\/(history-)?candles/, r => { const u = new URL(r.request().url()), bar = u.searchParams.get('bar'); asked.push(bar); r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: mk(bar) }); });
  await page.route(/^https?:\/\/(?!localhost|127\.0\.0\.1).*/, r => /okx\.com\/api\/v5\/market\/(history-)?candles/.test(r.request().url()) ? r.fallback() : r.abort());
  await page.goto('file://' + html, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => typeof Ws !== 'undefined' && Ws.panels.some(p => p.chart && p.chart.data.length > 50), null, { timeout: 30000 }).catch(() => {});
  ok(await page.evaluate(() => typeof Ws !== 'undefined' && Ws.panels.some(p => p.chart && p.chart.data.length > 50)), 'a chart panel loaded mocked candles');
  // helper in the page: paint once with spies on fillRect / fillText, return what was drawn
  await page.evaluate(() => { window.__run = (ch, wait) => { const fr = [], tx = [], f0 = ch.ctx.fillRect.bind(ch.ctx), t0 = ch.ctx.fillText.bind(ch.ctx);
    ch.ctx.fillRect = (x, y, w, h) => { fr.push([x, y, w, h]); return f0(x, y, w, h); }; ch.ctx.fillText = (s, x, y) => { tx.push(String(s)); return t0(s, x, y); };
    ch._paint(); ch.ctx.fillRect = f0; ch.ctx.fillText = t0; return { fr, tx }; };
    window.__ch = () => Ws.panels.find(p => p.chart && p.chart.data.length > 50).chart; });
  const settle = async tf => { await page.evaluate(tf => { const ch = __ch(); ch.htfRows(tf, 8); }, tf); await page.waitForFunction(tf => { const ch = __ch(), e = ch._htf && ch._htf[ch.sym + '|' + tf]; return e && !e.busy; }, tf, { timeout: 10000 }).catch(() => {}); };

  let r = await page.evaluate(() => { const ch = __ch(); ch.tf = '1H'; ch.dcOn = false; const s = __run(ch); return { big: s.fr.filter(a => a[2] === 26).length, tag: s.tx.filter(t => /^~?1D$/.test(t)).length }; });
  ok(r.big === 0 && r.tag === 0, 'indicator off: nothing is drawn');

  await settle('1D');
  r = await page.evaluate(() => { const ch = __ch(); ch.dcOn = true; Object.assign(ch.st.dcandle, { tf: '1D', n: 1, w: 26, gap: 6, off: 8, lbl: 1 }); const s = __run(ch), big = s.fr.filter(a => a[2] === 26); return { n: big.length, x: big[0] && big[0][0], ex: ch.W - ch.PR - 26 - 8, h: big[0] && big[0][3], tags: s.tx }; });
  ok(r.n === 1 && r.tags.includes('1D'), 'default (1D, 1 candle): one big candle and the 1D tag');
  ok(Math.abs(r.x - r.ex) < 0.5 && r.h >= 2, 'the candle sits at the right edge, offset 8 (x ' + r.x + ', expected ' + r.ex + ')');
  ok(asked.includes('1D'), 'the 1D candles were requested from the feed (real HTF candles, not only the loaded bars)');

  await settle('4H');
  r = await page.evaluate(() => { const ch = __ch(); Object.assign(ch.st.dcandle, { tf: '4H', n: 3, w: 20, gap: 5, off: 30 }); const s = __run(ch), big = s.fr.filter(a => a[2] === 20).sort((a, b) => a[0] - b[0]); return { n: big.length, xs: big.map(a => a[0]), ex: ch.W - ch.PR - 30 - 20, tags: s.tx.filter(t => /4H/.test(t)) }; });
  ok(r.n === 3 && r.tags.includes('4H'), '4H x 3 candles: three bodies and the 4H tag (the oldest ones have no tag)');
  ok(Math.abs(r.xs[2] - r.ex) < 0.5 && Math.abs((r.xs[2] - r.xs[1]) - 25) < 0.5 && Math.abs((r.xs[1] - r.xs[0]) - 25) < 0.5, 'width 20 + gap 5 spacing, newest at offset 30');

  await settle('1W');
  r = await page.evaluate(() => { const ch = __ch(); Object.assign(ch.st.dcandle, { tf: '1W', n: 2, w: 26, gap: 6, off: 8 }); const s = __run(ch); return { n: s.fr.filter(a => a[2] === 26).length, tags: s.tx.filter(t => /1W/.test(t)) }; });
  ok(r.n === 2 && r.tags.includes('1W'), 'weekly candles from the feed: no "~" even though the loaded 1H history is shorter than a week (tags ' + JSON.stringify(r.tags) + ')');

  r = await page.evaluate(() => { const ch = __ch(); Object.assign(ch.st.dcandle, { tf: '1H', n: 1 }); ch.tf = '1H'; const s = __run(ch); return { big: s.fr.filter(a => a[2] === 26).length, hint: s.tx.filter(t => /pick a higher timeframe/.test(t)).length }; });
  ok(r.big === 0 && r.hint === 1, 'an HTF that is not bigger than the chart timeframe draws nothing and shows a hint');

  r = await page.evaluate(() => { const ch = __ch(), keep = ch.data, r0 = ch.r, k0 = ch.tf; ch.tf = '5s'; Object.assign(ch.st.dcandle, { tf: '30s', n: 1 });
    const T0 = Math.floor(Date.now() / 30000) * 30000; ch.data = [0, 1, 2, 3].map(i => ({ t: T0 + i * 5000, o: 10 + i, h: 12 + i, l: 9, c: 11 + i, v: 1 })); ch.r = 3;
    const s = __run(ch); ch.data = keep; ch.r = r0; ch.tf = k0; return { big: s.fr.filter(a => a[2] === 26).length, tags: s.tx.filter(t => /30s/.test(t)) }; });
  ok(r.big === 1 && r.tags.includes('30s'), 'a sub-minute HTF (30s on a 5s chart) is built from the loaded bars (no feed request)');

  r = await page.evaluate(() => { const ch = __ch(), keep = ch.data, r0 = ch.r; Object.assign(ch.st.dcandle, { tf: '1D', n: 1 }); ch.tf = '1H'; const DAY = 864e5, day = Math.floor(Date.now() / DAY);
    ch._htf[ch.sym + '|1D'] = { rows: null, at: Date.now(), busy: false };   // the feed gave nothing: fall back to the loaded bars
    ch.data = [{ t: day * DAY + 5 * 36e5, o: 1, h: 3, l: .5, c: 2, v: 1 }, { t: day * DAY + 6 * 36e5, o: 2, h: 4, l: 1.5, c: 3, v: 1 }]; ch.r = 1; const a = __run(ch).tx.filter(t => /1D/.test(t));
    ch.data = [{ t: day * DAY, o: 1, h: 3, l: .5, c: 2, v: 1 }, { t: day * DAY + 36e5, o: 2, h: 4, l: 1.5, c: 3, v: 1 }]; const b = __run(ch).tx.filter(t => /1D/.test(t)); ch.data = keep; ch.r = r0; return { a, b }; });
  ok(r.a.includes('~1D') && r.b.includes('1D') && !r.b.includes('~1D'), 'fallback from loaded bars: ~1D when the history starts inside the day, 1D when it covers the day start');

  r = await page.evaluate(() => { const ch = __ch(); ch.tf = '1D'; Object.assign(ch.st.dcandle, { tf: '1W', n: 1 }); const s = __run(ch); const none = s.fr.filter(a => a[2] === 26).length; ch.tf = '1H'; ch.dcOn = false; return none; });
  ok(r === 1 || r === 0, 'a daily chart with a weekly HTF does not throw (drawn: ' + r + ')');

  const menu = await page.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /ƒx/.test(x.textContent)); if (!b) return 'no-button'; b.click(); return 'clicked'; });
  await page.waitForTimeout(400);
  ok(menu === 'clicked' && await page.evaluate(() => document.body.innerText.includes('HTF candles (day candle by default)')), 'the indicator menu lists "HTF candles (day candle by default)"');
  ok(fs.readFileSync(html, 'utf8').includes('dcandle:{tf:"1D",n:1,w:26,gap:6,off:8,lbl:1}'), 'built-in defaults: 1D, 1 candle, width 26, gap 6, offset 8, label on');
  ok(errors.length === 0, 'no JavaScript page errors' + (errors.length ? ': ' + errors[0] : ''));
  await browser.close();
  if (fail.length) { console.log('FAILED: ' + fail.length); process.exit(1); } else console.log('ALL OK');
})().catch(e => { console.error('ERROR', e.message.slice(0, 300)); process.exit(1); });
