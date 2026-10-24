// MOCK-TESTED ONLY. Saved heat-map history: (1) 7 days of synthetic book snapshots are kept compacted, (2) when localStorage throws QuotaExceeded the save retries with the oldest quarter dropped instead of silently stopping, (3) other keys are never removed, (4) a save stays cheap.
// Run: NODE_PATH=$(npm root -g) node tests/browser/heatmap_history_quota_mock.js /tmp/ws.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 120)));
  await p.route('**/*', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(800); await p.evaluate(() => { Ws.build(Ws.defaults()); });
  const res = await p.evaluate(async () => { const ch = Ws.panels.find(q => q.type === 'chart').chart; const out = {}; ch.sym = 'TEST-USDT'; ch.hm = null; ch.hmInit(); const now = Date.now();
    for (let m = 0; m < 7*24*60; m += 3) { const t = now - m*60000, lv = []; for (let i = 0; i < 90; i++) lv.push([100 + i*0.5, 1 + ((i*7 + m) % 13)]); ch.hmAdd({ t, bb: 120, ba: 120.5, lv }); }
    out.buckets = ch.hm.b.size; localStorage.setItem('other_key', 'keep'); const t0 = performance.now(); ch.hmSave(now); out.saveMs = Math.round(performance.now() - t0);
    const raw = localStorage.getItem('ai_ws_v5_hm_TEST-USDT'); out.savedChars = raw ? raw.length : 0; out.oldestDaysSaved = raw ? Math.round((now - Math.min(...Object.keys(JSON.parse(raw).b).map(Number)))/86400e3*10)/10 : null;
    const orig = Storage.prototype.setItem; let fails = 0; Storage.prototype.setItem = function(k, v){ if (k.includes('_hm_') && v.length > 200000){ fails++; throw new DOMException('quota', 'QuotaExceededError'); } return orig.call(this, k, v); };
    localStorage.removeItem('ai_ws_v5_hm_TEST-USDT'); ch.hmSave(now); Storage.prototype.setItem = orig; const raw2 = localStorage.getItem('ai_ws_v5_hm_TEST-USDT');
    out.quotaFails = fails; out.savedAfterQuota = raw2 ? raw2.length : 0; out.otherKeyKept = localStorage.getItem('other_key') === 'keep'; localStorage.removeItem('ai_ws_v5_hm_TEST-USDT'); return out; });
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
