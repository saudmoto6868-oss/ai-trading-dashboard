#!/usr/bin/env node
/* XPiX Agent (step 1): drives the REAL platform in a real browser (Playwright) so automation (n8n, Claude team, Telegram bot) can use it like a person.
   Runs on the owner's Mac against the local Streamlit app (default http://localhost:8501). Read / view / draw only: no orders, no keys, no outside pages.
   Library:  const { XpixAgent } = require("./xpix_agent");   CLI:  node tools/xpix_agent/xpix_agent.js <command> [args]   (see --help) */
const fs = require("fs"), os = require("os"), path = require("path"), { spawnSync } = require("child_process");

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
  params(ind, panel){ return this.x("params", ind, panel); } setParam(ind, key, value, panel){ return this.x("setParam", ind, key, value, panel); } layout(name){ return this.x("layout", name); }
  draw(o, panel){ return this.x("draw", o, panel); } clearDrawings(panel){ return this.x("clearDrawings", panel); }
  // ---- video (high quality): CDP screencast frames (JPEG q95) -> ffmpeg H.264 (CRF 16, yuv420p, constant fps). Playwright's own recordVideo is low-bitrate VP8, so it is not used. Needs ffmpeg on the PATH. ----
  async recStart(o = {}){
    if (this.rec) throw new Error("already recording");
    const fps = Math.max(5, Math.min(60, +o.fps || 30)), w = +o.w || 1920, h = +o.h || 1080, dir = fs.mkdtempSync(path.join(os.tmpdir(), "xpix_rec_"));
    this.rec = { fps, w, h, dir, frames: [], out: path.resolve(o.out || "xpix_" + new Date().toISOString().replace(/[:.]/g, "-") + ".mp4"), crf: Math.max(10, Math.min(28, +o.crf || 16)), vp: this.page.viewportSize() };
    await this.page.setViewportSize({ width: w, height: h }); await this.settle(300);
    const cdp = await this.ctx.newCDPSession(this.page); this.rec.cdp = cdp; let n = 0;
    cdp.on("Page.screencastFrame", async ev => { try { const f = path.join(dir, "f" + String(n++).padStart(6, "0") + ".jpg"); fs.writeFileSync(f, Buffer.from(ev.data, "base64")); this.rec.frames.push({ f, t: ev.metadata.timestamp }); await cdp.send("Page.screencastFrameAck", { sessionId: ev.sessionId }); } catch(e){} });
    await cdp.send("Page.startScreencast", { format: "jpeg", quality: 95, maxWidth: w, maxHeight: h, everyNthFrame: 1 });
    return { ok: true, recording: true, w, h, fps, out: this.rec.out };
  }
  async recStop(){
    const R = this.rec; if (!R) throw new Error("not recording"); this.rec = null;
    try { await R.cdp.send("Page.stopScreencast"); } catch(e){} await this.page.waitForTimeout(200); try { await R.cdp.detach(); } catch(e){}
    try { if (R.vp) await this.page.setViewportSize(R.vp); } catch(e){}
    const fr = R.frames.slice().sort((a, b) => a.t - b.t); if (fr.length < 2){ return { ok: false, err: "no frames captured (the page did not change; try again)", frames: fr.length }; }
    const lines = []; fr.forEach((x, i) => { const d = i < fr.length - 1 ? Math.max(0.001, fr[i + 1].t - x.t) : 0.5; lines.push("file '" + x.f.replace(/'/g, "'\\''") + "'", "duration " + d.toFixed(4)); }); lines.push("file '" + fr[fr.length - 1].f + "'");
    const lst = path.join(R.dir, "list.txt"); fs.writeFileSync(lst, lines.join("\n")); fs.mkdirSync(path.dirname(R.out), { recursive: true });
    const r = spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-vf", "fps=" + R.fps + ",scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", String(R.crf), "-movflags", "+faststart", R.out], { encoding: "utf8" });
    if (r.error || r.status !== 0) return { ok: false, err: "ffmpeg failed: " + (r.error ? r.error.message + " (install ffmpeg: brew install ffmpeg)" : (r.stderr || "").slice(0, 300)), frames: fr.length, keptFrames: R.dir };
    try { fs.rmSync(R.dir, { recursive: true, force: true }); } catch(e){}
    const st = fs.statSync(R.out); return { ok: true, out: R.out, bytes: st.size, frames: fr.length, seconds: +(fr[fr.length - 1].t - fr[0].t).toFixed(2), fps: R.fps, size: R.w + "x" + R.h };
  }
  async record(sec, o = {}){ const a = await this.recStart(o); await this.page.waitForTimeout(Math.max(1, +sec) * 1000); const b = await this.recStop(); return b.ok ? Object.assign(b, { started: a.ok }) : b; }
  // ---- screenshots (real browser pixels, scale 2 by default) ----
  async shot(o = {}){ const out = path.resolve(o.out || "xpix_" + new Date().toISOString().replace(/[:.]/g, "-") + ".png"); fs.mkdirSync(path.dirname(out), { recursive: true });
    if (o.workspace){ const f = await this.ws(), r = await f.evaluate(s => XCMD.shot(s), o.scale || 1); if (!r.ok) throw new Error(r.err); fs.writeFileSync(out, Buffer.from(r.png.split(",")[1], "base64")); return { ok: true, out, w: r.w, h: r.h, kind: "workspace-canvas" }; }
    await this.page.screenshot({ path: out, fullPage: !!o.full }); const s = fs.statSync(out); return { ok: true, out, bytes: s.size, kind: o.full ? "full-page" : "viewport" }; }
}

async function cli(argv){
  const opt = {}, rest = []; for (let i = 0; i < argv.length; i++){ const a = argv[i]; if (a === "--headed") opt.headed = true; else if (a === "--full") opt.full = true; else if (a === "--workspace") opt.workspace = true;
    else if (/^--(url|profile|out|scale|panel|json|fps|size|crf)$/.test(a)) opt[a.slice(2)] = argv[++i]; else rest.push(a); }
  const [cmd, ...a] = rest;
  if (!cmd || cmd === "help" || cmd === "--help"){ console.log(`XPiX Agent: node xpix_agent.js [--url U] [--headed] [--profile DIR] <command>
  pages | page <name|index> | state | list | symbol <SYM> | tf <TF> | toggle <indicator> <on|off> | addpanel <type> | closepanel <id>
  params <indicator> | set <indicator> <key> <value> | layout <standard|blank|save>
  record <seconds> [--out f.mp4] [--size 1920x1080] [--fps 30] [--crf 16]   (high quality H.264, needs ffmpeg) | recstart / recstop / wait <sec> (inside batch: record while other steps run)
  draw '<json>' | cleardrawings | shot [--out f.png] [--full] [--workspace] [--scale N] | batch '<json array of {cmd,args}>'
  Flags: --panel <id> targets one chart panel. Env: XPIX_URL, XPIX_PROFILE, XPIX_CHROME. Read / view / draw only.`); return 0; }
  const ag = new XpixAgent({ url: opt.url, profile: opt.profile, headed: opt.headed }); await ag.start();
  const RO = () => { const m = /^(\d+)x(\d+)$/.exec(opt.size || ""); return { out: opt.out, fps: opt.fps, crf: opt.crf, w: m ? +m[1] : undefined, h: m ? +m[2] : undefined }; };
  const one = async (c, args) => { const P = opt.panel;
    switch (c){ case "pages": return ag.pages(); case "page": return ag.openPage(args[0]); case "state": return ag.state(); case "list": return ag.list(P);
      case "symbol": return ag.symbol(args[0], P); case "tf": return ag.tf(args[0], P); case "toggle": return ag.toggle(args[0], /^(on|1|true)$/i.test(args[1] || "on"), P);
      case "addpanel": return ag.addPanel(args[0]); case "closepanel": return ag.closePanel(args[0]); case "params": return ag.params(args[0], P); case "set": return ag.setParam(args[0], args[1], args[2], P); case "layout": return ag.layout(args[0]);
      case "recstart": return ag.recStart(RO()); case "recstop": return ag.recStop(); case "record": return ag.record(args[0] || 5, RO()); case "wait": await ag.page.waitForTimeout((+args[0] || 1) * 1000); return { ok: true };
      case "draw": return ag.draw(JSON.parse(args[0]), P); case "cleardrawings": return ag.clearDrawings(P);
      case "shot": return ag.shot({ out: opt.out, full: opt.full, workspace: opt.workspace, scale: opt.scale ? +opt.scale : 1 }); default: throw new Error("unknown command: " + c); } };
  let res; try { res = cmd === "batch" ? await (async () => { const o = []; for (const s of JSON.parse(a[0])) o.push(await one(s.cmd, s.args || [])); return o; })() : await one(cmd, a); }
  catch(e){ res = { ok: false, err: String(e.message || e) }; } finally { await ag.stop(); }
  console.log(JSON.stringify(res)); return res && res.ok === false ? 1 : 0;
}
module.exports = { XpixAgent };
if (require.main === module) cli(process.argv.slice(2)).then(c => process.exit(c));
