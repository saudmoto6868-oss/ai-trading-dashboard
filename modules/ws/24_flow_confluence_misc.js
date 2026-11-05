/* ---- Flow confluence v1 (frozen rules) + its forward test. DESCRIPTION, not advice: it counts how many of four readings agree at a footprint level, writes every firing to a log and measures what price did afterwards.
   Rules (do not edit in place; a change makes a new version): 1) price is inside an untouched stacked-imbalance zone of the chart's footprint (gives the side: buy stack = up, sell stack = down);
   2) the current bar's delta has the same sign; 3) the last 60 s of tape is > 55 % in that direction; 4) an absorption by the same side within 3 rows in the last 2 min. Fires at 3 of 4 with rule 1 required; 5 min cool-down per symbol and side. ---- */
Ws.flowConf = sym => {
  const P = Ws.panels.find(p => p.chart && p.chart.sym === sym && p.chart.fpOn); if (!P) return null; const c = P.chart, d = c.data; if (!d.length) return null;
  const px = d[d.length - 1].c, tol = c._fpStep || 0, hit = c.flowLevels(true).filter(l => l.kind === "stack" && px >= l.lo - tol && px <= l.hi + tol);
  if (!hit.length) return {n:0, dir:0, parts:[], px};
  const dir = hit[0].side === "b" ? 1 : -1, parts = ["level"], m = c.fp.get(d[d.length - 1].t); if (m && (m.b - m.s)*dir > 0) parts.push("delta");
  const tp = Hub.last["trades|"+sym]; if (tp && !tp.error){ const now = Date.now(), rows = (tp.all || tp.rows || []).filter(r => now - r.t < 60000); let b = 0, sl = 0; rows.forEach(r => { if (r.side === "Buy") b += r.q; else sl += r.q; });
    if (b + sl > 0 && ((dir > 0 && b/(b + sl) > .55) || (dir < 0 && sl/(b + sl) > .55))) parts.push("tape"); }
  if (P.flt && P.flt.events && P.flt.events.some(e => e.ev === "ABSORB" && Date.now() - e.t < 120000 && ((dir > 0 && e.side === "bid") || (dir < 0 && e.side === "ask")) && Math.abs(e.p - px) <= tol*3)) parts.push("absorb");
  return {n:parts.length, dir, parts, px};
};
const FlowTest = (() => { let log = []; try { log = JSON.parse(localStorage.getItem(LS+"_ft") || "[]"); } catch(e){}
  const save = () => { try { localStorage.setItem(LS+"_ft", JSON.stringify(log.slice(-400))); } catch(e){} }, HZ = [["m5", 300000], ["m30", 1800000], ["h1", 3600000]];
  const lastPx = sym => { const P = Ws.panels.find(p => p.chart && p.chart.sym === sym && p.chart.data.length); return P ? P.chart.data[P.chart.data.length - 1].c : null; };
  const tick = () => { if (document.hidden) return; Ws.panels.forEach(P => { if (!P.chart || !P.chart.fpOn) return; const sym = P.chart.sym, cf = Ws.flowConf(sym); if (!cf || cf.n < 3 || !cf.dir) return;
      if (log.some(e => e.sym === sym && e.dir === cf.dir && (e.ty || "conf") === "conf" && Date.now() - e.t < 300000)) return; log.push({t:Date.now(), sym, dir:cf.dir, px:cf.px, parts:cf.parts.join("+"), v:1, ty:"conf", r:{}}); save(); });
    Ws.panels.forEach(P => { if (!P.chart || !P.chart.fpOn || !P.chart.data.length) return; const c = P.chart, d = c.data, sym = c.sym, A = c.cvdAn(d, c.fp, 12), dv = A.div.find(x => x.i === d.length - 2);   // CVD divergence v1: only on the bar that has just closed; bull = up, bear = down
      if (!dv) return; const dir = dv.side === "bull" ? 1 : -1; if (log.some(e => e.sym === sym && e.ty === "div" && e.bt === d[dv.i].t)) return; log.push({t:Date.now(), sym, dir, px:d[d.length - 1].c, parts:"cvd-div", v:1, ty:"div", bt:d[dv.i].t, r:{}}); save(); }); };
  const evalPending = () => { let ch = false; const now = Date.now(); log.forEach(e => HZ.forEach(([k, ms]) => { if (e.r[k] == null && now - e.t >= ms){ const px = lastPx(e.sym); if (px != null){ e.r[k] = +(((px - e.px)/e.px)*1e4*e.dir).toFixed(2); ch = true; } } })); if (ch) save(); };   // signed move in bps in the direction of the reading
  const stats = (k, ty) => { const a = log.filter(e => (e.ty || "conf") === (ty || "conf") && e.r[k] != null).map(e => e.r[k]), n = a.length; if (!n) return {n:0}; const mean = a.reduce((x, y) => x + y, 0)/n, sd = Math.sqrt(a.reduce((x, y) => x + (y - mean)**2, 0)/Math.max(1, n - 1)), t = n > 1 && sd > 0 ? mean/(sd/Math.sqrt(n)) : 0;
    const h = Math.floor(n/2), m1 = h ? a.slice(0, h).reduce((x, y) => x + y, 0)/h : 0, m2 = n - h ? a.slice(h).reduce((x, y) => x + y, 0)/(n - h) : 0;
    return {n, mean, hit:100*a.filter(v => v > 0).length/n, t, ok:n >= 100 && t > 3 && m1 > 0 && m2 > 0}; };
  setInterval(tick, 5000); setInterval(evalPending, 10000);
  return {log:() => log, stats, HZ, clear(){ log = []; save(); }}; })();
