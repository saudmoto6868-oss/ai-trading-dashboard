#!/usr/bin/env node
/* XPiX Agent (step 1): drives the REAL platform in a real browser (Playwright) so automation (n8n, Claude team, Telegram bot) can use it like a person.
   Runs on the owner's Mac against the local Streamlit app (default http://localhost:8501). Read / view / draw only: no orders, no keys, no outside pages.
   Library:  const { XpixAgent } = require("./xpix_agent");   CLI:  node tools/xpix_agent/xpix_agent.js <command> [args]   (see --help) */
const fs = require("fs"), os = require("os"), path = require("path");

class XpixAgent {
  constructor(o = {}){ this.url = o.url || process.env.XPIX_URL || "http://localhost:8501"; this.profile = o.profile || process.env.XPIX_PROFILE || path.join(os.homedir(), ".xpix_agent_profile");
    this.headed = !!o.headed; this.viewport = o.viewport || { width: 1600, height: 1000 }; this.scale = o.scale || 2; this.ctx = null; this.page = null; this.errors = []; }
  async start(){
    const { chromium } = require("playwright");
    const exe = process.env.XPIX_CHROME || undefined;   // optional: a specific Chrome / Chromium binary
    this.ctx = await chromium.launchPersistentContext(this.profile, { headless: !this.headed, viewport: this.viewport, deviceScaleFactor: this.scale, executablePath: exe, args: ["--no-sandbox"], acceptDownloads: true });
    this.page = this.ctx.pages()[0] || await this.ctx.newPage(); this.page.on("pageerror", e => this.errors.push(String(e).slice(0, 200)));
    await this.page.goto(this.url, { waitUntil: "domcontentloaded" }); await this.page.waitForSelector('[data-testid="stApp"]', { timeout: 60000 }); await this.settle(); return this;
  }
  async stop(){ if (this.ctx) await this.ctx.close(); this.ctx = null; }
  async settle(ms = 400){ await this.page.waitForTimeout(ms); try { await this.page.waitForFunction(() => !document.querySelector('[data-testid="stStatusWidget"]'), null, { timeout: 30000 }); } catch(e){} await this.page.waitForTimeout(ms); }
  // ---- Streamlit pages (the top page bar) ----
  async _pageGroup(timeout = 120000){ const t0 = Date.now(); for (;;){ try { return await this._pageGroup1(); } catch(e){ if (Date.now() - t0 > timeout) throw e; await this.page.waitForTimeout(1500); } } }
  async _pageGroup1(){ const groups = this.page.locator('[data-testid="stRadio"]'), n = await groups.count(); let best = null, bestN = 0;
    for (let i = 0; i < n; i++){ const c = await groups.nth(i).locator('[data-testid="stRadioOption"]').count(); if (c > bestN){ best = groups.nth(i); bestN = c; } } if (!best || bestN < 6) throw new Error("page bar not found"); return best; }
  async pages(){ const g = await this._pageGroup(); return (await g.locator('[data-testid="stRadioOption"]').allInnerTexts()).map((t, i) => ({ i, label: t.trim() })); }
  async openPage(which){ const g = await this._pageGroup(), labels = g.locator('[data-testid="stRadioOption"]'), all = await this.pages(); let k = -1;
    if (/^\d+$/.test(String(which))) k = +which; else k = all.findIndex(p => p.label.toLowerCase().includes(String(which).toLowerCase()));
    if (k < 0 || k >= all.length) throw new Error("unknown page: " + which + " (see pages)"); await labels.nth(k).click(); await this.settle(800); return { ok: true, page: all[k] }; }
  // ---- Workspace (XCMD inside the iframe) ----
  async ws(timeout = 45000){ const t0 = Date.now();
    while (Date.now() - t0 < timeout){ for (const f of this.page.frames()){ try { if (await f.evaluate(() => !!(window.XCMD && typeof Ws !== "undefined" && Ws.panels && Ws.panels.length))) return f; } catch(e){} } await this.page.waitForTimeout(500); }
    throw new Error("Workspace not found: open the Workspace page first (page Workspace)"); }
  async x(method, ...args){ const f = await this.ws(); return f.evaluate(([m, a]) => { const r = window.XCMD[m](...a); return Promise.resolve(r); }, [method, args]); }
  state(){ return this.x("state"); } list(panel){ return this.x("list", panel); }
  symbol(s, panel){ return this.x("setSymbol", s, panel); }
  async tf(t, panel){ const st = await this.state(), hit = st.ok && st.tfs.find(k => k.toLowerCase() === String(t).toLowerCase()); return this.x("setTf", hit || t, panel); }   // "1h" -> "1H"
  toggle(ind, on, panel){ return this.x("toggle", ind, !!on, panel); } addPanel(type){ return this.x("addPanel", type); } closePanel(id){ return this.x("closePanel", id); }
  draw(o, panel){ return this.x("draw", o, panel); } clearDrawings(panel){ return this.x("clearDrawings", panel); }
  // ---- screenshots (real browser pixels, scale 2 by default) ----
  async shot(o = {}){ const out = path.resolve(o.out || "xpix_" + new Date().toISOString().replace(/[:.]/g, "-") + ".png"); fs.mkdirSync(path.dirname(out), { recursive: true });
    if (o.workspace){ const f = await this.ws(), r = await f.evaluate(s => XCMD.shot(s), o.scale || 1); if (!r.ok) throw new Error(r.err); fs.writeFileSync(out, Buffer.from(r.png.split(",")[1], "base64")); return { ok: true, out, w: r.w, h: r.h, kind: "workspace-canvas" }; }
    await this.page.screenshot({ path: out, fullPage: !!o.full }); const s = fs.statSync(out); return { ok: true, out, bytes: s.size, kind: o.full ? "full-page" : "viewport" }; }
}

