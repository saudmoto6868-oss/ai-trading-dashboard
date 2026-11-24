/* ---- RADAR MODE (owner 2026-11-21): the Radar page's chart grid is this app with CFG.solo === "radar" - one of OUR chart widgets per
   symbol (own indicators menu, tools, timeframe), laid out as a grid, instead of the old lightweight-charts cards.
   CFG.radar = {cols, h, items:[{sym, tf, tag, info, pts:[{label, dir, kind, ind, lines}]}]} comes from main.py (render_chart_scanner).
   Under every chart: numbered points = what the scanner found on it. A click switches it on the chart: kind "ind" = one item of the
   indicators menu (Elliott, harmonic, MSB ...), "lines" = the chart pattern's own lines (modules/patterns.py), "sr" = the S/R button,
   "info" = shown only. The first point opens by itself. ▾ opens the explanation under the chart, over the chart below it only.
   Saved layout: LS = "ai_ws_radar" (never the Workspace one); a chart keeps its indicator choices while its symbol stays in the grid.
   Nothing here places an order. ---- */
const RadarMode = {
  items(){ return (CFG.radar && Array.isArray(CFG.radar.items)) ? CFG.radar.items : []; },
  tf(t){ const m = String(t || "1h").match(/^(\d+)(m|h|d|w|mo)$/); if (!m) return "1H"; return m[2] === "m" ? m[1] + "m" : m[2] === "mo" ? "1M" : m[1] + m[2].toUpperCase(); },
  layout(saved){
    const R = CFG.radar || {}, cols = Math.max(1, Math.min(12, +R.cols || 4)), H = Math.max(200, +R.h || 340), W = Math.max(320, Ws.el.clientWidth || innerWidth), w = Math.floor(W / cols);
    const old = {}; (saved || []).forEach(p => { if (p && p.type === "chart" && p.state && p.state.sym) old[p.state.sym] = p.state; });
    return this.items().map((it, i) => ["chart", {x:(i % cols)*w, y:this.BAR + Math.floor(i / cols)*H, w:w - 2, h:H - 2},
      Object.assign({group:0, ema:{9:true, 21:true, 50:false}}, old[it.sym] || {}, {sym:it.sym, tf:this.tf(it.tf), min:false, lock2:true})]);
  },
  // the frame's width is not known yet while the page boots: lay the grid out again once loaded and on every resize (Streamlit resizes the iframe)
  fit(){ const R = CFG.radar || {}, cols = Math.max(1, Math.min(12, +R.cols || 4)), H = Math.max(200, +R.h || 340), W = Math.max(320, document.documentElement.clientWidth || innerWidth), w = Math.floor(W / cols);
    Ws.panels.filter(p => p.type === "chart").forEach((p, i) => { p.rect = {x:(i % cols)*w, y:this.BAR + Math.floor(i / cols)*H, w:w - 2, h:H - 2}; p.apply(); try { p.chart.resize(); } catch(e){} });
    document.querySelectorAll(".rdinfo").forEach(x => x.remove()); },
  BAR: 30,   // height of the "indicators on ALL charts" bar above the grid
  allKey(){ return LS + "_all"; },
  allGet(){ const v = store.get(this.allKey(), {}); return v && typeof v === "object" ? v : {}; },
  // one indicator on / off on every chart (owner 2026-11-21: "pick an indicator once, it goes on all the charts"); remembered for this grid
  cleanKey(){ return LS + "_clean"; },
  unclean(){ if (!store.get(this.cleanKey(), false)) return; store.set(this.cleanKey(), false); this.charts().forEach(p => { p.chart.sidesOff = false; p.chart.draw(); }); },   // set by "Clear ALL": the charts stay bare (point 1 does not open by itself) until something is switched on again
  setAll(id, on){ const m = this.allGet(); m[id] = !!on; store.set(this.allKey(), m); if (on) this.unclean();
    Ws.panels.forEach(p => { const it = (p.indItems || []).find(x => x.id === id); if (!it || !p.chart) return; try { it.set(!!on); p.state.mode = ""; if (p.indSave) p.indSave(); p.chart.draw(); } catch(e){} });
    Ws.save(); },
  // owner 2026-11-21: one button = every chart bare: all indicators, tables, the order-flow column, VWAP / signals / flow / KZ, S/R and the points' lines off
  clearAll(){ const m = {};
    Ws.panels.forEach(p => { const ch = p.chart; if (!ch) return;
      (p.indItems || []).forEach(it => { if (it.id === "zlog" || typeof it.set !== "function") return; m[it.id] = false; try { if (it.get()) it.set(false); } catch(e){} });
      if (ch.ema){ Object.keys(ch.ema).forEach(k => { ch.ema[k] = false; }); p.state.ema = Object.assign({}, ch.ema); }
      ch.showSig = false; p.state.sig = false; ch.flowOn = false; p.state.flow = false; ch.kz = false; p.state.kz = false;
      ch.draws = ch.draws.filter(d => !d._rd); ch.sidesOff = true; p.state.mode = ""; p.state.sr = false; if (p.syncSR) p.syncSR();
      try { if (p.indSave) p.indSave(); } catch(e){} ch.draw(); });
    store.set(this.allKey(), m); store.set(this.cleanKey(), true);
    document.querySelectorAll(".rdpt.on").forEach(b => b.classList.remove("on")); Ws.save(); },
  charts(){ return Ws.panels.filter(p => p.type === "chart" && p.chart); },
  // the chart toolbar's own options, run on every chart at once (the symbol stays per chart)
  actions(bar){
    const B = (txt, tip, fn, cls) => { const b = el("button", "rdact" + (cls ? " " + cls : ""), txt); b.title = tip; b.onclick = e => { e.stopPropagation(); fn(b); }; bar.append(b); return b; };
    B("⏻ " + esc(Lg("Clear ALL", "امسح الكل")), Lg("Remove every indicator, table, order-flow column and S/R from ALL charts (drawings you made stay)", "شيل كل المؤشرات والجداول وعمود الأوردر فلو والدعم/المقاومة من كل الشارتات (رسوماتك بتفضل)"),
      () => { this.clearAll(); if (this._chips) this._chips(); }, "rdclear");
    const tf = el("select", "rdact"); tf.title = Lg("Timeframe of ALL charts", "فريم كل الشارتات");
    tf.append(Object.assign(el("option"), {value:"", textContent:"TF ▾"})); TFS.forEach(([v, l]) => tf.append(Object.assign(el("option"), {value:v, textContent:l})));
    tf.onchange = () => { const v = tf.value; if (v) this.charts().forEach(p => { try { p.setTf(v); } catch(e){} }); tf.value = ""; }; bar.append(tf);
    B("⟳", Lg("Reload the data of ALL charts (keeps each view)", "إعادة تحميل بيانات كل الشارتات (مع الحفاظ على العرض)"), () => this.charts().forEach(p => p.tbBtns && p.tbBtns.refresh.click()));
    B(esc(T("fit")), Lg("Fit ALL charts: latest candle back to the middle", "ملاءمة كل الشارتات: آخر شمعة في النص"), () => this.charts().forEach(p => { try { p.chart.centerNow(); } catch(e){} }));
    const rf = el("select", "rdact"); rf.title = T("rf") + " · " + Lg("ALL charts", "كل الشارتات");
    rf.append(Object.assign(el("option"), {value:"", textContent:"↻ ▾"})); [["1s",1000],["2s",2000],["5s",5000]].forEach(([l, v]) => rf.append(Object.assign(el("option"), {value:v, textContent:"↻ " + l})));
    rf.onchange = () => { const v = rf.value; if (v) this.charts().forEach(p => { const s = p.tbBtns && p.tbBtns.rf; if (s){ s.value = v; s.dispatchEvent(new Event("change")); } }); rf.value = ""; }; bar.append(rf);
    B("S/R", Lg("Daily + weekly support / resistance on ALL charts (click again = off)", "دعم ومقاومة يومي + أسبوعي على كل الشارتات (ضغطة تانية = إيقاف)"), b => {
      const on = !this.charts().some(p => p.chart.srOn); this.charts().forEach(p => { p.state.sr = on; if (p.syncSR) p.syncSR(); }); if (on) this.unclean(); b.classList.toggle("on", on); Ws.save(); });
    B("✎✕", Lg("Hide / show the drawings on ALL charts (nothing is deleted)", "إخفاء / إظهار الرسومات على كل الشارتات (مفيش حاجة بتتمسح)"), b => {
      const hide = this.charts().some(p => p.chart.drawingsVisible !== false);
      this.charts().forEach(p => { if ((p.chart.drawingsVisible !== false) === hide && p.tbBtns) p.tbBtns.drw.click(); }); b.classList.toggle("on", hide); });
    const xh = B("✚", Lg("Crosshair sync on ALL charts", "تزامن الكروس على كل الشارتات"), () => xhSet(!XHS.on)); XH_BTNS.add(xh); xh.classList.toggle("on", XHS.on);
  },
  applyAll(p){ const m = this.allGet(); Object.keys(m).forEach(id => { const it = (p.indItems || []).find(x => x.id === id); if (it && it.get() !== m[id]) try { it.set(m[id]); } catch(e){} });
    if (Object.keys(m).length && p.indSave) p.indSave(); },
  allBar(){
    const bar = el("div", "rdall"), btn = el("button", "rdallb", "ƒx " + esc(Lg("Indicators on ALL charts", "مؤشرات على كل الشارتات")) + " ▾"), chips = el("span", "rdchips");
    const pop = el("div", "rdpop"); pop.style.display = "none";
    const ref = () => (Ws.panels.find(p => p.indItems && p.indItems.length) || {}).indItems || [];
    const drawChips = () => { chips.innerHTML = ""; const m = this.allGet(), items = ref();
      Object.keys(m).filter(id => m[id]).forEach(id => { const it = items.find(x => x.id === id); const c = el("button", "rdchip", esc((it ? it.label : id).slice(0, 34)) + " ✕");
        c.title = Lg("Remove from all charts", "شيله من كل الشارتات"); c.onclick = () => { this.setAll(id, false); drawChips(); render(); }; chips.append(c); }); };
    const render = () => { pop.innerHTML = ""; const items = ref().filter(it => it.id !== "ma" && it.id !== "zlog" && typeof it.set === "function");
      const q = el("input"); q.placeholder = Lg("Search indicators…", "ابحث عن مؤشر…"); q.className = "rdq"; pop.append(q);
      const list = el("div", "rdlist"); pop.append(list); const m = this.allGet();
      const fill = () => { list.innerHTML = ""; const s = q.value.trim().toLowerCase(); let g0 = null;
        items.filter(it => !s || String(it.label).toLowerCase().includes(s)).forEach(it => { const g = it.grp ? Lg(it.grp.en, it.grp.ar) : "";
          if (g && g !== g0){ list.append(el("div", "rdgh", esc(g))); g0 = g; }
          const row = el("label", "rdrow"), cb = el("input"); cb.type = "checkbox"; cb.checked = !!m[it.id];
          cb.onchange = () => { this.setAll(it.id, cb.checked); m[it.id] = cb.checked; drawChips(); }; row.append(cb, el("span", null, esc(it.label))); if (it.tip) row.title = it.tip; list.append(row); }); };
      q.oninput = fill; fill();
      const clr = el("button", "rdclr", esc(Lg("Turn all of these off on every chart", "اقفل الكل من كل الشارتات")));
      clr.onclick = () => { Object.keys(this.allGet()).forEach(id => this.setAll(id, false)); store.set(this.allKey(), {}); drawChips(); render(); }; pop.append(clr); };
    btn.onclick = e => { e.stopPropagation(); if (pop.style.display !== "none"){ pop.style.display = "none"; return; } render(); pop.style.display = "block"; };
    document.addEventListener("pointerdown", e => { if (pop.style.display !== "none" && !pop.contains(e.target) && e.target !== btn) pop.style.display = "none"; }, true);
    this._chips = drawChips; bar.append(btn); this.actions(bar); bar.append(chips, pop); Ws.el.append(bar); setTimeout(drawChips, 1500);
  },
  isOn(p, pt){
    if (pt.kind === "ind"){ const it = (p.indItems || []).find(x => x.id === pt.ind); return !!(it && it.get()); }
    if (pt.kind === "sr") return !!(p.chart && p.chart.srOn);
    if (pt.kind === "lines" || pt.kind === "levels") return !!(p.chart && p.chart.draws.some(d => d._rd === pt.label));
    return false;
  },
  toggle(p, pt, on){
    const ch = p.chart; if (!ch) return;
    if (pt.kind === "ind"){ const it = (p.indItems || []).find(x => x.id === pt.ind); if (!it) return; it.set(on); if (p.indSave) p.indSave(); else Ws.save(); }
    else if (pt.kind === "sr"){ p.state.sr = on; Ws.save(); if (p.syncSR) p.syncSR(); }
    else if (pt.kind === "levels"){   // plan levels (Spot: buy 1 / buy 2 / target / invalidation): horizontal lines with their name
      ch.draws = ch.draws.filter(d => d._rd !== pt.label);
      if (on) (pt.levels || []).forEach((l, i) => { if (l && isFinite(l.p) && l.p > 0) ch.draws.push({id:"rd" + Date.now() + i + Math.random(), _rd:pt.label, type:"hline", color:l.color || "#f0b90b", w:1.4, txt:l.label || "", pts:[{t:Date.now(), p:+l.p}]}); });
    }
    else if (pt.kind === "lines"){
      ch.draws = ch.draws.filter(d => d._rd !== pt.label);
      if (on) (pt.lines || []).forEach((l, i) => { if (Array.isArray(l) && l.length === 4 && l.every(isFinite))
        ch.draws.push({id:"rd" + Date.now() + i + Math.random(), _rd:pt.label, type:"trend", color:pt.dir === "short" ? "#f6465d" : pt.dir === "long" ? "#0ecb81" : "#f0b90b", w:1.6, pts:[{t:+l[0], p:+l[1]}, {t:+l[2], p:+l[3]}]}); });
    }
    ch.draw();
  },
  decorate(p){
    const it = this.items().find(x => x.sym === p.state.sym); if (!it) return;
    const ft = el("div", "rdft"), pts = (it.pts || []).slice(0, 12);
    if (it.tag) ft.append(el("span", "rdtag", esc(it.tag)));
    const btns = pts.map((pt, i) => { const b = el("button", "rdpt " + (pt.dir || ""), (i + 1) + " · " + esc(pt.label)); b.title = pt.tip || pt.label;
      if (pt.kind === "info"){ b.disabled = true; b.classList.add("info"); }
      b.onclick = () => { const on = !b.classList.contains("on"); if (on) this.unclean(); this.toggle(p, pt, on); b.classList.toggle("on", on); }; ft.append(b); return b; });
    const more = el("button", "rdmore", "▾"); more.title = Lg("Explanation of this chart (opens under it, over the chart below)", "شرح الشارت ده (بيفتح تحته، فوق الشارت اللي تحته بس)"); ft.append(more);
    p.body.append(ft);
    let box = null; const close = () => { if (box){ box.remove(); box = null; more.textContent = "▾"; } };
    more.onclick = () => { if (box){ close(); return; }
      box = el("div", "rdinfo", it.info || esc(Lg("No explanation for this chart yet.", "مفيش شرح للشارت ده لسه.")));
      const r = p.rect; box.style.cssText = "left:" + r.x + "px;top:" + (r.y + r.h) + "px;width:" + r.w + "px;max-height:" + Math.max(160, r.h - 4) + "px";
      box.style.zIndex = ++Ws.z + 1000; Ws.el.append(box); more.textContent = "▴"; };
    // the chart needs a moment to load its candles (and the indicators menu); then mark what is on and open the first point
    let tries = 0; const sync = () => { if (!p.chart || !p.chart.data.length){ if (++tries < 40) setTimeout(sync, 500); return; }
      this.applyAll(p); if (store.get(this.cleanKey(), false)){ p.chart.sidesOff = true; p.chart.draw(); }
      btns.forEach((b, i) => b.classList.toggle("on", this.isOn(p, pts[i])));
      const first = store.get(this.cleanKey(), false) ? -1 : pts.findIndex(x => x.kind !== "info"); if (first >= 0 && !btns[first].classList.contains("on")){ this.toggle(p, pts[first], true); btns[first].classList.add("on"); } };   // the main find (point 1) always opens
    setTimeout(sync, 300);
  },
};