Ws.ftBtn = () => { const b = el("button", null, "📊"); b.title = Lg("Flow confluence: log and forward test","توافق الفلو: السجل والاختبار الأمامي"); b.onclick = e => { e.stopPropagation(); Ws.ftPop(b); }; b.onpointerdown = e => e.stopPropagation(); return b; };
Ws.ftPop = anchor => {
  document.querySelectorAll(".stpop").forEach(x => x.remove()); const pop = el("div", "stpop"), r = anchor.getBoundingClientRect(); pop.style.left = Math.max(4, Math.min(r.left, innerWidth - 380))+"px"; pop.style.top = (r.bottom + 3)+"px"; pop.style.minWidth = "400px"; pop.style.maxHeight = "70vh"; pop.style.overflowY = "auto"; pop.style.display = "block";
  const L = FlowTest.log(), nm = {m5:"5m", m30:"30m", h1:"1h"};
  let h = '<div style="font-weight:700;margin-bottom:4px">'+esc(Lg("Flow confluence v1: forward test","توافق الفلو v1: الاختبار الأمامي"))+'</div><div class="m" style="font-size:10px;line-height:1.5;margin-bottom:6px">'+esc(Lg("Fires when 3 of 4 agree at an untouched stacked-imbalance zone: level, bar delta, tape share, absorption. A reading, not advice. It counts as evidence only with n ≥ 100, t > 3 and both halves positive.","بتسجّل لما 3 من 4 يتفقوا عند منطقة إمبالانس مكدّس لسه ما اتلمستش: المستوى، دلتا الشمعة، حصة الشريط، الامتصاص. قراءة مش نصيحة. بتعتبر دليل بس لما n ≥ 100 وt > 3 والنصين موجبين."))+'</div>';
  h += '<table class="fx"><tr><th>'+esc(Lg("after","بعد"))+'</th><th class="r">n</th><th class="r">'+esc(Lg("avg bps","متوسط نقطة"))+'</th><th class="r">'+esc(Lg("hit %","نجاح %"))+'</th><th class="r">t</th><th>'+esc(Lg("verdict","الحكم"))+'</th></tr>';
  [["conf", Lg("Confluence","التوافق")], ["div", Lg("CVD divergence","تباعد CVD")]].forEach(([ty, tn]) => FlowTest.HZ.forEach(([k]) => { const st = FlowTest.stats(k, ty); h += '<tr><td>'+esc(tn)+' '+nm[k]+'</td><td class="r">'+st.n+'/100</td>'+(st.n ? '<td class="r '+(st.mean >= 0 ? "g" : "rd")+'">'+st.mean.toFixed(1)+'</td><td class="r">'+st.hit.toFixed(0)+'</td><td class="r">'+st.t.toFixed(1)+'</td><td style="font-size:10px">'+esc(st.ok ? Lg("passes the gate","عدّى البوابة") : Lg("not evidence yet","لسه مش دليل"))+'</td>' : '<td class="r m">–</td><td class="r m">–</td><td class="r m">–</td><td class="m" style="font-size:10px">'+esc(Lg("waiting","مستني"))+'</td>')+'</tr>'; }));
  h += '</table><div style="margin-top:6px;font-weight:600">'+esc(Lg("Latest firings","آخر التسجيلات"))+' ('+L.length+')</div>';
  h += L.length ? '<table class="fx">'+L.slice(-8).reverse().map(e => '<tr><td>'+hms(e.t)+'</td><td>'+esc(e.sym)+'</td><td class="'+(e.dir > 0 ? "g" : "rd")+'">'+(e.dir > 0 ? "▲" : "▼")+'</td><td class="r">'+fmtP(e.px)+'</td><td class="m" style="font-size:10px">'+esc(e.parts)+'</td><td class="r m">'+["m5", "m30", "h1"].map(k => e.r[k] == null ? "–" : e.r[k]).join(" / ")+'</td></tr>').join("")+'</table>' : '<div class="m">'+esc(Lg("Nothing yet. Turn the footprint on for a chart and let it run.","لسه مفيش. شغّل الفوت برنت على شارت وسيبه شغال."))+'</div>';
  const clr = el("button", null, Lg("Clear the log","امسح السجل")); clr.style.marginTop = "6px"; clr.onclick = () => { FlowTest.clear(); pop.remove(); }; clr.onpointerdown = e => e.stopPropagation();
  pop.innerHTML = h; pop.append(clr); document.body.append(pop); setTimeout(() => { const off = ev => { if (!pop.contains(ev.target) && ev.target !== anchor){ pop.remove(); document.removeEventListener("pointerdown", off, true); } }; document.addEventListener("pointerdown", off, true); }, 0);
};
Ws.sensPop = anchor => {
  document.querySelectorAll(".stpop").forEach(x => x.remove()); const pop = el("div","stpop"), r = anchor.getBoundingClientRect(); pop.style.left = Math.max(4, Math.min(r.left, innerWidth-300))+"px"; pop.style.top = (r.bottom+3)+"px"; pop.style.gridTemplateColumns = "1fr auto"; pop.style.minWidth = "240px";
  const h = el("div","full"); h.style.cursor = "default"; h.textContent = lang === "ar" ? "إعدادات Time & Sales" : "Time & Sales settings"; pop.append(h);
  Ws.sensRows(pop, (lab, input) => { const l = el("span"); l.textContent = lab; pop.append(l, input); input.onpointerdown = e => e.stopPropagation(); });
  document.body.append(pop); setTimeout(() => { const off = ev => { if (!pop.contains(ev.target) && ev.target !== anchor){ pop.remove(); document.removeEventListener("pointerdown", off, true); } }; document.addEventListener("pointerdown", off, true); }, 0);
};
/* ---- right-click: never the browser's menu inside the Workspace or the page above it; every place gets the menu of the thing under the pointer ---- */
function ctxCopy(txt){ try { if (navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(txt).catch(() => ctxCopyOld(txt)); return; } } catch(e){} ctxCopyOld(txt); }
function ctxCopyOld(txt){ const t = document.createElement("textarea"); t.value = txt; t.style.cssText = "position:fixed;left:-9999px;top:0"; document.body.append(t); t.select(); try { document.execCommand("copy"); } catch(e){} t.remove(); }
function ctxShow(x, y, items){   // items: [label, fn, danger?] or null (separator)
  document.querySelectorAll(".ctxm").forEach(m => m.remove());
  const m = el("div", "ctxm"); m.style.cssText = "position:fixed;z-index:2147483001;left:"+x+"px;top:"+y+"px;max-height:80vh;overflow-y:auto";
  items.forEach(it => { if (!it){ const sp = el("div"); sp.style.cssText = "height:1px;background:var(--line,#2b3139);margin:3px 0"; m.append(sp); return; }
    const b = el("button", null, esc(it[0])); if (it[2]) b.style.color = "#f6465d"; b.onclick = () => { m.remove(); try { it[1](); } catch(e){ console.error(e); } }; m.append(b); });
  document.body.append(m); const r = m.getBoundingClientRect();
  if (r.right > innerWidth) m.style.left = Math.max(4, innerWidth - r.width - 4)+"px"; if (r.bottom > innerHeight) m.style.top = Math.max(4, innerHeight - r.height - 4)+"px";
  const off = ev => { if (ev.target && m.contains(ev.target)) return; m.remove(); document.removeEventListener("pointerdown", off, true); }; setTimeout(() => document.addEventListener("pointerdown", off, true), 0);
}
function ctxPrice(tr, P){   // the price a table row is about: the first cell whose number is close to the symbol's last price (else the first number)
  if (!tr) return null; const ref = (() => { const c = Ws.panels.find(q => q.chart && q.chart.sym === P.state.sym); return c && c.chart.data.length ? c.chart.data[c.chart.data.length - 1].c : null; })(); let first = null;
  for (const td of tr.querySelectorAll("td")){ const v = parseFloat(String(td.textContent).replace(/[$,★\s]/g, "")); if (!isFinite(v) || v <= 0) continue; if (first == null) first = v; if (ref && Math.abs(v - ref)/ref < 0.3) return v; }
  return ref ? null : first; }
function ctxHline(sym, price){
  const c = Ws.panels.find(q => q.chart && q.chart.sym === sym); if (!c){ alert0(Lg("Open a chart of this symbol first","افتح شارت للرمز ده الأول")); return; }
  const ch = c.chart, d = {id:Date.now()+Math.random(), type:"hline", pts:[{t:ch.data.length ? ch.data[ch.data.length - 1].t : Date.now(), p:price}]}; ch.draws.push(d); ch.sel = d; ch.saveDraws(); ch.draw(); }
