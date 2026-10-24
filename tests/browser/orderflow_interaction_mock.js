// MOCK-TESTED ONLY (real Chromium, fake OKX). Order-flow checklist items 7, 8, 10 + the column on every chart panel:
// 7 price-scale drag with the column open keeps column width and plot; 8 pan / zoom / window resize keep a sane layout; 10 Order Book + Time & Sales panels keep updating; all 4 charts (5m/15m/1H/4H) show the column.
// Run: NODE_PATH=$(npm root -g) node tests/browser/orderflow_interaction_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160))); let tick = 0;
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const h = { 'access-control-allow-origin': '*' }; const J = d => r.fulfill({ status: 200, contentType: 'application/json', headers: h, body: JSON.stringify({ code: '0', data: d }) });
    if (/market\/candles|history-candles/.test(u)) { const now = Math.floor(Date.now() / 60000) * 60000, o = []; let c = 100; for (let i = 0; i < 300; i++) { c += Math.sin(i / 5) * 2; o.push([String(now - i * 60000), String(c), String(c + 2), String(c - 2), String(c + (i % 2 ? 1 : -1)), '10', '0', '0', '1']); } return J(o); }
    if (/market\/books/.test(u)) { tick++; const a = [], bd = []; for (let i = 0; i < 40; i++) { a.push([String(100 + 0.1 * i + 0.05), String(1 + ((i * 7 + tick) % 11)), '0', '3']); bd.push([String(100 - 0.1 * i - 0.05), String(1 + ((i * 5 + tick) % 13)), '0', '3']); } return J([{ asks: a, bids: bd, ts: String(Date.now()) }]); }
    if (/market\/trades/.test(u)) { tick++; return J(Array.from({ length: 30 }, (_, i) => ({ tradeId: String(tick * 100 + i), px: String(100 + Math.sin(i + tick)), sz: String(0.1 + (i % 5)), side: i % 2 ? 'buy' : 'sell', ts: String(Date.now() - i * 700) }))); }
    return J([]); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000);
  await p.evaluate(() => { let L = Ws.defaults().map(([t, r, st]) => { if (t === 'chart') { st = Object.assign({}, st, { dom: true, bub: true, dcol: true }); } return [t, r, st]; }); const c0 = L.find(x => x[0] === 'chart'); while (L.filter(x => x[0] === 'chart').length < 4) L.push(['chart', Object.assign({}, c0[1]), Object.assign({}, c0[2], { tf: ['5m', '15m', '1H', '4H'][L.length % 4] })]); Ws.build(L); }); await p.waitForTimeout(6000);
  const res = await p.evaluate(async () => { const wait = ms => new Promise(r => setTimeout(r, ms)), out = {}; const charts = Ws.panels.filter(q => q.type === 'chart' && q.chart); out.charts = charts.length; out.columnOnAll = charts.every(q => q.chart.colOn && q.chart.cw() > 0);
    const P = charts[0], ch = P.chart; const rc = ch.cv.getBoundingClientRect(), S = ch.S || 1; const fire = (t, x, y) => ch.cv.dispatchEvent(new PointerEvent(t, { clientX: rc.left + x*S, clientY: rc.top + y*S, pointerId: 1, bubbles: true, button: 0 }));
    // 7: price-scale drag (right axis strip) keeps the column and the plot
    const cw0 = ch.cw(), pr0 = ch.PR, z0 = ch.yZoom; const ax = ch.W - ch.axw/2; fire('pointerdown', ax, 60); for (let k = 1; k <= 8; k++){ fire('pointermove', ax, 60 + k*8); await wait(15); } fire('pointerup', ax, 130); await wait(80);
    out.item7 = { yZoomChanged: ch.yZoom !== z0, colWidthSame: ch.cw() === cw0, plotSame: ch.PR === pr0 };
    // 8: pan + wheel zoom + window resize
    const r0 = ch.r, bw0 = ch.bw; fire('pointerdown', 120, 100); for (let k = 1; k <= 6; k++){ fire('pointermove', 120 + k*15, 100); await wait(15); } fire('pointerup', 210, 100); await wait(60);
    ch.cv.dispatchEvent(new WheelEvent('wheel', { deltaY: -100, clientX: rc.left + 100*S, clientY: rc.top + 100*S, bubbles: true, cancelable: true })); await wait(80);
    out.item8 = { panMoved: ch.r !== r0, zoomChanged: ch.bw !== bw0, colAfter: Math.round(ch.cw()) };
    const root = P.root, w0 = root.style.width; root.style.width = (root.clientWidth - 140) + 'px'; await wait(250); ch.resize(); out.item8.resizedW = Math.round(ch.W); out.item8.colMax85 = ch.cw() <= Math.round(ch.W*0.85) + 1; out.item8.plotPx = Math.round(ch.PR); root.style.width = w0; await wait(100);
    // 10: Order Book + Time & Sales keep updating (two samples a few seconds apart)
    const dom = Ws.panels.find(q => q.type === 'dom'), tape = Ws.panels.find(q => q.type === 'tape'); const snap = () => ({ dom: dom ? dom.body.innerText.slice(0, 400) : null, tapeRows: tape ? tape.body.querySelectorAll('tr').length : -1, tape: tape ? tape.body.innerText.slice(0, 300) : null });
    const s1 = snap(); await wait(6000); const s2 = snap(); out.item10 = { domPanel: !!dom, domChanged: !!dom && s1.dom !== s2.dom, domHasRows: !!dom && /\d/.test(s2.dom || ''), tapePanel: !!tape, tapeRows: s2.tapeRows, tapeChanged: !!tape && s1.tape !== s2.tape };
    return out; });
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
