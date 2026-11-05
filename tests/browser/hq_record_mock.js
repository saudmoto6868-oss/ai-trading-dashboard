// MOCK-TESTED ONLY. Screen / workspace recording asks for the screen's REAL size (up to 8K) at 60 fps and records with the best codec at a bitrate that follows the real track size
// (4K60 -> >= 40 Mbps (VP9 ~50, H.264 ~80 in real Chrome; this test Chromium has no H.264), never the old fixed 6-8 Mbps). getDisplayMedia is faked with a 3840x2160@60 canvas stream; MediaRecorder's constructor options are captured.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.goto('file://' + process.argv[2] + '?blank=1'); await p.waitForTimeout(1200);
  const r = await p.evaluate(async () => {
    const o = {}; window.__gdm = null; window.__mr = null;
    navigator.mediaDevices.getDisplayMedia = async c => { window.__gdm = c; const cv = document.createElement('canvas'); cv.width = 3840; cv.height = 2160; const s = cv.captureStream(60), t = s.getVideoTracks()[0]; t.getSettings = () => ({ width: 3840, height: 2160, frameRate: 60 }); return s; };
    const MR = window.MediaRecorder; window.MediaRecorder = function (stream, opt) { window.__mr = opt; const m = new MR(stream, opt); return m; }; window.MediaRecorder.isTypeSupported = MR.isTypeSupported.bind(MR);
    const btn = [...document.querySelectorAll('#bar button')].find(x => x.textContent === '🖥'); btn.click(); await new Promise(r => setTimeout(r, 600)); o.gdm = window.__gdm && window.__gdm.video; o.mr = window.__mr; if (btn.textContent === '⏹') btn.click();
    const q = Snap.hq({ getVideoTracks: () => [{ getSettings: () => ({ width: 1920, height: 1080, frameRate: 30 }) }] }); o.q1080 = q;
    const q8 = Snap.hq({ getVideoTracks: () => [{ getSettings: () => ({ width: 7680, height: 4320, frameRate: 60 }) }] }); o.q8k = q8.bps;
    return o; });
  const ok = r.gdm && r.gdm.width.ideal >= 3840 && r.gdm.height.ideal >= 2160 && r.gdm.frameRate.ideal === 60 && !(r.gdm.width.max) && r.mr && r.mr.videoBitsPerSecond >= 40e6 && r.mr.videoBitsPerSecond <= 120e6 && r.q1080.bps >= 12e6 && r.q8k === 120e6 && /^(video\/mp4|video\/webm)/.test(r.mr.mimeType || 'video/webm') && !errs.length;
  console.log(JSON.stringify(r), 'errors', errs.length, errs[0] || '', ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
})();
