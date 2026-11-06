// MOCK-TESTED ONLY. modules/screen_recorder.js (page-wide recorder + editor) with a FAKE getDisplayMedia (animated canvas, 1280x720): start / pause / continue / flag / stop, the clip excludes the pause,
// the recorder survives a "page change" (the host swaps its content), the editor opens, a 2-segment trim + 2x speed exports a shorter clip. Run: node tests/browser/screen_recorder_mock.js (arg ignored)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1400, height: 800 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route('http://localhost/**', r => r.fulfill({ status: 200, contentType: 'text/html', body: '<body style="margin:0;background:#0b0e11"><div id="page">page A</div></body>' })); await p.goto('http://localhost/');   // a secure context (localhost) so mediaDevices exists
  await p.addInitScript(() => {}); await p.evaluate(() => { let n = 0; navigator.mediaDevices.getDisplayMedia = async () => { const cv = document.createElement('canvas'); cv.width = 1280; cv.height = 720; const x = cv.getContext('2d'); setInterval(() => { n++; x.fillStyle = '#' + (n * 37 % 4096).toString(16).padStart(3, '0'); x.fillRect(0, 0, 1280, 720); x.fillStyle = '#fff'; x.font = '60px sans-serif'; x.fillText('frame ' + n, 50 + (n % 40) * 10, 300); }, 33); const s = cv.captureStream(30); const t = s.getVideoTracks()[0]; t.getSettings = () => ({ width: 1280, height: 720, frameRate: 30 }); return s; }; });
  await p.addScriptTag({ path: path.join(__dirname, '../../modules/screen_recorder.js') }); await p.waitForTimeout(300);
  const r = {}; r.ui = await p.evaluate(() => !!document.getElementById('xpix-rec') && /REC/.test(document.getElementById('xpix-rec').textContent));
  r.start = await p.evaluate(() => __xpixRec.start()); await p.waitForTimeout(1800);
  await p.evaluate(() => { document.getElementById('page').textContent = 'page B (radar)'; });   // a page switch: the recorder must keep going
  await p.evaluate(() => __xpixRec.flag('moment A')); r.recAfterSwitch = await p.evaluate(() => __xpixRec.state().recording);
  await p.evaluate(() => __xpixRec.pause()); r.paused = await p.evaluate(() => __xpixRec.state().paused); await p.waitForTimeout(2500); await p.evaluate(() => __xpixRec.resume()); await p.waitForTimeout(1800);
  r.lamp = await p.evaluate(() => !!document.querySelector('#xpix-rec .xpl.rec'));
  await p.evaluate(() => __xpixRec.stop()); await p.waitForTimeout(1200);
  r.st = await p.evaluate(() => { const s = __xpixRec.state(); return { rec: s.recording, n: s.clips.length, dur: s.clips[0] && s.clips[0].dur, size: s.clips[0] && s.clips[0].size, w: s.clips[0] && s.clips[0].w, fmt: s.fmt && s.fmt.bps }; });
  // editor: two segments, 2x
  await p.evaluate(() => __xpixRec.edit()); await p.waitForSelector('#xpix-edit video'); await p.waitForTimeout(1500);
  const click = async txt => p.evaluate(t => { const x = [...document.querySelectorAll('#xpix-edit button')].find(e => e.textContent.includes(t)); x && x.click(); return !!x; }, txt);
  const setT = async t => p.evaluate(async t => { const v = document.querySelector('#xpix-edit video'); v.currentTime = t; await new Promise(r => setTimeout(r, 250)); }, t);
  await setT(0.2); await click('[ In'); await setT(1.2); await click('] Out'); await click('+ Add segment'); await setT(2.0); await click('[ In'); await setT(3.0); await click('] Out'); await click('+ Add segment');
  r.segs = await p.evaluate(() => /segments: 2/.test(document.querySelector('#xpix-edit').textContent));
  await p.evaluate(() => { const s = [...document.querySelectorAll('#xpix-edit select')].find(x => /Speed/.test(x.textContent)); s.value = '2'; });
  await click('Export edited'); await p.waitForFunction(() => /Saved/.test(document.querySelector('#xpix-edit').textContent), null, { timeout: 30000 }).catch(() => {});
  r.exp = await p.evaluate(() => { const s = __xpixRec.state(); const c = s.clips[0]; return { n: s.clips.length, kind: c.kind, dur: c.dur, status: document.querySelector('#xpix-edit').textContent.slice(-120) }; });
  await click('Close'); r.closed = await p.evaluate(() => !document.getElementById('xpix-edit'));
  const ok = r.ui && r.start.ok && r.recAfterSwitch && r.paused && r.lamp && !r.st.rec && r.st.n === 1 && r.st.dur > 2500 && r.st.dur < 5500 && r.st.size > 20000 && r.segs && r.exp.n === 2 && r.exp.kind === 'edit' && r.exp.dur > 400 && r.exp.dur < 2200 && r.closed && !errs.length;
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
