// MOCK-TESTED ONLY (mocked OKX, Chromium with touch emulation; getDisplayMedia removed like iPadOS / Android Chrome). Workspace screenshot (PNG) and video from inside the page.
// Run: NODE_PATH=$(npm root -g) node tests/browser/workspace_capture_mock.js /tmp/ws.html [/tmp/shot.png]
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const ctx = await b.newContext({ viewport: { width: 1180, height: 820 }, hasTouch: true, acceptDownloads: true, userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15' });
  await ctx.addInitScript(() => { try { delete navigator.mediaDevices.getDisplayMedia; navigator.mediaDevices.getDisplayMedia = undefined; } catch (e) {} });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (!/okx\.com\/api\/v5/.test(u)) return r.abort(); const now = Math.floor(Date.now() / 3600000) * 3600000, o = []; let c = 100;
    for (let i = 0; i < 300; i++) { c += Math.sin(i / 7) * 2; o.push([String(now - (300 - i) * 3600000), String(c - 0.5), String(c + 1), String(c - 1), String(c), '10', '0', '0', '1']); }
    o.reverse(); return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ code: '0', data: o }) }); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1000); await p.evaluate(() => { Ws.build(Ws.defaults()); Ws.save(); }); await p.waitForTimeout(3000);
  const out = { noGdm: await p.evaluate(() => !(navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia)), buttons: await p.evaluate(() => [...document.querySelectorAll('#bar button')].map(x => x.textContent).filter(t => /📸|🖥|⏹/.test(t)).join('')) };
  // screenshot
  const [dl] = await Promise.all([p.waitForEvent('download', { timeout: 20000 }), p.evaluate(() => [...document.querySelectorAll('#bar button')].find(x => x.textContent === '📸').click())]);
  const shot = process.argv[3] || '/tmp/ws_shot.png'; await dl.saveAs(shot); out.shotName = dl.suggestedFilename(); out.shotBytes = fs.statSync(shot).size;
  const png = fs.readFileSync(shot); out.shotW = png.readUInt32BE(16); out.shotH = png.readUInt32BE(20);
  // video from inside
  await p.evaluate(() => [...document.querySelectorAll('#bar button')].find(x => x.textContent === '🖥').click()); await p.waitForTimeout(3500);
  out.recording = await p.evaluate(() => [...document.querySelectorAll('#bar button')].some(x => x.textContent === '⏹'));
  const [vd] = await Promise.all([p.waitForEvent('download', { timeout: 20000 }), p.evaluate(() => [...document.querySelectorAll('#bar button')].find(x => x.textContent === '⏹').click())]);
  const vid = '/tmp/ws_rec.webm'; await vd.saveAs(vid); out.videoName = vd.suggestedFilename(); out.videoBytes = fs.statSync(vid).size;
  const ok = out.noGdm && /📸/.test(out.buttons) && /🖥|⏹/.test(out.buttons) && out.shotBytes > 20000 && out.shotW >= 1180 && out.recording && out.videoBytes > 5000 && /\.webm$|\.mp4$/.test(out.videoName) && !errs.length;
  console.log(JSON.stringify(out), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