async function cli(argv){
  const opt = {}, rest = []; for (let i = 0; i < argv.length; i++){ const a = argv[i]; if (a === "--headed") opt.headed = true; else if (a === "--full") opt.full = true; else if (a === "--workspace") opt.workspace = true;
    else if (/^--(url|profile|out|scale|panel|json)$/.test(a)) opt[a.slice(2)] = argv[++i]; else rest.push(a); }
  const [cmd, ...a] = rest;
  if (!cmd || cmd === "help" || cmd === "--help"){ console.log(`XPiX Agent: node xpix_agent.js [--url U] [--headed] [--profile DIR] <command>
  pages | page <name|index> | state | list | symbol <SYM> | tf <TF> | toggle <indicator> <on|off> | addpanel <type> | closepanel <id>
  draw '<json>' | cleardrawings | shot [--out f.png] [--full] [--workspace] [--scale N] | batch '<json array of {cmd,args}>'
  Flags: --panel <id> targets one chart panel. Env: XPIX_URL, XPIX_PROFILE, XPIX_CHROME. Read / view / draw only.`); return 0; }
  const ag = new XpixAgent({ url: opt.url, profile: opt.profile, headed: opt.headed }); await ag.start();
  const one = async (c, args) => { const P = opt.panel;
    switch (c){ case "pages": return ag.pages(); case "page": return ag.openPage(args[0]); case "state": return ag.state(); case "list": return ag.list(P);
      case "symbol": return ag.symbol(args[0], P); case "tf": return ag.tf(args[0], P); case "toggle": return ag.toggle(args[0], /^(on|1|true)$/i.test(args[1] || "on"), P);
      case "addpanel": return ag.addPanel(args[0]); case "closepanel": return ag.closePanel(args[0]); case "draw": return ag.draw(JSON.parse(args[0]), P); case "cleardrawings": return ag.clearDrawings(P);
      case "shot": return ag.shot({ out: opt.out, full: opt.full, workspace: opt.workspace, scale: opt.scale ? +opt.scale : 1 }); default: throw new Error("unknown command: " + c); } };
  let res; try { res = cmd === "batch" ? await (async () => { const o = []; for (const s of JSON.parse(a[0])) o.push(await one(s.cmd, s.args || [])); return o; })() : await one(cmd, a); }
  catch(e){ res = { ok: false, err: String(e.message || e) }; } finally { await ag.stop(); }
  console.log(JSON.stringify(res)); return res && res.ok === false ? 1 : 0;
}
module.exports = { XpixAgent };
if (require.main === module) cli(process.argv.slice(2)).then(c => process.exit(c));
