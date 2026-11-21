// Browser check of the TIA page (no JS page errors; widget names present). Run with the app on :8599:
//   python3 -m streamlit run main.py --server.headless true --server.port 8599
//   NODE_PATH=$(npm root -g) node tests/e2e/tia_widgets_check.js /path/to/out.png
// Mock-tested only: the sandbox blocks price sites, so no live data is shown. Network errors are expected here.
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message.slice(0, 160)));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text().slice(0, 160)); });
  await page.goto('http://localhost:8599/', { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForTimeout(4000);
  const tia = page.getByRole('radio', { name: /^TIA$/ }).first();
  let clicked = false;
  try { await tia.click({ timeout: 8000 }); clicked = true; } catch (e) {
    try { await page.getByText('TIA', { exact: true }).first().click({ timeout: 8000 }); clicked = true; } catch (e2) {}
  }
  await page.waitForTimeout(12000);
  const frames = page.frames().length;
  const frameTexts = [];
  for (const f of page.frames()) {
    try { const t = await f.evaluate(() => document.body ? document.body.innerText.slice(0, 4000) : ''); frameTexts.push(t); } catch (e) {}
  }
  const all = frameTexts.join('\n');
  const names = ['Footprint', 'DOM', 'Order flow', 'Time & Sales', 'TIA Pulse', 'TIA Walls'];
  const found = Object.fromEntries(names.map(n => [n, all.toLowerCase().includes(n.toLowerCase())]));
  await page.screenshot({ path: process.argv[2] || 'tia.png', fullPage: false });
  console.log(JSON.stringify({ clicked, frames, found, pageErrors: errors.filter(e => e.startsWith('pageerror')).slice(0,5), otherConsole: errors.filter(e => !e.startsWith('pageerror') && !/ERR_TUNNEL|WebSocket connection|Failed to load resource/.test(e)).slice(0,5), errorCount: errors.length }, null, 1));
  await browser.close();
})().catch(e => { console.error('FAILED', e.message.slice(0, 300)); process.exit(1); });
