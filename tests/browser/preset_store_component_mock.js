// MOCK-TESTED ONLY. The Radar preset store component (modules/preset_store/index.html) speaks the Streamlit component protocol: a "save" command writes the preset to localStorage and the value sent back contains it; the same command id is not applied twice; "delete" removes it; damaged storage never throws.
// Run: NODE_PATH=$(npm root -g) node tests/browser/preset_store_component_mock.js
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(() => chromium.launch());
  const p = await (await b.newContext()).newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.addInitScript(() => { window.__msgs = []; window.addEventListener('message', e => { if (e.data && e.data.isStreamlitMessage) window.__msgs.push(e.data); }); });
  await p.goto('file://' + path.resolve(__dirname, '../../modules/preset_store/index.html')); await p.waitForTimeout(200);
  const res = await p.evaluate(async () => { const wait = ms => new Promise(r => setTimeout(r, ms)), out = {}; const render = cmd => { window.postMessage({ type: 'streamlit:render', args: { cmd } }, '*'); return wait(80); };
    const vals = () => window.__msgs.filter(m => m.type === 'streamlit:setComponentValue').map(m => m.value); out.ready = window.__msgs.some(m => m.type === 'streamlit:componentReady');
    await render(null); out.firstValue = JSON.stringify(vals().slice(-1)[0]);
    await render({ id: 'a1', action: 'save', name: 'my scalp', data: { cs_rsi: ['rsi_lt30'], cs_side: 'Buy only' } }); out.afterSave = vals().slice(-1)[0]; out.ls = localStorage.getItem('xpix_radar_presets');
    const n = vals().length; await render({ id: 'a1', action: 'save', name: 'my scalp', data: { cs_rsi: ['x'] } }); out.sameIdIgnored = JSON.parse(localStorage.getItem('xpix_radar_presets'))['my scalp'].cs_rsi[0] === 'rsi_lt30'; out.noResendIfUnchanged = vals().length === n;
    await render({ id: 'a2', action: 'delete', name: 'my scalp' }); out.afterDelete = JSON.stringify(vals().slice(-1)[0]);
    localStorage.setItem('xpix_radar_presets', '{not json'); await render({ id: 'a3', action: 'save', name: 'ok', data: { cs_mode: 'Any selected' } }); out.recoveredFromDamage = JSON.stringify(vals().slice(-1)[0]); return out; });
  console.log(JSON.stringify(res), 'errors', errs.length, errs[0] || ''); await b.close();
})();
