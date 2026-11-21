/* ---- ORDER FLOW DESK (owner 2026-11-08 minutes, Grok plan; Claude build 2026-11-09). One widget that reads the linked chart and puts the
   desk's agents side by side: 1 level scanner (previous day / week high-low, today's open, volume profile POC / VAH / VAL), 2 context (bias,
   regime, ATR), 3+4 order-flow read (Flow confluence v1 = 3 of 4: stacked imbalance, delta, tape, absorption - needs Footprint on the chart),
   5 risk manager (0.25 % base; 0.50 % only for validated A+ with n >= 30; 2 % daily cap, lock after 3 stops, R:R >= 2), 6 skeptic (every
   reason NOT to take it). Description, not advice: nothing here places an order; under 30 journal trades nothing here is evidence. ---- */
/* DESK-BEGIN pure engine (no DOM, no fetch): tests/test_desk_js.py runs it with node on synthetic candles */
const DESK = {
  RULES: {risk:0.25, day:2, stops:3, rr:2},
  riskFor(grade, validationN, validationPassed){ return grade === "A+" && validationPassed === true && Number.isInteger(validationN) && validationN >= 30 ? 0.5 : 0.25; },
  atr(rows, n){ n = Math.min(n || 14, rows.length - 1); if (n < 1) return 0; let s = 0;
    for (let i = rows.length - n; i < rows.length; i++) s += Math.max(rows[i].h - rows[i].l, Math.abs(rows[i].h - rows[i-1].c), Math.abs(rows[i].l - rows[i-1].c)); return s/n; },
  // high / low of the last COMPLETE period before the current one (UTC day or UTC week starting Monday) + the current period's open
  period(rows, ms, offset){ if (!rows.length) return null; const key = t => Math.floor((t - (offset || 0))/ms), cur = key(rows[rows.length-1].t);
    let hi = -Infinity, lo = Infinity, prevKey = null, open = null;
    for (let i = rows.length - 1; i >= 0; i--){ const k = key(rows[i].t);
      if (k === cur){ open = rows[i].o; continue; }
      if (prevKey == null) prevKey = k; if (k !== prevKey) break; if (rows[i].h > hi) hi = rows[i].h; if (rows[i].l < lo) lo = rows[i].l; }
    return isFinite(hi) ? {hi, lo, open} : {hi:null, lo:null, open}; },
  // volume profile of the candles: each candle's volume spread evenly over its high-low range; POC = fullest bin, value area = 70 % around it
  vp(rows, bins){ bins = bins || 40; if (rows.length < 5) return null; let lo = Infinity, hi = -Infinity; rows.forEach(r => { if (r.l < lo) lo = r.l; if (r.h > hi) hi = r.h; });
    if (!(hi > lo)) return null; const w = (hi - lo)/bins, v = new Array(bins).fill(0);
    rows.forEach(r => { const vol = +r.v || 0; if (!(vol > 0)) return; const a = Math.max(0, Math.min(bins - 1, Math.floor((r.l - lo)/w))), b = Math.max(0, Math.min(bins - 1, Math.floor((r.h - lo)/w)));
      for (let k = a; k <= b; k++) v[k] += vol/(b - a + 1); });
    const tot = v.reduce((s, x) => s + x, 0); if (!(tot > 0)) return null;
    let p = 0; for (let k = 1; k < bins; k++) if (v[k] > v[p]) p = k;
    let a = p, b = p, acc = v[p];
    while (acc < 0.7*tot && (a > 0 || b < bins - 1)){ const dn = a > 0 ? v[a-1] : -1, up = b < bins - 1 ? v[b+1] : -1; if (up >= dn){ b++; acc += v[b]; } else { a--; acc += v[a]; } }
    const mid = k => lo + (k + 0.5)*w; return {poc:mid(p), vah:lo + (b + 1)*w, val:lo + a*w}; },
  // agent 1: every level with its name, nearest first relative to px (dist in ATR)
  levels(rows){ if (!rows || rows.length < 20) return {px:null, atr:0, list:[]}; const px = rows[rows.length-1].c, a = this.atr(rows, 14) || px*0.001, L = [];
    const d = this.period(rows, 86400000, 0), wk = this.period(rows, 604800000, 345600000);   // 1970-01-01 was a Thursday: +4 days = Monday weeks
    if (d){ if (d.hi != null){ L.push({p:d.hi, k:"PDH"}); L.push({p:d.lo, k:"PDL"}); } if (d.open != null) L.push({p:d.open, k:"DO"}); }
    if (wk && wk.hi != null){ L.push({p:wk.hi, k:"PWH"}); L.push({p:wk.lo, k:"PWL"}); }
    const v = this.vp(rows.slice(-300)); if (v){ L.push({p:v.poc, k:"POC"}); L.push({p:v.vah, k:"VAH"}); L.push({p:v.val, k:"VAL"}); }
    L.forEach(l => { l.dist = (l.p - px)/a; }); L.sort((x, y) => Math.abs(x.dist) - Math.abs(y.dist));
    return {px, atr:a, list:L, above:L.filter(l => l.p > px).sort((x, y) => x.p - y.p), below:L.filter(l => l.p < px).sort((x, y) => y.p - x.p)}; },
  // agent 5: same math as modules/desk_risk.py position_size / reward_risk
  size(eq, entry, stop, riskPct, pv, step){ const rp = riskPct == null ? this.RULES.risk : +riskPct, per = Math.abs(entry - stop)*(pv || 1);
    if (!(eq > 0) || !(rp > 0) || !(per > 0)) return {qty:0, risk:0, per:0, pct:0};
    let q = eq*rp/100/per; if (step > 0) q = Math.floor(q/step + 1e-9)*step; return {qty:q, risk:q*per, per, pct:q*per/eq*100}; },
  rr(entry, stop, target){ const r = Math.abs(entry - stop); if (!(r > 0)) return 0; return (stop < entry ? target - entry : entry - target)/r; },
  // Closed journal R is converted per trade using its recorded riskPct; legacy records safely default to base risk.
  day(trades, now, rules){ rules = rules || this.RULES; const d0 = Math.floor(now/86400000)*86400000;
    const done = (trades || []).filter(t => (t.status === "tp" || t.status === "sl") && (+t.t1 || +t.t0 || 0) >= d0);
    const R = done.reduce((s, t) => s + (+t.r || 0), 0), stops = done.filter(t => t.status === "sl" || (+t.r || 0) < 0).length;
    const netPct = done.reduce((s, t) => { const rp = typeof t.riskPct === "number" && Number.isFinite(t.riskPct) && t.riskPct > 0 ? t.riskPct : rules.risk; return s - (+t.r || 0)*rp; }, 0);
    return {n:done.length, stops, R, lossPct:Math.max(0, netPct)}; },
  // allowed / blocked, every failed rule listed (same rules as DeskDay.check)
  check(plan, dayS, rules, openSame){ rules = rules || this.RULES; const why = [];
    if (dayS.stops >= rules.stops) why.push(["stops", dayS.stops+" stops today (limit "+rules.stops+") - day locked", dayS.stops+" ستوب النهارده (الحد "+rules.stops+") - اليوم اتقفل"]);
    if (dayS.lossPct >= rules.day - 1e-9) why.push(["day", "daily loss "+dayS.lossPct.toFixed(2)+"% >= "+rules.day+"% - day locked", "خسارة اليوم "+dayS.lossPct.toFixed(2)+"% >= "+rules.day+"% - اليوم اتقفل"]);
    else if (plan.riskPct > rules.day - dayS.lossPct + 1e-9) why.push(["left", "risk "+plan.riskPct.toFixed(2)+"% > what is left of today's cap "+(rules.day - dayS.lossPct).toFixed(2)+"%", "المخاطرة "+plan.riskPct.toFixed(2)+"% أكبر من الباقي من حد اليوم "+(rules.day - dayS.lossPct).toFixed(2)+"%"]);
    const rr = this.rr(plan.entry, plan.stop, plan.target); if (rr < rules.rr - 1e-9) why.push(["rr", "reward:risk "+rr.toFixed(2)+" < "+rules.rr, "العائد للمخاطرة "+rr.toFixed(2)+" أقل من "+rules.rr]);
    const perTradeCap = typeof plan.riskCapPct === "number" && Number.isFinite(plan.riskCapPct) && plan.riskCapPct > 0 ? plan.riskCapPct : rules.risk;
    if (plan.riskPct > perTradeCap*1.0001) why.push(["cap", "risk "+plan.riskPct.toFixed(2)+"% > per-trade cap "+perTradeCap+"%", "المخاطرة "+plan.riskPct.toFixed(2)+"% أكبر من حد الصفقة "+perTradeCap+"%"]);
    if (openSame) why.push(["dup", "the same trade is already open in the journal", "نفس الصفقة مفتوحة في الجورنال"]);
    return {ok:!why.length, why, rr}; }
};
/* DESK-END */
Panel.prototype.build_ofdesk = function(){
  const S = this.state.od = Object.assign({eq:10000, pv:1, step:0, side:"auto", sym:""}, this.state.od || {});
  if (!document.getElementById("odCss")){ const st = el("style"); st.id = "odCss"; st.textContent =
    ".odw{font-size:12px;line-height:1.5}.odw .tb{display:flex;flex-wrap:wrap;gap:4px;align-items:center;margin-bottom:4px}.odw .tb input{width:86px}.odw .tb select,.odw .tb button,.odw .tb input{font-size:12px}"
    +".odw .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:6px}.odw .ag{border:1px solid var(--line);border-radius:7px;padding:6px 8px;border-top:3px solid var(--ac)}"
    +".odw .ah{font-weight:800;font-size:11px;color:var(--ac);letter-spacing:.04em;text-transform:uppercase;margin-bottom:3px}.odw table{width:100%;border-collapse:collapse}.odw td{padding:1px 3px}.odw td.r{text-align:end;font-family:ui-monospace,Menlo,Consolas,monospace}"
    +".odw .g{color:#0ecb81}.odw .rd{color:#f6465d}.odw .y{color:#f0b90b}.odw .m{color:var(--mut)}.odw .vd{font-weight:800;padding:1px 8px;border-radius:4px;color:#0b0e11}.odw ul{margin:2px 0;padding-inline-start:16px}";
    document.head.append(st); }
  this.body.classList.add("odw"); this.body.style.overflow = "auto";
  const stop_ = x => { x.onpointerdown = e => e.stopPropagation(); return x; }, num = (v, d) => { const n = parseFloat(v); return isFinite(n) ? n : d; };
  const charts = () => Ws.panels.filter(p => p.type === "chart" && p.chart), pick = () => { const C = charts(); return C.find(p => p.state.sym === S.sym && p.chart.data.length) || C.find(p => p.chart.data.length) || C[0] || null; };
  const tb = el("div","tb"), symSel = stop_(el("select")), sideSel = stop_(el("select")), eqI = stop_(el("input")), pvI = stop_(el("input")), enI = stop_(el("input")), slI = stop_(el("input")), tpI = stop_(el("input")), shB = stop_(el("button", null, "📈 "+Lg("Show on chart","اعرضها على الشارت")));
  [["auto",Lg("Side: auto (bias)","الاتجاه: تلقائي (الترند)")],["long",Lg("Long","شراء")],["short",Lg("Short","بيع")]].forEach(([v, l]) => sideSel.append(Object.assign(el("option"), {value:v, textContent:l}))); sideSel.value = S.side;
  eqI.type = pvI.type = enI.type = slI.type = tpI.type = "number"; eqI.step = "any"; pvI.step = "any"; enI.step = slI.step = tpI.step = "any";
  eqI.value = S.eq; pvI.value = S.pv; eqI.title = Lg("Account equity","رأس مال الحساب"); pvI.title = Lg("Money per 1.0 price move per unit (1 spot, 50 ES, 20 NQ)","قيمة حركة 1 في السعر للوحدة (1 سبوت، 50 ES، 20 NQ)");
  enI.placeholder = Lg("entry (auto)","دخول (تلقائي)"); slI.placeholder = Lg("stop (auto)","ستوب (تلقائي)"); tpI.placeholder = Lg("target (auto)","هدف (تلقائي)");
  const lab = t => el("span","m", esc(t));
  tb.append(symSel, sideSel, lab(Lg("equity","رأس المال")), eqI, lab(Lg("pt value","قيمة النقطة")), pvI, enI, slI, tpI, shB);
  const head = el("div"), grid = el("div","grid"), foot = el("div","m"); this.body.append(tb, head, grid, foot);
  foot.style.marginTop = "6px"; foot.textContent = Lg("Description, not advice: nothing here places an order. Mock-tested only; under 30 journal trades nothing here is evidence.","وصف مش نصيحة: مفيش أي أمر بيتبعت من هنا. متجرب على بيانات وهمية بس؛ أقل من 30 صفقة في الجورنال = مش دليل.");
  const save = () => { S.eq = num(eqI.value, S.eq); S.pv = num(pvI.value, 1) || 1; S.side = sideSel.value; S.sym = symSel.value; Ws.save(); draw(); };
  [eqI, pvI].forEach(i => i.onchange = save); sideSel.onchange = () => { enI.value = slI.value = tpI.value = ""; save(); }; symSel.onchange = () => { enI.value = slI.value = tpI.value = ""; save(); }; [enI, slI, tpI].forEach(i => i.oninput = () => draw());
  let last = null;
  const ag = (col, title, html) => '<div class="ag" style="--ac:'+col+'"><div class="ah">'+esc(title)+'</div>'+html+'</div>';
  const draw = () => {
    const C = charts(), syms = [...new Set(C.map(p => p.state.sym))]; if (symSel.options.length !== syms.length || [...symSel.options].some((o, i) => o.value !== syms[i])){ symSel.innerHTML = ""; syms.forEach(s => symSel.append(Object.assign(el("option"), {value:s, textContent:s.replace(/^HL:xyz:|^Y:|-USDT.*$/g, "")}))); }
    const P = pick(); if (P) symSel.value = P.state.sym;
    if (!P || !P.chart.data.length){ head.innerHTML = '<div class="m" style="padding:8px">'+esc(Lg("Open a chart first: the desk reads the chart's candles (and its footprint for the order-flow read).","افتح شارت الأول: الديسك بيقرا شموع الشارت (والفوت برينت بتاعه لقراءة الأوردر فلو)."))+'</div>'; grid.innerHTML = ""; return; }
    const ch = P.chart, rows = ch.data, sym = P.state.sym, tf = P.state.tf, Lv = DESK.levels(rows), px = Lv.px, a = Lv.atr;
    let bias = {available:false}; try { bias = TCE.bias(rows); } catch(e){}
    let reg = null; try { reg = (Regime.of(rows) || {}).regime || null; } catch(e){}
    let fc = null; try { fc = Ws.flowConf(sym); } catch(e){}
    let nw = null; try { nw = Ctx.news(sym); } catch(e){}
    const side = S.side === "long" ? 1 : S.side === "short" ? -1 : bias.bias === "bull" ? 1 : bias.bias === "bear" ? -1 : (fc && fc.dir) || 1;
    // auto plan: entry = price, stop = beyond the nearest level on the other side (+0.25 ATR) or 1 ATR, target = the next level in our direction (or 2R)
    const opp = side > 0 ? Lv.below[0] : Lv.above[0], nxt = (side > 0 ? Lv.above : Lv.below).find(l => Math.abs(l.p - px) >= 0.5*a);
    const aE = px, aS = opp && Math.abs(opp.p - px) <= 2*a ? opp.p - side*0.25*a : px - side*a, aT = nxt ? nxt.p : px + side*2*Math.abs(px - aS);
    const E = num(enI.value, aE), SL = num(slI.value, aS), TP = num(tpI.value, aT), riskPct = DESK.riskFor(null, 0, false), sz = DESK.size(S.eq, E, SL, riskPct, S.pv, S.step);
    const dayS = DESK.day(Journal.list, Date.now(), DESK.RULES), dirT = side > 0 ? "bullish" : "bearish";
    const openSame = (Journal.list || []).some(t => t.status === "open" && t.symbol === sym && t.dir === dirT);
    const rules = DESK.RULES, chk = DESK.check({entry:E, stop:SL, target:TP, riskPct:sz.pct, riskCapPct:riskPct}, dayS, rules, openSame);
    // agent 6: the skeptic - every reason against
    const skp = [];
    if (bias.available && ((side > 0 && bias.bias === "bear") || (side < 0 && bias.bias === "bull"))) skp.push(Lg("against the chart's bias ("+bias.trend+", price "+bias.ema+" EMA50)","عكس اتجاه الشارت ("+bias.trend+"، السعر "+(bias.ema === "above" ? "فوق" : "تحت")+" EMA50)"));
    if (reg && /vol|chop/i.test(reg)) skp.push(Lg("regime: "+reg+" - stops get hit more","الريجيم: "+reg+" - الستوبات بتضرب أكتر"));
    if (!fc) skp.push(Lg("no order-flow read: turn Footprint on in this chart","مفيش قراءة أوردر فلو: شغّل الفوت برينت في الشارت ده"));
    else if (fc.n < 3) skp.push(Lg("order flow: only "+fc.n+" of 4 (needs 3, level first)","الأوردر فلو: "+fc.n+" من 4 بس (محتاج 3، والمستوى أولًا)"));
    else if (fc.dir !== side) skp.push(Lg("order flow points the other way","الأوردر فلو بيشاور الناحية التانية"));
    if (Lv.list.length && Math.abs(Lv.list[0].dist) > 1) skp.push(Lg("price is not at a level (nearest "+Lv.list[0].k+" "+Math.abs(Lv.list[0].dist).toFixed(1)+" ATR away): order flow alone is not a signal","السعر مش عند مستوى (أقرب "+Lv.list[0].k+" على بعد "+Math.abs(Lv.list[0].dist).toFixed(1)+" ATR): الأوردر فلو لوحده مش إشارة"));
    if (nw) skp.push(Lg("news: ","خبر: ")+(nw.country || "")+" "+(nw.title || ""));
    chk.why.forEach(w => skp.push(lang === "ar" ? w[2] : w[1]));
    const verdict = !chk.ok ? "SKIP" : skp.length ? "WAIT" : "TAKE", VC = {TAKE:"#0ecb81", WAIT:"#f0b90b", SKIP:"#848e9c"}, VT = {TAKE:Lg("TAKE","ادخل"), WAIT:Lg("WAIT","استنى"), SKIP:Lg("SKIP","ماتدخلش")};
    last = {sym, side, E, SL, TP, tf};
    head.innerHTML = '<b style="font-size:14px">'+esc(sym.replace(/^HL:xyz:|^Y:|-USDT.*$/g, ""))+'</b> '+esc(tf)+' · '+fmtP(px)+' · ATR '+fmtP(a)+' · <b style="color:'+(side > 0 ? "#0ecb81" : "#f6465d")+'">'+(side > 0 ? "▲ "+esc(Lg("Long","شراء")) : "▼ "+esc(Lg("Short","بيع")))+'</b> · <span class="vd" style="background:'+VC[verdict]+'">'+VT[verdict]+'</span>';
    const lvRows = Lv.list.slice(0, 8).map(l => '<tr><td><b>'+l.k+'</b></td><td class="r">'+fmtP(l.p)+'</td><td class="r '+(l.p > px ? "rd" : "g")+'">'+(l.dist >= 0 ? "+" : "")+l.dist.toFixed(1)+' ATR</td></tr>').join("");
    const fcHtml = !fc ? '<div class="m">'+esc(Lg("Footprint is off on this chart: turn it on (Indicators → Footprint) to read stacked imbalance, delta, tape and absorption.","الفوت برينت مقفول في الشارت ده: شغّله (المؤشرات ← Footprint) عشان يقرا الإمبالانس والدلتا والتايب والامتصاص."))+'</div>'
      : '<div><b class="'+(fc.n >= 3 ? "g" : "y")+'">'+fc.n+' / 4</b> '+(fc.dir ? (fc.dir > 0 ? "▲" : "▼") : "")+'</div><div>'+["level","delta","tape","absorb"].map(k => (fc.parts.includes(k) ? '<b class="g">✓</b> ' : '<span class="m">✗</span> ')+esc({level:Lg("stacked imbalance level","مستوى إمبالانس متراكم"), delta:Lg("candle delta","دلتا الشمعة"), tape:Lg("tape 60 s > 55 %","التايب 60 ث > 55%"), absorb:Lg("absorption 2 min","امتصاص 2 دقيقة")}[k])).join("<br>")+'</div>';
    grid.innerHTML =
      ag("#4aa3ff", Lg("1 · Level scanner","1 · ماسح المستويات"), Lv.list.length ? '<table>'+lvRows+'</table><div class="m">'+esc(Lg("PDH/PDL = previous UTC day, PWH/PWL = previous week, DO = today's open, POC/VAH/VAL = volume profile of the loaded candles","PDH/PDL = اليوم السابق UTC، PWH/PWL = الأسبوع السابق، DO = فتح النهارده، POC/VAH/VAL = بروفايل الحجم للشموع المحملة"))+'</div>' : '<div class="m">'+esc(Lg("needs 20+ candles","محتاج 20 شمعة على الأقل"))+'</div>')
      + ag("#b57cff", Lg("2 · Context","2 · السياق"), '<div>'+esc(Lg("Bias","الاتجاه"))+': <b>'+(bias.available ? esc(bias.bias+" · "+bias.trend+" · "+bias.ema+" EMA50") : "–")+'</b></div><div>'+esc(Lg("Regime","الريجيم"))+': <b>'+esc(reg || "–")+'</b></div><div>ATR 14: <b>'+fmtP(a)+'</b></div>'+(nw ? '<div class="rd">⚠ '+esc((nw.country || "")+" "+(nw.title || ""))+'</div>' : '<div class="m">'+esc(Lg("no high-impact news now","مفيش أخبار قوية دلوقتي"))+'</div>'))
      + ag("#0ecb81", Lg("3+4 · Order-flow read (3 of 4)","3+4 · قراءة الأوردر فلو (3 من 4)"), fcHtml)
      + ag("#f0b90b", Lg("5 · Risk manager","5 · مدير المخاطرة"), '<table><tr><td>'+esc(Lg("Entry","دخول"))+'</td><td class="r">'+fmtP(E)+'</td></tr><tr><td>'+esc(Lg("Stop","ستوب"))+'</td><td class="r rd">'+fmtP(SL)+'</td></tr><tr><td>'+esc(Lg("Target","هدف"))+'</td><td class="r g">'+fmtP(TP)+'</td></tr>'
          +'<tr><td>'+esc(Lg("Risk tier","شريحة المخاطرة"))+'</td><td class="r">'+riskPct.toFixed(2)+'%</td></tr><tr><td>R:R</td><td class="r"><b class="'+(chk.rr >= rules.rr ? "g" : "rd")+'">'+chk.rr.toFixed(2)+'</b></td></tr><tr><td>'+esc(Lg("Size","الحجم"))+'</td><td class="r"><b>'+(sz.qty ? +sz.qty.toPrecision(4) : 0)+'</b></td></tr><tr><td>'+esc(Lg("Risk","المخاطرة"))+'</td><td class="r">'+sz.risk.toFixed(2)+' ('+sz.pct.toFixed(2)+'%)</td></tr>'
          +'<tr><td>'+esc(Lg("Today","النهارده"))+'</td><td class="r">'+dayS.n+' '+esc(Lg("closed","مقفولة"))+' · '+dayS.stops+'/'+rules.stops+' '+esc(Lg("stops","ستوب"))+' · −'+dayS.lossPct.toFixed(2)+'% / '+rules.day+'%</td></tr></table>'
          +'<div>'+(chk.ok ? '<b class="g">✓ '+esc(Lg("rules OK","القواعد تمام"))+'</b>' : chk.why.map(w => '<div class="rd">⛔ '+esc(lang === "ar" ? w[2] : w[1])+'</div>').join(""))+'</div>')
      + ag("#f6465d", Lg("6 · Skeptic: why NOT","6 · المتشكك: ليه لأ"), skp.length ? '<ul>'+skp.map(s => '<li>'+esc(s)+'</li>').join("")+'</ul>' : '<div class="g">'+esc(Lg("nothing against found - still not evidence under 30 trades","مفيش اعتراض - برضه مش دليل تحت 30 صفقة"))+'</div>');
  };
  shB.onclick = () => { if (!last) return; const long_ = last.side > 0; try { Ws.showOnChart({symbol:last.sym, direction:long_ ? "bullish" : "bearish", ttype:"Desk", tfk:String(last.tf || "").toLowerCase(), tfc:last.tf, score:0, max:10, src:"ofdesk",
      plan:{entry:last.E, stop:last.SL, tps:[last.TP]}, zones:[], tags:[], ana:{sig:[Lg("Order Flow Desk plan (not advice)","خطة الأوردر فلو ديسك (مش نصيحة)")]}}); } catch(e){ console.warn("ofdesk showOnChart", e); } };
  draw(); const iv = setInterval(() => { if (!document.hidden) draw(); }, 2000);
  this.unwatch = () => clearInterval(iv);
};
