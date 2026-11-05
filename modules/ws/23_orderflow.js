/* ---- price grouping (order book / heat rows): ONE control and ONE rule, reused by the DOM panel and the order-flow column ---- */
const GROUP_STEPS = [10000, 5000, 1000, 500, 100, 50, 10, 5, 1, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001];
function tickOfLevels(levels){   // smallest gap between neighbouring book prices = the instrument tick (estimate); 0 when unknown
  const ps = [...new Set(levels.map(x => +x.p))].filter(Number.isFinite).sort((a, b) => a - b); let t = 0;
  for (let i = 1; i < ps.length; i++){ const d = ps[i] - ps[i-1]; if (d > 1e-12 && (!t || d < t)) t = d; }
  return t ? +t.toPrecision(6) : 0; }
function groupBook(levels, step, side){   // [{p,q}] -> [{p,q}] summed per price bucket; bids round down, asks round up, so a bucket never crosses the spread
  if (!(step > 0)) return levels; const m = new Map(), r = x => +x.toFixed(10);
  levels.forEach(x => { const k = r((side === "ask" ? Math.ceil(x.p/step - 1e-9) : Math.floor(x.p/step + 1e-9))*step); m.set(k, (m.get(k) || 0) + x.q); });
  return [...m].map(([p, q]) => ({p, q})).sort((a, b) => side === "ask" ? a.p - b.p : b.p - a.p); }
const groupStepFor = (want, tick) => want > 0 ? Math.max(want, tick || 0) : 0;   // a value below the tick is clamped to the tick
function groupSelect(cur, tick, onChange){
  const sel = el("select"); sel.className = "gsel"; sel.title = Lg("Price grouping (Auto = automatic)", "تجميع السعر (Auto = تلقائي)"); const o0 = el("option", null, "Auto"); o0.value = "0"; sel.append(o0);
  GROUP_STEPS.forEach(v => { const o = el("option", null, String(v)); o.value = String(v); sel.append(o); });
  sel.sync = (c, t) => { [...sel.options].forEach(o => { o.disabled = +o.value > 0 && t > 0 && +o.value < t*0.999; }); sel.value = String(c || 0); if (sel.selectedIndex < 0) sel.value = "0"; };
  sel.sync(cur, tick); sel.onchange = () => onChange(+sel.value || 0);
  ["mousedown", "pointerdown", "click", "wheel", "dblclick"].forEach(ev => sel.addEventListener(ev, e => e.stopPropagation())); return sel; }