function alert0(msg){ const t = el("div"); t.textContent = msg; t.style.cssText = "position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#1e2329;color:#eaecef;border:1px solid #2b3139;border-radius:6px;padding:8px 14px;font-size:12px;z-index:2147483002"; document.body.append(t); setTimeout(() => t.remove(), 2600); }
document.addEventListener("contextmenu", e => {
  if (e.target.closest && e.target.closest(".ctxm")){ e.preventDefault(); return; }
  const cv = e.target.closest && e.target.closest("canvas"); if (cv && cv.closest(".chartwrap")){ e.preventDefault(); return; }   // the chart builds its own menu right after this
  e.preventDefault(); const panelEl = e.target.closest && e.target.closest(".panel"), P = panelEl ? Ws.panels.find(p => p.root === panelEl) : null, items = [];
  const sel = String(window.getSelection ? window.getSelection() : "").trim(), tr = e.target.closest && e.target.closest("tr"), link = e.target.closest && e.target.closest("a[href]"), inp = e.target.closest && e.target.closest("input[type=text],input[type=number],textarea");
  if (inp){ items.push([Lg("Cut","قص"), () => { inp.focus(); document.execCommand("cut"); }], [Lg("Copy","نسخ"), () => { inp.focus(); document.execCommand("copy"); }], [Lg("Paste","لصق"), () => { inp.focus(); try { navigator.clipboard.readText().then(t => document.execCommand("insertText", false, t)).catch(() => alert0(Lg("Press Ctrl+V","اضغط Ctrl+V"))); } catch(x){ alert0(Lg("Press Ctrl+V","اضغط Ctrl+V")); } }], [Lg("Select all","تحديد الكل"), () => { inp.focus(); inp.select(); }]); }
  else if (sel) items.push([Lg("Copy","نسخ"), () => ctxCopy(sel)]);
  if (link){ items.length && items.push(null); items.push([Lg("Open link in a new tab","افتح الرابط في تاب جديد"), () => window.open(link.href, "_blank", "noopener")], [Lg("Copy link address","انسخ عنوان الرابط"), () => ctxCopy(link.href)]); }
  if (P && !inp){
    const pr = P.state.sym ? ctxPrice(tr && tr.closest("table") ? tr : null, P) : null;
    if (pr != null){ items.length && items.push(null); items.push([Lg("Copy price ","نسخ السعر ")+fmtP(pr), () => ctxCopy(String(pr))], [Lg("Horizontal line on the chart at ","خط أفقي على الشارت عند ")+fmtP(pr), () => ctxHline(P.state.sym, pr)]); }
    const sRow = tr && tr.dataset && tr.dataset.s;   // watch list row: a symbol
    if (sRow){ items.length && items.push(null); items.push([Lg("Show on the chart: ","اعرضه على الشارت: ")+sRow.replace(/^(HL|Y):(xyz:)?/, ""), () => Ws.broadcast(P, sRow)], [Lg("Copy symbol","نسخ الرمز"), () => ctxCopy(sRow)]); }
    items.length && items.push(null);
    items.push([P.max ? Lg("Restore size","رجّع الحجم") : Lg("Maximise","تكبير"), () => P.toggleMax()], [P.min ? Lg("Expand","فتح") : Lg("Minimise","تصغير"), () => { P.min = !P.min; P.state.min = P.min; P.root.classList.toggle("min", P.min); Ws.save(); }],
      [P.locked ? Lg("Unlock","فك القفل") : Lg("Lock in place","تثبيت في مكانه"), () => { P.locked = !P.locked; P.state.lock2 = P.locked || undefined; P.applyLock(); Ws.save(); }], [Lg("Bring to front","للأمام"), () => P.front()],
      [Lg("Reset colours","رجّع الألوان"), () => { delete P.state.col; delete P.state.bg; P.paint(); Ws.save(); }], null, [Lg("Close widget","إغلاق الويدجت"), () => { if (!P.locked) P.close(); }, true]);
  } else if (!P && !inp){
    items.length && items.push(null);
    ["chart","setup","signals","dom","tape","limits","ofm","watch","scanner","news","notes"].forEach(k => items.push(["+ "+T(k), () => Ws.add(k)]));
    items.push(null, [Lg("Reload the Workspace","أعد تحميل الورك سبيس"), () => location.reload()]);
  }
  if (!items.length) items.push([Lg("Reload the Workspace","أعد تحميل الورك سبيس"), () => location.reload()]);
  ctxShow(e.clientX, e.clientY, items);
}, true);
Ws.flowLevels = sym => { const c = Ws.panels.find(p => p.chart && p.chart.sym === sym && p.chart.fpOn); return c ? c.chart.flowLevels() : []; };
function flowTag(sym, p, tol){   // a small badge when this price sits on a footprint level of the chart (nPOC = naked POC, SI = stacked imbalance, with its side)
  if (!sym) return ""; const L = Ws.flowLevels(sym); if (!L.length) return ""; const hit = L.filter(l => p >= l.lo - tol && p <= l.hi + tol); if (!hit.length) return "";
  return hit.slice(0, 2).map(l => l.kind === "npoc" ? '<b class="fl np" title="'+esc(Lg("Naked POC of an earlier footprint bar: price has not traded back through it","POC أعزل لشمعة سابقة: السعر ما رجعش عدّى عليه"))+'">nPOC</b>'
    : '<b class="fl '+(l.side === "b" ? "sb" : "ss")+'" title="'+esc(Lg("Stacked imbalance zone of an earlier footprint bar: price has not traded back into it","منطقة إمبالانس مكدّس لشمعة سابقة: السعر ما رجعلهاش"))+'">SI'+(l.side === "b" ? "▲" : "▼")+'</b>').join(""); }
