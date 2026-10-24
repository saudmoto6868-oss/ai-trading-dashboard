// MOCK-TESTED ONLY. Pen button = HIDE drawings (owner 2026-10-24): normal state shows drawings with nothing pressed; clicking hides them and lights the button; choosing a drawing tool shows them again; old saved "hidden" state is reset once.
// Run: NODE_PATH=$(npm root -g) node tests/browser/pen_hide_drawings_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 60000) * 60000, o = []; let c = 100; for (let i = 0; i < 300; i++) { c += Math.sin(i / 5) * 2; o.push([String(now - i * 60000), String(c), String(c + 2), String(c - 2), String(c + (i % 2 ? 1 : -1)), '10', '0', '0', '1']); }
    return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: /candles/.test(u) ? o : [] }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000);
  await p.evaluate(() => { const L = Ws.defaults().map(([t, r, st]) => [t, r, t === 'chart' ? Object.assign({}, st, { drawingsVisible: false }) : st]); Ws.build(L); }); await p.waitForTimeout(3500);   // OLD saved state: hidden, no migration flag
  const res = await p.evaluate(async () => { const wait = ms => new Promise(r => setTimeout(r, ms)), out = {}; const P = Ws.panels.find(q => q.type === 'chart' && q.chart.data.length), ch = P.chart; const btn = [...P.root.querySelectorAll('button')].find(x => x.textContent === '✎✕');
    out.buttonExists = !!btn; out.migratedVisible = ch.drawingsVisible === true && !btn.classList.contains('on');
    btn.click(); await wait(80); out.afterClickHidden = ch.drawingsVisible === false && btn.classList.contains('on') && P.state.drawingsVisible === false;
    ch.setTool('trend'); await wait(80); out.toolShowsAgain = ch.drawingsVisible === true && !btn.classList.contains('on') && P.state.drawingsVisible === true;
    btn.click(); await wait(80); btn.click(); await wait(80); out.toggleTwiceVisible = ch.drawingsVisible === true; return out; });
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