function renderDom(book, tape, prev, opts){
  const LV = (opts && opts.lev) || 12, asks = book.asks.slice().sort((a,b)=>a.p-b.p).slice(0,LV), bids = book.bids.slice().sort((a,b)=>b.p-a.p).slice(0,LV), cumOf = {};
  if (opts && opts.cum){ let c1 = 0; asks.forEach(x => cumOf[x.p] = (c1 += x.q)); c1 = 0; bids.forEach(x => cumOf[x.p] = (c1 += x.q)); }
  const all = asks.concat(bids).map(x=>x.q), mx = Math.max(...all, 1e-12), med = median(book.asks.concat(book.bids).map(x=>x.q));
  const hits = tape ? tape.hits : {}, ab = tape ? tape.ab : new Set(), sizes = {};
  const cell = (q, color, align, big, hot, grew, cum) => {
    const w = Math.max(4, Math.round(100*q/mx)), cls = (big ? "big " : "") + (hot ? "hot" : big ? "glow" : grew ? "gr" : "");
    return '<div class="cell '+cls+'"><div class="f" style="'+(align==="right"?"right":"left")+':0;width:'+w+'%;background:'+color+'"></div><div class="t" style="text-align:'+align+'">'+(big?"★ ":"")+fmtQ(q)+(cum != null ? ' <span style="opacity:.55;font-size:10px">Σ'+fmtQ(cum)+'</span>' : "")+'</div></div>';
  };
  let rows = "";
  const line = (x, side) => {
    sizes[x.p] = x.q; const big = med && x.q >= settings.big*med, hit = hits[x.p], grew = prev && (prev[x.p] == null || x.q >= prev[x.p]*1.25);
    const isAsk = side === "ask", pc = ab.has(x.p) ? "ab" : hit ? (hit==="Buy" ? "hb" : "hs") : "";
    return '<tr><td style="width:38%">'+(isAsk ? "" : cell(x.q,"#0ecb81","right",big,big&&hit,grew,cumOf[x.p]))+'</td><td class="'+pc+'" style="width:24%;text-align:center;font-weight:600;color:'+(isAsk?"#f6465d":"#0ecb81")+'">'+fmtP(x.p)+(ab.has(x.p)?' <b style="color:#b57cff">ABS</b>':"")+flowTag(opts && opts.sym, x.p, (opts && opts.tol) || 0)+'</td><td style="width:38%">'+(isAsk ? cell(x.q,"#f6465d","left",big,big&&hit,grew,cumOf[x.p]) : "")+'</td></tr>';
  };
  asks.slice().reverse().forEach(x => rows += line(x,"ask"));
  if (asks.length && bids.length) rows += '<tr><td colspan="3" style="text-align:center;color:#f0b90b;font-size:11px;border-top:1px solid #2b3139;border-bottom:1px solid #2b3139">'+Lg("spread ","الفارق ")+fmtP(asks[0].p-bids[0].p)+'</td></tr>';
  bids.forEach(x => rows += line(x,"bid"));
  const sB = bids.reduce((a, x) => a + x.q, 0), sA = asks.reduce((a, x) => a + x.q, 0), im = (sA + sB) ? (sB - sA)/(sA + sB)*100 : 0, bpc = (sA + sB) ? 100*sB/(sA + sB) : 50;
  const cf = opts && opts.conf, confHtml = cf && cf.dir ? ' · <b style="color:'+(cf.dir > 0 ? "#0ecb81" : "#f6465d")+'" title="'+esc(Lg("Flow confluence v1 (a reading, not advice): level + delta + tape + absorption","توافق الفلو v1 (قراءة مش نصيحة): مستوى + دلتا + شريط + امتصاص"))+'">'+Lg("Flow ","فلو ")+(cf.dir > 0 ? "▲" : "▼")+' '+cf.n+'/4 <span class="m" style="font-weight:400">'+cf.parts.join("+")+'</span></b>' : "";
  const strip = '<div class="stat" style="padding:2px 6px">'+Lg("Bids ","طلب ")+'<b class="g">'+fmtQ(sB)+'</b> · '+Lg("Asks ","عرض ")+'<b class="rd">'+fmtQ(sA)+'</b> · '+Lg("imbalance ","اختلال ")+'<b class="'+(im >= 0 ? "g" : "rd")+'">'+(im >= 0 ? "+" : "")+im.toFixed(0)+'%</b> <span class="m">('+LV+' '+Lg("levels","مستوى")+')</span>'+confHtml+'</div><div class="bar2"><div style="width:'+bpc.toFixed(0)+'%;background:#0ecb81"></div><div style="width:'+(100-bpc).toFixed(0)+'%;background:#f6465d"></div></div>';
  return {html:strip+'<table><tr><th>'+esc(T("bid"))+'</th><th style="text-align:center">'+esc(T("price"))+'</th><th>'+esc(T("ask"))+'</th></tr>'+rows+'</table>', sizes};
}
const TAPE_COLS = [24,20,22,18,16], LIM_COLS = [14,10,20,16,28,12];
function colGroup(panel, key, def){ const w = (panel.state.cw && panel.state.cw[key]) || def; return '<colgroup>'+w.map(x => '<col style="width:'+x+'%">').join("")+'</colgroup>'; }
function headRow(labels, aligns){ return '<tr>'+labels.map((l,i) => '<th class="'+(aligns[i]||"")+'" style="position:sticky">'+esc(l)+(i < labels.length-1 ? '<span class="rzh" data-i="'+i+'"></span>' : '')+'</th>').join("")+'</tr>'; }
function bindColResize(panel, box, key, def){
  box.addEventListener("pointerdown", e => {
    const h = e.target.closest(".rzh"); if (!h) return; e.preventDefault(); e.stopPropagation();
    const i = +h.dataset.i, table = box.querySelector("table"), total = table.clientWidth || 1, sx = e.clientX;
    const w0 = ((panel.state.cw && panel.state.cw[key]) || def).slice();
    const mv = ev => {
      const d = (ev.clientX - sx)/total*100, w = w0.slice(), mn = 4;
      let a = w0[i] + d, b = w0[i+1] - d; if (a < mn){ b -= mn - a; a = mn; } if (b < mn){ a -= mn - b; b = mn; }
      w[i] = a; w[i+1] = b; panel.state.cw = panel.state.cw || {}; panel.state.cw[key] = w;
      table.querySelectorAll("col").forEach((c,j) => c.style.width = w[j]+"%");
    };
    const up = () => { window.removeEventListener("pointermove", mv); window.removeEventListener("pointerup", up); Ws.save(); };
    window.addEventListener("pointermove", mv); window.addEventListener("pointerup", up);
  });
}
function renderTape(panel, rows){
  let h = '<table class="fx">'+colGroup(panel,"tape",TAPE_COLS)+headRow([T("price"),T("size"),T("value"),"",T("time")],["","r","r","","r"]);
  rows.forEach(r => {
    const buy = r.side === "Buy", col = buy ? "#0ecb81" : "#f6465d", rgb = buy ? "14,203,129" : "246,70,93";
    let cls = r.absorb ? "ab" : r.isNew && r.tier === "whale" ? "wn" : r.isNew && r.tier === "smart" ? "sn "+(buy?"nb":"ns") : r.isNew ? (buy ? "nb" : "ns") : "";
    const bg = "rgba("+rgb+",.07)", edge = "", mk = r.absorb ? '<i class="mk a"></i>' : r.tier === "whale" ? '<i class="mk w"></i>' : r.tier === "smart" ? '<i class="mk s"></i>' : "";   // no filled rows: the marker carries the meaning
    const tag = (r.tier === "whale" ? "WHALE" : r.tier === "smart" ? "SMART" : "") + (r.absorb ? " "+Lg("ABSORB","امتصاص") : "");
    h += '<tr class="'+cls+'" style="background:'+bg+';'+edge+'color:'+col+';font-weight:'+(r.tier!=="normal"?700:400)+'"><td>'+mk+fmtP(r.p)+'</td><td class="r">'+fmtQ(r.q)+'</td><td class="r" style="color:#eaecef;font-weight:400">$'+Math.round(r.notional).toLocaleString("en-US")+'</td><td style="color:'+(r.absorb?"#e0c9ff":"#f0b90b")+';font-size:10px">'+tag.trim()+flowTag(panel.state.sym, r.p, r.p*0.0001)+'</td><td class="r m" style="font-weight:400">'+hms(r.t)+'</td></tr>';
  });
  return h+'</table>';
}
function drawDepth(cv, book){
  if (!cv) return; const c = cv.getContext("2d"), W = cv.width, H = cv.height; c.clearRect(0,0,W,H);
  if (!book || !book.bids || !book.bids.length) return;
  const bids = book.bids.slice().sort((a,b)=>b.p-a.p).slice(0,40), asks = book.asks.slice().sort((a,b)=>a.p-b.p).slice(0,40);
  let cb = 0, ca = 0; const B = bids.map(x => ({p:x.p, c:(cb += x.q)})), A = asks.map(x => ({p:x.p, c:(ca += x.q)}));
  const lo = B[B.length-1].p, hi = A[A.length-1].p, mx = Math.max(cb, ca) || 1, X = p => (p-lo)/(hi-lo || 1)*W, Y = v => H - 3 - v/mx*(H-8);
  const area = (pts, col, fill) => {
    c.beginPath(); c.moveTo(X(pts[0].p), H); pts.forEach(q => c.lineTo(X(q.p), Y(q.c))); c.lineTo(X(pts[pts.length-1].p), H); c.closePath();
    c.fillStyle = fill; c.fill(); c.strokeStyle = col; c.lineWidth = 2; c.beginPath(); pts.forEach((q,i) => i ? c.lineTo(X(q.p), Y(q.c)) : c.moveTo(X(q.p), Y(q.c))); c.stroke();
  };
  area(B, "#0ecb81", "rgba(14,203,129,.28)"); area(A, "#f6465d", "rgba(246,70,93,.28)");
}
function absorbEvents(lt, rows){
  const now = nowS(), seen = {};   // exchange time, like the candles (PC clock may be off)
  rows.filter(r => r.absorb).forEach(r => { const o = seen[r.p] = seen[r.p] || {q:0, adir:r.adir}; o.q += r.q; });
  Object.entries(seen).forEach(([p,o]) => { const k = p+"|"+Math.floor(now/120000); if (lt.abs.has(k)) return; lt.abs.add(k); lt.events.unshift({t:now, ev:"ABSORB", side:o.adir === "sellers" ? "ask" : "bid", p:+p, q:o.q}); });
  lt.events = lt.events.slice(0, 200);
}
function limitUpdate(lt, book, rows){
  const now = nowS(), cur = {};
  [["bid", book.bids],["ask", book.asks]].forEach(([side, arr]) => {
    const med = median(arr.map(x=>x.q));
    arr.forEach(x => { if (med && x.q >= settings.big*med) cur[side+"|"+x.p] = x.q; });
  });
  let lo = null, hi = null; if (rows && rows.length){ const ps = rows.map(r=>r.p); lo = Math.min(...ps); hi = Math.max(...ps); }
  if (lt.prev){
    Object.keys(cur).forEach(k => { if (!(k in lt.prev)){ const [s,p] = k.split("|"); lt.events.unshift({t:now, ev:"PLACED", side:s, p:+p, q:cur[k]}); } });
    const bmin = Math.min(...book.bids.map(x=>x.p)), amax = Math.max(...book.asks.map(x=>x.p));
    Object.keys(lt.prev).forEach(k => {
      const [s,ps] = k.split("|"), p = +ps, old = lt.prev[k], nq = cur[k] || 0;
      if (s === "bid" && p < bmin) return; if (s === "ask" && p > amax) return;
      if (nq < 0.4*old){ const thru = (s==="ask" && hi != null && hi >= p) || (s==="bid" && lo != null && lo <= p); lt.events.unshift({t:now, ev:thru?"FILLED":"PULLED", side:s, p, q:old}); }
    });
  }
  lt.prev = cur; lt.events = lt.events.slice(0, 200);
}
function renderEvents(panel, evAll){
  const w = panel.state.lwin != null ? panel.state.lwin : 900000, f = panel.state.flt || "all", now = Date.now();
  const ev = evAll.filter(e => (!w || e.t >= now - w) && (f === "all" || (f === "abs" ? e.ev === "ABSORB" : e.side === f)));
  if (!ev.length) return '<div class="err" style="color:#848e9c">'+esc(T("watching"))+'</div>';
  const rgb = {PLACED:"74,163,255", PULLED:"240,185,11", FILLED:"132,142,156", ABSORB:"181,124,255"}, col = {PLACED:"#4aa3ff", PULLED:"#f0b90b", FILLED:"#9aa3ad", ABSORB:"#c9a3ff"};
  const note = {PLACED:T("placed"), PULLED:T("pulled"), FILLED:T("filled"), ABSORB:Lg("absorption","امتصاص")};
  const gly = {PLACED:"●", PULLED:"✕", FILLED:"■", ABSORB:"◆"}, nm = {PLACED:"NEW", PULLED:"PULL", FILLED:"FILL", ABSORB:"ABS"}, ev0 = {PLACED:Lg("new","جديد"), PULLED:Lg("pulled (possible fake wall)","اتشال (جدار وهمي محتمل)"), FILLED:Lg("traded","اتنفذ"), ABSORB:Lg("absorbed","امتصاص")};
  let h = '<div class="evl">'+["PLACED","PULLED","FILLED","ABSORB"].map(k => '<b style="color:'+col[k]+'">'+gly[k]+'</b> '+ev0[k]).join(" &nbsp; ")+'</div><table class="fx">'+colGroup(panel,"lim",LIM_COLS)+headRow([T("event"),T("side"),T("price"),T("size"),T("note"),T("time")],["","","","r","","r"]);
  ev.slice(0,60).forEach(e => { const key = e.ev === "ABSORB" || e.ev === "PULLED"; h += '<tr'+(now-e.t < 1500 ? ' class="evf"' : "")+(key ? ' style="box-shadow:inset 2px 0 0 '+col[e.ev]+'"' : "")+'><td title="'+esc(note[e.ev])+'"><b style="color:'+col[e.ev]+'">'+gly[e.ev]+'</b> '+nm[e.ev]+'</td><td class="'+(e.side==="bid"?"g":"rd")+'">'+e.side.toUpperCase()+'</td><td>'+fmtP(e.p)+flowTag(panel.state.sym, e.p, e.p*0.0001)+'</td><td class="r">'+fmtQ(e.q)+'</td><td class="m" style="font-size:10px">'+esc(note[e.ev])+'</td><td class="r m">'+hms(e.t)+'</td></tr>'; });
  return h+'</table>';
}