/* Depth-of-Trade settings (colours + sizes), ATAS-style */
Ws.ofPanel = (anchor, chart, onChange) => {
  document.querySelectorAll(".stpop").forEach(x => x.remove()); const OF = chart.st.of, ar = lang === "ar", L = (e, a) => ar ? a : e;
  const pop = el("div","stpop"), r = anchor.getBoundingClientRect(); pop.style.left = Math.max(4, Math.min(r.left, innerWidth-300))+"px"; pop.style.top = (r.bottom+3)+"px"; pop.style.gridTemplateColumns = "1fr auto"; pop.style.minWidth = "260px";
  const row = (lab, input) => { const l = el("span"); l.textContent = lab; pop.append(l, input); input.onpointerdown = e => e.stopPropagation(); };
  const col = (k, lab) => { const i = el("input"); i.type = "color"; i.value = OF[k]; i.oninput = () => { OF[k] = i.value; onChange(); }; row(lab, i); };
  const num = (k, lab, mn, mx, stp) => { const i = el("input"); i.type = "number"; i.min = mn; i.max = mx; i.step = stp; i.value = OF[k]; i.style.width = "60px"; i.onchange = () => { OF[k] = Math.max(mn, Math.min(mx, +i.value || OF[k])); i.value = OF[k]; onChange(); }; row(lab, i); };
  const h = el("div","full"); h.style.cursor = "default"; h.textContent = L("Depth of Trade settings","إعدادات عمق التداول"); pop.append(h);
  col("color", L("Buy colour (bubbles, DOM, cells, delta, POC)","لون الشراء (فقاعات، DOM، خلايا، دلتا، POC)")); col("color2", L("Sell colour","لون البيع"));
  const m = el("select"); [[1, L("Sweep/absorb follow buy/sell colour","السويب/الامتصاص بلون الشراء/البيع")],[0, L("Custom marker colours","ألوان مخصصة")]].forEach(([v,l]) => m.append(Object.assign(el("option"), {value:v, textContent:l}))); m.value = OF.sidec ? 1 : 0; m.onchange = () => { OF.sidec = +m.value; onChange(); }; row(L("Marker colours","ألوان العلامات"), m);
  col("sweepC", L("Sweep marker (custom)","علامة السويب (مخصص)")); col("absC", L("Absorption marker (custom)","علامة الامتصاص (مخصص)"));
  { const fpc = (k, base, lab) => { const i = el("input"); i.type = "color"; i.value = OF[k] || OF[base]; i.oninput = () => { OF[k] = i.value; onChange(); }; row(lab, i); };
    fpc("fpBuy", "color", L("Footprint buy colour","لون شراء الفوتبرنت")); fpc("fpSell", "color2", L("Footprint sell colour","لون بيع الفوتبرنت"));
    const fpr = el("button"); fpr.textContent = L("Use buy / sell colours","استخدم ألوان الشراء / البيع"); fpr.onclick = () => { OF.fpBuy = ""; OF.fpSell = ""; onChange(); pop.remove(); }; row(L("Footprint colours","ألوان الفوتبرنت"), fpr); }
  num("min", L("Bubbles: min size (0 all · 1 smart · 2 whale)","الفقاعات: أقل حجم (0 الكل · 1 ذكي · 2 حوت)"), 0, 2, 1); num("bsz", L("Bubble size ×","حجم الفقاعة ×"), 0.3, 3, 0.1); num("bop", L("Bubble opacity ×","شفافية الفقاعة ×"), 0.2, 2.5, 0.1);
  { const hs = el("select"); [["book", L("Bookmap thermal (blue → yellow → red)","بوك ماب حراري (أزرق ← أصفر ← أحمر)")], ["magma", L("Magma (purple → orange)","ماجما (بنفسجي ← برتقالي)")], ["ice", L("Ice (blue → cyan → white)","جليدي (أزرق ← سماوي ← أبيض)")], ["emerald", L("Emerald (green → lime)","زمردي (أخضر ← ليموني)")], ["side", L("Bid / ask colours (buy & sell colour)","ألوان الطلب والعرض (لون الشراء والبيع)")], ["amber", L("Amber (old)","كهرماني (القديم)")], ["custom", L("Custom: two colours","مخصص: لونين")]].forEach(([v, l]) => hs.append(Object.assign(el("option"), {value:v, textContent:l}))); hs.value = OF.hm || "book"; hs.onchange = () => { OF.hm = hs.value; onChange(); }; row(L("Heat-map colours","ألوان الهيت ماب"), hs); for (const [k, lab, dv] of [["hmLo", L("Heat-map low colour","لون الهيت ماب المنخفض"), "#010308"], ["hmHi", L("Heat-map high colour","لون الهيت ماب العالي"), "#fff5fa"]]){ const i = el("input"); i.type = "color"; i.value = OF[k] || dv; i.oninput = () => { OF[k] = i.value; OF.hm = "custom"; hs.value = "custom"; onChange(); }; row(lab, i); } const br = el("input"); br.type = "range"; br.min = "0.25"; br.max = "1.75"; br.step = "0.05"; br.value = String(OF.hmBright || 1); br.oninput = () => { OF.hmBright = +br.value; onChange(); }; row(L("Heat-map brightness","سطوع الهيت ماب"), br); }
  { const hx = el("select"); [["fix", L("Fixed saved history (up to 7 days when zoomed out)","تاريخ ثابت محفوظ (لحد 7 أيام لما تبعد)")], ["live", L("Live scrolling (old, max 20 min)","لايف بيتحرك (القديم، أقصى 20 دقيقة)")]].forEach(([v, l]) => hx.append(Object.assign(el("option"), {value:v, textContent:l}))); hx.value = OF.hmm || "fix"; hx.onchange = () => { OF.hmm = hx.value; onChange(); }; row(L("Heat-map mode","نمط الهيت ماب"), hx); }
  { const hd = el("select"); [["auto", L("Auto by timeframe","تلقائي حسب الفريم")], ["compact", L("Price detail: compact (wide view)","تفاصيل السعر: مختصرة (نطاق أوسع)")], ["balanced", L("Price detail: balanced","تفاصيل السعر: متوازنة")], ["precise", L("Price detail: precise (more rows)","تفاصيل السعر: دقيقة (صفوف أكثر)")]].forEach(([v,l]) => hd.append(Object.assign(el("option"), {value:v, textContent:l}))); hd.value = OF.hmDetail || "auto"; hd.onchange = () => { OF.hmDetail = hd.value; onChange(); }; row(L("Adaptive price detail","تفاصيل السعر التكيفية"), hd); }
  { const ws_ = el("select"); [[0,"Auto"],[120000,"2 min"],[600000,"10 min"],[3600000,"1 h"],[21600000,"6 h"],[86400000,"1 day"],[259200000,"3 days"],[604800000,"7 days"]].forEach(([v, l]) => ws_.append(Object.assign(el("option"), {value:v, textContent:l}))); ws_.value = String(ch().flowSpan || 0); ws_.onchange = () => { ch().flowSpan = +ws_.value || 0; onChange(); }; row(L("Column time window","الفترة الزمنية للعمود"), ws_); }
  { const vp = el("select"); [["auto", L("Auto (on from 1H up)","تلقائي (شغال من 1H وأعلى)")], ["on", L("On","شغال")], ["off", L("Off","مقفول")]].forEach(([v, l]) => vp.append(Object.assign(el("option"), {value:v, textContent:l}))); vp.value = OF.vpf === true ? "on" : OF.vpf === false ? "off" : "auto"; vp.onchange = () => { if (vp.value === "auto") delete OF.vpf; else OF.vpf = vp.value === "on"; onChange(); }; row(L("Estimated candle-volume profile (approx.; not order-book depth)","توزيع تقديري لحجم الشموع (تقريبي؛ مش عمق دفتر الأوامر)"), vp); }
  { const chk = (k, lab) => { const i = el("input"); i.type = "checkbox"; i.checked = OF[k] !== 0; i.onchange = () => { OF[k] = i.checked ? 1 : 0; onChange(); }; row(lab, i); };
    num("fpImb", L("Footprint imbalance ratio (× vs the diagonal row)","نسبة الإمبالانس في الفوتبرنت (× مقابل الصف القُطري)"), 1.5, 10, 0.5); num("fpStk", L("Stacked imbalance: min rows","الإمبالانس المكدّس: أقل عدد صفوف"), 2, 8, 1);
    const mv = el("select"); [0, 10, 25, 50, 100].forEach(v => mv.append(Object.assign(el("option"), {value:v, textContent:v ? v + "%" : L("off","مقفول")}))); mv.value = String(OF.fpMin || 0); mv.onchange = () => { OF.fpMin = +mv.value; onChange(); }; row(L("Imbalance: min row volume (% of the bar's average row)","الإمبالانس: أقل حجم للصف (% من متوسط صف الشمعة)"), mv);
    { const fm_ = el("select"); [["bidask", L("Sell × Buy per row","بيع × شراء لكل صف")], ["delta", L("Delta per row (heat)","دلتا كل صف (حراري)")], ["volume", L("Total volume per row (heat)","إجمالي حجم الصف (حراري)")]].forEach(([v, l]) => fm_.append(Object.assign(el("option"), {value:v, textContent:l}))); fm_.value = OF.fpMode || "bidask"; fm_.onchange = () => { OF.fpMode = fm_.value; onChange(); }; row(L("Footprint cells show","خلايا الفوتبرنت تعرض"), fm_);
      const fr_ = el("select"); [[1, L("Auto","تلقائي")], [2, "×2"], [5, "×5"], [10, "×10"]].forEach(([v, l]) => fr_.append(Object.assign(el("option"), {value:v, textContent:l}))); fr_.value = String(OF.fpRow || 1); fr_.onchange = () => { OF.fpRow = +fr_.value; onChange(); }; row(L("Footprint row size (prices grouped)","حجم صف الفوتبرنت (تجميع الأسعار)"), fr_); }
    chk("fpDiag", L("Diagonal imbalance (off = same row)","إمبالانس قُطري (مقفول = نفس الصف)")); chk("fpStack", L("Stacked imbalance zones","مناطق الإمبالانس المكدّس")); chk("fpNaked", L("Naked POC (runs on until traded)","POC الأعزل (يمتد لحد ما يتلمس)")); chk("fpAuc", L("Unfinished auction marks","علامات المزاد غير المنتهي")); chk("fpDelta", L("Bar delta label","رقم دلتا الشمعة")); chk("fpCvd", L("CVD strip + divergence marks","شريط CVD وعلامات التباعد")); chk("fpVA", L("Value area (70 %) bracket per bar","نطاق القيمة (70%) لكل شمعة")); }
  num("dom", L("Depth-map heat ×","حرارة خريطة العمق ×"), 0.3, 3, 0.1); num("bigx", L("Big-order dot: × avg row","نقطة الأوردر الكبير: × متوسط الصف"), 1.5, 10, 0.5);
  Ws.sensRows(pop, row);
  document.body.append(pop); setTimeout(() => { const off = ev => { if (!pop.contains(ev.target) && ev.target !== anchor){ pop.remove(); document.removeEventListener("pointerdown", off, true); } }; document.addEventListener("pointerdown", off, true); }, 0);
};
/* Arabic plain-language trade analysis (same text as the Crypto-tab scanner's "التحليل") */
Ws.anaPop = (anchor, e) => {
  document.querySelectorAll(".stpop").forEach(x => x.remove()); const ar = lang === "ar"; let a = e.ana; if (!a && (e.tags || []).length) a = {sig:e.tags.map(t => "["+t[0]+"] "+(t[3] || "")), against:"", htf:[], scen:[]};   // old stored alert: rebuild from its tag explanations
  const long_ = e.direction === "bullish";
  const pop = el("div","stpop"), r = anchor.getBoundingClientRect(); pop.style.left = Math.max(4, Math.min(r.left, innerWidth-460))+"px"; pop.style.top = Math.min(r.bottom+3, innerHeight-320)+"px"; pop.style.display = "block"; pop.style.width = "450px"; pop.style.maxHeight = "70vh"; pop.style.overflow = "auto";
  const sec = (t, lines) => lines && lines.length ? '<div style="margin-top:6px"><b style="color:#f0b90b">'+esc(t)+'</b>'+lines.map(x => '<div style="margin:2px 0;padding-inline-start:8px">'+esc(x)+'</div>').join("")+'</div>' : "";
  let h = '<div dir="rtl" style="text-align:right;font-size:12px;line-height:1.6;white-space:normal"><b>'+esc(e.symbol)+'</b> · '+esc(long_ ? "شراء" : "بيع")+' · '+e.score+'/'+e.max+' · '+esc(e.trade || e.ttype || "")+' · '+esc(e.tf || e.tfk || "");
  const ti = tfTxt(e); if (ti) h += ' · <span style="color:#0ecb81">'+esc(ti)+'</span>';
  h += '</div>';
  if (!a){ h += '<div class="m" style="padding:8px">'+esc(ar ? "التحليل غير متاح لهذه الصفقة (قديمة) — هيظهر في المسح الجاي." : "No analysis stored for this older trade — it appears after the next scan.")+'</div>'; }
  else { const pl = e.plan; h += '<div dir="rtl" style="text-align:right;font-size:12px;line-height:1.6;white-space:normal">'
    + (e.vol && e.vol.weight ? '<div style="margin-top:6px"><b style="color:#f0b90b">حجم المركز المقترح</b> — '+Math.round(e.vol.weight*100)+'% من رأس المال المخصص للصفقة (تذبذب سنوي حالي '+Math.round(e.vol.ann_vol*100)+'%، الهدف '+Math.round(e.vol.target*100)+'%) — كل ما زاد التذبذب قلّ الحجم</div>' : "")
    + (pl ? '<div style="margin-top:6px"><b style="color:#f0b90b">الخطة</b> — دخول '+fmtP(pl.entry)+' · وقف '+fmtP(pl.stop)+' · '+pl.tps.map((v,i) => 'هدف '+(i+1)+' '+fmtP(v)).join(' · ')+'</div>' : "")
    + sec("لماذا الإشارة", a.sig) + (a.against ? '<div style="margin-top:6px;color:#f6465d">'+esc(a.against)+'</div>' : "") + sec("الفريمات الأعلى", a.htf) + sec("إطار الأسبوعي / اليومي / 4س", a.mtf) + sec("السياق (تحيز اليوم / النطاق / التوقيت)", a.ctx) + sec("السيناريوهات", a.scen) + '</div>'; }
  pop.innerHTML = h; { const vb = Voice.button(() => pop.innerText); vb.style.cssText = "position:sticky;top:0;float:left;font-size:13px;padding:1px 6px"; pop.prepend(vb); } document.body.append(pop);
  setTimeout(() => { const off = ev => { if (!pop.contains(ev.target)){ pop.remove(); document.removeEventListener("pointerdown", off, true); } }; document.addEventListener("pointerdown", off, true); }, 0);
};
/* strategy picker popup (shared by the Ready-trades header) */
Ws.stratPop = (anchor, onChange) => {
  document.querySelectorAll(".stpop").forEach(x => x.remove());
  const pop = el("div","stpop"), r = anchor.getBoundingClientRect(); pop.style.left = Math.max(4, Math.min(r.left, innerWidth-330))+"px"; pop.style.top = (r.bottom+3)+"px";
  const all = el("div","full"); all.textContent = lang === "ar" ? "الكل (بدون فلتر)" : "All (no filter)"; all.onclick = () => { FILT.st = []; pop.querySelectorAll("input").forEach(i => i.checked = false); onChange(); }; pop.append(all);
  STRATS.forEach(([id, en]) => { const lb = el("label"), cb = el("input"); cb.type = "checkbox"; cb.checked = FILT.st.includes(id);
    cb.onchange = () => { FILT.st = cb.checked ? FILT.st.concat([id]) : FILT.st.filter(x => x !== id); onChange(); }; lb.append(cb, document.createTextNode(lang === "ar" ? id : en)); pop.append(lb); });
  document.body.append(pop); setTimeout(() => { const off = ev => { if (!pop.contains(ev.target) && ev.target !== anchor){ pop.remove(); document.removeEventListener("pointerdown", off, true); } }; document.addEventListener("pointerdown", off, true); }, 0);
};
/* quick-jump strip: live setup chips from the scanner; click = load symbol + setup on the chart */
// the top bar (another frame of the same page) shows the belt in the empty band under it when it can; this frame keeps its own strip as the fallback
const ribHost = () => { try { for (const f of window.parent.document.querySelectorAll("iframe")){ const w = f.contentWindow; if (w && w !== window && typeof w.__xpixRibbon === "function" && f.getBoundingClientRect().height > 0) return w; } } catch(_){} return null; };
const ribItem = (e, i) => { const long_ = e.direction === "bullish", pct = Math.round(100*e.score/Math.max(1,e.max)), pl = e.plan || {}, risk = Math.abs((pl.entry||0) - (pl.stop||0)),
    rr = risk > 0 && pl.tps && pl.tps.length ? Math.abs(pl.tps[0] - pl.entry)/risk : null, fresh = e._t && Date.now() - e._t < 15*60000;
  return {i, sym:e.symbol.replace(/-(USDT|USDC|SWAP)$/,""), dir:long_ ? 1 : -1, tags:(e.tags||[]).slice(0,2).map(t => tagTxt(t[0])).join(" · "), meta:ttTxt(e.ttype)+" · "+(e.tfk||""), pct, hot:pct >= 70,
    rr:rr ? Math.round(rr*10)/10 : null, fresh, tip:(e.tags||[]).map(t => tagTip(t) || t[0]).join("\n")+(pl.entry ? "\n"+Lg("entry ","دخول ")+fmtP(pl.entry)+" · "+Lg("stop ","ستوب ")+fmtP(pl.stop)+" · "+Lg("target ","هدف ")+fmtP(pl.tps[0]) : "")}; };
