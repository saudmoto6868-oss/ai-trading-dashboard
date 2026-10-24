// MOCK-TESTED ONLY. Signals table + alert cards show a mini chart (spark + entry / stop / TP1); the Setup Card has the class select; all class selects follow ONE shared filter.
// Run: NODE_PATH=$(npm root -g) node tests/browser/mini_chart_class_ui_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1700, height: 950 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(800);
  const res = await p.evaluate(async () => { const wait = ms => new Promise(r => setTimeout(r, ms)); const sp = Array.from({ length: 40 }, (_, i) => 100 + Math.sin(i / 4) * 3);
    const mk = (symbol, score) => ({ symbol, direction: 'bullish', ttype: 'Day Trade', tfk: '1h', score, max: 10, tags: [], spark: sp, plan: { entry: 101, stop: 99, tps: [104, 105, 106] } });
    CFG.ready = [mk('BTC-USDT', 9), mk('HL:xyz:GOLD', 8), mk('Y:EURUSD=X', 7)]; Ws.build([['signals', { x: 0, y: 0, w: 700, h: 300 }, {}], ['setup', { x: 0, y: 300, w: 500, h: 300 }, {}], ['ready', { x: 700, y: 0, w: 500, h: 300 }, {}]]); await wait(800);
    const sig = Ws.panels.find(q => q.type === 'signals'), set = Ws.panels.find(q => q.type === 'setup'), out = {};
    out.signalsRows = sig.body.querySelectorAll('tr[data-i]').length; out.signalsSparks = sig.body.querySelectorAll('tr[data-i] svg polyline').length;
    out.setupHasSelect = !!set.body.querySelector('.tb select'); const sels = [...document.querySelectorAll('select')].filter(s => [...s.options].some(o => o.value === '__best')); out.classSelects = sels.length;
    const cs = set.body.querySelector('.tb select'); cs.value = 'Metals'; cs.dispatchEvent(new Event('change')); await wait(300);
    out.allFollow = sels.every(s => s.value === 'Metals'); out.signalsAfterMetals = sig.body.querySelectorAll('tr[data-i]').length;
    const a = { card: mk('BTC-USDT', 9), t: Date.now() }; out.alertCardSpark = alertCard(a).querySelectorAll('svg polyline').length; return out; });
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
