/* ---------------- own candlestick chart (canvas) ---------------- */
function niceTicks(lo, hi, n){
  const range = Math.max(hi-lo, 1e-12), raw = range/n, mag = Math.pow(10, Math.floor(Math.log10(raw))), nm = raw/mag;
  const step = (nm < 1.5 ? 1 : nm < 3 ? 2 : nm < 7 ? 5 : 10) * mag, out = [];
  for (let v = Math.ceil(lo/step)*step; v <= hi; v += step) out.push(v);
  return {ticks:out, step};
}
// task 52: a time-synced crosshair. When on, moving the cross over one chart of a symbol draws the same time on every other chart of that symbol.
const XHS = {on:true, t:null, sym:null, src:null}; const XH_CHARTS = new Set(), XH_BTNS = new Set();
function xhSet(v){ XHS.on = !!v; store.set(LS+"_xh", XHS.on); XH_BTNS.forEach(b => b.classList.toggle("on", XHS.on)); if (!XHS.on) XHS.t = null; XH_CHARTS.forEach(c => c.draw()); }   // one switch for all charts / tabs
function xhSync(src){ if (!XHS.on) return; const ii = Math.max(0, Math.min(src.data.length-1, Math.round(src.idx(src.mouse ? src.mouse.x : 0)))); const d = src.data[ii]; if (!d) return;
  XHS.t = d.t; XHS.sym = src.sym; XHS.src = src; XH_CHARTS.forEach(c => { if (c !== src && c.sym === src.sym && c.data && c.data.length) c.draw(); }); }