Ws.drawStrip = () => {
  const box = document.getElementById("strip"); if (!box) return; const rows = readyList().slice(0, 40), TFC = TFC_ALL;
  const sig = lang+"|"+rows.map(e => e.symbol+e.direction+e.tfk+e.score+(e.tags||[]).length).join(",")+"|"+(CFG.scanning ? 1 : 0);
  const host = MOB ? null : ribHost();
  if (host){   // show it in the top bar: summary + chips (click = this frame shows the setup on the chart)
    document.body.classList.add("rib-out"); if (host.__xpixRibbonSig === sig) return;
    const items = rows.map(ribItem), up = items.filter(x => x.dir > 0).length;
    host.__xpixRibbon({sig, ar:lang === "ar", label:(lang === "ar" ? "إشارات حية" : "Live setups"), n:items.length, up, dn:items.length - up, empty:rows.length ? "" : (CFG.scanning ? T("scanning") : T("rdEmpty")), items},
      i => { const e = rows[i]; if (e) Ws.showOnChart(Object.assign({tfc: TFC[e.tfk] || "1H"}, e)); });
    return; }
  document.body.classList.remove("rib-out");
  if (box._sig === sig) return; box._sig = sig;   // unchanged list: leave the strip alone (no flicker, no scroll reset)
  const keep = box.scrollLeft; box.innerHTML = ""; const lb = el("span","lbl"); lb.textContent = lang === "ar" ? "إشارات حية" : "Live setups"; box.append(lb);
  if (!rows.length){ const m = el("span","m"); m.textContent = CFG.scanning ? T("scanning") : T("rdEmpty"); box.append(m); box._loop = 0; return; }
  const mk = e => { const long_ = e.direction === "bullish", pct = Math.round(100*e.score/Math.max(1,e.max)), c = el("span","chip");
    c.style.borderColor = long_ ? "#0ecb81" : "#f6465d"; if (pct >= 70){ c.classList.add("hot"); c.style.setProperty("--hc", long_ ? "#0ecb81" : "#f6465d"); } c.title = (e.tags||[]).map(t => tagTip(t) || t[0]).join("\n");
    c.innerHTML = "<b>"+esc(e.symbol.replace(/-(USDT|USDC|SWAP)$/,""))+"</b> <span style='color:"+(long_?"#0ecb81":"#f6465d")+"'>"+(long_ ? "▲" : "▼")+"</span> "+esc((e.tags||[]).slice(0,2).map(t => tagTxt(t[0])).join(" · "))+" <span class='m'>"+esc(ttTxt(e.ttype))+" · "+esc(e.tfk||"")+" "+pct+"%</span>";
    c.onclick = () => { if (box._moved) return; Ws.showOnChart(Object.assign({tfc: TFC[e.tfk] || "1H"}, e)); }; return c; };
  const first = rows.map(mk); first.forEach(c => box.append(c));
  // wide enough to scroll -> a second copy follows the first so the belt loops with no jump
  const lblW = lb.offsetWidth + 5; let w1 = 0; first.forEach(c => w1 += c.offsetWidth + 5);
  box._loop = w1 > box.clientWidth - lblW ? w1 : 0;
  if (box._loop){ const sp = el("span"); sp.style.cssText = "flex:none;width:12px"; box.append(sp); box._loop = w1 + 12 + 5; rows.map(mk).forEach(c => box.append(c)); }
  box.scrollLeft = box._loop ? keep % box._loop : 0;
};
(() => {   // the belt: slow auto-scroll, stops under the mouse or while dragging, drag with the mouse / finger to move it, no scrollbar
  const box = document.getElementById("strip"); if (!box) return; let hover = false, down = false, sx = 0, sl = 0, last = 0, acc = 0;
  const reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  box.addEventListener("pointerenter", () => hover = true); box.addEventListener("pointerleave", () => { hover = false; });
  box.addEventListener("pointerdown", e => { down = true; sx = e.clientX; sl = box.scrollLeft; box._moved = false; box.classList.add("drag"); });
  addEventListener("pointermove", e => { if (!down) return; const dx = e.clientX - sx; if (Math.abs(dx) > 4) box._moved = true; if (box._moved){ let v = sl - dx; if (box._loop){ v = ((v % box._loop) + box._loop) % box._loop; } box.scrollLeft = v; } });
  const up = () => { if (!down) return; down = false; box.classList.remove("drag"); setTimeout(() => { box._moved = false; }, 0); };
  addEventListener("pointerup", up); addEventListener("pointercancel", up);
  const tick = t => { const dt = Math.min(100, t - (last || t)); last = t;
    if (box._loop && !hover && !down && !reduce && !document.hidden){ acc += 28*dt/1000; if (acc >= 1){ const d = Math.floor(acc); acc -= d; box.scrollLeft += d; if (box.scrollLeft >= box._loop) box.scrollLeft -= box._loop; } }
    requestAnimationFrame(tick); };
  requestAnimationFrame(tick);
})();
Alerts.subs.add(() => Ws.drawStrip()); setInterval(() => Ws.drawStrip(), 5000); setTimeout(() => Ws.drawStrip(), 300);
Ws.showOnChart = c => {
  Setup.sel = c; Setup.subs.forEach(f => f());
  const ch = Ws.panels.find(p => p.type === "chart"); if (!ch) return;
  if (ch.state.sym !== c.symbol) Ws.broadcast(ch, c.symbol);
  ch.setOverlay({tf:c.tfc, dir:c.direction, tags:c.tags, zones:c.zones, plan:c.plan, ew:c.ew}); ch.front();
};
/* ---- video helpers ---- */
function embedUrl(u){
  let m;
  if ((m = u.match(/(?:youtube\.com\/(?:watch\?(?:.*&)?v=|shorts\/|embed\/|live\/)|youtu\.be\/)([\w-]{11})/i))) return "https://www.youtube-nocookie.com/embed/"+m[1];
  if ((m = u.match(/youtube\.com\/playlist\?(?:.*&)?list=([\w-]+)/i))) return "https://www.youtube-nocookie.com/embed/videoseries?list="+m[1];
  if ((m = u.match(/tiktok\.com\/.*\/video\/(\d+)/i))) return "https://www.tiktok.com/embed/v2/"+m[1];
  return "";
}
function insights(text){
  if (!text.trim()) return '<div class="m">'+esc(T("none"))+'</div>';
  const low = text.toLowerCase(), names = {BTC:["btc","bitcoin","بيتكوين","البيتكوين"],ETH:["eth","ethereum","إيثريوم","ايثريوم"],SOL:["sol","solana","سولانا"],XRP:["xrp","ripple","ريبل"],BNB:["bnb","binance coin"],DOGE:["doge","dogecoin","دوج"]};
  SYMS.forEach(s => { const b = s.split("-")[0]; if (!names[b]) names[b] = [b.toLowerCase()]; });
  const coins = Object.keys(names).filter(k => names[k].some(w => new RegExp("(^|[^a-z\\u0600-\\u06FF])"+w.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+"($|[^a-z\\u0600-\\u06FF])","i").test(low)));
  const lv = [...new Set((text.match(/\$?\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\$?\b\d{2,6}(?:\.\d+)?\s?[kK]\b|\$\d+(?:\.\d+)?/g) || []).map(s => s.trim()))].slice(0,14);
  const bullW = ["bullish","breakout","rally","pump","support holds","buy","long","moon","صعود","صاعد","شراء","اختراق","ارتفاع"], bearW = ["bearish","breakdown","dump","crash","sell","short","resistance rejects","هبوط","هابط","بيع","كسر","انخفاض"];
  const cnt = ws => ws.reduce((a,w) => a + (low.split(w).length-1), 0), b = cnt(bullW), r = cnt(bearW);
  const sents = text.split(/(?<=[.!?؟\n])\s+/).filter(s => /(target|support|resistance|stop|entry|breakout|هدف|دعم|مقاومة|وقف|دخول|اختراق|\d)/i.test(s)).slice(0,6);
  return '<div><b>'+esc(T("coins"))+':</b> '+(coins.length ? coins.map(c => '<span class="chip">'+esc(c)+'</span>').join("") : esc(T("none")))+'</div>'
    +'<div><b>'+esc(T("levels"))+':</b> '+(lv.length ? lv.map(c => '<span class="chip">'+esc(c)+'</span>').join("") : esc(T("none")))+'</div>'
    +'<div><b>'+esc(T("tone"))+':</b> <span class="g">'+esc(T("bull"))+' '+b+'</span> / <span class="rd">'+esc(T("bear"))+' '+r+'</span></div>'
    +'<div><b>'+esc(T("claims"))+':</b><ul style="margin:2px 0;padding-inline-start:16px">'+(sents.length ? sents.map(s => '<li>'+esc(s)+'</li>').join("") : "<li>"+esc(T("none"))+"</li>")+'</ul></div>';
}

