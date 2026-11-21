// X77 widget (owner 2026-11-21: X77 next to the charts). Reads the scanner's live setups (readyList) for the linked symbol and
// sorts each setup's detectors into X77 schools (CFG.x77, built from modules/x77_detect.py). Labels only: no fetch, no orders.
// Pre-registered pairs (docs/X77_PREREG_PAIRS_2026-11-21.md) are flagged and marked killed on history (2026-11-21); the count of agreeing schools was killed on history.
const X77_PAIRS = [["P1", ["sweep"], ["ote"]], ["P2", ["sweep"], ["rsi_div", "macd_div"]], ["P3", ["level"], ["pa_engulf", "pa_pin"]],
                   ["P4", ["ma_cross", "ema_stack"], ["fib"]]];
const x77Pairs = keys => X77_PAIRS.filter(([, a, b]) => a.some(k => keys.includes(k)) && b.some(k => keys.includes(k))).map(p => p[0]);
Panel.prototype.build_x77 = function(){
  const S = this.state, ar = lang === "ar", L = (e, a) => ar ? a : e, X = (typeof CFG !== "undefined" && CFG.x77) || {};
  const KM = X.keys || {}, SC = X.schools || {}, LB = X.lib || {};
  if (!document.getElementById("x77Css")){ const st = el("style"); st.id = "x77Css"; st.textContent =
    ".x77w{height:100%;overflow:auto;padding:6px;font-size:12px;line-height:1.5}.x77w .tb{display:flex;gap:4px;align-items:center;flex-wrap:wrap}"
    +".x77w .cd{border:1px solid var(--line);border-inline-start:4px solid var(--vc,#888);border-radius:7px;padding:6px 8px;margin:6px 2px;cursor:pointer}"
    +".x77w .ch{display:inline-block;border:1px solid var(--line);border-radius:10px;padding:0 7px;margin:2px 3px 0 0;font-size:11px;cursor:help}"
    +".x77w .pr{display:inline-block;background:#f0b90b;color:#000;border-radius:4px;padding:0 6px;margin-inline-start:4px;font-size:10px;font-weight:700}"
    +".x77w .mut{color:var(--mut,#888);font-size:11px}";
    document.head.appendChild(st); }
  const wrap = el("div", "x77w"); this.body.innerHTML = ""; this.body.appendChild(wrap);
  const tb = el("div", "tb"); this.symSel = this.symSelect(); const allB = el("button"); allB.textContent = L("All symbols", "كل الرموز");
  allB.onclick = () => { S.x77all = !S.x77all; Ws.save(); draw(); }; tb.append(this.symSel, allB); wrap.appendChild(tb);
  const note = el("div", "mut"); note.textContent = L("Live scanner setups sorted by X77 school. A label is not evidence; the count of agreeing schools failed on history (2026-11-21).",
    "سيتابات السكانر الحية متصنفة بمدرسة X77. التصنيف وصف مش دليل؛ عدد المدارس المتفقة اتختبر على التاريخ وفشل (2026-11-21).");
  const box = el("div"); wrap.append(note, box);
  const schoolsOf = keys => [...new Set(keys.map(k => KM[k] || "S_OTHER"))];
  const chip = s => { const v = SC[s] || [s, s, ""]; const n = LB[s] || 0;
    return `<span class="ch" title="${esc((v[2] || "") + (n ? L(" · library examples: ", " · أمثلة في المكتبة: ") + n : ""))}">${esc(ar ? v[0] : v[1])}${n ? " 📚" + n : ""}</span>`; };
  const draw = () => {
    if (!Object.keys(KM).length){ box.innerHTML = `<div class="mut">${L("No X77 map from the server.", "مفيش خريطة X77 من السيرفر.")}</div>`; return; }
    let list = []; try { list = readyList(true); } catch(e){}
    allB.style.fontWeight = S.x77all ? "700" : "400";
    const rows = (S.x77all ? list : list.filter(e => e.symbol === S.sym)).slice(0, 30);
    if (!rows.length){ box.innerHTML = `<div class="mut">${L("No live setup for ", "مفيش سيتاب حي لـ ")}${esc(S.sym || "")}${L(" right now. Try All symbols.", " دلوقتي. جرّب كل الرموز.")}</div>`; return; }
    box.innerHTML = rows.map((e, i) => { const keys = e.keys || [], sch = schoolsOf(keys), prs = x77Pairs(keys), up = e.direction === "bullish";
      return `<div class="cd" data-i="${i}" style="--vc:${up ? "#0ecb81" : "#f6465d"}"><b>${esc(e.symbol)}</b> · ${up ? L("Long", "شراء") : L("Short", "بيع")} · ${esc(e.tf || e.tfk || "")}`
        + prs.map(p => `<span class="pr" title="${esc(L("Pre-registered pair: killed on history 2026-11-21 (net R below 0 after costs)", "زوج متسجل مسبقا: اتلغى على التاريخ 2026-11-21 (صافي R تحت الصفر بعد التكلفة)"))}">${p}</span>`).join("")
        + `<div>${sch.map(chip).join("") || `<span class="mut">${L("no detector keys on this setup", "السيتاب ده من غير مفاتيح كاشفات")}</span>`}</div></div>`; }).join("");
    box.querySelectorAll(".cd").forEach(d => d.onclick = () => { const e = rows[+d.dataset.i]; if (e) Ws.broadcast(this, e.symbol); });
  };
  this.resub = () => { this.setTitle(); draw(); };
  const tm = setInterval(draw, 15000); this.unsubs.push(() => clearInterval(tm)); draw();
};
// Chart indicator "X77" (Indicators menu, Sessions & signals group): the same school labels drawn on the chart.
// One line per live setup on this symbol (top left) + a small "X77" tag at its entry price. Labels only.
CandleChart.prototype.paintX77 = function(c, py, PR){
  const X = (typeof CFG !== "undefined" && CFG.x77) || {}, KM = X.keys || {}, SC = X.schools || {}, LB = X.lib || {}, ar = lang === "ar";
  let rows = []; try { rows = readyList(true).filter(e => e.symbol === this.sym).slice(0, 4); } catch(e){}
  const ov = this.overlay;   // the chart's own scanner setup for this symbol AND timeframe (same one the chart draws)
  if (!rows.length && ov && ov.plan) rows = [{direction: ov.dir, tf: ov.tf, keys: ov.keys || [], plan: ov.plan}];
  c.save(); c.font = "11px sans-serif"; c.textBaseline = "middle"; c.textAlign = "left";
  const y0 = 34 + 4*15, line = (txt, y, col) => { const w = c.measureText(txt).width + 12; c.fillStyle = "rgba(11,14,17,.8)"; c.fillRect(44, y - 8, w, 16);   // x 44: clear of the drawing toolbar on the left
    c.fillStyle = col; c.fillText(txt, 50, y); };
  if (!rows.length) line("X77: " + (CFG.scanning ? (ar ? "السكانر لسه شغال... استنى" : "scanner still running... wait")
    : (ar ? "مفيش سيتاب حي للرمز ده (السكانر ماطلعش إشارة)" : "no live setup on this symbol (scanner found none)")), y0, "#9aa4b2");
  rows.forEach((e, i) => {
    const up = e.direction === "bullish", col = up ? "#0ecb81" : "#f6465d", keys = e.keys || [];
    const ids = [...new Set(keys.map(k => KM[k] || "S_OTHER"))], sch = ids.map(s => (SC[s] || [s, s])[ar ? 0 : 1]);
    const nLib = ids.reduce((a, s) => a + (LB[s] || 0), 0);   // library examples (owner pictures) for these schools
    const prs = x77Pairs(keys);
    line("X77 " + (up ? "▲" : "▼") + " " + (e.tf || e.tfk || "") + ": " + (sch.join(" · ") || "-") + (prs.length ? "  [" + prs.join(",") + (ar ? " اتلغى" : " killed") + "]" : "") + (nLib ? "  📚" + nLib : ""), y0 + i*18, col);
    const ent = e.plan && e.plan.entry, y = ent != null ? py(ent) : null;
    if (y != null && isFinite(y)){ c.fillStyle = col; c.fillRect(PR - 34, y - 7, 30, 14); c.fillStyle = "#000"; c.textAlign = "center"; c.fillText("X77", PR - 19, y); c.textAlign = "left"; }
  });
  c.restore();
};
