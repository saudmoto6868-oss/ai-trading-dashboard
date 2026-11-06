// MOCK-TESTED ONLY. Trade Classes (deliberation engine) widget (type "tclass", modules/ws/24b_tclass.js): fake OKX candles for BTC-USDT (a range 60000..61000
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
  await p.evaluate(() => { if (!SYMS.includes("ETH-USDT")) SYMS.push("ETH-USDT"); Ws.build([["chart", {x:0,y:0,w:600,h:400}, {sym:"BTC-USDT", tf:"15m"}], ["tclass", {x:610,y:0,w:900,h:800}, {sym:"BTC-USDT", tc:{uni:"watch", show:"all"}}], ["setup", {x:0,y:410,w:500,h:400}, {}]]); });
  const out = {}; let ok = true;
  for (const style of ["Scalp", "Day Trade", "Swing", "Position"]) {
    await p.evaluate(st => { const pn = Ws.panels.find(x => x.type === "tclass"); const s = pn.body.querySelector("select"); s.value = st; s.dispatchEvent(new Event("change")); }, style);
    await p.waitForFunction(st => SYMS.every(s => TC.res[st + "|" + s]) && !TC.busy, style, { timeout: 60000 }).catch(() => {});
    out[style] = await p.evaluate(st => { const pn = Ws.panels.find(x => x.type === "tclass"); return SYMS.map(s => { const r = TC.res[st + "|" + s] || {};
      return { s, err: r.err || null, ideas: (r.ideas || []).length, dets: [...new Set((r.ideas || []).map(x => x.det))], best: r.ideas && r.ideas[0] ? { v: r.ideas[0].j.verdict, pros: r.ideas[0].j.pros.length, cons: r.ideas[0].j.cons.length, ok: planOk(r.ideas[0].j.plan, r.ideas[0].side > 0 ? "bullish" : "bearish") } : null }; })
      .concat([{ cards: pn.body.querySelectorAll(".cd").length, sum: pn.body.querySelector(".sum").innerText.slice(0, 160) }]); }, style);
    const rows = out[style].slice(0, -1), ui = out[style][out[style].length - 1];
    ok = ok && rows.every(r => !r.err && r.ideas >= 1 && r.best && r.best.ok && (r.best.pros + r.best.cons) >= 2) && ui.cards >= 1 && /2\/2/.test(ui.sum);
  }
  console.log(JSON.stringify(out, null, 1));
  const al = await p.evaluate(() => { const take = SYMS.filter(s => { const r = TC.res["Position|" + s]; return r && r.ideas[0] && r.ideas[0].j.verdict === "TAKE" && r.ideas[0].now; }).length;
    return { take, alerts: Alerts.list.filter(a => a.card && a.card.src === "tclass" && a.card.ttype === "Position").length, menu: [...document.querySelectorAll("#bar option")].some(o => o.value === "tclass") }; });
  console.log('alerts', JSON.stringify(al)); ok = ok && al.alerts === al.take && al.menu;
  // harmonic school: a hand-built bullish Gartley (X 100, A 110, B 103.82, C 107.6, D 102.14) -> TC.harm gives a valid long
  const hm = await p.evaluate(() => { const piv = [[0, 104], [40, 100], [60, 110], [75, 103.82], [88, 107.6], [104, 102.14]], rows = [];
    for (let i = 0; i <= 104; i++){ let k = 0; while (piv[k+1][0] < i) k++; const [i0, p0] = piv[k], [i1, p1] = piv[k+1], c = p0 + (p1 - p0)*(i - i0)/(i1 - i0) + 0.03*Math.sin(i*12.9898), o = rows.length ? rows[rows.length-1].c : c, w = 0.08*(1 + 0.5*Math.abs(Math.sin(i*7.31)));
      rows.push({t:i*9e5, o, h:Math.max(o, c) + w, l:Math.min(o, c) - w, c, v:1}); }
    return TC.harm("BTC-USDT", "Scalp", rows, [], [], {}).map(c => ({ dir: c.direction, tag: c.tags[0][0], ok: planOk(c.plan, c.direction) })); });
  console.log('harmonic', JSON.stringify(hm)); ok = ok && hm.length >= 1 && hm[0].dir === 'bullish' && /Gartley/.test(hm[0].tag) && hm[0].ok;
  console.log('errors', errs.length, errs[0] || ''); console.log(ok && !errs.length ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok && !errs.length ? 0 : 1);
})();