/* ---------------- workspace manager ---------------- */
Ws.el = document.getElementById("ws");
const SYMW = ["chart","dom","tape","limits","ofm","liq","posn","tvc"];
// app symbol -> TradingView symbol (crypto on OKX like the app; TradFi on liquid TradingView feeds)
function tvSym(s){ s = String(s || "");
  const TF_ = {GOLD:"OANDA:XAUUSD", SILVER:"OANDA:XAGUSD", OIL:"TVC:USOIL", WTI:"TVC:USOIL", BRENT:"TVC:UKOIL", SP500:"OANDA:SPX500USD", SPX:"OANDA:SPX500USD", NASDAQ:"OANDA:NAS100USD", NDX:"OANDA:NAS100USD",
    NAS100:"OANDA:NAS100USD", DJI:"OANDA:US30USD", EUR:"FX:EURUSD", GBP:"FX:GBPUSD", JPY:"FX:USDJPY", TLT:"NASDAQ:TLT", DXY:"TVC:DXY", NATGAS:"TVC:NATURALGAS", COPPER:"COMEX:HG1!"};
  const Y_ = {"GC=F":"OANDA:XAUUSD", "SI=F":"OANDA:XAGUSD", "CL=F":"TVC:USOIL", "BZ=F":"TVC:UKOIL", "NG=F":"TVC:NATURALGAS", "^GSPC":"OANDA:SPX500USD", "^NDX":"OANDA:NAS100USD", "^IXIC":"NASDAQ:IXIC", "^DJI":"OANDA:US30USD", "DX-Y.NYB":"TVC:DXY", "^VIX":"TVC:VIX"};
  if (/^HL:/.test(s)){ const k = s.split(":").pop().toUpperCase(); return TF_[k] || k; }
  if (/^Y:/.test(s)){ const k = s.slice(2); if (Y_[k]) return Y_[k]; const fx = k.match(/^([A-Z]{6})=X$/); return fx ? "FX:"+fx[1] : k.replace(/^\^/, ""); }
  if (/^FH:/.test(s)){ const m = s.slice(3).match(/^([A-Z_]+):([A-Z]+)_([A-Z]+)$/); return m ? m[1]+":"+m[2]+m[3] : s.slice(3); }
  const p = s.split("-"); if (p.length >= 2) return "OKX:"+p[0]+p[1]+(p[2] === "SWAP" ? ".P" : "");
  return s; }
