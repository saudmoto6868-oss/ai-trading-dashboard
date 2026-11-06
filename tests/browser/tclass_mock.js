// MOCK-TESTED ONLY. Trade classes widget (type "tclass", modules/ws/24b_tclass.js): fake OKX candles for BTC-USDT (a range 60000..61000
// whose last close sits on the support) -> the widget lists a long bounce trade, sends it to Alerts, and readyList() (Setup Card / strip) has it.
// Run: python3 -c "from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w').write(b(['BTC-USDT']))" && NODE_PATH=$(npm root -g) node tests/browser/tclass_mock.js /tmp/ws.html
const { chromium } = require('playwright');
const BAR = { '5m': 300e3, '15m': 900e3, '1H': 3600e3, '4H': 14400e3, '1D': 864e5, '1W': 6048e5, '1Mutc': 2592e6 };
function candles(bar, limit) {   // OKX shape, newest first; a clean range with a fixed small noise, last close at the bottom
  const step = BAR[bar] || 900e3, n = 400, now = Math.floor(Date.now() / step) * step, out = [];
  let prev = null;
  for (let i = 0; i < n; i++) {
    const c = 60500 + 500 * Math.sin(2 * Math.PI * i / 40 - Math.PI / 2) + 15 * Math.sin(i * 12.9898), o = prev == null ? c : prev, w = 40 * (1 + 0.5 * Math.abs(Math.sin(i * 7.31)));
    out.push([String(now - (n - 1 - i) * step), String(o), String(Math.max(o, c) + w), String(Math.min(o, c) - w), String(c), '10', '0', '0', '1']); prev = c;
  }
  return out.reverse().slice(0, limit);
}
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue();
    if (/okx\.com\/api\/v5\/market\/(history-)?candles/.test(u)) { const q = new URL(u).searchParams; const hist = /history-candles/.test(u);
      return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: hist ? [] : candles(q.get('bar'), +q.get('limit') || 300) }) }); }
    return r.abort(); });
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(800);
  await p.evaluate(() => { Ws.build([["chart", {x:0,y:0,w:600,h:400}, {sym:"BTC-USDT", tf:"15m"}], ["tclass", {x:610,y:0,w:700,h:400}, {sym:"BTC-USDT"}], ["setup", {x:0,y:410,w:500,h:400}, {}]]); });
  await p.waitForFunction(() => Object.keys(TC.res).length && !TC.busy, null, { timeout: 30000 }).catch(() => {});
  await p.waitForTimeout(500);
  const res = await p.evaluate(() => { const r = TC.res["Scalp|BTC-USDT"] || {}, pn = Ws.panels.find(x => x.type === "tclass");
    return { err: r.err || null, n: r.n, cards: (r.cards || []).map(c => ({ dir: c.direction, tt: c.ttype, tfc: c.tfc, pct: Math.round(100 * c.score / c.max), pts: c.pts, plan: c.plan, hist: c.hist && c.hist.n, why: c.why })),
      rows: pn.body.querySelectorAll("tr[data-i]").length, foot: pn.body.innerText.includes("not evidence"), alerts: Alerts.list.filter(a => a.card && a.card.src === "tclass").length,
      ready: readyList().filter(e => e.src === "tclass").length, menu: [...document.querySelectorAll("#bar option")].some(o => o.value === "tclass"), title: pn.ttl.textContent }; });
  console.log(JSON.stringify(res, null, 1));
  const c0 = res.cards.find(c => c.dir === 'bullish'); let ok = !res.err && res.rows >= 1 && !!c0 && c0.plan.stop < c0.plan.entry && c0.plan.entry < c0.plan.tps[0] && c0.tt === 'Scalp' && c0.tfc === '5m' && res.menu && res.foot && res.alerts >= 1 && res.ready >= 1;
  // switch to Swing (1W bias / 1D setup / 4H entry) on the same mock
  await p.evaluate(() => { const pn = Ws.panels.find(x => x.type === "tclass"); const s = pn.body.querySelector("select"); s.value = "Swing"; s.dispatchEvent(new Event("change")); });
  await p.waitForFunction(() => TC.res["Swing|BTC-USDT"] && !TC.busy, null, { timeout: 30000 }).catch(() => {});
  const sw = await p.evaluate(() => { const r = TC.res["Swing|BTC-USDT"] || {}; return { err: r.err || null, cards: (r.cards || []).map(c => c.ttype + "/" + c.tfc) }; });
  console.log('swing', JSON.stringify(sw));
  ok = ok && !sw.err && sw.cards.every(x => x === 'Swing/4H');
  console.log('errors', errs.length, errs[0] || ''); console.log(ok && !errs.length ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok && !errs.length ? 0 : 1);
})();
