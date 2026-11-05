#!/usr/bin/env node
/* XPiX Agent HTTP server (step 4): lets n8n / the Claude team / the Telegram bot call the Agent over HTTP on the owner's Mac.
   Safety: listens on 127.0.0.1 only (unless you pass --host), a bearer token from the ENV is REQUIRED (the server will not start without it),
   a fixed allow-list of commands (read / view / draw: no orders, no keys, nothing is evaluated), screenshots / videos are written ONLY inside the output folder,
   one command at a time, 60 requests / minute, 64 KB request bodies.
   Run:  XPIX_AGENT_TOKEN=<long random string> node tools/xpix_agent/server.js [--port 8765] [--host 127.0.0.1] [--out ./xpix_out] [--url http://localhost:8501] [--headed]
   Call: curl -H "Authorization: Bearer $XPIX_AGENT_TOKEN" -d '{"cmd":"tf","args":["15m"]}' http://127.0.0.1:8765/cmd */
const http = require("http"), fs = require("fs"), path = require("path"), crypto = require("crypto");
const { XpixAgent, COMMANDS } = require("./xpix_agent");

const FILE_RE = /^[A-Za-z0-9._-]{1,80}\.(png|mp4)$/;
function tokenOk(got, want){ const a = Buffer.from(String(got || "")), b = Buffer.from(String(want)); return a.length === b.length && crypto.timingSafeEqual(a, b); }

function createServer({ agent, token, outDir, rate = 60, maxBody = 65536 }){
  if (!token || String(token).length < 16) throw new Error("XPIX_AGENT_TOKEN is required (at least 16 characters)");
  outDir = path.resolve(outDir || "xpix_out"); fs.mkdirSync(outDir, { recursive: true });
  let chain = Promise.resolve(), hits = [];
  const send = (res, code, obj, type) => { const body = type ? obj : JSON.stringify(obj); res.writeHead(code, { "content-type": type || "application/json", "cache-control": "no-store" }); res.end(body); };
  const safeOut = (name, ext) => { const base = name ? path.basename(String(name)) : ""; const n = FILE_RE.test(base) && base.endsWith(ext) ? base : "xpix_" + new Date().toISOString().replace(/[:.]/g, "-") + ext; return path.join(outDir, n); };
  const once = (c, args, o) => { const ext = c === "shot" ? ".png" : /^rec/.test(c) ? ".mp4" : null; const oo = Object.assign({}, o); if (ext) oo.out = safeOut(oo.out, ext); else delete oo.out;
    return agent.run(c, args || [], oo).then(r => { if (r && r.out){ r.file = "/files/" + path.basename(r.out); delete r.out; } return r; }); };
  const exec = body => { const job = chain.then(async () => {
      if (Array.isArray(body)) { if (body.length > 40) return { ok: false, err: "batch too long (max 40)" }; const out = []; for (const s of body){ if (!s || !COMMANDS.includes(s.cmd)){ out.push({ ok: false, err: "unknown command" }); break; } try { out.push(await once(s.cmd, s.args, s.opts)); } catch(e){ out.push({ ok: false, err: String(e.message || e) }); break; } } return out; }
      if (!body || !COMMANDS.includes(body.cmd)) return { ok: false, err: "unknown command", commands: COMMANDS };
      try { return await once(body.cmd, body.args, body.opts); } catch(e){ return { ok: false, err: String(e.message || e) }; } });
    chain = job.catch(() => {}); return job; };
  return http.createServer((req, res) => {
    const auth = /^Bearer (.+)$/.exec(req.headers.authorization || "");
    if (!auth || !tokenOk(auth[1], token)) return send(res, 401, { ok: false, err: "unauthorized" });
    const now = Date.now(); hits = hits.filter(t => now - t < 60000); if (hits.length >= rate) return send(res, 429, { ok: false, err: "rate limit" }); hits.push(now);
    const url = (req.url || "").split("?")[0];
    if (req.method === "GET" && url === "/health") return send(res, 200, { ok: true, commands: COMMANDS });
    if (req.method === "GET" && url.startsWith("/files/")){ const name = decodeURIComponent(url.slice(7)); if (!FILE_RE.test(name)) return send(res, 400, { ok: false, err: "bad file name" });
      const f = path.join(outDir, name); if (path.dirname(f) !== outDir || !fs.existsSync(f)) return send(res, 404, { ok: false, err: "not found" });
      res.writeHead(200, { "content-type": name.endsWith(".png") ? "image/png" : "video/mp4", "content-length": fs.statSync(f).size, "cache-control": "no-store" }); return fs.createReadStream(f).pipe(res); }
    if (req.method === "POST" && (url === "/cmd" || url === "/batch")){ let n = 0; const chunks = [];
      req.on("data", c => { n += c.length; if (n > maxBody){ send(res, 413, { ok: false, err: "body too large" }); req.destroy(); } else chunks.push(c); });
      req.on("end", async () => { if (n > maxBody) return; let body; try { body = JSON.parse(Buffer.concat(chunks).toString("utf8") || "null"); } catch(e){ return send(res, 400, { ok: false, err: "bad json" }); }
        if (url === "/batch" && !Array.isArray(body)) return send(res, 400, { ok: false, err: "batch needs a JSON array" }); send(res, 200, await exec(body)); }); return; }
    send(res, 404, { ok: false, err: "not found" });
  });
}

async function main(argv){
  const o = {}; for (let i = 0; i < argv.length; i++){ const a = argv[i]; if (a === "--headed") o.headed = true; else if (/^--(port|host|out|url|profile)$/.test(a)) o[a.slice(2)] = argv[++i]; }
  const token = process.env.XPIX_AGENT_TOKEN; if (!token || token.length < 16){ console.error("Set XPIX_AGENT_TOKEN (a long random string, at least 16 chars) in the environment. Not started."); return 1; }
  const agent = new XpixAgent({ url: o.url, profile: o.profile, headed: o.headed }); await agent.start();
  const srv = createServer({ agent, token, outDir: o.out }); const host = o.host || "127.0.0.1", port = +o.port || 8765;
  srv.listen(port, host, () => console.log("XPiX Agent server on http://" + host + ":" + port + "  (token required; output folder " + path.resolve(o.out || "xpix_out") + ")"));
  const bye = async () => { try { srv.close(); await agent.stop(); } catch(e){} process.exit(0); }; process.on("SIGINT", bye); process.on("SIGTERM", bye); return null;
}
module.exports = { createServer, tokenOk };
if (require.main === module) main(process.argv.slice(2)).then(c => { if (c) process.exit(c); });