Ws.broadcast = (from, sym) => {
  if (SYMW.includes(from.type)) from.setSymbol(sym);
  const g = from.state.group;
  Ws.panels.forEach(p => { if (p !== from && SYMW.includes(p.type) && (g ? p.state.group === g : from.type === "watch")) p.setSymbol(sym); });
};
// phones, MT5 layout: MetaTrader's bottom tabs (text only). A tab shows the first widget of its kinds and creates one if missing; the rest are under "More".
const MTABS = [[["Quotes","الأسعار"], ["watch"], "watch"], [["Chart","الرسم البياني"], ["chart","tvc"], "chart"], [["Trade","التداول"], ["setup","dom","signals"], "setup"],
               [["History","السجل"], ["journal","alerts"], "journal"], [["Messages","الرسائل"], ["news","alerts"], "news"]];   // labels picked at build time (the language is known then)
Ws.focusTrade = async id => {
  const t = Journal.list.find(x => x.id === id); if (!t) return;
  const panel = Ws.panels.find(q => q.type === "chart" && q.chart && q.state && q.state.sym === t.symbol); if (!panel) return;
  for (let k = 0; k < 20 && panel.chart.data.length && panel.chart.data[0].t > t.t0 && !panel.noMore; k++) await panel.loadMore();
  const ch = panel.chart, i0 = ch.data.findIndex(b => b.t >= t.t0); if (i0 < 0) return;
  ch.r = i0 + Math.round(ch.PR/ch.bw/2); ch.clampR(); ch.saveView(); ch.draw();
};
Ws.mshow = p => { if (!MOB || !p) return; p.root.classList.add("p-"+p.type); Ws.panels.forEach(q => q.root.classList.toggle("mact", q === p)); Ws.mcur = p; p.min = false; p.root.classList.remove("min");
  const mm = document.getElementById("mmore"); if (mm) mm.classList.remove("on");
  document.querySelectorAll("#mnav button").forEach(b => b.classList.toggle("on", !!b._match && b._match(p))); setTimeout(() => { try { p.chart && (p.chart.resize ? p.chart.resize() : 0, p.chart.draw()); } catch(e){} }, 30); };
