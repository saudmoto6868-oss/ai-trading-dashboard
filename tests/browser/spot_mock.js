// MOCK-TESTED ONLY. Spot desk widget (type "spot", modules/ws/24d_spot.js) reads CFG.spot; here a fixture snapshot is injected.
// Run: python3 -c "from modules.workspace import build_workspace_html as b; open('/tmp/ws.html','w').write(b(['BTC-USDT']))" && NODE_PATH=$(npm root -g) node tests/browser/spot_mock.js /tmp/ws.html
const { chromium } = require('playwright');
const SNAP = { generated: "2026-11-15T05:00:00Z", log: ["الدهب: 3 مدد"], risk_off: 0, news: [], classes: { GOLD: "metals", BTC: "crypto" },
  ideas: [{ asset: "GOLD", name: "الدهب", kind: "buy", title: "شراء", entry: [2300, 2310], stop: 2280, targets: [2350, 2400], rr: 2.5, conf: 4, pros: ["دعم شهري"], cons: ["دولار قوي"] }],
  markets: [{ asset: "GOLD", name: "الدهب", cls: "metals", price: 2305.5, wk: 1.2, score: 3, zone: "support", n_ideas: 1 }, { asset: "BTC", name: "البيتكوين", cls: "crypto", price: 60000, wk: -2, score: -1, zone: "", n_ideas: 0 }],
  brains: [{ asset: "BTC", price: 60000, head: "HEAD-BTC", news: { score: 0 }, guard: [], horizons: {}, setups: [] }, { asset: "GOLD", price: 2305.5, head: "HEAD-GOLD", news: { score: 0 }, guard: [], horizons: { day: { label: "يوم", tf: "1D", score: -10, verdict: "wait", verdict_ar: "استنى", reasons: ["ضغط"] } },
    setups: [{ asset: "GOLD", school_ar: "كلاسيك", name: "SETUP-COUP", side: "buy", tf: "1W", ev_label: "t 3.2 n 41" }, { asset: "GOLD", school_ar: "فلو", name: "SETUP-NOEV", side: "sell", tf: "1D" }] }] };
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }).catch(() => chromium.launch());
  const p = await (await b.newContext({ viewport: { width: 1400, height: 900 } })).newPage(); const errs = [];
  p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); return r.abort(); });
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(800);
  await p.evaluate(snap => { CFG.spot = snap; Ws.build([["spot", { x: 0, y: 0, w: 900, h: 700 }, {}]]); }, SNAP);
  await p.waitForTimeout(300);
  const txt = async () => p.evaluate(() => Ws.panels.find(x => x.type === "spot").body.innerText);
  const views = {};
  for (const v of ["ideas", "brain", "setups", "markets", "log"]) {
    await p.evaluate(v => { const pn = Ws.panels.find(x => x.type === "spot"); const s = pn.body.querySelectorAll("select")[2]; s.value = v; s.dispatchEvent(new Event("change")); }, v);
    views[v] = await txt();
  }
  const menu = await p.evaluate(() => [...document.querySelectorAll("#bar option")].some(o => o.value === "spot") || !!document.querySelector("#bar") );
  // class filter: crypto hides the gold idea, setups and market; the brain line follows the class
  await p.evaluate(() => { const pn = Ws.panels.find(x => x.type === "spot"); const v = pn.body.querySelectorAll("select")[2]; v.value = "ideas"; v.dispatchEvent(new Event("change")); const s = pn.body.querySelectorAll("select")[0]; s.value = "crypto"; s.dispatchEvent(new Event("change")); });
  const crypto = await txt();
  const cryptoOk = !/SETUP-COUP/.test(crypto) && !/الدهب/.test(crypto) && /HEAD-BTC/.test(crypto);
  // screenshot for the owner (deviceScaleFactor 2)
  await p.evaluate(() => { const pn = Ws.panels.find(x => x.type === "spot"); const s = pn.body.querySelectorAll("select")[0]; s.value = ""; s.dispatchEvent(new Event("change")); });
  await p.evaluate(() => { const pn = Ws.panels.find(x => x.type === "spot"); const s = pn.body.querySelectorAll("select")[2]; s.value = "setups"; s.dispatchEvent(new Event("change")); });
  const ok = /شراء|Entry|دخول/.test(views.ideas) && /HEAD-GOLD/.test(views.brain) && /استنى|Wait|wait/.test(views.brain)
    && /SETUP-COUP/.test(views.setups) && /t 3.2 n 41/.test(views.setups) && /SETUP-NOEV/.test(views.setups) && /not tested|لسه ماتقاسش/.test(views.setups)
    && /الدهب/.test(views.markets) && /الدهب: 3 مدد/.test(views.log) && /HEAD-/.test(views.ideas) && cryptoOk && menu && !errs.length;
  const shot = process.env.SPOT_SHOT || "";
  if (shot) await p.locator(".spw").first().screenshot({ path: shot });
  console.log(JSON.stringify({ ideas: views.ideas.slice(0, 120), setupsHasEv: /t 3.2 n 41/.test(views.setups), menu, cryptoOk }));
  console.log('errors', errs.length, errs[0] || ''); console.log(ok ? 'PASS' : 'FAIL');
  await b.close(); process.exit(ok ? 0 : 1);
})();