function logoColor(sym){ let h = 0; for (const c of sym) h = (h*31 + c.charCodeAt(0)) % 360; return "hsl("+h+",70%,60%)"; }
const durTxt = ms => { const m = Math.max(1, Math.round(ms/60000)), d = Math.floor(m/1440), h = Math.floor(m%1440/60), mi = m%60, ar = lang === "ar";
  return (d ? d+(ar ? " يوم " : "d ") : "")+(h ? h+(ar ? " ساعة " : "h ") : "")+(!d ? mi+(ar ? " دقيقة" : "m") : "").trim(); };
function alertOutcome(a){   // the journal follows every alert trade on OKX candles until TP1 or the stop is touched
  const c = a.card, key = c.symbol+"|"+c.direction+"|"+c.ttype; let best = null;
  Journal.list.forEach(t => { if (t.key === key && t.t0 >= a.t - 60000 && (t.status === "tp" || t.status === "sl") && t.t1 && (!best || t.t0 < best.t0)) best = t; });
  return best;
}
function alertCard(a){
  const c = a.card, bull = c.direction === "bullish", st = "★".repeat(c.score)+'<span class="o">'+"★".repeat(Math.max(0,c.max-c.score))+'</span>';
  const f = v => fmtP(v), pl = c.plan, base = c.symbol.split("-")[0];
  const oc = alertOutcome(a);
  const d = el("div","card"); d.style.borderInlineStart = "3px solid "+(bull ? "#0ecb81" : "#f6465d");
  d.innerHTML = '<div class="row"><span class="logo" style="background:'+logoColor(base)+'">'+esc(base.slice(0,4))+'</span><b style="font-size:13px">'+esc(c.symbol)+'</b>'
    +'<span class="badge" style="background:'+(bull?"#0ecb81":"#f6465d")+';color:#000">'+esc(bull ? T("long") : T("short"))+'</span><span class="grow"></span>'+sparkSvg(c, 64, 20)+'<span class="stars" title="'+c.score+'/'+c.max+'" style="margin-inline-start:6px">'+st+'</span></div>'
    +'<div class="row" style="margin-top:4px">'+(c.tags||[]).map(t => '<a class="badge" target="_blank" rel="noopener noreferrer" href="'+esc(/^https:\/\//.test(c.tv||"") ? c.tv : "#")+'" title="'+esc(tagTip(t))+'" style="text-decoration:none;cursor:help;background:'+esc(t[1])+';color:'+esc(t[2])+'">'+esc(tagTxt(t[0]))+'</a>').join("")+'<span class="m">'+c.score+' '+esc(T("strats"))+'</span><span class="grow"></span><b style="color:'+(c.score/c.max>=0.6?"#0ecb81":c.score/c.max>=0.4?"#f0b90b":"#848e9c")+'" title="'+esc(T("conf"))+'">'+Math.round(100*c.score/c.max)+'%</b></div>'
    +(pl ? '<div class="plan"><div style="color:#4aa3ff">'+esc(T("entry"))+'<br>'+f(pl.entry)+'</div><div style="color:#f6465d">'+esc(T("stop"))+(oc && oc.status === "sl" ? ' <b style="font-size:13px">✓</b>' : '')+'<br>'+f(pl.stop)+'</div>'+pl.tps.map((v,i) => '<div style="color:#0ecb81">TP'+(i+1)+(oc && oc.status === "tp" && i === 0 ? ' <b style="font-size:13px">✓</b>' : '')+'<br>'+f(v)+'</div>').join("")+'</div>' : "")
    +(oc ? '<div class="m" style="margin-top:3px;font-weight:600;color:'+(oc.status === "tp" ? "#0ecb81" : "#f6465d")+'">✓ '+esc(oc.status === "tp" ? (lang === "ar" ? "تحقق الهدف TP1" : "TP1 hit") : (lang === "ar" ? "تحقق وقف الخسارة SL" : "Stop-loss hit"))+' · '+esc((lang === "ar" ? "خلال " : "after ")+durTxt(oc.t1 - a.t))+'</div>' : '')
    +'<div class="row" style="margin-top:5px"><span class="badge" style="border:1px solid #f0b90b;color:#f0b90b">'+esc(ttTxt(c.ttype))+'</span><span class="m">'+esc(T("eta"))+': TP1 '+esc(etaTxt((c.eta||{}).tp1))+' · TP3 '+esc(etaTxt((c.eta||{}).tp3))+'</span></div>'
    +'<div class="row" style="margin-top:5px"><button class="sc">'+esc(T("showchart"))+'</button><button class="an">'+esc(lang === "ar" ? "التحليل" : "Analysis")+'</button><a class="link" target="_blank" rel="noopener noreferrer" href="'+esc(/^https:\/\//.test(c.tv||"") ? c.tv : "#")+'">'+esc(T("tvopen"))+' ↗</a><span class="grow"></span><span class="m">'+hms(a.t)+'</span></div>';
  d.querySelector(".sc").onclick = () => Ws.showOnChart(c);
  d.querySelector(".an").onclick = e => { e.stopPropagation(); Ws.anaPop(e.currentTarget, c); };
  { const tt = tfTxt(c); if (tt){ const m = el("div","m"); m.style.cssText = "font-size:10px;margin-top:3px"; m.textContent = (lang === "ar" ? "تاريخياً: " : "History: ")+tt; d.append(m); } }
  return d;
}
/* Time & Sales sensitivity (Smart / Big / Absorb) — lives in the tape + Order Flow settings, not the top bar */
Ws.sensRows = (pop, row) => { const ar = lang === "ar";
  [["smart", ar ? "حساسية Smart ×" : "Smart × (T&S smart threshold)"],["big", ar ? "حساسية Big ×" : "Big × (T&S big threshold)"],["absorb", ar ? "حساسية Absorb ×" : "Absorb × (absorption)"]].forEach(([k,lab]) => {
    const i = el("input"); i.type = "number"; i.step = "0.5"; i.min = "1"; i.value = settings[k]; i.style.width = "60px"; i.onchange = () => { settings[k] = Math.max(1, +i.value || settings[k]); i.value = settings[k]; saveSettings(); }; row(lab, i); }); };
Ws.fmtBtn = () => { const b = el("button", null, "#.#"); b.title = Lg("Number format: decimals, thousands separators, compact sizes (all tables)","تنسيق الأرقام: العشري والفواصل والاختصار (كل الجداول)"); b.onclick = e => { e.stopPropagation(); Ws.fmtPop(b); }; b.onpointerdown = e => e.stopPropagation(); return b; };
Ws.fmtPop = anchor => {
  document.querySelectorAll(".stpop").forEach(x => x.remove()); const pop = el("div", "stpop"), r = anchor.getBoundingClientRect(); pop.style.left = Math.max(4, Math.min(r.left, innerWidth - 300))+"px"; pop.style.top = (r.bottom + 3)+"px"; pop.style.gridTemplateColumns = "1fr auto"; pop.style.minWidth = "250px";
  const h = el("div", "full"); h.style.cursor = "default"; h.textContent = Lg("Number format (all tables)","تنسيق الأرقام (كل الجداول)"); pop.append(h);
  const apply = () => { Fmt.save(); Ws.panels.forEach(p => { try { p.gRedraw && p.gRedraw(); p.rerender && p.rerender(); p.wDraw && p.wDraw(); p.chart && p.chart.draw(); } catch(e){} }); };
  const row = (lab, input) => { const l = el("span"); l.textContent = lab; pop.append(l, input); input.onpointerdown = e => e.stopPropagation(); };
  const dsel = (key) => { const sel = el("select"); [["", Lg("Auto","تلقائي")], 0, 1, 2, 3, 4, 5, 6].forEach(v => { const o = el("option"); o.value = typeof v === "object" ? v[0] : v; o.textContent = typeof v === "object" ? v[1] : v + " " + Lg("decimals","أرقام عشرية"); sel.append(o); }); sel.value = Fmt[key] == null ? "" : String(Fmt[key]); sel.onchange = () => { Fmt[key] = sel.value === "" ? null : +sel.value; apply(); }; return sel; };
  row(Lg("Price decimals","العشري في السعر"), dsel("pd")); row(Lg("Size decimals","العشري في الحجم"), dsel("qd"));
  { const c1 = el("input"); c1.type = "checkbox"; c1.checked = Fmt.sep; c1.onchange = () => { Fmt.sep = c1.checked; apply(); }; row(Lg("Thousands separators","فواصل الآلاف"), c1);
    const c2 = el("input"); c2.type = "checkbox"; c2.checked = Fmt.cmp; c2.onchange = () => { Fmt.cmp = c2.checked; apply(); }; row(Lg("Compact sizes (K / M)","أحجام مختصرة (K / M)"), c2); }
  document.body.append(pop); setTimeout(() => { const off = ev => { if (!pop.contains(ev.target) && ev.target !== anchor){ pop.remove(); document.removeEventListener("pointerdown", off, true); } }; document.addEventListener("pointerdown", off, true); }, 0);
};
/* FLOWREAD:BEGIN - pure functions (no DOM): ONE wall tracker shared by the heat-map flashes, the limits list and the sync lights, plus the plain-language reading of the order book + tape + limits. Tested by tests/test_flow_read.py (node). Every sentence it produces DESCRIBES what was seen in the last minutes; it never predicts (research: no order-flow signal is proven net of costs, so this is context). Limits stated on purpose: snapshots (1-2 s) miss orders placed and pulled between two polls; one venue is a partial view. */
const FlowRead = (() => {
  const med = a => { if (!a.length) return 0; const s = a.slice().sort((x, y) => x - y), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m-1] + s[m])/2; };
  const tickOf = ps => { const s = [...new Set(ps)].sort((a, b) => a - b); let t = Infinity; for (let i = 1; i < s.length; i++){ const d = s[i] - s[i-1]; if (d > 1e-12 && d < t) t = d; } return t === Infinity ? 0 : t; };
  const newState = () => ({walls:new Map(), prevT:0, prev:null, mids:[], big:5, ev:[]});
  // snap = {t, bids:[{p,q}], asks:[{p,q}]} (any order); trades = [{t,p,q,side:"Buy"|"Sell"}] (any age: only prints after the previous snapshot count).
  // -> events [{t, kind:"PLACED"|"PULLED"|"FILLED"|"REFILL", side:"bid"|"ask", p, q, age (ms the wall had rested), dist (fraction of mid), ratio (printed qty / vanished qty), near (price had been approaching)}]
  function update(st, snap, trades, opt){
    const big = (opt && opt.big) || st.big || 5, bids = snap.bids || [], asks = snap.asks || [];
    if (!bids.length || !asks.length) return [];
    let bb = -Infinity, ba = Infinity; bids.forEach(x => { if (x.p > bb) bb = x.p; }); asks.forEach(x => { if (x.p < ba) ba = x.p; });
    if (!(bb < ba)) return [];
    const t = snap.t, mid = (bb + ba)/2, all = bids.concat(asks), m = med(all.map(x => x.q));
    let lo = Infinity, hi = -Infinity; all.forEach(x => { if (x.p < lo) lo = x.p; if (x.p > hi) hi = x.p; });
    const tk = tickOf(all.map(x => x.p)) || mid*1e-4, sizeAt = new Map(); all.forEach(x => sizeAt.set(x.p, (sizeAt.get(x.p) || 0) + x.q));
    const tr = (trades || []).filter(x => x.t > st.prevT && x.t <= t + 1000);
    st.mids.push([t, mid]); while (st.mids.length && t - st.mids[0][0] > 60000) st.mids.shift();
    const midAgo = ms => { let r = st.mids[0] ? st.mids[0][1] : mid; for (const [tt, mm] of st.mids){ if (t - tt >= ms) r = mm; else break; } return r; };
    const tradedAt = p => tr.reduce((a, x) => a + (Math.abs(x.p - p) <= tk*0.6 ? x.q : 0), 0);
    let mx = 0; all.forEach(x => { if (Math.abs(x.p - mid)/mid <= 0.005 && x.q > mx) mx = x.q; });
    const thr = Math.max(big*m, ((opt && opt.rel) || st.rel || 0.25)*mx);   // a wall must be big against the typical level AND a real share (25 %) of the biggest level near price: on a 2000-level crypto ladder 5 x median is a few cents of BTC that flicker all the time
    const cur = new Map(); bids.forEach(x => { if (m > 0 && x.q >= thr) cur.set("bid|"+x.p, x.q); }); asks.forEach(x => { if (m > 0 && x.q >= thr) cur.set("ask|"+x.p, x.q); });
    const events = [], pw = st.prev;
    const ev = (kind, w, q, extra) => { const dist = Math.abs(w.p - mid)/mid, d0 = Math.abs(w.p - midAgo(10000))/midAgo(10000);
      events.push(Object.assign({t, kind, side:w.side, p:w.p, q, age:t - w.first, dist, near:d0 > dist*1.25}, extra || {})); };
    cur.forEach((q, k) => {
      const w = st.walls.get(k);
      if (!w){ const i = k.indexOf("|"), side = k.slice(0, i), p = +k.slice(i + 1), seen = !!pw && p >= pw.lo && p <= pw.hi;   // seen: the previous snapshot already covered this price, so it is a genuinely new order (not a level that entered the book window because price moved)
        const nw = {side, p, first:t, last:t, q, qMax:q, n:1, refills:0, lastRefill:0, born:seen ? "placed" : "entered"}; st.walls.set(k, nw); if (seen) ev("PLACED", nw, q); return; }
      w.n++; w.last = t; const ex = tradedAt(w.p);
      if (q < 0.6*w.q){ const drop = w.q - q, ratio = ex/drop; ev(ratio >= 0.5 ? "FILLED" : "PULLED", w, drop, {ratio:+ratio.toFixed(2), partial:true}); }
      else if (ex >= 0.5*w.q && q >= 0.8*w.q && t - w.lastRefill > 10000){ w.refills++; w.lastRefill = t; ev("REFILL", w, ex, {refills:w.refills}); }   // hit by prints and the shown size is back: a refill (absorption-like), never called an iceberg
      w.q = q; if (q > w.qMax) w.qMax = q;
    });
    st.walls.forEach((w, k) => {
      if (cur.has(k)) return;
      if (w.p < lo || w.p > hi){ st.walls.delete(k); return; }   // left the visible ladder because price moved: not an event
      const now_ = sizeAt.get(w.p) || 0;
      if (now_ >= 0.6*w.q){ if (now_ < thr*0.7) st.walls.delete(k); else w.q = now_; return; }   // only the 'big' bar moved (median changed): not an event
      const drop = w.q - now_, ratio = tradedAt(w.p)/drop; ev(ratio >= 0.5 ? "FILLED" : "PULLED", w, drop, {ratio:+ratio.toFixed(2)}); st.walls.delete(k);
    });
    st.prev = {lo, hi, t}; st.prevT = t; st.ev.push(...events); if (st.ev.length > 300) st.ev.splice(0, 100);
    return events;
  }
  const fq = q => q >= 1e6 ? (q/1e6).toFixed(1)+"M" : q >= 1000 ? (q/1000).toFixed(1)+"k" : q >= 10 ? q.toFixed(0) : q.toFixed(2);
  const fa = ms => ms < 90000 ? Math.round(ms/1000)+" s" : Math.round(ms/60000)+" m";
  const defP = p => p >= 1000 ? p.toFixed(1) : p >= 1 ? p.toFixed(3) : p.toPrecision(4);
  // ctx = {now, snap:{t,bids,asks}, trades:[{t,p,q,side,tier}], events:[engine events + {kind:"ABSORB", side, p, q, t}], fmtP}
  // -> {tilt:{book,tape,lim,dir,label}, lines:[{sev, side:"bid"|"ask"|null, p, en, ar}], facts}
  function read(st, ctx){
    const now = ctx.now, fp = ctx.fmtP || defP, snap = ctx.snap, lines = [], F = {};
    const stale = snap ? (now - snap.t)/1000 : null;
    let bb = -Infinity, ba = Infinity; if (snap){ (snap.bids || []).forEach(x => { if (x.p > bb) bb = x.p; }); (snap.asks || []).forEach(x => { if (x.p < ba) ba = x.p; }); }
    const mid = isFinite(bb) && isFinite(ba) ? (bb + ba)/2 : null; F.mid = mid;
    if (stale != null && stale > 6) lines.push({sev:5, side:null, p:null, en:"Book data is "+Math.round(stale)+" s old: the reading is unreliable", ar:"داتا الدفتر قديمة ("+Math.round(stale)+" ث): القراءة مش موثوقة"});
    if (mid == null) return {tilt:{book:null, tape:null, lim:0, dir:0, label:{en:"no book", ar:"مفيش دفتر"}}, lines, facts:F};
    let bd = 0, ad = 0; snap.bids.forEach(x => { if (Math.abs(x.p - mid)/mid <= 0.005) bd += x.q; }); snap.asks.forEach(x => { if (Math.abs(x.p - mid)/mid <= 0.005) ad += x.q; });
    const book = bd + ad > 0 ? (bd - ad)/(bd + ad) : null; F.book = {bid:bd, ask:ad, v:book};
    const T = (ctx.trades || []).filter(x => x.t >= now - 120000); let b2 = 0, s2 = 0, b30 = 0, s30 = 0; T.forEach(x => { const buy = x.side === "Buy"; if (buy) b2 += x.q; else s2 += x.q; if (x.t >= now - 30000){ if (buy) b30 += x.q; else s30 += x.q; } });
    const tape = b2 + s2 > 0 ? (b2 - s2)/(b2 + s2) : null; F.tape = {buy:b2, sell:s2, v:tape, v30:b30 + s30 > 0 ? (b30 - s30)/(b30 + s30) : null};
    const evs = (ctx.events || []).filter(e => now - e.t <= 120000); let lim = 0, nl = 0;
    evs.forEach(e => { if (now - e.t > 60000) return; const v = e.kind === "PLACED" ? (e.side === "bid" ? 1 : -1) : e.kind === "PULLED" ? (e.side === "bid" ? -1 : 1) : e.kind === "FILLED" ? (e.side === "ask" ? 1 : -1) : (e.kind === "ABSORB" || e.kind === "REFILL") ? (e.side === "bid" ? 1 : -1) : 0; lim += v; if (v) nl++; });
    const sg = (v, th) => v == null ? 0 : v >= th ? 1 : v <= -th ? -1 : 0, L = [sg(book, .15), sg(tape, .2), nl ? sg(lim, 1) : 0], dir = L.every(x => x === 1) ? 1 : L.every(x => x === -1) ? -1 : 0;
    const act = L.filter(x => x !== 0), mixed = act.some(x => x > 0) && act.some(x => x < 0);
    const label = dir > 0 ? {en:"all three lean buying", ar:"التلاتة بيميلوا للشراء"} : dir < 0 ? {en:"all three lean selling", ar:"التلاتة بيميلوا للبيع"} : mixed ? {en:"book / tape / limits disagree", ar:"الدفتر والشريط والليمت متعارضين"} : act.length ? {en:"one of three leans "+(act[0] > 0 ? "buying" : "selling"), ar:"واحد من التلاتة بيميل لل"+(act[0] > 0 ? "شراء" : "بيع")} : {en:"balanced / quiet", ar:"متوازن / هادي"};
    const sd = s => s === "bid" ? {en:"bid", ar:"شراء"} : {en:"ask", ar:"بيع"}, bp = d => Math.round(d*1e4);
    const pulled = evs.filter(e => e.kind === "PULLED").sort((a, b) => b.t - a.t), near = pulled.find(e => e.dist <= 0.002 && e.age >= 8000) || pulled.find(e => e.near && e.age >= 8000);
    if (near) lines.push({sev:4, side:near.side, p:near.p, en:sd(near.side).en[0].toUpperCase()+sd(near.side).en.slice(1)+" wall "+fq(near.q)+" at "+fp(near.p)+" pulled without trading ("+bp(near.dist)+" bp from price, rested "+fa(near.age)+")", ar:"حائط "+sd(near.side).ar+" "+fq(near.q)+" على "+fp(near.p)+" اتسحب من غير تنفيذ (على بُعد "+bp(near.dist)+"bp من السعر، قاعد "+fa(near.age).replace(" s", " ث").replace(" m", " د")+")"});
    else if (pulled.length >= 3) lines.push({sev:2, side:null, p:null, en:pulled.length+" walls pulled in the last 2 min without trading", ar:pulled.length+" حيطان اتسحبت من غير تنفيذ في آخر دقيقتين"});
    const ab = evs.filter(e => e.kind === "ABSORB").sort((a, b) => b.t - a.t)[0];
    if (ab) lines.push({sev:4, side:ab.side, p:ab.p, en:"Absorption-like at "+fp(ab.p)+": "+(ab.side === "ask" ? "aggressive buying" : "aggressive selling")+" "+fq(ab.q)+" met resting orders without moving price", ar:"امتصاص محتمل عند "+fp(ab.p)+": "+(ab.side === "ask" ? "شراء" : "بيع")+" عدواني "+fq(ab.q)+" اتقابل بأوامر معلّقة من غير ما السعر يتحرك"});
    const rf = evs.filter(e => e.kind === "REFILL").sort((a, b) => b.t - a.t)[0];
    if (rf) lines.push({sev:4, side:rf.side, p:rf.p, en:"Refill at "+fp(rf.p)+" ("+rf.refills+"x): prints hit the "+sd(rf.side).en+" wall and its size came back", ar:"إعادة ملء عند "+fp(rf.p)+" ("+rf.refills+"×): الصفقات بتضرب حائط ال"+sd(rf.side).ar+" وحجمه بيرجع"});
    const fl = evs.filter(e => e.kind === "FILLED" && !e.partial).sort((a, b) => b.t - a.t)[0];
    if (fl) lines.push({sev:3, side:fl.side, p:fl.p, en:sd(fl.side).en[0].toUpperCase()+sd(fl.side).en.slice(1)+" wall "+fq(fl.q)+" at "+fp(fl.p)+" was traded through ("+Math.round(fl.ratio*100)+"% printed)", ar:"حائط "+sd(fl.side).ar+" "+fq(fl.q)+" على "+fp(fl.p)+" اتنفذ ("+Math.round(fl.ratio*100)+"% صفقات)"});
    if (book != null && tape != null && Math.abs(book) >= .15 && Math.abs(tape) >= .2){ const same = (book > 0) === (tape > 0);
      lines.push({sev:2, side:null, p:null, en:"Book "+(book > 0 ? "+" : "")+Math.round(book*100)+"% vs tape "+(tape > 0 ? "+" : "")+Math.round(tape*100)+"%: "+(same ? "agree" : "disagree (resting size and prints point opposite ways)"), ar:"الدفتر "+(book > 0 ? "+" : "")+Math.round(book*100)+"% والشريط "+(tape > 0 ? "+" : "")+Math.round(tape*100)+"%: "+(same ? "متفقين" : "متعارضين (الأوامر المعلقة والصفقات في اتجاهين مختلفين)")}); }
    const walls = [...st.walls.values()].filter(w => Math.abs(w.p - mid)/mid <= 0.005 && now - w.first >= 20000); ["bid", "ask"].forEach(s => { const w = walls.filter(x => x.side === s).sort((a, b) => b.q - a.q)[0];
      if (w) lines.push({sev:1, side:s, p:w.p, en:"Biggest "+sd(s).en+" wall "+fq(w.q)+" at "+fp(w.p)+" ("+bp(Math.abs(w.p - mid)/mid)+" bp, resting "+fa(now - w.first)+(w.refills ? ", refilled "+w.refills+"x" : "")+")", ar:"أكبر حائط "+sd(s).ar+" "+fq(w.q)+" على "+fp(w.p)+" (بُعد "+bp(Math.abs(w.p - mid)/mid)+"bp، قاعد "+fa(now - w.first).replace(" s", " ث").replace(" m", " د")+(w.refills ? "، اتملى "+w.refills+"×" : "")+")"}); });
    const big = T.filter(x => now - x.t <= 60000).sort((a, b) => b.q - a.q)[0], mq = med(T.map(x => x.q));
    if (big && mq > 0 && big.q >= 6*mq) lines.push({sev:1, side:null, p:big.p, en:"Largest print: "+(big.side === "Buy" ? "buy" : "sell")+" "+fq(big.q)+" at "+fp(big.p)+" "+Math.round((now - big.t)/1000)+" s ago", ar:"أكبر صفقة: "+(big.side === "Buy" ? "شراء" : "بيع")+" "+fq(big.q)+" عند "+fp(big.p)+" من "+Math.round((now - big.t)/1000)+" ث"});
    const tk_ = tickOf((snap.bids || []).concat(snap.asks || []).map(x => x.p)) || mid*1e-4, Z = zonesOf(st, now, mid, tk_, evs, T);
    const tolZ = Math.max(3*tk_, mid*0.0003), inZone = l => l.p != null && Z.some(z => l.p >= z.lo - tolZ && l.p <= z.hi + tolZ);
    for (let i = lines.length - 1; i >= 0; i--) if (inZone(lines[i]) && lines[i].sev < 5) lines.splice(i, 1);   // the zone line already names these ingredients
    Z.forEach(z => lines.push({zone:true, sev:z.strength >= 3 ? 4.5 : 3.5, side:null, p:z.p, en:"Confluence at "+fp(z.p)+": "+zTxt(z, "en")+" ("+z.strength+" of 4 sources)", ar:"منطقة التقاء عند "+fp(z.p)+": "+zTxt(z, "ar")+" ("+z.strength+" من 4 مصادر)"}));
    if (!lines.length) lines.push({sev:0, side:null, p:null, en:"Quiet: no wall pulled or traded through, no absorption in the last 2 min", ar:"هادي: مفيش حائط اتسحب أو اتنفذ ومفيش امتصاص في آخر دقيقتين"});
    lines.sort((a, b) => b.sev - a.sev);
    return {tilt:{book, tape, lim, dir, label}, lines, facts:F, zones:Z};
  }
  // heat level 0..1 from a resting size: liquidity filter (hmCut = hide cells below this % of the biggest), colour ceiling (hmTop = % of the biggest that already gets the brightest colour), contrast (hmGam exponent, 0 = the site default `gam`), brightness (hmBri) and the old 'Heat x' (dom)
  const level = (q, mx, OF, gam) => {
    const top = Math.max(.05, (OF.hmTop || 100)/100), cut = Math.max(0, Math.min(.9, (OF.hmCut || 0)/100));
    let u = q/((mx || 1)*top); if (u > 1) u = 1; if (u <= cut) return 0; u = (u - cut)/(1 - cut);
    return Math.min(1, Math.pow(u, OF.hmGam || gam)*(OF.dom || 1)*(OF.hmBri || 1));
  };
  // confluence zones: where SEVERAL independent things happened at the same price in the last 2 minutes. Sources: book (a wall that rested >= 15 s), limits (a wall pulled after resting / traded through / refilled), tape (absorption-like), prints (a big print). 2+ sources = a zone of interest; it says WHERE to look, not which way price goes.
  function zonesOf(st, now, mid, tk, evs, trades){
    const tol = Math.max(3*tk, mid*0.0003), pts = [];
    st.walls.forEach(w => { if (now - w.first >= 15000 && Math.abs(w.p - mid)/mid <= 0.005) pts.push({p:w.p, src:"book", side:w.side, q:w.q}); });
    evs.forEach(e => { if (e.kind === "ABSORB") pts.push({p:e.p, src:"tape", side:e.side, q:e.q});
      else if (e.kind === "REFILL" || e.kind === "FILLED" || (e.kind === "PULLED" && e.age >= 8000)) pts.push({p:e.p, src:"limits", side:e.side, q:e.q, kind:e.kind}); });
    const mq = med(trades.map(x => x.q)); trades.forEach(x => { if (now - x.t <= 60000 && mq > 0 && x.q >= 6*mq) pts.push({p:x.p, src:"prints", side:x.side === "Buy" ? "ask" : "bid", q:x.q}); });
    pts.sort((a, b) => a.p - b.p); const groups = [];
    pts.forEach(x => { const g = groups[groups.length - 1]; if (g && x.p - g.hi <= tol && x.p - g.lo <= 2*tol){ g.items.push(x); g.hi = Math.max(g.hi, x.p); } else groups.push({lo:x.p, hi:x.p, items:[x]}); });
    return groups.map(g => { const srcs = [...new Set(g.items.map(i => i.src))], qs = g.items.reduce((a, i) => a + i.q, 0), p = g.items.reduce((a, i) => a + i.p*i.q, 0)/(qs || 1); return {p, lo:g.lo, hi:g.hi, srcs, strength:srcs.length, items:g.items}; })
      .filter(z => z.strength >= 2).sort((a, b) => b.strength - a.strength || b.items.length - a.items.length).slice(0, 3);
  }
  const zTxt = (z, lg) => z.srcs.map(s => { const it = z.items.filter(i => i.src === s);
    if (s === "book"){ const b = it.slice().sort((a, c) => c.q - a.q)[0]; return lg === "ar" ? "حائط "+(b.side === "bid" ? "شراء" : "بيع")+" "+fq(b.q) : (b.side === "bid" ? "bid" : "ask")+" wall "+fq(b.q); }
    if (s === "limits"){ const M = lg === "ar" ? {PULLED:"اتسحب", FILLED:"اتنفذ", REFILL:"إعادة ملء"} : {PULLED:"pulled", FILLED:"traded through", REFILL:"refill"}; return [...new Set(it.map(i => i.kind))].map(k => M[k]).join("/"); }
    if (s === "tape") return lg === "ar" ? "امتصاص محتمل" : "absorption-like";
    const pr = it.slice().sort((a, c) => c.q - a.q)[0]; return lg === "ar" ? "صفقة كبيرة "+(pr.side === "ask" ? "شراء" : "بيع")+" "+fq(pr.q) : "big "+(pr.side === "ask" ? "buy" : "sell")+" print "+fq(pr.q); }).join(" + ");
  return {newState, update, read, med, tickOf, level, zonesOf};
})();
/* Zone forward test (owner 2026-10-23): every confluence zone (2+ sources) is logged once per 5 min with its price; afterwards the price path decides what happened at it: 'hold' = after touching the level price moved >= RBP bp BACK to the side it came from, 'break' = it went >= RBP bp THROUGH. Every zone has a CONTROL level (the mirror price across the mid at creation: an arbitrary level at the same distance) tracked the same way, so a hold rate means something only against the control's. Direction-neutral on purpose: it asks "do these zones matter at all", not "which way". Pure; the page stores the records per symbol. */
const ZoneLog = (() => {
  const RBP = 6, TOUCH = 1.5, TTL = 900000, DEDUP = 300000;   // reaction 6 bp, touch = within 1.5 bp or crossed, 15 min life, the same zone is not re-logged for 5 min
  const track = () => ({touchT:0, out:null});
  function add(log, z, mid, now){
    if (log.recs.some(r => now - r.t < DEDUP && Math.abs(r.p - z.p)/mid*1e4 <= 4)) return null;
    const r = {t:now, p:z.p, strength:z.strength, srcs:z.srcs.slice(), mid0:mid, from:mid > z.p ? 1 : -1, ctl:2*mid - z.p, z:track(), c:track(), last:mid};
    log.recs.push(r); if (log.recs.length > 300) log.recs.splice(0, 50); return r;
  }
  function one(r, tr, L, from, mid){
    if (tr.out) return; const bp = x => x/mid*1e4;
    if (!tr.touchT){ const crossed = (r.last - L)*(mid - L) <= 0; if (Math.abs(bp(mid - L)) <= TOUCH || crossed) tr.touchT = 1; else return; }
    const d = bp((mid - L)*from);   // + = back on the side price came from (a hold), - = through the level
    if (d >= RBP) tr.out = "hold"; else if (d <= -RBP) tr.out = "break";
  }
  function step(log, mid, now){ log.recs.forEach(r => { if (r.done) return; if (now - r.t > TTL){ r.done = true; return; } one(r, r.z, r.p, r.from, mid); one(r, r.c, r.ctl, -r.from, mid); r.last = mid; }); }
  function stats(log){
    const S = {n:log.recs.length, z:{touch:0, hold:0, brk:0}, c:{touch:0, hold:0, brk:0}, pair:0, diff:0, t:0}, ds = [];
    log.recs.forEach(r => { [["z", r.z], ["c", r.c]].forEach(([k, tr]) => { if (tr.touchT) S[k].touch++; if (tr.out === "hold") S[k].hold++; else if (tr.out === "break") S[k].brk++; });
      if (r.z.out && r.c.out) ds.push((r.z.out === "hold" ? 1 : 0) - (r.c.out === "hold" ? 1 : 0)); });
    S.pair = ds.length; if (ds.length > 1){ const m = ds.reduce((a, b) => a + b, 0)/ds.length, sd = Math.sqrt(ds.reduce((a, b) => a + (b - m)*(b - m), 0)/(ds.length - 1)); S.diff = +m.toFixed(3); S.t = sd > 0 ? +(m/(sd/Math.sqrt(ds.length))).toFixed(2) : 0; }
    return S;
  }
  return {add, step, stats, RBP, TTL};
})();
/* FLOWREAD:END */
const exportZoneLog = ch => { const zl = ch.zlog || {recs:store.get(LS+"_zlog_"+ch.sym, [])}, blob = new Blob([JSON.stringify({sym:ch.sym, built:Date.now(), rbp:ZoneLog.RBP, ttl:ZoneLog.TTL, recs:zl.recs})], {type:"application/json"}), a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = "zone_log_"+ch.sym+".json"; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 2000); };   // the zone forward-test records, judged offline by modules/zone_eval.py