Ws.mjump = () => {
  if (!MT5){ ["mnav","mmore"].forEach(id => { const x = document.getElementById(id); if (x) x.remove(); }); Ws.panels.forEach(q => q.root.classList.remove("mact")); if (typeof M5 !== "undefined") M5.destroy(); return; }
  if (MOB && typeof M5 !== "undefined"){ ["mnav","mmore"].forEach(id => { const x = document.getElementById(id); if (x) x.remove(); }); if (!document.getElementById("m5nav")) M5.build(); return; }   // phones: the MetaTrader 5 copy
  let j = document.getElementById("mnav"); if (!j){ j = el("div"); j.id = "mnav"; document.body.append(j); }
  let mm = document.getElementById("mmore"); if (!mm){ mm = el("div"); mm.id = "mmore"; document.body.append(mm); }
  j.innerHTML = ""; const used = new Set();
  MTABS.forEach(([lab, kinds, make]) => { const b = el("button", null, Lg(lab[0], lab[1])); const pick = () => kinds.map(k => Ws.panels.find(p => p.type === k && !used.has(p))).find(Boolean);
    const p0 = pick(); if (p0) used.add(p0); b._match = p => p === p0 || (!p0 && kinds.includes(p.type));
    b.onclick = () => { let p = p0 && Ws.panels.includes(p0) ? p0 : null; if (!p){ Ws.add(make); p = Ws.panels[Ws.panels.length - 1]; } Ws.mshow(p); }; j.append(b); });
  const rest = Ws.panels.filter(p => !used.has(p)), more = el("button", null, Lg("More","المزيد"));
  more._match = p => rest.includes(p); more.onclick = () => { mm.innerHTML = ""; rest.forEach(p => { const x = el("button", null, T(p.type)); x.onclick = () => Ws.mshow(p); mm.append(x); });
    const add = el("button", null, "+ "+Lg("Add widget","إضافة ويدجت")); add.onclick = () => { mm.classList.remove("on"); const sel = document.querySelector("#bar select"); sel && sel.focus(); }; mm.append(add); mm.classList.toggle("on"); };
  j.append(more);
  if (!Ws.mcur || !Ws.panels.includes(Ws.mcur)) Ws.mshow(Ws.panels.find(p => p.type === "chart") || Ws.panels[0]); else Ws.mshow(Ws.mcur); };
Ws.checkEmpty = () => { Ws.mjump && Ws.mjump(); const e = document.getElementById("empty"); e.textContent = T("emptyMsg"); e.style.display = Ws.panels.length ? "none" : "flex"; };
Ws.save = () => {
  const wsNow = { lang, v:7, panels: Ws.panels.map(p => ({type:p.type, rect: p.max && p.prev ? p.prev : p.rect, state:p.state})) };
  store.set(LS, wsNow);
  try { sessionStorage.setItem(LS+"_tab", JSON.stringify(wsNow)); } catch(e){}   // task 54: this tab reloads its own layout, not whatever another tab saved last
  Ws.checkEmpty(); Ws.histPush();
};
/* Undo / Redo: every saved change of the workspace (panels added / removed / moved / resized, symbols, timeframes, indicators, colours, per-panel settings) is a step; the last 120 steps are kept */
Ws.hist = {a:[], i:-1, max:121, mute:0};
Ws.histPush = () => { const H = Ws.hist; if (H.mute) return; let snap; try { snap = JSON.stringify(Ws.panels.map(p => [p.type, p.max && p.prev ? p.prev : p.rect, p.state])); } catch(e){ return; }
  if (H.a[H.i] === snap) return; const now = Date.now(); if (H.i > 0 && H.i === H.a.length-1 && now - (H.t || 0) < 400){ H.a[H.i] = snap; H.t = now; Ws.histUI(); return; }   // saves fired back-to-back by one action count as one step
  H.t = now; H.a = H.a.slice(0, H.i+1); H.a.push(snap); if (H.a.length > H.max) H.a.shift(); H.i = H.a.length-1; Ws.histUI(); };
Ws.histGo = d => { const H = Ws.hist, j = H.i + d; if (j < 0 || j >= H.a.length) return; H.i = j; H.mute++;
  try { const list = JSON.parse(H.a[j]); Ws.clear(); Ws.build(list); Ws.save(); } finally { H.mute--; } Ws.histUI(); };
Ws.undo = () => Ws.histGo(-1); Ws.redo = () => Ws.histGo(1);
Ws.histUI = () => { const H = Ws.hist, u = document.getElementById("undoB"), r = document.getElementById("redoB"); if (u){ u.disabled = H.i <= 0; u.title = (lang === "ar" ? "تراجع (Ctrl+Z) — " : "Undo (Ctrl+Z) — ")+Math.max(0, H.i)+(lang === "ar" ? " خطوة متاحة" : " steps available"); }
  if (r){ r.disabled = H.i >= H.a.length-1; r.title = (lang === "ar" ? "إعادة (Ctrl+Shift+Z / Ctrl+Y) — " : "Redo (Ctrl+Shift+Z / Ctrl+Y) — ")+Math.max(0, H.a.length-1-H.i)+(lang === "ar" ? " خطوة" : " steps"); } };
document.addEventListener("keydown", e => { if (!(e.ctrlKey || e.metaKey) || e.altKey) return; const t = e.target, tn = t && t.tagName; if (tn === "INPUT" || tn === "TEXTAREA" || tn === "SELECT" || (t && t.isContentEditable)) return;
  const k = e.key.toLowerCase(); if (k === "z" && !e.shiftKey){ e.preventDefault(); Ws.undo(); } else if ((k === "z" && e.shiftKey) || k === "y"){ e.preventDefault(); Ws.redo(); } });
Ws.clear = () => { Ws.panels.slice().forEach(p => { p.clearSubs(); p.destroy && p.destroy(); p.root.remove(); }); Ws.panels = []; };
Ws.defaults = () => {
  const W = Ws.el.clientWidth || 1200, H0 = Ws.el.clientHeight || 700, r = v => Math.round(v/10)*10, rh = 150, oy = rh + 10, H = H0 - oy;
  const lw = r(W*0.22), x1 = lw+10, cw = r(W*0.36), x2 = x1+cw+10, dw = r(W*0.18), x3 = x2+dw+10, tw = W-x3;
  const top = r(H*0.7), wh = r(H*0.62), sh = 0;
  return [["signals", {x:0,y:0,w:W,h:rh}, {}]].concat([
    ["watch", {x:0,y:0,w:lw,h:wh}, {group:1}],
    ["alerts", {x:0,y:wh+10,w:lw,h:H-wh-10}, {}],
    ["chart", {x:x1,y:sh,w:cw,h:r((top-sh)/2)}, {sym:SYMS[0], group:1, tf:"15s", ema:{9:true,21:false,50:false}}],
    ["chart", {x:x1,y:sh+r((top-sh)/2)+10,w:cw,h:top-sh-r((top-sh)/2)-10}, {sym:SYMS[0], group:1, tf:"5m", ema:{9:true,21:true,50:false}}],
    ["dom", {x:x2,y:sh,w:dw,h:top-sh}, {sym:SYMS[0], group:1}],
    ["tape", {x:x3,y:sh,w:tw,h:top-sh}, {sym:SYMS[0], group:1}],
    ["limits", {x:x1,y:top+10,w:cw,h:H-top-10}, {sym:SYMS[0], group:1}],
    ["scanner", {x:x2,y:top+10,w:dw+10+tw,h:H-top-10}, {}],
  ].map(([t,rc,st]) => [t, Object.assign({}, rc, {y:rc.y+oy}), st]));
};
