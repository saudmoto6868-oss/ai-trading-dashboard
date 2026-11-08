// Theme 17 header chip: dot-matrix status next to the bell exists only for deerflow (mock-tested, no network).
const { chromium } = require("playwright");
(async () => {
  const { execSync } = require("child_process");
  const mk = th => execSync(`python3 -c "from modules.header_bar import build_header_html as b;import sys;sys.stdout.write(b('',[],[],theme='${th}',theme_vars={}))"`, { cwd: process.cwd(), env: { ...process.env, PYTHONPATH: "/tmp/stlib" }, maxBuffer: 1 << 26 }).toString();
  const br = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" }); const out = {}; let errors = 0;
  for (const th of ["deerflow", "classic"]) {
    const pg = await br.newPage({ viewport: { width: 1300, height: 70 } }); pg.on("pageerror", () => errors++);
    await pg.route("**/*", r => r.request().url().startsWith("http") ? r.abort() : r.continue());
    await pg.setContent(mk(th)); await pg.waitForTimeout(400);
    out[th] = await pg.evaluate(() => { const d = document.getElementById("dm"); return d ? { dots: d.querySelectorAll(".ic i").length, text: d.querySelector(".tr").textContent.slice(0, 40), nextToBell: d.previousElementSibling && d.previousElementSibling.id } : null; });
    if (th === "deerflow") await pg.screenshot({ path: "/tmp/o/header_deerflow.png" });
  }
  console.log(JSON.stringify(out), "errors", errors); await br.close();
})();
