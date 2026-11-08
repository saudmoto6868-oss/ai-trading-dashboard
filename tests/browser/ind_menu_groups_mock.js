// MOCK-TESTED ONLY. The indicator list is grouped / ordered / renamed ONLY: same 49+ ids as before, every group is one contiguous block, children sit right after their parent, nothing changes what it does (toggle still flips state).
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(800);
  await p.evaluate(() => { Ws.build([['chart', { x: 10, y: 10, w: 1400, h: 800 }, { sym: 'BTC-USDT', tf: '15m', group: 0 }]]); }); await p.waitForTimeout(1500);
  const r = await p.evaluate(() => { const it = Ws.panels[0].indItems, ids = it.map(i => i.id), o = {}; o.n = ids.length; o.dupes = ids.length !== new Set(ids).size;
    const need = ['ma','vwap','sbox','kz','sync','liqm','astro','gann','kzs','dot3','bub','dot','dom','mk','fp','delta','smt','vp','ew','ote','bvd','harm','sig','flow','volume','rsi','lv','ll','llt','dcol','cwide','cown','ofg','read','zlog','ofs','div','mt5','msb','don','zn','bso','bbshow','r2','rm','macd','adx','cci','psar']; o.missing = need.filter(x => !ids.includes(x));
    const seen = []; it.forEach(i => { const g = i.grp && i.grp.en; if (seen[seen.length - 1] !== g) seen.push(g); }); o.groups = seen; o.contiguous = seen.length === new Set(seen).size;
    o.firstChildOk = it.every((i, k) => !i.lvl || (k > 0 && it[k - 1].grp === i.grp)); o.abbr = it.filter(i => !/\(([A-Z0-9]{2,6})\)|^(VWAP|RSI|MACD|ADX|CCI)/.test(i.label)).map(i => i.id);
    const x = XCMD.toggle('msb', true); o.on = XCMD.state().panels[0].ind.includes('msb'); XCMD.toggle('msb', false); o.off = !XCMD.state().panels[0].ind.includes('msb'); return o; });
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '');
  const ok = r.n >= 49 && !r.dupes && !r.missing.length && r.contiguous && r.firstChildOk && !r.abbr.length && r.on && r.off && !errs.length;
  console.log(ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
