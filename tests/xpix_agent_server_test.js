// XPiX Agent HTTP server: auth, allow-list, path safety, size / rate limits, one-at-a-time. Uses a stub agent (no browser). Run: node tests/xpix_agent_server_test.js
const http = require('http'), fs = require('fs'), os = require('os'), path = require('path');
const { createServer } = require('../tools/xpix_agent/server'); const { COMMANDS } = require('../tools/xpix_agent/xpix_agent');
const TOKEN = 'test-token-0123456789abcdef', out = fs.mkdtempSync(path.join(os.tmpdir(), 'xpsrv_')); let running = 0, maxRun = 0; const calls = [];
const agent = { async run(c, a, o){ calls.push([c, a, o]); running++; maxRun = Math.max(maxRun, running); await new Promise(r => setTimeout(r, 30)); running--;
  if (c === 'shot'){ fs.writeFileSync(o.out, 'PNG'); return { ok: true, out: o.out, bytes: 3 }; } if (c === 'boom') throw new Error('x'); return { ok: true, c, a }; } };
const req = (srv, method, url, body, tok = TOKEN) => new Promise(res => { const r = http.request({ port: srv.address().port, host: '127.0.0.1', method, path: url, headers: Object.assign({ 'content-type': 'application/json' }, tok === null ? {} : { authorization: 'Bearer ' + tok }) }, rs => { const ch = []; rs.on('data', d => ch.push(d)); rs.on('end', () => res({ code: rs.statusCode, body: Buffer.concat(ch).toString() })); }); r.on('error', e => res({ code: 0, body: String(e) })); r.end(body == null ? undefined : (typeof body === 'string' ? body : JSON.stringify(body))); });
(async () => {
  const ok = []; const t = (n, v) => { ok.push([n, !!v]); };
  try { createServer({ agent, token: 'short', outDir: out }); t('short token refused', false); } catch(e){ t('short token refused', true); }
  const srv = createServer({ agent, token: TOKEN, outDir: out, rate: 40 }); await new Promise(r => srv.listen(0, '127.0.0.1', r));
  t('no token 401', (await req(srv, 'GET', '/health', null, null)).code === 401); t('wrong token 401', (await req(srv, 'GET', '/health', null, 'nope')).code === 401);
  t('health ok', (await req(srv, 'GET', '/health')).code === 200);
  const r1 = JSON.parse((await req(srv, 'POST', '/cmd', { cmd: 'tf', args: ['15m'] })).body); t('cmd runs', r1.ok && r1.c === 'tf');
  t('unknown cmd refused', JSON.parse((await req(srv, 'POST', '/cmd', { cmd: 'eval', args: ['1'] })).body).ok === false); t('pages runs', JSON.parse((await req(srv, 'POST', '/cmd', { cmd: 'pages' })).body).ok === true);
  t('every allow-listed name is known to the agent list', COMMANDS.includes('shot') && !COMMANDS.includes('eval') && !COMMANDS.some(c => /order|trade|buy|sell|key|eval|exec/i.test(c)));
  const s = JSON.parse((await req(srv, 'POST', '/cmd', { cmd: 'shot', opts: { out: '../../etc/passwd' } })).body); t('shot stays in the output folder', s.ok && s.file.startsWith('/files/') && fs.existsSync(path.join(out, path.basename(s.file))) && !s.out);
  const sn = JSON.parse((await req(srv, 'POST', '/cmd', { cmd: 'shot', opts: { out: 'gold.png' } })).body); t('good file name kept', sn.file === '/files/gold.png');
  const f = await req(srv, 'GET', '/files/gold.png'); t('file served', f.code === 200 && f.body === 'PNG');
  t('traversal refused', (await req(srv, 'GET', '/files/..%2F..%2Fetc%2Fpasswd')).code === 400 && (await req(srv, 'GET', '/files/nothere.png')).code === 404 && (await req(srv, 'GET', '/files/x.txt')).code === 400);
  t('opts.out dropped for non-file commands', (calls.find(c => c[0] === 'tf')[2].out === undefined));
  t('bad json 400', (await req(srv, 'POST', '/cmd', '{nope')).code === 400); t('batch needs array', (await req(srv, 'POST', '/batch', { cmd: 'tf' })).code === 400);
  const b = JSON.parse((await req(srv, 'POST', '/batch', [{ cmd: 'page', args: ['radar'] }, { cmd: 'nope' }, { cmd: 'state' }])).body); t('batch stops at an unknown command', b.length === 2 && b[0].ok && !b[1].ok);
  const r413 = (await req(srv, 'POST', '/cmd', JSON.stringify({ cmd: 'tf', args: ['x'.repeat(70000)] }))).code;  t('body limit 413 (or connection cut)', r413 === 413 || r413 === 0);
  await Promise.all([1, 2, 3, 4].map(i => req(srv, 'POST', '/cmd', { cmd: 'state', args: [i] }))); t('one command at a time', maxRun === 1);
  let got429 = false; for (let i = 0; i < 60 && !got429; i++) got429 = (await req(srv, 'GET', '/health')).code === 429; t('rate limit 429', got429);
  srv.close(); const bad = ok.filter(x => !x[1]); console.log(JSON.stringify(ok.map(x => x[0] + ':' + (x[1] ? 'ok' : 'FAIL')))); console.log(bad.length ? 'FAIL ' + bad.map(x => x[0]).join(', ') : 'PASS'); process.exit(bad.length ? 1 : 0);
})();
