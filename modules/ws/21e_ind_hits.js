/* IND-HITS-BEGIN "what is this?" on the chart (owner 2026-11-24): hold the mouse still on anything drawn for IH_DWELL ms -> a small card names the indicator that drew it
   (+ one-line help + where a trade plan comes from); a click on the card, or a double-click on the thing itself, opens the Indicators window on that row and flashes it.
   Cost: zero while you work. Only when the mouse rests (or on a double-click) the chart paints ONCE with its drawing calls logged per indicator, then hit-tests that log. */
const IH_DWELL = 3000;
const IH_MAP = {   // painter -> Indicators-menu id (or a pseudo id from IH_EXTRA). A painter called inside another keeps the outer id (paintPending inside paintHarm = harm)
  paintKZ:"kz", paintKZS:"kzs", paintGann:"gann", paintGannOffset:"gann", paintGann144:"gann", paintLiq:"liqm", paintAstro:"astro", paintSyncMarks:"sync", paintSyncCard:"ofs",
  paintBB:"bbshow", paintDon:"don", paintMsb:"msb", paintS26:"s26", paintMt5:"mt5", paintHtfCandles:"dcandle", paintLv:"lv", paintLL:"ll", paintX77:"x77", paintSmt:"smt",
  paintHarm:"harm", paintVp:"vp", paintBvd:"bvd", paintEWauto:"ew", paintEWforming:"ew", paintEWdiag:"ew", paintEWfib:"ew", paintProjection:"ew", paintEW:"sig",
  paintFp:ch => ch.fpOn ? "fp" : "delta", paintDots:"dot", paintMk:"mk", paintBal:"dom", paintSetupBox:"sig", paintSigs:"sig", paintCol:"dcol", paintHeatCol:"dcol",
  paintGauge:"ofg", paintRead:"read", paintDiv:"div", paintJournal:"journal", paintDraws:"draw", paintAlarms:"alarm", paintPlus:"alarm", paintSR:"sr", paintSides:"sides"
};
const IH_EXTRA = {   // things that are not a row of the Indicators window
  journal:["Journal trade: a trade the journal is tracking for this symbol (setups from the server scanner / alerts that passed the journal filter, or your own). Always shown; closed ones are faded. Full list: Journal panel.",
           "صفقة جورنال: صفقة الجورنال بيتابعها للرمز ده (سيتابات السكانر / التنبيهات اللي عدّت فلتر الجورنال، أو صفقاتك). بتظهر دايمًا؛ المقفولة باهتة. القايمة كاملة: لوحة الجورنال."],
  draw:["Your own drawing (drawing tools). Double-click it to edit.", "رسمة من رسوماتك (أدوات الرسم). دبل كليك عليها لتعديلها."],
  alarm:["Price alert line (⏰). Right-click the chart → Alerts to manage.", "خط تنبيه سعر (⏰). كليك يمين على الشارت ← التنبيهات للإدارة."],
  sr:["Support / resistance lines: the S/R button in the chart toolbar.", "خطوط الدعم / المقاومة: زرار S/R في شريط الشارت."],
  sides:["Gann / Elliott side marks.", "علامات جانبية لجان / إليوت."],
  volume:["Volume bars (VOL).", "أعمدة الفوليوم (VOL)."]
};
let IH_WRAPPED = false;
const ihWrap = () => {   // wrap the painters once (lazily: some are added by later parts, e.g. paintX77)
  if (IH_WRAPPED) return; IH_WRAPPED = true; const P = CandleChart.prototype;
  Object.keys(IH_MAP).forEach(fn => { const f = P[fn]; if (typeof f !== "function" || f._ih) return; const id = IH_MAP[fn];
    const w = function(...a){ if (!this._ihRec || this._ihId) return f.apply(this, a); this._ihId = typeof id === "function" ? id(this) : id; try { return f.apply(this, a); } finally { this._ihId = null; } };
    w._ih = true; P[fn] = w; });
};
/* pure geometry (tested in node: tests/test_ind_hits.py) */
const ihDist = (px, py, x1, y1, x2, y2) => { const dx = x2 - x1, dy = y2 - y1, L = dx*dx + dy*dy; let t = L ? ((px - x1)*dx + (py - y1)*dy)/L : 0; t = Math.max(0, Math.min(1, t)); return Math.hypot(px - (x1 + t*dx), py - (y1 + t*dy)); };
const ihPick = (log, x, y) => {   // log rows: [id, kind, a, b, c, d] -> ids under (x, y), best first (text, dots, lines, then boxes small to big), max 4
  const hit = [];
  log.forEach(r => { const [id, k, a, b, c, d] = r; let s = null;
    if (k === "t" && x >= a - 2 && x <= a + c + 2 && y >= b - 2 && y <= b + d + 2) s = 0;
    else if (k === "o" && Math.hypot(x - a, y - b) <= c + 3) s = 1 + c/100;
    else if (k === "l" && ihDist(x, y, a, b, c, d) <= 4) s = 2;
    else if (k === "r" && x >= a - 1 && x <= a + c + 1 && y >= b - 1 && y <= b + d + 1) s = 3 + Math.log10(1 + c*d);
    if (s != null) hit.push([s, id]); });
  hit.sort((p, q) => p[0] - q[0]); const out = []; hit.forEach(([, id]) => { if (!out.includes(id)) out.push(id); }); return out.slice(0, 4);
};
Object.assign(CandleChart.prototype, {
  ihRecord(){   // one synchronous paint with fillText / rects / paths / arcs logged under the painter's id, in chart units (same as this.mouse)
    ihWrap(); const c = this.ctx, CP = CanvasRenderingContext2D.prototype, log = [], base = c.getTransform().inverse(); let last = {};
    const tp = (x, y) => { const p = base.multiply(c.getTransform()).transformPoint(new DOMPoint(x, y)); return [p.x, p.y]; };
    const tr = (x, y, w, h) => { const [a, b] = tp(x, y), [e, f] = tp(x + w, y + h); return [Math.min(a, e), Math.min(b, f), Math.abs(e - a), Math.abs(f - b)]; };
    const on = () => this._ihId;
    const P = {
      fillText(s, x, y){ if (on()){ const w = c.measureText(String(s)).width, fs = +((/(\d+(?:\.\d+)?)px/.exec(c.font) || [0, 11])[1]), al = c.textAlign, bl = c.textBaseline;
        const x0 = al === "center" ? x - w/2 : (al === "right" || al === "end") ? x - w : x, y0 = bl === "middle" ? y - fs/2 : (bl === "top" || bl === "hanging") ? y : y - fs*.8;
        log.push([on(), "t", ...tr(x0, y0, w, fs)]); } return CP.fillText.apply(c, arguments); },
      fillRect(x, y, w, h){ if (on()) log.push([on(), "r", ...tr(x, y, w, h)]); return CP.fillRect.apply(c, arguments); },
      strokeRect(x, y, w, h){ if (on()) log.push([on(), "r", ...tr(x, y, w, h)]); return CP.strokeRect.apply(c, arguments); },
      rect(x, y, w, h){ if (on() && !(x === 0 && y === 0)) log.push([on(), "r", ...tr(x, y, w, h)]); return CP.rect.apply(c, arguments); },   // (0,0,PR,PB) = a clip, not a drawing
      moveTo(x, y){ if (on()) last[on()] = tp(x, y); return CP.moveTo.apply(c, arguments); },
      lineTo(x, y){ const id = on(); if (id){ const q = tp(x, y), p = last[id]; if (p) log.push([id, "l", p[0], p[1], q[0], q[1]]); last[id] = q; } return CP.lineTo.apply(c, arguments); },
      arc(x, y, r){ if (on()){ const [a, b] = tp(x, y); log.push([on(), "o", a, b, r]); } return CP.arc.apply(c, arguments); }
    };
    Object.assign(c, P); this._ihRec = true; this._ihId = null;
    try { this.paint(); } catch(e){ console.warn("ind-hits", e); }
    finally { this._ihRec = false; this._ihId = null; Object.keys(P).forEach(k => delete c[k]); }
    return log;
  },
  ihAt(x, y){   // ids under a chart point: indicator panes below the price chart by pane, the rest from one logged paint
    if (y > this.PB){ const p = (this._panes || []).find(q => y >= q.y0 && y <= q.y0 + q.h); return p ? [p.k] : []; }
    if (this.drawingsVisible && this.draws && this.draws.some(d => !d.hidden && this.hit(d, x, y))) return ["draw"];
    return ihPick(this.ihRecord(), x, y);
  },
  ihInfo(id){   // {name, help, src, menu}
    const it = this.indInfo ? this.indInfo(id) : null, ex = IH_EXTRA[id];
    let src = "";
    if (id === "sig" || id === "mk"){ const ov = this.overlay; src = ov ? Lg("Source: server scanner plan for ", "المصدر: خطة سكانر السيرفر لـ ")+(this.sym || "")+" · "+(ov.tf || this.tf)+(ov.score != null ? " · "+Lg("score ","سكور ")+ov.score+(ov.max ? "/"+ov.max : "") : "")+(ov.ttype ? " · "+ov.ttype : "")+((ov.tags || []).length ? "\n"+Lg("Why: ","ليه: ")+ov.tags.slice(0, 8).join(" · ") : "") : Lg("Source: server scanner (no plan for this timeframe right now)", "المصدر: سكانر السيرفر (مفيش خطة للفريم ده دلوقتي)"); }
    if (id === "harm") src = Lg("Source: the harmonic pattern's own plan (entry at D, targets from the AD leg) - not the scanner", "المصدر: خطة نموذج الهارمونيك نفسه (الدخول عند D والأهداف من ضلع AD) - مش السكانر");
    const rec = this.ihRecord_(id); if (rec) src = (src ? src + "\n" : "") + rec;
    return {name: it ? it.label : id, help: (typeof indHelp === "function" && indHelp(id)) || (it && it.tip) || (ex ? ex[lang === "ar" ? 1 : 0] : ""), src, menu: !!it, on: it ? it.on : null};
  },
  ihRecord_(id){   // 2026-11-27: the strategy's own track record from the signal ledger (server, CFG.ledger), so the card says how this source has done
    const SRC = {sig:"scanner", mk:"scanner", kzs:"kzs", s26:"2.6", gann:"gann", harm:"harmonic"}, k = SRC[id];
    if (!k || typeof CFG === "undefined") return ""; const L = (CFG.ledger || {})[k];
    if (!L || !L.n) return Lg("Ledger: no graded trade of this strategy yet", "الدفتر: لسه مفيش صفقة متقيّمة للاستراتيجية دي") + (L && L.sig ? " (" + L.sig + Lg(" signals waiting / not filled", " إشارة مستنية / ماتنفذتش") + ")" : "");
    const lv = {collecting:Lg("watch only, n < 10", "مراقبة بس، أقل من 10"), lean:Lg("lean, NOT evidence", "ميل، مش دليل"), evidence:Lg("evidence after costs", "دليل بعد التكاليف"), evidence_weak:Lg("n >= 30, edge not proven", "30+، الميزة مش مثبتة")}[L.lvl] || L.lvl;
    return Lg("Ledger record: ", "سجل الدفتر: ") + L.n + Lg(" trades · win ", " صفقة · فوز ") + (L.win != null ? L.win + "%" : "—") + " · " + (L.avg != null ? (L.avg >= 0 ? "+" : "") + L.avg + "R" : "—") + " · " + lv;
  },
  ihHide(){ clearTimeout(this._ihT); if (this._ihTip){ this._ihTip.remove(); this._ihTip = null; } },
  ihShow(ids, cx, cy){
    this.ihHide(); if (!ids.length) return; const tip = el("div", "ihtip"); tip.style.cssText = "position:fixed;z-index:2147483002;max-width:340px;left:"+(cx + 14)+"px;top:"+(cy + 14)+"px";
    ids.forEach((id, j) => { const I = this.ihInfo(id), b = el("div", "ihrow"); if (j) b.style.borderTop = "1px solid var(--line,#2b3139)";
      const nm = I.name && I.name !== id ? I.name : (IH_EXTRA[id] ? {journal:Lg("Journal","الجورنال"), draw:Lg("Drawing","رسمة"), alarm:Lg("Alert","تنبيه"), sr:"S/R", sides:Lg("Side marks","علامات جانبية"), volume:Lg("Volume","الفوليوم")}[id] || id : id);
      b.innerHTML = "<b>"+esc(nm)+"</b>"+(I.on === false ? " <span style='color:#848e9c'>("+esc(Lg("off","مقفول"))+")</span>" : "")+(I.help ? "<div class='ihh'>"+esc(I.help)+"</div>" : "")+(I.src ? "<div class='ihs'>"+esc(I.src).replace(/\n/g, "<br>")+"</div>" : "")
        +(I.menu ? "<div class='iho'>↗ "+esc(Lg("Open in Indicators", "افتحه في المؤشرات"))+"</div>" : "");
      if (I.menu){ b.style.cursor = "pointer"; b.onclick = e => { e.stopPropagation(); this.ihHide(); this.openInd && this.openInd(id); }; }
      tip.append(b); });
    tip.onpointerdown = e => e.stopPropagation(); tip.onpointerenter = () => { this._ihIn = true; }; tip.onpointerleave = () => { this._ihIn = false; this._ihT = setTimeout(() => this.ihHide(), 500); };
    document.body.append(tip); const r = tip.getBoundingClientRect();   // keep it on screen
    if (r.right > innerWidth - 4) tip.style.left = Math.max(4, cx - r.width - 14)+"px"; if (r.bottom > innerHeight - 4) tip.style.top = Math.max(4, cy - r.height - 14)+"px";
    this._ihTip = tip; this._ihA = {x:cx, y:cy};
    const off = ev => { if (this._ihTip && !this._ihTip.contains(ev.target)){ this.ihHide(); document.removeEventListener("pointerdown", off, true); } }; setTimeout(() => document.addEventListener("pointerdown", off, true), 0);
  },
  ihInit(){   // called from the constructor: dwell timer on the canvas
    const cv = this.cv; let pos = null;
    cv.addEventListener("pointermove", e => {
      if (e.pointerType === "touch") return;
      if (this._ihTip && this._ihA && Math.hypot(e.clientX - this._ihA.x, e.clientY - this._ihA.y) > 28 && !this._ihIn){ clearTimeout(this._ihT); this._ihT = setTimeout(() => { if (!this._ihIn) this.ihHide(); }, 350); }
      if (pos && Math.hypot(e.clientX - pos.x, e.clientY - pos.y) < 5) return;   // tiny jitter does not restart the wait
      pos = {x:e.clientX, y:e.clientY}; clearTimeout(this._ihW);
      if (e.buttons || this.drag || this.tool !== "cur" || this._ihTip) return;
      this._ihW = setTimeout(() => { if (this.drag || this.tool !== "cur" || !this.mouse) return; const ids = this.ihAt(this.mouse.x, this.mouse.y); if (ids.length) this.ihShow(ids, pos.x, pos.y); }, IH_DWELL);
    });
    ["pointerdown", "wheel"].forEach(t => cv.addEventListener(t, () => { clearTimeout(this._ihW); pos = null; }, {passive:true}));
    cv.addEventListener("pointerleave", () => { clearTimeout(this._ihW); pos = null; if (this._ihTip){ clearTimeout(this._ihT); this._ihT = setTimeout(() => { if (!this._ihIn) this.ihHide(); }, 400); } });
  },
  ihDbl(e){   // double-click on an indicator's drawing: open its row in the Indicators window (true = handled, so the view is not re-fitted)
    if (this.tool !== "cur") return false; const q = this.pt(e), ids = this.ihAt(q.x, q.y).filter(id => id !== "draw"); if (!ids.length) return false;
    const m = ids.find(id => this.indInfo && this.indInfo(id)); if (m && this.openInd){ this.openInd(m); return true; }
    this.ihShow(ids, e.clientX, e.clientY); return true;
  }
});
/* IND-HITS-END */