class CandleChart {
  constructor(host){
    this.host = host; this.cv = el("canvas"); host.appendChild(this.cv); this.ctx = this.cv.getContext("2d");
    this.data = []; this.S = 1; this.bw = 9; this.r = 0; this.yZoom = 1; this.yShift = 0; this.tf = "1H"; this.autoCenter = false;
    this.ema = {vwap:false}; this.maL = [{on:true, type:"EMA", len:9, color:"#f0b90b", w:1.2, dash:""}, {on:true, type:"EMA", len:21, color:"#4aa3ff", w:1.2, dash:""}, {on:false, type:"EMA", len:50, color:"#b57cff", w:1.2, dash:""}]; this.rsiOn = false; this.macdOn = false; this.donOn = false; this.mt5On = false; this.lvOn = false; this.llOn = false; this.llD = null; this.divOn = true; this.colOn = false; this.colW = 0; this.colWide = 0; this.wom = {snaps:[]}; this.subOrd = ["rsi","macd","adx","cci","zn","bso","rm","r2"]; this.adxOn = false; this.cciOn = false; this.psarOn = false; this.znOn = false; this.r2On = false; this.bbShow = true; this.bsoOn = false; this.rmOn = false; this.kzsOn = false; this.gannOn = false; this.liqOn = false; this.liqs = []; this.syncOn = false; this.sync = null; this.syncLog = []; this.astroOn = false;
    this.st = {vwap:{color:"#e6e6e6",w:1.2,dash:"6,3"},
      rsi:{color:"#b57cff",w:1.2,dash:"",len:14,ob:70,os:30,hp:18}, vol:{color:"#848e9c",w:1,dash:"",h:18,delta:1}, of:{hm:"book",hmm:"fix",hmBright:1,color:"#0ecb81",color2:"#f6465d",w:1,dash:"",min:1,dom:1,bsz:1,bop:1,sidec:1,sweepC:"#4aa3ff",absC:"#f0b90b",bigx:2.5, fpMode:"bidask", fpRow:1, fpImb:3, fpStk:3, fpMin:10, fpDiag:1, fpStack:1, fpNaked:1, fpDelta:1, fpAuc:1}, macd:{color:"#4aa3ff",color2:"#f0b90b",w:1.2,dash:"",fast:12,slow:26,sig:9,hp:18},
      zn:{color:"#f0e442",color2:"#8a94a3",w:1.4,dash:"",k:5,d:9,s:3,rl:14,sell:85,buy:15,hp:20}, bso:{color:"#4aa3ff",color2:"#f0b90b",w:1.2,dash:"",bb:20,dev:2,k:5,d:3,s:3,fast:12,slow:26,sig:9,hp:20}, rm:{color:"#b57cff",color2:"#f0b90b",w:1.3,dash:"",len:14,ma:8,m1:21,m2:30,m3:40,hi:92,lo:8,hp:18}, r2:{color:"#e6e600",color2:"#00e000",w:1.3,dash:"",len:2,fast:1000,slow:2,sig:2000,hp:20}, adx:{color:"#f0b90b",color2:"#0ecb81",w:1.3,dash:"",len:14,lvl:25,hp:18}, cci:{color:"#26c6da",w:1.3,dash:"",len:20,hp:18}, psar:{color:"#0ecb81",color2:"#f6465d",w:1,dash:"",step:.02,max:.2},
      gann:{color:"#26c6da",color2:"#f6465d",w:1,dash:"",v3:1,v4:1,v5:1,lcyc:"auto",mtf:"auto",mtfn:3,ctol:.35,ctolT:3,zsrc:"clusters",zw:2,htf:"auto",anc:"best",tq:"off",sqr:1,cbox:0,mode:"auto",src:"auto",start:0,spacing:0,tback:0,dir:"both",shape:4,calc:"avg",cycles:1,sec:1,lbl:1,ext:1,tlv:1,tsp:0,toff:0,tdate:"",star:0,starc:"#f0b90b",spts:8,fan:1,zone:1},liq:{color:"#f6465d",color2:"#0ecb81",w:1,dash:"",min:10000,size:1},astro:{color:"#f0b90b",color2:"#9aa4b2",w:1,dash:"",moon:1,mq:0,asp:1,p1:"jupiter",p2:"saturn",ahel:0,aset:"major",retro:1,rp:"mercury",pl:0,plp:"sun",plhel:0,scale:0,harm:4},sync:{color:"#0ecb81",color2:"#f6465d",w:1,dash:"",book:.15,tape:.2,lim:1,win:60,rr:1.5,cool:3,exp:60},vp:{v:3,mode:"vd",range:"vis",rowpx:3,wpct:10,lbl:0,book:1,walls:1},
      flow:{color:"#f0b90b",color2:"#b57cff",w:1.5,dash:"",anchor:1,len:0,max:6,age:120,tgt:1},
      mt5:{color:"#ffeb3b",w:1.4,dash:"",ema:0,step:.02,max:.2,fr:2,sar:1,frc:1,rib:1,p1:10,p2:20,p3:50,p4:100,p5:200}}; this.overlay = null; this.harmOn = false; this.bvdOn = false; this.ewOn = false; this.volOn = true; this.lockR = null; this.subDrag = null; this.onSubH = null; this.lastBook = null; this.planLen = 40; this.planDrag = false; this._planH = null; this.onPlanLen = null; this.fpOn = false; this.deltaOn = false; this.fp = new Map(); this.bubOn = false; this.dotOn = false; this.domOn = false; this.mkOn = false; this.bub = []; this.dom = new Map(); this.vpOn = false; this.vpLv = null; this._harm = null; this.showSig = true; this.marks = []; this.sigs = []; this.flowOn = true; this.pulse = true; this.mouse = null; this.drag = null; this.onNeedMore = null; XH_CHARTS.add(this); this.W = 0; this.H = 0;
    const cv = this.cv;
    window.addEventListener("pagehide", () => { try { this.saveView(); } catch(e){} }); document.addEventListener("visibilitychange", () => { if (document.hidden){ try { this.saveView(); } catch(e){} } });   // flush on tab close / refresh
    cv.addEventListener("wheel", e => { e.preventDefault(); clearTimeout(this._svT); this._svT = setTimeout(() => this.saveView(), 250); this.wheel(e); }, {passive:false});   // wheel fires 60+/s: one localStorage write after the gesture, not one per event
    cv.addEventListener("pointerdown", e => this.down(e));
    cv.addEventListener("pointermove", e => this.move(e));
    cv.addEventListener("pointerup", e => this.up(e));
    cv.addEventListener("pointercancel", e => { (this.tp || new Map()).delete(e.pointerId); this.pinch = null; this.up(e); });   // the browser took the gesture (vertical page scroll)
    cv.addEventListener("pointerleave", () => { if (!this.drag){ this.mouse = null; this.draw(); } });
    cv.addEventListener("dblclick", e => { const q = this.pt(e), d = this.drawingsVisible && this.tool === "cur" ? this.draws.slice().reverse().find(x => !x.hidden && this.hit(x, q.x, q.y)) : null; if (d){ this.sel = d; this.draw(); this.openEditor(d); } else this.fit(); });
    cv.addEventListener("contextmenu", e => this.ctxMenu(e));
    cv.tabIndex = 0; cv.style.outline = "none";
    cv.addEventListener("keydown", e => { if (e.key === "Delete" || e.key === "Backspace"){ this.deleteSel(); } else if (e.key === "Escape"){ this.cancelTool(); } });
    this.draws = []; this.drawingsVisible = true; this.tool = "cur"; this.sel = null; this.creating = null; this.setupMode = "lines"; this.drawKey = null; this.onToolChange = null;
    this.ro = new ResizeObserver(() => this.resize()); this.ro.observe(host); this.resize();
  }
  destroy(){ this.ro.disconnect(); }
  cw(){ if (!this.colOn) return 0; const mx = Math.max(60, Math.round(this.W*0.65 - this.axw));   // the candle area keeps at least 35 % of the chart (owner 2026-10-24)
    if (this.colW) return Math.max(60, Math.min(mx, this.colW)); const big = (TFSEC[this.tf] || 3600) >= 14400;   // 4H / 1D / 1W: the default column is slimmer so it does not cover levels
    const nar = this.W < 520;   // a small panel (tablet grid, phone): the candles keep more of the width, the column is slimmer
    return Math.min(mx, big ? Math.max(nar ? 72 : 130, Math.min(nar ? 150 : 240, Math.round(this.W*(nar ? 0.20 : 0.24)))) : Math.max(nar ? 96 : 180, Math.min(nar ? 220 : 340, Math.round(this.W*(nar ? 0.30 : 0.34))))); }   // bigger default (owner 2026-11-05: "too small"); the candles still keep >= 35 %, drag the edge or double-click to change/reset   // order-flow column sits between the plot and the price axis; drag its left edge to resize
  subActive(){ return this.subOrd.filter(k => this[k+"On"]); }
  get axw(){ return this._axw || (this._axw = Math.max(44, Math.min(200, +store.get(LS+"_axw", 62) || 62))); } set axw(v){ this._axw = v; store.set(LS+"_axw", v); }
  get PR(){ return this.W - this.axw - this.cw(); } subHs(){ const a = this.subActive().map(k => Math.max(18, Math.round(this.H*this.st[k].hp/100))); const tot = a.reduce((x,y) => x+y, 0), cap = Math.max(0, this.H - 70); /* a pane can shrink to its title strip (18 px) or grow until the price area is 70 px */ return tot > cap && tot ? a.map(v => v*cap/tot) : a; }
  get subH(){ return this.subHs().reduce((x,y) => x+y, 0); }
  get PB(){ return this.H - 20 - this.subH; }
  drawSoon(){ if (this._rq) return; this._rq = requestAnimationFrame(() => { this._rq = 0; this.draw(); }); }   // live ticks can arrive dozens of times a second per chart: at most one full repaint per frame
  resize(){
    const dpr = window.devicePixelRatio || 1, hw = this.host.clientWidth, hh = this.host.clientHeight; this.S = CHART_S;
    this.W = hw/this.S; this.H = hh/this.S;   // the chart is laid out in its own units: at 50 % zoom it has twice the room, so more candles fit
    const cw_ = Math.round(this.W*dpr), ch_ = Math.round(this.H*dpr); if (this.cv.width !== cw_) this.cv.width = cw_; if (this.cv.height !== ch_) this.cv.height = ch_;   // assigning width/height clears the canvas even when the value is the same
    this.cv.style.width = hw+"px"; this.cv.style.height = hh+"px";
    this.ctx.setTransform(dpr,0,0,dpr,0,0); this.paint();   // paint NOW, not draw(): ResizeObserver runs after the frame's rAF callbacks, so a rAF-deferred repaint leaves one blank canvas frame on screen = the blink
  }
  setData(arr, fit){
    this.data = arr; this.calcEma();
    if (fit){ const sv = this.autoCenter ? null : store.get(this.viewKey(), null); this.fit(); if (sv && arr.length > 3 && sv.bw){ this.restoreFrom(sv); this.draw(); } }   // fit() overwrote the saved view with the default: put back what was saved (zoom, position, price scale) so a reload opens exactly where it was left
    else { if (this.autoCenter) this.followLatest(); this.draw(); }
    if (fit && this.lockR && arr.length){ const lc = arr[arr.length-1].c, lo = this.lockR[0], hi = this.lockR[1], sp = hi - lo;   // a saved manual price lock that the price has left by more than its whole height is a stale leftover (owner 2026-11-05: locked while the PC clock was wrong, gold now 4127 vs lock ~4020-4065): back to automatic
      if (sp > 0 && (lc < lo - sp || lc > hi + sp)){ this.autoY(); this.draw(); } }
  }
  restoreFrom(v){ this.bw = v.bw || this.bw; this.yZoom = v.yZoom || 1; this.yShift = v.yShift || 0; this.r = (this.data.length-1) - v.back; this.clampR(); this.saveView(); }
  calcEma(){
    this.emaV = {};
    const emaOf = (arr, len) => { const k = 2/(len+1); let e = null; return arr.map(v => (e = e == null ? v : v*k + e*(1-k))); };
    const cl = this.data.map(c => c.c);
    this.emaV = {9:maOf(cl, 9, "EMA"), 21:maOf(cl, 21, "EMA")};   // the REJ filter's fast / slow pair, always on
    this.maV = this.maL.map(m => m.on ? maOf(cl, Math.max(1, m.len|0), m.type) : null);
    if (this.rsiOn){ const L = Math.max(2, this.st.rsi.len|0); let ag = 0, al = 0; this.rsiV = cl.map((v,i) => { if (!i) return 50; const d = v - cl[i-1], g = Math.max(d,0), l = Math.max(-d,0);
        if (i <= L){ ag += g/L; al += l/L; } else { ag = (ag*(L-1)+g)/L; al = (al*(L-1)+l)/L; } return i < L ? 50 : al === 0 ? 100 : 100 - 100/(1+ag/al); }); }
    if (this.macdOn){ const m = this.st.macd, ef = emaOf(cl, m.fast|0 || 12), es = emaOf(cl, m.slow|0 || 26), ml = ef.map((v,i) => v - es[i]), sg = emaOf(ml, m.sig|0 || 9); this.macdV = {m:ml, s:sg, h:ml.map((v,i) => v - sg[i])}; }
    if (this.znOn){ const z = this.st.zn, K = stochK(this.data, z.k|0 || 5, z.s|0 || 3); this.znV = {k:K, d:smaOf(K, z.d|0 || 9), r:rsiOf(cl, z.rl|0 || 14)}; }
    if (this.rmOn){ const m = this.st.rm, r = rsiOf(cl, m.len|0 || 14); const ex = [[m.m1 ?? 21, "#26c6da"], [m.m2 ?? 30, "#ff9800"], [m.m3 ?? 40, "#ec407a"]].filter(x => (x[0]|0) > 0).map(([n, col]) => ({n:n|0, col, a:smaOf(r, n|0)})); this.rmV = {r, m:smaOf(r, m.ma|0 || 8), ex}; }
    if (this.r2On){ const m = this.st.r2, r = rsiOf(cl, m.len|0 || 2), kf = 2/((m.fast|0 || 1000)+1), ks = 2/((m.slow|0 || 2)+1), sgN = m.sig|0 || 2000; let ef = r[0], es = r[0]; const mac = r.map(v => { ef = v*kf + ef*(1-kf); es = v*ks + es*(1-ks); return ef - es; });   // MT5 "Moving Average of Oscillator" (OsMA) applied to the RSI data: MACD = EMA(fast) - EMA(slow) of the RSI, signal = SMA(MACD, sig); histogram = MACD - signal. With fewer bars than the signal period, the SMA runs over the bars available.
      let sum = 0; const sg = mac.map((v, i) => { sum += v; if (i >= sgN) sum -= mac[i-sgN]; return sum/Math.min(i + 1, sgN); }); const os_ = mac.map((v, i) => v - sg[i]); this.r2V = {r, osma:os_};
      { const sm50 = smaOf(cl, 50), sgl = []; let prev = null; os_.forEach((v, i) => { const st = v > 0 && v <= 10 ? "up" : v > 10 ? "down" : null; if (st && st !== prev) sgl.push([i, st]); prev = st ? st : (v > 0 ? prev : null); });   // live success rate of the rule on the candles this chart has loaded (same variants as modules/backtest_osma.py)
        const stat = (flip, filt, H) => { let n = 0, w = 0; sgl.forEach(([i, d0]) => { if (i + H >= cl.length || i < 50) return; const d = flip ? (d0 === "up" ? "down" : "up") : d0; if (filt && !((d === "up" && cl[i] > sm50[i]) || (d === "down" && cl[i] < sm50[i]))) return; const rr = (cl[i+H]/cl[i] - 1)*(d === "up" ? 1 : -1); n++; if (rr > 0) w++; }); return n ? Math.round(1000*w/n)/10 + "% (" + n + ")" : "—"; };
        this.r2S = [5, 10].map(H => "next " + H + " bars · rule " + stat(false, false, H) + " · flipped " + stat(true, false, H) + " · rule+trend " + stat(false, true, H) + " · flipped+trend " + stat(true, true, H)); } }
    if (this.bsoOn){ const b = this.st.bso, K = stochK(this.data, b.k|0 || 5, b.s|0 || 3), n = b.bb|0 || 20, mid = smaOf(cl, n), sd = cl.map((v,i) => { const a = cl.slice(Math.max(0, i-n+1), i+1), mu = mid[i]; return Math.sqrt(a.reduce((x,y) => x + (y-mu)*(y-mu), 0)/a.length); });
      const ef = emaOf(cl, b.fast|0 || 12), es = emaOf(cl, b.slow|0 || 26), ml = ef.map((v,i) => v - es[i]), sg = emaOf(ml, b.sig|0 || 9);
      this.bsoV = {k:K, d:smaOf(K, b.d|0 || 3), osma:ml.map((v,i) => v - sg[i]), mid, up:mid.map((v,i) => v + (b.dev||2)*sd[i]), lo:mid.map((v,i) => v - (b.dev||2)*sd[i])}; }
    if (this.adxOn) this.adxV = adxOf(this.data, Math.max(2, this.st.adx.len|0 || 14));
    if (this.cciOn) this.cciV = cciOf(this.data, Math.max(2, this.st.cci.len|0 || 20));
    if (this.psarOn) this.psarV = psarOf(this.data, +this.st.psar.step || .02, +this.st.psar.step || .02, +this.st.psar.max || .2);
    const sec = TFSEC[this.tf] || 3600; let pv = 0, vv = 0, day = null;
    this.vwV = this.data.map(c => { const d = Math.floor(c.t/86400000); if (sec < 86400 && d !== day){ pv = 0; vv = 0; day = d; } const tp = (c.h+c.l+c.c)/3; pv += tp*c.v; vv += c.v; return vv ? pv/vv : c.c; });
  }
  followLatest(){
    const n = this.data.length; if (!this.autoCenter || !n) return;
    // Keep the user-selected horizontal and vertical zoom; move the latest candle to the plot center.
    this.r = n - 1 + Math.round(0.5*this.PR/this.bw);
    if (!isFinite(this.r)) return;   // no layout yet: keep the current view
    const [lo, hi] = this.range(Math.max(0, Math.floor(this.idx(0))-1), Math.min(n-1, Math.ceil(this.r)));
    const span = (hi-lo || hi*0.01 || 1)*1.12*this.yZoom;
    if (span > 0) this.yShift = (this.data[n-1].c - (hi+lo)/2) / span;
    this.clampR();
  }
  fit(){
    const n = this.data.length; this.yZoom = 1; this.yShift = 0; this._bookFit = !!this.bookFitOn;   // bookFitOn (off by default: the column stays on the chart's own price scale, level with the candles). _bookFit: with the order-flow column on, the price scale is framed once around the order book as soon as a book snapshot exists (see paint)
    this.r = n - 1 + Math.round(0.5*this.PR/this.bw); if (this.autoCenter) this.followLatest(); this.saveView(); this.draw();   // standard: the latest candle opens in the middle of the chart (free space on the right), with or without the order-flow column
  }
  freezeY(){   // price scale -> manual at the range on screen right now (TradingView: dragging the chart vertically switches auto-scale off); the ⇅ / 🔒 button switches it back
    if (this.lockR || this._lo == null || !isFinite(this._lo) || !isFinite(this._hi) || this._hi <= this._lo) return;
    const mid = (this._lo + this._hi)/2, half = (this._hi - this._lo)/2/1.12; this.lockR = [mid - half, mid + half]; this.yZoom = 1; this.yShift = 0; this.onFree && this.onFree(); }
  autoY(){ this.lockR = null; this.yZoom = 1; this.yShift = 0; this.onFree && this.onFree(); }   // price scale back to automatic (the same thing the toolbar's Auto / Manual button does)
  zoomY(f, ay){   // price-scale zoom by factor f, anchored at the price under y = ay (px from the top of the plot): that price stays put, so the candles do not fly away. One call changes the scale by at most 25 %, and the scale stays between 0.05x and 8x of the auto range (the old limits were 0.02x .. 60x: a few wheel clicks flattened the candles into a line)
    const n = this.data.length, z0 = this.yZoom, z1 = Math.max(0.05, Math.min(8, z0*Math.max(0.8, Math.min(1.25, f)))); if (!n || z1 === z0) return;
    const lo0 = this._lo, hi0 = this._hi; if (!isFinite(lo0) || !isFinite(hi0) || !(hi0 > lo0) || !(this.PB > 0)){ this.yZoom = z1; return; }
    const frac = Math.max(0, Math.min(1, ay/this.PB)), pa = hi0 - frac*(hi0 - lo0), y0 = this.yZoom, s0 = this.yShift;
    this.yZoom = 1; this.yShift = 0; const [bl, bh] = this.range(Math.max(0, Math.floor(this.idx(0)) - 1), Math.min(n - 1, Math.ceil(this.r))); this.yZoom = y0; this.yShift = s0;   // the auto (or locked) range at zoom 1
    const sp1 = (bh - bl)*z1; if (!(sp1 > 0)) return; const hi1 = pa + frac*sp1, mid1 = hi1 - sp1/2; this.yZoom = z1; this.yShift = (mid1 - (bh + bl)/2)/sp1;
  }
  candleY(){   // y (px from the plot top) of the middle of the candles on screen, clamped into view: the anchor for price-axis zoom (MT5 feel: the candles scale around themselves and never run away; the cursor is only the anchor for Shift + wheel)
    const n = this.data.length, lo0 = this._lo, hi0 = this._hi; if (!n || !(hi0 > lo0) || !(this.PB > 0)) return (this.PB || 0)/2;
    let l = Infinity, h = -Infinity; for (let i = Math.max(0, Math.floor(this.idx(0))); i <= Math.min(n-1, Math.ceil(this.r)); i++){ const d = this.data[i]; if (d.l < l) l = d.l; if (d.h > h) h = d.h; }
    if (!isFinite(l) || !isFinite(h)) return this.PB/2; return Math.max(0.1*this.PB, Math.min(0.9*this.PB, (hi0 - (l + h)/2)/(hi0 - lo0)*this.PB)); }
  clampR(){
    const n = this.data.length, maxR = n - 1 + 0.7*this.PR/this.bw, minR = Math.min(n-1, 3);
    this.r = Math.max(minR, Math.min(maxR, this.r));
  }
  x(i){ return this.PR - (this.r - i + 0.5)*this.bw; }
  idx(x){ return this.r + 0.5 - (this.PR - x)/this.bw; }
  wheel(e){
    const rect = this.cv.getBoundingClientRect(), mx = (e.clientX - rect.left)/this.S;
    if (mx > this.W-this.axw){ this._bookFit = false; this.zoomY(Math.exp(Math.max(-120, Math.min(120, e.deltaY))*0.0012), this.candleY()); this.drawSoon(); return; }   // wheel over the price axis: anchored at the cursor, at most ~15 % a notch
    if (mx > this.PR){ this.flowSpan = Math.max(20000, Math.min((this.st.of.hmm || "fix") === "fix" ? 604800000 : 1200000, this.fspan(nowS())*Math.exp(e.deltaY*0.001))); this.drawSoon(); return; }   // over the order-flow column: wheel = time zoom (20 s .. 20 min)
    if (e.shiftKey){ this._bookFit = false; this.freezeY(); this.zoomY(Math.exp(Math.max(-120, Math.min(120, e.deltaY))*0.0012), (e.clientY - rect.top)/this.S); this.drawSoon(); return; }   // Shift + wheel = price zoom, price scale stays where you put it
    const anchor = this.idx(mx), f = Math.exp(-Math.max(-120, Math.min(120, e.deltaY))*0.0015);   // one wheel event can zoom at most ~20 % (high-resolution wheels / trackpads send huge deltas)
    this.bw = Math.max(0.6, Math.min(600, this.bw*f));
    this.r = anchor - 0.5 + (this.PR - mx)/this.bw; this.clampR(); this.drawSoon(); this.checkMore();
  }
  down(e){
    { const r1 = this.cv.getBoundingClientRect(), mx1 = (e.clientX - r1.left)/this.S, my1 = (e.clientY - r1.top)/this.S;   // ✕ on the order-flow gauge / sync card
      const hit = k => { const Z = this[k]; return Z && mx1 >= Z.x && mx1 <= Z.x + Z.w && my1 >= Z.y && my1 <= Z.y + Z.h; };
      if (this.colOn && hit("_gaX")){ this.gaOn = false; this._gaX = null; this.onOfX && this.onOfX(); this.draw(); return; }
      if (this.colOn && hit("_scX")){ this.scOn = false; this._scX = null; this.onOfX && this.onOfX(); this.draw(); return; } }
    { const X = this._llX, r0 = this.cv.getBoundingClientRect(), mx0 = (e.clientX - r0.left)/this.S, my0 = (e.clientY - r0.top)/this.S;   // ✕ on the targets table
      if (X && this.llOn && this.llTbl !== false && mx0 >= X.x && mx0 <= X.x + X.w && my0 >= X.y && my0 <= X.y + X.h){ this.llTbl = false; this._llX = null; this.onLLTbl && this.onLLTbl(); this.draw(); return; }
      const K = this._kzsX; if (K && this.kzsOn && this.kzsTbl !== false && mx0 >= K.x && mx0 <= K.x + K.w && my0 >= K.y && my0 <= K.y + K.h){ this.kzsTbl = false; this._kzsX = null; this.onKzsTbl && this.onKzsTbl(); this.draw(); return; } }
    if (e.pointerType === "touch"){ this._tap0 = (this.tp && this.tp.size) ? null : {x:e.clientX, y:e.clientY, t:Date.now()};
      if (this.xMode){ const rc = this.cv.getBoundingClientRect(); this._lp = true; this.drag = null; this.mouse = {x:(e.clientX - rc.left)/this.S, y:(e.clientY - rc.top)/this.S}; this.draw(); return; } }   // MT5 crosshair button: one finger moves the cross
    if (e.pointerType === "touch"){ clearTimeout(this._lpT); this._lp = false; const sx = e.clientX, sy = e.clientY;
      this._lpT = setTimeout(() => { if (this.drag && Math.hypot(this.drag.x - sx, this.drag.y - sy) < 8 && !this.pinch){ this._lp = true; this.drag = null; const rc = this.cv.getBoundingClientRect(); this.mouse = {x:(sx - rc.left)/this.S, y:(sy - rc.top)/this.S}; this.draw(); } }, 450); }   // long press = crosshair
    if (e.pointerType === "touch"){ const tp = this.tp = this.tp || new Map(); tp.set(e.pointerId, {x:e.clientX, y:e.clientY});
      if (tp.size === 2){ const [a, b] = [...tp.values()], rect = this.cv.getBoundingClientRect(), mid = ((a.x + b.x)/2 - rect.left)/this.S;   // two fingers = pinch zoom on time
        this.pinch = {d0:Math.max(20, Math.abs(a.x - b.x)), dy0:Math.max(20, Math.abs(a.y - b.y)), vert:Math.abs(a.y - b.y) > Math.abs(a.x - b.x)*1.2, dyP:Math.max(20, Math.abs(a.y - b.y)), bw0:this.bw, mid, anchor:this.idx(mid)}; this.drag = null; return; } }   // vert = the two fingers started mostly one above the other: that spread zooms the PRICE scale
    try { this.cv.setPointerCapture(e.pointerId); } catch(_){} this.cv.focus({preventScroll:true});
    { const r0 = this.cv.getBoundingClientRect(), mx0 = (e.clientX - r0.left)/this.S, my = (e.clientY - r0.top)/this.S, hit = this.layoutHit(mx0, my);
      if (hit){
        if (hit.kind === "col"){ const now = Date.now(); if (this._colClick && now - this._colClick < 350){ this.colW = 0; this.onLayout && this.onLayout(); this.draw(); this._colClick = 0; return; } this._colClick = now; this.colDrag = {x:e.clientX, w:this.cw()}; return; }
        if (hit.kind === "axw"){ this.axDrag = {x:e.clientX, w:this.axw}; return; }
        if (hit.kind === "up" || hit.kind === "dn"){ this.swapSub(hit.k, hit.kind === "up" ? -1 : 1); return; }
        if (hit.kind === "x"){ this[hit.k+"On"] = false; this.onSubOff && this.onSubOff(hit.k); this.resize ? this.resize() : 0; this.draw(); return; }   // ✕ = turn the pane off
        if (hit.kind === "move"){ this.subMove = {k:hit.k}; return; }
        if (hit.kind === "size"){ this.subDrag = {k:hit.k, y:e.clientY, hp:this.st[hit.k].hp}; return; }
      } }
    if (this.toolDown(e)) return;
    const rect = this.cv.getBoundingClientRect(), mx = (e.clientX - rect.left)/this.S;
    this.drag = {x:e.clientX, y:e.clientY, axis: mx > this.W-this.axw};
  }
  move(e){
    if (this.pinch && this.tp && this.tp.has(e.pointerId)){ this.tp.set(e.pointerId, {x:e.clientX, y:e.clientY}); const v = [...this.tp.values()]; if (v.length < 2) return;
      const P = this.pinch; if (P.vert){ const dy = Math.max(20, Math.abs(v[0].y - v[1].y)); this._bookFit = false; if (!this.lockR) this.freezeY(); this.zoomY(P.dyP/dy, this.candleY()); P.dyP = dy; this.drawSoon(); return; }   // price pinch: spreading the fingers magnifies the candles, anchored on the middle of the candles (never flies away)
      const f = Math.max(20, Math.abs(v[0].x - v[1].x))/P.d0; this.bw = Math.max(0.6, Math.min(600, P.bw0*f)); this.r = P.anchor - 0.5 + (this.PR - P.mid)/this.bw; this.clampR(); this.drawSoon(); this.checkMore(); return; }
    const rect = this.cv.getBoundingClientRect(); this.mouse = {x:(e.clientX-rect.left)/this.S, y:(e.clientY-rect.top)/this.S}; XH_CHARTS.add(this); xhSync(this);
    if (this._tap0 && Math.hypot(e.clientX - this._tap0.x, e.clientY - this._tap0.y) > 8) this._tap0 = null;
    if (this._lp){ this.drawSoon(); return; }   // crosshair mode (long press): move the cross, do not pan
    if (this.axDrag){ this.axw = Math.max(36, Math.min(320, Math.round(this.axDrag.w + (this.axDrag.x - e.clientX)/this.S))); this.drawSoon(); return; }
    if (this.colDrag){ this.colW = Math.max(60, Math.min(Math.round(this.W*0.65 - this.axw), Math.round(this.colDrag.w + (this.colDrag.x - e.clientX)/this.S))); /* order-flow column: 60 px .. 85 % */ this.drawSoon(); return; }
    if (this.subDrag){ const dh = ((this.subDrag.y - e.clientY)/this.S)/Math.max(1, this.H)*100; this.st[this.subDrag.k].hp = Math.max(1, Math.min(92, Math.round((this.subDrag.hp + dh)*10)/10)); /* drag the divider all the way down or up */ this.resize(); this.drawSoon(); return; }
    if (this.subMove){ const act = this.subActive(), i = act.indexOf(this.subMove.k), P = this._panes || [], me = P.find(q => q.k === this.subMove.k);
      if (me && i >= 0){ const my = this.mouse.y; if (i > 0 && my < me.y0 - 4) this.swapSub(this.subMove.k, -1); else if (i < act.length-1 && my > me.y0 + me.h + 8) this.swapSub(this.subMove.k, 1); } return; }
    { const hh = this.layoutHit(this.mouse.x, this.mouse.y); this.cv.style.cursor = hh ? ((hh.kind === "col" || hh.kind === "axw") ? "ew-resize" : hh.kind === "size" ? "ns-resize" : hh.kind === "move" ? "grab" : "pointer") : (this.tool === "cur" ? "" : "crosshair"); }
    if (this.tool === "cur" && this.drawingsVisible && !this.drag && !this.dragD && this.mouse){ const q0 = this.pt(e);
      if (q0.x <= this.PR && q0.y <= this.PB){ const hd = this.draws.slice().reverse().find(x => !x.hidden && this.hit(x, q0.x, q0.y)); if (hd) this.cv.style.cursor = hd.lock ? "not-allowed" : "move"; } }
    if (this.toolMove(e)){ this.drawSoon(); return; }
    if (this.drag){
      const dx = (e.clientX - this.drag.x)/this.S, dy = (e.clientY - this.drag.y)/this.S; this.drag.x = e.clientX; this.drag.y = e.clientY;
      if (this.drag.axis){ this._bookFit = false; if (!this.lockR && this.drag.ay == null){ this.freezeY(); this.drag.ay = 1; } this.zoomY(Math.exp(Math.max(-30, Math.min(30, dy))*0.004), this.candleY()); }   // drag the price axis: smooth, about the middle of the plot (the scale turns manual first so the candles are not re-fitted under your hand)
      else { this._bookFit = false; this.drag.ty = (this.drag.ty || 0) + Math.abs(dy); this.drag.tx = (this.drag.tx || 0) + Math.abs(dx);
        const vert = e.pointerType !== "touch" || (this.drag.ty > 28 && this.drag.ty > 1.6*this.drag.tx);   // a finger: only a clearly VERTICAL drag turns the price scale manual; a sideways swipe (even a wobbly one) just moves time and never locks the scale
        if (this.lockR || vert){ if (this.drag.ty > 6) this.freezeY(); this.yShift += dy/Math.max(1, this.PB); }
        this.r -= dx/this.bw; this.clampR(); this.checkMore(); }
    }
    this.drawSoon();
  }
  /* view memory: the position is kept as offsets from the latest candle, so a refresh reopens the same view (not re-fitted) */
  viewKey(){ return LS+"_view|"+(this.uid || "")+"|"+this.sym+"|"+this.tf; }
  saveView(){ if (!this.data.length || this.r == null || this.autoCenter) return; try { store.set(this.viewKey(), {back: (this.data.length-1) - this.r, bw: this.bw, yZoom: this.yZoom, yShift: this.yShift}); } catch(e){} }
  restoreView(){ try { if (this.autoCenter) return false; const v = store.get(this.viewKey(), null); if (!v || !this.data.length) return false; this.bw = v.bw || this.bw; this.yZoom = v.yZoom || 1; this.yShift = v.yShift || 0; this.r = (this.data.length-1) - v.back; this.clampR(); return true; } catch(e){ return false; } }
  up(e){
    if (this.creating && this.creating.type === "brush"){ const d = this.creating; this.creating = null; if (d.pts.length < 3) this.draws = this.draws.filter(x => x !== d); else { this.sel = d; this.saveDraws(); } this.setTool("cur"); this.draw(); return; }
    if (e && e.pointerType === "touch"){ const t0 = this._tap0, lp = this._lp; this._tap0 = null; clearTimeout(this._lpT); if (this._lp){ this._lp = false; if (!this.xMode) this.mouse = null; this.draw(); }
      if (t0 && !lp && !this.xMode && !this.pinch && Date.now() - t0.t < 350 && (!this.tool || this.tool === "cur") && this.onTap){ const rc = this.cv.getBoundingClientRect(); this.onTap((t0.x - rc.left)/this.S, (t0.y - rc.top)/this.S); } }   // a quick tap = MT5 round menu
    if (this.tp){ this.tp.delete(e.pointerId); if (this.tp.size < 2) this.pinch = null; } this.axDrag = null; if (this.subDrag){ this.subDrag = null; this.onSubH && this.onSubH(); } if (this.colDrag){ this.colDrag = null; this.onLayout && this.onLayout(); } if (this.subMove){ this.subMove = null; this.onLayout && this.onLayout(); } this.toolUp(e); this.drag = null; }
  swapSub(k, dir){ const act = this.subActive(), i = act.indexOf(k), j = i + dir; if (i < 0 || j < 0 || j >= act.length) return; const a = this.subOrd.indexOf(k), b = this.subOrd.indexOf(act[j]); [this.subOrd[a], this.subOrd[b]] = [this.subOrd[b], this.subOrd[a]]; this.onLayout && this.onLayout(); this.draw(); }
  layoutHit(mx, my){
    if (Math.abs(mx - (this.W - this.axw)) <= 3 && my >= 0 && my < this.H) return {kind:"axw"};   // what the pointer is on: the order-flow column's left edge, a sub-pane's top edge (resize), its title (drag to reorder) or its up/down buttons
    if (this.colOn && Math.abs(mx - this.PR) <= 4 && my >= 0 && my < this.PB) return {kind:"col"};
    for (const q of (this._panes || [])){ if (my >= q.y0 - 7 && my <= q.y0 + 2 && mx < this.PR) return {kind:"size", k:q.k};
      if (my > q.y0 + 2 && my <= q.y0 + 17){ if (mx >= this.PR - 54 && mx < this.PR - 38) return {kind:"x", k:q.k}; if (mx >= this.PR - 36 && mx < this.PR - 20) return {kind:"up", k:q.k}; if (mx >= this.PR - 20 && mx < this.PR - 4) return {kind:"dn", k:q.k}; if (mx >= 0 && mx < 150) return {kind:"move", k:q.k}; } }
    return null; }
  checkMore(){ if (this.onNeedMore && this.r - this.PR/this.bw < 15) this.onNeedMore(); }
  planLevels(){
    const o = this.overlay, lastC = this.data.length ? this.data[this.data.length-1].c : 0; if (!o || !o.plan || !this.showSig) return [];
    return [o.plan.entry, o.plan.stop].concat(o.plan.tps || []).filter(v => Math.abs(v-lastC)/lastC < 0.12);
  }
  range(i0, i1){
    let lo = Infinity, hi = -Infinity;
    for (let i = i0; i <= i1; i++){ const c = this.data[i]; if (c.l < lo) lo = c.l; if (c.h > hi) hi = c.h; }
    this.planLevels().forEach(v => { if (v < lo) lo = v; if (v > hi) hi = v; });
    if (!isFinite(lo)) return [0,1];
    if (this.lockR){ lo = this.lockR[0]; hi = this.lockR[1]; }   // Manual mode: the price scale stays where you left it
    const span = (hi-lo || hi*0.01 || 1)*1.12*this.yZoom, mid = (hi+lo)/2 + this.yShift*span;
    return [mid-span/2, mid+span/2];
  }
  fmtTime(ms){
    const d = new Date(ms), day = d.getDate()+" "+["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][d.getMonth()];
    if (TFSEC[this.tf] < 60) return pad2(d.getHours())+":"+pad2(d.getMinutes())+":"+pad2(d.getSeconds());
    if (this.tf === "1D" || this.tf === "1W") return day;
    return d.getHours() === 0 && d.getMinutes() === 0 ? day : pad2(d.getHours())+":"+pad2(d.getMinutes());
  }
  drawData(){   // redraw asked by streaming data (book polls, trades): at most ~7 per second per chart; mouse / touch still use draw() at full speed
    const now = performance.now(); if (now - (this._dd || 0) >= 140){ this._dd = now; this.draw(); return; }
    if (!this._ddT) this._ddT = setTimeout(() => { this._ddT = 0; this._dd = performance.now(); this.draw(); }, 140 - (now - this._dd)); }
  draw(){
    if (this._raf) return;
    this._raf = requestAnimationFrame(() => { this._raf = 0; this.paint(); });
  }
  paint(){   // per-chart palette (state.pal: up / dn / bg / grid) is laid over the theme colours for the duration of one paint
    { const sg = this.r+"|"+this.bw+"|"+this.yZoom+"|"+this.yShift; if (sg !== this._sg){ this._sg = sg; clearTimeout(this._svT2); this._svT2 = setTimeout(() => this.saveView(), 500); } }   // auto-save: any change of the view (drag, zoom, price scale, resize) is stored 0.5 s later, so the next open starts exactly here
    if (!this.pal) this._paint(); else { const bak = Object.assign({}, TH); Object.assign(TH, this.pal); try { this._paint(); } finally { Object.assign(TH, bak); } }
    this._autoChip = null;
    { const n = this.data.length, lo = this._lo, hi = this._hi;   // the price scale is manual and the newest candle is outside it (a finger drag locked it): a big tap target brings the candles back
      if (this.lockR && n && lo != null && hi != null && isFinite(lo) && isFinite(hi)){ const lc = this.data[n-1].c; if (lc < lo || lc > hi){ const c = this.ctx, w = TCH ? 112 : 92, h2 = TCH ? 34 : 22, x = Math.max(6, this.PR - w - 10), y = 30;
        c.save(); c.fillStyle = "rgba(240,185,11,.95)"; c.beginPath(); c.roundRect ? c.roundRect(x, y, w, h2, 6) : c.rect(x, y, w, h2); c.fill(); c.fillStyle = "#111"; c.font = "bold "+(TCH ? 14 : 12)+"px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle";
        c.fillText("⇅ "+(lang === "ar" ? "أوتو" : "Auto"), x + w/2, y + h2/2); c.restore(); this._autoChip = {x, y, w, h:h2}; } } }
    const h = this._hint; if (h && Date.now() - h.t < 3500){ const c = this.ctx; c.save(); c.font = "bold 12px sans-serif"; c.textAlign = "left"; const w = c.measureText(h.s).width + 16; c.fillStyle = "rgba(240,185,11,.92)"; c.fillRect(8, 26, Math.min(w, this.W - 16), 22); c.fillStyle = "#111"; c.fillText(h.s, 16, 41); c.restore(); }
  }
  _paint(){
    const c = this.ctx, W = this.W, H = this.H, PR = this.PR, PB = this.PB, n = this.data.length; this._gChip = null;
    c.clearRect(0,0,W,H); c.fillStyle = TH.bg; c.fillRect(0,0,W,H);   // clear first: a dashboard theme may use a see-through background
    c.font = "11px ui-monospace,Menlo,Consolas,monospace"; c.textBaseline = "middle";
    if (!n){ c.fillStyle = TH.mut; c.fillText(T("loading"), 12, 20); return; }
    const i0 = Math.max(0, Math.floor(this.idx(0)) - 1), i1 = Math.min(n-1, Math.ceil(this.r));
    if (i1 < i0) return;
    if (this._bookFit && this.colOn && this.domOn && !this.lockR){   // the book only lists orders near the price (a thin band), the chart scale spans all visible candles: frame the scale around the book once, so the column shows real orders from the start without any zoom
      const sn = this.flowB && this.flowB[this.flowB.length-1], px = this.data[n-1].c;
      if (sn && sn.lv && sn.lv.length > 3){ let bl = px, bh = px; sn.lv.forEach(([q]) => { if (q < bl) bl = q; if (q > bh) bh = q; });
        const y0 = this.yZoom, s0 = this.yShift; this.yZoom = 1; this.yShift = 0; const [l0, h0] = this.range(i0, i1), sp0 = (h0 - l0) || 1, tg = Math.max((bh - bl)*1.3, px*(["1m","5m","13m","15m","30m","1H","1h","2H","2h","4H","4h"].includes(this.tf) ? 0.02 : 0.004));   // task 56 batch 1: small timeframes show a wider price band (at least ±1%) so more of the order flow is visible
        if (tg < sp0){ this.yZoom = Math.max(0.02, tg/sp0); this.yShift = (px - (h0 + l0)/2)/(sp0*this.yZoom); } else { this.yZoom = y0; this.yShift = s0; }
        this._bookFit = false; } }
    const [lo, hi] = this.range(i0, i1), py = v => PB - (v-lo)/(hi-lo)*PB; this._lo = lo; this._hi = hi;
    // grid + price axis
    const nt = niceTicks(lo, hi, Math.max(3, Math.floor(PB/48))), dec = Math.max(0, Math.min(8, 1 - Math.floor(Math.log10(nt.step))));
    c.strokeStyle = TH.grid; c.fillStyle = TH.mut; c.lineWidth = 1; c.textAlign = "left";
    nt.ticks.forEach(v => { const y = Math.round(py(v))+.5; c.beginPath(); c.moveTo(0,y); c.lineTo(PR,y); c.stroke(); c.fillText(v.toFixed(dec), (this.W-this.axw)+5, y); });
    // time axis
    const stepBars = Math.max(1, Math.ceil(90/this.bw)), mag = Math.pow(10, Math.floor(Math.log10(stepBars))), nb = stepBars/mag;
    const st = (nb <= 1 ? 1 : nb <= 2 ? 2 : nb <= 5 ? 5 : 10)*mag;
    c.textAlign = "center";
    for (let i = Math.ceil(i0/st)*st; i <= i1; i += st){
      const x = Math.round(this.x(i))+.5; c.beginPath(); c.moveTo(x,0); c.lineTo(x,PB); c.stroke();
      c.fillText(this.fmtTime(this.data[i].t), x, H-10);
    }
    c.strokeStyle = TH.line; c.beginPath(); c.moveTo(0,PB+.5); c.lineTo(W,PB+.5); c.moveTo(0,H-19.5); c.lineTo(W,H-19.5); c.moveTo((this.W-this.axw)+.5,0); c.lineTo((this.W-this.axw)+.5,H); c.stroke();
    // clip plot
    c.save(); c.beginPath(); c.rect(0,0,PR,PB); c.clip();
    if (this.kz) this.paintKZ(c, py, i0, i1, PB);
    if (this.kzsOn) this.paintKZS(c, py, i0, i1, PB);
    if (this.gannOn) this.paintGann(c, py, i0, i1, PB);
    if (this.liqOn) this.paintLiq(c, py, i0, i1, PB);
    if (this.astroOn) this.paintAstro(c, py, i0, i1, PB);
    if (this.syncOn){ this.paintSyncMarks(c, py, i0, i1, PB); }   // the card lives under the order-flow column (paintCol)
    if (this.psarOn && this.psarV){ const S = this.psarV, st = this.st.psar, r = Math.max(1.5, Math.min(3, this.bw*0.22)) * (st.w || 1);
      for (let i = i0; i <= i1; i++){ if (S.v[i] == null) continue; c.fillStyle = S.up[i] ? st.color : st.color2; c.beginPath(); c.arc(this.x(i), py(S.v[i]), r, 0, Math.PI*2); c.fill(); } }
    // Order-flow heat must stay in its dedicated column; never paint it over candle bodies.
    let vmax = 0; for (let i = i0; i <= i1; i++) vmax = Math.max(vmax, this.data[i].v);
    const bwp = Math.max(1, this.bw*0.7), DOT = !!this.dots && this.bw >= 5, ds = Math.max(3, Math.min(6, Math.round(this.bw*0.22))), dr = ds*0.36;   // dot-matrix style (theme 17 / 🎨 menu): candles, wicks, volume and averages are drawn as small dots
    const dotRect = (x0, y0, w, h) => { if (h < 1) h = 1; const nx = Math.max(1, Math.round(w/ds)), xs = x0 + (w - (nx-1)*ds)/2, ya = Math.ceil(y0/ds)*ds, yb = y0 + h; c.beginPath(); let any = false; for (let yy = ya; yy <= yb; yy += ds) for (let q = 0; q < nx; q++){ c.moveTo(xs + q*ds + dr, yy); c.arc(xs + q*ds, yy, dr, 0, Math.PI*2); any = true; } if (!any){ c.moveTo(xs + dr, y0); c.arc(xs, y0, dr, 0, Math.PI*2); } c.fill(); };
    for (let i = i0; i <= i1; i++){
      const k = this.data[i], up = k.c >= k.o, col = up ? TH.up : TH.dn, x = this.x(i);
      if (DOT){ const y1 = py(k.o), y2 = py(k.c);
        if (this.volOn){ const vh = vmax ? k.v/vmax*PB*(this.st.vol.h/100) : 0; c.fillStyle = hexA(up ? (TH.vu || TH.up) : (TH.vd || TH.dn), .35); dotRect(x - bwp/2, PB - vh, bwp, vh); }
        c.fillStyle = col; const wy0 = py(k.h), wy1 = py(k.l); c.beginPath(); for (let yy = Math.ceil(wy0/ds)*ds; yy <= wy1; yy += ds){ c.moveTo(x + dr*0.8, yy); c.arc(x, yy, dr*0.8, 0, Math.PI*2); } c.fill();
        dotRect(x - bwp/2, Math.min(y1, y2), bwp, Math.max(1, Math.abs(y1 - y2))); continue; }
      c.fillStyle = hexA(up ? (TH.vu || TH.up) : (TH.vd || TH.dn), .28);   // volume bars: own up / down colours when set (🎨 menu), else the candle colours
      if (this.volOn){ const vh = vmax ? k.v/vmax*PB*(this.st.vol.h/100) : 0, fm = this.fp.get(k.t);
        if (this.st.vol.delta && fm){ const OFc = this.st.of; c.fillStyle = hexA(fm.b >= fm.s ? OFc.color : OFc.color2, .45); }   // real delta colour when live trades exist
        c.fillRect(x-bwp/2, PB-vh, bwp, vh); }
      c.strokeStyle = col; c.fillStyle = col; c.beginPath(); c.moveTo(Math.round(x)+.5, py(k.h)); c.lineTo(Math.round(x)+.5, py(k.l)); c.stroke();
      const y1 = py(k.o), y2 = py(k.c);
      if (this.fpOn && this.bw >= 44 && this.fp.has(k.t)){ c.lineWidth = 1; c.strokeRect(Math.round(x-bwp/2)+.5, Math.min(y1,y2), bwp, Math.max(1, Math.abs(y1-y2))); }   // footprint candle: body becomes an outline, the cells show the volume
      else c.fillRect(x-bwp/2, Math.min(y1,y2), bwp, Math.max(1, Math.abs(y1-y2)));
    }
    this.maL.forEach((m, j) => {   // Moving averages: every line of the one MA indicator
      const v = this.maV && this.maV[j]; if (!m.on || !v) return;
      c.strokeStyle = m.color; c.lineWidth = DOT ? Math.max(2, (m.w || 1.2)*1.6) : (m.w || 1.2); c.lineCap = DOT ? "round" : "butt"; c.setLineDash(DOT ? [0.1, ds] : m.dash ? m.dash.split(",").map(Number) : []); c.beginPath(); let f = true;
      for (let i = i0; i <= i1; i++){ if (v[i] == null) continue; const y = py(v[i]), x = this.x(i); f ? c.moveTo(x,y) : c.lineTo(x,y); f = false; }
      c.stroke(); c.setLineDash([]); c.lineCap = "butt";
    });
    if (this.ema.vwap && this.vwV){
      const sv = this.st.vwap; c.strokeStyle = sv.color; c.lineWidth = sv.w; c.setLineDash(sv.dash ? sv.dash.split(",").map(Number) : []); c.beginPath();
      for (let i = i0; i <= i1; i++){ const y = py(this.vwV[i]), x = this.x(i); i === i0 ? c.moveTo(x,y) : c.lineTo(x,y); }
      c.stroke(); c.setLineDash([]);
    }
    if (this.bsoOn && this.bbShow) this.paintBB(c, py, dec, i0, i1);
    if (this.volOn && vmax) this.paintDiv(c, "vol", [1], i => this.x(i), i => PB - this.data[i].v/vmax*PB*(this.st.vol.h/100), i0, i1);
    if (this.donOn) this.paintDon(c, py, i0, i1);
    if (this.mt5On) this.paintMt5(c, py, i0, i1);
    if (this.lvOn) this.paintLv(c, py, PR);
    if (this.llOn) this.paintLL(c, py, PR, i0, i1);
    if (this.smtOn) this.paintSmt(c, py, dec, i0, i1);
    this.infoChip(c);
    if (this.ewOn || this.harmOn) this.htfNote(c, 2);   // bigger-timeframe trend, once per paint
    if (this.harmOn) this.paintHarm(c, py, dec);
    if (this.vpOn) this.paintVp(c, py, dec, PR, PB, i0, i1);
    if (this.bvdOn) this.paintBvd(c, py, dec, i0, i1);
    if (this.ewOn) this.paintEWauto(c, py, dec);
    if (this.fpOn || this.deltaOn) this.paintFp(c, py, dec, i0, i1, PB);
    this.paintJournal(c, py, dec);   // journal trades of this symbol: kept on every timeframe, closed ones dimmed (2026-10-19)
    // Large-print bubbles are rendered only inside the dedicated order-flow column.
    if (this.dotOn) this.paintDots(c, py, i0, i1);
    if (this.mkOn) this.paintMk(c, py, PR);
    if (this.domOn && this.colOn) this.paintBal(c, PB, PR);
    const ov = this.showSig ? this.overlay : null;
    if (ov){
      (ov.zones || []).forEach(z => { c.fillStyle = z[2]; c.globalAlpha = .2; c.fillRect(0, py(z[1]), PR, Math.max(2, py(z[0])-py(z[1]))); c.globalAlpha = 1; });
    }
    c.restore(); c.lineWidth = 1;
    if (ov){
      const pl = ov.plan;
      if (pl && this.setupMode === "box"){
        this.paintSetupBox(c, py, pl, dec);
      } else if (pl){
        const lines = [[pl.entry, "Entry", "#4aa3ff", ""], [pl.stop, "SL", "#f6465d", "5,4"]].concat((pl.tps||[]).map((v,i) => [v, "TP"+(i+1), "#0ecb81", "5,4"]));
        const sp = this.planSpan();
        lines.forEach(([v, lab, col, dash]) => {
          const y = py(v); if (y < 0 || y > PB) return;
          c.strokeStyle = col; c.lineWidth = 1; c.setLineDash(dash ? dash.split(",").map(Number) : []); c.beginPath(); c.moveTo(sp.x0, y+.5); c.lineTo(sp.x1, y+.5); c.stroke(); c.setLineDash([]);
          c.fillStyle = col; c.fillRect((this.W-this.axw)+1, y-7, this.axw-2, 14); c.fillStyle = "#000"; c.textAlign = "left"; c.fillText(lab+" "+v.toFixed(dec), (this.W-this.axw)+3, y);
        });
      }
      if (pl){ const sp = this.planSpan(), hy = py(pl.entry); this._planH = {x:sp.x1, y:hy, x0:sp.x0};
        c.fillStyle = "#4aa3ff"; c.strokeStyle = "#0b0e11"; c.lineWidth = 1; c.fillRect(sp.x1-4, hy-6, 8, 12); c.strokeRect(sp.x1-4+.5, hy-6+.5, 7, 11); }
    }
    if (this.showSig && n) this.paintSigs(c, py, PR, PB, ov);
    if (this.flowOn && this.marks.length && n){
      // order-flow lines: sweep (dot) / absorption (small square). The line starts at the CURRENT candle and runs ahead of it
      // (or from the event candle when "Start at event" is chosen); repeats = small ticks, target = dashed path + small arrow.
      const F = this.st.flow, al = this.pulse ? 1 : .45, xNow = this.x(n-1) + this.bw/2, now = (this.data[n-1] || {}).t || Date.now();
      const len = (F.len|0) > 0 ? (F.len|0)*this.bw : PR, ageMs = (F.age|0) > 0 ? (F.age|0)*60000 : Infinity;
      this.marks.filter(m => now - m.t <= ageMs).slice(0, Math.max(1, F.max|0 || 6)).forEach(m => {   // marks are newest first
        let k = -1; for (let i = n-1; i >= 0; i--) if (this.data[i].t <= m.t){ k = i; break; } if (k < 0) k = 0;
        const y = py(m.p); if (y < 0 || y > PB) return;
        const xe = this.x(k), ab = m.kind === "absorb", col = (ab ? F.color2 : F.color) || (ab ? "#b57cff" : "#f0b90b"), up = m.dir > 0;
        // the marker sits on the current candle but never closer than 70 px to the price axis (latest candle at the right edge = the old line was a few px long, i.e. invisible)
        const x0 = Math.max(0, Math.min(F.anchor ? xNow : xe, PR - 70)), x1 = Math.min(PR, Math.max(x0 + 60, x0 + len)), xs = Math.min(x0, Math.max(0, xe));
        c.globalAlpha = al; c.strokeStyle = c.fillStyle = col; c.lineWidth = F.w || 1.5; c.setLineDash(F.dash ? F.dash.split(",").map(Number) : []);
        c.beginPath(); c.moveTo(x0, y); c.lineTo(x1, y); c.stroke(); c.setLineDash([]);
        if (xs < x0 - 4){ c.globalAlpha = .3; c.lineWidth = 1; c.setLineDash([2,3]); c.beginPath(); c.moveTo(xs, y); c.lineTo(x0, y); c.stroke(); c.setLineDash([]); c.lineWidth = F.w || 1.5; }   // faint trail back to the event candle
        c.globalAlpha = .9; c.fillRect(PR + 1, y - 2, 6, 4);   // small tag on the price axis so the level is found even when zoomed out
        if (F.anchor && xe < x0 - 4){ c.globalAlpha = .55; c.fillRect(xe - 1, y - 1, 3, 3); }   // tiny tick where the event actually happened
        c.globalAlpha = 1;
        if (ab){ c.strokeRect(x0 - 3.5, y - 3.5, 7, 7); } else { c.beginPath(); c.arc(x0, y, 3.5, 0, 6.3); c.fill(); }   // marker on the current candle
        c.beginPath(); const ay = y + (up ? -9 : 9); c.moveTo(x0, ay + (up ? -4 : 4)); c.lineTo(x0 - 3, ay + (up ? 2 : -2)); c.lineTo(x0 + 3, ay + (up ? 2 : -2)); c.closePath(); c.fill();   // small direction arrow
        for (let r = 1; r < Math.min(m.n || 1, 6); r++) c.fillRect(x0 + 6 + r*4, y + (up ? 4 : -6), 2, 2);   // repeats: small dots instead of "×n"
        if (m.tgt && F.tgt){ const ty = py(m.tgt);
          if (ty > 0 && ty < PB){ c.globalAlpha = .85; c.setLineDash([2,4]); c.lineWidth = 1; c.beginPath(); c.moveTo(x0, y); c.lineTo(Math.min(x1, x0 + 40), ty); c.lineTo(x1, ty); c.stroke(); c.setLineDash([]);
            c.beginPath(); c.moveTo(x1, ty); c.lineTo(x1 - 6, ty - 3); c.lineTo(x1 - 6, ty + 3); c.closePath(); c.fill(); c.globalAlpha = 1; } }
      });
      c.globalAlpha = 1; c.font = "11px ui-monospace,Menlo,Consolas,monospace";
    }
    if (ov && ov.ew) this.paintEW(c, py, ov.ew, dec);
    this.paintSR(c, py, PB, dec); this.paintDraws(c, py, dec); this.dbar();
    if (this.vpLv){ c.font = "10px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "right"; this.vpLv.forEach(l => { const y = py(l.p); if (y < 0 || y > PB) return;
      const col = l.k === "POC" ? "#f0b90b" : "#4aa3ff"; c.strokeStyle = col; c.globalAlpha = .85; c.lineWidth = l.k === "POC" ? 1.6 : 1; c.setLineDash(l.k === "POC" ? [] : [6,3]); c.beginPath(); c.moveTo(0,y+.5); c.lineTo(PR,y+.5); c.stroke(); c.setLineDash([]); c.globalAlpha = 1; c.lineWidth = 1;
      c.fillStyle = col; c.fillText(l.tf+" "+l.k+" "+l.p.toFixed(dec), PR-4, y-4); }); c.textAlign = "left"; c.font = "11px ui-monospace,Menlo,Consolas,monospace"; }
    if (this.fibLv){ c.font = "10px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "left"; this.fibLv.forEach(l => { const y = py(l.p); if (y < 0 || y > PB) return;
      const col = l.r < 0 ? "#0ecb81" : l.r > 1 ? "#f6465d" : "#f0b90b"; c.strokeStyle = col; c.globalAlpha = .8; c.setLineDash([4,3]); c.beginPath(); c.moveTo(0,y+.5); c.lineTo(PR,y+.5); c.stroke(); c.setLineDash([]); c.globalAlpha = 1;
      c.fillStyle = col; c.fillText(l.r+"  "+l.p.toFixed(dec), 4, y-5); }); c.font = "11px ui-monospace,Menlo,Consolas,monospace"; }
    // last price line
    const last = this.data[n-1], ly = py(last.c), lup = last.c >= last.o, lcol = lup ? TH.up : TH.dn;
    if (ly > 0 && ly < PB){
      c.strokeStyle = lcol; c.setLineDash([3,3]); c.beginPath(); c.moveTo(0,ly+.5); c.lineTo(PR,ly+.5); c.stroke(); c.setLineDash([]);
      c.fillStyle = lcol; c.fillRect((this.W-this.axw)+1, ly-8, this.axw-2, 16); c.fillStyle = "#000"; c.textAlign = "left"; c.fillText(last.c.toFixed(dec), (this.W-this.axw)+5, ly);
      const rem = candleRem(last.t, this.tf), sec = Math.floor(rem/1000), hh = Math.floor(sec/3600), mm = Math.floor(sec%3600/60), ss = sec%60;
      c.fillStyle = "#2b3139"; c.fillRect((this.W-this.axw)+1, ly+9, this.axw-2, 14); c.fillStyle = "#eaecef"; c.fillText("⏱ "+(hh ? hh+":"+pad2(mm)+":"+pad2(ss) : pad2(mm)+":"+pad2(ss)), (this.W-this.axw)+5, ly+16);
    }
    // crosshair + legend
    let show = last;
    if (!this.mouse && XHS.on && XHS.sym === this.sym && XHS.t != null && this.data.length){   // task 52: time from another chart
      let j = this.data.length - 1; while (j > 0 && this.data[j].t > XHS.t) j--; const xs = this.x(j);
      if (xs > 0 && xs < PR){ c.strokeStyle = "#f0b90b"; c.setLineDash([3,3]); c.beginPath(); c.moveTo(xs+.5,0); c.lineTo(xs+.5,H-20); c.stroke(); c.setLineDash([]); } }
    const m = this.mouse;
    if (m && m.x < PR && m.y < H-20){   // vertical line runs through the chart AND every indicator pane down to the time strip
      const ii = Math.max(0, Math.min(n-1, Math.round(this.idx(m.x)))); show = this.data[ii] || last; const inMain = m.y < PB;
      c.strokeStyle = "#5a636e"; c.setLineDash([2,3]); c.beginPath(); c.moveTo(m.x+.5,0); c.lineTo(m.x+.5,H-20); c.moveTo(0,m.y+.5); c.lineTo(PR,m.y+.5); c.stroke(); c.setLineDash([]);
      if (inMain){ c.fillStyle = "#2b3139"; c.fillRect((this.W-this.axw)+1, m.y-8, this.axw-2, 16); c.fillStyle = "#eaecef"; c.textAlign = "left"; c.fillText((lo + (PB-m.y)/PB*(hi-lo)).toFixed(dec), (this.W-this.axw)+5, m.y); }
      const tx = this.x(ii), label = this.fmtTime(this.data[ii].t); const tw = c.measureText(label).width + 10;
      c.fillStyle = "#2b3139"; c.fillRect(tx-tw/2, H-19, tw, 18); c.fillStyle = "#eaecef"; c.textAlign = "center"; c.fillText(label, tx, H-10);
    }
    const chg = show.o ? (show.c-show.o)/show.o*100 : 0, dcol = show.c >= show.o ? TH.up : TH.dn;
    c.textAlign = "left"; c.fillStyle = "#848e9c";
    const txt = "O "+show.o.toFixed(dec)+"  H "+show.h.toFixed(dec)+"  L "+show.l.toFixed(dec)+"  C "+show.c.toFixed(dec)+"  ";
    c.fillText(txt, 8, 10); c.fillStyle = dcol; c.fillText((chg>=0?"+":"")+chg.toFixed(2)+"%", 8+c.measureText(txt).width, 10);
    try { const rg = Regime.now(this.data); if (rg && rg.regime && rg.regime !== "Mixed" && this.W > 330){ const pct = (chg>=0?"+":"")+chg.toFixed(2)+"%", x0 = 8 + c.measureText(txt).width + c.measureText(pct).width + 10; const f0 = c.font; c.fillStyle = Regime.col[rg.regime]; c.font = "bold 9px sans-serif"; c.fillText(rg.regime.toUpperCase(), x0, 10); c.font = f0; } } catch(e){}   // market regime chip (Trend / Chop / Hi-Vol / Crash / Squeeze / Thin) next to the change %: a description of now
    if (this.colOn){ this.paintCol(c, py, PB, PR, i0, i1); this.paintXhCol(c, PR, PB); } else this.placeGroupSel(false);
    this.paintSub(c, PB, i0, i1);
  }
  paintSub(c, PB, i0, i1){
    const subs = this.subActive(); this._panes = [];
    if (!subs.length) return; const PR = this.PR, hsub = this.subHs(), dash = d => d ? d.split(",").map(Number) : [];
    subs.forEach((k, j) => {
      const hE = hsub[j] || 50, y0 = PB + hsub.slice(0, j).reduce((x,y) => x+y, 0), h = hE - 4; this._panes.push({k, y0, h}); c.save(); c.beginPath(); c.rect(0, y0, PR, h); c.clip();
      c.fillStyle = TH.pane; c.fillRect(0, y0, PR, h); c.strokeStyle = TH.grid; c.lineWidth = 1; c.strokeRect(.5, y0+.5, PR-1, h-1);
      if (!this[k+"V"]){ c.restore(); return; }
      c.textAlign = "left"; c.font = "10px ui-monospace,Menlo,Consolas,monospace";
      const PDOT = !!this.dots, pds = Math.max(3, Math.min(6, Math.round(this.bw*0.22)));
      const line = (arr, col, w, ds, y) => { c.strokeStyle = col; c.lineWidth = PDOT ? Math.max(2, w*1.6) : w; c.lineCap = PDOT ? "round" : "butt"; c.setLineDash(PDOT ? [0.1, pds] : ds); c.beginPath(); let on = false;
        for (let i = i0; i <= i1; i++){ const v = arr[i]; if (v == null){ on = false; continue; } const x = this.x(i), yy = y(v); on ? c.lineTo(x, yy) : c.moveTo(x, yy); on = true; } c.stroke(); c.setLineDash([]); c.lineCap = "butt"; };
      const lvl = (v, y, dsh) => { c.strokeStyle = "#3a424b"; c.lineWidth = 1; c.setLineDash(dsh ? [3,3] : []); c.beginPath(); c.moveTo(0, Math.round(y(v))+.5); c.lineTo(PR, Math.round(y(v))+.5); c.stroke(); c.setLineDash([]); };
      const last = a => { for (let i = Math.min(i1, a.length-1); i >= 0; i--) if (a[i] != null) return a[i]; return null; };
      if (k === "adx"){
        const st = this.st.adx, A = this.adxV; let mx = 50; for (let i = i0; i <= i1; i++) mx = Math.max(mx, A.adx[i] || 0, A.pdi[i] || 0, A.mdi[i] || 0); mx = Math.min(100, Math.ceil(mx/10)*10);
        const y = v => y0 + h - 2 - v/mx*(h-4); lvl(st.lvl || 25, y, true); lvl(20, y, true);
        line(A.pdi, TH.up, 1, [], y); line(A.mdi, TH.dn, 1, [], y); line(A.adx, st.color, st.w + .4, dash(st.dash), y);
        c.restore(); const a = last(A.adx), pp = last(A.pdi), mm = last(A.mdi);
        c.fillStyle = "#848e9c"; c.fillText("ADX "+st.len+"  "+(a == null ? "—" : a.toFixed(1))+"  +DI "+(pp == null ? "—" : pp.toFixed(1))+"  -DI "+(mm == null ? "—" : mm.toFixed(1))+"  "+(a == null ? "" : a >= (st.lvl || 25) ? Lg("trend","ترند") + (pp > mm ? " ▲" : " ▼") : a < 20 ? Lg("no trend / range","مفيش ترند / رينج") : Lg("weak","ضعيف")), 6, y0+8);
        c.fillText(String(st.lvl || 25), (this.W-this.axw)+5, y(st.lvl || 25));
      } else if (k === "cci"){
        const st = this.st.cci, V = this.cciV; let mx = 220; for (let i = i0; i <= i1; i++) mx = Math.max(mx, Math.abs(V[i] || 0)); mx *= 1.05;
        const y = v => y0 + h/2 - v/mx*(h/2-3); lvl(0, y, false); [100, -100].forEach(v => lvl(v, y, true)); if (mx > 230) [200, -200].forEach(v => lvl(v, y, true));
        c.globalAlpha = .12; c.fillStyle = "#848e9c"; c.fillRect(0, y(100), PR, y(-100) - y(100)); c.globalAlpha = 1;
        line(V, st.color, st.w, dash(st.dash), y);
        c.restore(); const v = last(V); c.fillStyle = "#848e9c"; c.fillText("CCI "+st.len+"  "+(v == null ? "—" : v.toFixed(0))+(v == null ? "" : v > 100 ? "  "+Lg("above +100","فوق +100") : v < -100 ? "  "+Lg("below -100","تحت -100") : ""), 6, y0+8);
        [100, -100].forEach(q => c.fillText(String(q), (this.W-this.axw)+5, y(q)));
      } else if (k === "rsi"){
        const st = this.st.rsi, y = v => y0 + h - 2 - v/100*(h-4);
        [st.os, 50, st.ob].forEach((v,q) => { c.strokeStyle = q === 1 ? "#1f252b" : "#3a424b"; c.setLineDash(q === 1 ? [] : [3,3]); c.beginPath(); c.moveTo(0,y(v)+.5); c.lineTo(PR,y(v)+.5); c.stroke(); }); c.setLineDash([]);
        c.strokeStyle = st.color; c.lineWidth = st.w; c.setLineDash(dash(st.dash)); c.beginPath();
        for (let i = i0; i <= i1; i++){ const yy = y(this.rsiV[i]), x = this.x(i); i === i0 ? c.moveTo(x,yy) : c.lineTo(x,yy); } c.stroke(); c.setLineDash([]);
        this.paintDiv(c, "rsi", this.rsiV, i => this.x(i), i => y(this.rsiV[i]), i0, i1);
        c.restore(); c.fillStyle = "#848e9c"; c.fillText("RSI "+st.len+"  "+(this.rsiV[Math.min(i1, this.data.length-1)]||0).toFixed(1), 6, y0+8);
        [st.os, st.ob].forEach(v => c.fillText(String(v), (this.W-this.axw)+5, y(v)));
      } else if (k === "macd"){
        const st = this.st.macd, M = this.macdV; let mx = 1e-12; for (let i = i0; i <= i1; i++) mx = Math.max(mx, Math.abs(M.m[i]), Math.abs(M.s[i]), Math.abs(M.h[i]));
        const y = v => y0 + h/2 - v/mx*(h/2-3), bw = Math.max(1, this.bw*0.6);
        c.strokeStyle = "#3a424b"; c.beginPath(); c.moveTo(0,y(0)+.5); c.lineTo(PR,y(0)+.5); c.stroke();
        for (let i = i0; i <= i1; i++){ const v = M.h[i], x = this.x(i); c.fillStyle = v >= 0 ? "rgba(14,203,129,.55)" : "rgba(246,70,93,.55)"; c.fillRect(x-bw/2, Math.min(y(v), y(0)), bw, Math.max(1, Math.abs(y(v)-y(0)))); }
        [[M.m, st.color],[M.s, st.color2]].forEach(([arr,col]) => { c.strokeStyle = col; c.lineWidth = st.w; c.setLineDash(dash(st.dash)); c.beginPath();
          for (let i = i0; i <= i1; i++){ const yy = y(arr[i]), x = this.x(i); i === i0 ? c.moveTo(x,yy) : c.lineTo(x,yy); } c.stroke(); c.setLineDash([]); });
        this.paintDiv(c, "macd", M.m, i => this.x(i), i => y(M.m[i]), i0, i1);
        c.restore(); c.fillStyle = "#848e9c"; c.fillText("MACD "+st.fast+" "+st.slow+" "+st.sig, 6, y0+8);
      } else this.paintX(c, k, y0, h, i0, i1, PR);
      c.font = "11px ui-monospace,Menlo,Consolas,monospace";
    });
    // pane controls: grip (drag the title to reorder), up / down buttons, thin handle on the top edge (drag to resize)
    c.save(); c.textAlign = "center"; c.textBaseline = "middle"; c.font = "10px sans-serif";
    this._panes.forEach((q, j) => { const bx = PR - 36;
      c.fillStyle = "rgba(43,49,57,.9)"; c.fillRect(bx, q.y0 + 3, 15, 13); c.fillRect(bx + 17, q.y0 + 3, 15, 13); c.fillRect(bx - 18, q.y0 + 3, 15, 13);
      c.fillStyle = "#f6465d"; c.fillText("✕", bx - 10.5, q.y0 + 10);   // close this indicator pane
      c.fillStyle = j > 0 ? "#eaecef" : "#5a636e"; c.fillText("▲", bx + 7.5, q.y0 + 10); c.fillStyle = j < this._panes.length-1 ? "#eaecef" : "#5a636e"; c.fillText("▼", bx + 24.5, q.y0 + 10);
      c.fillStyle = "#5a636e"; c.fillRect(Math.round(PR/2) - 14, q.y0 - 3, 28, 3); });
    c.restore();
  }
}


