/* a tab in the background is throttled by the browser (timers, sockets); when it comes back or the network returns, restart the charts and recycle stale sockets */
{ let lastWake = 0;
  const wake = () => { if (document.hidden || Date.now() - lastWake < 3000) return; lastWake = Date.now();
    try { Object.values(WSX.conns).forEach(c => { if (c.ws && (c.ws.readyState > 1 || (c.last && Date.now() - c.last > 30000))) try { c.ws.close(); } catch(e){} }); } catch(e){}
    try { Ws.panels.forEach(p => { if (p.type === "chart" && p.kick && (!p._okAt || Date.now() - p._okAt > 15000 || !p.chart.data.length)) p.kick(); }); } catch(e){} };
  document.addEventListener("visibilitychange", wake); window.addEventListener("focus", wake); window.addEventListener("online", wake); window.addEventListener("pageshow", wake); }
/* ---------------- widget panels ---------------- */
const Ws = { panels:[], z:10, el:null, seq:1 };

// phones / small tablets (the Streamlit iframe is as wide as the screen): stacked layout + touch gestures
const MOB = (() => { try { return /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent) || (matchMedia("(pointer:coarse)").matches && window.innerWidth < 1100); } catch(e){ return false; } })();   // phones and tablets only: a narrow desktop window keeps the desktop layout (width alone switched it, 2026-10-19)
const TCH = (() => { try { return navigator.maxTouchPoints > 0 || matchMedia("(pointer:coarse)").matches; } catch(e){ return false; } })();   // a touch screen (iPadOS reports a Mac user agent, so this does not rely on the user agent)
const TAB = TCH && (() => { try { return Math.min(screen.width, screen.height) >= 600 || Math.min(innerWidth, innerHeight) >= 600; } catch(e){ return false; } })();   // tablet-sized touch screen: the chart keeps every gesture (phones keep the page scroll in the stacked layout)
let MT5 = MOB && store.get(LS+"_mt5", !TAB) !== false;   // tablets: the full workspace by default (the phone MetaTrader layout hides the toolbar); a phone keeps MT5 on. The choice is remembered either way
//   // phones: MetaTrader-style layout (option, on by default; the bar button switches it)
const mobH = type => { const sh = Math.min((window.screen && screen.availHeight) || 800, 1000); return Math.round(sh*(type === "chart" || type === "tvc" ? .72 : type === "dom" || type === "tape" || type === "limits" ? .6 : .5)); };
class Panel {
  constructor(type, rect, state){
    this.type = type; this.id = "p"+(Ws.seq++); this.state = Object.assign({sym:SYMS[0], group:0}, state||{});
    this.rect = Object.assign({x:20,y:20,w:360,h:280}, rect||{}); this.min = !!this.state.min; this.max = false; this.unsubs = [];
    this.root = el("div","panel");
    this.head = el("div","ph"); this.ttl = el("span","ttl"); this.head.append(this.ttl);
    this.grp = el("select"); this.grp.title = T("group");
    ["—",1,2,3].forEach((g,i) => { const o = el("option"); o.value = i; o.textContent = i ? "#"+i : "—"; this.grp.append(o); });
    this.grp.value = this.state.group; this.grp.onchange = () => { this.state.group = +this.grp.value; Ws.save(); };
    this.grp.onpointerdown = e => e.stopPropagation();
    const bLock = el("button",null,"🔓"); bLock.title = Lg("Lock: freeze this widget in place (no move, resize or close) until you unlock it","قفل: تثبيت الويدجت في مكانه (ما يتحركش، ما يتكبرش، ما يتقفلش) لحد ما تفك القفل");
    this.locked = !!this.state.lock2; this.applyLock = () => { this.root.classList.toggle("locked", this.locked); bLock.textContent = this.locked ? "🔒" : "🔓"; bLock.classList.toggle("on", this.locked); };
    bLock.onpointerdown = e => e.stopPropagation(); bLock.onclick = () => { this.locked = !this.locked; this.state.lock2 = this.locked || undefined; this.applyLock(); Ws.save(); };
    const bMin = el("button",null,"–"), bMax = el("button",null,"▢"), bX = el("button",null,"✕");
    [bMin,bMax,bX].forEach(b => b.onpointerdown = e => e.stopPropagation());
    bMin.onclick = () => { this.min = !this.min; this.state.min = this.min; this.root.classList.toggle("min", this.min); Ws.save(); };
    bMax.onclick = () => this.toggleMax(); bX.onclick = () => { if (!this.locked) this.close(); };
    // per-widget colours: header/border accent + body tint (saved with the layout)
    const mkCol = (title, key) => { const i = el("input"); i.type = "color"; i.title = title; i.className = "pc"; i.value = this.state[key] || (key === "col" ? "#1e2329" : "#0b0e11");
      i.onpointerdown = e => e.stopPropagation(); i.oninput = () => { this.state[key] = i.value; this.paint(); }; i.onchange = () => Ws.save(); return i; };
    const rc = el("button",null,"↺"); rc.title = Lg("reset colours","رجّع الألوان"); rc.onpointerdown = e => e.stopPropagation();
    rc.onclick = () => { delete this.state.col; delete this.state.bg; this.paint(); Ws.save(); };
    this.head.append(bLock, mkCol(Lg("header colour","لون العنوان"),"col"), mkCol(Lg("background colour","لون الخلفية"),"bg"), rc, this.grp, bMin, bMax, bX); this.applyLock();
    this.body = el("div","pb"); this.rz = el("div","rz");
    this.root.append(this.head, this.body, this.rz);
    // resize from every side and corner (thin invisible grips on the border; the old corner grip stays)
    this.rzs = ["n","s","e","w","ne","nw","se","sw"].map(d => { const g = el("div","rzh rz-"+d); g.dataset.d = d; this.root.append(g); return g; });
    Ws.el.append(this.root); Ws.panels.push(this);
    this.apply(); this.paint(); this.root.classList.toggle("min", this.min);
    this.bindDrag(); this.setTitle(); this.build();
    this.root.addEventListener("pointerdown", () => this.front(), true); this.front();
  }
  setTitle(){ { const hasS = ["chart","dom","tape","limits","ofm","fund","liq","posn","tvc"].includes(this.type); this.ttl.innerHTML = esc(T(this.type)) + (hasS ? " · "+symIcon(this.state.sym, 14)+esc(this.state.sym) : ""); } this.grp.title = T("group"); }
  paint(){ const c = this.state.col, b = this.state.bg;
    this.head.style.background = c || ""; this.root.style.borderColor = c || ""; this.body.style.background = b || ""; }
  front(){ this.root.style.zIndex = ++Ws.z; Ws.panels.forEach(p => p.root.classList.toggle("focus", p === this)); }
  apply(){ const r = this.rect, s = this.root.style; if (MOB){ s.height = MT5 ? "" : (this.max ? Math.round(mobH("chart")*1.25) : mobH(this.type))+"px"; return; }   // phones: MT5 = one widget fills the screen (CSS .mact); else stacked   // mobile: stacked, own height (desktop rects kept for the desktop)
    s.left = r.x+"px"; s.top = r.y+"px"; s.width = r.w+"px"; s.height = r.h+"px"; }
  toggleMax(){
    if (MOB && MT5) return;   // phones, MT5 layout: the widget is already full screen
    if (MOB){ this.max = !this.max; this.apply(); this.root.scrollIntoView({block:"start"}); return; }
    if (!this.max){ this.prev = Object.assign({}, this.rect); this.rect = {x:0,y:0,w:Ws.el.clientWidth,h:Ws.el.clientHeight}; this.max = true; this.min = false; this.root.classList.remove("min"); }
    else { this.rect = this.prev; this.max = false; }
    this.apply(); this.front(); Ws.save();
  }
  bindDrag(){
    const snap = v => Math.round(v/10)*10;
    this.head.addEventListener("pointerdown", e => {
      if (this.max || MOB || this.locked) return;   // mobile: no dragging (stacked layout; a finger on the title bar scrolls the page)
      this.head.setPointerCapture(e.pointerId); this.root.classList.add("drag");
      const sx = e.clientX, sy = e.clientY, ox = this.rect.x, oy = this.rect.y;
      const mv = ev => {
        this.rect.x = Math.max(-this.rect.w+80, Math.min(Ws.el.clientWidth-60, snap(ox+ev.clientX-sx)));
        this.rect.y = Math.max(0, Math.min(Ws.el.clientHeight-26, snap(oy+ev.clientY-sy))); this.apply();
      };
      const up = () => { this.head.removeEventListener("pointermove", mv); this.head.removeEventListener("pointerup", up); this.head.removeEventListener("pointercancel", up); this.root.classList.remove("drag"); Ws.save(); };
      this.head.addEventListener("pointermove", mv); this.head.addEventListener("pointerup", up); this.head.addEventListener("pointercancel", up);
    });
    this.head.addEventListener("dblclick", () => this.toggleMax());
    this.rzs.forEach(g => g.addEventListener("pointerdown", e => {   // edge / corner grips: n s e w ne nw se sw
      if (this.max || MOB) return; e.stopPropagation(); g.setPointerCapture(e.pointerId); this.root.classList.add("drag"); this.front();
      const d = g.dataset.d, sx = e.clientX, sy = e.clientY, o = Object.assign({}, this.rect), MW = 160, MH = 90;
      const mv = ev => { const dx = ev.clientX - sx, dy = ev.clientY - sy, r = this.rect;
        if (d.includes("e")) r.w = Math.max(MW, snap(o.w + dx));
        if (d.includes("s")) r.h = Math.max(MH, snap(o.h + dy));
        if (d.includes("w")){ const w = Math.max(MW, snap(o.w - dx)); r.x = o.x + o.w - w; r.w = w; }
        if (d.includes("n")){ const h = Math.max(MH, snap(o.h - dy)), y = Math.max(0, o.y + o.h - h); r.h = o.y + o.h - y; r.y = y; }
        this.apply(); };
      const up = () => { g.removeEventListener("pointermove", mv); g.removeEventListener("pointerup", up); g.removeEventListener("pointercancel", up); this.root.classList.remove("drag"); this.max = false; Ws.save(); };
      g.addEventListener("pointermove", mv); g.addEventListener("pointerup", up); g.addEventListener("pointercancel", up); }));
    this.rz.addEventListener("pointerdown", e => { if (this.locked) return;
      e.stopPropagation(); this.rz.setPointerCapture(e.pointerId); this.root.classList.add("drag");
      const sx = e.clientX, sy = e.clientY, ow = this.rect.w, oh = this.rect.h;
      const mv = ev => { this.rect.w = Math.max(160, snap(ow+ev.clientX-sx)); this.rect.h = Math.max(90, snap(oh+ev.clientY-sy)); this.apply(); };
      const up = () => { this.rz.removeEventListener("pointermove", mv); this.rz.removeEventListener("pointerup", up); this.rz.removeEventListener("pointercancel", up); this.root.classList.remove("drag"); this.max = false; Ws.save(); };
      this.rz.addEventListener("pointermove", mv); this.rz.addEventListener("pointerup", up); this.rz.addEventListener("pointercancel", up);
    });
  }
  symSelect(){
    const s = el("select"); SYMS.forEach(x => { const o = el("option"); o.value = x; o.textContent = x; s.append(o); });
    s.value = this.state.sym; s.onchange = () => Ws.broadcast(this, s.value); return s;
  }
  setSymbol(sym){
    this.state.sym = sym; this.setTitle(); if (this.symSel) this.symSel.value = sym; this.resub(); Ws.save();
  }
  clearSubs(){ this.unsubs.forEach(u => u()); this.unsubs = []; }
  resub(){}
  close(){ this.clearSubs(); this.destroy && this.destroy(); this.root.remove(); Ws.panels = Ws.panels.filter(p => p !== this); Ws.save(); Ws.checkEmpty(); }
  build(){ this["build_"+this.type](); }

  /* ---- chart ---- */
  build_chart(){
    const tb = el("div","tb"); this.symSel = this.symSelect(); tb.append(this.symSel);
    this.tfSel = el("select"); this.tfSel.title = Lg("Timeframe","الفريم"); TFS.forEach(([v,l]) => this.tfSel.append(Object.assign(el("option"), {value:v, textContent:l})));
    this.tfSel.onchange = () => this.setTf(this.tfSel.value); tb.append(this.tfSel);
    if (MOB){ const row = el("div","mtf"); this.mtfRow = row; [["1m","M1"],["5m","M5"],["15m","M15"],["30m","M30"],["1H","H1"],["4H","H4"],["1D","D1"],["1W","W1"],["1M","MN"]].forEach(([v, l]) => {
        const b = el("button", null, l); b.dataset.tf = v; b.onclick = () => this.setTf(v); row.append(b); }); this._mtfPending = row; }   // MetaTrader's timeframe strip (phones)
    const vw = el("button",null,T("vwap")); vw.onclick = () => { this.chart.ema.vwap = !this.chart.ema.vwap; this.state.ema = Object.assign({}, this.chart.ema); vw.classList.toggle("on", !!this.chart.ema.vwap); this.chart.draw(); Ws.save(); };
    const sg = el("button",null,T("sig")); sg.onclick = () => { this.chart.showSig = !this.chart.showSig; this.state.sig = this.chart.showSig; sg.classList.toggle("on", this.chart.showSig); this.chart.draw(); Ws.save(); };
    const fl = el("button",null,T("flow")); fl.onclick = () => { this.chart.flowOn = !this.chart.flowOn; this.state.flow = this.chart.flowOn; fl.classList.toggle("on", this.chart.flowOn); this.chart.draw(); Ws.save(); };
    const rf = el("select"); rf.title = T("rf"); [["1s",1000],["2s",2000],["5s",5000]].forEach(([l,v]) => { const o = el("option"); o.value = v; o.textContent = "↻ "+l; rf.append(o); });
    rf.value = this.state.rf || 2000; rf.onchange = () => { this.state.rf = +rf.value; Ws.save(); };
    this.cdEl = el("span","m"); this.cdEl.style.cssText = "font-family:ui-monospace,Menlo,monospace;min-width:52px";
    const fit = el("button",null,T("fit")); fit.onclick = () => this.chart.fit();
    const palB = el("button",null,"🎨"); palB.title = Lg("Chart colours: candles, background, grid, presets","ألوان الشارت: الشموع، الخلفية، الشبكة، قوالب جاهزة");
    palB.onclick = ev => { ev.stopPropagation(); document.querySelectorAll(".stpop").forEach(x => x.remove()); const ch_ = this.chart, base = () => Object.assign({up:TH.up, dn:TH.dn, bg:TH.bg, grid:TH.grid, vu:TH.vu || TH.up, vd:TH.vd || TH.dn, pane:TH.pane}, ch_.pal || {});
      const pop = el("div","stpop"), r_ = palB.getBoundingClientRect(); pop.style.left = Math.max(4, Math.min(r_.left, innerWidth-280))+"px"; pop.style.top = (r_.bottom+3)+"px"; pop.style.gridTemplateColumns = "1fr auto"; pop.style.minWidth = "250px"; pop.onpointerdown = e => e.stopPropagation();
      const apply = pal => { ch_.pal = pal; this.state.pal = pal; Ws.save(); ch_.draw(); };
      const ins = {}, put = (k, lab) => { const l = el("span"); l.textContent = lab; const i = el("input"); i.type = "color"; i.value = base()[k] || "#000000"; i.oninput = () => { apply(Object.assign(base(), {[k]: i.value})); }; ins[k] = i; pop.append(l, i); };
      const PRE = [[Lg("Theme default","افتراضي الثيم"), null], ["TradingView", {up:"#26a69a", dn:"#ef5350"}], [Lg("Blue / Orange","أزرق / برتقالي"), {up:"#2196f3", dn:"#ff9800"}], [Lg("Mono","أبيض / رمادي"), {up:"#e6e6e6", dn:"#6b6b6b"}], [Lg("Neon","نيون"), {up:"#00ff9d", dn:"#ff3d71", bg:"#05070d", grid:"#101522"}]];
      const sel = el("select"); PRE.forEach(([n], i) => sel.append(Object.assign(el("option"), {value:i, textContent:n}))); sel.onchange = () => { const v = PRE[+sel.value][1]; apply(v ? Object.assign({}, v) : null); const b = base(); Object.keys(ins).forEach(k => { ins[k].value = b[k] || "#000000"; }); };
      const l0 = el("span"); l0.textContent = Lg("Preset","قالب"); pop.append(l0, sel);
      put("up", Lg("Up candle","شمعة صاعدة")); put("dn", Lg("Down candle","شمعة هابطة")); put("bg", Lg("Background","الخلفية")); put("grid", Lg("Grid","الشبكة")); put("vu", Lg("Volume up","حجم صاعد")); put("vd", Lg("Volume down","حجم هابط")); put("pane", Lg("Indicator panes","خلفية المؤشرات"));
      const dl = el("label"); dl.style.cssText = "grid-column:1/-1;display:flex;gap:6px;align-items:center;cursor:pointer"; const dc = el("input"); dc.type = "checkbox"; dc.checked = !!ch_.dots; dc.onchange = () => { ch_.dots = dc.checked; this.state.dots = dc.checked; Ws.save(); ch_.draw(); }; dl.append(dc, document.createTextNode(Lg("Dot-matrix candles and lines","شموع وخطوط بنقط (دوت ماتريكس)"))); pop.append(dl);
      const rs = el("div","full"); rs.textContent = Lg("Reset to theme","رجوع لألوان الثيم"); rs.onclick = () => { apply(null); pop.remove(); }; pop.append(rs);
      document.body.append(pop); const off = e => { if (!pop.contains(e.target)){ pop.remove(); document.removeEventListener("pointerdown", off, true); } }; setTimeout(() => document.addEventListener("pointerdown", off, true), 0); };
    const ac = el("button",null,"⊙"); ac.title = Lg("Auto-Center: follow the latest candle while preserving zoom","توسيط تلقائي: متابعة الشمعة الحالية مع الحفاظ على الزوم"); ac.classList.toggle("on", acGet());
    ac.onclick = () => { this.chart.autoCenter = !this.chart.autoCenter; acSet(this.chart.autoCenter); ac.classList.toggle("on", this.chart.autoCenter); this.chart.saveView(); this.chart.draw(); Ws.save(); };
    // task 22: Master: one click turns every indicator off, the next click turns the same ones back on (drawings, layout and the chart itself are not touched)
    const masterB = el("button",null,"⏻"); masterB.title = Lg("Master: turn all indicators off, click again to restore them","الماستر: إيقاف كل المؤشرات، والضغطة التانية ترجعهم");
    masterB.onclick = () => {
      const items = this.indItems || [];
      const onNow = items.filter(x => { try { return x.get && x.get(); } catch(e){ return false; } });
      if (onNow.length){ this._masterOn = onNow.map(x => x.id); onNow.forEach(x => { try { x.set(false); } catch(e){} }); }
      else { (this._masterOn || []).forEach(id => { const x = items.find(y => y.id === id); if (x && x.set) { try { x.set(true); } catch(e){} } }); this._masterOn = null; }
      masterB.classList.toggle("on", !!this._masterOn); this.chart.draw(); Ws.save();
    };
    // task 52: crosshair sync toggle (same time on every chart of this symbol)
    const xhB = el("button",null,"✚"); xhB.title = Lg("Crosshair sync: the same time on every chart of this symbol, incl. their order-flow columns","تزامن الكروس: نفس الوقت في كل شارتات الرمز وعمود الأوردر فلو بتاعها");
    XHS.on = store.get(LS+"_xh", true) !== false; XH_BTNS.add(xhB); xhB.classList.toggle("on", XHS.on);
    xhB.onclick = () => xhSet(!XHS.on);
    const drw = el("button",null,"✎✕"); drw.title = Lg("Hide all drawings without deleting them (click again to show them; highlighted = hidden)","إخفاء كل الرسومات بدون حذفها (اضغط تاني لإظهارها؛ مضيء = مخفية)");
    const syncDrawings = () => { const vis = this.state.drawingsVisible !== false; drw.classList.toggle("on", !vis); drw.style.opacity = "1"; };   // owner 2026-10-24: normal = drawings shown (no need to press anything); the button HIDES them and lights up while they are hidden
    drw.onclick = () => { this.chart.drawingsVisible = !this.chart.drawingsVisible; this.state.drawingsVisible = this.chart.drawingsVisible; syncDrawings(); this.chart.draw(); Ws.save(); }; syncDrawings();
    const refreshNow = el("button",null,"⟳"); refreshNow.title = Lg("Reload chart data and preserve the current view","إعادة تحميل بيانات الشارت مع الحفاظ على موضع العرض والتكبير");
    refreshNow.onclick = () => { const ch = this.chart; if (!ch || !ch.data.length) { this.resub(); return; } this._refreshView = {sym:this.state.sym, tf:this.state.tf, bw:ch.bw, yZoom:ch.yZoom, yShift:ch.yShift, back:(ch.data.length-1)-ch.r}; ch.saveView(); this.resub(); Ws.save(); };
    const srB = el("button", null, "S/R"); srB.title = Lg("Daily + weekly support / resistance from the 1D and 1W candles (table of levels). Not a signal.", "دعم ومقاومة يومي + أسبوعي من شموع اليوم والأسبوع (جدول المستويات). مش إشارة.");
    this.srAuto = () => this.state.sr === undefined ? /^1[DW]/.test(String(this.state.tf || "")) : !!this.state.sr;   // on by itself on the daily / weekly charts, off elsewhere until switched on
    this.syncSR = () => { const ch = this.chart; if (!ch) return; ch.srOn = this.srAuto(); srB.classList.toggle("on", ch.srOn); if (!ch.srOn){ ch.srData = null; ch.draw(); return; }
      const sym = this.state.sym; SR.load(sym).then(o => { if (this.state.sym !== sym || !this.chart) return; this.chart.srData = o; this.chart.draw(); if (this._srPop) this._srPop(); }).catch(() => {}); };
    srB.onclick = ev => { ev.stopPropagation(); const had = document.querySelector(".stpop.srpop"); document.querySelectorAll(".stpop").forEach(x => x.remove()); const turnOff = this.srAuto() && !!had;
      if (turnOff){ this.state.sr = false; Ws.save(); this.syncSR(); return; } this.state.sr = true; Ws.save(); this.syncSR();
      const pop = el("div", "stpop srpop"), r_ = srB.getBoundingClientRect(); pop.style.left = Math.max(4, Math.min(r_.left, innerWidth-330))+"px"; pop.style.top = (r_.bottom+3)+"px"; pop.style.gridTemplateColumns = "1fr"; pop.style.minWidth = "310px"; pop.onpointerdown = e => e.stopPropagation(); document.body.append(pop);
      this._srPop = () => { if (!pop.isConnected){ this._srPop = null; return; } const o = this.chart && this.chart.srData, dec = this.chart ? (this.chart.dec != null ? this.chart.dec : 2) : 2; if (!o){ pop.textContent = Lg("Loading 1D / 1W candles…", "بحمّل شموع اليوم والأسبوع…"); return; }
        const rows = [["D", o.D], ["W", o.W]].flatMap(([tf, lv]) => SR.top(lv, 3).map(l => Object.assign({tf}, l))).sort((a, b) => b.p - a.p);
        pop.innerHTML = '<div style="font-weight:700;margin-bottom:3px">'+esc(Lg("Support / resistance (daily, weekly)","دعم / مقاومة (يومي، أسبوعي)"))+'</div>'+(rows.length ? '<table class="wt" style="width:100%"><tr><th>TF</th><th></th><th class="r">'+esc(Lg("Price","السعر"))+'</th><th class="r">'+esc(Lg("Touches","لمسات"))+'</th><th class="r">'+esc(Lg("Strength","القوة"))+'</th><th class="r">%</th></tr>'
          + rows.map(l => '<tr><td>'+l.tf+'</td><td style="color:'+(l.kind === "R" ? "#f6465d" : "#0ecb81")+'">'+(l.kind === "R" ? "R" : "S")+'</td><td class="r">'+fmtP(l.p)+'</td><td class="r">×'+l.touches+'</td><td class="r">'+"★".repeat(l.strength)+'</td><td class="r m">'+(l.dist >= 0 ? "+" : "")+l.dist.toFixed(1)+'</td></tr>').join("")+'</table>' : '<div class="m">'+esc(Lg("No clear levels in the candles loaded (needs at least 2 touches).","مفيش مستويات واضحة في الشموع المحمّلة (لازم لمستين على الأقل)."))+'</div>')
          + '<div style="margin-top:4px"><button class="srOff">'+esc(Lg("Hide S/R lines","إخفاء خطوط الدعم والمقاومة"))+'</button></div><div class="m" style="margin-top:4px">'+esc(Lg("Levels where price reacted before (swing highs / lows, 2+ touches); "+o.nD+" daily / "+o.nW+" weekly candles. Not a signal. Order-flow (liquidity wall) levels need recorded book history: not available yet.","مستويات السعر اتفاعل عندها قبل كده (قمم / قيعان، لمستين+)؛ "+o.nD+" شمعة يومية / "+o.nW+" أسبوعية. مش إشارة. مستويات الأوردر فلو (جدران السيولة) محتاجة تسجيل للـ book: لسه مش متاحة."))+'</div>'; };
      this._srPop(); pop.addEventListener("click", e => { if (e.target.classList && e.target.classList.contains("srOff")){ this.state.sr = false; Ws.save(); pop.remove(); this.syncSR(); } });
      const off = e => { if (!pop.contains(e.target)){ pop.remove(); document.removeEventListener("pointerdown", off, true); } }; setTimeout(() => document.addEventListener("pointerdown", off, true), 0); };
    // screenshot (PNG) and video (WebM, 8 Mbps) of the chart; both download to the device (= save)
    const fname = (ext) => "xpix-"+this.chart.sym+"-"+this.chart.tf+"-"+new Date().toISOString().slice(0,19).replace(/[:T]/g,"-")+"."+ext;
    const dl = (href, name) => { const a = document.createElement("a"); a.href = href; a.download = name; document.body.append(a); a.click(); a.remove(); };
    const shotB = el("button",null,"📷"); shotB.title = Lg("Screenshot of the chart (PNG, download)","لقطة شاشة للشارت (PNG، تتحمل)");
    shotB.onclick = () => dl(this.chart.cv.toDataURL("image/png"), fname("png"));
    const recB = el("button",null,"🎥"); recB.title = Lg("Record the chart as video (WebM, download when stopped)","سجّل فيديو للشارت (WebM، يتحمل لما توقف)"); let rec = null, chunks = [];
    recB.onclick = () => {
      if (rec){ rec.stop(); return; }
      if (!window.MediaRecorder || !this.chart.cv.captureStream){ alert(Lg("Video recording is not supported in this browser","التسجيل مش مدعوم في المتصفح ده")); return; }
      const mime = ["video/webm;codecs=vp9","video/webm"].find(m => MediaRecorder.isTypeSupported(m)) || "";
      rec = new MediaRecorder(this.chart.cv.captureStream(30), {mimeType: mime, videoBitsPerSecond: 8000000}); chunks = [];
      rec.ondataavailable = e => { if (e.data.size) chunks.push(e.data); };
      rec.onstop = () => { dl(URL.createObjectURL(new Blob(chunks, {type: "video/webm"})), fname("webm")); rec = null; recB.classList.remove("on"); recB.textContent = "🎥"; };
      rec.start(1000); recB.classList.add("on"); recB.textContent = "⏹";
    };
    this.pxEl = el("b","px"); this.pxEl.style.cssText = "margin-inline-start:6px;padding:0 4px;border-radius:3px;font-family:ui-monospace,Menlo,monospace";
    this.updEl = el("span","m"); this.updEl.style.fontSize = "10px";
    const kzb = el("button",null,"KZ"); kzb.title = T("kzTip"); kzb.onclick = () => { this.chart.kz = !this.chart.kz; this.state.kz = this.chart.kz; kzb.classList.toggle("on", this.chart.kz); this.chart.draw(); Ws.save(); };
        this.indBtn = this.buildIndMenu();
    const lockBtn = el("button"); lockBtn.title = T("lockTip");
    const lockSync = () => { lockBtn.textContent = this.chart.lockR ? "🔒 "+T("manual") : "⇅ "+T("auto"); lockBtn.classList.toggle("on", !!this.chart.lockR); };
    lockBtn.onclick = () => { const c_ = this.chart, LK = this.state.locks = this.state.locks || {}; if (c_.lockR){ c_.lockR = null; c_.yZoom = 1; c_.yShift = 0; delete LK[this.state.sym]; } else { c_.lockR = [c_._lo, c_._hi]; c_.yZoom = 1; c_.yShift = 0; LK[this.state.sym] = c_.lockR; } Ws.save(); lockSync(); c_.draw(); };
    this.lockSync = lockSync;
    this.ofSync = () => {};   // Depth of Trade now lives inside the Indicators menu
    this.gSelTb = groupSelect(0, 0, v => { const c = this.chart; if (!c.ofStepMap) return; c.ofStepMap[c.sym] = v; c._hmMerge = null; c.onOfStep && c.onOfStep(); c.draw(); }); this.gSelTb.style.display = "none";
    tb.append(this.indBtn, lockBtn, masterB, xhB, rf, refreshNow, srB, fit, this.gSelTb, palB, drw, shotB, recB, this.cdEl, this.pxEl, this.updEl); this.body.style.overflow = "hidden"; this.body.style.display = "flex"; this.body.style.flexDirection = "column"; tb.style.flex = "none"; tb.style.flexWrap = "nowrap"; tb.style.overflowX = "auto"; this.body.append(tb); if (this._mtfPending){ this._mtfPending.style.flex = "none"; this.body.append(this._mtfPending); }
    const wrap = el("div","chartwrap"); this.body.append(wrap); this.msg = el("div","err"); this.msg.style.cssText = "position:absolute;bottom:22px;left:0;z-index:2;font-size:11px"; this.body.append(this.msg);
    this.chart = new CandleChart(wrap); if (!this.state.chartUid){ this.state.chartUid = Math.random().toString(36).slice(2, 10); Ws.save(); } this.chart.uid = this.state.chartUid; if (!this.state.dvMig){ this.state.dvMig = 1; this.state.drawingsVisible = true; }   /* the pen button used to mean "show" (dim = hidden): one-time reset so nobody keeps drawings hidden by the old meaning */ this.chart.drawingsVisible = this.state.drawingsVisible !== false; syncDrawings(); this.chart.onDrawVis = () => { this.state.drawingsVisible = true; syncDrawings(); Ws.save(); }; this.chart.fibPreset = FIB_PRESETS[this.state.fibp] ? this.state.fibp : "Retracement"; this.state.tf = this.state.tf || "1H"; this.chart.tf = this.state.tf;
    if (this.state.maL) this.chart.maL = this.state.maL.map(m => Object.assign({}, m));
    else if (this.state.ema){ const E = this.state.ema, S0 = this.state.st || {}, DC = {9:"#f0b90b", 21:"#4aa3ff", 50:"#b57cff"};   // older saves: the three fixed EMA lines
      this.chart.maL = [9,21,50].map(n => { const s = S0[n] || {}; return {on:!!E[n], type:"EMA", len:s.len || n, color:s.color || DC[n], w:s.w || 1.2, dash:s.dash || ""}; }); }
    if (this.state.ema) this.chart.ema = Object.assign({}, this.chart.ema, this.state.ema);
    if (this.state.st) Object.keys(this.state.st).forEach(k => { if (this.chart.st[k]) Object.assign(this.chart.st[k], this.state.st[k]); });
    this.chart.lockR = (this.state.locks || {})[this.state.sym] || null; this.chart.pal = this.state.pal || null; this.chart.dots = this.state.dots !== undefined ? !!this.state.dots : CFG.ui === "deerflow"; this.chart.onFree = () => { const LK = this.state.locks = this.state.locks || {}; if (this.chart.lockR) LK[this.state.sym] = this.chart.lockR; else delete LK[this.state.sym]; Ws.save(); this.lockSync(); }; this.chart.autoCenter = acGet(); this.lockSync(); this.chart.volOn = this.state.volOn !== false; this.chart.onSubOff = k => { this.state[k] = false; Ws.save(); };
    this.chart.onLLTbl = () => { this.state.llt = false; Ws.save(); };
    this.chart.onGroupSel = (on, cur, tick) => { this.gSelTb.style.display = on ? "" : "none"; if (on) this.gSelTb.sync(cur, tick); };
    this.state.ofstep = this.state.ofstep || {}; this.chart.ofStepMap = this.state.ofstep; this.chart.onOfStep = () => Ws.save();   // price grouping of the order-flow column, per symbol
    this.chart.readOn = this.state.read === true; this.chart.colWide = this.state.cwide === false ? 0 : 1; this.chart.colWideR = +this.state.cwr || 0; this.chart.onWideR = () => { this.state.cwr = this.chart.colWideR || 0; Ws.save(); }; this.chart.gaOn = this.state.ofg !== false; this.chart.scOn = this.state.ofs !== false; this.chart.onOfX = () => { this.state.ofg = this.chart.gaOn; this.state.ofs = this.chart.scOn; Ws.save(); };   // ✕ on the order-flow gauge / sync card: hidden per chart, restored from the Order-flow menu
    this.chart.onKzsTbl = () => { this.state.kzst = false; Ws.save(); };   // Kill Zone Sniper table ✕ (turning the indicator off and on again brings it back)   // the table's own ✕ (turn it back on from the indicator settings)
    this.chart.onSubH = () => { this.state.st = JSON.parse(JSON.stringify(this.chart.st)); Ws.save(); }; this.chart.planLen = this.state.planLen || 40; this.chart.onPlanLen = n => { this.state.planLen = n; Ws.save(); }; this.chart.harmOn = !!this.state.harm; this.chart.bvdOn = !!this.state.bvd; this.chart.ewOn = !!this.state.ew; this.chart.oteAlways = !!this.state.oteAlways; this.chart.vpOn = !!this.state.vp; this.chart.llOn = !!this.state.ll; this.chart.llTbl = this.state.llt !== false; this.chart.smtOn = !!this.state.smt; if (!this.state.dcol && (this.state.dom || this.state.bub)) this.state.dcol = true; this.chart.colOn = !!this.state.dcol; this.chart.colW = Math.max(0, Math.min(2000, +this.state.colW || 0)); { const ALL = ["rsi","macd","adx","cci","zn","bso","rm","r2"], so = Array.isArray(this.state.subOrd) ? this.state.subOrd.filter(k => ALL.includes(k)) : []; this.chart.subOrd = so.concat(ALL.filter(k => !so.includes(k))); } this.chart.onLayout = () => { this.state.colW = this.chart.colW || 0; this.state.subOrd = this.chart.subOrd.slice(); Ws.save(); }; this.chart.divOn = this.state.div !== false; this.chart.donOn = !!this.state.don; this.chart.mt5On = !!this.state.mt5; this.chart.lvOn = !!this.state.lv; this.chart.znOn = !!this.state.zn; this.chart.bsoOn = !!this.state.bso; this.chart.rmOn = !!this.state.rm; this.chart.r2On = !!this.state.r2; this.chart.bbShow = this.state.bbShow !== false; this.chart.fpOn = !!this.state.fp; this.chart.bubOn = !!this.state.bub; this.chart.dotOn = !!this.state.dot; this.chart.domOn = !!this.state.dom; this.chart.mkOn = !!this.state.mk; this.ofSync(); this.chart.deltaOn = !!this.state.dl; this.chart.rsiOn = !!this.state.rsi; this.chart.macdOn = !!this.state.macd; this.chart.adxOn = !!this.state.adx; this.chart.cciOn = !!this.state.cci; this.chart.psarOn = !!this.state.psar; this.chart.calcEma();
    this.chart.setupMode = this.state.smode || "lines"; this.chart.kz = !!this.state.kz; this.chart.kzsOn = !!this.state.kzs; this.chart.kzsTbl = this.state.kzst !== false; this.chart.gannOn = !!this.state.gann; this.chart.liqOn = !!this.state.liq; this.chart.syncOn = this.state.sync !== false; this.chart.astroOn = !!this.state.astro; kzb.classList.toggle("on", this.chart.kz); this.kzb = kzb;
    // left drawing toolbar
    const dt = el("div","dt"); this.toolBtns = {};
    [["cur","↖",T("tCur")],["trend","╱",T("tTrend")],["hline","─",T("tH")],["rect","▭",T("tRect")],["channel","⫽",T("tChan")],["text","T",T("tText")],["fib","Fib",T("tFib")],["wave","〰",T("tWave")],["vline","│",Lg("Vertical line","خط رأسي")],["ray","↗",Lg("Ray","شعاع")],["arrow","→",Lg("Arrow","سهم")],["measure","⟷",Lg("Measure: price and bars","قياس: سعر وشموع")],["prange","≡",Lg("Price range","نطاق سعري")],["drange","⫼",Lg("Date range","نطاق زمني")],["brush","✎",Lg("Brush (hold and drag)","فرشاة (اضغط واسحب)")],["info","ⓘ",Lg("Info line (price, %, bars, angle)","خط معلومات (سعر، نسبة، شموع، زاوية)")],["extline","↔",Lg("Extended line","خط ممتد")],["cross","✛",Lg("Cross line","خط متقاطع")],["ellipse","◯",Lg("Ellipse","قطع ناقص")],["triangle","△",Lg("Triangle (3 clicks)","مثلث (3 نقرات)")],["pitchfork","⑂",Lg("Andrews pitchfork (3 clicks)","شوكة أندروز (3 نقرات)")],["callout","💬",Lg("Callout","تعليق")],["plabel","🏷",Lg("Price label","علامة سعر")],["arrup","⬆",Lg("Arrow mark up","علامة سهم لأعلى")],["arrdn","⬇",Lg("Arrow mark down","علامة سهم لأسفل")],["flag","⚑",Lg("Flag mark","علامة علم")],["long","▲",T("tLong")],["short","▼",T("tShort")]].forEach(([k,ic,tt]) => {
      const b = el("button",null,ic); b.title = tt; this.toolBtns[k] = b; dt.append(b);
      if (k === "fib"){
        const closePop = () => { if (this.fibPop){ this.fibPop.remove(); this.fibPop = null; } };
        b.onclick = () => {
          if (this.fibPop){ closePop(); return; }
          if (this.chart.tool === "fib"){ this.chart.setTool("cur"); return; }
          const pop = el("div","fibpop"); this.fibPop = pop;
          Object.entries(FIB_PRESETS).forEach(([name, lv]) => { const it = el("div"); it.textContent = name; it.append(Object.assign(el("small"), {textContent:lv.slice(0,5).join(" · ")+(lv.length > 5 ? " …" : "")}));
            if (name === this.chart.fibPreset) it.classList.add("on");
            it.onclick = () => { this.chart.fibPreset = name; this.state.fibp = name; Ws.save(); closePop(); this.chart.setTool("fib"); }; pop.append(it); });
          wrap.append(pop); setTimeout(() => { const off = ev => { if (!pop.contains(ev.target)){ closePop(); document.removeEventListener("pointerdown", off, true); } }; document.addEventListener("pointerdown", off, true); }, 0);
        };
      } else b.onclick = () => this.chart.setTool(this.chart.tool === k && k !== "cur" ? "cur" : k);
    });
    // tools grouped like TradingView: one button per category (it shows the tool used last), each popup lists its tools under headings, beside the button
    const CATS = [
      [Lg("Trend lines","خطوط الاتجاه"), [[Lg("Lines","خطوط"), ["trend","info","ray","extline","hline","vline","cross"]], [Lg("Channels and pitchforks","قنوات وشوكات"), ["channel","pitchfork"]]]],
      [Lg("Projection and measure","التوقع والقياس"), [[Lg("Positions","صفقات"), ["long","short"]], [Lg("Measure","قياس"), ["measure","prange","drange"]]]],
      [Lg("Brushes and shapes","فرش وأشكال"), [[Lg("Brushes","فرش"), ["brush"]], [Lg("Shapes","أشكال"), ["rect","ellipse","triangle"]]]],
      [Lg("Text and marks","نصوص وعلامات"), [[Lg("Text","نص"), ["text","callout","plabel"]], [Lg("Arrows and marks","أسهم وعلامات"), ["arrow","arrup","arrdn","flag"]]]]];
    this.catBtns = [];
    const gbs = CATS.map(([cname, sections]) => {
      const members = sections.flatMap(z => z[1]).filter(k => this.toolBtns[k]), gb = el("button", null, this.toolBtns[members[0]].textContent); gb.title = cname;
      const gpop = el("div", "fibpop gp"), closeG = () => { if (gpop.parentNode) gpop.remove(); };
      sections.forEach(([hd, ks]) => { const ms = ks.filter(k => this.toolBtns[k]); if (!ms.length) return; gpop.append(el("div", "gh", hd));
        ms.forEach(k => { const mb = this.toolBtns[k], ic = mb.textContent; mb.textContent = ""; mb.append(el("span", "ic", ic)); gpop.append(mb); mb.addEventListener("click", () => { gb.firstChild.nodeValue = ic; closeG(); }); }); });
      gb.onclick = () => {
        if (gpop.parentNode){ closeG(); return; }
        wrap.append(gpop); { const wr = wrap.getBoundingClientRect(), gr = gb.getBoundingClientRect(); gpop.style.left = "40px"; gpop.style.top = Math.max(0, Math.min(gr.top - wr.top - 3, wrap.clientHeight - gpop.offsetHeight - 4)) + "px"; }   // beside its own button, never off the window
        setTimeout(() => { const off = ev => { if (!gpop.contains(ev.target) && ev.target !== gb){ closeG(); document.removeEventListener("pointerdown", off, true); } }; document.addEventListener("pointerdown", off, true); }, 0);
      };
      this.catBtns.push([gb, members]); return gb;
    });
    dt.append(this.toolBtns.cur, gbs[0], this.toolBtns.fib, this.toolBtns.wave, gbs[1], gbs[2], gbs[3]);
    // object tree (owner 2026-10-19: TradingView-style list): every drawing of this chart, newest first; click selects, eye hides, x deletes
    const ob = el("button",null,"≣"); ob.title = Lg("object tree","شجرة الكائنات"); dt.append(ob);
    const closeObj = () => { if (this.objPop){ this.objPop.remove(); this.objPop = null; } };
    ob.onclick = () => {
      if (this.objPop){ closeObj(); return; }
      const ch = this.chart, pop = el("div","fibpop"); this.objPop = pop;
      const rows = ch.draws.slice().reverse();
      let dragSrc = null; // drag a row onto another row to change the draw order (z-order)
      if (!rows.length){ const e0 = el("div"); e0.textContent = Lg("no drawings on this chart","مفيش رسمات على الشارت ده"); pop.append(e0); }
      rows.forEach(d => {
        const it = el("div"); const name = d.type + (d.txt ? " · "+d.txt : "");
        it.draggable = true; it.title = Lg("drag to reorder","اسحب لتغيير الترتيب");
        it.ondragstart = e => { dragSrc = d; e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", ""); };
        it.ondragover = e => { if (dragSrc && dragSrc !== d){ e.preventDefault(); e.dataTransfer.dropEffect = "move"; } };
        it.ondrop = e => {
          e.preventDefault(); if (!dragSrc || dragSrc === d) return;
          const from = ch.draws.indexOf(dragSrc); if (from < 0 || ch.draws.indexOf(d) < 0) return;
          ch.draws.splice(from, 1); ch.draws.splice(ch.draws.indexOf(d) + 1, 0, dragSrc); dragSrc = null;
          ch.saveDraws(); ch.draw(); closeObj(); ob.onclick(); // reopen the list in its new order
        };
        it.ondragend = () => { dragSrc = null; };
        it.append(Object.assign(el("span"), {textContent: name}));
        const eye = el("small"); eye.textContent = d.hidden ? "◌" : "●"; eye.title = Lg("show / hide","إظهار / إخفاء");
        eye.onclick = e => { e.stopPropagation(); d.hidden = !d.hidden; ch.saveDraws(); ch.draw(); eye.textContent = d.hidden ? "◌" : "●"; };
        const x = el("small"); x.textContent = "✕"; x.title = Lg("delete","حذف");
        x.onclick = e => { e.stopPropagation(); ch.draws = ch.draws.filter(z => z !== d); if (ch.sel === d) ch.sel = null; ch.saveDraws(); ch.draw(); it.remove(); };
        it.onclick = () => { ch.sel = d; ch.draw(); closeObj(); };
        it.append(eye, x); pop.append(it);
      });
      wrap.append(pop);
      setTimeout(() => { const off = ev => { if (!pop.contains(ev.target) && ev.target !== ob){ closeObj(); document.removeEventListener("pointerdown", off, true); } }; document.addEventListener("pointerdown", off, true); }, 0);
    };
    const del = el("button",null,"🗑"); del.title = T("tDel"); del.onclick = () => this.chart.deleteSel();
    const clr2 = el("button",null,"✕"); clr2.title = T("tClr"); let armed = 0;
    clr2.onclick = () => { if (Date.now() - armed < 2500){ this.chart.clearDraws(); armed = 0; clr2.textContent = "✕"; } else { armed = Date.now(); clr2.textContent = "?"; setTimeout(() => { if (Date.now() - armed >= 2400) clr2.textContent = "✕"; }, 2600); } };
    dt.append(del, clr2); wrap.append(dt);
    this.chart.onToolChange = t => { Object.entries(this.toolBtns).forEach(([k,b]) => b.classList.toggle("on", k === t)); (this.catBtns || []).forEach(([gb, ms]) => gb.classList.toggle("on", ms.includes(t))); };
    this.chart.onToolChange("cur");
    this.chart.flowOn = this.state.flow !== false; fl.classList.toggle("on", this.chart.flowOn);
    // task 54 (second tab flashing): the pulse only redraws in a visible tab; a hidden tab does not keep repainting the chart
    this.animTimer = setInterval(() => { if (!document.hidden && this.chart.flowOn && this.chart.marks.length){ this.chart.pulse = !this.chart.pulse; this.chart.draw(); } }, 450);
    this.chart.showSig = this.state.sig !== false; sg.classList.toggle("on", this.chart.showSig); vw.classList.toggle("on", !!this.chart.ema.vwap);
    this.cdTimer = setInterval(() => this.tickCd(), 1000); this.flowIv = setInterval(() => { if (this.chart && this.chart.colOn && !document.hidden) this.chart.draw(); }, 1000);   // was 300 ms: repainted the whole canvas ~3x/s per chart
    this.chart.onNeedMore = () => this.loadMore();
    this.tfSel.value = this.state.tf;
    this.resub();
  }
  /* ---- one "Indicators" dropdown: on/off + a settings panel (colour, width, style, parameters) per indicator ---- */
  buildIndMenu(){
    const btn = el("button", null, "ƒx "+T("ind")+" ▾"), pop = el("div","indpop"); pop.style.display = "none";
    const DASH = [["","—"],["6,3","- -"],["2,3","···"]];
    const P = (key, label, min, max, step) => ({key, label, min, max, step}), PS = (key, label, opts, tip) => ({key, label, opts, tip}), PB = (key, label, tip) => ({key, label, bool:true, tip}),
      PC = (key, label) => ({key, label, color:true}), PN = (key, label, tip) => ({key, label, free:true, tip}), PT = (key, label, ph, tip) => ({key, label, text:true, ph, tip}), PH = label => ({sep:true, label});
    const ch = () => this.chart;
    const items = [
      {id:"ma", ma:true, label:Lg("Moving averages (SMA / EMA / WMA, up to 7)","المتوسطات المتحركة (SMA / EMA / WMA، لحد 7)"), tip:Lg("One indicator for every moving average. Each line in the box: on/off, SMA / EMA / WMA, period, colour, thickness, dash, remove.","مؤشر واحد لكل المتوسطات. كل خط في الصندوق: تشغيل/إيقاف، SMA / EMA / WMA، الفترة، اللون، السُمك، الشكل، حذف."), get:() => ch().maL.some(m => m.on), set:v => { ch().maL.forEach(m => m.on = v); }},
      {id:"vwap", label:"VWAP", get:() => !!ch().ema.vwap, set:v => { ch().ema.vwap = v; this.state.ema = Object.assign({}, ch().ema); }, sty:"vwap", params:[]},
      {id:"sbox", label:Lg("Trade box (setup as a box, not lines)","صندوق الصفقة (الخطة كصندوق بدل خطوط)"), tip:Lg("Draws the signal's trade plan (entry / stop / targets) as a risk-reward box on the chart instead of plain lines.","بيرسم خطة الصفقة (دخول / وقف / أهداف) كصندوق ربح/خسارة على الشارت بدل الخطوط."), get:() => ch().setupMode === "box", set:v => { ch().setupMode = v ? "box" : "lines"; this.state.smode = v ? "box" : "lines"; }},
      {id:"kz", label:T("indKz"), tip:T("kzTip"), get:() => ch().kz, set:v => { ch().kz = v; this.state.kz = v; this.kzb && this.kzb.classList.toggle("on", v); }},
      {id:"sync", label:Lg("Order-flow sync (book + tape + limits)","تزامن الأوردر فلو (الدفتر + الصفقات + الليمت)"), tip:Lg("Fires only when the order book imbalance, the aggressor tape and the big-limit events all point the same way at the same moment. Each setup is followed live (stop 1 ATR, target in R) and the card under the order-flow column shows the forward-test stats. Diamonds on the chart = setups (hollow = open). Needs the live book and tape (OKX symbols).","بيطلع بس لما الدفتر والصفقات وأحداث الليمت الكبيرة يتفقوا على نفس الاتجاه في نفس اللحظة. كل صفقة بتتتابع لايف (ستوب 1 ATR، هدف بالـ R) والكارت تحت الأوردر فلو بيعرض نتايج الاختبار الحي. المعينات على الشارت = الصفقات (فاضي = مفتوحة). محتاج دفتر وصفقات لايف (عملات OKX)."), get:() => ch().syncOn, set:v => { ch().syncOn = v; this.state.sync = v; }, sty:"sync", col2:true, params:[P("book","Book imbalance (0.05-0.6)",0.05,0.6,0.05), P("tape","Tape delta (0.05-0.6)",0.05,0.6,0.05), P("lim","Net limit events",1,6,1), P("win","Limit window (s)",15,300,15), P("rr","Target (R)",0.5,4,0.25), P("cool","Cool-down (min)",1,30,1), P("exp","Expiry (min)",5,240,5)]},
      {id:"liqm", label:Lg("Liquidations (OKX)","التصفيات (OKX)"), tip:Lg("OKX public liquidation orders for this perpetual: one bubble per candle, size = USD liquidated. Red = longs liquidated (forced sells), green = shorts liquidated. A big cluster after a sweep often marks the turn. One exchange only; OKX returns only the latest 100, so it fills in while the chart is open.","أوامر التصفية العامة من OKX للعقد ده: فقاعة لكل شمعة وحجمها = الدولارات المصفّاة. أحمر = تصفية لونج، أخضر = تصفية شورت. تجمع كبير بعد سويب غالباً بيعلّم الانعكاس. بورصة واحدة بس؛ OKX بيدي آخر 100 بس، فبتتملي وانت فاتح الشارت."), get:() => ch().liqOn, set:v => { ch().liqOn = v; this.state.liq = v; this.liqKick && this.liqKick(); }, sty:"liq", col2:true, params:[P("min","Min USD per bubble",1000,1000000,1000), P("size","Bubble size",0.5,3,0.25)]},
      {id:"astro", label:Lg("Gann astro (moon, aspects, retrograde, planetary lines) - optional","جان الفلكي (القمر، الزوايا، التراجع، خطوط الكواكب) - اختياري"), tip:Lg("Planet positions computed in the browser (Schlyter elements; checked on known moons, the 2020 Jupiter-Saturn conjunction and the April 2024 Mercury retrograde). Moon phases, aspects 0/60/90/120/180 between two bodies (geo or helio), retrograde shading, and Gann planetary price lines: 1 degree of longitude = 1 price unit x scale, repeating every 360. Visual only: there is no scientific evidence that planets move prices; the lunar effect found in 2001 was small and inconsistent later - the weekly lab tests it on our markets.","أماكن الكواكب بتتحسب في المتصفح (معادلات Schlyter؛ اتراجعت على أطوار قمر معروفة واقتران المشتري وزحل 2020 وتراجع عطارد أبريل 2024). أطوار القمر، الزوايا 0/60/90/120/180 بين جسمين (جيو أو هيليو)، فترات التراجع، وخطوط جان السعرية للكواكب: درجة = وحدة سعر × المقياس وبتتكرر كل 360. عرض بصري بس: مفيش دليل علمي إن الكواكب بتحرك الأسعار؛ أثر القمر اللي اتلاقى 2001 كان صغير ومش ثابت بعد كده - المعمل الأسبوعي بيختبره على أسواقنا."), get:() => ch().astroOn, set:v => { ch().astroOn = v; this.state.astro = v; }, sty:"astro", col2:true, params:[
        PH(Lg("Moon","القمر")), PB("moon", Lg("New / full moon","المحاق / البدر")), PB("mq", Lg("Also quarters","والتربيعات")),
        PH(Lg("Aspects","الزوايا")), PB("asp", Lg("Aspects on","تشغيل الزوايا")), PS("p1", Lg("Body 1","الجسم 1"), [["sun","☉ Sun"],["moon","☽ Moon"],["mercury","☿ Mercury"],["venus","♀ Venus"],["mars","♂ Mars"],["jupiter","♃ Jupiter"],["saturn","♄ Saturn"],["uranus","♅ Uranus"],["neptune","♆ Neptune"]]), PS("p2", Lg("Body 2","الجسم 2"), [["sun","☉ Sun"],["moon","☽ Moon"],["mercury","☿ Mercury"],["venus","♀ Venus"],["mars","♂ Mars"],["jupiter","♃ Jupiter"],["saturn","♄ Saturn"],["uranus","♅ Uranus"],["neptune","♆ Neptune"]]),
        PS("aset", Lg("Which aspects","أنهي زوايا"), [["major", Lg("Major 0/60/90/120/180","الرئيسية 0/60/90/120/180")],["hard", Lg("Hard 0/90/180","الصعبة 0/90/180")],["all", Lg("All incl. 30/45/135/150","كلها مع 30/45/135/150")]]), PB("ahel", Lg("Heliocentric","هيليو (من الشمس)")),
        PH(Lg("Retrograde","التراجع")), PB("retro", Lg("Shade retrograde","ظلّل التراجع")), PS("rp", Lg("Planet","الكوكب"), [["sun","☉ Sun"],["moon","☽ Moon"],["mercury","☿ Mercury"],["venus","♀ Venus"],["mars","♂ Mars"],["jupiter","♃ Jupiter"],["saturn","♄ Saturn"],["uranus","♅ Uranus"],["neptune","♆ Neptune"]].slice(2)),
        PH(Lg("Planetary price lines","خطوط الكواكب السعرية")), PB("pl", Lg("Lines on","تشغيل الخطوط")), PS("plp", Lg("Planet","الكوكب"), [["sun","☉ Sun"],["moon","☽ Moon"],["mercury","☿ Mercury"],["venus","♀ Venus"],["mars","♂ Mars"],["jupiter","♃ Jupiter"],["saturn","♄ Saturn"],["uranus","♅ Uranus"],["neptune","♆ Neptune"]]), PB("plhel", Lg("Heliocentric","هيليو")), PN("scale", Lg("Price per degree (0 = auto)","سعر لكل درجة (0 = أوتو)")), P("harm", Lg("Harmonics (lines per 360°)","الهارمونيك (خطوط لكل 360°)"), 1, 12, 1)]},
      {id:"gann", label:Lg("Gann: price angles, time levels, star (Se7s rules)","جان: زوايا السعر، مستويات الزمن، النجمة (قواعد Se7s)"), tip:Lg("360 deg = (sqrt(start/spacing) +- 2)^2 x spacing; angles by averages (Se7s) or by formula; shape 1-10 = main angles every 360/n deg, secondary halfway. AUTO picks the start swing and spacing on 1D (or 1W / 4H) that later swings respected most versus the same grid shifted, and the time spacing the same way - so all timeframes show the same levels. Labels: angle = price, xN = later swings that touched it. The yellow box = next time level x the price levels around the last price. In-sample fit: it describes the past, it does not prove the future.","360° = (جذر(البداية÷التباعد) ± 2)² × التباعد؛ الزوايا بالمتوسطات (Se7s) أو بالمعادلة؛ الشكل 1-10 = زوايا أساسية كل 360/ن وثانوية في النص. الأوتوماتيك بيختار نقطة البداية والتباعد على اليومي (أو الأسبوعي / 4س) اللي السعر احترمها أكتر من نفس الشبكة متزحزحة، ونفس الشيء للزمن - فكل الفريمات بتبين نفس المستويات. الليبل: الزاوية = السعر، ×ن = عدد القمم/القيعان اللي لمسته. المربع الأصفر = مستوى الزمن الجاي × مستويات السعر حوالين آخر سعر. مطابقة على الماضي، مش ضمان للمستقبل."), get:() => ch().gannOn, set:v => { ch().gannOn = v; this.state.gann = v; }, sty:"gann", col2:true, params:[
        PH(Lg("Mode","الوضع")), PS("mode", Lg("Mode","الوضع"), [["auto", Lg("Auto (best fit)","أوتوماتيك (أفضل مطابقة)")], ["manual", Lg("Manual","يدوي")]]), PS("src", Lg("Levels from","المستويات من"), [["auto", Lg("Auto = this chart's timeframe","أوتو = فريم الشارت")],["1m","1m"],["3m","3m"],["5m","5m"],["15m","15m"],["30m","30m"],["1H","1H"],["2H","2H"],["4H","4H"],["6H","6H"],["12H","12H"],["1D","1D"],["1W","1W"],["1M","1M"]]),
        PS("anc", Lg("Start point","نقطة البداية"), [["best", Lg("Best major swing (auto)","أفضل قمة/قاع كبير (أوتو)")],["high", Lg("Highest high","أعلى قمة")],["low", Lg("Lowest low","أقل قاع")],["last", Lg("Latest major swing","آخر قمة/قاع كبير")]]),
        PS("htf", Lg("Higher-timeframe grid","شبكة الفريم الأعلى"), [["auto", Lg("Auto (next timeframe up)","أوتو (الفريم الأعلى)")],["off", Lg("Off","مقفول")],["1H","1H"],["4H","4H"],["1D","1D"],["1W","1W"],["1M","1M"]]),
        PH(Lg("Price angles","زوايا السعر")), PN("start", Lg("Start price (0 = auto)","سعر البداية (0 = أوتو)")), PN("spacing", Lg("Spacing (0 = auto)","التباعد (0 = أوتو)")), P("tback", Lg("Manual start: bars ago on the source","البداية اليدوي: شمعة لورا"), 0, 2000, 1),
        PS("dir", Lg("Up or down","طالع ولا نازل"), [["auto", Lg("Auto (low = up)","أوتو (قاع = طالع)")], ["up", Lg("Up","طالع")], ["down", Lg("Down","نازل")], ["both", Lg("Both","الاتنين")]]),
        PS("shape", Lg("Shape type","نوع الشكل"), [[1,"01-Circle"],[2,"02-StraightLine"],[3,"03-Triangle"],[4,"04-Square"],[5,"05-Pentagon"],[6,"06-Hexagon"],[7,"07-Heptagon"],[8,"08-Octagon"],[9,"09-Nonagon"],[10,"10-Decagon"]]),
        PS("calc", Lg("Angles","الزوايا"), [["avg", Lg("By averages (Se7s)","بالمتوسطات (Se7s)")], ["formula", Lg("By formula (Square of 9)","بالمعادلة (مربع التسعة)")]]), P("cycles", Lg("Rings of 360° (min; more are added to cover the price)","حلقات 360° (أقل عدد؛ بيزيد لوحده لحد ما يغطي السعر)"), 1, 12, 1),
        PB("sec", Lg("Secondary angles","زوايا ثانوية")), PB("lbl", Lg("Labels","الليبلز")), PB("ext", Lg("Extend lines to the left","مد الخطوط للشمال")),
        PH(Lg("Time","الزمن")), PB("tlv", Lg("Time levels","مستويات الزمن")), PS("tq", Lg("Time quarters","أرباع الزمن"), [["q", Lg("Quarters of the cycle","أرباع الدورة")],["e", Lg("Eighths of the cycle","أثمان الدورة")],["t", Lg("Thirds of the cycle","أثلاث الدورة")],["cal", Lg("Calendar 90/180/270/360 days","تقويم 90/180/270/360 يوم")],["off", Lg("Off","مقفول")]]), PB("cbox", Lg("Cycle start / end boxes","بداية ونهاية الدورات")), PS("lcyc", Lg("Long cycles (49d .. 30y)","الدورات الطويلة (49 يوم .. 30 سنة)"), [["auto", Lg("Auto: 5y+ and H/L confluences (daily and bigger)","أوتو: 5 سنين+ وتقاطعات القمة/القاع (اليومي وأكبر)")],["on", Lg("All cycles and multiples","كل الدورات ومضاعفاتها")],["off", Lg("Off","مقفول")]]), PN("tsp", Lg("Time spacing in source bars (0 = auto)","تباعد الزمن بشموع المصدر (0 = أوتو)")), P("toff", Lg("Bar offset (<-left 0 right->)","إزاحة الشموع (<-شمال 0 يمين->)"), -500, 500, 1), PT("tdate", Lg("Manual start date","تاريخ البداية اليدوي"), "YYYY-MM-DD"),
        PH(Lg("Geometry","الأشكال")), PB("sqr", Lg("Square of the range (1/8 & 1/3, price + time)","مربع الرينج (أثمان وأثلاث، سعر وزمن)")), P("zw", Lg("Zone width (source bars each side)","عرض المنطقة (شموع على كل جنب)"), 1, 10, 1),
        PH(Lg("Multi-timeframe clusters","تجمعات الفريمات")), PS("mtf", Lg("Clusters","التجمعات"), [["auto", Lg("On (this + higher timeframes)","شغال (الفريم ده + الأعلى)")],["off", Lg("Off","مقفول")]]), P("mtfn", Lg("Higher timeframes used","عدد الفريمات الأعلى"), 1, 3, 1),
        P("ctol", Lg("Price cluster tolerance (x ATR)","سماحية تجمع السعر (× ATR)"), .1, 2, .05), P("ctolT", Lg("Time cluster tolerance (bars)","سماحية تجمع الزمن (شموع)"), 1, 20, 1),
        PS("zsrc", Lg("Zone trades use","صفقات المناطق على"), [["clusters", Lg("Clusters (strongest)","التجمعات (الأقوى)")],["grid", Lg("This timeframe's grid","شبكة الفريم ده")]]), PB("zone", Lg("Zone trades: arrows, entry / stop / TP1 / TP2, history stats","صفقات المناطق: أسهم ودخول/ستوب/أهداف وإحصائيات")), PB("star", Lg("Gann star (in the range box)","نجمة جان (جوه صندوق الرينج)")), PC("starc", Lg("Star colour","لون النجمة")), P("spts", Lg("Star points","نقط النجمة"), 3, 12, 1), PB("fan", Lg("Gann box on the range (1x1, 1x2, 2x1)","صندوق جان على الرينج (1x1، 1x2، 2x1)"))]},
      {id:"kzs", label:Lg("Kill Zone Sniper (JOAT style)","Kill Zone Sniper (ستايل JOAT)"), tip:Lg("Sweep-and-reverse inside the London (02-05) / NY AM (07-10) kill zones, New York time: a candle takes the 20-bar low (high), closes back with a body >= 0.9 ATR (and >= 1.5x average volume when the feed has volume). Draws the swept pool, a sniper mark, and the projected entry / stop (sweep wick) / target (30-bar swing, >= 1.5R) as a green/red box, plus a small table counting what is drawn. Same rules as the scanner's Kill Zone Sniper detector. 1H and lower. Idea from the open-source 'ICT Kill Zone Sniper [JOAT]' description; not a copy of its code.","سحب سيولة وانعكاس جوه كيل زون لندن (02-05) / نيويورك الصبح (07-10) بتوقيت نيويورك: شمعة تكسر أقل قاع لآخر 20 شمعة (أو أعلى قمة) وتقفل راجعة بجسم >= 0.9 ATR (و>= 1.5 ضعف متوسط الفوليوم لو فيه فوليوم). بيرسم المستوى المسحوب، علامة القناص، وصندوق الدخول / الوقف (طرف الذيل) / الهدف (قمة/قاع آخر 30 شمعة، >= 1.5R)، وجدول صغير بعدد اللي اترسم. نفس قواعد كاشف Kill Zone Sniper في السكانر. فريم ساعة وأقل. الفكرة من وصف مؤشر JOAT المفتوح، مش نسخة من الكود."), get:() => ch().kzsOn, set:v => { ch().kzsOn = v; this.state.kzs = v; if (v){ ch().kzsTbl = true; this.state.kzst = true; } }},
      {id:"dot3", refresh:true, label:T("indDot3"), tip:T("dot3Tip"), get:() => ch().bubOn && ch().dotOn && ch().domOn && ch().mkOn, set:v => { const c_ = ch(); c_.bubOn = c_.dotOn = c_.domOn = c_.mkOn = v; if (v) c_.colOn = true; Object.assign(this.state, {bub:v, dot:v, dom:v, mk:v, dcol:v ? true : this.state.dcol}); }},
      {id:"bub", label:T("indBub"), tip:T("bubTip"), get:() => ch().bubOn, set:v => { const c_ = ch(); c_.bubOn = v; if (v) c_.colOn = true; this.state.bub = v; if (v) this.state.dcol = true; }, sty:"of", col2:true, params:[P("min","Min size 0=all 1=smart 2=whale",0,2,1), P("bsz","Bubble ×",0.3,3,0.1), P("bop","Bubble opacity ×",0.2,2.5,0.1), P("dom","Heat ×",0.3,3,0.1)]},
      {id:"dot", label:T("indDot"), tip:T("dotTip"), get:() => ch().dotOn, set:v => { ch().dotOn = v; this.state.dot = v; }},
      {id:"dom", label:T("indDom"), tip:T("domTip"), get:() => ch().domOn, set:v => { const c_ = ch(); c_.domOn = v; if (v) c_.colOn = true; this.state.dom = v; if (v) this.state.dcol = true; }},
      {id:"mk", label:T("indMk"), get:() => ch().mkOn, set:v => { ch().mkOn = v; this.state.mk = v; }},
      {id:"fp", label:T("indFp"), tip:T("fpTip"), get:() => ch().fpOn, set:v => { ch().fpOn = v; this.state.fp = v; if (v && this.fpFill) this.fpFill(); if (!v && this.fpSave) this.fpSave(); }},
      {id:"delta", label:T("indDelta"), tip:T("deltaTip"), get:() => ch().deltaOn, set:v => { ch().deltaOn = v; this.state.dl = v; }},
      {id:"smt", label:"SMT", tip:Lg("SMT divergence: draws the correlated market (BTC↔ETH, ETH↔SOL …) on this chart and marks swings where one makes a new extreme and the other refuses.","SMT: يرسم السوق المرتبط (BTC↔ETH …) على نفس الشارت ويعلّم القمم/القيعان اللي واحد فيهم يكسر والتاني يرفض."), get:() => ch().smtOn, set:v => { ch().smtOn = v; this.state.smt = v; if (v){ this.smtT = 0; setTimeout(() => this.smtKick(), 0); } this.smtT = 0; if (!v) ch().smtD = null; }},
      {id:"vp", label:T("indVp"), tip:T("vpTip"), get:() => ch().vpOn, set:v => { ch().vpOn = v; this.state.vp = v; }, sty:"vp", params:[
        PS("mode", Lg("Show","العرض"), [["vd", Lg("Volume + delta (grey + colour)","حجم + دلتا (رمادي + لون)")], ["delta", Lg("Delta only","دلتا بس")], ["split", Lg("Buy / sell split","شراء / بيع جنب بعض")]]),
        PS("range", Lg("Candles","الشموع"), [["vis", Lg("Visible on screen","المعروضة على الشاشة")], ["all", Lg("All loaded","كل المحمّل")]]),
        P("rowpx", Lg("Row height px (detail)","ارتفاع الصف بكسل (التفاصيل)"), 1, 12, 1), P("wpct", Lg("Width % of chart","العرض % من الشارت"), 5, 30, 1), PB("lbl", Lg("Delta numbers on rows","أرقام الدلتا على الصفوف")),
        PB("book", Lg("Limit orders strip (order book)","شريط أوامر الليميت (الأوردر بوك)")), PB("walls", Lg("Mark big lasting walls","علّم الحوائط الكبيرة الثابتة"))]},
      {id:"ew", label:T("indEw"), get:() => ch().ewOn, set:v => { ch().ewOn = v; this.state.ew = v; }},
      {id:"ote", label:Lg("OTE: show waiting zone","OTE: إظهار المنطقة قبل دخول السعر"), tip:Lg("Off by default: the active 62–79% OTE zone appears only after a later confirmed candle trades inside it. Turn on to keep the active zone visible while waiting. Historical completed zones remain visible either way.","مقفول افتراضيًا: منطقة OTE النشطة (62–79%) تظهر فقط بعد دخول شمعة لاحقة مؤكدة إليها. شغّله لإظهار المنطقة أثناء الانتظار. المناطق التاريخية المكتملة تظل ظاهرة في الحالتين."), get:() => !!ch().oteAlways, set:v => { ch().oteAlways = v; this.state.oteAlways = v; ch().draw(); }},
      {id:"bvd", label:T("indBvd"), tip:T("bvdTip"), get:() => ch().bvdOn, set:v => { ch().bvdOn = v; this.state.bvd = v; }},
      {id:"harm", label:T("indHarm"), tip:T("harmTip"), get:() => ch().harmOn, set:v => { ch().harmOn = v; this.state.harm = v; }},
      {id:"sig", label:T("indSig"), get:() => ch().showSig, set:v => { ch().showSig = v; this.state.sig = v; }},
      {id:"flow", label:T("indFlow"), get:() => ch().flowOn, set:v => { ch().flowOn = v; this.state.flow = v; }, sty:"flow", col2:true, params:[P("anchor","Start at: 1 = current candle, 0 = event",0,1,1), P("len","Line length in bars (0 = to the edge)",0,200,1), P("max","Max lines shown",1,30,1), P("age","Hide older than N minutes (0 = never)",0,1440,5), P("tgt","Target path (1/0)",0,1,1)]},
      {id:"volume", label:T("indVol"), get:() => ch().volOn, set:v => { ch().volOn = v; this.state.volOn = v; }, sty:"vol", params:[P("h","Height %",5,60,1), P("delta","Colour by delta (1/0)",0,1,1)]},
      {id:"rsi", label:"RSI", get:() => ch().rsiOn, set:v => { ch().rsiOn = v; this.state.rsi = v; }, sty:"rsi", params:[P("len","Length",2,100,1), P("ob","Overbought",50,100,1), P("os","Oversold",0,50,1), P("hp","Height %",1,92,1)]},
      {id:"lv", label:Lg("Open levels (4H / D / W / M)","مستويات الفتح (4س / يوم / أسبوع / شهر)"), tip:Lg("Open of the current 4-hour, daily, weekly and monthly candle (solid) and the previous candle's open (dashed). In a 24/7 market the previous close equals the new open, so one line carries both. Daily/weekly/monthly use UTC candles.","فتح شمعة 4 ساعات واليوم والأسبوع والشهر الحالية (خط كامل) وفتح الشمعة السابقة (متقطع). في سوق 24/7 إغلاق الشمعة السابقة = فتح الجديدة فخط واحد بيمثلهم. اليوم والأسبوع والشهر بتوقيت UTC."), get:() => ch().lvOn, set:v => { ch().lvOn = v; this.state.lv = v; if (v){ this.lvT = 0; setTimeout(() => this.lvKick(), 0); } }},
      {id:"ll", label:Lg("MTF Liquidity Levels & Targets (XPIX)","مستويات سيولة متعددة الفريمات + أهداف (XPIX)"), tip:Lg("Port of the MTF LLT TradingView script: nearest previous-candle high/low for 5M/15M/1H/4H/D/W (hidden when > 15 ATR away), the X77 target after the last EMA77/EMA144 cross (nearest level inside 70-170 pips), a predictive target number above the last candle (gold = a previous high/low lies in the way), and a targets table. Alerts and the MA plots of the original are not ported.","نسخة من مؤشر MTF LLT من تريدينج فيو: أقرب قمة/قاع للشمعة السابقة على 5د/15د/1س/4س/يوم/أسبوع (تخفى لو أبعد من 15 ATR)، هدف X77 بعد آخر تقاطع EMA77/EMA144 (أقرب مستوى داخل 70-170 نقطة)، رقم هدف متوقع فوق آخر شمعة (ذهبي = في قمة/قاع سابق في الطريق)، وجدول أهداف. التنبيهات وخطوط المتوسطات في الأصل لم تُنقل."), get:() => ch().llOn, set:v => { ch().llOn = v; this.state.ll = v; if (v){ this.llT = 0; setTimeout(() => this.llKick(), 0); } ch().draw(); }},
      {id:"llt", label:Lg("XPIX targets table (show / hide)","جدول أهداف XPIX (إظهار / إخفاء)"), tip:Lg("The targets table of the MTF Liquidity Levels & Targets indicator (bottom right of the chart). Switch it off to keep only the lines and the target number.","جدول الأهداف الخاص بمؤشر XPIX (أسفل يمين الشارت). أغلقه لو عايز الخطوط ورقم الهدف بس."), get:() => ch().llTbl !== false, set:v => { ch().llTbl = v; this.state.llt = v; ch().draw(); }},
      {id:"dcol", label:Lg("Order-flow column (heat map + bubbles)","عمود Order Flow (هيت ماب + فقاعات)"), tip:Lg("A separate column right of the price axis on the same price scale: a yellow liquidity heat map of resting orders from the order book (stronger = bigger orders, also far from the price) and bubbles of what actually traded at each price (green = buying, red = selling). The latest candle moves to the middle of the chart. Both fill up live while this chart is open (OKX gives no order-book history).","عمود منفصل يمين محور السعر على نفس مقياس السعر: هيت ماب أصفر للأوامر الواقفة في دفتر الأوامر (أقوى = أوامر أكبر، حتى لو بعيدة عن السعر) وفقاعات للي اتنفذ فعلاً عند كل سعر (أخضر شراء، أحمر بيع). آخر شمعة بتروح لنص الشارت. الاتنين بيتبنوا لايف وانت فاتح الشارت (OKX مبتدّيش تاريخ لدفتر الأوامر)."), get:() => ch().colOn, set:v => { const c_ = ch(); c_.colOn = v; this.state.dcol = v; if (v){ c_.domOn = c_.bubOn = true; this.state.dom = this.state.bub = true; } c_.fit(); }},
      {id:"cwide", label:Lg("Order-flow column: WIDE map (the whole book + support / resistance lines)","عمود الأوردر فلو: خريطة واسعة (الدفتر كله + خطوط الدعم والمقاومة)"), tip:Lg("The column gets its OWN price scale over the whole order book (Hyperliquid about ±5 %, OKX as far as the exchange lists), never narrower than the chart: biggest resting orders drawn as labelled lines (red above the price = resistance-like, green below = support-like), a gold bracket shows what the chart shows now, buy / sell bubbles on top. Needs the book (DOM) layer on. Off = the column follows the chart's own price scale. Describes what rests in the book, never a signal.","العمود بياخد مقياس سعر لوحده على دفتر الأوامر كله (هايبرليكويد حوالي ±5%، وOKX على قد ما البورصة بتعرض)، ومش بيبقى أضيق من الشارت: أكبر الأوامر الواقفة خطوط عليها السعر والحجم (أحمر فوق السعر = شبه مقاومة، أخضر تحته = شبه دعم)، وقوس دهبي بيبيّن اللي الشارت عارضه دلوقتي، وفقاعات الشراء والبيع. محتاج طبقة الدفتر (DOM) شغالة. مقفولة = العمود بيمشي على مقياس الشارت. وصف للي واقف في الدفتر، مش إشارة."), get:() => ch().colWide > 0, set:v => { ch().colWide = v ? 1 : 0; this.state.cwide = v; ch().draw(); }},
      {id:"ofg", label:Lg("Order-flow gauge (buy / sell pressure)","مقياس ضغط الشراء والبيع (Order Flow)"), tip:Lg("Show or hide the pressure gauge in the order-flow column. You can also hide it with its ✕.","إظهار أو إخفاء مقياس الضغط في عمود Order Flow. تقدر كمان تخفيه بزر ✕ بتاعه."), get:() => ch().gaOn !== false, set:v => { ch().gaOn = v; this.state.ofg = v; ch().draw(); }},
      {id:"read", label:Lg("Flow reading (what book + tape + limits did)","قراءة الأوردر فلو (اللي عمله الدفتر والشريط والليمت)"), tip:Lg("A short numbered reading inside the order-flow column, with the same numbers marked on the heat map: pulled / filled walls, absorption-like zones, refills, book vs tape agreement, and the confluence zones. It describes the last 2 minutes and never predicts. Off by default; needs a wide enough column.","قراءة قصيرة مرقّمة جوه عمود الأوردر فلو، ونفس الأرقام متعلّمة على الهيت ماب: حيطان اتسحبت أو اتنفذت، مناطق شبه امتصاص، إعادة ملء، واتفاق الدفتر مع الشريط، ومناطق الالتقاء. وصف لآخر دقيقتين، مش توقع. مقفولة افتراضيًا ومحتاجة عمود عريض كفاية."), get:() => ch().readOn === true, set:v => { ch().readOn = v; this.state.read = v; ch().draw(); }},
      {id:"zlog", label:Lg("Export zone test log (JSON)","تصدير سجل اختبار المناطق (JSON)"), tip:Lg("Downloads the forward-test records of the confluence zones of this symbol (kept in this browser). The Technical Office > Flow lab judges them against control levels.","بينزّل سجل الاختبار الأمامي لمناطق الالتقاء للرمز ده (محفوظ في المتصفح). المكتب الفني ← معمل الأوردر فلو بيحكم عليه مقابل مستويات كنترول."), get:() => false, set:v => { if (v) exportZoneLog(ch()); }},
      {id:"ofs", label:Lg("Order-flow card (lights, OI, setups)","كارت Order Flow (الإشارات، OI، الأفكار)"), tip:Lg("Show or hide the card under the order-flow column. You can also hide it with its ✕.","إظهار أو إخفاء الكارت تحت عمود Order Flow. تقدر كمان تخفيه بزر ✕ بتاعه."), get:() => ch().scOn !== false, set:v => { ch().scOn = v; this.state.ofs = v; ch().draw(); }},
      {id:"div", label:Lg("Divergence lines (RSI / MACD / Volume)","خطوط الدايفرجنس (RSI / MACD / الفوليوم)"), tip:Lg("Draws regular bullish (green) and bearish (red) divergences on the RSI and MACD panes and on the volume bars: price makes a new swing extreme but the indicator (or volume) does not confirm. Needs the RSI / MACD panes switched on.","يرسم الدايفرجنس العادي الصاعد (أخضر) والهابط (أحمر) على بانل RSI وMACD وعلى أعمدة الفوليوم: السعر يعمل قمة/قاع جديد والمؤشر (أو الفوليوم) ما يأكدش. لازم بانل RSI / MACD يكونوا شغالين."), get:() => ch().divOn, set:v => { ch().divOn = v; this.state.div = v; }},
      {id:"mt5", label:Lg("MT5 pack (MA ribbon + SAR + fractals)","حزمة MT5 (ريبون MA + SAR + فراكتال)"), tip:Lg("Copied from the MT5 phone chart: 5 moving averages (periods adjustable), Parabolic SAR as yellow diamonds, and Williams fractals as red/green arrows. The exact MT5 periods are not known - set them in the settings.","منقولة من شارت MT5 على الموبايل: 5 متوسطات متحركة (الفترات قابلة للتعديل)، وParabolic SAR كمعينات صفراء، وفراكتال ويليامز كأسهم حمرا/خضرا. فترات MT5 الحقيقية مش معروفة - اضبطها من الإعدادات."), get:() => ch().mt5On, set:v => { ch().mt5On = v; this.state.mt5 = v; }, sty:"mt5", params:[P("sar","SAR on (1/0)",0,1,1), P("step","SAR step",0.005,0.1,0.005), P("max","SAR max",0.05,1,0.05), P("frc","Fractals on (1/0)",0,1,1), P("fr","Fractal bars each side",1,5,1), P("rib","MA ribbon on (1/0)",0,1,1), P("ema","MA type 0=SMA 1=EMA",0,1,1), P("p1","MA 1",2,400,1), P("p2","MA 2",2,400,1), P("p3","MA 3",2,400,1), P("p4","MA 4",2,400,1), P("p5","MA 5",2,400,1)]},
      {id:"don", label:Lg("Donchian ensemble","قنوات Donchian (مجمّعة)"), tip:Lg("Donchian channels on closes (20 / 60 / 150 bars) and how many of the 9 lookbacks (5-360) are in an up or down breakout. Idea from the SSRN paper 'Catching Crypto Trends'; the thresholds are this dashboard's own.","قنوات Donchian على الإغلاق (20 / 60 / 150 شمعة) وكام فترة من 9 (5-360) في حالة اختراق صاعد أو هابط. الفكرة من ورقة SSRN 'Catching Crypto Trends'، والعتبات من عندنا."), get:() => ch().donOn, set:v => { ch().donOn = v; this.state.don = v; }},
      {id:"zn", label:Lg("Scalp zones (Stoch+RSI)","زونات السكالب (Stoch+RSI)"), tip:Lg("Stoch 5,9,3 with RSI 14. Sell zone 85-90, TP line 50, Buy zone 10-15; SELL/BUY marks when the line leaves a zone. Rebuilt from a screenshot - the original custom indicator is not public.","Stoch 5,9,3 مع RSI 14. منطقة بيع 85-90، خط TP عند 50، منطقة شراء 10-15؛ علامات SELL/BUY لما الخط يخرج من المنطقة. مبني من لقطة شاشة."), get:() => ch().znOn, set:v => { ch().znOn = v; this.state.zn = v; }, sty:"zn", params:[P("k","Stoch K",2,50,1), P("d","Stoch D",1,50,1), P("s","Slowing",1,10,1), P("rl","RSI length",2,50,1), P("sell","Sell level",60,95,1), P("buy","Buy level",5,40,1), P("hp","Height %",1,92,1)]},
      {id:"bso", label:Lg("Bollinger + Stoch + OsMA","بولينجر + Stoch + OsMA"), tip:Lg("Bollinger Bands on the price (20,2) with a pane of Stoch 5,3,3 and OsMA 12,26,9. SELL/BUY marks when Stoch leaves 80/20 and crosses its signal.","بولينجر على السعر (20,2) مع Stoch 5,3,3 وOsMA 12,26,9. علامات SELL/BUY لما Stoch يخرج من 80/20 ويقطع الإشارة."), get:() => ch().bsoOn, set:v => { ch().bsoOn = v; this.state.bso = v; }, sty:"bso", params:[P("bb","BB period",5,100,1), P("dev","BB deviation",0.5,4,0.1), P("k","Stoch K",2,50,1), P("d","Stoch D",1,50,1), P("s","Slowing",1,10,1), P("fast","OsMA fast",2,100,1), P("slow","OsMA slow",2,200,1), P("sig","OsMA signal",1,100,1), P("hp","Height %",1,92,1)], col2:true},
      {id:"bbshow", label:Lg("   ↳ Bollinger bands on the price chart","   ↳ خطوط البولنجر على الشارت"), tip:Lg("Show / hide the Bollinger Bands drawn on the candles. The Stoch + OsMA pane below stays either way (needs 'Bollinger + Stoch + OsMA' turned on).","إظهار / إخفاء خطوط البولنجر على الشموع. الشريط اللي تحت (Stoch + OsMA) بيفضل زي ما هو في الحالتين (لازم 'بولينجر + Stoch + OsMA' يكون شغال)."), get:() => ch().bbShow, set:v => { ch().bbShow = v; this.state.bbShow = v; }},
      {id:"r2", label:Lg("RSI(2) + OsMA (MT5 window 1)","RSI(2) + OsMA (نافذة MT5 رقم 1)"), tip:Lg("Copied from the MT5 phone chart, indicator window 1: RSI period 2 with levels 30 / 20 / 10 / 5 plus 'Moving Average of Oscillator' (Fast EMA 1000, Slow EMA 2, MACD SMA 2000) applied to the RSI data, drawn as green/red bars. With fewer than 2000 bars the signal average runs over the bars available. buy/sell marks when RSI(2) drops under 10 / rises over 90.","منقولة من شارت MT5 على الموبايل، نافذة المؤشر رقم 1: RSI فترة 2 بمستويات 30 / 20 / 10 / 5 مع 'Moving Average of Oscillator' (Fast EMA 1000 وSlow EMA 2 وMACD SMA 2000) مطبّق على بيانات الـ RSI، مرسوم أعمدة خضرا/حمرا. لو الشموع أقل من 2000 المتوسط بيتحسب على المتاح. علامات buy/sell لما RSI(2) ينزل تحت 10 / يطلع فوق 90."), get:() => ch().r2On, set:v => { ch().r2On = v; this.state.r2 = v; }, sty:"r2", params:[P("len","RSI period",2,50,1), P("fast","OsMA Fast EMA",1,3000,1), P("slow","OsMA Slow EMA",1,3000,1), P("sig","MACD SMA",1,3000,1), P("hp","Height %",1,92,1)], col2:true},
      {id:"rm", label:Lg("RSI + MA extremes (92/8)","RSI + MA مع مستويات 92/8"), tip:Lg("RSI 14 with an 8-period MA of the RSI and extreme levels 92 / 8 (also 70/30). SELL/BUY marks when RSI comes back inside from an extreme.","RSI 14 مع متوسط 8 على الـ RSI ومستويات متطرفة 92 / 8 (و70/30). علامات SELL/BUY لما الـ RSI يرجع للداخل من المستوى المتطرف."), get:() => ch().rmOn, set:v => { ch().rmOn = v; this.state.rm = v; }, sty:"rm", params:[P("len","RSI length",2,100,1), P("ma","MA length",1,100,1), P("m1","Extra MA 1 (0 = off)",0,200,1), P("m2","Extra MA 2 (0 = off)",0,200,1), P("m3","Extra MA 3 (0 = off)",0,200,1), P("hi","Upper extreme",70,99,1), P("lo","Lower extreme",1,30,1), P("hp","Height %",1,92,1)], col2:true},
      {id:"macd", label:"MACD", get:() => ch().macdOn, set:v => { ch().macdOn = v; this.state.macd = v; }, sty:"macd", params:[P("fast","Fast",2,100,1), P("slow","Slow",2,200,1), P("sig","Signal",1,100,1), P("hp","Height %",1,92,1)], col2:true},
      {id:"adx", label:"ADX / DMI", get:() => ch().adxOn, set:v => { ch().adxOn = v; this.state.adx = v; }, sty:"adx", params:[P("len","Length",2,100,1), P("lvl","Trend level",10,50,1), P("hp","Height %",1,92,1)]},
      {id:"cci", label:"CCI", get:() => ch().cciOn, set:v => { ch().cciOn = v; this.state.cci = v; }, sty:"cci", params:[P("len","Length",2,200,1), P("hp","Height %",1,92,1)]},
      {id:"psar", label:"Parabolic SAR", get:() => ch().psarOn, set:v => { ch().psarOn = v; this.state.psar = v; }, sty:"psar", col2:true, params:[P("step","Step",0.005,0.1,0.005), P("max","Max",0.05,1,0.05)]},
    ];
    this.indItems = items;   // task 22: the Master button turns these off/on together
    const save = () => { this.state.st = JSON.parse(JSON.stringify(ch().st)); this.state.maL = ch().maL.map(m => Object.assign({}, m)); ch().calcEma(); ch().resize(); Ws.save(); this.ofSync && this.ofSync(); };
    // chart MODES: one click switches a whole indicator set; display options (trade box, divergence lines, table, BB lines) are left alone
    const KEEP = ["sbox","llt","bbshow","div","flow","dot3"];
    const UI = this.indUI = this.indUI || {x:null, y:null, min:false, pin:false};
    const place = () => { if (UI.x != null){ pop.style.left = UI.x + "px"; pop.style.top = UI.y + "px"; } pop.classList.toggle("pin", UI.pin); };
    const head = () => { const h = el("div","ihead"), t = el("span", null, "⠿ ƒx " + Lg("Indicators","المؤشرات")), mn = el("button", null, UI.min ? "▢" : "–"), cl = el("button", null, "×");
      mn.title = Lg("Fold / unfold (the window stays open while you watch the chart)","تصغير / تكبير (النافذة بتفضل مفتوحة وانت بتتابع الشارت)"); cl.title = Lg("Close","إغلاق");
      mn.onclick = e => { e.stopPropagation(); UI.min = !UI.min; UI.pin = true; render(); }; cl.onclick = e => { e.stopPropagation(); UI.pin = false; UI.min = false; pop.style.display = "none"; place(); };
      h.onpointerdown = e => { if (e.target.tagName === "BUTTON") return; e.preventDefault(); e.stopPropagation(); const r0 = pop.getBoundingClientRect(), pr = pop.offsetParent ? pop.offsetParent.getBoundingClientRect() : {left:0, top:0}, dx = e.clientX - r0.left, dy = e.clientY - r0.top;
        const mv = ev => { UI.x = Math.max(0, ev.clientX - pr.left - dx); UI.y = Math.max(0, ev.clientY - pr.top - dy); UI.pin = true; place(); }, up = () => { document.removeEventListener("pointermove", mv); document.removeEventListener("pointerup", up); };
        document.addEventListener("pointermove", mv); document.addEventListener("pointerup", up); };
      h.append(t, mn, cl); return h; };
    const render = () => {
      pop.innerHTML = ""; pop.append(head()); place(); if (UI.min){ const open = items.filter(it => it.open && it.get()); if (!open.length) return; }
      if (!UI.min){ const mr = el("div","irow"); mr.style.cssText = "gap:4px;padding-bottom:6px;border-bottom:1px solid var(--line);margin-bottom:4px"; const ml = el("span","m",Lg("Mode","الوضع")); ml.style.flex = "0 0 100%"; mr.append(ml);
        CHART_MODES.forEach(md => { const b = el("button", null, esc(Lg(md.en, md.ar))); b.title = Lg(md.tipEn, md.tipAr); if (this.state.mode === md.id) b.classList.add("on");
          b.onclick = e => { e.stopPropagation(); items.forEach(it => { if (it.id === "ma") ch().maL.forEach(m => m.on = md.on.includes("ma") && (!md.ma || md.ma.includes(m.len))); else if (!KEEP.includes(it.id)) it.set(md.on.includes(it.id)); }); this.state.mode = md.id; save(); render(); };
          mr.append(b); });
        pop.append(mr); }
      (UI.min ? items.filter(it => it.open && it.get()) : items).forEach(it => {   // folded: only the indicators whose settings are open
        const row = el("div","irow"), cb = el("input"); cb.type = "checkbox"; cb.checked = !!it.get();
        cb.onchange = () => { it.set(cb.checked); if (!KEEP.includes(it.id)) this.state.mode = ""; save(); render(); }; const lb = el("label",null,esc(it.label)); if (it.tip) lb.title = it.tip; lb.onclick = () => { cb.checked = !cb.checked; cb.onchange(); };
        row.append(cb, lb);
        if (it.id === "dot3"){ const g = el("button",null,"⚙"); g.title = T("ofSet"); g.onclick = e => { e.stopPropagation(); Ws.ofPanel(g, this.chart, () => { this.state.st = JSON.parse(JSON.stringify(this.chart.st)); Ws.save(); this.chart.draw(); }); }; row.append(g); }
        { const note = indHelp(it.id) || it.tip; if (note){ const q = el("button",null,"ⓘ"); q.title = lang === "ar" ? "شرح المؤشر" : "What is this?"; q.className = "ihelp"; const nb = el("div","inote"); nb.textContent = note; nb.style.display = it.hOpen ? "block" : "none";
          q.onclick = e => { e.stopPropagation(); it.hOpen = !it.hOpen; nb.style.display = it.hOpen ? "block" : "none"; }; row.append(q); row.after = null; row._note = nb; } }
        if (it.ma){ const g = el("button",null,"⚙"); g.title = T("indSet"); row.append(g); const box = el("div","iset"); box.style.display = it.open ? "flex" : "none"; box.style.flexDirection = "column"; box.style.alignItems = "stretch";
          const build = () => { box.innerHTML = ""; const M = ch().maL;
            M.forEach((m, j) => { const ln = el("div"), on = el("input"), ty = el("select"), per = el("input"), col = el("input"), w = el("select"), d = el("select"), x = el("button",null,"×");
              ln.style.cssText = "display:flex;gap:4px;align-items:center;flex-wrap:nowrap;white-space:nowrap";
              on.type = "checkbox"; on.checked = !!m.on; on.title = Lg("Show this line","إظهار الخط"); on.onchange = () => { m.on = on.checked; cb.checked = ch().maL.some(q => q.on); save(); };
              MA_TYPES.forEach(t => ty.append(Object.assign(el("option"), {value:t, textContent:t}))); ty.value = m.type; ty.title = Lg("SMA / EMA / WMA","SMA / EMA / WMA"); ty.onchange = () => { m.type = ty.value; save(); };
              per.type = "number"; per.min = 1; per.max = 500; per.step = 1; per.value = m.len; per.style.width = "52px"; per.title = Lg("Period","الفترة"); per.onchange = () => { m.len = Math.max(1, Math.min(500, +per.value || m.len)); per.value = m.len; save(); };
              col.type = "color"; col.value = m.color; col.title = T("indColor"); col.oninput = () => { m.color = col.value; save(); };
              [1,1.5,2,3,4].forEach(v => w.append(Object.assign(el("option"), {value:v, textContent:v+"px"}))); w.value = m.w; w.title = T("indWidth"); w.onchange = () => { m.w = +w.value; save(); };
              DASH.forEach(([v,l]) => d.append(Object.assign(el("option"), {value:v, textContent:l}))); d.value = m.dash || ""; d.title = T("indStyle"); d.onchange = () => { m.dash = d.value; save(); };
              x.title = Lg("Remove this line","احذف الخط"); x.onclick = () => { M.splice(j, 1); save(); build(); };
              [on, ty, per, col, w, d, x].forEach(n => n.onpointerdown = e => e.stopPropagation());
              ln.append(on, ty, per, col, w, d, x); box.append(ln); });
            const add = el("button",null,"+ "+Lg("Add MA","أضف متوسط")); add.disabled = M.length >= MA_MAX; add.title = Lg("Up to 7 moving averages","لحد 7 متوسطات"); add.style.alignSelf = "flex-start";
            add.onclick = () => { const k = M.length; M.push({on:true, type:"EMA", len:[50,100,200,10,20,5,30][k] || 14, color:MA_COLS[k % MA_COLS.length], w:1.2, dash:""}); save(); build(); }; box.append(add); };
          build(); g.onclick = () => { it.open = !it.open; box.style.display = it.open ? "flex" : "none"; }; row.append(box);
        }
        else if (it.sty){
          if (SIG_IND.includes(it.sty)){ const sl = el("label","sgl"), sc = el("input"); sc.type = "checkbox"; sc.checked = ch().st[it.sty].sg !== false; sl.title = Lg("Signals: show this indicator's BUY / SELL marks","إشارات: اعرض علامات الشراء/البيع بتاعة المؤشر"); sc.onchange = () => { ch().st[it.sty].sg = sc.checked; save(); }; sl.append(sc, document.createTextNode(Lg("Signals","إشارات"))); sl.onclick = e => e.stopPropagation(); row.append(sl); }
          const g = el("button",null,"⚙"); g.title = T("indSet"); row.append(g); const box = el("div","iset"); box.style.display = it.open ? "flex" : "none";
          const st = () => ch().st[it.sty];
          const col = el("input"); col.type = "color"; col.value = st().color; col.title = T("indColor"); col.oninput = () => { st().color = col.value; save(); };
          box.append(col);
          if (it.col2){ const c2 = el("input"); c2.type = "color"; c2.value = st().color2; c2.title = T("indColor")+" 2"; c2.oninput = () => { st().color2 = c2.value; save(); }; box.append(c2); }
          const w = el("select"); [1,1.5,2,3,4].forEach(v => w.append(Object.assign(el("option"), {value:v, textContent:v+"px"}))); w.value = st().w; w.title = T("indWidth"); w.onchange = () => { st().w = +w.value; save(); }; box.append(w);
          const d = el("select"); DASH.forEach(([v,l]) => d.append(Object.assign(el("option"), {value:v, textContent:l}))); d.value = st().dash || ""; d.title = T("indStyle"); d.onchange = () => { st().dash = d.value; save(); }; box.append(d);
          (it.params || []).forEach(pp => { if (pp.sep){ const h = el("div","isep",esc(pp.label)); box.append(h); return; }
            const l = el("label",null,esc(pp.label)); let n;
            if (pp.opts){ n = el("select"); pp.opts.forEach(([v, t]) => n.append(Object.assign(el("option"), {value:v, textContent:t}))); n.value = String(st()[pp.key]); n.onchange = () => { st()[pp.key] = isNaN(+n.value) || n.value === "" ? n.value : +n.value; save(); }; }
            else if (pp.bool){ n = el("input"); n.type = "checkbox"; n.checked = !!st()[pp.key]; n.onchange = () => { st()[pp.key] = n.checked ? 1 : 0; save(); }; }
            else if (pp.color){ n = el("input"); n.type = "color"; n.value = st()[pp.key] || "#ffffff"; n.oninput = () => { st()[pp.key] = n.value; save(); }; }
            else if (pp.text){ n = el("input"); n.type = "text"; n.value = st()[pp.key] || ""; n.placeholder = pp.ph || ""; n.style.width = "92px"; n.onchange = () => { st()[pp.key] = n.value.trim(); save(); }; }
            else { n = el("input"); n.type = "number"; n.step = pp.free ? "any" : pp.step; if (!pp.free){ n.min = pp.min; n.max = pp.max; } n.value = st()[pp.key]; n.style.width = pp.free ? "80px" : "52px";
              n.onchange = () => { const v = pp.free ? Math.max(0, +n.value || 0) : Math.max(pp.min, Math.min(pp.max, +n.value || st()[pp.key])); n.value = v; st()[pp.key] = v; save(); }; }
            n.onpointerdown = e => e.stopPropagation(); l.append(n); if (pp.tip) l.title = pp.tip; box.append(l); });
          g.onclick = () => { it.open = !it.open; box.style.display = it.open ? "flex" : "none"; };
          [col, w, d].forEach(x => x.onpointerdown = e => e.stopPropagation());
          row.append(box);
        }
        pop.append(row); if (row._note) pop.append(row._note);
      });
    };
    btn.onclick = e => { e.stopPropagation(); if (pop.style.display === "none"){ render(); pop.style.display = "block"; } else pop.style.display = "none"; };
    document.addEventListener("pointerdown", e => { if (pop.style.display !== "none" && !(this.indUI && this.indUI.pin) && !pop.contains(e.target) && e.target !== btn) pop.style.display = "none"; });
    pop.onpointerdown = e => e.stopPropagation(); this.body.append(pop); this.indPop = pop;
    return btn;
  }
  setTf(tf){
    this.tfSel.value = tf; if (this.mtfRow) this.mtfRow.querySelectorAll("button").forEach(b => b.classList.toggle("on", b.dataset.tf === tf));
    this.state.tf = tf; this.chart.tf = tf; this.chart.data = []; this.chart.draw(); this.resub(); Ws.save();
  }
  tickCd(){
    const d = this.chart.data; if (!d.length) { this.cdEl.textContent = ""; return; }
    let rem = candleRem(d[d.length-1].t, this.state.tf);
    const sec = Math.floor(rem/1000), h = Math.floor(sec/3600), m = Math.floor(sec%3600/60), ss = sec%60;
    this.cdEl.textContent = "⏱ " + (h ? h+":"+pad2(m)+":"+pad2(ss) : pad2(m)+":"+pad2(ss));   // DOM text only: no full chart repaint each second
  }
  syncMarks(){
    const ch = this.chart, d = ch.data; if (!d.length || !this.flt) return;
    const rows = d.slice(-14), atr = rows.reduce((a,k) => a + (k.h - k.l), 0)/rows.length || 0, now = nowS(), out = [];
    this.flt.events.filter(e => now - e.t < Math.max(15, (ch.st.flow.age|0) || 120)*60000 && (e.ev === "ABSORB" || e.ev === "FILLED")).slice(0, 12).forEach(e => {
      if (e.ev === "ABSORB"){ const dir = e.side === "ask" ? -1 : 1; out.push({t:e.t, p:e.p, kind:"absorb", dir, tgt:e.p + dir*1.5*atr}); }
      else out.push({t:e.t, p:e.p, kind:"sweep", dir:e.side === "bid" ? -1 : 1});
    });
    // one mark per kind/side/price zone: repeats within 0.35 ATR (and 6 candles) collapse into one with a count
    const ded = [], sec = (TFSEC[this.state.tf] || 60)*1000, tf = this.state.tf;
    out.sort((a,b) => b.t - a.t).forEach(m => { const o = ded.find(x => x.kind === m.kind && x.dir === m.dir && Math.abs(x.p - m.p) <= 0.35*atr && Math.abs(x.t - m.t) <= 6*sec); if (o) o.n = (o.n || 1) + 1; else ded.push(Object.assign({tf}, m)); });
    ch.marks = ded; this.syncTick(); ch.draw();
  }
  /* ORDER-FLOW SYNC: order book + time & sales + limit tracking agree at the same moment.
     book  = bid vs ask size within 0.5 % of the mid (latest snapshot), light when |imbalance| >= st.sync.book
     tape  = aggressor buy vs sell volume of the last 2 min of prints, light when |delta| >= st.sync.tape
     limits= big-order events of the last st.sync.win s: bid placed / ask pulled / ask filled / absorption at the bid = +1, mirror = -1; light when |net| >= st.sync.lim
     All three the same side -> a setup: entry = last price, stop = 1 ATR14 (chart <= 5m) else 0.25 %, target = rr x risk, expiry st.sync.exp min (then marked to market).
     Outcomes are followed live in this browser and kept per symbol (LS_sync_SYM, last 300): a forward test, not a backtest. */
  syncTick(){
    const ch = this.chart, d = ch.data; if (!ch.syncOn || !d.length || !this.flt) return;
    const now = nowS(), S = ch.st.sync, G = ch.gaugeData(now), sym = this.state.sym, px = d[d.length-1].c;
    { const cx = Ctx.cache[sym]; if (!cx || now - cx.t > 60000) Ctx.get(sym); }
    const book = G.bk ? G.bk.v : null, tape = G.tr ? G.tr.v : null; let lim = 0, nl = 0;
    this.flt.events.forEach(e => { if (now - e.t > (S.win || 60)*1000) return; const v = e.ev === "PLACED" ? (e.side === "bid" ? 1 : -1) : e.ev === "PULLED" ? (e.side === "bid" ? -1 : 1) : e.ev === "FILLED" ? (e.side === "ask" ? 1 : -1) : e.ev === "ABSORB" ? (e.side === "bid" ? 1 : -1) : 0; lim += v; if (v) nl++; });
    const sg = (v, th) => v == null ? 0 : v >= th ? 1 : v <= -th ? -1 : 0, L = [sg(book, +S.book || .15), sg(tape, +S.tape || .2), nl ? sg(lim, +S.lim || 1) : 0];
    const dir = L.every(x => x === 1) ? 1 : L.every(x => x === -1) ? -1 : 0;
    if (!this._syncSym || this._syncSym !== sym){ this._syncSym = sym; this.syncLogArr = store.get(LS+"_sync_"+sym, []); this._syncLast = 0; }
    const log = this.syncLogArr; let dirty = false;
    log.forEach(t => { if (t.res != null) return; const r1 = Math.abs(t.en - t.sl) || 1e-9;
      if (t.dir > 0 ? px <= t.sl : px >= t.sl){ t.res = -1; t.t1 = now; dirty = true; }
      else if (t.dir > 0 ? px >= t.tp : px <= t.tp){ t.res = +S.rr || 1.5; t.t1 = now; dirty = true; }
      else if (now - t.t > (S.exp || 60)*60000){ t.res = Math.round((px - t.en)*t.dir/r1*100)/100; t.t1 = now; dirty = true; } });
    if (dir && (now - (this._syncLast || 0) > (S.cool || 3)*60000 || this._syncDir !== dir)){
      const rows = d.slice(-15); let atr = 0; for (let i = 1; i < rows.length; i++) atr += Math.max(rows[i].h - rows[i].l, Math.abs(rows[i].h - rows[i-1].c), Math.abs(rows[i].l - rows[i-1].c)); atr /= Math.max(1, rows.length - 1);
      const risk = Math.max(px*.0005, (TFSEC[this.state.tf] || 60) <= 300 ? atr : px*.0025);
      log.push({t:now, dir, en:px, sl:px - dir*risk, tp:px + dir*risk*(+S.rr || 1.5), tf:this.state.tf, k:[book, tape, lim].map(v => v == null ? null : Math.round(v*100)/100), ctx:Ctx.snapshot(sym, dir > 0 ? "bullish" : "bearish")});
      if (log.length > 300) log.splice(0, log.length - 300); this._syncLast = now; this._syncDir = dir; dirty = true; }
    if (dirty) store.set(LS+"_sync_"+sym, log);
    ch.sync = {book, tape, lim, nl, L, dir, t:now, cx:Ctx.cache[sym] || null}; ch.syncLog = log;
  }
  setOverlay(o){ if (o && o.plan && !planOk(o.plan, o.dir)){ console.warn("plan direction mismatch - not drawn", o.dir, o.plan); o = null; } this.chart.overlay = o; this.chart.showSig = true; this.state.sig = true; this.chart.draw(); }
  showPx(price, src){
    if (!(price > 0)) return;
    const prev = this.lastPx; this.lastPx = price; this.pxEl.textContent = fmtP(price);
    this.pxEl.style.color = prev == null || price === prev ? "var(--txt)" : price > prev ? TH.up : TH.dn;
    if (prev != null && price !== prev){ this.pxEl.classList.remove("nb","ns"); void this.pxEl.offsetWidth; this.pxEl.classList.add(price > prev ? "nb" : "ns"); }
    this.updEl.textContent = (src === "ws" ? "● WS " : "● ") + hms(Date.now());
  }
  liveTick(row){
    const ch = this.chart; if (!ch.data.length) return;
    const last = ch.data[ch.data.length-1];
    if (row.t === last.t) Object.assign(last, row); else if (row.t > last.t) ch.data.push(row); else return;
    ch.calcEma(); if (ch.autoCenter) ch.followLatest(); ch.drawSoon(); this.showPx(row.c, "ws");
  }
  parseC(rows){ return rows.map(x => ({t:+x[0], o:+x[1], h:+x[2], l:+x[3], c:+x[4], v:+x[5]})).reverse(); }
  resub(){
    if (this.type !== "chart") return;
    clearTimeout(this.timer); const tok = this.tok = (this.tok||0)+1, sym = this.state.sym, tf = this.state.tf;
    { const lk = (this.state.locks || {})[sym] || null; if (lk !== this.chart.lockR){ this.chart.lockR = lk; this.chart.yZoom = 1; this.chart.yShift = 0; } }   // the price-scale lock belongs to its symbol: another symbol starts unlocked (its range is absolute prices)
    this.chart.srData = null;   // S/R levels belong to the symbol: never draw the previous symbol's levels while the new one loads
    this.msg.textContent = ""; this.chart.data = []; this.chart.draw(); this.noMore = false; this.lastPx = null;
    this.unwatch && this.unwatch(); this.wsUnsubs = [];
    { const ch = this.chart; ch.wom = {snaps:[]}; if (ch.colWide > 0) OFM.restore(this, sym, tok);   // the wide column's book history belongs to its symbol: a new symbol starts empty (or from its saved copy)
      const iv = setInterval(() => { if (tok !== this.tok){ clearInterval(iv); return; } if (ch.colWide > 0 && !document.hidden && ch.wom.snaps.length > 4) OFM.save(sym, ch.wom.snaps); }, 20000); this.wsUnsubs.push(() => clearInterval(iv)); }
    const chan = "candle"+okxBar(tf), subMin = TFSEC[tf] < 60;
    this.chart.loadDraws(LS+"_dr_"+sym);
    if (this.jsub) Journal.subs.delete(this.jsub);
    this.jsub = () => { if (!this.chart) return; this.chart.sigs = Journal.list.filter(t => t.symbol === sym && t.t0).map(t => ({t:t.t0, dir:t.dir, pct:t.pct, tfk:t.tfk, status:t.status})); this.chart.jtr = Journal.list.filter(t => t.symbol === sym && t.t0); this.chart.draw(); }; Journal.subs.add(this.jsub); this.jsub();
    { const sc = CFG.scan && CFG.scan[sym] && CFG.scan[sym][tf];   // the scanner result for exactly this symbol AND this chart timeframe (a plan from another timeframe may point the other way)
      this.chart.overlay = (sc && planOk(sc.plan, sc.dir) && passFilters(sc.dir, sc.ttype)) ? sc : null; } this.chart.marks = [];
    this.flt = {prev:null, events:[], sym, abs:new Set()};
    this.chart.liqs = []; { const seenL = new Set(); let liqT = 0;
      this.liqKick = async () => { if (tok !== this.tok || !this.chart.liqOn || !liqFam(sym)) return; liqT = Date.now();
        try { const out = await okxLiqs(sym); if (tok !== this.tok) return; (out || []).forEach(r => { const k = r.t+"|"+r.p+"|"+r.usd; if (!seenL.has(k)){ seenL.add(k); this.chart.liqs.push(r); } });
          if (this.chart.liqs.length > 3000) this.chart.liqs = this.chart.liqs.slice(-3000); this.chart.draw(); } catch(e){} };
      const lqIv = setInterval(() => { if (tok !== this.tok){ clearInterval(lqIv); return; } if (this.chart.liqOn && Date.now() - liqT > 15000) this.liqKick(); }, 2000); this.wsUnsubs.push(() => clearInterval(lqIv)); }
    this.chart.lvD = null; const lvIv = setInterval(() => { if (tok !== this.tok){ clearInterval(lvIv); return; } if (this.chart.lvOn && Date.now() - (this.lvT || 0) > 30000){ this.lvT = Date.now(); this.lvKick(); } }, 1500); this.wsUnsubs.push(() => clearInterval(lvIv)); this.chart.llD = null; const llIv = setInterval(() => { if (tok !== this.tok){ clearInterval(llIv); return; } if (this.chart.llOn && Date.now() - (this.llT || 0) > 30000){ this.llT = Date.now(); this.llKick(); } }, 1500); this.wsUnsubs.push(() => clearInterval(llIv));
    this.chart.fp = new Map(); this.chart.bub = []; this.chart.dom = new Map(); this.chart.flowB = []; this.chart.flowT = []; this.chart.sym = sym; const seenF = new Set();
    this.wsUnsubs.push(Hub.sub("book", sym, b => { if (b.error || tok !== this.tok) return; this.chart.domAdd(b); if (this.chart.domOn || this.chart.vpOn) this.chart.drawData(); }));
    this._fpRdy = 0; this._fpI = null; let fcov = [], fvEnd = 0, fpend = [];   // a new subscription (symbol / timeframe change) starts from the store again   // known-complete ranges (from the store + this panel), end of what this panel verified, prints waiting to be stored
    const frec = r => { if (FPS.off) return; fpend.push([r.t, r.p, r.q, r.side]); if (fpend.length > 60000) fpend.splice(0, 20000); };
    this.wsUnsubs.push(Hub.sub("trades", sym, p => { if (p.error || tok !== this.tok) return; const ch = this.chart;
      if (!this._fpRdy){ if (this.fpInit) this.fpInit(); return; }   // the store is read first: prints are re-sent by the next poll, so none is lost, and none is counted twice
      (p.rows || []).slice().sort((a,b) => a.t-b.t).forEach(r => { if (seenF.has(r.id) || FPS.span(fcov, r.t)) return; seenF.add(r.id); if (ch._fpLoadedMax && +r.id <= ch._fpLoadedMax) return; frec(r); ch.fpAdd(r); }); if (ch.fpOn || ch.deltaOn || ch.vpOn) ch.drawData(); }));
    this.fpSave = () => { try { const ch = this.chart, d = ch.data; if (!ch.fpOn || !d.length || /^(HL:|Y:)/.test(sym)) return; const bars = [];   // the newest FP_BARS bars, with their rows: another tab or a refresh starts from this instead of from nothing
        for (let i = Math.max(0, d.length - FP_BARS); i < d.length; i++){ const m = ch.fp.get(d[i].t); if (m && m.px.size) bars.push([d[i].t, m.b, m.s, m.part ? 1 : 0, [...m.px].map(([pp, v]) => [pp, v.b, v.s])]); }
        if (bars.length) localStorage.setItem(LS+"_fp|"+sym+"|"+tf, JSON.stringify({t:Date.now(), max:ch._fpMax || 0, bars})); } catch(e){} };
    this.fpLoad = () => { const ch = this.chart; ch._fpLd = 1; let mx = 0; try { const o = JSON.parse(localStorage.getItem(LS+"_fp|"+sym+"|"+tf) || "null"); if (!o || Date.now() - o.t > 4*3600000) return 0; const have = new Set(ch.data.map(k => k.t));
        o.bars.forEach(([t, b, sl, part, px]) => { if (!have.has(t) || ch.fp.has(t)) return; ch.fp.set(t, {px:new Map(px.map(([pp, bb, ss]) => [pp, {b:bb, s:ss}])), b, s:sl, part:!!part}); });
        mx = o.max || 0; ch._fpMax = Math.max(ch._fpMax || 0, mx); ch._fpLoadedMax = mx; ch.drawData(); } catch(e){} return mx; };
    { const fpIv = setInterval(() => { if (tok !== this.tok){ clearInterval(fpIv); return; } if (!document.hidden) this.fpSave(); }, 20000); this.wsUnsubs.push(() => clearInterval(fpIv)); }
    this.fpInit = () => {   // read the stored footprint of this symbol once (the live handler waits for it): older candles come from the store, a refresh no longer starts empty
      if (this._fpI) return this._fpI; const ch = this.chart; if (!ch.data.length) return null; const hl = /^(HL:|Y:)/.test(sym), ms = (TFSEC[tf] || 0)*1000;
      return this._fpI = (hl ? Promise.resolve(null) : (ms >= FPS.MIN ? FPS.loadSrv : FPS.load)(sym, Math.max(ch.data[0].t, Date.now() - FPS.KEEP))).then(o => { if (tok !== this.tok) return;
        if (o && o.cov.length){ if (ms >= FPS.MIN){ fcov = o.cov; FPS.fold(o.mins, ch, ms, fcov, fvEnd); } ch._fpLd = 1; ch._fpLoadedMax = 0; } else if (!ch._fpLd) this.fpLoad();   // empty or unusable store: the old 4-hour snapshot
        this._fpRdy = 1; this.fpMark(); }); };
    this.fpMark = () => { const ch = this.chart; FPS.mark(ch, (TFSEC[tf] || 0)*1000, fcov, fvEnd); const sp = fvEnd ? FPS.span(fcov, fvEnd) : null; ch.fpCov = sp ? sp[0] : 0; ch.draw(); };
    const fcommit = async (from, to) => {   // prints in (from, to] are now known to be complete: store them, mark the range known
      if (!(to > from) || /^(HL:|Y:)/.test(sym)) return; const take = fpend.filter(x => x[0] <= to); fpend = fpend.filter(x => x[0] > to);
      await FPS.commit(sym, take, from, to); if (tok !== this.tok) return; fcov = FPS.join(fcov, from, to); fvEnd = Math.max(fvEnd, to); this.fpMark(); };
    this.fpSync = async (stopT, maxPg, pace, idFloor) => {   // newest-first through history-trades until a print falls in a known range (everything newer is then fetched), is older than stopT, or is covered by the snapshot
      const ch = this.chart; let after = "", newest = 0, oldest = Infinity, from = null;
      for (let pg = 0; pg < maxPg && from === null; pg++){ if (tok !== this.tok || !ch.fpOn) return {cancel:true};
        let rows; try { rows = await okx("/market/history-trades?instId="+encodeURIComponent(sym)+"&type=1&limit=100"+(after ? "&after="+after : "")); } catch(e){ this._fpBackoff = Date.now() + 60000; break; } if (!rows || !rows.length) break;
        for (const x of rows){ const t = +x.ts, sp = FPS.span(fcov, t); if (t > newest) newest = t;
          if (sp){ from = sp[1]; break; } if (t < stopT){ from = stopT - 1; break; } if (idFloor && +x.tradeId <= idFloor){ from = Math.min(oldest, t); break; }
          oldest = Math.min(oldest, t); if (seenF.has(x.tradeId)) continue; seenF.add(x.tradeId); const r = {id:x.tradeId, t, p:+x.px, q:+x.sz, side:x.side === "buy" ? "Buy" : "Sell"}; frec(r); ch.fpAdd(r, true); }
        ch.drawData(); after = rows[rows.length-1].tradeId; if (from === null) await new Promise(r => setTimeout(r, pace)); }
      if (!newest) return null; return {from: from === null ? oldest : from, to: newest, capped: from === null}; };   // ran out of pages: only what was fetched is claimed, the rest stays "partial"
    this.fpFill = async () => {   // footprint of the newest candles: the store holds the past, this fills the rest from OKX history-trades (newest first, back to the stored range or the FP_BARS-th candle)
      if (tok !== this.tok || /^(HL:|Y:)/.test(sym) || this._fpFilled === sym+"|"+tf) return; const ch = this.chart, d = ch.data; if (d.length < 3) return; this._fpFilled = sym+"|"+tf;
      await this.fpInit(); if (tok !== this.tok) return;
      const r = await this.fpSync(d[Math.max(0, d.length - FP_BARS)].t, FP_PAGES, 180, ch._fpLoadedMax || 0);
      if (r && r.cancel){ this._fpFilled = null; return; } if (r) await fcommit(r.from, r.to); this.fpMark(); };
    this.fpCatch = async () => {   // the live tape poll (100 prints / poll) can miss prints on a busy market: page back until a print is inside the verified range, so the newest candle is complete and the gap-free range grows
      if (tok !== this.tok || /^(HL:|Y:)/.test(sym) || this._fpCatching || Date.now() < (this._fpBackoff || 0)) return; const ch = this.chart; if (!ch.fpOn || !ch.data.length) return; this._fpCatching = true;
      try { const r = await this.fpSync(0, 25, 250, 0); if (r && !r.cancel) await fcommit(r.from, r.to); } finally { this._fpCatching = false; } };
    { const fcIv = setInterval(() => { if (tok !== this.tok){ clearInterval(fcIv); return; } if (!document.hidden && this.chart.fpOn && this._fpFilled === sym+"|"+tf) this.fpCatch(); }, 30000); this.wsUnsubs.push(() => clearInterval(fcIv)); }
    if (this.chart.fpOn) setTimeout(() => this.fpFill && this.fpFill(), 2500);
    this.wsUnsubs.push(Hub.sub("book", sym, b => { if (b.error) return; const tp = Hub.last["trades|"+sym]; limitUpdate(this.flt, b, tp && !tp.error ? tp.rows : null); this.syncMarks(); }));
    this.wsUnsubs.push(Hub.sub("trades", sym, p => { if (!p.error){ absorbEvents(this.flt, p.rows); this.syncMarks(); } }));
    if (subMin){
      const sec = TFSEC[tf], seen = new Set(); let firstB = true, hist = false;
      const smtIv = setInterval(() => { if (tok !== this.tok){ clearInterval(smtIv); return; } if (this.chart.smtOn && Date.now() - (this.smtT || 0) > 8000) this.smtKick(); }, 1500); this.wsUnsubs.push(() => clearInterval(smtIv));
      this.wsUnsubs.push(Hub.sub("trades", sym, p => {
        if (tok !== this.tok || p.error) return;
        const ch = this.chart, doApply = !(firstB && hist && ch.data.length);
        (p.rows || []).slice().sort((a,b) => a.t-b.t).forEach(r => {
          if (seen.has(r.id)) return; seen.add(r.id); if (!doApply) return;
          const b = Math.floor(r.t/(sec*1000))*sec*1000, last = ch.data[ch.data.length-1];
          if (last && b === last.t){ last.h = Math.max(last.h, r.p); last.l = Math.min(last.l, r.p); last.c = r.p; last.v += r.q; }
          else if (!last || b > last.t) ch.data.push({t:b, o:r.p, h:r.p, l:r.p, c:r.p, v:r.q});
        });
        firstB = false; if (ch.data.length){ ch.calcEma(); if (ch.data.length < 3) ch.fit(); else if (!ch.r) { if (!ch.restoreView()) ch.fit(); else ch.draw(); } else ch.draw(); this.showPx(ch.data[ch.data.length-1].c, "rest"); }
      }));
      (async () => {
        try {
          const d = await okx("/market/candles?instId="+encodeURIComponent(sym)+"&bar=1s&limit=300");
          if (tok !== this.tok) return;
          const rows = this.parseC(d), agg = [];
          rows.forEach(k => { const b = Math.floor(k.t/(sec*1000))*sec*1000, l = agg[agg.length-1];
            if (l && l.t === b){ l.h = Math.max(l.h,k.h); l.l = Math.min(l.l,k.l); l.c = k.c; l.v += k.v; } else agg.push({t:b,o:k.o,h:k.h,l:k.l,c:k.c,v:k.v}); });
          hist = agg.length > 0; if (hist) this.chart.setData(agg, true);
        } catch(e){ if (tok !== this.tok) return;
          const why = "No second-level history here (" + (e.message||e) + ")";
          // a seconds timeframe the source does not have (Hyperliquid, or an OKX symbol without 1s candles) shows 1m candles instead of a blank chart.
          // A network blip, rate limit or timeout keeps the timeframe: it only shows the message
          if (!/^(HL:|Y:)/.test(sym) && !/not available|unsupported|not support|Parameter|51000|51001/i.test(String(e.message||e))){ this.msg.textContent = why; return; }
          this.state.tf = "1m"; this.chart.tf = "1m"; this.tfSel.value = "1m"; this.resub(); this.msg.textContent = why + " - showing 1m candles"; }
      })();
    } else if (!TF_AGG[tf])
    this.wsUnsubs.push(WSX.sub("business", {channel:chan, instId:sym}, data => {
      if (tok !== this.tok) return; const k = data[0]; this.liveTick({t:+k[0], o:+k[1], h:+k[2], l:+k[3], c:+k[4], v:+k[5]});
    }));
    this.wsUnsubs.push(WSX.sub("public", {channel:"tickers", instId:sym}, data => {
      if (tok !== this.tok || !this.chart.data.length) return;
      const px = +data[0].last, ch = this.chart, last = ch.data[ch.data.length-1];
      if (!(px > 0)) return;
      last.c = px; last.h = Math.max(last.h, px); last.l = Math.min(last.l, px); ch.calcEma(); ch.drawSoon(); this.showPx(px, "ws");
    }));
    this.unwatch = () => { (this.wsUnsubs||[]).forEach(u => u()); this.wsUnsubs = []; };
    if (subMin){ this.unwatch = () => { (this.wsUnsubs||[]).forEach(u => u()); this.wsUnsubs = []; }; return; }
    let fails = 0;   // first paint = ONE request ("quick"); the history walk runs afterwards in the background; failed first loads back off 2 s -> 4 -> 8 -> 15 s
    const fillHist = async () => { if (this._fillTok === tok) return; this._fillTok = tok;
      try { const full = await candlesTf(sym, tf, true); if (tok !== this.tok || !full.length) return; const cur = this.chart.data;
        if (cur.length && full[0].t < cur[0].t){ const old = full.filter(k => k.t < cur[0].t); if (old.length){ this.chart.r += old.length; this.chart.setData(old.concat(cur), false); } } } catch(e){} };
    const loop = async first => {
      if (tok !== this.tok) return;
      if (first && !fails && !this.chart.data.length) this.msg.textContent = T("loading");
      if (first && !this.chart.data.length){ const cc = CandleCache.get(sym, tf); if (cc){ this.chart.setData(cc, true); this.chart.draw(); this.msg.textContent = ""; this._ccShown = true; } }   // open instantly with the last candles seen in this browser (marked stale until the real answer arrives)
      try {
        const rows = await Promise.race([candlesTf(sym, tf, first ? "quick" : false), new Promise((_, rj) => setTimeout(() => rj(new Error("timeout")), 25000))]);
        if (tok !== this.tok) return;
        this._okAt = Date.now(); setStatus(true); this.msg.textContent = "";
        if (rows.length) this.showPx(rows[rows.length-1].c, "rest");
        if (this.chart.smtOn && Date.now() - (this.smtT || 0) > 8000){ this.smtT = Date.now(); this.smtFetch(sym, tf, tok); }
        fails = 0;
        if (first){
          this._ccShown = false; this.chart.setData(rows, true); fillHist(); CandleCache.put(sym, tf, rows); this.syncSR && this.syncSR();
          const v = this._refreshView;
          if (v && v.sym === sym && v.tf === tf && this.chart.data.length && !this.chart.autoCenter){ this.chart.bw = v.bw; this.chart.yZoom = v.yZoom; this.chart.yShift = v.yShift; this.chart.r = (this.chart.data.length-1) - v.back; this.chart.clampR(); this.chart.saveView(); this.chart.draw(); }
          this._refreshView = null;
        }
        else {
          const data = this.chart.data.slice();
          { const lastT = data.length ? data[data.length-1].t : 0, step = (TFSEC[tf] || 60)*1000, now = Date.now(), ga = this._gapAt = (this._gapAt || []).filter(x => now - x < 600000);
            if (lastT && rows.length && rows[0].t > lastT + 2*step && ga.length < 2){   // saved / old candles + fresh ones = a hole in the chart (owner 2026-11-05, 15m gold): drop the old ones and load the whole history again
              ga.push(now); CandleCache.drop(sym, tf); this.chart.data = []; clearTimeout(this.timer); return loop(true); } }
          rows.forEach(k => { const j = data.length ? data.findIndex(z => z.t === k.t) : -1; if (j >= 0) data[j] = k; else if (!data.length || k.t > data[data.length-1].t) data.push(k); });
          this.chart.setData(data, false);
        }
      } catch(e){
        if (!isRL(e)) setStatus(false); this.msg.textContent = isRL(e) ? offTxt(sym, e) : offTxt(sym, e)+" ("+(e.message||e)+")";
        { const d = this.chart.data, lt = d.length ? d[d.length-1].t : 0, ag = lt ? Date.now() - lt : 0; if (lt && ag > 3*(TFSEC[tf] || 60)*1000 + 60000) this.msg.textContent += " · ⚠ "+Lg("the last candle shown is ", "آخر شمعة معروضة من ")+ageTxt(ag)+Lg(" old: this price is NOT live", " فاتت: السعر ده مش حي"); }   // owner 2026-11-05: charts showed saved candles (~90 off the live price) with only a small rate-limit line
        const sd = CFG.seed;
        if (sd && sd.sym === sym && sd.tf === tf && !this.chart.data.length){ this.chart.setData(sd.rows.map(x => ({t:x[0],o:x[1],h:x[2],l:x[3],c:x[4],v:x[5]})), true); this.msg.textContent += " — showing saved snapshot"; }
      }
      if (!this.chart.data.length) fails++;
      this.timer = setTimeout(() => loop(!this.chart.data.length), !this.chart.data.length && fails ? Math.min(15000, 2000*Math.pow(2, fails-1)) : (this.state.rf || (/^HL:/.test(sym) ? hlPoll(tf) : 2000)));   // Hyperliquid: 6 s (its request weight is limited per minute; 4 gold charts polling every 2 s alone were ~1500 of 1200)
    };
    this.kick = () => { if (tok !== this.tok) return; clearTimeout(this.timer); loop(!this.chart.data.length); };   // restart the polling right now (tab came back, network came back)
    loop(true);
  }
  async smtFetch(sym, tf, tok){
    const pr = smtPeers(sym); if (!pr.length){ this.chart.smtD = null; this.chart.smtName = Lg("no correlated pair for "+sym, "لا يوجد زوج مرتبط"); this.chart.draw(); return; }
    const sel = pr.find(x => x[0] === this.state.smtPeer) || pr[0]; this.chart.smtName = sel[0]; this.chart.smtInv = sel[1];
    this.chart.smtName = sel[0]+(this.chart.smtD ? "" : " (loading...)"); const sec = TFSEC[tf], sub = sec < 60;
    try { let rows = sub ? this.parseC(await okx("/market/candles?instId="+encodeURIComponent(sel[0])+"&bar=1s&limit=300")) : await candlesTf(sel[0], tf, true, 150); if (tok !== this.tok) return;
      if (sub){ const agg = []; rows.forEach(k => { const b = Math.floor(k.t/(sec*1000))*sec*1000, l = agg[agg.length-1]; if (l && l.t === b){ l.h = Math.max(l.h,k.h); l.l = Math.min(l.l,k.l); l.c = k.c; l.v += k.v; } else agg.push({t:b,o:k.o,h:k.h,l:k.l,c:k.c,v:k.v}); }); rows = agg; }
      this.chart.smtD = rows; this.chart.smtName = sel[0]; this.chart.draw(); } catch(e){ this.chart.smtName = sel[0]+" (peer data failed: "+(e.message||e)+")"; this.chart.draw(); }
  }
  lvKick(){ if (this.type !== "chart") return; const sym = this.state.sym, tok = this.tok, bars = {"4H":"4H","D":"1Dutc","W":"1Wutc","M":"1Mutc"};
    Promise.all(Object.entries(bars).map(async ([k, b]) => { try { const rows = this.parseC(await okx("/market/candles?instId="+encodeURIComponent(sym)+"&bar="+b+"&limit=2")); return rows.length >= 2 ? [k, {prev:rows[rows.length-2], cur:rows[rows.length-1]}] : null; } catch(e){ return null; } }))
      .then(r => { if (tok !== this.tok) return; const o = {}; r.forEach(x => { if (x) o[x[0]] = x[1]; }); this.chart.lvD = Object.keys(o).length ? o : null; this.chart.draw(); }); }
  llKick(){ if (this.type !== "chart") return; const sym = this.state.sym, tok = this.tok;   // higher-timeframe candles for the MTF LLT indicator, shared by every chart of the same symbol (one request set per 25 s, one after the other): four gold charts used to send 24 requests at once and made Hyperliquid rate-limit the whole page
    llFetch(sym).then(o => { if (tok !== this.tok) return; if (o){ this.chart.llD = o; this.chart.llErr = 0; } else { this.chart.llErr = Date.now(); this.llT = Date.now() - 20000; const g = LLC.get(sym); if (g && g.v && !this.chart.llD) this.chart.llD = g.v; }   // keep the last good data on a failure and retry in ~10 s
      this.chart.draw(); }); }
  smtKick(){ if (this.type !== "chart" || !this.chart.smtOn) return; this.smtT = Date.now(); this.smtFetch(this.state.sym, this.state.tf, this.tok); }
  async loadMore(){
    if (this.loadingMore || this.noMore || !this.chart.data.length) return; if (TF_AGG[this.state.tf]){ this.noMore = true; return; }
    this.loadingMore = true; const tok = this.tok;
    try {
      const oldest = this.chart.data[0].t;
      const d = await okx("/market/history-candles?instId="+encodeURIComponent(this.state.sym)+"&bar="+okxBar(this.state.tf)+"&after="+oldest+"&limit=100");
      if (tok === this.tok){
        const rows = this.parseC(d);
        if (!rows.length) this.noMore = true;
        else { const ch = this.chart; ch.r += rows.length; ch.setData(rows.concat(ch.data), false); }
      }
    } catch(e){ this.noMore = true; }
    this.loadingMore = false;
  }
  destroy(){ clearTimeout(this.timer); clearInterval(this.cdTimer); clearInterval(this.flowIv); clearInterval(this.animTimer); this.tok = -1; this.chart && this.chart.destroy(); this.unwatch && this.unwatch(); }

  /* ---- DOM ---- */
  build_dom(){
    const tb = el("div","tb"); this.symSel = this.symSelect(); tb.append(this.symSel);
    const gm = () => (this.state.gstep = this.state.gstep || {});   // price grouping, saved per symbol in the panel state
    this.gSel = groupSelect(gm()[this.state.sym], 0, v => { gm()[this.state.sym] = v; Ws.save(); this.gRedraw && this.gRedraw(); }); tb.append(this.gSel);
    { const lv = el("select"); lv.title = Lg("Levels shown on each side","عدد المستويات على كل جهة"); [6, 12, 20, 30, 40].forEach(n => { const o = el("option", null, String(n)); o.value = n; lv.append(o); }); lv.value = String(this.state.dlev || 12);
      lv.onchange = () => { this.state.dlev = +lv.value; Ws.save(); this.gRedraw && this.gRedraw(); }; ["mousedown", "pointerdown", "click", "wheel"].forEach(ev => lv.addEventListener(ev, e => e.stopPropagation())); tb.append(lv);
      const cu = el("button", null, "Σ"); cu.title = Lg("Cumulative size from the best price outward","الحجم التراكمي من أفضل سعر للخارج"); cu.classList.toggle("on", !!this.state.dcum); cu.onclick = () => { this.state.dcum = !this.state.dcum; cu.classList.toggle("on", !!this.state.dcum); Ws.save(); this.gRedraw && this.gRedraw(); }; tb.append(cu); }
    tb.append(Ws.fmtBtn(), Ws.ftBtn());
    this.domBox = el("div"); this.body.append(tb, this.domBox); this.resub();
  }
  /* ---- tape ---- */
  winSelect(key, def){
    const sel = el("select"); sel.title = T("win");
    [["1m",60000],["5m",300000],["15m",900000],["1h",3600000],["all",0]].forEach(([l,v]) => { const o = el("option"); o.value = v; o.textContent = l; sel.append(o); });
    sel.value = this.state[key] != null ? this.state[key] : def; sel.onchange = () => { this.state[key] = +sel.value; Ws.save(); this.rerender && this.rerender(); };
    return sel;
  }
  build_tape(){
    const tb = el("div","tb"); this.symSel = this.symSelect(); tb.append(this.symSel, this.winSelect("win", 300000), Ws.fmtBtn());
    const sg = el("button", null, "⚙"); sg.title = lang === "ar" ? "حساسية ذكي / كبير / امتصاص" : "Smart / Big / Absorb sensitivity"; sg.onclick = e => { e.stopPropagation(); Ws.sensPop(sg); }; tb.append(sg);
    const hd = el("div","hdr"); this.statBox = el("div"); this.depthCv = el("canvas"); this.depthCv.width = 240; this.depthCv.height = 84; this.depthCv.style.cssText = "width:120px;height:42px;flex:none;background:#0b0e11;border-radius:3px";
    hd.append(this.statBox, this.depthCv);
    this.tapeBox = el("div"); this.legBox = el("div","legend"); this.legBox.textContent = T("legend");
    this.body.append(tb, hd, this.tapeBox, this.legBox); bindColResize(this, this.tapeBox, "tape", TAPE_COLS); this.resub();
  }
  build_ofm(){ OFM.build(this); }
  /* ---- limits ---- */
  build_limits(){
    const tb = el("div","tb"); this.symSel = this.symSelect(); tb.append(this.symSel, this.winSelect("lwin", 900000), Ws.fmtBtn());
    const seg = el("div","seg"); this.fltBtns = {};
    [["all","fAll"],["bid","fBid"],["ask","fAsk"],["abs","fAbs"]].forEach(([k,l]) => { const b = el("button",null,T(l)); b.onclick = () => { this.state.flt = k; Object.entries(this.fltBtns).forEach(([kk,bb]) => bb.classList.toggle("on", kk===k)); Ws.save(); this.rerender(); }; this.fltBtns[k] = b; seg.append(b); });
    this.state.flt = this.state.flt || "all"; this.fltBtns[this.state.flt].classList.add("on"); tb.append(seg);
    this.evBox = el("div"); this.body.append(tb, this.evBox); bindColResize(this, this.evBox, "lim", LIM_COLS); this.resub();
  }
  /* ---- watchlist ---- */
  build_watch(){
    const tb = el("div","tb"), inp = el("input"), go = el("button",null,"+");
    inp.placeholder = T("addsym"); inp.style.flex = "1"; inp.style.minWidth = "0";
    const add = () => {
      const v = inp.value.trim().toUpperCase().replace("/","-");
      const hl = "HL:xyz:"+v.replace(/^(HL:)?XYZ:/, "");   // "GOLD", "xyz:GOLD", "SP500" -> Hyperliquid market when it exists
      if (HL.q[hl]){ addSym(hl); inp.value = ""; return; }
      if (!SYM_RE.test(v)) return; addSym(v); inp.value = "";
    };
    const addSym = v => { if (!SYMS.includes(v)){ SYMS.push(v); extraSyms.push(v); store.set(LS+"_syms", extraSyms); } Ws.panels.forEach(p => p.type === "watch" && p.resub()); };
    // ---- OKX universe: every USDT / USDC instrument OKX lists, grouped by category, "top N by 24h volume" ----
    const uni = el("div","uni"); uni.style.display = "block"; const ub = el("button",null,"🌐"); ub.title = T("uniTip");
    const U = this.state.u = Object.assign({type:"SPOT", quote:"USDT", cat:(Object.keys(YF).length ? "__mine" : "All"), top:10}, this.state.u || {});   // Yahoo markets are not in OKX's universe -> "My list" by default
    const selU = (opts, key) => { const x = el("select"); opts.forEach(([v,l]) => x.append(Object.assign(el("option"), {value:v, textContent:l}))); x.value = U[key]; x.onchange = () => { U[key] = isNaN(+x.value) ? x.value : +x.value; Ws.save(); loadU(); }; return x; };
    const uTb = el("div","tb"), uBox = el("div"); const catSel = el("select"); catSel.onchange = () => { U.cat = catSel.value; if (!U.cat.startsWith("__")){ const want = U.cat === "Options" ? "OPTION" : /^(Crypto|Meme)/.test(U.cat) ? "SPOT" : (U.cat === "All" ? U.type : (U.type === "SPOT" ? "SWAP" : U.type)); if (want !== U.type){ U.type = want; typeSel.value = want; if (!/^(Crypto|Meme|All)/.test(U.cat)) U.quote = "ALL"; Ws.save(); return loadU(); } } Ws.save(); renderU(); };
    const typeSel = selU([["SPOT",Lg("Spot","فوري")],["SWAP",Lg("Perp (swap)","دائم (Swap)")],["FUTURES",Lg("Futures","آجلة")],["OPTION",Lg("Options","خيارات")]], "type");
    uTb.append(typeSel, selU([["ALL",Lg("All quotes","كل العملات المقابلة")],["USDT","USDT"],["USDC","USDC"],["USD","USD"]], "quote"), catSel, selU([[5,"Top 5"],[10,"Top 10"],[20,"Top 20"],[50,"Top 50"],[100,"Top 100"],[9999,"All"]], "top"));
    // technical filters (team task 10): closes from OKX 1H candles, top-30 by volume only, cached 5 min
    const TECH_OPTS = [["none",Lg("Technical: off","فني: مقفول")],["rsiLo","RSI(14) < 30"],["rsiHi","RSI(14) > 70"],["aboveEma",Lg("Price > EMA20 (1H)","السعر > EMA20 (ساعة)")],["belowEma",Lg("Price < EMA20 (1H)","السعر < EMA20 (ساعة)")],["brkUp",Lg("Breakout: close > 20-bar high (1H)","اختراق: إغلاق > أعلى 20 شمعة (ساعة)")]];
    const techC = new Map(); let techBusy = false;
    const techCalc = cl => {   // cl: closes, oldest first; null when there is not enough history
      if (cl.length < 35) return null;
      let g = 0, l = 0; for (let i = 1; i <= 14; i++){ const d = cl[i] - cl[i-1]; g += Math.max(d, 0); l += Math.max(-d, 0); } g /= 14; l /= 14;
      for (let i = 15; i < cl.length; i++){ const d = cl[i] - cl[i-1]; g = (g*13 + Math.max(d, 0))/14; l = (l*13 + Math.max(-d, 0))/14; }
      const k = 2/21; let ema = cl[0]; for (let i = 1; i < cl.length; i++) ema = cl[i]*k + ema*(1-k);
      const last = cl[cl.length-1], prevHi = Math.max(...cl.slice(-21, -1));
      return {rsi: l === 0 ? 100 : 100 - 100/(1 + g/l), ema20: ema, last, brkUp: last > prevHi};
    };
    const loadTech = ids => Promise.all(ids.map(id => okx("/market/candles?instId="+id+"&bar=1H&limit=100").then(k => { const cl = k.map(r => +r[4]).reverse(); techC.set(id, {t: Date.now(), v: techCalc(cl)}); }).catch(() => techC.set(id, {t: Date.now(), v: null}))));
    const techFilter = (rows) => {
      const tf = U.tech; if (!tf || tf === "none") return rows;
      const top = rows.slice(0, 30), stale = top.filter(x => !techC.has(x.id) || Date.now() - techC.get(x.id).t > 300000).map(x => x.id);
      if (stale.length && !techBusy){ techBusy = true; loadTech(stale).then(() => { techBusy = false; renderU(); }); }
      return top.filter(x => { const e = techC.get(x.id), v = e && e.v; if (!v) return false;
        return tf === "rsiLo" ? v.rsi < 30 : tf === "rsiHi" ? v.rsi > 70 : tf === "aboveEma" ? v.last > v.ema20 : tf === "belowEma" ? v.last < v.ema20 : v.brkUp; });
    };
    uTb.append(selU(TECH_OPTS, "tech"));
    uni.append(uTb, uBox); let rowsU = [], cats = [];
    const CAT = {"1":"Crypto","3":"Stocks","4":"Commodities","5":"Forex","6":"Bonds"}, METAL = ["XAU","XAG","XPT","XPD","XAUT","PAXG"], ENERGY = ["CL","WTI","BRENT","XTI","XBR","NG","NATGAS","OIL","UKOIL","USOIL","HO","RB"], INDEX = ["SPX","NDX","DJI","US500","US100","US30","SPX500","NAS100","DAX","GER40","FTSE","UK100","HSI","N225","JP225","VIX","SPY","QQQ","IWM","DIA","VOO","IVV"];
    const MEMEB = (CFG.meme || []).map(s => s.split("-")[0]), catOf = (i, base) => (METAL.includes(base) ? "Metals" : ENERGY.includes(base) ? "Oil & Gas" : INDEX.includes(base) ? "Indices" : MEMEB.includes(base) ? "Meme coins" : CAT[i.instCategory]) || "Crypto";
    const renderU = () => {
      uBox.innerHTML = ""; this.uSyms = []; this.uMeta = {};
      if (U.cat.startsWith("__")){ this.uTitle = ""; this.wRender && this.wRender(Hub.last["tickers|all"]); return; }
      const yfCat = y => /\.CA$|^Y:\^CASE30$/.test(y) ? "Egypt (EGX)" : /\.SR$/.test(y) ? "Saudi (Tadawul)" : /=X$/.test(y) ? "Forex" : /^Y:\^/.test(y) ? "Indices" : "", yfRows = Object.keys(YF).filter(y => yfCat(y) === U.cat).map(y => ({id:y, vol:1e18, cat:U.cat}));   // Yahoo markets (not in OKX): candles were embedded for the page-level Asset class
      if (/^(Egypt|Saudi)/.test(U.cat) && !yfRows.length){ uBox.innerHTML = '<div class="err" style="color:#f0b90b">'+esc(lang === "ar" ? "السوق ده بييجي من Yahoo: اختار \""+U.cat+"\" من قايمة Asset class فوق (Chart Scanner) وارجع هنا." : "This market comes from Yahoo: pick \""+U.cat+"\" in the Asset class dropdown (Chart Scanner tab), then come back.")+'</div>'; this.wRender && this.wRender(Hub.last["tickers|all"]); return; }
      const hlRows = HL.list.filter(x => x.cat === U.cat).sort((a, b) => b.vol - a.vol).map(x => ({id:x.id, vol:3e18 + x.vol, cat:x.cat}));
      if (!HL.t && !/^error/.test(HL.state) && /^(Forex|Metals|Oil & Gas|Indices|Stocks|Bonds|Commodities)$/.test(U.cat)) setTimeout(() => renderU(), 1500);   // Hyperliquid list still loading
      yfRows.unshift(...hlRows);
      const fhRows = CFG.fhToken ? FH_LIST.filter(x => x.cat === U.cat && !fhDup(x.id)).map(x => ({id:x.id, vol:2e18, cat:x.cat})) : [];
      yfRows.unshift(...fhRows.filter(f => !yfRows.some(y => y.id === f.id)));
      const r = techFilter(yfRows.concat(rowsU.filter(x => (U.cat === "All" || x.cat === U.cat || (U.cat === "Metals" && x.cat === "Commodities")))).sort((a,b) => b.vol - a.vol).slice(0, U.top));
      if (!r.length && /^error/.test(HL.state) && /^(Forex|Metals|Oil & Gas|Indices|Stocks|Bonds)$/.test(U.cat)){ uBox.innerHTML = '<div class="err">'+esc(Lg("Hyperliquid (live gold / oil / indices / FX) is not reachable right now: ", "Hyperliquid (ذهب / بترول / مؤشرات / فوركس لحظي) مش متاح دلوقتي: ")+HL.state.replace(/^error: /, "")+Lg(" - retrying every 4 s.", " - بيحاول تاني كل 4 ثواني."))+'</div>'; }
      else if (!r.length) uBox.innerHTML = '<div class="err" style="color:#848e9c">'+esc((U.cat === "Forex" || U.cat === "Indices") ? (lang === "ar" ? "\""+U.cat+"\" بييجي من Yahoo: اختاره من قايمة Asset class فوق (Chart Scanner) وارجع هنا." : "\""+U.cat+"\" comes from Yahoo: pick it in the Asset class dropdown (Chart Scanner tab), then come back.") : T("uniNone"))+'</div>';
      this.uSyms = r.map(x => x.id); r.forEach(x => this.uMeta[x.id] = x); this.uTitle = [U.type, U.quote, U.cat === "All" ? T("fAll") : U.cat, "Top "+(U.top > 5000 ? "All" : U.top)].join(" · ");
      this.wRender && this.wRender(Hub.last["tickers|all"]);   // the symbols simply load into the live list below
      Hub.extra = new Set([...(Hub.extra || []), ...this.uSyms]); Hub.kick("tickers|all");   // fetch the new category now, not in 3 s
    };
    const loadU = async () => {
      uBox.innerHTML = '<div class="err" style="color:#848e9c">'+esc(T("loading"))+'</div>';
      try {
        const OU = ["BTC-USD","ETH-USD"], isO = U.type === "OPTION", q_ = p => isO ? Promise.all(OU.map(u => okx(p+"&uly="+u).catch(() => []))).then(a => a.flat()) : okx(p);
        const [tk, ins] = await Promise.all([q_("/market/tickers?instType="+U.type), q_("/public/instruments?instType="+U.type)]);
        const meta = {}; ins.forEach(i => meta[i.instId] = i);
        rowsU = tk.filter(x => (isO || U.quote === "ALL" || x.instId.split("-")[1] === U.quote) && meta[x.instId]).map(x => { const base = x.instId.split("-")[0], last = +x.last, o = +x.open24h;
          return {id:x.instId, last, chg:o ? (last-o)/o*100 : 0, vol:isO ? (+x.vol24h || 0) : (+x.volCcy24h || 0) * (U.type !== "SPOT" ? last : 1), cat:isO ? "Options" : catOf(meta[x.instId], base)}; });
        cats = [...new Set(rowsU.map(x => x.cat).concat(["Crypto","Forex","Metals","Oil & Gas","Commodities","Indices","Stocks","Bonds","Options","Meme coins","Egypt (EGX)","Saudi (Tadawul)"]))]; catSel.innerHTML = ""; [["__fav", lang === "ar" ? "★ المفضلة" : "★ Favorites"], ["__mine", lang === "ar" ? "قائمتي" : "My list"]].forEach(([v, l]) => catSel.append(Object.assign(el("option"), {value:v, textContent:l}))); ["All"].concat(cats).forEach(c => catSel.append(Object.assign(el("option"), {value:c, textContent:c === "All" ? T("fAll") : catL(c)})));
        if (CFG.cls && U.ucls !== CFG.cls){   // the page-level Asset class dropdown sets the default once; the selectors here stay usable
          U.ucls = CFG.cls; U.cat = CFG.cls; if (!/^(Crypto|Meme)/.test(CFG.cls)) U.quote = "ALL"; const want = CFG.cls === "Options" ? "OPTION" : /^(Crypto|Meme)/.test(CFG.cls) ? "SPOT" : "SWAP";
          if (U.type !== want){ U.type = want; typeSel.value = want; Ws.save(); return loadU(); } Ws.save(); }
        catSel.value = U.cat; renderU();
      } catch(e){ if (Object.keys(YF).length){ rowsU = []; U.cat = CFG.cls || U.cat; renderU(); uBox.insertAdjacentHTML("afterbegin", '<div class="err">'+esc(T("offline"))+'</div>'); return; } uBox.innerHTML = '<div class="err">'+esc(T("offline"))+'</div>'; }   // OKX universe down: the Yahoo markets (embedded in the page) still list
    };
    ub.onclick = () => { const on = uni.style.display === "none"; uni.style.display = on ? "block" : "none"; if (on) loadU(); };
    loadU();   // selectors + list are part of the watchlist itself
    go.onclick = add; inp.onkeydown = e => { if (e.key === "Enter") add(); };
    const favB = el("button",null,"★"); favB.title = lang === "ar" ? "المفضلة فقط" : "Favorites only"; favB.onclick = () => { if (U.cat === "__fav"){ U.cat = this.state.prevCat || "__mine"; } else { this.state.prevCat = U.cat; U.cat = "__fav"; } catSel.value = U.cat; favB.style.color = U.cat === "__fav" ? "#f0b90b" : ""; Ws.save(); loadU(); }; favB.style.color = U.cat === "__fav" ? "#f0b90b" : "";
    this.state.wtf = "1H"; // AMD select removed from the watchlist (team task 9); AMD column stays on 1H
    HL.start();
    const fhS = el("span","m"); fhS.style.cssText = "font-size:10px;white-space:nowrap"; if (CFG.fhToken){ FH.start(); const upd = () => { const n = Object.keys(FH.q).length; fhS.textContent = "FH "+(FH.state === "live" ? "● "+n+"/"+FH_LIST.length : FH.state); fhS.title = Lg("Finnhub live CFD feed: symbols with at least one tick / total","مصدر Finnhub اللحظي: الرموز اللي وصلها سعر / الإجمالي"); }; upd(); this.fhUpd = upd; }   // refreshed with every ticker snapshot (wRender), so it survives resub()
    const hlS = el("span","m"); hlS.style.cssText = "font-size:10px;white-space:nowrap"; const hlUpd = () => { hlS.textContent = "HL "+(HL.state === "live" ? "● "+HL.list.length : HL.state === "rest" ? "◐ "+HL.list.length : HL.state); hlS.title = Lg("Hyperliquid TradFi feed: ● websocket live, ◐ REST every 4 s; number = markets listed","مصدر Hyperliquid: ● لحظي websocket، ◐ كل 4 ثواني؛ الرقم = عدد الأسواق"); };
    hlUpd(); const fu0 = this.fhUpd; this.fhUpd = () => { hlUpd(); fu0 && fu0(); };
    tb.append(inp, go, favB, ub, fhS, hlS); this.wBox = el("div"); this.body.append(tb, uni, this.wBox); this.resub();
  }
  /* ---- links bar ---- */
  build_links(){
    const box = el("div","lk"); (CFG.links || []).forEach(l => {
      if (!/^https?:\/\//.test(l.url||"")) return;
      const a = el("a",null,esc(l.name)); a.href = l.url; a.target = "_blank"; a.rel = "noopener noreferrer"; box.append(a);
      if (l.patterns){ const sel = el("select"); sel.append(Object.assign(el("option"), {textContent:"▾ patterns", value:""}));
        l.patterns.forEach(p => sel.append(Object.assign(el("option"), {textContent:p.name, value:p.url})));
        sel.onchange = () => { if (/^https:\/\//.test(sel.value)) window.open(sel.value, "_blank", "noopener"); sel.value = ""; }; box.append(sel); }
    });
    this.body.append(box);
  }
  /* ---- news ticker ---- */
  build_ticker(){
    const items = worldItems().filter(n => n.headline); this.body.style.overflow = "hidden";
    if (!items.length){ this.body.innerHTML = '<div class="err">'+esc(feedMsg() || T("nonews"))+'</div>'; return; }
    const half = Math.ceil(items.length/2), rows = items.length > 3 ? [items.slice(0,half), items.slice(half)] : [items];
    rows.forEach((r, ri) => {
      const mq = el("div","mq"+(ri ? " rev" : "")), tr = el("div","tr");
      const mk = () => r.map(n => '<span class="it"><span class="sr">'+esc(n.source||"")+'</span> '+esc(n.headline)+'</span>').join("");
      tr.innerHTML = mk()+mk(); tr.style.setProperty("--d", Math.max(30, r.reduce((a,n)=>a+n.headline.length,0)*0.45)+"s");
      const idx = []; r.forEach(n => idx.push(n)); const its = () => tr.querySelectorAll(".it");
      its().forEach((e,i) => e.onclick = () => this.tickerPop(idx[i % idx.length]));
      mq.append(tr); this.body.append(mq);
    });
  }
  tickerPop(n){
    const old = this.body.querySelector(".pop"); old && old.remove();
    const safe = /^https?:\/\//i.test(n.url||"") ? n.url : "", p = el("div","pop");
    p.innerHTML = '<button class="x">✕</button> <b>'+esc(n.headline)+'</b><div class="m">'+esc(n.source||"")+(n.datetime ? " · "+esc(n.datetime) : "")+'</div><p>'+esc(n.summary||"")+'</p>'+(safe ? '<a class="link" target="_blank" rel="noopener noreferrer" href="'+esc(safe)+'">'+esc(T("read"))+' ↗</a>' : "");
    p.querySelector(".x").onclick = () => p.remove(); this.body.append(p);
  }
  /* ---- alerts ---- */
  build_alerts(){
    const F = this.state.af = Object.assign({tf:"", tt:"", dir:""}, this.state.af || {});
    const tb = el("div","tb"), clr = el("button",null,T("clear")); clr.onclick = () => Alerts.clear();
    const mkSel = (key, opts) => { const s2 = el("select"); opts.forEach(([v,l]) => { const o = el("option",null,esc(l)); o.value = v; s2.append(o); }); s2.value = F[key]; s2.onchange = () => { F[key] = s2.value; Ws.save(); draw(); }; return s2; };
    tb.append(mkSel("dir", [["",T("fAll")],["bullish",Lg("Long","شراء")],["bearish",Lg("Short","بيع")]]),
      mkSel("tt", [["",T("fAll")],["Scalp",Lg("Scalp","سكالب")],["Day Trade",Lg("Day","داي")],["Swing",Lg("Swing","سوينج")],["Position",Lg("Position","بوزشن")]]),
      mkSel("tf", [["",T("fAll")]].concat(TFK_OPTS)), (() => { const c2 = el("select"); clsOptions().forEach(([v,l]) => c2.append(Object.assign(el("option"), {value:v, textContent:l}))); CLS_SELS.add(c2); CLS_SELS.add(c2); c2.title = Lg("Market class","فئة السوق"); c2.value = FILT.cls || "All"; c2.onchange = () => { FILT.cls = c2.value; clsBroadcast(); store.set(LS+"_filt", FILT); Alerts.subs.forEach(f => f()); Setup.subs.forEach(f => f()); }; return c2; })(), clr);
    this.aBox = el("div"); this.body.append(tb, this.aBox);
    const draw = () => {
      const now = Date.now();
      const rows = Alerts.list.filter(a => a.card && passFilters(a.card.direction, a.card.ttype) && (!F.tf || a.card.tfk === F.tf) && (!F.tt || a.card.ttype === F.tt) && (!F.dir || a.card.direction === F.dir) && clsOk(a.card.symbol))
        .sort((x,y) => (y.card.score - x.card.score) || (y.t - x.t));
      { const seenG = new Set(); for (let i = 0; i < rows.length; i++){ const c = rows[i].card, g = c.symbol+"|"+c.direction+"|"+c.ttype; if (seenG.has(g)){ rows.splice(i--, 1); } else seenG.add(g); } }   // same symbol + side + type = one card
      this.aBox.innerHTML = "";
      if (!rows.length){ this.aBox.innerHTML = '<div class="err" style="color:#848e9c">'+esc(T("noalerts"))+'</div>'; return; }
      rows.forEach(a => this.aBox.append(alertCard(a)));
    };
    draw(); Alerts.subs.add(draw); Journal.subs.add(draw); this.unwatch = () => { Alerts.subs.delete(draw); Journal.subs.delete(draw); };
  }
  /* ---- ready trades (scanner trades + alerts, best confidence first) ---- */
  build_ready(){
    const sideSel = el("select"), ttSel = el("select"), snd = el("input");
    [["All",T("fAll")],["Long",Lg("Long","شراء")],["Short",Lg("Short","بيع")]].forEach(([v,l]) => sideSel.append(Object.assign(el("option"), {value:v, textContent:l})));
    [["All",T("fAll")],["Scalp",Lg("Scalp","سكالب")],["Day Trade",Lg("Day","داي")],["Swing",Lg("Swing","سوينج")],["Position",Lg("Position","بوزشن")]].forEach(([v,l]) => ttSel.append(Object.assign(el("option"), {value:v, textContent:l})));
    const tfSel = el("select"); [["All",T("fAll")]].concat(TFK_OPTS).forEach(([v,l]) => tfSel.append(Object.assign(el("option"), {value:v, textContent:l}))); tfSel.title = lang === "ar" ? "الفريم" : "Timeframe"; tfSel.value = FILT.tf || "All"; tfSel.onpointerdown = e => e.stopPropagation(); tfSel.onchange = () => { FILT.tf = tfSel.value; sv(); };
    const clsSel = el("select"); clsOptions().forEach(([v,l]) => clsSel.append(Object.assign(el("option"), {value:v, textContent:l}))); CLS_SELS.add(clsSel); clsSel.title = Lg("Market class","فئة السوق"); clsSel.value = FILT.cls || "All"; clsSel.onpointerdown = e => e.stopPropagation(); clsSel.onchange = () => { FILT.cls = clsSel.value; clsBroadcast(); store.set(LS+"_filt", FILT); Alerts.subs.forEach(f => f()); Setup.subs.forEach(f => f()); };
    sideSel.value = FILT.side; ttSel.value = FILT.tt; snd.type = "checkbox"; snd.title = T("sound"); snd.checked = this.state.snd !== false;
    [sideSel, ttSel, snd].forEach(x => x.onpointerdown = e => e.stopPropagation());
    const sv = () => { store.set(LS+"_filt", FILT); draw(); Alerts.subs.forEach(f => f()); };
    sideSel.onchange = () => { FILT.side = sideSel.value; sv(); }; ttSel.onchange = () => { FILT.tt = ttSel.value; sv(); };
    snd.onchange = () => { this.state.snd = snd.checked; Ws.save(); };
    const stBtn = el("button"); stBtn.style.cssText = "font-size:11px;padding:1px 6px"; stBtn.onpointerdown = e => e.stopPropagation(); this.stBtn = stBtn;
    const stTxt = () => { stBtn.textContent = (lang === "ar" ? "استراتيجيات: " : "Strategies: ") + (FILT.st.length ? FILT.st.length : (lang === "ar" ? "الكل" : "All")) + " ▾"; };
    stTxt(); stBtn.onclick = e => { e.stopPropagation(); Ws.stratPop(stBtn, () => { stTxt(); sv(); }); };
    this.head.insertBefore(stBtn, this.ttl.nextSibling); this.head.insertBefore(snd, stBtn); this.head.insertBefore(ttSel, snd); this.head.insertBefore(sideSel, ttSel); this.head.insertBefore(tfSel, ttSel); this.head.insertBefore(clsSel, tfSel);
    const box = el("div","rdy"); this.body.append(box); this.body.style.overflow = "auto";
    const TFC = TFC_ALL;
    const spark = (e, long_) => { const v = e.spark || []; if (v.length < 2) return ""; const pl = e.plan, all = v.concat([pl.stop, pl.tps[0]]), lo = Math.min(...all), hi = Math.max(...all), W = 64, H = 20;
      const y = p => H-2-(p-lo)/((hi-lo)||1)*(H-4), pts = v.map((p,i) => (i*W/(v.length-1)).toFixed(1)+","+y(p).toFixed(1)).join(" ");
      return '<svg width="'+W+'" height="'+H+'"><polyline points="'+pts+'" fill="none" stroke="#9aa3ad" stroke-width="1"/><line x1="0" x2="'+W+'" y1="'+y(pl.stop)+'" y2="'+y(pl.stop)+'" stroke="#f6465d" stroke-dasharray="2 2"/><line x1="0" x2="'+W+'" y1="'+y(pl.tps[0])+'" y2="'+y(pl.tps[0])+'" stroke="#0ecb81" stroke-dasharray="2 2"/></svg>'; };
    const collect = readyList;
    const beep = () => { try { const ac = Ws.ac || (Ws.ac = new (window.AudioContext || window.webkitAudioContext)()); if (ac.state === "suspended") ac.resume();
      [0, .16].forEach((d, i) => { const o = ac.createOscillator(), g = ac.createGain(); o.frequency.value = i ? 1175 : 880; g.gain.value = .06; o.connect(g); g.connect(ac.destination); o.start(ac.currentTime+d); o.stop(ac.currentTime+d+.12); }); } catch(e){} };
    document.addEventListener("pointerdown", () => { try { Ws.ac && Ws.ac.resume(); } catch(e){} }, {once:true});
    const seenKeys = new Set(store.get(LS+"_rdseen", [])); let first = true;
    const draw = () => {
      const rows = collect(); box.innerHTML = "";
      if (!rows.length){ box.innerHTML = '<div class="err" style="color:#848e9c">'+esc(CFG.scanning ? T("scanning") : T("rdEmpty"))+'</div>'; return; }
      let h = '<table class="rdt"><tr><th>'+esc(T("symbol"))+'</th><th>'+esc(T("rdType"))+'</th><th>'+esc(T("rdSetup"))+'</th><th></th><th>'+esc(T("stop"))+'</th><th>TP1</th><th>'+esc(T("rdStr"))+'</th><th></th></tr>';
      rows.slice(0, 40).forEach((e, i) => {
        const long_ = e.direction === "bullish", pct = Math.round(100*e.score/Math.max(1,e.max)), col = pct >= 70 ? "#0ecb81" : pct >= 50 ? "#f0b90b" : "#848e9c";
        h += '<tr data-i="'+i+'"><td><b>'+esc(e.symbol)+'</b> <span class="m">'+esc(e.tfk||"")+'</span> <span style="color:'+(long_?"#0ecb81":"#f6465d")+';font-weight:700">'+esc(long_ ? T("long") : T("short"))+'</span> <button class="ana" title="'+esc(lang === "ar" ? "التحليل" : "Analysis")+'">ⓘ</button></td>'
          +'<td style="color:#f0b90b">'+esc(ttTxt(e.ttype))+'</td><td>'+(e.tags||[]).slice(0,4).map(t => '<a class="tg" target="_blank" rel="noopener noreferrer" href="'+esc(/^https:\/\//.test(e.tv||"") ? e.tv : "#")+'" title="'+esc(tagTip(t))+'" style="background:'+esc(t[1])+';color:'+esc(t[2])+'">'+esc(tagTxt(t[0]))+'</a>').join("")+'</td>'
          +'<td>'+spark(e, long_)+'</td><td style="color:#f6465d">'+fmtP(e.plan.stop)+'</td><td style="color:#0ecb81">'+fmtP(e.plan.tps[0])+'</td>'
          +'<td><span class="bar"><i style="width:'+pct+'%;background:'+col+'"></i></span> '+pct+'%<div class="m" style="font-size:10px" title="'+esc(lang === "ar" ? "نسبة ضرب الهدف الأول تاريخياً لهذه الاستراتيجية على هذا التايم فريم" : "Historical TP1 hit-rate of this strategy on this timeframe")+'">'+esc(tfTxt(e))+'</div></td><td><a class="tg" target="_blank" rel="noopener noreferrer" href="'+esc(/^https:\/\//.test(e.tv||"") ? e.tv : "#")+'" style="border:1px solid #2b3139;color:#4aa3ff">TV</a></td></tr>';
      });
      box.innerHTML = h+'</table>';
      box.querySelectorAll("tr[data-i]").forEach(tr => { const e = rows[+tr.dataset.i]; if (!e) return; const an = e.ana, lines = an && an.sig && an.sig.length ? an.sig : (e.tags || []).map(t => "["+t[0]+"] "+(t[3] || "")); tr.title = (lang === "ar" ? "التحليل (اضغط على التحليل للتفاصيل):\n" : "Analysis (click Analysis for details):\n")+lines.slice(0, 4).join("\n")+(an && an.scen && an.scen.length ? "\n"+an.scen[0] : ""); });   // hover = quick why-this-trade
      box.querySelectorAll("tr[data-i]").forEach(tr => tr.onclick = ev => { if (ev.target.closest("a")) return; const e = rows[+tr.dataset.i]; if (ev.target.closest(".ana")){ ev.stopPropagation(); Ws.anaPop(ev.target.closest(".ana"), e); return; } Ws.showOnChart(Object.assign({tfc: TFC[e.tfk] || "1H"}, e)); });
      // sound once for a NEW 50%+ trade (never on the first paint after load)
      const fresh = rows.filter(e => 100*e.score/e.max >= 50 && !seenKeys.has(e.symbol+"|"+e.direction+"|"+e.tfk+"|"+e.score));
      fresh.forEach(e => seenKeys.add(e.symbol+"|"+e.direction+"|"+e.tfk+"|"+e.score));
      if (fresh.length){ store.set(LS+"_rdseen", [...seenKeys].slice(-400)); if (!first && this.state.snd !== false) beep(); }
      first = false;
    };
    draw(); Alerts.subs.add(draw); this.unwatch = () => Alerts.subs.delete(draw);
  }
  /* ---- Fibonacci levels (named ratio presets, editable) ---- */
  build_fib(){
    const PRE = FIB_PRESETS, S = this.state;
    S.fp = S.fp || "Retracement"; S.fdir = S.fdir || "long"; S.fon = S.fon || {};
    const top = el("div","tb"), pSel = el("select"), dSel = el("select"), hi = el("input"), lo = el("input"), auto = el("button",null,T("fibAuto")), show = el("button",null,T("showchart")), clr = el("button",null,"✕");
    Object.keys(PRE).forEach(k => pSel.append(Object.assign(el("option"), {value:k, textContent:k}))); pSel.value = S.fp;
    [["long","▲ "+T("long")],["short","▼ "+T("short")]].forEach(([v,l]) => dSel.append(Object.assign(el("option"), {value:v, textContent:l}))); dSel.value = S.fdir;
    [hi, lo].forEach(i => { i.type = "number"; i.step = "any"; i.style.width = "88px"; }); hi.placeholder = T("fibHi"); lo.placeholder = T("fibLo"); hi.value = S.hi || ""; lo.value = S.lo || "";
    top.append(pSel, dSel, hi, lo, auto, show, clr);
    const rt = el("textarea"); rt.style.cssText = "width:100%;height:34px;resize:vertical;margin:2px 0"; rt.title = T("fibRatios");
    const box = el("div","fibv"); this.body.append(top, rt, box); this.body.style.overflow = "auto";
    const ratios = () => (S.fr || PRE[S.fp] || []);
    const fmt = v => isFinite(v) ? fmtP(v) : "–";
    const price = r => { const A = S.fdir === "long" ? +S.lo : +S.hi, B = S.fdir === "long" ? +S.hi : +S.lo; return B + (A - B)*r; };
    const rows = () => ratios().map(r => ({r, p:price(r), on:S.fon[r] !== false}));
    const push = () => { const ch = Ws.panels.find(p => p.type === "chart"); if (ch) { ch.chart.fibLv = rows().filter(x => x.on && isFinite(x.p)).map(x => ({r:x.r, p:x.p})); ch.chart.draw(); } };
    const draw = () => {
      rt.value = ratios().join(", "); box.innerHTML = "";
      const t = el("table","rdt"); t.innerHTML = "<tr><th></th><th>"+esc(T("fib"))+"</th><th>"+esc(T("price"))+"</th></tr>";
      rows().forEach(x => { const tr = el("tr"); tr.innerHTML = '<td><input type="checkbox" '+(x.on?"checked":"")+'></td><td style="color:'+(x.r < 0 ? "#0ecb81" : x.r > 1 ? "#f6465d" : "#f0b90b")+'">'+x.r+'</td><td>'+fmt(x.p)+'</td>';
        tr.querySelector("input").onchange = e => { S.fon[x.r] = e.target.checked; Ws.save(); push(); }; t.append(tr); });
      box.append(t); push();
    };
    const upd = () => { S.hi = hi.value; S.lo = lo.value; Ws.save(); draw(); };
    pSel.onchange = () => { S.fp = pSel.value; delete S.fr; Ws.save(); draw(); }; dSel.onchange = () => { S.fdir = dSel.value; Ws.save(); draw(); };
    hi.onchange = lo.onchange = upd;
    rt.onchange = () => { const a = rt.value.split(/[ ,;]+/).map(Number).filter(v => isFinite(v) && rt.value.trim() !== ""); if (a.length){ S.fr = a; Ws.save(); } draw(); };
    auto.onclick = () => { const ch = Ws.panels.find(p => p.type === "chart"); const d = ch && ch.chart.data.slice(-120); if (!d || d.length < 5) return;
      let H = -Infinity, L = Infinity, hx = 0, lx = 0; d.forEach((c,i) => { if (c.h > H){ H = c.h; hx = i; } if (c.l < L){ L = c.l; lx = i; } });
      S.hi = H; S.lo = L; S.fdir = lx < hx ? "long" : "short"; hi.value = H; lo.value = L; dSel.value = S.fdir; Ws.save(); draw(); };
    show.onclick = push; clr.onclick = () => { const ch = Ws.panels.find(p => p.type === "chart"); if (ch){ ch.chart.fibLv = null; ch.chart.draw(); } };
    draw();
  }
  /* ---- Signals: ONE central list of every live signal (scanner trades + alerts), searchable, sortable, with its plan ---- */
  build_signals(){
    const F = this.state.sg = Object.assign({q:"", side:"", tf:"", min:0, sort:"pct", dir:-1}, this.state.sg || {});
    const tb = el("div","tb"), q = el("input"), side = el("select"), tf = el("select"), mn = el("select"), cnt = el("span","m");
    q.type = "search"; q.placeholder = T("sgSearch"); q.value = F.q; q.style.width = "140px";
    [["",T("sgAny")],["bullish",Lg("Long","شراء")],["bearish",Lg("Short","بيع")]].forEach(([v,l]) => side.append(Object.assign(el("option"), {value:v, textContent:l}))); side.value = F.side;
    [["",T("sgAny")]].concat(TFK_OPTS).forEach(([v,l]) => tf.append(Object.assign(el("option"), {value:v, textContent:l}))); tf.value = F.tf;
    [0,40,50,60,70,80].forEach(v => mn.append(Object.assign(el("option"), {value:v, textContent:v ? T("sgMin")+" "+v+"%" : T("sgMin")}))); mn.value = String(F.min);
    const cl = el("select"); clsOptions().forEach(([v,l]) => cl.append(Object.assign(el("option"), {value:v, textContent:l}))); CLS_SELS.add(cl); cl.title = Lg("Market class","فئة السوق"); cl.value = FILT.cls || "All"; cl.onchange = () => { FILT.cls = cl.value; clsBroadcast(); store.set(LS+"_filt", FILT); Alerts.subs.forEach(f => f()); Setup.subs.forEach(f => f()); draw(); };
    [q, side, tf, mn, cl].forEach(x => x.onpointerdown = e => e.stopPropagation());
    tb.append(q, side, tf, mn, cl, cnt); const box = el("div","rdy"); this.body.append(tb, box); this.body.style.overflow = "auto";
    const rr = e => { const p = e.plan; const r = Math.abs(p.entry - p.stop); return r ? Math.abs(p.tps[0] - p.entry)/r : 0; };
    const ageTxt = t => { if (!t) return "–"; const m = Math.max(0, Math.round((Date.now() - t)/60000)); return m < 60 ? m+"m" : m < 1440 ? Math.round(m/60)+"h" : Math.round(m/1440)+"d"; };
    const pxOf = sym => { const t = Hub.last["tickers|all"]; return t && !t.error && t[sym] ? t[sym].last : null; };
    const COLS = [["sym",T("symbol")],["chart",Lg("Chart","الشارت")],["tf","TF"],["side",""],["tt",T("rdType")],["tags",T("rdSetup")],["pct",T("rdStr")],["rr","R:R"],["tm",T("sgTiming")],["age",T("sgAge")],["src",T("sgSrc")]];
    const val = {sym:e => e.symbol, tf:e => e.tfk || "", side:e => e.direction, tt:e => e.ttype || "", tags:e => (e.tags || []).length, pct:e => e.score/Math.max(1,e.max), rr:rr, tm:e => planTiming(e, pxOf(e.symbol)).o, age:e => e._t || 0, src:e => e._t ? 1 : 0};
    const TMC = {tmNow:"#0ecb81", tmWait:"#f0b90b", tmRun:"#4aa3ff", tmLate:"#f6465d", tmStop:"#848e9c", tmTp:"#848e9c", tmNA:"#848e9c"};
    const draw = () => {
      F.q = q.value.trim().toLowerCase(); F.side = side.value; F.tf = tf.value; F.min = +mn.value;
      let rows = readyList().filter(e => (!F.side || e.direction === F.side) && (!F.tf || e.tfk === F.tf) && 100*e.score/Math.max(1,e.max) >= F.min
        && (!F.q || (e.symbol+" "+(e.tags || []).map(t => t[0]+" "+(TAG_EN[t[0]] || "")).join(" ")).toLowerCase().includes(F.q)));
      const g = val[F.sort] || val.pct; rows = rows.sort((a, b) => { const x = g(a), y = g(b); return (x < y ? -1 : x > y ? 1 : 0)*F.dir || (b._t - a._t); });
      const nl = rows.filter(e => e.direction === "bullish").length; cnt.textContent = rows.length+" "+T("sgCount")+" · ▲"+nl+" ▼"+(rows.length - nl);
      box.innerHTML = ""; if (!rows.length){ box.innerHTML = '<div class="err" style="color:#848e9c">'+esc(CFG.scanning ? T("scanning") : T("sgNone"))+'</div>'; return; }
      let h = '<table class="rdt"><tr>'+COLS.map(([k,l]) => '<th data-k="'+k+'" style="cursor:pointer"'+(k === "tm" ? ' title="'+esc(T("sgTimeTip"))+'"' : '')+'>'+esc(l)+(F.sort === k ? (F.dir < 0 ? " ▾" : " ▴") : "")+'</th>').join("")+'</tr>';
      rows.slice(0, 120).forEach((e, i) => { const long_ = e.direction === "bullish", pct = Math.round(100*e.score/Math.max(1,e.max)), col = pct >= 70 ? "#0ecb81" : pct >= 50 ? "#f0b90b" : "#848e9c";
        h += '<tr data-i="'+i+'" style="cursor:pointer"><td><b>'+esc(e.symbol)+'</b>'+(pipSetup(e) ? ' <span title="'+esc(T("sgPipTip"))+' ('+pipSetup(e).st+' / '+pipSetup(e).tp+')" style="background:#f0b90b;color:#000;border-radius:3px;padding:0 4px;font-size:10px;font-weight:700">★120</span>' : '')+'</td><td>'+sparkSvg(e)+'</td><td class="m">'+esc(e.tfk || "")+'</td><td style="color:'+(long_ ? "#0ecb81" : "#f6465d")+';font-weight:700">'+esc(long_ ? T("long") : T("short"))+'</td>'
          +'<td style="color:#f0b90b">'+esc(ttTxt(e.ttype))+'</td><td>'+(e.tags || []).slice(0, 4).map(t => '<span class="tg" title="'+esc(tagTip(t))+'" style="margin-inline-end:3px;background:'+esc(t[1])+';color:'+esc(t[2])+'">'+esc(tagTxt(t[0]))+'</span>').join("")+'</td>'
          +'<td><span class="bar"><i style="width:'+pct+'%;background:'+col+'"></i></span> '+pct+'%</td><td>'+rr(e).toFixed(1)+'</td><td style="color:'+TMC[planTiming(e, pxOf(e.symbol)).k]+'">'+esc(T(planTiming(e, pxOf(e.symbol)).k))+'</td><td class="m">'+esc(ageTxt(e._t))+'</td><td class="m">'+esc(e._t ? T("sgAlert") : T("sgScan"))+'</td></tr>'; });
      box.innerHTML = h+"</table>";
      box.querySelectorAll("th[data-k]").forEach(th => th.onclick = () => { const k = th.dataset.k; if (F.sort === k) F.dir = -F.dir; else { F.sort = k; F.dir = (k === "sym" || k === "tf" || k === "tt") ? 1 : -1; } Ws.save(); draw(); });
      box.querySelectorAll("tr[data-i]").forEach(tr => tr.onclick = () => { const e = rows[+tr.dataset.i]; if (e) Ws.showOnChart(Object.assign({tfc: TFC_ALL[e.tfk] || "1H"}, e)); });
    };
    [q, side, tf, mn].forEach(x => x.oninput = x.onchange = () => { Ws.save(); draw(); });
    draw(); Alerts.subs.add(draw); const un = Hub.sub("tickers", "all", () => draw()); this.unwatch = () => { Alerts.subs.delete(draw); un(); };
  }
  /* ---- Settings: theme presets (Dark / Midnight / Day) + candle / background colours, applied to every chart and panel ---- */
  build_settings(){
    const box = el("div"); box.style.cssText = "padding:10px;display:flex;flex-direction:column;gap:12px"; this.body.append(box); this.body.style.overflow = "auto";
    const render = () => {
      box.innerHTML = ""; const ar = lang === "ar";
      const h1 = t => { const d = el("div"); d.textContent = t; d.style.cssText = "font-weight:700;color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px"; return d; };
      const g1 = el("div"); g1.append(h1(T("stTheme"))); const row = el("div"); row.style.cssText = "display:flex;gap:8px;flex-wrap:wrap";
      Object.entries(THEMES).forEach(([k, t]) => { const b = el("button"); b.style.cssText = "padding:8px 12px;border-radius:6px;min-width:92px;text-align:start;border:2px solid "+(ThemeCfg.name === k ? "var(--gold)" : "var(--line)")+";background:"+t.css.panel+";color:"+t.css.txt;
        b.innerHTML = '<div style="font-weight:700;margin-bottom:4px">'+esc(ar ? ({dark:"داكن",midnight:"منتصف الليل",day:"نهاري"})[k] : t.name)+'</div><div style="display:flex;gap:3px"><i style="width:14px;height:14px;border-radius:3px;background:'+t.ch.up+'"></i><i style="width:14px;height:14px;border-radius:3px;background:'+t.ch.dn+'"></i><i style="width:14px;height:14px;border-radius:3px;background:'+t.ch.bg+';border:1px solid '+t.css.line+'"></i></div>';
        b.onclick = () => { setTheme({name:k, up:"", dn:"", bg:""}); render(); }; row.append(b); });
      g1.append(row);
      const g2 = el("div"); g2.append(h1(T("stCandles"))); const r2 = el("div"); r2.style.cssText = "display:flex;gap:14px;align-items:center;flex-wrap:wrap";
      const pick = (lab, key, cur) => { const w = el("label"); w.style.cssText = "display:flex;gap:6px;align-items:center"; const i = el("input"); i.type = "color"; i.value = cur; i.style.cssText = "width:34px;height:24px;padding:0"; i.oninput = () => setTheme({[key]:i.value}); w.append(i, document.createTextNode(lab)); return w; };
      r2.append(pick(T("stUp"), "up", TH.up), pick(T("stDn"), "dn", TH.dn), pick(T("stBg"), "bg", TH.bg));
      const rs = el("button", null, T("stReset")); rs.onclick = () => { setTheme({up:"", dn:"", bg:""}); render(); }; r2.append(rs); g2.append(r2);
      const nt = el("div","m"); nt.textContent = T("stNote");
      box.append(g1, g2, nt);
    };
    render();
  }
  /* ---- Market radar (the Scanner widget): where to look BEFORE looking for a setup. One row per market, daily candles:
     trend = sign of the 20 / 60 / 100-day returns (time-series momentum, the best-documented edge in the research), ADX(14) strength,
     ATR% volatility, position in the 20-day range, RSI(14), volatility-adjusted 60-day momentum, and whether a live setup exists on
     the trend side. Ranked by |trend| x ADX. Daily data, refreshed every 10 min; a ranking, not a signal. ---- */
  build_scanner(){
    const S = this.state; S.rg = S.rg || "all"; S.rw = !!S.rw;
    const tb = el("div","tb"), grp = el("select"), only = el("label"), oc = el("input"), info = el("span","m"), box = el("div");
    [["all",Lg("All markets","كل الأسواق")],["crypto",Lg("Crypto","كريبتو")],["tradfi",Lg("Gold / oil / indices / FX / stocks (Hyperliquid)","ذهب / بترول / مؤشرات / عملات / أسهم (Hyperliquid)")],["mine",Lg("My list + favorites","قائمتي + المفضلة")]].forEach(([v,t]) => grp.append(Object.assign(el("option"), {value:v, textContent:t})));
    grp.value = S.rg; oc.type = "checkbox"; oc.checked = S.rw; only.append(oc, document.createTextNode(" "+Lg("trending only","الترند بس"))); only.title = Lg("Hide markets without a clear trend (ADX < 20 or mixed returns)","اخفي الأسواق اللي مفيهاش ترند واضح (ADX أقل من 20 أو عوائد متضاربة)");
    info.style.cssText = "font-size:10px;white-space:nowrap"; tb.append(grp, only, info); box.style.cssText = "overflow:auto;height:calc(100% - 30px)"; this.body.append(tb, box);
    const R = Ws.radar = Ws.radar || {d:{}, t:{}, busy:false};
    const list = () => { const fav = store.get(LS+"_fav", []), cr = SYMS.filter(x => !/^(Y|HL|FH):/.test(x)).slice(0, 20), tf = HL.list.slice().sort((a,b) => b.vol - a.vol).slice(0, 25).map(x => x.id);
      return [...new Set(S.rg === "crypto" ? cr : S.rg === "tradfi" ? tf : S.rg === "mine" ? SYMS.concat(fav).filter(x => !/^FH:/.test(x)) : cr.concat(tf))]; };
    const calc = d => { const n = d.length; if (n < 61) return null; const c = d.map(k => k.c), last = c[n-1], ret = b => n > b ? last/c[n-1-b] - 1 : null;
      const r20 = ret(20), r60 = ret(60), r100 = ret(100), tr = [r20, r60, r100].filter(v => v != null).reduce((a, v) => a + Math.sign(v), 0);
      const A = adxOf(d, 14), adx = A.adx[n-1], pd = A.pdi[n-1], md = A.mdi[n-1], rsi = rsiOf(c, 14)[n-1];
      let a = 0; for (let i = n-14; i < n; i++) a += Math.max(d[i].h - d[i].l, Math.abs(d[i].h - d[i-1].c), Math.abs(d[i].l - d[i-1].c)); const atrp = a/14/last*100;
      const w = d.slice(-20), hi = Math.max(...w.map(k => k.h)), lo = Math.min(...w.map(k => k.l)), pos = hi > lo ? (last - lo)/(hi - lo) : .5;
      const rr = c.slice(-61).map((v, i, x) => i ? Math.log(v/x[i-1]) : 0).slice(1), sd = Math.sqrt(rr.reduce((s_, v) => s_ + v*v, 0)/rr.length) || 1e-9, mv = Math.log(c[n-1]/c[n-61])/(sd*Math.sqrt(60));
      const verdict = adx == null || adx < 20 ? "range" : tr >= 2 ? "up" : tr <= -2 ? "down" : "mixed";
      return {last, r20, r60, tr, adx, pd, md, rsi, atrp, pos, mv, verdict, rank:Math.abs(tr)*(adx || 0)}; };
    const load = async () => { if (R.busy) return; R.busy = true;
      try { for (const s of list()){ if (R.t[s] && Date.now() - R.t[s] < 600000) continue; try { R.d[s] = calc(parseRows(await okx("/market/candles?instId="+encodeURIComponent(s)+"&bar=1Dutc&limit=130"))); } catch(e){ R.d[s] = {err:String(e.message || e)}; } R.t[s] = Date.now(); draw(); await new Promise(r => setTimeout(r, 120)); } }
      finally { R.busy = false; draw(); } };
    const pct = v => v == null ? "–" : (v >= 0 ? "+" : "")+(v*100).toFixed(1)+"%";
    const draw = () => {
      const live = readyList(), syms = list(), rows = syms.map(s => [s, R.d[s]]).filter(([, x]) => x && !x.err && (!S.rw || x.verdict === "up" || x.verdict === "down")).sort((a, b) => b[1].rank - a[1].rank);
      const nm = s => /^HL:/.test(s) ? esc(hlLabel(s))+' <span class="hlb">HL</span>' : esc(s.replace(/-USDT(-SWAP)?$/, ""));
      const V = {up:["▲ "+Lg("Uptrend","صاعد"),"g"], down:["▼ "+Lg("Downtrend","هابط"),"rd"], range:["↔ "+Lg("Range","رينج"),"m"], mixed:["~ "+Lg("Mixed","متضارب"),"m"]};
      let h = '<table class="wt"><tr><th>'+esc(T("symbol"))+'</th><th>'+esc(Lg("Trend","الترند"))+'</th><th class="r">ADX</th><th class="r">20d</th><th class="r">60d</th><th class="r" title="'+esc(Lg("60-day momentum divided by its volatility","زخم 60 يوم مقسوم على التذبذب"))+'">M/σ</th><th class="r">ATR%</th><th class="r">RSI</th><th title="'+esc(Lg("Where the price sits in its 20-day range","مكان السعر في رينج آخر 20 يوم"))+'">'+esc(Lg("Range","الرينج"))+'</th><th>'+esc(Lg("Setup","سيت اب"))+'</th></tr>';
      rows.forEach(([s, x]) => { const v = V[x.verdict], st = live.filter(e => e.symbol === s), w = st.find(e => (e.direction === "bullish") === (x.verdict === "up") && (x.verdict === "up" || x.verdict === "down")), ag = st.length && !w;
        h += '<tr class="wr" data-s="'+esc(s)+'"><td>'+nm(s)+'</td><td class="'+v[1]+'">'+esc(v[0])+'</td><td class="r">'+(x.adx == null ? "–" : x.adx.toFixed(0))+'</td><td class="r '+(x.r20 >= 0 ? "g" : "rd")+'">'+pct(x.r20)+'</td><td class="r '+(x.r60 >= 0 ? "g" : "rd")+'">'+pct(x.r60)+'</td><td class="r">'+x.mv.toFixed(2)+'</td><td class="r">'+x.atrp.toFixed(1)+'</td><td class="r">'+(x.rsi || 0).toFixed(0)+'</td>'
          +'<td><div style="position:relative;width:56px;height:6px;background:var(--line);border-radius:3px"><div style="position:absolute;left:'+Math.round(x.pos*52)+'px;top:-2px;width:4px;height:10px;background:var(--gold, #f0b90b);border-radius:2px"></div></div></td>'
          +'<td>'+(w ? '<span class="g" title="'+esc(Lg("a live setup on the trend side","سيت اب شغال مع الترند"))+'">✓ '+esc(w.trade || w.ttype || "")+'</span>' : ag ? '<span class="rd" title="'+esc(Lg("only setups AGAINST the trend - weaker in the research and in our lab","سيت اب ضد الترند بس - أضعف في الأبحاث وفي المعمل"))+'">⚠</span>' : "")+'</td></tr>'; });
      const errs = syms.filter(s => R.d[s] && R.d[s].err).length, waiting = syms.filter(s => !R.d[s]).length;
      if (!rows.length) h += '<tr><td colspan="10" class="m">'+esc(waiting ? T("loading") : Lg("Nothing matches.","مفيش حاجة مطابقة."))+'</td></tr>';
      box.innerHTML = h+'</table>'; info.textContent = rows.length+"/"+syms.length+(waiting ? " · "+Lg("loading","بيحمّل")+" "+waiting : "")+(errs ? " · "+errs+" "+Lg("failed","فشل") : "");
      box.querySelectorAll(".wr").forEach(r => r.onclick = () => Ws.broadcast(this, r.dataset.s)); };
    grp.onchange = () => { S.rg = grp.value; Ws.save(); draw(); load(); }; oc.onchange = () => { S.rw = oc.checked; Ws.save(); draw(); };
    HL.start(); draw(); load(); const iv = setInterval(() => { draw(); load(); }, 60000), iv2 = setTimeout(() => { draw(); load(); }, 2500);
    this.unwatch = () => { clearInterval(iv); clearTimeout(iv2); };
  }
  /* ---- journal: funded-account style analytics (equity curve, stat cards, win/loss calendar) ---- */
  build_journal(){
    const S = this.state; S.jr = S.jr || "30"; S.jc = S.jc != null ? S.jc : 0; const now0 = new Date(); S.jm = S.jm || (now0.getFullYear()+"-"+now0.getMonth());
    const tb = el("div","tb"), rng = el("select"), cf = el("select"), clr = el("button",null,T("clear")); let armed = 0;
    [["7","7d"],["30","30d"],["90","90d"],["0",T("fAll")]].forEach(([v,l]) => rng.append(Object.assign(el("option"), {value:v, textContent:l}))); rng.value = S.jr;
    [[0,T("fAll")],[50,"≥ 50%"],[70,"≥ 70%"]].forEach(([v,l]) => cf.append(Object.assign(el("option"), {value:v, textContent:T("conf")+" "+l}))); cf.value = S.jc;
    rng.onchange = () => { S.jr = rng.value; Ws.save(); draw(); }; cf.onchange = () => { S.jc = +cf.value; Ws.save(); draw(); };
    clr.onclick = () => { if (Date.now() - armed < 2500){ Journal.list = []; Journal.save(); armed = 0; clr.textContent = T("clear"); } else { armed = Date.now(); clr.textContent = "?"; setTimeout(() => clr.textContent = T("clear"), 2500); } };
    const csvB = el("button", null, "CSV"); csvB.title = Lg("Export closed trades with their context layers (for the Performance tab and the A+++ review)","صدّر الصفقات المقفولة مع طبقات السياق (لتاب الأداء ومراجعة A+++)");
    // layer columns (order flow, session, news, funding, OI, score) let the lab-style review check which layers add R on YOUR trades
    const cell = v => { const x = v == null ? "" : typeof v === "object" ? JSON.stringify(v) : String(v); return /[",\n]/.test(x) ? '"' + x.replace(/"/g, '""') + '"' : x; };
    csvB.onclick = () => { const st = Journal.stats(+S.jc, S.jr === "0" ? 0 : Date.now() - (+S.jr)*86400e3), rows = ["time,symbol,side,tf,r,entry_time,rr,score_pct,tags,of,session,news,funding,oi,grade,htf,loc,vol,reg,time"].concat(st.closed.map(t => [new Date(t.t1).toISOString(), t.symbol || t.sym || "", t.dir === "bullish" ? "long" : "short", t.tfk || "", (+t.r).toFixed(3),
      t.t0 ? new Date(t.t0).toISOString() : "", t.rr != null ? (+t.rr).toFixed(2) : "", t.pct != null ? t.pct : "", t.tags, t.ctx && t.ctx.of, t.ctx && t.ctx.ses, t.ctx && t.ctx.news, t.ctx && t.ctx.fund, t.ctx && t.ctx.oi, t.chain && t.chain.g, t.chain && t.chain.htf, t.chain && t.chain.loc, t.chain && t.chain.vol, t.chain && t.chain.reg, t.chain && t.chain.time].map(cell).join(",")));
      const txt = rows.join("\n"); try { const a2 = document.createElement("a"); a2.href = URL.createObjectURL(new Blob([txt], {type:"text/csv"})); a2.download = "journal_trades.csv"; document.body.append(a2); a2.click(); a2.remove(); }
      catch(e){}
      try { navigator.clipboard.writeText(txt).then(() => { csvB.textContent = "✓"; setTimeout(() => csvB.textContent = "CSV", 1500); }, () => {}); } catch(e2){} };   // also copied to the clipboard in case the host page blocks downloads
    const lg = el("select"); [[0,"0%"],[40,"≥ 40%"],[50,"≥ 50%"],[60,"≥ 60%"],[70,"≥ 70%"]].forEach(([v,l]) => lg.append(Object.assign(el("option"), {value:v, textContent:Lg("Log only","سجّل بس")+" "+l}))); lg.value = String(Journal.cfg.min);
    lg.title = Lg("Only setups at or above this strength are recorded from now on (weak ones stay out of the statistics). Existing records are not changed.","الصفقات اللي قوتها أقل من كده مش هتتسجل من دلوقتي (عشان ما تبوّظش الإحصائيات). السجلات القديمة ما بتتغيرش.");
    lg.onchange = () => { Journal.cfg.min = +lg.value; store.set(LS+"_jset", Journal.cfg); };
    tb.append(rng, cf, lg, csvB, clr); const box = el("div","jr");
    const loc = el("div","m jlocal"); loc.style.cssText = "font-size:11px;padding:3px 8px;opacity:.85"; loc.textContent = Lg("Local · this browser only. For personal review, not evidence of performance (the server signal log is the source of truth).","محلي · في المتصفح ده بس. للمراجعة الشخصية، مش دليل أداء (المصدر الأساسي سجل السيرفر).");
    this.body.append(tb, loc, box); this.body.style.overflow = "auto";
    const f2 = v => (v >= 0 ? "+" : "") + v.toFixed(2);
    const draw = () => {
      const since = S.jr === "0" ? 0 : Date.now() - (+S.jr)*86400e3, st = Journal.stats(+S.jc, since);
      const card = (lab, val, col) => '<div class="jc"><div class="jl">'+esc(lab)+'</div><div class="jv" style="color:'+(col||"var(--txt)")+'">'+val+'</div></div>';
      let h = '<div class="jcards">'
        + card(T("jWin"), st.wr.toFixed(1)+"%", st.closed.length ? (st.wr >= 50 ? "#0ecb81" : "#f6465d") : "")
        + card(T("jNet"), f2(st.net)+" R", st.net >= 0 ? "#0ecb81" : "#f6465d") + card(T("jTrades"), st.wins+" / "+st.losses+" · "+st.open+" "+T("jOpen"))
        + card(T("jAvg"), f2(st.avg)+" R") + card(Lg("Profit factor","معامل الربح"), st.pf === Infinity ? "∞" : st.pf.toFixed(2)) + card(T("jBest"), f2(st.best)+" R", "#0ecb81") + card(T("jWorst"), f2(st.worst)+" R", "#f6465d") + card(T("jDd"), "-"+st.dd.toFixed(2)+" R", "#f6465d") + '</div>';
      // equity curve
      const c = st.curve; let svg = '<div class="jl" style="margin:6px 4px 0">'+esc(T("jEq"))+'</div>';
      if (c.length > 1){ const W = 600, H = 120, vs = c.map(p => p.v).concat([0]), lo = Math.min(...vs), hi = Math.max(...vs), y = v => H-6-(v-lo)/((hi-lo)||1)*(H-12), x = i => i*W/(c.length-1);
        const pts = c.map((p,i) => x(i).toFixed(1)+","+y(p.v).toFixed(1)).join(" "), up = c[c.length-1].v >= 0, col = up ? "#0ecb81" : "#f6465d";
        svg += '<svg viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none" style="width:100%;height:120px;background:#0e1217;border:1px solid var(--line);border-radius:6px"><line x1="0" x2="'+W+'" y1="'+y(0)+'" y2="'+y(0)+'" stroke="#3a424b" stroke-dasharray="4 3"/><polygon points="0,'+y(0)+' '+pts+' '+W+','+y(0)+'" fill="'+col+'" opacity=".15"/><polyline points="'+pts+'" fill="none" stroke="'+col+'" stroke-width="2" vector-effect="non-scaling-stroke"/></svg>';
      } else svg += '<div class="m" style="padding:10px">'+esc(T("jEmpty"))+'</div>';
      h += svg;
      // performance report: only from real closed journal trades
      { const cl = st.closed, ar = lang === "ar", L = (e,a) => ar ? a : e; h += '<div class="jl" style="margin:6px 4px 0">'+L("Performance report","تقرير الأداء")+'</div>';
        if (!cl.length) h += '<div class="m" style="padding:8px">'+L("Empty until real trades close — it fills from the journal only.","فاضي لحد ما صفقات حقيقية تتقفل — بيتملي من الجورنال بس.")+'</div>';
        else { const W = cl.filter(t => t.r > 0), Ls = cl.filter(t => t.r <= 0), av = a => a.length ? a.reduce((s,t) => s + t.r, 0)/a.length : 0;
          let mw = 0, ml = 0, cw = 0, cL = 0; cl.slice().sort((a,b) => a.t1 - b.t1).forEach(t => { if (t.r > 0){ cw++; cL = 0; } else { cL++; cw = 0; } mw = Math.max(mw, cw); ml = Math.max(ml, cL); });
          const wr = a => { const x = cl.filter(t => t.dir === a); return x.length ? Math.round(100*x.filter(t => t.r > 0).length/x.length)+"% ("+x.length+")" : "–"; };
          const hold = cl.reduce((s,t) => s + (t.t1 - t.t0), 0)/cl.length, hm = hold >= 3600e3 ? (hold/3600e3).toFixed(1)+"h" : Math.round(hold/60e3)+"m";
          const bs = {}; cl.forEach(t => bs[t.symbol] = (bs[t.symbol] || 0) + t.r); const sy = Object.entries(bs).sort((a,b) => b[1]-a[1]), bst = sy[0], wst = sy[sy.length-1];
          const pc = (lab, v, col) => '<div class="jc"><div class="jl">'+esc(lab)+'</div><div class="jv" style="color:'+(col||"var(--txt)")+';font-size:13px">'+v+'</div></div>';
          h += '<div class="jperf">'+pc(L("Expectancy / trade","التوقع / صفقة"), f2(av(cl))+" R", av(cl) >= 0 ? "#0ecb81" : "#f6465d")+pc(L("Avg win","متوسط الربح"), f2(av(W))+" R", "#0ecb81")+pc(L("Avg loss","متوسط الخسارة"), f2(av(Ls))+" R", "#f6465d")
            +pc(L("Max win streak","أطول سلسلة ربح"), mw)+pc(L("Max loss streak","أطول سلسلة خسارة"), ml)+pc(L("Long win rate","نجاح الشراء"), wr("bullish"))+pc(L("Short win rate","نجاح البيع"), wr("bearish"))
            +pc(L("Avg hold","متوسط المدة"), hm)+pc(L("Best symbol","أفضل رمز"), esc(bst[0])+" "+f2(bst[1]), "#0ecb81")+pc(L("Worst symbol","أسوأ رمز"), esc(wst[0])+" "+f2(wst[1]), "#f6465d")+'</div>'; } }
      { const ts = CFG.tfstats && CFG.tfstats.stats, ar = lang === "ar", L = (x,y) => ar ? y : x; h += '<div class="jl" style="margin:6px 4px 0">'+L("Best timeframe per strategy (historical TP1 hit-rate, walk-forward on OKX candles)","أفضل تايم فريم لكل استراتيجية (نسبة ضرب الهدف الأول تاريخياً)")+'</div>';
        if (!ts) h += '<div class="m" style="padding:8px">'+L("Backtest not ready yet — it runs in the background and is cached for a day.","الباك تيست لسه ما جهزش — بيشتغل في الخلفية وبيتحفظ يوم.")+'</div>';
        else { const TFS = ["1m","1h","1d","1w"], min = CFG.tfstats.min_n || 8, best = CFG.tfstats.best || {};
          h += '<table class="rdt"><tr><th>'+L("Strategy","الاستراتيجية")+'</th>'+TFS.map(t => '<th>'+t+'</th>').join("")+'<th>'+L("Best","الأفضل")+'</th></tr>'
            + Object.keys(ts).sort((a,b) => a === "*" ? -1 : b === "*" ? 1 : 0).map(g => '<tr><td>'+esc(g === "*" ? L("All signals","كل الإشارات") : tagTxt(g))+'</td>'+TFS.map(t => { const d = ts[g][t]; return !d || d.n < min ? '<td class="m">–</td>' : '<td style="color:'+(d.hit >= .5 ? "#0ecb81" : "#f6465d")+(best[g] === t ? ";font-weight:700" : "")+'">'+Math.round(100*d.hit)+'% <span class="m">n'+d.n+'</span></td>'; }).join("")+'<td style="color:#f0b90b">'+esc(best[g] || "–")+'</td></tr>').join("")+'</table>'; } }
      // calendar
      const [cy, cm] = S.jm.split("-").map(Number), first = new Date(cy, cm, 1), dim = new Date(cy, cm+1, 0).getDate(), day = {};
      st.closed.forEach(t => { const d = new Date(t.t1), k = d.getFullYear()+"-"+d.getMonth()+"-"+d.getDate(); (day[k] = day[k] || {r:0,n:0}).r += t.r; day[k].n++; });
      const mname = first.toLocaleString(lang === "ar" ? "ar" : "en", {month:"long", year:"numeric"}); let cal = '<div class="jcal"><div class="jl" style="display:flex;align-items:center;gap:8px"><button class="jp">◀</button><b style="color:var(--txt)">'+esc(mname)+'</b><button class="jn">▶</button></div><div class="jgrid">';
      ["S","M","T","W","T","F","S"].forEach(d => cal += '<div class="jh">'+d+'</div>'); for (let i = 0; i < first.getDay(); i++) cal += '<div></div>';
      for (let d = 1; d <= dim; d++){ const x = day[cy+"-"+cm+"-"+d]; const bg = x ? (x.r >= 0 ? "rgba(14,203,129,"+Math.min(.75, .25+Math.abs(x.r)*.12)+")" : "rgba(246,70,93,"+Math.min(.75, .25+Math.abs(x.r)*.12)+")") : "transparent";
        cal += '<div class="jd" style="background:'+bg+'" title="'+(x ? x.n+" trades" : "")+'"><span>'+d+'</span>'+(x ? '<b>'+f2(x.r)+'</b>' : "")+'</div>'; }
      cal += '</div></div>';
      // strategies
      const by = {}; st.closed.forEach(t => (t.tags || []).forEach(g => { const k = tagTxt(g); (by[k] = by[k] || {w:0,n:0}).n++; if (t.status === "tp") by[k].w++; }));
      const rowsS = Object.entries(by).sort((a,b) => b[1].n - a[1].n).slice(0,8).map(([k,v]) => '<tr><td>'+esc(k)+'</td><td>'+v.n+'</td><td style="color:'+(v.w/v.n >= .5 ? "#0ecb81" : "#f6465d")+'">'+Math.round(100*v.w/v.n)+'%</td></tr>').join("");
      const byT = {}; st.closed.forEach(t => { const k = ttTxt(t.ttype); (byT[k] = byT[k] || {w:0,n:0}).n++; if (t.status === "tp") byT[k].w++; });
      const rowsT = Object.entries(byT).map(([k,v]) => '<tr><td>'+esc(k)+'</td><td>'+v.n+'</td><td style="color:'+(v.w/v.n >= .5 ? "#0ecb81" : "#f6465d")+'">'+Math.round(100*v.w/v.n)+'%</td></tr>').join("");
      const mkRows = f => { const o = {}; st.closed.forEach(t => { const k = f(t); (o[k] = o[k] || {w:0,n:0,r:0}).n++; o[k].r += t.r; if (t.status === "tp") o[k].w++; }); return Object.entries(o).sort((a,b) => b[1].n - a[1].n).map(([k,v]) => '<tr><td>'+esc(k)+'</td><td>'+v.n+'</td><td style="color:'+(v.w/v.n >= .5 ? "#0ecb81" : "#f6465d")+'">'+Math.round(100*v.w/v.n)+'%</td><td style="color:'+(v.r >= 0 ? "#0ecb81" : "#f6465d")+'">'+f2(v.r/v.n)+'</td></tr>').join("") || '<tr><td class="m">–</td></tr>'; };
      const rowsF = mkRows(t => t.tfk || "?"), rowsP = mkRows(t => t.pct >= 70 ? "≥70%" : t.pct >= 50 ? "50-69%" : "<50%");
      const ST = Journal.stopTable(st.closed), f2s = v => (v >= 0 ? "+" : "") + v.toFixed(2);
      const stopHtml = !ST ? '<div class="m" style="padding:2px 4px">'+esc(Lg("no finished trade has its candle replay yet (needs the candle history to reach the entry)","لسه مفيش صفقة اتعمل لها إعادة تشغيل الشموع (محتاج تاريخ شموع يوصل للدخول)"))+'</div>'
        : '<table class="rdt"><tr><th>'+esc(Lg("stop x risk","الستوب × المخاطرة"))+'</th><th>n</th><th>'+esc(Lg("win %","فوز %"))+'</th><th>'+esc(Lg("avg R","متوسط R"))+'</th></tr>'+ST.rows.map(r => '<tr><td>'+r.k+(r.k === 1 ? " ("+esc(Lg("real","الفعلي"))+")" : "")+'</td><td>'+r.n+'</td><td>'+Math.round(r.win)+'%</td><td style="color:'+(r.avg >= 0 ? "#0ecb81" : "#f6465d")+'">'+f2s(r.avg)+'</td></tr>').join("")+'</table>'
        +'<div class="m" style="padding:3px 4px;font-size:10px">'+esc(Lg("Stopped trades that reached the target later: ","صفقات ضربت الستوب وبعدين وصلت الهدف: "))+'<b>'+ST.rec+' / '+ST.stopped+'</b>'+(ST.mae.n ? ' · '+esc(Lg("how far winners went against you first (R): median ","لحد فين الرابحة عكست ضدك الأول (R): الوسيط "))+ST.mae.p50.toFixed(2)+' · 75% '+ST.mae.p75.toFixed(2)+' · 90% '+ST.mae.p90.toFixed(2) : '')+'<br>'+esc(Lg("trades replayed: ","صفقات اتعملها إعادة تشغيل: "))+ST.n+esc(Lg(" ("+ST.full+" with the full time window; the rest are counted so far and can only miss recoveries that come later)"," ("+ST.full+" بنافذة وقتها كاملة؛ الباقي لحد دلوقتي وممكن تفوته تعافي لسه جاي)"))+(ST.n < 30 ? '<br>'+esc(Lg("under 30 trades = not evidence","أقل من 30 صفقة = مش دليل")) : '')+'</div>';
      const rowsG = mkRows(t => t.chain ? t.chain.g : "not recorded"), rowsL = mkRows(t => !t.chain ? "not recorded" : t.chain.loc ? Lg("with location","مع الموقع") : Lg("against location","ضد الموقع"));
      const rowsO = mkRows(t => (t.ctx && t.ctx.of) || "not recorded"), rowsN = mkRows(t => !t.ctx ? "not recorded" : t.ctx.news ? Lg("news ±1h","خبر قريب") : Lg("no news","مفيش خبر")), rowsK = mkRows(t => (t.ctx && t.ctx.ses) || "not recorded"),
        rowsI = mkRows(t => !t.ctx || !t.ctx.oi ? "not recorded" : ({longs:Lg("new longs","لونجات جديدة"), cover:Lg("short covering","تغطية شورت"), shorts:Lg("new shorts","شورتات جديدة"), closing:Lg("longs closing","لونجات بتقفل")})[t.ctx.oi] + " · " + (t.dir > 0 || t.dir === "bullish" ? "long" : "short"));
      const side = '<div class="jside"><div class="jl">'+esc(T("jStrat"))+'</div><table class="rdt">'+(rowsS || '<tr><td class="m">–</td></tr>')+'</table><div class="jl" style="margin-top:6px">'+esc(T("rdType"))+'</div><table class="rdt">'+(rowsT || '<tr><td class="m">–</td></tr>')+'</table>'
        +'<div class="jl" style="margin-top:6px">'+esc(Lg("Timeframe (n · win · avg R)","الفريم (عدد · نجاح · متوسط R)"))+'</div><table class="rdt">'+rowsF+'</table><div class="jl" style="margin-top:6px">'+esc(Lg("Strength (n · win · avg R)","القوة (عدد · نجاح · متوسط R)"))+'</div><table class="rdt">'+rowsP+'</table>'
        +'<div class="jl" style="margin-top:6px">'+esc(Lg("Order flow at entry","الأوردر فلو وقت الدخول"))+'</div><table class="rdt">'+rowsO+'</table><div class="jl" style="margin-top:6px">'+esc(Lg("Session","الجلسة"))+'</div><table class="rdt">'+rowsK+'</table><div class="jl" style="margin-top:6px">'+esc(Lg("Stop test: the same trades with a wider stop (same target)","اختبار الستوب: نفس الصفقات بستوب أوسع (نفس الهدف)"))+'</div>'+stopHtml+'<div class="jl" style="margin-top:6px">'+esc(Lg("Chain grade (htf · location · volume · regime · time)","درجة السلسلة (اتجاه · موقع · فوليوم · ريجيم · وقت)"))+'</div><table class="rdt">'+rowsG+'</table><div class="jl" style="margin-top:6px">'+esc(Lg("Location layer (long low / short high of range)","طبقة الموقع (شراء من الأسفل / بيع من الأعلى)"))+'</div><table class="rdt">'+rowsL+'</table>'+'<div class="jl" style="margin-top:6px">'+esc(Lg("High-impact news","الأخبار القوية"))+'</div><table class="rdt">'+rowsN+'</table><div class="jl" style="margin-top:6px">'+esc(Lg("Open interest at entry (4h)","العقود المفتوحة وقت الدخول (4س)"))+'</div><table class="rdt">'+rowsI+'</table></div>';
      h += '<div class="jrow">'+cal+side+'</div>';
      // trades table
      const last = st.all.slice().sort((a,b) => b.t0 - a.t0).slice(0, 25);
      h += '<div class="jl" style="margin:6px 4px 0">'+esc(T("jLog"))+'</div><table class="rdt"><tr><th>'+esc(T("symbol"))+'</th><th>'+esc(T("rdType"))+'</th><th>'+esc(T("entry"))+'</th><th>'+esc(T("jRes"))+'</th><th>R</th><th>'+esc(T("time"))+'</th></tr>'
        + last.map(t => { const lg = t.dir === "bullish", col = t.status === "tp" ? "#0ecb81" : t.status === "sl" ? "#f6465d" : "#848e9c", lab = t.status === "tp" ? "TP1 ✓" : t.status === "sl" ? "SL ✗" : t.status === "nf" ? Lg("no fill","ما اتنفذتش") : t.status === "exp" ? T("jExp") : T("jOpen");
          return '<tr data-tid="'+esc(t.id)+'" style="cursor:pointer"><td><b>'+esc(t.symbol)+'</b> <span class="m">'+esc(t.tfk)+'</span> <span style="color:'+(lg?"#0ecb81":"#f6465d")+'">'+esc(lg ? T("long") : T("short"))+'</span> <span class="m">'+t.pct+'%</span></td><td>'+esc(ttTxt(t.ttype))+'</td><td>'+fmtP(t.entry)+'</td><td style="color:'+col+'">'+esc(lab)+'</td><td style="color:'+col+'">'+(t.status === "open" || t.status === "exp" ? "–" : f2(t.r))+'</td><td class="m">'+new Date(t.t0).toLocaleDateString()+" "+hms(t.t0).slice(0,5)+'</td></tr>'; }).join("") + '</table>';
      box.innerHTML = h; box.onclick = e => { const r = e.target.closest && e.target.closest("tr[data-tid]"); if (r) Ws.focusTrade(r.dataset.tid); };   // a journal row jumps the chart to that trade in the past
      const mv = dlt => { const d = new Date(cy, cm+dlt, 1); S.jm = d.getFullYear()+"-"+d.getMonth(); Ws.save(); draw(); };
      box.querySelector(".jp").onclick = () => mv(-1); box.querySelector(".jn").onclick = () => mv(1);
    };
    draw(); Journal.subs.add(draw); this.unwatch = () => Journal.subs.delete(draw);
  }
  /* ---- news ---- */
  build_news(){
    const S = this.state, ar = lang === "ar"; if (S.wmLang !== lang) { if (!S.wmLangManual) S.wm = Object.assign({}, S.wm || {}, {ar: ar ? 1 : 0, en: ar ? 0 : 1}); S.wmLang = lang; Ws.save(); } S.wm = Object.assign({eco:1, pol:1, geo:1, ar:ar ? 1 : 0, en:ar ? 0 : 1}, S.wm || {});
    const bar = el("div","tb"); bar.style.flexWrap = "wrap";
    [["eco", ar ? "اقتصادي" : "Economic"],["pol", ar ? "سياسي" : "Political"],["geo", ar ? "جيوسياسي" : "Geopolitical"],["ar", "عربي"],["en", ar ? "أجنبي" : "Foreign"]].forEach(([k, lab]) => {
      const b = el("button", null, lab), paint = () => { b.style.opacity = S.wm[k] ? "1" : ".4"; b.style.borderColor = S.wm[k] ? "#f0b90b" : ""; }; paint();
      b.onclick = () => { S.wm[k] = S.wm[k] ? 0 : 1; if (k === "ar" || k === "en") S.wmLangManual = true; paint(); Ws.save(); this.showNewsList(); }; bar.append(b); });
    this.nBox = el("div","news-body"); this.body.append(bar, this.nBox); this.showNewsList();
  }
  showNewsList(){
    const items = worldItems(this.state.wm);
    if (!items.length || !items.some(n => n.url || n.summary)){ this.nBox.innerHTML = '<div class="err">'+esc(feedMsg() || T("nonews"))+'</div>' + items.map(n => '<div class="news-item">'+esc(n.headline)+'</div>').join(""); return; }
    this.nBox.innerHTML = ""; if (feedMsg()){ const b = el("div","m"); b.style.cssText = "padding:4px 8px;color:#f0b90b;font-size:11px"; b.textContent = feedMsg(); this.nBox.append(b); }
    items.forEach(n => { const d = el("div","news-item"); d.innerHTML = '<div>'+esc(n.headline)+'</div><div class="m">'+esc(n.source||"")+(n.datetime ? " · "+esc(n.datetime) : "")+'</div>'; d.onclick = () => this.showNewsDetail(n); this.nBox.append(d); });
  }
  showNewsDetail(n){
    const safe = /^https?:\/\//i.test(n.url||"") ? n.url : "";
    this.nBox.innerHTML = '<div class="news-detail"><button class="bk">← '+esc(T("back"))+'</button><h3>'+esc(n.headline)+'</h3><div class="m">'+esc(n.source||"")+(n.datetime ? " · "+esc(n.datetime) : "")+'</div><p>'+esc(n.summary||"")+'</p>'+(safe ? '<a class="link" target="_blank" rel="noopener noreferrer" href="'+esc(safe)+'">'+esc(T("read"))+' ↗</a>' : "")+'</div>';
    this.nBox.querySelector(".bk").onclick = () => this.showNewsList();
  }
  /* ---- video ---- */
  build_video(){
    const box = el("div","vbox"), bar = el("div","tb"), inp = el("input"); inp.placeholder = T("videoUrl"); inp.style.flex = "1"; inp.value = this.state.url || "";
    const go = el("button",null,T("load")); bar.append(inp, go);
    const vf = el("div","vf"); const ins = el("div","ins");
    const ta = el("textarea"); ta.placeholder = T("transcript"); ta.style.cssText = "width:100%;height:56px;resize:vertical"; ta.value = this.state.txt || "";
    const ex = el("button",null,T("extract")); const out = el("div"); const hint = el("div","m"); hint.textContent = T("hint");
    ins.append(ta, ex, hint, out); box.append(bar, vf, ins); this.body.append(box); this.body.style.overflow = "hidden";
    const load = () => {
      const u = inp.value.trim(); this.state.url = u; Ws.save(); const src = embedUrl(u);
      vf.innerHTML = src ? '<iframe class="vid" allowfullscreen referrerpolicy="strict-origin-when-cross-origin" allow="autoplay; encrypted-media; picture-in-picture" src="'+esc(src)+'"></iframe>' : '<div class="err">'+esc(T("videoUrl"))+'</div>';
    };
    go.onclick = load; inp.onkeydown = e => { if (e.key === "Enter") load(); }; if (this.state.url) load();
    ex.onclick = () => { this.state.txt = ta.value; Ws.save(); out.innerHTML = insights(ta.value); };
  }
  /* ---- Positioning (OKX public, no key): open interest of the perpetual (now + 1 h / 4 h / 24 h change), long/short ACCOUNT ratio, and the
     standard price x OI reading: price up + OI up = new longs; price up + OI down = short covering; price down + OI up = new shorts;
     price down + OI down = longs closing / liquidations. One exchange (OKX) - a sample of the market, not all of it. Refresh 60 s. ---- */
  build_posn(){
    const S = this.state, ar = lang === "ar", L = (e, a) => ar ? a : e; S.sym = S.sym || SYMS[0];
    const tb = el("div","tb"); this.symSel = this.symSelect(); tb.append(this.symSel);
    const hd = el("div"), cv = el("canvas"), ft = el("div","m"); hd.style.cssText = "padding:4px 8px;font-size:11px;line-height:1.55"; cv.style.cssText = "width:100%;flex:1;min-height:90px;display:block";
    ft.style.cssText = "padding:2px 8px;font-size:10px"; ft.textContent = L("OKX perpetual only (one exchange). Account ratio = accounts net long vs net short, not size.", "عقود OKX بس (بورصة واحدة). نسبة الحسابات = عدد الحسابات لونج مقابل شورت، مش الحجم.");
    this.body.append(tb, hd, cv, ft); this.body.style.display = "flex"; this.body.style.flexDirection = "column";
    let D = null, err = "", tm = 0;
    const usd = v => v >= 1e9 ? (v/1e9).toFixed(2)+"B" : v >= 1e6 ? (v/1e6).toFixed(1)+"M" : v >= 1e3 ? (v/1e3).toFixed(0)+"K" : (+v).toFixed(0);
    const pct = v => v == null || !isFinite(v) ? "–" : (v > 0 ? "+" : "")+v.toFixed(2)+"%";
    const draw = () => { const r = cv.getBoundingClientRect(), dpr = window.devicePixelRatio || 1, W = Math.max(80, r.width), H = Math.max(60, r.height); cv.width = W*dpr; cv.height = H*dpr;
      const c = cv.getContext("2d"); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.fillStyle = "#0b0e11"; c.fillRect(0, 0, W, H);
      if (err){ hd.innerHTML = '<span class="err">'+esc(err)+'</span>'; return; } if (!D){ hd.textContent = L("Loading…","بيحمّل…"); return; }
      const read = (dp, doi) => dp == null || doi == null ? "" : dp >= 0 && doi >= 0 ? L("new longs (trend fuel)","لونجات جديدة (وقود للصعود)") : dp >= 0 ? L("short covering (weaker rise)","تغطية شورت (صعود أضعف)") : doi >= 0 ? L("new shorts (pressure down)","شورتات جديدة (ضغط هبوط)") : L("longs closing / liquidations","لونجات بتقفل / تصفيات");
      const col = v => v == null ? "#848e9c" : v >= 0 ? "var(--grn)" : "var(--red)";
      hd.innerHTML = '<b>OI</b> $'+usd(D.oi)+' · 1h <span style="color:'+col(D.oi1)+'">'+pct(D.oi1)+'</span> · 4h <span style="color:'+col(D.oi4)+'">'+pct(D.oi4)+'</span> · 24h <span style="color:'+col(D.oi24)+'">'+pct(D.oi24)+'</span><br>'
        + L('Price ','السعر ')+'1h <span style="color:'+col(D.p1)+'">'+pct(D.p1)+'</span> · 4h <span style="color:'+col(D.p4)+'">'+pct(D.p4)+'</span> · 24h <span style="color:'+col(D.p24)+'">'+pct(D.p24)+'</span><br>'
        + '<b>'+L('Reading','القراءة')+'</b> 4h: '+esc(read(D.p4, D.oi4))+' · 24h: '+esc(read(D.p24, D.oi24))+'<br>'
        + '<b>'+L('Long/short accounts','لونج/شورت (حسابات)')+'</b> '+(D.ls != null ? D.ls.toFixed(2)+' ('+Math.round(100*D.ls/(1 + D.ls))+'% '+L('long','لونج')+')' : '–')+(D.ls != null && D.ls >= 2.5 ? ' · <span style="color:var(--gold)">'+L('crowded long','زحمة لونج')+'</span>' : D.ls != null && D.ls <= 0.6 ? ' · <span style="color:var(--gold)">'+L('crowded short','زحمة شورت')+'</span>' : '');
      // 24 h lines: OI (gold), price (grey), long/short ratio (blue, own scale)
      const pad = 6, line = (arr, colr, dash) => { if (!arr || arr.length < 2) return; const mn = Math.min(...arr), mx = Math.max(...arr), sp = mx - mn || 1; c.strokeStyle = colr; c.lineWidth = 1.4; c.setLineDash(dash || []); c.beginPath();
        arr.forEach((v, i) => { const x = pad + i/(arr.length - 1)*(W - 2*pad), y = H - pad - (v - mn)/sp*(H - 2*pad - 10); i ? c.lineTo(x, y) : c.moveTo(x, y); }); c.stroke(); c.setLineDash([]); };
      line(D.px, "#848e9c", [3,3]); line(D.oiS, "#f0b90b"); line(D.lsS, "#4aa3ff");
      c.font = "9px sans-serif"; c.fillStyle = "#f0b90b"; c.fillText("OI 24h", pad, 10); c.fillStyle = "#848e9c"; c.fillText(L("price","السعر"), pad + 46, 10); c.fillStyle = "#4aa3ff"; c.fillText("L/S", pad + 86, 10); };
    this.resub = () => { this.clearSubs(); D = null; err = ""; const sym = S.sym, fam = liqFam(sym); this.setTitle();
      if (!fam){ err = L("Positioning: OKX crypto perpetuals only (pick e.g. BTC-USDT).","التمركز: عقود OKX للكريبتو بس (اختار مثلاً BTC-USDT)."); draw(); return; }
      let alive = true; this.unsubs.push(() => { alive = false; clearTimeout(tm); });
      const ccy = fam.split("-")[0], inst = fam + "-SWAP";
      const poll = async () => { try {
          const [oiNow, oiH, oi5, lsH, cd] = await Promise.all([okx("/public/open-interest?instType=SWAP&instId="+inst), okx("/rubik/stat/contracts/open-interest-volume?ccy="+ccy+"&period=1H"),
            okx("/rubik/stat/contracts/open-interest-volume?ccy="+ccy+"&period=5m"), okx("/rubik/stat/contracts/long-short-account-ratio?ccy="+ccy+"&period=1H").catch(() => []), okx("/market/candles?instId="+inst+"&bar=1H&limit=25")]);
          const h = oiH.map(r => +r[1]), m5 = oi5.map(r => +r[1]), px = cd.map(r => +r[4]), ch = (a, k) => a.length > k && a[k] ? (a[0]/a[k] - 1)*100 : null;
          D = {oi:oiNow && oiNow[0] ? +oiNow[0].oiUsd || h[0] : h[0], oi1:ch(m5, 12), oi4:ch(h, 4), oi24:ch(h, 24), p1:ch(px, 1), p4:ch(px, 4), p24:ch(px, 24),
               ls:lsH && lsH[0] ? +lsH[0][1] : null, oiS:h.slice(0, 25).reverse(), px:px.slice().reverse(), lsS:(lsH || []).slice(0, 25).map(r => +r[1]).reverse()}; err = "";
        } catch(e){ err = "OKX: "+(e.message || e); }
        if (!alive) return; draw(); tm = setTimeout(poll, 180000); };
      poll(); };
    const ro = new ResizeObserver(() => draw()); ro.observe(cv); this.unsubs.push(() => ro.disconnect()); this.resub();
  }
  /* ---- Funding heat map: current funding rate of the top-N OKX USDT perpetuals by 24 h volume, tiles sorted from most negative to most positive;
     colour = sign and size, text = rate per 8 h and annualised. Extreme positive = crowded longs (fuel for a squeeze down), extreme negative = crowded shorts. Refresh 5 min. ---- */
  build_fundhm(){
    const S = this.state, ar = lang === "ar", L = (e, a) => ar ? a : e; S.n = S.n || 40;
    const tb = el("div","tb"), nS = el("select"), info = el("span","m"); info.style.cssText = "font-size:10px;margin-inline-start:6px";
    [20,40,60].forEach(v => { const o = el("option"); o.value = v; o.textContent = L("top ","أعلى ")+v; nS.append(o); }); nS.value = S.n; tb.append(nS, info);
    const grid = el("div"); grid.style.cssText = "flex:1;overflow:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(92px,1fr));gap:3px;padding:4px;align-content:start";
    this.body.append(tb, grid); this.body.style.display = "flex"; this.body.style.flexDirection = "column";
    let tm = 0, alive = true; this.unsubs.push(() => { alive = false; clearTimeout(tm); });
    const load = async () => { info.textContent = L("loading…","بيحمّل…");
      try { const tk = await okx("/market/tickers?instType=SWAP"), list = tk.filter(x => /-USDT-SWAP$/.test(x.instId)).sort((a, b) => +b.volCcy24h - +a.volCcy24h).slice(0, +S.n).map(x => x.instId), out = [];
        for (let i = 0; i < list.length; i += 8){ await Promise.all(list.slice(i, i + 8).map(async id => { try { const f = await okx("/public/funding-rate?instId="+id); if (f && f[0]) out.push({id, b:id.split("-")[0], r:+f[0].fundingRate, h:Math.max(1, Math.round((+f[0].nextFundingTime - +f[0].fundingTime)/3600000) || 8)}); } catch(e){} })); }
        if (!alive) return; out.sort((a, b) => a.r - b.r); grid.innerHTML = "";
        out.forEach(o => { const per8 = o.r*8/o.h, ann = o.r*(24/o.h)*365*100, t = Math.min(1, Math.abs(per8)/0.0005), d = el("div");
          d.style.cssText = "border-radius:4px;padding:4px 6px;cursor:pointer;font-size:11px;background:"+(per8 >= 0 ? "rgba(246,70,93,"+(.12 + .6*t)+")" : "rgba(14,203,129,"+(.12 + .6*t)+")");
          d.innerHTML = '<b>'+esc(o.b)+'</b><br><span style="font-family:ui-monospace,monospace">'+(per8*100).toFixed(4)+'%</span><br><span class="m" style="font-size:9px">'+(ann >= 0 ? "+" : "")+ann.toFixed(1)+L('% / yr','% / سنة')+'</span>';
          d.title = (o.r*100).toFixed(4)+"% / "+o.h+"h"; d.onclick = () => Ws.broadcast({type:"watch", state:{group:0}}, o.b + "-USDT"); grid.append(d); });
        const pos = out.filter(o => o.r*8/o.h >= 0.0005).length, neg = out.filter(o => o.r*8/o.h <= -0.0003).length;
        info.textContent = out.length + L(" coins · ", " عملة · ") + pos + L(" crowded long (≥0.05%/8h) · ", " زحمة لونج (≥0.05%/8س) · ") + neg + L(" paying shorts"," شورت بيدفع");
      } catch(e){ info.textContent = "OKX: "+(e.message || e); }
      if (alive) tm = setTimeout(load, 300000); };
    nS.onchange = () => { S.n = +nS.value; Ws.save(); clearTimeout(tm); load(); }; load();
  }
  /* ---- RSI heat map (CoinGlass style): RSI(14, Wilder) of the top-N OKX USDT pairs by 24 h volume on one timeframe; y = RSI, zones 30 / 40 / 60 / 70.
     Our own calculation from OKX candles in the browser (CoinGlass does not publish its method). Click a coin = open it in the linked widgets. Refresh 2 min. ---- */
  build_rsihm(){
    const S = this.state, ar = lang === "ar", L = (e, a) => ar ? a : e; S.tf = S.tf || "4H"; S.n = S.n || 40;
    const tb = el("div","tb"), tfS = el("select"), nS = el("select"), info = el("span","m"); info.style.cssText = "font-size:10px;margin-inline-start:6px";
    [["5m","5m"],["15m","15m"],["1H","1h"],["4H","4h"],["1D","1d"],["1W","1w"]].forEach(([v,t]) => { const o = el("option"); o.value = v; o.textContent = t; tfS.append(o); });
    [20,40,60,100].forEach(v => { const o = el("option"); o.value = v; o.textContent = L("top ","أعلى ")+v; nS.append(o); });
    tfS.value = S.tf; nS.value = S.n; tb.append(tfS, nS, info);
    const cv = el("canvas"); cv.style.cssText = "width:100%;flex:1;min-height:120px;display:block;cursor:pointer";
    this.body.append(tb, cv); this.body.style.display = "flex"; this.body.style.flexDirection = "column";
    let pts = [], hit = [], busy = false, tm = 0;
    const rsi = cl => { const n = 14; if (cl.length < n + 2) return null; let g = 0, l = 0; for (let i = 1; i <= n; i++){ const d = cl[i] - cl[i-1]; d > 0 ? g += d : l -= d; } g /= n; l /= n;
      for (let i = n + 1; i < cl.length; i++){ const d = cl[i] - cl[i-1]; g = (g*(n-1) + Math.max(d, 0))/n; l = (l*(n-1) + Math.max(-d, 0))/n; } return l === 0 ? 100 : 100 - 100/(1 + g/l); };
    const draw = () => { const r = cv.getBoundingClientRect(), dpr = window.devicePixelRatio || 1, W = Math.max(100, r.width), H = Math.max(100, r.height); cv.width = W*dpr; cv.height = H*dpr;
      const c = cv.getContext("2d"); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.fillStyle = "#0b0e11"; c.fillRect(0, 0, W, H);
      const top = 10, bot = H - 18, lx = 30, rx = W - 8, y = v => top + (90 - Math.max(10, Math.min(90, v)))/80*(bot - top);
      [[70,90,"rgba(246,70,93,.16)",L("Overbought","تشبع شراء")],[60,70,"rgba(246,70,93,.07)",L("Strong","قوي")],[40,60,"rgba(132,142,156,.04)",L("Neutral","محايد")],[30,40,"rgba(14,203,129,.07)",L("Weak","ضعيف")],[10,30,"rgba(14,203,129,.16)",L("Oversold","تشبع بيع")]]
        .forEach(([a, b, col, t]) => { c.fillStyle = col; c.fillRect(lx, y(b), rx - lx, y(a) - y(b)); c.fillStyle = "#6b7684"; c.font = "9px sans-serif"; c.textAlign = "right"; c.fillText(t, rx - 3, y(b) + 10); });
      c.font = "9px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "right"; c.fillStyle = "#848e9c"; [30,40,50,60,70].forEach(v => { c.fillText(v, lx - 4, y(v) + 3); c.strokeStyle = "#1e2329"; c.beginPath(); c.moveTo(lx, y(v)); c.lineTo(rx, y(v)); c.stroke(); });
      hit = []; if (!pts.length){ c.textAlign = "center"; c.fillStyle = "#848e9c"; c.font = "11px sans-serif"; c.fillText(busy ? L("Loading RSI…","بيحمّل الـ RSI…") : L("No data","مفيش بيانات"), W/2, H/2); return; }
      const avg = pts.reduce((a, p) => a + p.r, 0)/pts.length; c.setLineDash([5,4]); c.strokeStyle = "#f0b90b"; c.beginPath(); c.moveTo(lx, y(avg)); c.lineTo(rx, y(avg)); c.stroke(); c.setLineDash([]);
      c.fillStyle = "#f0b90b"; c.textAlign = "left"; c.fillText(L("avg ","متوسط ")+avg.toFixed(1), lx + 4, y(avg) - 4);
      const step = (rx - lx - 20)/Math.max(1, pts.length - 1);
      pts.forEach((p, i) => { const x = lx + 10 + i*step, yy = y(p.r), col = p.r >= 70 ? "#f6465d" : p.r >= 60 ? "#ff8f9e" : p.r <= 30 ? "#0ecb81" : p.r <= 40 ? "#7fe0b8" : "#848e9c";
        c.fillStyle = col; c.beginPath(); c.arc(x, yy, 3.5, 0, 6.3); c.fill(); c.fillStyle = "#c3c9d1"; c.font = "9px sans-serif"; c.textAlign = "center"; c.fillText(p.b, x, yy + (i % 2 ? 12 : -6)); hit.push({x, y:yy, s:p.s, r:p.r}); });
      info.textContent = pts.length + L(" coins · ", " عملة · ") + (pts.filter(p => p.r >= 70).length) + L(" overbought · "," تشبع شراء · ") + (pts.filter(p => p.r <= 30).length) + L(" oversold"," تشبع بيع"); };
    const load = async () => { if (busy) return; busy = true; draw();
      try { const tk = await okx("/market/tickers?instType=SPOT"), list = tk.filter(x => /-USDT$/.test(x.instId) && !/^(USDC|DAI|FDUSD|TUSD|USDE|PYUSD)-/.test(x.instId)).sort((a, b) => +b.volCcy24h - +a.volCcy24h).slice(0, +S.n).map(x => x.instId), out = [];
        for (let i = 0; i < list.length; i += 6){ await Promise.all(list.slice(i, i + 6).map(async id => { try { const k = await okx("/market/candles?instId="+id+"&bar="+S.tf+"&limit=100"); const cl = k.map(r => +r[4]).reverse(); const v = rsi(cl); if (v != null) out.push({s:id, b:id.split("-")[0], r:v, vi:list.indexOf(id)}); } catch(e){} })); }
        pts = out.sort((a, b) => a.vi - b.vi); } catch(e){ info.textContent = "OKX: " + (e.message || e); }
      busy = false; draw(); clearTimeout(tm); tm = setTimeout(load, 120000); };
    tfS.onchange = () => { S.tf = tfS.value; Ws.save(); pts = []; load(); }; nS.onchange = () => { S.n = +nS.value; Ws.save(); pts = []; load(); };
    cv.onclick = e => { const r = cv.getBoundingClientRect(), mx = e.clientX - r.left, my = e.clientY - r.top; let best = null, bd = 144; hit.forEach(h => { const d = (h.x - mx)**2 + (h.y - my)**2; if (d < bd){ bd = d; best = h; } }); if (best) Ws.broadcast({type:"watch", state:{group:0}}, best.s); };
    cv.title = L("Click a coin to open it in the linked widgets","دوس على عملة تفتحها في الويدجتات المربوطة");
    const ro = new ResizeObserver(() => draw()); ro.observe(cv); this.unsubs.push(() => { ro.disconnect(); clearTimeout(tm); }); load();
  }
  /* ---- liquidations: OKX public liquidation orders (no key) for the symbol's perpetual family. ONE exchange only, not the whole market ----
     forced SELL = longs liquidated, forced BUY = shorts liquidated; USD = contracts x ctVal x bankruptcy price (linear) or contracts x ctVal (inverse) */
  build_liq(){
    const S = this.state, ar = lang === "ar", L = (e, a) => ar ? a : e; S.sym = S.sym || SYMS[0]; S.big = S.big || 100000;
    const tb = el("div","tb"); this.symSel = this.symSelect(); const bg = el("select");
    [[10000,"$10K+"],[50000,"$50K+"],[100000,"$100K+"],[1000000,"$1M+"]].forEach(([v,t]) => { const o = el("option"); o.value = v; o.textContent = L("big ","كبيرة ")+t; bg.append(o); });
    bg.value = S.big; bg.onchange = () => { S.big = +bg.value; Ws.save(); this.liqDraw && this.liqDraw(); }; tb.append(this.symSel, bg);
    const hd = el("div"), box = el("div"), ft = el("div","m"); hd.style.cssText = "padding:4px 6px;font-size:11px"; box.style.cssText = "overflow:auto;flex:1;font:11px ui-monospace,Menlo,Consolas,monospace";
    ft.style.cssText = "padding:2px 6px;font-size:10px"; ft.textContent = L("OKX only (one exchange) - a cluster of liquidations often marks the end of a sweep. Polled every 10 s.", "OKX بس (بورصة واحدة) - تجمع تصفيات غالباً بيعلّم نهاية السويب. تحديث كل 10 ثواني.");
    this.body.append(tb, hd, box, ft); this.body.style.display = "flex"; this.body.style.flexDirection = "column";
    const usd = v => v >= 1e6 ? (v/1e6).toFixed(2)+"M" : v >= 1e3 ? (v/1e3).toFixed(1)+"K" : v.toFixed(0);
    let rows = [], err = "";
    this.liqDraw = () => {
      if (err){ hd.innerHTML = ""; box.innerHTML = '<div class="err">'+esc(err)+'</div>'; return; }
      const now = Date.now(), sum = (ms, side) => rows.filter(r => r.side === side && now - r.t <= ms).reduce((a, r) => a + r.usd, 0), span = rows.length ? now - rows[rows.length-1].t : 0;
      const line = (lab, ms) => { const lg = sum(ms, "L"), sh = sum(ms, "S"); return '<b>'+lab+'</b> <span style="color:var(--red)">'+L("longs","لونج")+' $'+usd(lg)+'</span> · <span style="color:var(--grn)">'+L("shorts","شورت")+' $'+usd(sh)+'</span>'; };
      hd.innerHTML = line("5m", 3e5) + '<br>' + line("1h", 36e5) + '<br><span class="m">' + rows.length + L(" orders, covering ", " أمر، بتغطي ") + Math.round(span/60000) + L(" min", " دقيقة") + '</span>';
      box.innerHTML = rows.slice(0, 100).map(r => { const b = r.usd >= S.big, c = r.side === "L" ? "var(--red)" : "var(--grn)";
        return '<div style="display:flex;gap:8px;padding:1px 6px;'+(b ? 'font-weight:700;background:rgba(240,185,11,.08)' : 'opacity:.8')+'"><span class="m">'+new Date(r.t).toLocaleTimeString()+'</span><span style="color:'+c+';flex:1">'
          +(r.side === "L" ? L("▼ longs liquidated","▼ تصفية لونج") : L("▲ shorts liquidated","▲ تصفية شورت"))+'</span><span>'+fmtP(r.p)+'</span><span style="min-width:62px;text-align:end">$'+usd(r.usd)+'</span></div>'; }).join("") || '<div class="m" style="padding:6px">'+L("No liquidations returned yet.","مفيش تصفيات لسه.")+'</div>';
    };
    this.resub = () => { this.clearSubs(); rows = []; err = ""; const sym = S.sym;
      if (!liqFam(sym)){ err = L("Liquidations: OKX crypto perpetuals only (pick e.g. BTC-USDT).","التصفيات: عقود OKX للكريبتو بس (اختار مثلاً BTC-USDT)."); this.liqDraw(); return; }
      let alive = true, tm = 0; this.unsubs.push(() => { alive = false; clearTimeout(tm); });
      const poll = async () => { try { const out = await okxLiqs(sym); if (!alive) return; rows = out || []; err = ""; this.liqDraw(); }
        catch(e){ if (!alive) return; err = "OKX: "+(e.message || e); this.liqDraw(); }
        if (alive) tm = setTimeout(poll, 10000); };
      poll(); };
    this.resub();
  }
  /* ---- external chart site in a frame (ChartLabs by default). Works only if the site allows framing; the site, its login and its data are theirs ---- */
  build_web(){
    const S = this.state, ar = lang === "ar", L = (e, a) => ar ? a : e, box = el("div","vbox"), bar = el("div","tb"), inp = el("input");
    inp.style.flex = "1"; inp.value = S.url || ""; inp.placeholder = "https://...";
    const go = el("button",null,L("Load","تحميل")), tab = el("button",null,"↗"); tab.title = L("Open in a new tab","افتح في تاب جديد");
    // free TradingView embed widgets (their data, no key) - same URL form their embed scripts load
    const tv = (w, o) => "https://s.tradingview.com/embed-widget/"+w+"/?locale="+(ar ? "ar_AE" : "en")+"#"+encodeURIComponent(JSON.stringify(Object.assign({colorTheme:"dark", isTransparent:false, width:"100%", height:"100%"}, o)));
    const pre = el("select"); [["", L("Presets…","جاهز…")], ["https://chartlabs.co/", "ChartLabs"],
      [tv("events", {importanceFilter:"0,1", countryFilter:"us,eu,gb,jp,cn"}), L("Economic calendar (TradingView)","المفكرة الاقتصادية (TradingView)")],
      [tv("forex-heat-map", {currencies:["EUR","USD","JPY","GBP","CHF","AUD","CAD","NZD"]}), L("Forex heat map (TradingView)","خريطة قوة العملات (TradingView)")],
      [tv("crypto-coins-heatmap", {dataSource:"Crypto", blockSize:"market_cap_calc", blockColor:"change"}), L("Crypto heat map (TradingView)","خريطة الكريبتو (TradingView)")],
      [tv("stock-heatmap", {dataSource:"SPX500", grouping:"sector", blockSize:"market_cap_basic", blockColor:"change"}), L("S&P 500 heat map (TradingView)","خريطة S&P 500 (TradingView)")]]
      .forEach(([v, t]) => { const o = el("option"); o.value = v; o.textContent = t; pre.append(o); });
    pre.onchange = () => { if (pre.value){ inp.value = pre.value; load(); } pre.value = ""; };
    const vf = el("div","vf"), note = el("div","m"); note.style.cssText = "padding:2px 6px;font-size:10px";
    note.textContent = L("Blank or refused? The site blocks embedding - use ↗. Sign-ins / broker links inside the frame may need third-party cookies.",
      "لو فاضي أو مرفوض: الموقع مانع العرض جوه مواقع تانية - استخدم ↗. تسجيل الدخول والبروكر جوه الإطار ممكن ما يشتغلش.");
    bar.append(pre, inp, go, tab); box.append(bar, vf, note); this.body.append(box); this.body.style.overflow = "hidden";
    const url = () => { let u = inp.value.trim(); if (u && !/^https:\/\//i.test(u)) u = "https://" + u.replace(/^\w+:\/\//, ""); return u; };
    const load = () => { const u = url(); S.url = u; Ws.save(); vf.innerHTML = "";
      if (!u) return; const f = el("iframe","vid"); f.src = u; f.referrerPolicy = "strict-origin-when-cross-origin"; f.allow = "fullscreen; clipboard-write";
      f.setAttribute("sandbox", "allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"); vf.append(f); };
    go.onclick = load; inp.onkeydown = e => { if (e.key === "Enter") load(); }; tab.onclick = () => { const u = url(); if (u) window.open(u, "_blank", "noopener"); };
    load();
  }
  /* ---- TradingView chart: TradingView's free embeddable Advanced Chart (their data + tools, live for crypto exchanges; some
     stock / index feeds are delayed by TradingView). Follows the linked symbol; any TradingView symbol can be typed. ---- */
  build_tvc(){
    const S = this.state, ar = lang === "ar", L = (e, a) => ar ? a : e; S.sym = S.sym || SYMS[0];
    // TradingView's embed widget forgets everything inside it (interval, indicators, chart type) whenever its frame is rebuilt: a refresh, a symbol change, a closed + re-opened widget. A page cannot read or write
    // another site's frame, so the settings are chosen HERE, passed to the widget on every load, and kept in this browser: per widget (saved with the workspace) and as the default for the next TradingView widget you open.
    const TVK = LS+"_tvset", TVD = (() => { try { return store.get(TVK, null) || {}; } catch(e){ return {}; } })();
    S.tvtf = S.tvtf || TVD.tvtf || "15"; if (!Array.isArray(S.tvst)) S.tvst = Array.isArray(TVD.tvst) ? TVD.tvst.slice() : []; S.tvsty = S.tvsty || TVD.tvsty || "1";
    const tvKeep = () => { try { store.set(TVK, {tvtf:S.tvtf, tvst:S.tvst, tvsty:S.tvsty}); } catch(e){} };
    const tb = el("div","tb"), inp = el("input"), tf = el("select"), go = el("button",null,"↻"), tab = el("button",null,"↗"), vf = el("div","vf"), note = el("div","m");
    this.symSel = this.symSelect(); inp.style.cssText = "flex:1;min-width:90px"; inp.placeholder = L("TradingView symbol, e.g. OKX:BTCUSDT","رمز TradingView، مثلاً OKX:BTCUSDT"); tab.title = L("Open on TradingView","افتح على TradingView");
    [["1","1m"],["5","5m"],["15","15m"],["60","1H"],["240","4H"],["D","1D"],["W","1W"]].forEach(([v, t]) => { const o = el("option"); o.value = v; o.textContent = t; tf.append(o); }); tf.value = S.tvtf;
    note.style.cssText = "padding:2px 6px;font-size:10px"; note.textContent = L("TradingView's own widget and data (no key). Crypto is live; some stock / index symbols are delayed by TradingView. Signals and drawings of this app are not inside it.",
      "ويدجت وبيانات TradingView نفسها (من غير مفتاح). الكريبتو لحظي؛ بعض الأسهم والمؤشرات متأخرة من TradingView. إشارات ورسومات التطبيق مش جواه.");
    const TVSTUDY = [["RSI@tv-basicstudies","RSI"],["MACD@tv-basicstudies","MACD"],["MASimple@tv-basicstudies","SMA"],["MAExp@tv-basicstudies","EMA"],["BB@tv-basicstudies","Bollinger"],["Volume@tv-basicstudies","Volume"],["VWAP@tv-basicstudies","VWAP"],
      ["Stochastic@tv-basicstudies","Stoch"],["StochasticRSI@tv-basicstudies","StochRSI"],["ATR@tv-basicstudies","ATR"],["ADX@tv-basicstudies","ADX"],["IchimokuCloud@tv-basicstudies","Ichimoku"],["PSAR@tv-basicstudies","SAR"],["PivotPointsStandard@tv-basicstudies","Pivots"]];
    const TVSTYLE = [["1",L("Candles","شموع")],["0",L("Bars","أعمدة")],["2",L("Line","خط")],["3",L("Area","مساحة")],["8",L("Heikin Ashi","هيكين آشي")],["9",L("Hollow","شموع مفرغة")]];
    const cfgB = el("button", null, "ƒx"), pop = el("div"); cfgB.title = L("Indicators and chart type of this TradingView chart. They are saved here and applied every time the widget loads","مؤشرات ونوع شارت تريدنج فيو. بتتحفظ هنا وبتتطبق كل مرة الويدجت يفتح");
    pop.style.cssText = "display:none;position:absolute;z-index:30;background:var(--panel2);border:1px solid var(--line);border-radius:6px;padding:8px;max-width:260px;box-shadow:0 6px 20px #0008;font-size:12px"; pop.className = "tvpop";
    const popFill = () => { pop.innerHTML = ""; const hd = el("div", "m", L("Chart type","نوع الشارت")); hd.style.marginBottom = "4px"; const st = el("select"); TVSTYLE.forEach(([v, t]) => { const o = el("option"); o.value = v; o.textContent = t; st.append(o); }); st.value = S.tvsty; st.onchange = () => { S.tvsty = st.value; tvKeep(); load(); }; pop.append(hd, st);
      const h2 = el("div", "m", L("Indicators","المؤشرات")); h2.style.margin = "8px 0 4px"; pop.append(h2); const g = el("div"); g.style.cssText = "display:grid;grid-template-columns:1fr 1fr;gap:2px 10px";
      TVSTUDY.forEach(([id, t]) => { const lb = el("label"); lb.style.cssText = "display:flex;gap:5px;align-items:center;cursor:pointer;min-height:26px"; const cb = el("input"); cb.type = "checkbox"; cb.checked = S.tvst.includes(id);
        cb.onchange = () => { S.tvst = cb.checked ? S.tvst.concat([id]) : S.tvst.filter(x => x !== id); tvKeep(); load(); }; lb.append(cb, document.createTextNode(t)); g.append(lb); }); pop.append(g);
      const nt = el("div", "m", L("Indicators you add inside TradingView's own toolbar cannot be remembered (a page cannot read another site's frame): add them here instead.","المؤشرات اللي بتضيفها من شريط تريدنج فيو نفسه مش بتتحفظ (الصفحة مش بتقدر تقرا فريم موقع تاني): ضيفها من هنا.")); nt.style.cssText = "margin-top:6px;font-size:10px"; pop.append(nt); };
    cfgB.onclick = e => { e.stopPropagation(); if (pop.style.display === "block"){ pop.style.display = "none"; return; } popFill(); const r = cfgB.getBoundingClientRect(), br = this.body.getBoundingClientRect(); pop.style.left = Math.max(2, Math.min(r.left - br.left, br.width - 270))+"px"; pop.style.top = (r.bottom - br.top + 2)+"px"; pop.style.display = "block"; };
    document.addEventListener("pointerdown", e => { if (pop.style.display === "block" && !pop.contains(e.target) && e.target !== cfgB) pop.style.display = "none"; });
    this.body.style.position = "relative";
    tb.append(this.symSel, inp, tf, cfgB, go, tab); this.body.append(tb, vf, note, pop); this.body.style.display = "flex"; this.body.style.flexDirection = "column"; vf.style.flex = "1";
    const url = () => { const sym = (S.tvsym || tvSym(S.sym)).trim(); S.tvsym_last = sym;
      return "https://s.tradingview.com/embed-widget/advanced-chart/?locale="+(ar ? "ar_AE" : "en")+"#"+encodeURIComponent(JSON.stringify({symbol:sym, interval:S.tvtf, timezone:"Etc/UTC", theme:"dark", colorTheme:"dark",
        autosize:true, width:"100%", height:"100%", allow_symbol_change:true, studies:S.tvst.slice(), style:S.tvsty, hide_side_toolbar:false, withdateranges:true, save_image:false, details:false, calendar:false, support_host:"https://www.tradingview.com"})); };
    const load = () => { inp.value = S.tvsym || tvSym(S.sym); vf.innerHTML = ""; const f = el("iframe","vid"); f.src = url(); f.referrerPolicy = "strict-origin-when-cross-origin"; f.allow = "fullscreen; clipboard-write";
      f.setAttribute("sandbox", "allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"); f.style.cssText = "width:100%;height:100%;border:0"; vf.append(f); Ws.save(); };
    inp.onkeydown = e => { if (e.key === "Enter"){ S.tvsym = inp.value.trim().toUpperCase(); load(); } };
    go.onclick = () => { S.tvsym = inp.value.trim().toUpperCase() === tvSym(S.sym) ? "" : inp.value.trim().toUpperCase(); load(); };
    tf.onchange = () => { S.tvtf = tf.value; tvKeep(); load(); };
    tab.onclick = () => window.open("https://www.tradingview.com/chart/?symbol="+encodeURIComponent(S.tvsym_last || tvSym(S.sym)), "_blank", "noopener");
    this.resub = () => { this.setTitle(); S.tvsym = ""; load(); };   // a linked symbol change wins over a typed symbol
    load();
  }
  /* ---- notes ---- */
  /* ---- value levels: volume-profile POC / VAH / VAL on every timeframe ---- */
  build_valuelv(){
    const S = this.state; S.sym = S.sym || SYMS[0]; this.symSel = this.symSelect();
    const ar = lang === "ar", L = (e, a) => ar ? a : e;
    const tb = el("div","tb"), rf = el("button",null,"↻"), show = el("button",null,T("showchart")), clr = el("button",null,"✕"), box = el("div"); this.levelsData = {};
    tb.append(this.symSel, rf, show, clr); this.body.append(tb, box); this.body.style.overflow = "auto";
    const render = () => {
      const D = this.levelsData; let px = null; Object.values(D).forEach(d => { if (d && d.px) px = d.px; });
      let h = "<table class='rdt'><tr><th>"+L("TF","الفريم")+"</th><th>VAH</th><th>POC</th><th>VAL</th><th>"+L("Price vs value","السعر مقابل القيمة")+"</th></tr>";
      VP_TFS.forEach(([k,lab]) => { const d = D[k]; if (!d || !d.vp){ h += "<tr><td>"+lab+"</td><td colspan=4 class='m'>…</td></tr>"; return; }
        const v = d.vp, dist = (d.px - v.poc)/v.poc*100; let st, col;
        if (d.px > v.vah){ st = L("Above value ▲ (magnet ↓ POC)","فوق القيمة ▲ (المغناطيس ↓ POC)"); col = "#f6465d"; }
        else if (d.px < v.val){ st = L("Below value ▼ (magnet ↑ POC)","تحت القيمة ▼ (المغناطيس ↑ POC)"); col = "#0ecb81"; }
        else { st = L("Inside value ◆","جوه القيمة ◆"); col = "#848e9c"; }
        h += "<tr><td><b>"+lab+"</b></td><td>"+fmtP(v.vah)+"</td><td style='color:#f0b90b'><b>"+fmtP(v.poc)+"</b></td><td>"+fmtP(v.val)+"</td><td style='color:"+col+"'>"+st+" · "+(dist>=0?"+":"")+dist.toFixed(2)+"% "+L("from POC","من POC")+"</td></tr>"; });
      h += "</table>";
      const pocs = VP_TFS.map(([k]) => D[k] && D[k].vp ? {k, p:D[k].vp.poc, px:D[k].px} : null).filter(Boolean);
      if (pocs.length){ const px0 = pocs[0].px, near = pocs.slice().sort((a,b) => Math.abs(a.p-px0)-Math.abs(b.p-px0))[0];
        h += "<div class='m' style='padding:6px 8px'>"+L("Nearest magnet: ","أقرب مغناطيس: ")+"<b style='color:#f0b90b'>"+near.k+" POC "+fmtP(near.p)+"</b> ("+((near.p-px0)/px0*100).toFixed(2)+"%)</div>"; }
      box.innerHTML = h;
    };
    const load = async () => {
      const sym = S.sym, tok = this.lvTok = (this.lvTok||0)+1; this.levelsData = {}; render();
      await Promise.all(VP_TFS.map(async ([k]) => { try {
        const rows = (await okx("/market/candles?instId="+encodeURIComponent(sym)+"&bar="+k+"&limit=300")).map(r => ({t:+r[0], h:+r[2], l:+r[3], c:+r[4], v:+r[5]})).reverse();
        if (tok !== this.lvTok) return; this.levelsData[k] = {vp:vpCalc(rows, 60), px:rows[rows.length-1].c}; render(); } catch(e){ } }));
    };
    const push = on => Ws.panels.filter(p => p.type === "chart").forEach(p => { p.chart.vpLv = on ? VP_TFS.flatMap(([k]) => { const d = this.levelsData[k]; return d && d.vp ? [["POC",d.vp.poc],["VAH",d.vp.vah],["VAL",d.vp.val]].map(([n,pr]) => ({tf:k,k:n,p:pr})) : []; }) : null; p.chart.draw(); });
    this.resub = () => { this.setTitle(); load(); }; this.setSymbol = sym => { S.sym = sym; this.symSel.value = sym; Ws.save(); this.resub(); };
    rf.onclick = load; show.onclick = () => push(true); clr.onclick = () => push(false); this.symSel.value = S.sym; this.destroy = () => push(false);
    this.lvTimer = setInterval(load, 120000); const od = this.destroy; this.destroy = () => { clearInterval(this.lvTimer); od(); }; load();
  }

  /* ---- crypto fundamentals (OKX public data only, no key): funding, open interest, long/short, taker flow, volume ---- */
  build_fund(){
    const S = this.state; S.sym = S.sym || SYMS[0]; this.symSel = this.symSelect();
    const ar = lang === "ar", L = (e, a) => ar ? a : e, G = "#0ecb81", R = "#f6465d", Y = "#f0b90b", M = "#848e9c";
    const tb = el("div","tb"), rf = el("button",null,"↻"), box = el("div"); tb.append(this.symSel, rf); this.body.append(tb, box); this.body.style.overflow = "auto";
    const usd = v => (v < 0 ? "-" : "") + "$" + fmtV(Math.abs(v)), pc = (v, d) => (v >= 0 ? "+" : "") + v.toFixed(d == null ? 2 : d) + "%", col = (v, up, dn) => v > up ? G : v < dn ? R : M;
    let D = null;
    const render = () => {
      if (!D){ box.innerHTML = "<div class='m' style='padding:8px'>…</div>"; return; }
      const na = "<span class='m'>n/a</span>"; let h = "<table class='rdt'>", reads = [];
      const row = (k, v, note) => h += "<tr><td><b>"+k+"</b></td><td>"+v+"</td><td class='m'>"+(note||"")+"</td></tr>";
      // funding
      if (D.fr){ const f = D.fr.rate*100, ann = D.fr.rate*(24/D.fr.hrs)*365*100;
        row(L("Funding rate","معدل التمويل"), "<b style='color:"+(f > 0.03 ? R : f < -0.01 ? G : M)+"'>"+f.toFixed(4)+"%</b> / "+D.fr.hrs+"h", L("≈ ","≈ ")+ann.toFixed(1)+"% "+L("per year","سنويا")+(D.frAvg != null ? " · "+L("7d avg ","متوسط 7 أيام ")+(D.frAvg*100).toFixed(4)+"%" : ""));
        if (f > 0.03) reads.push([R, L("Funding is high: longs are crowded and paying shorts (squeeze/flush risk for longs).","التمويل عالي: اللونج زحمة وبتدفع للشورت (خطر تصفية للونج).")]);
        else if (f < -0.01) reads.push([G, L("Funding is negative: shorts pay longs - crowded shorts can fuel a squeeze up.","التمويل سالب: الشورت بيدفع للونج - زحمة الشورت ممكن تغذي صعود سريع (سكويز).")]);
        else reads.push([M, L("Funding is near neutral - no crowding signal.","التمويل قريب من الصفر - مفيش زحمة واضحة.")]); }
      else row(L("Funding rate","معدل التمويل"), na, L("no perpetual swap for this symbol on OKX","مفيش عقد دائم للرمز ده على OKX"));
      // open interest
      if (D.oi){ const ch = D.oiCh;
        row(L("Open interest","الفائدة المفتوحة"), "<b>"+usd(D.oi)+"</b>"+(ch != null ? " <span style='color:"+col(ch,0,0)+"'>"+pc(ch,1)+"</span>" : ""), ch != null ? L("change over "+D.oiHrs+"h","التغير خلال "+D.oiHrs+" ساعة") : L("history unavailable","مفيش تاريخ")+(D.errs && D.errs.oi ? " ("+D.errs.oi+")" : ""));
        if (ch != null && D.pxCh != null){ const up = D.pxCh >= 0, oiUp = ch >= 0;
          reads.push(up && oiUp ? [G, L("Price up + OI up: new longs entering - healthy trend.","السعر طالع + الفائدة طالعة: لونج جديد داخل - اتجاه صحي.")] : up ? [Y, L("Price up + OI down: short covering, not new buying - weaker move.","السعر طالع + الفائدة نازلة: تغطية شورت مش شراء جديد - حركة أضعف.")] : oiUp ? [R, L("Price down + OI up: new shorts entering - bearish pressure.","السعر نازل + الفائدة طالعة: شورت جديد داخل - ضغط هبوطي.")] : [Y, L("Price down + OI down: longs closing/liquidated - may be near exhaustion.","السعر نازل + الفائدة نازلة: لونج بيقفل/بيتصفى - ممكن قرب الاستنزاف.")]); } }
      else row(L("Open interest","الفائدة المفتوحة"), na, "");
      // long/short account ratio
      if (D.ls){ row(L("Long/Short accounts","نسبة لونج/شورت (حسابات)"), "<b style='color:"+(D.ls > 1.5 ? R : D.ls < 0.8 ? G : M)+"'>"+D.ls.toFixed(2)+"</b>"+(D.ls0 ? " <span class='m'>("+L("was ","كانت ")+D.ls0.toFixed(2)+" "+L("before","قبل")+" "+D.lsHrs+"h)</span>" : ""), L("accounts net long vs short (contrarian at extremes)","عدد الحسابات لونج مقابل شورت (عكسي عند التطرف)"));
        if (D.ls > 1.5) reads.push([R, L("Long/short ratio is stretched to the long side - retail crowd long.","النسبة مايلة بقوة للونج - الجمهور داخل لونج.")]);
        else if (D.ls < 0.8) reads.push([G, L("Long/short ratio leans short - crowd short, contrarian bullish.","النسبة مايلة للشورت - الجمهور شورت، إشارة عكسية صاعدة.")]); }
      else row(L("Long/Short accounts","نسبة لونج/شورت (حسابات)"), na, D.errs && D.errs.ls ? "OKX: "+D.errs.ls : "");
      // taker flow
      if (D.tk){ row(L("Taker buy share","حصة الشراء العدواني"), "<b style='color:"+col(D.tk,52,48)+"'>"+D.tk.toFixed(1)+"%</b>"+(D.tk1 != null ? " <span class='m'>("+L("last 1h ","آخر ساعة ")+D.tk1.toFixed(1)+"%)</span>" : ""), L("market buys vs sells in contracts, last "+D.tkHrs+"h","شراء مقابل بيع بأوامر السوق في العقود، آخر "+D.tkHrs+" ساعة")); }
      else row(L("Taker buy share","حصة الشراء العدواني"), na, D.errs && D.errs.tk ? "OKX: "+D.errs.tk : "");
      // volume
      if (D.vol != null){ row(L("24h volume (spot)","حجم 24 ساعة (سبوت)"), "<b>"+usd(D.vol)+"</b>"+(D.volRel != null ? " <span style='color:"+col(D.volRel-100,30,-30)+"'>"+D.volRel.toFixed(0)+"%</span>" : ""), D.volRel != null ? L("of the previous 7-day average","من متوسط آخر 7 أيام") : ""); }
      else row(L("24h volume (spot)","حجم 24 ساعة (سبوت)"), na, "");
      if (D.swVol != null) row(L("24h volume (perp)","حجم 24 ساعة (دائم)"), "<b>"+usd(D.swVol)+"</b>", D.vol ? L("perp/spot ","دائم/سبوت ")+(D.swVol/D.vol).toFixed(1)+"x" : "");
      if (D.basis != null) row(L("Perp basis","فرق الدائم عن السبوت"), "<b style='color:"+col(D.basis,0.1,-0.1)+"'>"+pc(D.basis,3)+"</b>", L("perpetual price vs spot","سعر الدائم مقابل السبوت"));
      const cm = CFG.cmc && CFG.cmc.ok ? CFG.cmc : null, base0 = S.sym.split("-")[0];
      if (cm){ const g = cm.global, me = cm.coins.find(c => c.sym === base0), own = base0 === "BTC" ? g.btc_dom : base0 === "ETH" ? g.eth_dom : me && g.mcap ? me.mcap/g.mcap*100 : null;
        row(L("Dominance","الهيمنة (Dominance)"), own != null ? "<b>"+own.toFixed(2)+"%</b>" : na, "BTC "+(+g.btc_dom).toFixed(1)+"% · ETH "+(+g.eth_dom).toFixed(1)+"%"+(me ? " · "+L("rank ","الترتيب ")+"#"+me.rank : "") + " (CoinMarketCap)"); }
      else row(L("Dominance","الهيمنة (Dominance)"), na, L("not provided by OKX - needs the CoinMarketCap key (CMC_API_KEY)","OKX مش بتوفرها - محتاجة مفتاح CoinMarketCap (CMC_API_KEY)"));
      h += "</table>";
      if (reads.length) h += "<div style='padding:6px 8px;font-size:12px;line-height:1.7;border-top:1px solid #2b3139'><b>"+L("Reading","القراءة")+"</b><br>"+reads.map(r => "<span style='color:"+r[0]+"'>● </span>"+r[1]).join("<br>")+"</div>";
      h += "<div class='m' style='padding:4px 8px;font-size:10px'>"+L("Rules of thumb from OKX public data - context for a trade, not a signal on its own. Updated ","قواعد استرشادية من بيانات OKX العامة - سياق للصفقة مش إشارة بحد ذاتها. آخر تحديث ")+new Date(D.at).toLocaleTimeString()+"</div>";
      box.innerHTML = h;
    };
    const load = async () => {
      const sym = S.sym, tok = this.fdTok = (this.fdTok||0)+1, base = sym.split("-")[0], sw = base+"-USDT-SWAP", enc = encodeURIComponent, d = {at:Date.now()};
      D = null; render(); const g = async (f) => { try { return await f(); } catch(e){ return null; } };
      const errs = d.errs = {}, slp = ms => new Promise(r => setTimeout(r, ms));
      const g2 = async (name, ...fs) => { for (const f of fs){ try { const r = await f(); if (r && r.length) return r; errs[name] = "empty"; } catch(e){ errs[name] = String(e.message || e).slice(0, 40); } await slp(350); } return null; };
      const rub = (async () => {   // rubik (statistics) endpoints are rate-limited: go one by one, with a newer per-instrument route as fallback
        const oiv = await g2("oi", () => okx("/rubik/stat/contracts/open-interest-volume?ccy="+base+"&period=1H"), () => okx("/rubik/stat/contracts/open-interest-history?instId="+sw+"&period=1H&limit=48").then(a => a.map(x => [x[0], x[3]]))); await slp(350);
        const ls = await g2("ls", () => okx("/rubik/stat/contracts/long-short-account-ratio?ccy="+base+"&period=1H"), () => okx("/rubik/stat/contracts/long-short-account-ratio-contract?instId="+sw+"&period=1H&limit=48")); await slp(350);
        const tk = await g2("tk", () => okx("/rubik/stat/taker-volume?ccy="+base+"&instType=CONTRACTS&period=1H"), () => okx("/rubik/stat/taker-volume-contract?instId="+sw+"&period=1H&limit=48"));
        return [oiv, ls, tk]; })();
      const [fr, frh, oi, sp, sT, dc] = await Promise.all([
        g(() => okx("/public/funding-rate?instId="+sw)), g(() => okx("/public/funding-rate-history?instId="+sw+"&limit=21")), g(() => okx("/public/open-interest?instType=SWAP&instId="+sw)),
        g(() => okx("/market/ticker?instId="+enc(sym))), g(() => okx("/market/ticker?instId="+enc(sw))), g(() => okx("/market/candles?instId="+enc(sym)+"&bar=1D&limit=8"))]);
      const [oiv, ls, tk] = await rub;
      if (tok !== this.fdTok) return;
      if (fr && fr[0]){ const f = fr[0], hrs = f.nextFundingTime && f.fundingTime ? Math.round((+f.nextFundingTime - +f.fundingTime)/3600000) : 8; d.fr = {rate:+f.fundingRate, hrs:hrs > 0 ? hrs : 8}; }
      if (frh && frh.length) d.frAvg = frh.reduce((a, x) => a + +x.fundingRate, 0) / frh.length;
      if (sp && sp[0]){ d.pxCh = (+sp[0].last - +sp[0].open24h)/+sp[0].open24h*100; d.px = +sp[0].last; d.vol = +sp[0].volCcy24h; }
      if (sT && sT[0]){ d.swVol = +sT[0].volCcy24h * +sT[0].last; if (d.px) d.basis = (+sT[0].last - d.px)/d.px*100; }
      const ser = a => (a || []).map(x => x.map(Number)).sort((p, q) => q[0]-p[0]);   // newest first
      const O = ser(oiv); if (O.length){ d.oi = O[0][1]; const k = Math.min(24, O.length-1); if (k >= 6 && O[k][1] > 0){ d.oiCh = (O[0][1]/O[k][1]-1)*100; d.oiHrs = k; } }
      if (!d.oi && oi && oi[0]) d.oi = +oi[0].oiUsd;
      const LS = ser(ls); if (LS.length){ d.ls = LS[0][1]; const k = Math.min(24, LS.length-1); if (k >= 6){ d.ls0 = LS[k][1]; d.lsHrs = k; } }
      const T_ = ser(tk); if (T_.length){ const w = T_.slice(0, 24), b = w.reduce((a, x) => a + x[2], 0), t = w.reduce((a, x) => a + x[1] + x[2], 0); if (t > 0){ d.tk = b/t*100; d.tkHrs = w.length; d.tk1 = T_[0][1]+T_[0][2] > 0 ? T_[0][2]/(T_[0][1]+T_[0][2])*100 : null; } }
      if (dc && dc.length > 3){ const q = dc.map(r => +r[7]); const prev = q.slice(1), avg = prev.reduce((a, b) => a + b, 0)/prev.length; if (d.vol == null) d.vol = q[0]; if (avg > 0 && d.vol > 0) d.volRel = d.vol/avg*100; }
      D = d; render();
    };
    this.resub = () => { this.setTitle(); load(); }; this.setSymbol = sym => { S.sym = sym; this.symSel.value = sym; Ws.save(); this.resub(); };
    rf.onclick = load; this.symSel.value = S.sym; this.fdTimer = setInterval(load, 300000); this.destroy = () => clearInterval(this.fdTimer); load();
  }

  /* ---- CoinMarketCap: global market + top coins (server-side fetch, key never reaches the browser) ---- */
  build_cmc(){
    const ar = lang === "ar", L = (e, a) => ar ? a : e, G = "#0ecb81", R = "#f6465d", C = CFG.cmc || {};
    const tb = el("div","tb"), q = el("input"); q.placeholder = L("Filter e.g. SOL","فلتر مثلا SOL"); q.style.width = "120px"; tb.append(q);
    const hd = el("div"), box = el("div"); this.body.append(tb, hd, box); this.body.style.overflow = "auto";
    const pc = v => v == null ? "<span class='m'>–</span>" : "<span style='color:"+(v >= 0 ? G : R)+"'>"+(v >= 0 ? "+" : "")+v.toFixed(2)+"%</span>", usd = v => v == null ? "–" : "$"+(v >= 1e12 ? (v/1e12).toFixed(2)+"T" : fmtV(v));
    if (!C.ok){ const msg = {nokey:L("Add CMC_API_KEY to Streamlit secrets (free Basic key from pro.coinmarketcap.com) and reload.","ضيف CMC_API_KEY في Secrets بتاعة Streamlit (مفتاح Basic مجاني من pro.coinmarketcap.com) وأعد تحميل الصفحة."),
        badkey:L("CoinMarketCap rejected the key - check CMC_API_KEY.","CoinMarketCap رفض المفتاح - راجع CMC_API_KEY."), limit:L("Monthly/minute credit limit reached - try later.","وصلت لحد الاستخدام - جرب بعدين."), net:L("CoinMarketCap unreachable from the server right now.","CoinMarketCap مش متاح من السيرفر دلوقتي.")}[C.err] || L("No CoinMarketCap data.","مفيش بيانات من CoinMarketCap.");
      box.innerHTML = "<div class='m' style='padding:10px;line-height:1.7'>"+msg+"</div>"; return; }
    const g = C.global || {};
    hd.innerHTML = "<div style='display:flex;flex-wrap:wrap;gap:14px;padding:6px 8px;font-size:12px;border-bottom:1px solid #2b3139'>"
      + "<span>"+L("Market cap","القيمة السوقية")+" <b>"+usd(g.mcap)+"</b> "+pc(g.mcap_ch)+"</span><span>"+L("24h vol","حجم 24س")+" <b>"+usd(g.vol)+"</b> "+pc(g.vol_ch)+"</span>"
      + "<span>BTC.D <b style='color:#f0b90b'>"+(+g.btc_dom).toFixed(1)+"%</b></span><span>ETH.D <b style='color:#627eea'>"+(+g.eth_dom).toFixed(1)+"%</b></span>"
      + "<span>"+L("Alts","الباقي")+" <b>"+(100-g.btc_dom-g.eth_dom).toFixed(1)+"%</b></span></div>";
    const render = () => { const f = q.value.trim().toUpperCase(), rows = C.coins.filter(c => !f || (c.sym||"").toUpperCase().includes(f) || (c.name||"").toUpperCase().includes(f));
      box.innerHTML = "<table class='rdt'><tr><th>#</th><th>"+L("Coin","العملة")+"</th><th>"+L("Price","السعر")+"</th><th>1h</th><th>24h</th><th>7d</th><th>"+L("Mkt cap","القيمة")+"</th><th>"+L("Vol 24h","حجم 24س")+"</th></tr>"
        + rows.map(c => "<tr><td>"+c.rank+"</td><td><b>"+c.sym+"</b> <span class='m'>"+(c.name||"")+"</span></td><td>"+(c.price != null ? fmtP(c.price) : "–")+"</td><td>"+pc(c.h1)+"</td><td>"+pc(c.d1)+"</td><td>"+pc(c.d7)+"</td><td>"+usd(c.mcap)+"</td><td>"+usd(c.vol)+"</td></tr>").join("")
        + "</table><div class='m' style='padding:4px 8px;font-size:10px'>CoinMarketCap · "+L("refreshes every 15 min on page load; free plan = personal use","بيتحدث كل 15 دقيقة مع تحميل الصفحة؛ الخطة المجانية للاستخدام الشخصي")+"</div>"; };
    q.oninput = render; render();
  }

  /* ---- macro fundamentals: FRED (rates, inflation, jobs, dollar, VIX) + CFTC COT speculator positioning ---- */
  build_macrof(){
    const ar = lang === "ar", L = (e, a) => ar ? a : e, G = "#0ecb81", R = "#f6465d", Y = "#f0b90b", M = "#848e9c", C = CFG.macrof || {};
    const box = el("div"); this.body.append(box); this.body.style.overflow = "auto";
    const AR = {"Fed funds rate %":"فايدة الفيدرالي %","US 2Y yield %":"عائد سندات 2 سنة %","US 10Y yield %":"عائد سندات 10 سنين %","10Y-2Y curve %":"منحنى 10-2 سنة %","CPI inflation YoY %":"التضخم السنوي %","Unemployment %":"البطالة %","Nonfarm payrolls (monthly chg, K)":"الوظائف غير الزراعية (تغير شهري ألف)","Dollar index (broad)":"مؤشر الدولار (واسع)","VIX":"VIX (الخوف)"};
    const num = (v, d) => v == null ? "–" : v.toFixed(d == null ? 2 : d), reads = [];
    let h = "<div style='padding:5px 8px;font-weight:700;border-bottom:1px solid #2b3139'>FRED · "+L("US macro","الماكرو الأمريكي")+"</div>";
    if (C.fred_err){ h += "<div class='m' style='padding:8px'>"+(C.fred_err === "badkey" ? L("FRED rejected the key - check FRED_API_KEY.","FRED رفض المفتاح - راجع FRED_API_KEY.") : L("Add FRED_API_KEY to Streamlit secrets (free key from fred.stlouisfed.org) and reload.","ضيف FRED_API_KEY في Secrets بتاعة Streamlit (مفتاح مجاني من fred.stlouisfed.org) وأعد تحميل الصفحة."))+"</div>"; }
    else if (!(C.fred||[]).length) h += "<div class='m' style='padding:8px'>…</div>";
    else {
      h += "<table class='rdt'><tr><th>"+L("Indicator","المؤشر")+"</th><th>"+L("Latest","آخر قراءة")+"</th><th>"+L("Previous","السابقة")+"</th><th>"+L("Date","التاريخ")+"</th></tr>";
      C.fred.forEach(f => { if (!f.ok){ h += "<tr><td>"+(ar && AR[f.label] || f.label)+"</td><td colspan=3 class='m'>n/a</td></tr>"; return; }
        const up = f.val - f.prev, inv = f.id === "T10Y2Y" && f.val < 0, c = f.id === "VIXCLS" ? (f.val > 25 ? R : f.val < 15 ? G : M) : inv ? R : M;
        h += "<tr><td><b>"+(ar && AR[f.label] || f.label)+"</b></td><td><b style='color:"+c+"'>"+num(f.val, f.id === "DTWEXBGS" || f.id === "PAYEMS" ? 1 : 2)+"</b> <span style='color:"+(up > 0 ? G : up < 0 ? R : M)+"'>"+(up >= 0 ? "▲" : "▼")+"</span></td><td class='m'>"+num(f.prev, f.id === "DTWEXBGS" || f.id === "PAYEMS" ? 1 : 2)+"</td><td class='m'>"+f.date+"</td></tr>"; });
      h += "</table>";
      const g = id => (C.fred.find(f => f.id === id && f.ok) || {}).val;
      if (g("T10Y2Y") != null && g("T10Y2Y") < 0) reads.push([R, L("Yield curve inverted (10Y below 2Y): historically a recession warning, supportive of gold and bonds.","المنحنى مقلوب (10 سنين تحت سنتين): إنذار ركود تاريخيا، داعم للذهب والسندات.")]);
      if (g("VIXCLS") != null && g("VIXCLS") > 25) reads.push([R, L("VIX above 25: fear in equities - risk-off, crypto usually follows lower.","VIX فوق 25: خوف في الأسهم - هروب من المخاطرة والكريبتو غالبا بيتبع.")]);
      else if (g("VIXCLS") != null && g("VIXCLS") < 15) reads.push([G, L("VIX below 15: calm market - risk-on conditions.","VIX تحت 15: سوق هادي - ظروف رغبة في المخاطرة.")]);
      if (g("CPIAUCSL") != null && g("CPIAUCSL") > 3.5) reads.push([Y, L("Inflation above 3.5%: the Fed has little room to cut - pressure on risk assets.","التضخم فوق 3.5%: الفيدرالي مقدرش يخفض بسهولة - ضغط على الأصول عالية المخاطر.")]);
    }
    h += "<div style='padding:5px 8px;font-weight:700;border-top:1px solid #2b3139;border-bottom:1px solid #2b3139'>CFTC COT · "+L("speculators (non-commercial) net position","صافي مراكز المضاربين (غير التجاريين)")+"</div>";
    const cot = C.cot || [];
    if (!cot.length) h += "<div class='m' style='padding:8px'>…</div>";
    else {
      h += "<table class='rdt'><tr><th>"+L("Market","السوق")+"</th><th>"+L("Net long","صافي لونج")+"</th><th>"+L("Weekly chg","تغير أسبوعي")+"</th><th>"+L("52w position","موقعه في 52 أسبوع")+"</th></tr>";
      cot.forEach(c => { if (!c.ok){ h += "<tr><td>"+c.name+"</td><td colspan=3 class='m'>n/a</td></tr>"; return; }
        const col = c.pct >= 80 ? R : c.pct <= 20 ? G : M;
        h += "<tr><td><b>"+c.name+"</b></td><td style='color:"+(c.net >= 0 ? G : R)+"'>"+(c.net >= 0 ? "+" : "")+c.net.toLocaleString("en-US")+"</td><td style='color:"+(c.chg > 0 ? G : c.chg < 0 ? R : M)+"'>"+(c.chg == null ? "–" : (c.chg >= 0 ? "+" : "")+c.chg.toLocaleString("en-US"))+"</td><td><span style='display:inline-block;width:70px;height:6px;background:#2b3139;border-radius:3px;vertical-align:middle'><span style='display:block;width:"+c.pct+"%;height:6px;background:"+col+";border-radius:3px'></span></span> <b style='color:"+col+"'>"+c.pct+"</b></td></tr>";
        if (c.pct >= 90) reads.push([R, c.name+": "+L("speculators at a 52-week extreme long - crowded, reversal risk.","المضاربين في أعلى لونج في 52 أسبوع - زحمة وخطر انعكاس.")]);
        else if (c.pct <= 10) reads.push([G, c.name+": "+L("speculators at a 52-week extreme short - crowded, squeeze/reversal risk.","المضاربين في أعلى شورت في 52 أسبوع - زحمة وخطر سكويز/انعكاس.")]); });
      h += "</table><div class='m' style='padding:2px 8px;font-size:10px'>"+L("Report date ","تاريخ التقرير ")+(cot.find(c => c.ok) || {}).date+" · "+L("published Fridays for Tuesday positions","بيصدر الجمعة عن مراكز الثلاثاء")+"</div>";
    }
    if (reads.length) h += "<div style='padding:6px 8px;font-size:12px;line-height:1.7;border-top:1px solid #2b3139'><b>"+L("Reading","القراءة")+"</b><br>"+reads.map(r => "<span style='color:"+r[0]+"'>● </span>"+r[1]).join("<br>")+"</div>";
    h += "<div class='m' style='padding:4px 8px;font-size:10px'>"+L("Context for a decision, not a signal on its own. Refreshes with the page (cached 6h).","سياق للقرار مش إشارة بحد ذاتها. بيتحدث مع الصفحة (كاش 6 ساعات).")+"</div>";
    box.innerHTML = h;
  }

  /* ---- stock fundamentals (Finnhub, fetched server-side; key never reaches the browser) ---- */
  build_stockf(){
    const ar = lang === "ar", L = (e, a) => ar ? a : e, G = "#0ecb81", R = "#f6465d", Y = "#f0b90b", M = "#848e9c", C = CFG.stockf || {};
    const S = this.state, tb = el("div","tb"), sel = el("select"), box = el("div"); this.body.append(tb, box); this.body.style.overflow = "auto";
    if (!C.ok){ const msg = {nokey:L("Add FINNHUB_API_KEY to Streamlit secrets (free key from finnhub.io) and reload.","ضيف FINNHUB_API_KEY في Secrets بتاعة Streamlit (مفتاح مجاني من finnhub.io) وأعد تحميل الصفحة."),
        badkey:L("Finnhub returned nothing - key rejected or service unreachable. Check FINNHUB_API_KEY.","Finnhub مرجعش بيانات - المفتاح مرفوض أو الخدمة مش متاحة. راجع FINNHUB_API_KEY."), net:L("Finnhub unreachable from the server right now.","Finnhub مش متاح من السيرفر دلوقتي.")}[C.err] || L("No stock data.","مفيش بيانات أسهم.");
      box.innerHTML = "<div class='m' style='padding:10px;line-height:1.7'>"+msg+"</div>"; return; }
    const list = C.stocks.filter(x => x.ok); list.forEach(x => sel.append(Object.assign(el("option"), {value:x.sym, textContent:x.sym+(x.name ? " · "+x.name : "")}))); tb.append(sel);
    if (!list.length){ box.innerHTML = "<div class='m' style='padding:10px'>n/a</div>"; return; }
    sel.value = list.some(x => x.sym === S.tk) ? S.tk : list[0].sym;
    const n = (v, d, suf) => v == null ? "<span class='m'>n/a</span>" : v.toFixed(d == null ? 2 : d)+(suf||""), usd = v => v == null ? "<span class='m'>n/a</span>" : "$"+(v >= 1e12 ? (v/1e12).toFixed(2)+"T" : fmtV(v));
    const render = () => { const x = list.find(a => a.sym === sel.value) || list[0]; S.tk = x.sym; Ws.save(); const reads = [];
      let h = "<div style='padding:6px 8px;border-bottom:1px solid #2b3139'><b style='font-size:14px'>"+x.sym+"</b> <span class='m'>"+(x.name||"")+(x.industry ? " · "+x.industry : "")+"</span><br>"
        + "<b>"+(x.price != null ? fmtP(x.price) : "–")+"</b> <span style='color:"+(x.chg >= 0 ? G : R)+"'>"+(x.chg == null ? "" : (x.chg >= 0 ? "+" : "")+x.chg.toFixed(2)+"%")+"</span> · "+L("Mkt cap","القيمة السوقية")+" "+usd(x.mcap)+"</div>";
      const row = (k, v, nt) => "<tr><td><b>"+k+"</b></td><td>"+v+"</td><td class='m'>"+(nt||"")+"</td></tr>";
      h += "<table class='rdt'>" + row(L("P/E (TTM)","مكرر الربحية"), n(x.pe,1), x.pe != null ? (x.pe < 0 ? L("loss-making","شركة خاسرة") : x.pe > 40 ? L("expensive - growth priced in","غالي - النمو متسعّر") : x.pe < 12 ? L("cheap or low growth","رخيص أو نمو ضعيف") : "") : "")
        + row("EPS (TTM)", n(x.eps), "") + row(L("Price/Sales","السعر/المبيعات"), n(x.ps,1), "") + row(L("Price/Book","السعر/الدفترية"), n(x.pb,1), "")
        + row(L("Revenue growth YoY","نمو الإيرادات سنويا"), n(x.rev_g,1,"%"), "") + row(L("Net margin","هامش صافي الربح"), n(x.margin,1,"%"), "") + row("ROE", n(x.roe,1,"%"), "")
        + row(L("Debt / equity","الدين / الملكية"), n(x.debt_eq), x.debt_eq != null && x.debt_eq > 2 ? L("highly leveraged","مديونية عالية") : "") + row(L("Dividend yield","عائد التوزيعات"), n(x.div,2,"%"), "") + row("Beta", n(x.beta), "") + "</table>";
      if (x.hi52 && x.lo52 && x.price != null && x.hi52 > x.lo52){ const pos = (x.price-x.lo52)/(x.hi52-x.lo52)*100;
        h += "<div style='padding:6px 8px;font-size:12px'>"+L("52-week range","نطاق 52 أسبوع")+" "+fmtP(x.lo52)+" <span style='display:inline-block;width:120px;height:6px;background:#2b3139;border-radius:3px;vertical-align:middle;position:relative'><span style='position:absolute;left:"+Math.max(0,Math.min(100,pos))+"%;top:-3px;width:3px;height:12px;background:#f0b90b'></span></span> "+fmtP(x.hi52)+" ("+pos.toFixed(0)+"%)</div>";
        if (pos > 90) reads.push([Y, L("Near the 52-week high.","قريب من أعلى سعر في 52 أسبوع.")]); else if (pos < 10) reads.push([Y, L("Near the 52-week low.","قريب من أقل سعر في 52 أسبوع.")]); }
      if (x.reco){ const r = x.reco, t = r.sb+r.b+r.h+r.s+r.ss; if (t){ const bull = (r.sb+r.b)/t*100, bear = (r.s+r.ss)/t*100;
        h += "<div style='padding:6px 8px;font-size:12px;border-top:1px solid #2b3139'><b>"+L("Analyst ratings","توصيات المحللين")+"</b> ("+t+", "+(r.period||"")+")<div style='display:flex;height:8px;margin:4px 0;border-radius:4px;overflow:hidden'><span style='width:"+bull+"%;background:"+G+"'></span><span style='width:"+(100-bull-bear)+"%;background:#848e9c'></span><span style='width:"+bear+"%;background:"+R+"'></span></div>"
          + "<span style='color:"+G+"'>"+L("Buy","شراء")+" "+(r.sb+r.b)+"</span> · <span class='m'>"+L("Hold","احتفاظ")+" "+r.h+"</span> · <span style='color:"+R+"'>"+L("Sell","بيع")+" "+(r.s+r.ss)+"</span></div>";
        reads.push(bull >= 70 ? [G, L("Analyst consensus is strongly bullish (analysts are usually optimistic - weigh accordingly).","إجماع المحللين صاعد بقوة (المحللين غالبا متفائلين - خد ده في الاعتبار).")] : bear >= 30 ? [R, L("A notable share of analysts is bearish.","نسبة ملحوظة من المحللين سلبية.")] : [M, L("Analyst consensus is mixed.","إجماع المحللين متباين.")]); } }
      if (x.surprises.length){ const beats = x.surprises.filter(e => e.actual > e.est).length;
        h += "<div style='padding:6px 8px;font-size:12px;border-top:1px solid #2b3139'><b>"+L("Last earnings vs estimate","آخر أرباح مقابل التوقعات")+"</b><br>"+x.surprises.map(e => (e.period||"")+": "+n(e.actual)+" vs "+n(e.est)+" <span style='color:"+(e.actual >= e.est ? G : R)+"'>"+(e.pct != null ? (e.pct >= 0 ? "+" : "")+e.pct.toFixed(1)+"%" : "")+"</span>").join("<br>")+"</div>";
        reads.push(beats >= 3 ? [G, L("Beat EPS estimates in "+beats+" of the last "+x.surprises.length+" quarters.","تخطى توقعات الأرباح في "+beats+" من آخر "+x.surprises.length+" أرباع.")] : beats <= 1 ? [R, L("Missed EPS estimates in most recent quarters.","فوّت توقعات الأرباح في معظم الأرباع الأخيرة.")] : [M, L("Mixed earnings record.","سجل أرباح متباين.")]); }
      if (x.next_earn && x.next_earn.date) h += "<div style='padding:4px 8px;font-size:12px'>"+L("Next earnings","الأرباح القادمة")+": <b style='color:#f0b90b'>"+x.next_earn.date+"</b>"+(x.next_earn.eps_est != null ? " · "+L("EPS est.","توقع السهم")+" "+x.next_earn.eps_est.toFixed(2) : "")+" <span class='m'>("+L("high volatility around the date","تقلب عالي حوالين التاريخ")+")</span></div>";
      if (x.rev_g != null && x.rev_g > 20) reads.push([G, L("Revenue growing over 20% a year.","الإيرادات بتنمو أكتر من 20% سنويا.")]);
      if (x.debt_eq != null && x.debt_eq > 2) reads.push([R, L("High debt relative to equity.","ديون عالية مقارنة بحقوق الملكية.")]);
      if (reads.length) h += "<div style='padding:6px 8px;font-size:12px;line-height:1.7;border-top:1px solid #2b3139'><b>"+L("Reading","القراءة")+"</b><br>"+reads.map(r => "<span style='color:"+r[0]+"'>● </span>"+r[1]).join("<br>")+"</div>";
      h += "<div class='m' style='padding:4px 8px;font-size:10px'>Finnhub · "+L("Analyst price targets are a paid Finnhub feature (not shown). Context, not a signal. Cached 6h.","السعر المستهدف للمحللين ميزة مدفوعة في Finnhub (مش معروضة). سياق مش إشارة. كاش 6 ساعات.")+"</div>";
      box.innerHTML = h; };
    sel.onchange = render; render();
  }
  /* ---- risk manager: position size, lots, exposure, daily loss limit, Monte-Carlo risk of ruin ---- */
  build_risk(){
    const S = this.state, ar = lang === "ar", L = (e, a) => ar ? a : e;
    Object.assign(S, Object.assign({bal:10000, rp:1, entry:"", stop:"", tp:"", kind:"crypto", lev:100, dl:3, wl:6, dd:30, be:1}, S));
    const wrap = el("div"); wrap.style.cssText = "padding:8px;display:grid;grid-template-columns:repeat(2,1fr);gap:6px;align-content:start"; const out = el("div"); out.style.cssText = "grid-column:1/-1;font-size:12px;line-height:1.7"; const ros = el("div"); ros.style.cssText = "grid-column:1/-1;font-size:12px;border-top:1px solid #2b3139;padding-top:6px";
    const inp = (k, lab, step) => { const w = el("label"); w.style.cssText = "display:flex;flex-direction:column;font-size:10px;color:#848e9c;gap:2px"; const i = el("input"); i.type = "number"; i.step = step || "any"; i.value = S[k]; i.style.width = "100%"; i.oninput = () => { S[k] = i.value === "" ? "" : +i.value; Ws.save(); calc(); }; w.append(L(lab[0], lab[1]), i); wrap.append(w); return i; };
    const ks = el("select"); [["crypto",L("Crypto (units)","كريبتو (وحدات)")],["fx",L("Forex lot = 100k","فوركس لوت = 100 ألف")],["gold",L("Gold lot = 100 oz","ذهب لوت = 100 أوقية")]].forEach(([v,l]) => ks.append(Object.assign(el("option"), {value:v, textContent:l}))); ks.value = S.kind; ks.onchange = () => { S.kind = ks.value; Ws.save(); calc(); };
    const kw = el("label"); kw.style.cssText = "display:flex;flex-direction:column;font-size:10px;color:#848e9c;gap:2px"; kw.append(L("Instrument","الأداة"), ks);
    inp("bal", ["Balance $","الرصيد $"]); inp("rp", ["Risk % per trade","المخاطرة % للصفقة"], "0.1"); wrap.append(kw); inp("lev", ["Leverage","الرافعة"]);
    inp("entry", ["Entry","الدخول"]); inp("stop", ["Stop","الوقف"]); inp("tp", ["Target (optional)","الهدف (اختياري)"]); inp("dl", ["Daily loss limit %","حد الخسارة اليومي %"], "0.5"); inp("wl", ["Weekly loss limit %","حد الخسارة الأسبوعي %"], "0.5"); inp("be", ["Break-even after (R)","تعادل بعد (R)"], "0.1"); inp("dd", ["Ruin = drawdown %","الإفلاس = تراجع %"]);
    wrap.append(out, ros); this.body.append(wrap); this.body.style.overflow = "auto";
    const cs = () => S.kind === "fx" ? 100000 : S.kind === "gold" ? 100 : 1;
    const ruin = (p, b, risk, ddp) => { let ruined = 0; const N = 1500, T_ = 300; for (let n = 0; n < N; n++){ let eq = 1, pk = 1; for (let t = 0; t < T_; t++){ eq *= Math.random() < p ? 1 + risk*b : 1 - risk; if (eq > pk) pk = eq; if (eq <= pk*(1-ddp)){ ruined++; break; } } } return ruined/N*100; };
    const calc = () => {
      const bal = +S.bal, rp = +S.rp, e = +S.entry, sl = +S.stop, tp = +S.tp, risk$ = bal*rp/100; let h = "";
      if (bal > 0 && rp > 0 && e > 0 && sl > 0 && e !== sl){
        const d = Math.abs(e-sl), units = risk$/d, notional = units*e, lots = units/cs(), long = sl < e;
        h += "<b>"+(long ? "▲ " : "▼ ")+L("Risk","المخاطرة")+" $"+risk$.toFixed(2)+"</b> · "+L("Size","الحجم")+" <b style='color:#f0b90b'>"+(S.kind === "crypto" ? units.toPrecision(4)+" "+L("units","وحدة") : lots.toFixed(2)+" "+L("lots","لوت"))+"</b><br>";
        h += L("Notional","القيمة")+" $"+notional.toFixed(0)+" · "+L("Margin","الهامش")+" ≈ $"+(notional/Math.max(1,+S.lev)).toFixed(0)+" · "+L("Exposure","التعرض")+" "+(notional/bal*100).toFixed(0)+"%<br>";
        if (tp > 0 && ((long && tp > e) || (!long && tp < e))){ const rr = Math.abs(tp-e)/d; h += "R:R <b>1 : "+rr.toFixed(2)+"</b> · "+L("Reward","العائد")+" $"+(risk$*rr).toFixed(2)+" · "+L("break-even win rate","نسبة النجاح المطلوبة")+" "+(100/(1+rr)).toFixed(0)+"%<br>"; }
        h += "<span style='color:#848e9c'>"+L("Move stop to break-even after price travels 1R: ","حرّك الوقف للتعادل لما السعر يمشي 1R: ")+fmtP(long ? e+d : e-d)+"</span>";
      } else h = "<span style='color:#848e9c'>"+L("Enter balance, entry and stop.","ادخل الرصيد والدخول والوقف.")+"</span>";
      out.innerHTML = h;
      const st = Journal.stats(0, 0), today = new Date(); today.setHours(0,0,0,0); const tr = st.closed.filter(t => t.t1 >= today.getTime()).reduce((a,t) => a + t.r, 0), lossPct = -tr*rp, lim = +S.dl;
      const used = Math.max(0, Math.min(100, lossPct/lim*100)), p = st.closed.length >= 10 ? st.wr/100 : 0.45, bavg = st.closed.length >= 10 && st.wins ? Math.max(0.2, (st.net + st.losses)/st.wins) : 2, r = ruin(p, bavg, rp/100, +S.dd/100);
      const wk = new Date(); wk.setHours(0,0,0,0); wk.setDate(wk.getDate() - ((wk.getDay()+6)%7)); const wr_ = st.closed.filter(t => t.t1 >= wk.getTime()).reduce((a,t) => a + t.r, 0), wUsed = Math.max(0, Math.min(100, -wr_*rp/(+S.wl||1)*100));
      const opn = Journal.list.filter(t => t.status === "open"), expo = opn.length*rp, be = [];
      opn.forEach(t => { if (!t.last) return; const long = t.dir === "bullish", d = Math.abs(t.entry - t.sl), mv = (long ? t.last - t.entry : t.entry - t.last)/d; if (mv >= +S.be && (long ? t.sl < t.entry : t.sl > t.entry)) be.push(t.symbol+" "+(long?"▲":"▼")+" ("+mv.toFixed(1)+"R → SL "+fmtP(t.entry)+")"); });
      const sameDir = {}; opn.forEach(t => { const k = t.dir; sameDir[k] = (sameDir[k]||0) + 1; });
      const extra = "<div style='margin-top:6px'>"+L("Open exposure","التعرض المفتوح")+": <b style='color:"+(expo>+S.dl?"#f6465d":expo>+S.dl*0.6?"#f0b90b":"#0ecb81")+"'>"+opn.length+" "+L("trades","صفقة")+" × "+rp+"% = "+expo.toFixed(1)+"%</b>"+(Math.max(sameDir.bullish||0, sameDir.bearish||0) >= 3 ? " <span style='color:#f6465d'>⚠ "+L("3+ trades same direction (correlated)","3+ صفقات في نفس الاتجاه (مرتبطة)")+"</span>" : "")+"</div>"
        +"<div>"+L("This week","الأسبوع")+": <b style='color:"+(wr_>=0?"#0ecb81":"#f6465d")+"'>"+(wr_>=0?"+":"")+wr_.toFixed(2)+"R</b> · "+L("weekly limit used","المستخدم من الحد الأسبوعي")+" "+wUsed.toFixed(0)+"%"+(wUsed >= 100 ? " <b style='color:#f6465d'>⛔ "+L("weekly limit hit","وصلت الحد الأسبوعي")+"</b>" : "")+"</div>"
        +(be.length ? "<div style='color:#f0b90b'>🔒 "+L("Move stop to break-even: ","حرّك الوقف للتعادل: ")+esc(be.join(" · "))+"</div>" : "");
      ros.innerHTML = L("Today (journal)","النهارده (الجورنال)")+": <b style='color:"+(tr>=0?"#0ecb81":"#f6465d")+"'>"+(tr>=0?"+":"")+tr.toFixed(2)+"R</b> ≈ "+(tr*rp>=0?"+":"")+(tr*rp).toFixed(2)+"% · "+L("daily limit used","المستخدم من حد اليوم")+" "+used.toFixed(0)+"%"
        +"<div style='height:6px;background:#2b3139;border-radius:3px;margin:3px 0 6px'><div style='height:6px;width:"+used+"%;background:"+(used>=100?"#f6465d":used>60?"#f0b90b":"#0ecb81")+";border-radius:3px'></div></div>"
        +(used >= 100 ? "<b style='color:#f6465d'>⛔ "+L("Daily loss limit hit — stop trading today.","وصلت حد الخسارة اليومي — وقّف تداول النهارده.")+"</b><br>" : "")
        +L("Risk of ruin","احتمال الإفلاس")+" ("+L("hit","تراجع")+" "+S.dd+"% "+L("drawdown in 300 trades","خلال 300 صفقة")+"): <b style='color:"+(r>10?"#f6465d":r>3?"#f0b90b":"#0ecb81")+"'>"+r.toFixed(1)+"%</b><span style='color:#848e9c'> · "+L("win rate","نسبة النجاح")+" "+(p*100).toFixed(0)+"% "+L("avg win","متوسط الربح")+" "+bavg.toFixed(2)+"R "+(st.closed.length >= 10 ? L("(from journal)","(من الجورنال)") : L("(assumed, <10 journal trades)","(افتراضي، أقل من 10 صفقات)"))+"</span>"+extra;
    };
    this.riskSub = calc; Journal.subs.add(calc); this.destroy = () => Journal.subs.delete(calc); calc();
  }
  /* ---- Setup Card: the full "what's going on" for one setup (conditions that fired, plan, context). Follows the setup you click (chip / ready row), jumps to a brand-new alert, else shows the best live one ---- */
  build_setup(){
    const bar = el("div","tb"), btn = el("button", null, Lg("Show on chart","اعرضها على الشارت")), box = el("div"); box.style.cssText = "overflow:auto;height:calc(100% - 28px)"; const cs = el("select"); clsOptions().forEach(([v,l]) => cs.append(Object.assign(el("option"), {value:v, textContent:l}))); CLS_SELS.add(cs); cs.title = Lg("Market class","فئة السوق"); cs.value = FILT.cls || "All"; cs.onpointerdown = e => e.stopPropagation(); cs.onchange = () => { FILT.cls = cs.value; clsBroadcast(); store.set(LS+"_filt", FILT); Alerts.subs.forEach(f => f()); Setup.subs.forEach(f => f()); };
    this.clsSync = () => { cs.value = FILT.cls || "All"; }; bar.append(btn, cs, Voice.button(() => box.innerText)); this.body.append(bar, box);
    let cur = null, first = true, lastId = null; const key = e => e.symbol+"|"+e.direction+"|"+e.ttype;
    btn.onpointerdown = ev => ev.stopPropagation(); btn.onclick = () => { if (cur) Ws.showOnChart(Object.assign({tfc: TFC_ALL[cur.tfk] || "1H"}, cur)); };
    const draw = () => { this.clsSync && this.clsSync();
      const newest = Alerts.list.filter(a => a.card).sort((x, y) => y.t - x.t)[0]; if (newest){ if (!first && newest.id !== lastId) Setup.sel = newest.card; lastId = newest.id; } first = false;
      const live = readyList(); let e = Setup.sel ? (live.find(x => key(x) === key(Setup.sel)) || Setup.sel) : live[0]; cur = e || null;
      box.innerHTML = e ? setupHtml(e) : '<div class="m" style="padding:12px">'+esc(CFG.scanning ? T("scanning") : T("rdEmpty"))+'</div>';
    };
    draw(); Alerts.subs.add(draw); Setup.subs.add(draw); const iv = setInterval(draw, 15000); this.unwatch = () => { Alerts.subs.delete(draw); Setup.subs.delete(draw); clearInterval(iv); };
  }
  build_notes(){
    const ta = el("textarea"); ta.className = "fill"; ta.style.cssText = "width:100%;height:100%;border:0;border-radius:0;resize:none"; ta.value = this.state.txt || "";
    ta.oninput = () => { this.state.txt = ta.value; Ws.save(); }; this.body.append(ta); this.body.style.overflow = "hidden";
  }
}

/* subscriptions per type (kept outside the class for readability) */
const origResub = Panel.prototype.resub;
Panel.prototype.resub = function(){
  if (this.type === "chart") return origResub.call(this);
  this.clearSubs(); const sym = this.state.sym;
  if (this.type === "dom"){
    let book = null, prevSizes = null;
    const draw = () => {
      const tape = Hub.last["trades|"+sym];
      if (!book) return;
      if (book.error){ this.domBox.innerHTML = '<div class="'+(isRL(book.error) ? "m" : "err")+'">'+esc(offTxt(this.state.sym, book.error))+'<br><small>'+esc(String(book.error).slice(0,140))+'</small></div>'; return; }
      const gm = (this.state.gstep || {})[sym] || 0, tick = tickOfLevels(book.bids.concat(book.asks)), gs = groupStepFor(gm, tick);
      this.gSel && this.gSel.sync(gm, tick);
      const bk = gs ? Object.assign({}, book, {bids:groupBook(book.bids, gs, "bid"), asks:groupBook(book.asks, gs, "ask")}) : book;
      const res = renderDom(bk, tape && !tape.error ? tape : null, prevSizes, {lev:this.state.dlev || 12, cum:!!this.state.dcum, sym:this.state.sym, tol:gs || tick || 0, conf:Ws.flowConf(this.state.sym)}); prevSizes = res.sizes; this.domBox.innerHTML = res.html;
    };
    this.gRedraw = () => { prevSizes = null; draw(); };
    this.unsubs.push(Hub.sub("book", sym, b => { book = b; draw(); }));
    this.unsubs.push(Hub.sub("trades", sym, () => {}));
  } else if (this.type === "tape"){
    let last = null, book = null;
    this.rerender = () => {
      if (!last) return;
      if (last.error){ this.tapeBox.innerHTML = '<div class="'+(isRL(last.error) ? "m" : "err")+'">'+esc(offTxt(this.state.sym, last.error))+'<br><small>'+esc(String(last.error).slice(0,140))+'</small></div>'; return; }
      const w = this.state.win != null ? this.state.win : 300000, now = Date.now();
      const rows = (last.all || last.rows).filter(r => !w || r.t >= now - w);
      const buy = rows.filter(r=>r.side==="Buy").reduce((a,r)=>a+r.q,0), sell = rows.filter(r=>r.side==="Sell").reduce((a,r)=>a+r.q,0);
      const span = w ? w/1000 : (rows.length ? Math.max(1,(rows[rows.length-1].t-rows[0].t)/1000) : 1);
      const pace = rows.length/span, bp = buy+sell ? 100*buy/(buy+sell) : 50, d = buy-sell;
      const abr = rows.filter(r=>r.absorb), abDir = abr.length ? abr[abr.length-1].adir : "";
      this.statBox.innerHTML = '<div class="stat">'+esc(T("pace"))+' <b style="color:#eaecef">'+pace.toFixed(1)+'</b>/s · '+esc(T("delta"))+' <b class="'+(d>=0?"g":"rd")+'">'+(d>=0?"+":"-")+fmtQ(Math.abs(d))+'</b>'+(abDir ? ' · <b style="color:#b57cff" class="ab">'+Lg("ABSORB ","امتصاص ")+Lg(abDir, abDir === "sellers" ? "بائعين" : "مشترين")+'</b>' : '')+'</div><div class="bar2"><div style="width:'+bp.toFixed(0)+'%;background:#0ecb81"></div><div style="width:'+(100-bp).toFixed(0)+'%;background:#f6465d"></div></div>';
      this.tapeBox.innerHTML = renderTape(this, rows.slice().reverse().slice(0, 80));
      drawDepth(this.depthCv, book);
    };
    this.unsubs.push(Hub.sub("trades", sym, p => { last = p; this.rerender(); }));
    this.unsubs.push(Hub.sub("book", sym, b => { book = b.error ? null : b; drawDepth(this.depthCv, book); }));
  } else if (this.type === "ofm"){
    OFM.resub(this, sym);
  } else if (this.type === "limits"){
    this.lt = {prev:null, events:[], sym, abs:new Set()}; let book = null;
    this.rerender = () => { this.evBox.innerHTML = renderEvents(this, this.lt.events); };
    const run = () => { const tp = Hub.last["trades|"+sym]; if (book && !book.error) limitUpdate(this.lt, book, tp && !tp.error ? tp.rows : null); this.rerender(); };
    this.unsubs.push(Hub.sub("book", sym, b => { book = b && !b.error && b.deep && b.deep.bids && b.deep.bids.length ? Object.assign({}, b, {bids:b.deep.bids, asks:b.deep.asks}) : b; run(); }));   // same deep book (up to 400 levels per side) the order-flow heat map uses, so big orders far from the price are tracked too (before: only the nearest 50 levels)
    this.unsubs.push(Hub.sub("trades", sym, p => { if (!p.error){ absorbEvents(this.lt, p.rows); this.rerender(); } }));
  } else if (this.type === "watch"){
    this.amd = this.amd || {}; this.pv = this.pv || {}; this.flash = new Set(); let M = null;
    const favs = () => store.get(LS+"_fav", []), SYMS_ = () => SYMS;
    const L_ = (a, b) => lang === "ar" ? b : a;
    const PH = {A:["#4aa3ff", L_("Accum","تجميع")], M:["#b9a76a", L_("Manip","تلاعب")], D:["#b57cff", L_("Distrib","توزيع")]};
    const amdChip = s => { const a = this.amd[s]; if (!a || !a.phase || a.phase === "?") return '<span class="m">'+(a && a.phase ? "–" : "…")+'</span>'; if (a.phase === "-") return '<span class="m">–</span>'; const [c, n] = PH[a.phase];
      return '<span class="amd" style="color:'+c+';border-color:'+c+'" title="'+esc(L_("Phase on the "+(this.state.wtf||"1H")+" chart (ICT AMD / Power of 3)","المرحلة على فريم "+(this.state.wtf||"1H")+" (ICT AMD)"))+'">'+n+(a.dir ? (a.dir === "up" ? " ▲" : " ▼") : "")+'</span>'; };
    const amdLoad = async list => { const bar = this.state.wtf || "1H"; let chg = false;
      if (this._amdRun || Date.now() < (this._amdNext || 0)) return; this._amdRun = true; let nReq = 0;   // ONE pass at a time, ~3 requests/s, at most 12 symbols per pass: 40 back-to-back candle calls from 4 charts + this list hit OKX's 429
      try { for (const s of list.slice(0, 40)){ const c = this.amd[s]; if (c && (c.busy || (c.bar === bar && Date.now() - c.t < 300000))) continue; if (nReq++ >= 12) break; if (nReq > 1) await new Promise(z => setTimeout(z, 330)); this.amd[s] = Object.assign({}, c && c.bar === bar && c.phase ? c : {}, {busy:true, bar, t:Date.now()});   // keep the last phase visible while refreshing (no "…" blink)
        try { const d = (await okx("/market/candles?instId="+encodeURIComponent(s)+"&bar="+bar+"&limit=60")).map(r => ({o:+r[1], h:+r[2], l:+r[3], c:+r[4]})).reverse(); this.amd[s] = Object.assign(amdPhase(d), {bar, t:Date.now()}); }
        catch(e){ const o = c && c.bar === bar && c.phase && c.phase !== "?" ? c : {phase:"?"}; this.amd[s] = Object.assign({}, o, {bar, t:Date.now() - 100000, busy:false, err:String(e && e.message || e)}); }
        if (!c || c.phase !== this.amd[s].phase || c.dir !== this.amd[s].dir) chg = true;
        if (/rate limit|429|Too Many/i.test(String(this.amd[s].err || ""))) break; } } finally { this._amdRun = false; this._amdNext = Date.now() + (nReq >= 12 ? 4000 : 0); }
      if (chg) this.wDraw(); };
    this.wDraw = () => {
      if (!M) return; if (M.error){ this.wBox.innerHTML = '<div class="err">'+esc(T("offline"))+'<br><small>'+esc(String(M.error).slice(0,140))+'</small></div>'; return; }
      const F = favs(), UC = (this.state.u || {}).cat || (Object.keys(YF).length ? "__mine" : "All"), only = UC === "__fav";   // Yahoo markets (forex / EGX / ...) are not in OKX's universe: show "My list" by default
      const groups = UC === "__fav" ? [[L_("★ Favorites","★ المفضلة"), F]] : UC === "__mine" ? [[L_("My list","قائمتي"), SYMS.slice()]] : [[(this.uTitle || L_("Market","السوق")), this.uSyms || []]];
      const shown = []; let h = '<table class="wt"><tr><th></th><th>'+esc(T("symbol"))+'</th><th class="r">'+esc(T("last"))+'</th><th class="r">'+esc(T("chg"))+'</th><th>AMD '+esc(this.state.wtf || "1H")+'</th></tr>';
      groups.forEach(([title, list]) => { if (!list.length) return; h += '<tr class="wh"><td colspan="5">'+esc(title)+'</td></tr>';
        list.forEach(s => { shown.push(s); const x = M[s], p = this.pv[s] || {}, fav = F.includes(s), fl = this.flash.has(s) ? (p.dir > 0 ? " fu" : " fd") : "", col = p.dir > 0 ? "g" : p.dir < 0 ? "rd" : "";
          const st = '<td class="stc"><span class="st'+(fav ? " on" : "")+'" data-st="'+esc(s)+'">'+(fav ? "★" : "☆")+'</span></td>';
          const nm = symIcon(s, 13) + (/^HL:/.test(s) ? esc(hlLabel(s))+' <span class="hlb" title="'+esc(L_("Hyperliquid perpetual "+hlCoin(s)+" - live, 24/7, can differ slightly from spot / futures", "عقد دائم على Hyperliquid "+hlCoin(s)+" - لحظي 24/7، ممكن يختلف شوية عن السبوت / الفيوتشرز"))+'">HL</span>'
            : FH_MAP[s] ? esc(FH_MAP[s].label)+' <span class="m" title="Finnhub / OANDA CFD, live">●</span>'
            : /^Y:/.test(s) ? esc(s.slice(2).replace(/^([A-Z]{3})([A-Z]{3})=X$/, "$1/$2").replace(/=F$/, " fut"))+' <span class="m" title="'+esc(L_("Yahoo Finance, delayed - refreshed when the page reloads","Yahoo Finance متأخر - بيتحدث مع تحديث الصفحة"))+'">Y</span>' : esc(s));
          if (!x && FH_MAP[s]){ const cl = fxClosed(); h += '<tr class="wr" data-s="'+esc(s)+'">'+st+'<td>'+nm+'</td><td class="r m" title="'+esc(cl ? L_("Forex / CFD market closed (Fri 17:00 - Sun 17:00 New York); Finnhub sends no ticks until it reopens", "سوق الفوركس قافل (الجمعة 5 م - الأحد 5 م بتوقيت نيويورك)؛ Finnhub مش بيبعت أسعار لحد ما يفتح") : L_("waiting for the first tick (or this symbol is not on Finnhub's free plan)", "مستني أول سعر (أو الرمز ده مش في خطة Finnhub المجانية)"))+'">'+esc(cl ? L_("closed", "قافل") : "…")+'</td><td class="r m">–</td><td>'+amdChip(s)+'</td></tr>'; return; }
          if (!x){ h += '<tr class="wr" data-s="'+esc(s)+'">'+st+'<td>'+nm+'</td><td class="r m">…</td><td class="r m">–</td><td>'+amdChip(s)+'</td></tr>'; return; }
          const ch = x.open ? (x.last-x.open)/x.open*100 : 0, chC = x.open ? '<td class="r '+(ch>=0?"g":"rd")+'">'+(ch>=0?"▲ +":"▼ ")+ch.toFixed(2)+'%</td>' : '<td class="r m" title="'+esc(L_("no reference close for this feed","مفيش سعر إغلاق مرجعي للمصدر ده"))+'">–</td>';
          h += '<tr class="wr" data-s="'+esc(s)+'">'+st+'<td>'+nm+'</td><td class="r '+col+fl+'">'+fmtP(x.last)+(x.stale ? ' <span class="m" title="'+esc(L_("Delayed: last good price (OKX did not answer)","متأخر: آخر سعر سليم (OKX ما ردّش)"))+'">⏱</span>' : "")+(p.dir ? ' <span class="ar">'+(p.dir > 0 ? "▲" : "▼")+'</span>' : "")+'</td>'+chC+'<td>'+amdChip(s)+'</td></tr>'; }); });
      if (!shown.length) h += '<tr><td colspan="5" class="m">'+esc(only ? L_("No favorites yet — tap ☆ next to a symbol","لا توجد مفضلة — اضغط ☆ بجانب أي رمز") : T("uniNone"))+'</td></tr>';
      const full = h+'</table>', sig = (this.state.wtf || "") + "|" + (this.state.u || {}).cat + "|" + shown.map(z => z + (F.includes(z) ? "*" : "")).join(",") + "|" + lang;
      if (full !== this._wbHtml){ this._wbHtml = full; const old = this.wBox.querySelector("table.wt");
        if (old && sig === this._wbSig){   // same rows: patch only the price / change / AMD cells (the symbol cell holds the coin icon: rebuilding it reloads the image = blink)
          const nw = document.createElement("div"); nw.innerHTML = full; const A = old.rows, B = nw.querySelector("table").rows;
          if (A.length === B.length) for (let i = 0; i < A.length; i++){ if (A[i].cells.length !== B[i].cells.length || A[i].cells.length < 5){ if (A[i].innerHTML !== B[i].innerHTML) A[i].innerHTML = B[i].innerHTML; continue; }
            for (let k = 2; k < 5; k++){ const a = A[i].cells[k], b = B[i].cells[k]; if (a.innerHTML !== b.innerHTML) a.innerHTML = b.innerHTML; if (a.className !== b.className) a.className = b.className; } }
          else this.wBox.innerHTML = full; }
        else this.wBox.innerHTML = full; this._wbSig = sig; }
      this.flash.clear();
      this.wBox.querySelectorAll(".wr").forEach(r => r.onclick = () => { const f = FH_MAP[r.dataset.s]; if (!f) return Ws.broadcast(this, r.dataset.s); if (f.y && YF[f.y]) Ws.broadcast(this, f.y); else r.title = L_("Chart: pick this market's Asset class in the Chart Scanner tab first (Yahoo candles)","الشارت: اختار فئة السوق ده من Asset class في تاب Chart Scanner الأول"); });
      this.wBox.querySelectorAll(".st").forEach(b => b.onclick = ev => { ev.stopPropagation(); const k = b.dataset.st, f = favs(), i = f.indexOf(k); i < 0 ? f.push(k) : f.splice(i, 1); store.set(LS+"_fav", f); this.wDraw(); });
      Hub.extra = new Set(); Ws.panels.forEach(p => { if (p.type === "watch") favs().concat(p.uSyms || []).forEach(z => Hub.extra.add(z)); });
      amdLoad(shown);
    };
    this.wRender = m => { if (!m) return; M = m; this.fhUpd && this.fhUpd(); if (!m.error){ const seen = new Set(SYMS.concat(favs(), this.uSyms || []));
        seen.forEach(s => { const x = m[s]; if (!x) return; const p = this.pv[s] = this.pv[s] || {last:x.last, dir:0}; if (x.last !== p.last){ p.dir = x.last > p.last ? 1 : -1; p.last = x.last; this.flash.add(s); } }); }
      this.wDrawSoon(); };
    this.wDrawSoon = () => { if (this._wdPend) return; this._wdPend = true; setTimeout(() => { this._wdPend = false; this.wDraw(); }, 1000); };   // at most one table rebuild per second
    this.unsubs.push(Hub.sub("tickers", "all", m => this.wRender(m)));
  }
};

