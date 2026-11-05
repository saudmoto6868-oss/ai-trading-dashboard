/* ---------------- drawing tools (TradingView-style) ---------------- */
Object.assign(CandleChart.prototype, {
  /* order flow: every live trade is added to the candle it belongs to, per price, split into sells (hit the bid) and buys (lifted the ask) */
  fpAdd(r, quiet){
    const d = this.data; if (!d.length || r.t < d[0].t) return; { const idn = +r.id; if (isFinite(idn) && idn > (this._fpMax || 0)) this._fpMax = idn; }
    let i = d.length-1; while (i > 0 && d[i].t > r.t) i--;
    const key = d[i].t; let m = this.fp.get(key); if (!m){ m = {px:new Map(), b:0, s:0}; this.fp.set(key, m); }
    const k = r.p, o = m.px.get(k) || (m.px.set(k, {b:0, s:0}), m.px.get(k));
    if (r.side === "Buy"){ o.b += r.q; m.b += r.q; } else { o.s += r.q; m.s += r.q; }
    if (!quiet){ this.bub.push({t:r.t, p:r.p, q:r.q, side:r.side, tier:r.tier || "normal"}); if (this.bub.length > 500) this.bub.splice(0, 100); }
    if (!quiet) (this.flowT = this.flowT || []).push({t:r.t, p:r.p, q:r.q, side:r.side, tier:r.tier || "normal"}); if (!quiet && this.flowT.length > 4000) this.flowT.splice(0, 800);   // Bookmap column: every print with its own timestamp
    if (this.fp.size > 600){ const ks = [...this.fp.keys()].sort((a,b) => a-b); for (let j = 0; j < 100; j++) this.fp.delete(ks[j]); }
  },
  bkTrack(b){   // limit tracking for the profile: each price level's size is smoothed over snapshots, n = how many polls in a row it stayed; flickering (spoof) orders fade, resting walls build up
    const S = this.bkS = this.bkS || new Map(), seen = new Set(), add = (arr, sd) => (arr || []).forEach(x => { if (!(x.q > 0)) return; seen.add(x.p); const o = S.get(x.p); if (o && o.sd === sd){ o.q = o.q*.7 + x.q*.3; o.n++; } else S.set(x.p, {q:x.q*.3, sd, n:1}); });
    add(b.deep ? b.deep.bids : b.bids, "b"); add(b.deep ? b.deep.asks : b.asks, "a");
    S.forEach((o, p) => { if (!seen.has(p)){ o.q *= .6; o.n = 0; if (o.q < 1e-9 || S.size > 9000) S.delete(p); } }); this.bkN = (this.bkN || 0) + 1;
  },
  bucketBook(bids, asks){   // price levels -> buckets of a stable round step (~0.4 bp of price), summed sizes: one snapshot stays a few hundred numbers even with 2000 levels a side
    let all = bids.concat(asks); if (!all.length) return []; const m0 = all[0].p; all = all.filter(x => Math.abs(x.p - m0) <= m0*0.01); if (!all.length) return []; let mn = Infinity, mx = -Infinity; all.forEach(x => { if (x.p < mn) mn = x.p; if (x.p > mx) mx = x.p; }); const mid = all[0].p, raw = Math.max(mid*0.00004, (mx - mn)/500),   /* only +-1 % of the price counts for the row size: the WIDE book (Hyperliquid +-5 %) made the step 2 USD on gold = 7 chunky rows on the chart (owner 2026-11-05) */ mag = Math.pow(10, Math.floor(Math.log10(raw || 1e-9))), bk = [1,2,5,10].map(x => x*mag).find(x => x >= raw) || raw, g = new Map();
    all.forEach(x => { const k = Math.round(x.p/bk); g.set(k, (g.get(k) || 0) + x.q); }); const out = []; g.forEach((q, k) => out.push([k*bk, q])); this.bk = bk; return out;
  },
  flowDiff(fb){   // a big resting order that shrank between two book snapshots: executed (trades at that price covered it) = "fill", otherwise it was pulled = "pull"
    const n = fb.length; if (n < 2) return; const A = fb[n-2], B = fb[n-1], cur = new Map(B.lv.map(([p, q]) => [p, q])); if (!A.lv.length || !B.lv.length) return;
    let lo = Infinity, hi = -Infinity; B.lv.forEach(([p]) => { if (p < lo) lo = p; if (p > hi) hi = p; });
    const avg = A.lv.reduce((a, x) => a + x[1], 0)/A.lv.length, mid = (B.bb + B.ba)/2, tk = Math.max(1e-12, ...[0].concat(A.lv.length > 1 ? [Math.abs(A.lv[1][0] - A.lv[0][0])] : [])) || 1e-9;
    const T_ = (this.flowT || []).filter(x => x.t >= A.t - 500), E = this.flowE = this.flowE || [];
    A.lv.forEach(([p, q]) => { if (q < 4*avg || p < lo || p > hi) return; const q2 = cur.get(p) || 0, drop = q - q2; if (drop < 0.5*q) return;
      const ex = T_.reduce((a, x) => a + (Math.abs(x.p - p) <= tk*0.6 ? x.q : 0), 0); E.push({t:B.t, p, q:drop, kind:ex >= 0.5*drop ? "fill" : "pull", bid:p <= mid}); });
    if (E.length > 300) E.splice(0, 100);
  },
  zlTick(b, t){   // ZONE FORWARD TEST (ported from feat/orderflow-zonetest, no UI change): a SIDE tracker (it does not touch the heat-map flashes / limits list / sync lights) feeds FlowRead; every confluence zone (2+ sources) is logged and judged by the price path against a control level. Export: chart settings -> "Export zone test log"; judged offline by modules/zone_eval.py. Description, not a signal.
    try { const bids = (b.deep ? b.deep.bids : b.bids) || [], asks = (b.deep ? b.deep.asks : b.asks) || []; if (!bids.length || !asks.length) return; const fr = this.zfr = this.zfr || FlowRead.newState(); fr.big = settings.big; FlowRead.update(fr, {t, bids, asks}, this.flowT || []);
      if (t - (this._zlT || 0) < 600) return; this._zlT = t; const m_ = (bids[0].p + asks[0].p)/2; if (!isFinite(m_) || !m_) return;
      const R = FlowRead.read(fr, {now:t, snap:{t, bids, asks}, trades:(this.flowT || []).filter(x => x.t >= t - 120000), events:(fr.ev || []).slice(), fmtP:v => fmtP(v)}); if (!R) return; this._rd = R;
      const zl = this.zlog = this.zlog || {recs:store.get(LS+"_zlog_"+this.sym, [])}; (R.zones || []).forEach(z => ZoneLog.add(zl, z, m_, t)); ZoneLog.step(zl, m_, t);
      if (t - (this._zlS || 0) > 15000){ this._zlS = t; store.set(LS+"_zlog_"+this.sym, zl.recs); } } catch(e){} },
  domAdd(b){
    if (this.colWide > 0 && this.domOn){ const w = this.wom.snaps, sn = OFM.snap(b, w[w.length-1]); if (sn) OFM.push(w, sn); }   // snapshots for the WIDE order-flow column (Order Flow Map renderer)
    this.lastBook = b; this.zlTick(b, nowS()); this.bkTrack(b); if (this.domOn) { const fb = this.flowB = this.flowB || []; fb.push({t:nowS(), bb:b.bids && b.bids[0] ? b.bids[0].p : 0, ba:b.asks && b.asks[0] ? b.asks[0].p : 0, lv:this.bucketBook((b.deep ? b.deep.bids : b.bids) || [], (b.deep ? b.deep.asks : b.asks) || [])}); if (fb.length > 900) fb.splice(0, 200); this.flowDiff(fb); this.hmAdd(fb[fb.length-1]); }   // Record heatmap history only while the order-flow book layer is enabled
    const d = this.data; if (!d.length) return; const t = d[d.length-1].t; let m = this.dom.get(t); if (!m){ m = new Map(); this.dom.set(t, m); if (this.dom.size > 300){ const ks = [...this.dom.keys()].sort((a,b) => a-b); for (let j = 0; j < 60; j++) this.dom.delete(ks[j]); } }
    (b.bids || []).forEach(x => { const o = m.get(x.p); if (!o || x.q > o.q) m.set(x.p, {q:x.q, side:"b"}); });
    (b.asks || []).forEach(x => { const o = m.get(x.p); if (!o || x.q > o.q) m.set(x.p, {q:x.q, side:"a"}); });
  },
  fspan(now){   // time window of the order-flow column. Manual choice (selector / wheel) wins. AUTO = Bookmap's rolling window: exactly the live book history recorded in this session, capped at 10 min (min 10 s), always anchored to "now" - so the heat map fills the WHOLE column from the first seconds and then scrolls left as new snapshots arrive. Longer windows (1 h .. 7 d from the saved history) are chosen manually.
    if (this.flowSpan) return this.flowSpan; if ((this.st.of.hmm || "fix") !== "fix") return 120000;
    const fb = this.flowB && this.flowB[0], age = fb ? now - fb.t : 0, base = Math.max(10000, Math.min(600000, Math.round(age*1.04)));
    const tfMs = this.secMs(); if (tfMs <= 600000) return base;   // 1m..5m charts: the live window as before
    const rec = this.hmRecorded(now); return Math.max(base, Math.min(tfMs, rec, 7*864e5));   // 15m / 1H / 4H / 1D: show one candle's worth of book history (or everything recorded so far if that is less), not just the last 10 minutes
  },
  hmRecorded(now){   // ms of book history this browser has recorded for the symbol (oldest saved bucket -> now)
    if (!this.hm || this.hmSym !== this.sym){ try { this.hmInit(); } catch(e){ return 0; } } const H = this.hm; if (!H || !H.b.size) return 0;
    if (this._hmOldN !== H.b.size || this._hmOldS !== this.sym){ let m = Infinity; H.b.forEach((o, t) => { if (t < m) m = t; }); this._hmOld = m; this._hmOldN = H.b.size; this._hmOldS = this.sym; }
    return Math.max(0, now - this._hmOld); },
  hmCover(now){ if (!this.hm || this.hmSym !== this.sym){ try { this.hmInit(); } catch(e){ return null; } } const H = this.hm; if (!H || !H.b.size) return null; const it = []; H.b.forEach((o, t) => it.push([t, o.w || 60000])); return FPS.cover(it, now, 4*60000); },   // holes = times the app was closed
  hmInit(){   // fixed-grid order-book history (Bookmap style): absolute price rows x absolute time buckets, saved in the browser so it keeps growing across sessions
    if (this.hmSym === this.sym && this.hm) return; this.hmSym = this.sym; this.hm = {step:0, b:new Map()}; this._hmSv = nowS();
    // Load the existing local history without deleting it just because it is large.
    // Keep parsing guarded; corrupted data is ignored but never automatically removed.
    let raw = null; try { raw = localStorage.getItem(LS+"_hm_"+this.sym); } catch(e){}
    const s = raw ? (() => { try { return JSON.parse(raw); } catch(e){ return null; } })() : null, cut = nowS() - 7*86400e3;
    if (s && s.step && s.b){ this.hm.step = s.step; Object.keys(s.b).forEach(k => { if (+k < cut) return; const o = s.b[k]; this.hm.b.set(+k, {w:o.w, m:o.m, c:new Map(o.c)}); }); }
    { const H = this.hm, sym = this.sym; FPS.getHm(sym).then(o => { if (this.hm !== H || !o) return; if (FPS.hmMerge(H, o, cut)){ this._hmOldN = null; this._hmMerge = null; this._hmIdb = sym; this.draw(); } else if (o.step) this._hmIdb = sym; }); }   // older history saved in IndexedDB joins what localStorage had
  },
  hmAdd(sn){
    this.hmInit(); const H = this.hm, mid = (sn.bb + sn.ba)/2; if (!sn.lv.length || !mid) return;
    if (!H.step){ const raw = Math.max(mid*0.0001, this.bk || 0), mag = Math.pow(10, Math.floor(Math.log10(raw))); H.step = [1,2,2.5,5,10].map(x => x*mag).find(x => x >= raw) || raw; }
    const tb = Math.floor(sn.t/60000)*60000; let o = H.b.get(tb); if (!o){ o = {w:60000, m:mid, c:new Map()}; H.b.set(tb, o); } o.m = mid;
    sn.lv.forEach(([p, q]) => { const k = Math.round(p/H.step), v = o.c.get(k); if (v == null || q > v) o.c.set(k, q); });
    if (sn.t - this._hmSv > 120000){ this._hmSv = sn.t; const go = () => this.hmSave(sn.t); if (window.requestIdleCallback) requestIdleCallback(go, {timeout:8000}); else setTimeout(go, 50); }   // was 30 s: compaction + JSON.stringify of up to 1.4 MB + a synchronous localStorage write per chart is a visible main-thread stall
  },
  hmSave(now){   // compact (older than 3 h -> 5 min buckets, keep the biggest walls only), keep 7 days, write to localStorage
    this._hmSv = now; const H = this.hm; if (!H) return; const nb = new Map();
    [...H.b.keys()].sort((a, b) => a - b).forEach(t => { if (t < now - 7*86400e3) return; const o = H.b.get(t), old = t < now - 3*3600e3, w = old ? 300000 : 60000, tb = Math.floor(t/w)*w; let n = nb.get(tb); if (!n){ n = {w, m:o.m, c:new Map()}; nb.set(tb, n); } n.m = o.m; o.c.forEach((q, k) => { const v = n.c.get(k); if (v == null || q > v) n.c.set(k, q); }); });
    nb.forEach(o => { const lim = o.w > 60000 ? 40 : 150; if (o.c.size > lim){ const top = [...o.c.entries()].sort((a, b) => b[1] - a[1]).slice(0, lim); o.c = new Map(top); } }); H.b = nb;
    const pack = () => { const b = {}; nb.forEach((o, t) => { if (t >= now - 7*86400e3) b[t] = {w:o.w, m:+o.m.toPrecision(7), c:[...o.c.entries()].map(([k, q]) => [k, +q.toPrecision(4)])}; }); return {step:H.step, b}; };  // fix: save all buckets within 7-day window (prev condition skipped 1-3h minute-resolution buckets)
    try {
      const j = pack(), sym = this.sym, wasIdb = this._hmIdb === sym;   // IndexedDB first (no 5 MB shared quota); the localStorage copy is removed only after IndexedDB confirmed the write
      FPS.putHm(sym, wasIdb ? j : JSON.parse(JSON.stringify(j))).then(ok => { if (ok){ this._hmIdb = sym; try { localStorage.removeItem(LS+"_hm_"+sym); } catch(e){} } else if (this._hmIdb === sym) this._hmIdb = null; });
      if (wasIdb) return;   // already in IndexedDB: skip the old capped localStorage write
      let txt = JSON.stringify(j);
      // If storage is tight, prune oldest buckets in small batches; preserve recent history
      // and never delete another symbol's history as a side effect of this save.
      const ks = () => Object.keys(j.b).map(Number).sort((a, b) => a - b);
      let keys = ks(), cutCount = 0;
      while (txt.length > 1400000 && keys.length > 24 && cutCount < 12) {
        const removeCount = Math.max(1, Math.ceil(keys.length * 0.08));
        for (let i = 0; i < removeCount && keys.length; i++) delete j.b[keys.shift()];
        cutCount++;
        txt = JSON.stringify(j);
      }
      // QuotaExceeded (all symbols + the rest of the app share ~5 MB): do not give up silently (history would stop growing for good): drop the oldest 30 % and retry, up to 8 times; other symbols' keys are never touched
      for (let tries = 0; ; tries++){
        try { localStorage.setItem(LS+"_hm_"+this.sym, txt); break; }
        catch(e){ if (tries >= 8 || keys.length <= 12) break; const rm = Math.max(1, Math.ceil(keys.length*0.3)); for (let i = 0; i < rm && keys.length; i++) delete j.b[keys.shift()]; txt = JSON.stringify(j); }
      }
    } catch(e) {
      // JSON / storage unavailable: keep every existing localStorage key intact.
    }
  },
  paintHeatCol(c, py, PB, tx, gx0, gx1, tL, tR){   // fixed heat map inside the order-flow column: cells are pinned to their real price and real time (saved history, up to 7 days subject to browser storage); the column only chooses how much time it shows
    const H = this.hm; if (!H || !H.step || !H.b.size) return null; const OF = this.st.of, scheme = OF.hm || "book", lo = this._lo, hi = this._hi, mult = this.ofStepNow() > 0 ? Math.max(1, Math.round(this.ofStepNow()/H.step)) : Math.max(1, Math.ceil((hi - lo)/Math.max(1, PB/5)/H.step)), sR = mult*H.step, rowH = Math.max(1.5, Math.abs(py(0) - py(sR)));
    const ramps = {book:[[0,[1,3,8]],[.25,[20,70,190]],[.5,[20,190,210]],[.7,[240,220,40]],[.88,[245,120,30]],[1,[255,250,235]]], magma:[[0,[5,4,18]],[.3,[75,25,110]],[.58,[190,45,95]],[.8,[255,135,55]],[1,[255,245,180]]], ice:[[0,[2,12,25]],[.3,[10,75,120]],[.6,[45,190,210]],[.82,[180,240,245]],[1,[255,255,255]]], emerald:[[0,[2,15,10]],[.3,[0,90,60]],[.6,[20,190,110]],[.82,[180,235,70]],[1,[255,250,210]]]}, RAMP = ramps[scheme] || ramps.book, bright = Math.max(.25, Math.min(1.75, Number(OF.hmBright) || 1)); const colorAt = (t, price, mid) => { if (scheme === "side") return hexA(price <= mid ? OF.color : OF.color2, .1 + .85*t); if (scheme === "amber") return "rgba(255,"+Math.round(190 + 65*t*t)+","+Math.round(30 + 210*t*t*t)+","+(.1 + .85*t).toFixed(2)+")"; if (scheme === "custom") return hmMix(t, hexRgb(OF.hmLo || "#010308"), hexRgb(OF.hmHi || "#fff5fa")); for (let q = 1; q < RAMP.length; q++){ if (t <= RAMP[q][0]){ const a = RAMP[q-1], b = RAMP[q], u = (t-a[0])/(b[0]-a[0] || 1); return "rgb("+Math.round(a[1][0]+(b[1][0]-a[1][0])*u)+","+Math.round(a[1][1]+(b[1][1]-a[1][1])*u)+","+Math.round(a[1][2]+(b[1][2]-a[1][2])*u)+")"; } } return "rgb(255,250,235)"; };
    const bs = []; H.b.forEach((o, t) => { if (t + o.w >= tL && t <= tR) bs.push([t, o]); }); if (!bs.length) return null; bs.sort((a, b) => a[0] - b[0]);
    let mx = 0; bs.forEach(([t, o]) => { if (o._mu !== mult){ const r = new Map(); o.c.forEach((q, k) => { const kr = Math.floor(k/mult), v = r.get(kr); if (v == null || q > v) r.set(kr, q); }); o._r = r; o._mu = mult; let m = 0; r.forEach(q => { if (q > m) m = q; }); o._mx = m; } if (o._mx > mx) mx = o._mx; });
    // more time buckets than ~2 px columns (a long window): merge them per pixel column (max per row), cached while the window stands still.
    // Drawing every 1-minute bucket of a day was ~140k rectangles every 300 ms and froze the page (owner, 2026-10-17).
    let cols = bs; const maxC = Math.max(20, Math.floor((gx1 - gx0)/2));
    if (bs.length > maxC){ const key = [bs.length, bs[0][0], bs[bs.length-1][0], mult, Math.round(gx0), Math.round(gx1), Math.round(tL/1000)].join("|");
      if (this._hmMerge && this._hmMerge.key === key) cols = this._hmMerge.cols;
      else { const by = new Map(); bs.forEach(([t, o]) => { const ci = Math.floor((tx(t) - gx0)/2); let m = by.get(ci); if (!m){ m = {t, w:0, m:o.m, _r:new Map()}; by.set(ci, m); }
          m.w = Math.max(m.w, t + o.w - m.t); m.m = o.m; o._r.forEach((q, kr) => { const v = m._r.get(kr); if (v == null || q > v) m._r.set(kr, q); }); });
        cols = [...by.values()].map(m => [m.t, m]); this._hmMerge = {key, cols}; } }
    const HDOT = !!this.dots, hp = 4, hdots = HDOT ? new Map() : null;   // dot theme: each ~4px grid cell gets one dot (strongest cell wins), radius follows intensity
    cols.forEach(([t, o]) => { const x0 = Math.max(gx0, tx(t)), x1 = Math.min(gx1, tx(t + o.w)); if (x1 < gx0 || x0 > gx1) return; const w = Math.max(1.2, x1 - x0 + .6);
      o._r.forEach((q, kr) => { const pr = (kr + .5)*sR, y = py(pr); if (y < -rowH || y > PB + rowH) return; const rawT = Math.min(1, Math.pow(q/(mx || 1), .5)*(OF.dom || 1)), t = Math.min(1, Math.pow(rawT, 1/bright)); if (t < .04) return;
        if (HDOT){ const gi = Math.floor(((x0 + x1)/2 - gx0)/hp), gj = Math.floor(y/hp), k = gi*100003 + gj, e = hdots.get(k); if (!e || e.t < t) hdots.set(k, {t, x:gx0 + (gi+.5)*hp, y:(gj+.5)*hp, f:colorAt(t, pr, o.m)}); return; }
        c.fillStyle = colorAt(t, pr, o.m); c.fillRect(x0, y - rowH/2, w, rowH + .5); }); });
    if (HDOT){ hdots.forEach(e => { c.fillStyle = e.f; c.beginPath(); c.arc(e.x, e.y, .6 + 1.5*e.t, 0, 6.2832); c.fill(); }); }
    return bs[0][0];
  },
  paintSigs(c, py, PR, PB, ov){   // BUY/SELL arrows: live scanner signal on the last candle + past journal signals for this symbol
    const d = this.data, n = d.length, sm = this.secMs(), list = this.sigs.slice(); c.font = "bold 10px sans-serif"; c.textAlign = "center";
    if (ov && ov.dir){ list.push({t:d[n-1].t, dir:ov.dir, pct:Math.round(100*ov.score/Math.max(1,ov.max)), tfk:ov.tf || this.tf, live:true}); }
    list.sort((a, b) => a.t - b.t); const lastK = {bullish:-1e18, bearish:-1e18}, GAP = 8*sm;   // thin out: at most one marker per side every 8 candles (live one always shown)
    const shown = list.filter(s => { if (s.live) return true; if (s.t - lastK[s.dir] < GAP) return false; lastK[s.dir] = s.t; return true; });
    shown.forEach(s => {
      if (s.t < d[0].t - sm) return; let k = -1; for (let i = n-1; i >= 0; i--) if (d[i].t <= s.t){ k = i; break; } if (k < 0) return;
      const long_ = s.dir === "bullish", x = this.x(k), col = long_ ? "#0ecb81" : "#f6465d", y = long_ ? py(d[k].l) + 26 : py(d[k].h) - 26; if (y < 4 || y > PB - 4 || x < 0 || x > PR) return;
      c.fillStyle = col; c.strokeStyle = s.status === "tp" ? "#ffffff" : s.status === "sl" ? "#848e9c" : col; c.lineWidth = s.live ? 2 : 1;
      const sz = s.live ? 6 : 4.5, mo = this.mouse, hot = !!mo && Math.abs(mo.x - x) <= 9 && Math.abs(mo.y - y) <= 12; c.beginPath(); c.arc(x, y, hot ? sz+1 : sz-.5, 0, 6.3); c.fill(); c.stroke(); c.fillStyle = "#0b0e11"; c.beginPath(); c.arc(x, y, 1.4, 0, 6.3); c.fill(); c.fillStyle = col;
      const lab = (long_ ? "BUY " : "SELL ") + (s.pct != null ? s.pct+"% " : "") + (s.tfk || "") + (s.status === "tp" ? " ✓" : s.status === "sl" ? " ✗" : "");
      if (!hot){ c.globalAlpha = 1; return; }   // name + strength only while the pointer is on the marker
      const w = c.measureText(lab).width + 8, ly = long_ ? y + sz + 10 : y - sz - 10; c.fillStyle = col; c.globalAlpha = s.live ? 1 : .8; c.fillRect(x-w/2, ly-7, w, 13); c.globalAlpha = 1; c.fillStyle = "#0b0e11"; c.fillText(lab, x, ly);
    });
    c.textAlign = "left"; c.font = "11px ui-monospace,Menlo,Consolas,monospace";
  },
  paintDots(c, py, i0, i1){   // sweep = diamond, absorption = ring + cross; colour = same buy/sell colours as bubbles, DOM and the tape
    const OF = this.st.of, d = this.data; c.save(); c.font = "bold 9px sans-serif"; c.textAlign = "left"; c.textBaseline = "middle";
    this.marks.forEach(m => { let i = d.length-1; while (i > 0 && d[i].t > m.t) i--; if (i < i0 || i > i1) return;
      const x = this.x(i), y = py(m.p), side = m.dir > 0 ? OF.color : OF.color2, col = OF.sidec ? side : (m.kind === "sweep" ? OF.sweepC : OF.absC); c.strokeStyle = col; c.fillStyle = col; c.lineWidth = 2;
      if (m.kind === "sweep"){ c.beginPath(); c.arc(x, y, 3.5, 0, 6.3); c.fill(); if (m.n > 1){ c.fillStyle = "#eaecef"; c.fillText("×"+m.n, x+7, y); } }   // sweep = a small dot only (no word)
      else { c.beginPath(); c.arc(x, y, 8, 0, 6.3); c.stroke(); c.lineWidth = 1.5; c.beginPath(); c.moveTo(x-4, y-4); c.lineTo(x+4, y+4); c.moveTo(x+4, y-4); c.lineTo(x-4, y+4); c.stroke(); if (m.n > 1){ c.fillStyle = "#eaecef"; c.fillText("×"+m.n, x+11, y); }
        if (m.tgt){ const ty = py(m.tgt); c.setLineDash([3,3]); c.lineWidth = 1; c.strokeStyle = col; c.beginPath(); c.moveTo(x, y); c.lineTo(x+40, ty); c.stroke(); c.setLineDash([]); c.fillStyle = col; c.beginPath(); c.arc(x+40, ty, 3, 0, 6.3); c.fill(); } } });
    c.restore();
  },
  paintBvd(c, py, dec, i0, i1){   // Breakout Volume Delta: close through a confirmed swing high/low, labelled with who was stronger inside the breakout bar
    const d = this.data, n = d.length, N = 5, OF = this.st.of; if (n < 2*N+3) return;
    const sw = [];
    for (let i = N; i < n-N; i++){ let hh = true, ll = true; for (let k = i-N; k <= i+N; k++){ if (k === i) continue; if (d[k].h >= d[i].h) hh = false; if (d[k].l <= d[i].l) ll = false; } if (hh) sw.push({i, p:d[i].h, up:true}); if (ll) sw.push({i, p:d[i].l, up:false}); }
    c.save(); c.font = "bold 10px sans-serif"; c.textBaseline = "middle";
    sw.forEach(w => { let k = -1; for (let j = w.i+N+1; j < n; j++){ if (w.up ? d[j].c > w.p : d[j].c < w.p){ k = j; break; } if (w.up ? d[j].h > w.p*1.5 : false) break; }
      if (k < i0 || k > i1 || k < 0) return;
      const m = this.fp.get(d[k].t), rng = (d[k].h - d[k].l) || 1e-9; let buy, real = false;
      if (m && m.b + m.s > 0){ buy = m.b/(m.b+m.s); real = true; } else buy = (d[k].c - d[k].l)/rng;   // real delta from live trades when we have them, otherwise close position inside the bar
      const bull = w.up, good = bull ? buy >= .55 : buy <= .45, pct = Math.round((bull ? buy : 1-buy)*100), col = good ? (bull ? OF.color : OF.color2) : "#848e9c", x0 = this.x(w.i), x1 = this.x(k), y = py(w.p);
      if (!good || (!real && pct < 70)) return;   // weak breakouts and guessed (~) labels below 70% stay hidden
      const txt = (bull ? "▲ BUY " : "▼ SELL ")+pct+"%"+(real ? "" : "~"), ty = py(bull ? d[k].l : d[k].h) + (bull ? 26 : -26), mo = this.mouse, hot = !!mo && Math.abs(mo.x - x1) <= 8 && Math.abs(mo.y - ty) <= 10, s5 = hot ? 6 : 4.5;
      c.fillStyle = hexA(col, hot ? 1 : .9); c.strokeStyle = "#0b0e11"; c.lineWidth = 1.5; c.beginPath(); c.arc(x1, ty, s5-.5, 0, 6.3); c.fill(); c.stroke(); c.fillStyle = "#0b0e11"; c.beginPath(); c.arc(x1, ty, 1.4, 0, 6.3); c.fill();   // round dot (not a triangle, so it never reads as a fractal arrow)
      if (hot){   // strength shows only while the pointer is on the marker
        c.strokeStyle = col; c.globalAlpha = .7; c.setLineDash([4,3]); c.lineWidth = 1; c.beginPath(); c.moveTo(x0, y); c.lineTo(x1, y); c.stroke(); c.setLineDash([]); c.globalAlpha = 1;
        const tw = c.measureText(txt).width+8, ly = ty + (bull ? 18 : -18); c.fillStyle = hexA(col, .95); c.fillRect(x1-tw/2, ly-8, tw, 16); c.fillStyle = "#0b0e11"; c.textAlign = "center"; c.fillText(txt, x1, ly); } });
    c.restore();
  },
  paintBal(c, PB, PR){   // ATAS-style vertical bid/ask balance bar (resting book): ask on top (sell colour), bid below (buy colour)
    const b = this.lastBook; if (!b || !b.bids || !b.asks) return; const OF = this.st.of, sb = b.bids.reduce((a,x) => a+x.q, 0), sa = b.asks.reduce((a,x) => a+x.q, 0), tot = sb+sa; if (!tot) return;
    const x = PR-12, w = 9, ha = PB*sa/tot; c.fillStyle = hexA(OF.color2, .8); c.fillRect(x, 0, w, ha); c.fillStyle = hexA(OF.color, .8); c.fillRect(x, ha, w, PB-ha);
    c.fillStyle = "#0b0e11"; c.fillRect(x, ha-1, w, 2); c.font = "bold 9px sans-serif"; c.textAlign = "right"; c.fillStyle = "#eaecef"; c.fillText("A "+Math.round(100*sa/tot)+"%", x-3, 10); c.fillText("B "+Math.round(100*sb/tot)+"%", x-3, PB-8); c.textAlign = "left";
  },
  paintMk(c, py, PR){   // small BUY / SELL badge at the entry with its target
    const ov = this.overlay, pl = ov && ov.plan; if (!pl || !this.data.length) return; const OF = this.st.of, long_ = (pl.tps && pl.tps[0] || 0) > pl.entry, col = long_ ? OF.color : OF.color2, x = this.x(this.data.length-1) + 14, y = py(pl.entry), dc = pl.entry >= 100 ? 2 : pl.entry >= 1 ? 4 : 6;
    c.fillStyle = col; c.beginPath(); long_ ? (c.moveTo(x, y-6), c.lineTo(x-6, y+5), c.lineTo(x+6, y+5)) : (c.moveTo(x, y+6), c.lineTo(x-6, y-5), c.lineTo(x+6, y-5)); c.closePath(); c.fill();
    c.font = "bold 10px sans-serif"; c.textAlign = "left"; c.textBaseline = "middle"; c.fillText((long_ ? "BUY " : "SELL ")+pl.entry.toFixed(dc), x+9, y);
    (pl.tps || []).slice(0, 3).forEach((v, n) => { const ty = py(v); c.fillStyle = col; c.beginPath(); c.arc(x, ty, 3, 0, 6.3); c.fill(); c.fillText("TP"+(n+1)+" "+v.toFixed(dc), x+9, ty); });
    c.fillStyle = "#f6465d"; c.beginPath(); c.arc(x, py(pl.stop), 3, 0, 6.3); c.fill(); c.fillText("SL "+pl.stop.toFixed(dc), x+9, py(pl.stop));
  },
  flowLevels(ft){   // ft = first touch: ignore the current bar, so a level the price is reaching right now still counts as untouched. Footprint levels price has not traded back into yet (naked POC, stacked imbalance zones) over the last 40 bars: shared with the DOM, tape and limit tracker
    const now = performance.now(), ck = ft ? "_flF" : "_flC"; if (this[ck] && now - this[ck].t < 1000) return this[ck].v; const out = [], d = this.data, step = this._fpStep, OF = this.st.of;
    if (step && d.length && this.fpOn){ for (let i = Math.max(0, d.length - 41); i < d.length; i++){ const m = this.fp.get(d[i].t); if (!m || !m.px.size) continue;
        const rows = new Map(); m.px.forEach((v, p) => { const k = Math.round(p/step); const o = rows.get(k) || (rows.set(k, {b:0, s:0}), rows.get(k)); o.b += v.b; o.s += v.s; });
        const an = this.fpAn(m, rows, step, OF), touched = (lo, hi) => { for (let j = i + 1; j < (ft ? d.length - 1 : d.length); j++) if (d[j].l <= hi && d[j].h >= lo) return true; return false; };
        if (OF.fpNaked !== 0 && an.poc != null && i < d.length - 1){ const pp = an.poc*step; if (!touched(pp - step/2, pp + step/2)) out.push({kind:"npoc", lo:pp, hi:pp, t:d[i].t}); }
        if (OF.fpStack !== 0) an.runs.forEach(rn => { const lo = (rn.k0 - .5)*step, hi = (rn.k1 + .5)*step; if (!touched(lo, hi)) out.push({kind:"stack", side:rn.side, lo, hi, t:d[i].t}); }); } }
    this[ck] = {t:now, v:out}; return out; },
  fpAn(m, rows, step, OF){   // rule-based reading of one footprint bar (descriptions only): diagonal imbalances, stacked runs, POC, unfinished extremes
    const R = OF.fpImb || 3, MS = OF.fpStk || 3, ck = [step, R, MS, OF.fpMin || 0, OF.fpDiag, m.b + m.s, rows.size].join("|"); if (m._an && m._ck === ck) return m._an;
    const ks = [...rows.keys()].sort((a, b) => a - b), tot = ks.reduce((a, k) => a + rows.get(k).b + rows.get(k).s, 0), minV = (OF.fpMin || 0)/100*(tot/Math.max(1, ks.length));
    const imb = new Map(), ZERO = {b:0, s:0}, g = k => rows.get(k) || ZERO; let poc = null, mx = 0;   // an empty neighbouring row counts as zero volume (like the other footprint tools): a lone row of buyers is an unopposed imbalance, the minimum-volume filter removes the thin ones
    ks.forEach(k => { const v = rows.get(k), t = v.b + v.s; if (t > mx){ mx = t; poc = k; } });
    ks.forEach(k => { const v = rows.get(k), dn = g(k - 1), up = g(k + 1);
      if (OF.fpDiag === 0){ if (v.b > R*Math.max(v.s, 1e-12) && v.b > minV) imb.set(k, "b"); else if (v.s > R*Math.max(v.b, 1e-12) && v.s > minV) imb.set(k, "s"); return; }
      if (dn && v.b > R*dn.s && v.b > minV) imb.set(k, "b");   // buyers at this row against the sellers one row below (diagonal)
      else if (up && v.s > R*up.b && v.s > minV) imb.set(k, "s"); });   // sellers at this row against the buyers one row above
    const runs = []; let cur = null; ks.forEach((k, j) => { const sd = imb.get(k);
      if (sd && cur && cur.side === sd && k === cur.k1 + 1){ cur.k1 = k; } else { if (cur && cur.k1 - cur.k0 + 1 >= MS) runs.push(cur); cur = sd ? {side:sd, k0:k, k1:k} : null; } });
    if (cur && cur.k1 - cur.k0 + 1 >= MS) runs.push(cur);
    const hi = ks.length ? rows.get(ks[ks.length - 1]) : null, lo = ks.length ? rows.get(ks[0]) : null;
    m._ck = ck; return (m._an = {imb, runs, poc, hiK:ks[ks.length - 1], loK:ks[0], hiUnf:!!(hi && hi.b > 0 && hi.s > 0), loUnf:!!(lo && lo.b > 0 && lo.s > 0)});
  },
  vaOf(rows, pct){   // value area of one bar: from the POC row, add the side (two rows up or two rows down) with more volume until pct of the bar's volume is inside; returns {poc, vah, val} as row keys
    let k0 = Infinity, k1 = -Infinity, tot = 0, poc = null, mx = 0; rows.forEach((v, k) => { const t = v.b + v.s; tot += t; k0 = Math.min(k0, k); k1 = Math.max(k1, k); if (t > mx){ mx = t; poc = k; } });
    if (poc == null || tot <= 0) return null; const vol = k => { const v = rows.get(k); return v ? v.b + v.s : 0; };
    let lo = poc, hi = poc, acc = vol(poc); while (acc < tot*pct && (lo > k0 || hi < k1)){ const up = hi < k1 ? vol(hi + 1) + (hi + 1 < k1 ? vol(hi + 2) : 0) : -1, dn = lo > k0 ? vol(lo - 1) + (lo - 1 > k0 ? vol(lo - 2) : 0) : -1;
      if (up >= dn){ acc += vol(hi + 1) + (hi + 1 < k1 ? vol(hi + 2) : 0); hi = Math.min(k1, hi + 2); } else { acc += vol(lo - 1) + (lo - 1 > k0 ? vol(lo - 2) : 0); lo = Math.max(k0, lo - 2); } }
    return {poc, vah:hi, val:lo}; },
  cvdAn(d, fp, N){   // cumulative delta over the bars that have footprint data, and divergences on CLOSED bars: price makes a new N-bar extreme but CVD does not confirm it (a description of the past N bars, not a forecast)
    const cvd = new Array(d.length).fill(null), div = []; let acc = 0, seen = false;
    for (let i = 0; i < d.length; i++){ const m = fp.get(d[i].t); if (!m) continue; acc += m.b - m.s; cvd[i] = acc; seen = true; }
    if (!seen) return {cvd, div};
    for (let i = N; i < d.length - 1; i++){ if (cvd[i] == null) continue; let hh = -Infinity, ll = Infinity, ch = -Infinity, cl = Infinity, n = 0;
      for (let j = i - N; j < i; j++){ hh = Math.max(hh, d[j].h); ll = Math.min(ll, d[j].l); if (cvd[j] != null){ ch = Math.max(ch, cvd[j]); cl = Math.min(cl, cvd[j]); n++; } }
      if (n < N/2) continue;
      if (d[i].h > hh && cvd[i] < ch) div.push({i, side:"bear"}); else if (d[i].l < ll && cvd[i] > cl) div.push({i, side:"bull"}); }
    return {cvd, div}; },
  paintFp(c, py, dec, i0, i1, PB){
    const bw = this.bw, d = this.data, fmt = v => v >= 1000 ? (v/1000).toFixed(1)+"k" : v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v.toFixed(2);
    const big = this.fpOn && bw >= 44, mid = bw >= 20, fs = Math.max(9, Math.min(15, Math.round(bw/9)));
    if (this.fpOn && this.fpCov){ c.save(); c.fillStyle = "rgba(139,141,152,.9)"; c.textAlign = "left"; c.font = "10px sans-serif"; const dt = new Date(this.fpCov), z = n => String(n).padStart(2, "0");
      c.fillText(Lg("Footprint recorded without gaps since ", "الفوت برينت مسجّل بلا فجوات منذ ") + z(dt.getDate()) + "/" + z(dt.getMonth()+1) + " " + z(dt.getHours()) + ":" + z(dt.getMinutes()), 8, this.PB - 6); c.restore(); }
    // price step of one footprint row ~ 11px tall
    const lo = this._lo, hi = this._hi, rowPx = fs+3, raw = (hi-lo)/Math.max(1, PB/rowPx), mag = Math.pow(10, Math.floor(Math.log10(raw || 1))), step0 = [1,2,2.5,5,10].map(x => x*mag).find(x => x >= raw) || raw;
    const OF = this.st.of, FM = OF.fpMode || "bidask", step = step0*(OF.fpRow || 1); this._fpStep = step; c.save(); c.textBaseline = "middle"; c.font = fs+"px ui-monospace,Menlo,Consolas,monospace";
    const FB = OF.fpBuy || OF.color, FS = OF.fpSell || OF.color2;   // footprint colours: own override, else the Depth-of-Trade buy / sell colours (added 2026-10-19)
    const BO = 20, brk = i => { if (i < BO) return 0; let hh = -Infinity, ll = Infinity; for (let j = i-BO; j < i; j++){ hh = Math.max(hh, d[j].h); ll = Math.min(ll, d[j].l); } return d[i].c > hh ? 1 : d[i].c < ll ? -1 : 0; };   // closed beyond the previous 20-bar range
    for (let i = i0; i <= i1; i++){
      const cd = d[i], m = this.fp.get(cd.t), bk = brk(i), isBo = bk !== 0 && brk(i-1) !== bk;   // only the FIRST candle of a breakout is marked
      if (isBo){   // the breakout candle: its body shows the buy / sell split (green = buyers, red = sellers), a small plain text under it gives the ratio
        const rg = cd.h - cd.l, est = !m, b_ = m ? m.b : (rg > 0 ? (cd.c - cd.l)/rg : .5), s_ = m ? m.s : 1 - b_, tot = (b_ + s_) || 1, bp = b_/tot, x_ = this.x(i), bwid = Math.max(5, bw*0.8), yT = Math.min(py(cd.o), py(cd.c)), yB = Math.max(py(cd.o), py(cd.c)), hB = Math.max(8, yB - yT), yT2 = yT - (hB - (yB - yT))/2;
        c.fillStyle = FS; c.fillRect(x_ - bwid/2, yT2, bwid, hB*(1 - bp)); c.fillStyle = FB; c.fillRect(x_ - bwid/2, yT2 + hB*(1 - bp), bwid, hB*bp);
        c.strokeStyle = bk > 0 ? FB : FS; c.lineWidth = 1.2; c.strokeRect(x_ - bwid/2 + .5, yT2 + .5, bwid - 1, hB - 1); c.lineWidth = 1;
        if (bw >= 14){ const bps = Math.round(bp*100), tx = (est ? "~" : "")+Lg("Buy ", "شراء ")+bps+"% · "+Lg("Sell ", "بيع ")+(100 - bps)+"%"; c.font = "bold 10px sans-serif"; c.textAlign = "center"; c.fillStyle = bp >= .5 ? FB : FS; c.fillText(tx, x_, Math.min(PB - 6, py(cd.l) + 12)); c.font = fs+"px ui-monospace,Menlo,Consolas,monospace"; } }
      if (!m) continue; const x = this.x(i), w = Math.max(6, bw-3), delta = m.b - m.s, dcol = delta >= 0 ? FB : FS;
      if (m.part && this.fpOn && big){ c.fillStyle = "#f0b90b"; c.textAlign = "center"; c.font = "9px sans-serif"; c.fillText(Lg("partial", "جزئي"), x, Math.max(8, py(cd.h) - 8)); c.font = fs + "px ui-monospace,Menlo,Consolas,monospace"; }
      if (OF.fpDelta !== 0 && this.fpOn && big){ c.fillStyle = dcol; c.textAlign = "center"; c.font = "bold " + Math.max(9, fs - 1) + "px ui-monospace,Menlo,Consolas,monospace"; c.fillText("Δ " + (delta >= 0 ? "+" : "−") + fmt(Math.abs(delta)), x, Math.min(PB - 5, py(cd.l) + (isBo ? 26 : 13))); c.font = fs + "px ui-monospace,Menlo,Consolas,monospace"; }
      if (this.fpOn && (big || mid)){
        const rows = new Map(); m.px.forEach((v, p) => { const k = Math.round(p/step); const o = rows.get(k) || (rows.set(k, {b:0, s:0}), rows.get(k)); o.b += v.b; o.s += v.s; });
        let mx = 0, poc = null; rows.forEach((v, k) => { const t = v.b + v.s; if (t > mx){ mx = t; poc = k; } });
        let mxd = 0; rows.forEach(v => { mxd = Math.max(mxd, Math.abs(v.b - v.s)); });   // the biggest |delta| of the bar: scales the colour in the delta mode
        const an = this.fpAn(m, rows, step, OF), PRx = this.PR;
        const touched = (j0, lo_, hi_) => { for (let j = j0; j < d.length; j++) if (d[j].l <= hi_ && d[j].h >= lo_) return j; return -1; };   // first later candle that trades inside [lo_, hi_]
        rows.forEach((v, k) => {
          const y = py(k*step), h = Math.max(2, Math.abs(py(k*step) - py((k+1)*step)) - 1), a = (v.b + v.s)/(mx || 1);
          if (FM === "delta") c.fillStyle = hexA(v.b >= v.s ? FB : FS, .1 + .6*Math.abs(v.b - v.s)/(mxd || 1)); else if (FM === "volume") c.fillStyle = hexA("#4aa3ff", .1 + .6*a); else c.fillStyle = hexA(v.b >= v.s ? FB : FS, .12+.5*a);
          c.fillRect(x-w/2, y-h/2, w, h);
          if (k === poc){ c.strokeStyle = v.b >= v.s ? FB : FS; c.lineWidth = 2; c.strokeRect(x-w/2, y-h/2, w, h); c.lineWidth = 1; }
          if (big && (v.b + v.s) >= OF.bigx*(m.b + m.s)/Math.max(1, rows.size) && h >= 6){   // large order: dot + offset + radius proportional to its size, same colour as the cell
            const ratio = Math.min(1, (v.b + v.s)/(mx || 1)), bc = v.b >= v.s ? FB : FS, ox = x+w/2+5+ratio*22, rr = 2.5+ratio*5;
            c.strokeStyle = bc; c.globalAlpha = .5; c.lineWidth = 1; c.beginPath(); c.moveTo(x+w/2, y); c.lineTo(ox, y); c.stroke(); c.globalAlpha = 1;
            c.fillStyle = bc; c.beginPath(); c.arc(ox, y, rr, 0, 6.3); c.fill(); c.textAlign = "left"; c.font = "bold "+fs+"px ui-monospace,Menlo,Consolas,monospace"; c.fillText(fmt(v.b + v.s), ox+rr+3, y);
            if (i === i1){ const last = d[d.length-1].c, dist = k*step - last; c.font = fs+"px ui-monospace,Menlo,Consolas,monospace"; c.fillText((dist >= 0 ? "+" : "")+dist.toFixed(dec), ox+rr+3+26, y); } }
          const im_ = an.imb.get(k), imbB = im_ === "b", imbS = im_ === "s";
          if (big && h >= 8 && FM !== "bidask"){ const dv = v.b - v.s, tv = FM === "delta" ? dv : v.b + v.s; c.textAlign = "center"; c.fillStyle = FM === "delta" ? (dv >= 0 ? "#6df0b5" : "#ff8a97") : "#c7ccd3"; c.font = ((imbB || imbS) ? "bold " : "") + fs+"px ui-monospace,Menlo,Consolas,monospace"; c.fillText((tv < 0 ? "−" : (FM === "delta" && tv > 0 ? "+" : "")) + fmt(Math.abs(tv)), x, y); }
          else if (big && h >= 8){ c.textAlign = "right"; c.fillStyle = imbS ? "#ff8a97" : "#c7ccd3"; c.font = (imbS ? "bold " : "") + fs+"px ui-monospace,Menlo,Consolas,monospace"; c.fillText(fmt(v.s), x-2, y);
            c.textAlign = "left"; c.fillStyle = imbB ? "#6df0b5" : "#c7ccd3"; c.font = (imbB ? "bold " : "") + fs+"px ui-monospace,Menlo,Consolas,monospace"; c.fillText(fmt(v.b), x+2, y); }
        });
        if (OF.fpStack !== 0) an.runs.forEach(rn => {   // stacked imbalance: a bar beside the cells and a faint zone to the right until price trades back into it
          const yT = py((rn.k1 + .5)*step), yB = py((rn.k0 - .5)*step), col = rn.side === "b" ? FB : FS, j = touched(i + 1, rn.k0*step - step/2, rn.k1*step + step/2), xe = j < 0 ? PRx : Math.min(PRx, this.x(j));
          c.fillStyle = hexA(col, .1); c.fillRect(x + w/2, yT, Math.max(0, xe - (x + w/2)), yB - yT); c.fillStyle = col; c.fillRect(x + w/2 + 1, yT, 3, yB - yT); });
        if (OF.fpVA !== 0 && big){ const va = this.vaOf(rows, .7); if (va){ const yT = py((va.vah + .5)*step), yB = py((va.val - .5)*step), xl = x - w/2 - 3; c.strokeStyle = "#b57cff"; c.lineWidth = 2; c.beginPath(); c.moveTo(xl + 3, yT); c.lineTo(xl, yT); c.lineTo(xl, yB); c.lineTo(xl + 3, yB); c.stroke(); c.lineWidth = 1;
            if (bw >= 70){ c.fillStyle = "#b57cff"; c.font = "8px sans-serif"; c.textAlign = "right"; c.fillText("VAH", xl - 2, yT + 4); c.fillText("VAL", xl - 2, yB - 1); } } }   // value area (70 %) of the bar: a bracket on the left of the cells
        if (OF.fpNaked !== 0 && an.poc != null){ const pp = an.poc*step, j = touched(i + 1, pp - step/2, pp + step/2), yp = py(pp);   // naked POC: runs on until price trades through it
          if (j < 0 && i < d.length - 1){ c.save(); c.strokeStyle = hexA("#f0b90b", .8); c.setLineDash([4, 3]); c.lineWidth = 1; c.beginPath(); c.moveTo(x + w/2, yp); c.lineTo(PRx, yp); c.stroke(); c.restore(); c.fillStyle = "#f0b90b"; c.textAlign = "right"; c.font = "9px sans-serif"; c.fillText(Lg("nPOC", "POC أعزل"), PRx - 3, yp - 6); c.font = fs+"px ui-monospace,Menlo,Consolas,monospace"; } }
        if (OF.fpAuc !== 0 && big){ [[an.hiUnf, an.hiK, -1], [an.loUnf, an.loK, 1]].forEach(([u, kk, dir]) => { if (!u || kk == null) return; const yy = py(kk*step);   // unfinished auction: both sides traded at the extreme row, small ring + the level stays marked until the extreme is traded again
            const lvl = kk*step, jj = (() => { for (let j = i + 1; j < d.length; j++) if (dir < 0 ? d[j].h >= lvl : d[j].l <= lvl) return j; return -1; })(), xe = jj < 0 ? PRx : Math.min(PRx, this.x(jj));
            c.save(); c.strokeStyle = "rgba(200,206,214,.55)"; c.setLineDash([2, 3]); c.beginPath(); c.moveTo(x + w/2, yy); c.lineTo(xe, yy); c.stroke(); c.restore();
            c.strokeStyle = "#c8ced6"; c.beginPath(); c.arc(x, yy + dir*(-5), 3, 0, 6.3); c.stroke(); }); }
      }
    }
    if (OF.fpCvd !== 0 && PB > 160){   // CVD strip at the bottom of the plot + divergence marks on the candles
      const N = 12, A = this.cvdAn(d, this.fp, N), yT = PB*0.8, yB = PB - 6; let mn = Infinity, mx2 = -Infinity;
      for (let i = i0; i <= i1; i++) if (A.cvd[i] != null){ mn = Math.min(mn, A.cvd[i]); mx2 = Math.max(mx2, A.cvd[i]); }
      if (mn < mx2){ const yy = v => yB - (v - mn)/(mx2 - mn)*(yB - yT); c.strokeStyle = "#4aa3ff"; c.globalAlpha = .85; c.lineWidth = 1.4; c.beginPath(); let st = false;
        for (let i = i0; i <= i1; i++){ if (A.cvd[i] == null) continue; const X = this.x(i); if (!st){ c.moveTo(X, yy(A.cvd[i])); st = true; } else c.lineTo(X, yy(A.cvd[i])); } c.stroke(); c.globalAlpha = 1; c.lineWidth = 1;
        c.fillStyle = "#4aa3ff"; c.font = "9px sans-serif"; c.textAlign = "left"; c.fillText("CVD", this.x(i0) + 2, yT - 2); }
      A.div.forEach(({i, side}) => { if (i < i0 || i > i1) return; const X = this.x(i), up = side === "bull", yy = up ? py(d[i].l) + 9 : py(d[i].h) - 9; c.fillStyle = up ? "#0ecb81" : "#f6465d"; c.beginPath();
        if (up){ c.moveTo(X, yy - 5); c.lineTo(X - 4, yy + 2); c.lineTo(X + 4, yy + 2); } else { c.moveTo(X, yy + 5); c.lineTo(X - 4, yy - 2); c.lineTo(X + 4, yy - 2); } c.fill();
        if (bw >= 14){ c.font = "bold 9px sans-serif"; c.textAlign = "center"; c.fillText(Lg("CVD div", "تباعد CVD"), X, up ? yy + 12 : yy - 8); } }); }
    c.restore();
  },
  paintXhCol(c, PR, PB){   // crosshair on the order-flow column: the time (and price) of this chart's pointer, or the time shared from a linked chart
    const tx = this._colTx, CW = this.cw(); if (!tx || !CW) return; let t = null, y = null;
    if (this.mouse && this.mouse.x < PR && this.mouse.y < PB){ const ii = Math.max(0, Math.min(this.data.length-1, Math.round(this.idx(this.mouse.x)))); if (this.data[ii]) t = this.data[ii].t; y = this.mouse.y; }
    else if (XHS.on && XHS.sym === this.sym && XHS.t != null) t = XHS.t;
    if (t == null) return; const xr = tx(t), x0 = PR + 5, x1 = PR + CW - 3, x = Math.max(x0, Math.min(x1, xr)), off = xr < x0 ? "◀ " : xr > x1 ? "▶ " : "";   // outside the column's window: the line pins to the edge with the time, so the column still shows where the crosshair is
    const own = !!this.mouse; c.save(); c.strokeStyle = own ? "#5a636e" : "#f0b90b"; c.setLineDash([3,3]); c.beginPath(); c.moveTo(x+.5, 0); c.lineTo(x+.5, PB);
    if (own && y != null){ c.moveTo(PR, y+.5); c.lineTo(PR + CW, y+.5); }
    c.stroke(); c.setLineDash([]); if (off){ c.fillStyle = c.strokeStyle; c.font = "10px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = x < PR + CW/2 ? "left" : "right"; c.fillText(off + this.fmtTime(t), x + (x < PR + CW/2 ? 4 : -4), 26); }
    c.restore(); },
  ofStepNow(){ return (this.ofStepMap && this.ofStepMap[this.sym]) || 0; },   // 0 = Auto
  placeGroupSel(on){   // the price-grouping list lives in the chart toolbar (next to Fit) and shows only while the order-flow column is on
    if (!on) return this.onGroupSel && this.onGroupSel(false);
    const tick = tickOfLevels(((this.flowB && this.flowB.length && this.flowB[this.flowB.length-1].lv) || []).map(a => ({p:a[0], q:a[1]})));
    this.onGroupSel && this.onGroupSel(true, this.ofStepNow(), tick); },
  paintCol(c, py, PB, PR, i0, i1){   // Bookmap / ATAS style: a time-scrolling liquidity heat map + trade bubbles on the chart's price scale. x = TIME (newest at the right edge), independent of the candle timeframe. Wheel over it = time zoom, drag its left edge = width.
    if (this.colWide > 0 && this.domOn){   // WIDE mode (owner 2026-11-05: "the column covers only the chart's few dollars; I want the whole book, weekly support / resistance"): the column has its OWN price scale over the whole book (never narrower than the chart), the biggest resting orders as labelled lines, a bracket for what the chart shows
      const cwW = this.cw(); this.placeGroupSel(false); this._colTx = null; c.save(); c.beginPath(); c.rect(PR, 0, cwW, PB); c.clip(); c.translate(PR, 0);
      const own = this.colOwn === true, wo = {compact:true, ylink:own ? null : [this._lo, this._hi], vis:own ? [this._lo, this._hi] : null, rman:own ? this.colWideR : 0, win:this.flowSpan ? Math.max(10000, Math.min(OFM.KEEP, this.flowSpan)) : 0}; OFM.render(c, {snaps:this.wom.snaps, trades:this.bub}, {omB:true}, cwW, PB, wo); this._wideAutoR = wo.outR; this._wideLink = wo.ylink; this._wideWin = wo.outWin; c.restore();
      if (this.syncOn && this.scOn !== false){ const room = this.H - 20 - PB - 6; if (room >= 96) this.paintSyncCard(c, PR + 4, PR + cwW - 3, PB, {top:PB + 3, h:room}); }   // the sync card keeps its place under the plot (never over the map)
      return; }
    const OF = this.st.of, X0 = PR, CW = this.cw(), XE = X0 + CW, lo = this._lo, hi = this._hi, now = nowS(), span = this.fspan(now), gx0 = X0 + 5, gx1 = XE - 3, gw = gx1 - gx0;
    const fixedHm0 = (OF.hmm || "fix") === "fix", qa = span/8, anchor = fixedHm0 && (this.flowSpan || span > 900000) ? Math.ceil(now/qa)*qa : now;   // fixed mode: the time axis is anchored to a grid of span/8, so cells stand still and only jump one step when the window fills (no continuous sliding)
    const tx = t => gx1 - (anchor - t)/span*gw;   // time -> x
    this._colTx = tx; this.placeGroupSel(true);
    c.save(); c.fillStyle = (this.st.of.hm || "book") === "book" && this.domOn ? "rgb(1,3,8)" : "#0d1116"; c.fillRect(X0, 0, CW, PB);   // heat-map base colour fills the column top to bottom; the book itself only exists where the exchange lists orders c.strokeStyle = "#2b3139"; c.beginPath(); c.moveTo(X0 + .5, 0); c.lineTo(X0 + .5, PB); c.moveTo(XE + .5, 0); c.lineTo(XE + .5, PB); c.stroke();
    c.fillStyle = "#3a424b"; c.fillRect(X0 + 1, Math.round(PB/2) - 12, 3, 24);   // grip: drag to resize, double-click = default
    c.beginPath(); c.rect(X0 + 5, 0, CW - 7, PB); c.clip();
    const raw0 = Math.max((hi-lo)/Math.max(1, PB/6), this.bk || 0), detail = OF.hmDetail || "auto", tfSec = TFSEC[this.tf] || 3600, detailMul = detail === "compact" ? 2.5 : detail === "precise" ? 0.65 : detail === "auto" ? (tfSec <= 300 ? 0.7 : tfSec <= 3600 ? 1 : tfSec <= 14400 ? 1.35 : tfSec < 86400 ? 1.7 : 2.2) : 1, raw = raw0 * detailMul, mag = Math.pow(10, Math.floor(Math.log10(raw || 1))), step = this.ofStepNow() > 0 ? Math.max(this.ofStepNow(), this.bk || 0) : ([1,2,2.5,5,10].map(x => x*mag).find(x => x >= raw) || raw), rowH = Math.max(2, Math.abs(py(0) - py(step)));
    const B = (this.flowB || []).filter(x => x.t >= anchor - span*1.05), T_ = (this.flowT || []).filter(x => x.t >= anchor - span);
    // 1) heat map: each book snapshot is a vertical slice that lasts until the next snapshot; colour = resting size at that price (scheme: Bookmap thermal / bid-ask colours / amber). The per-snapshot price rows are computed once and cached.
    let hm = 0; const rows = B.map(sn => { if (sn._rs !== step){ const m = new Map(); sn.lv.forEach(([p, q]) => { const k = Math.round(p/step), o = m.get(k); if (o) o.q += q; else m.set(k, {q, bid:sn.bb ? p <= sn.bb : true}); }); let mx = 0; m.forEach(v => { if (v.q > mx) mx = v.q; }); sn._r = m; sn._mx = mx; sn._rs = step; } if (sn._mx > hm) hm = sn._mx; return sn._r; });
    const scheme = OF.hm || "book", ramps = {book:[[0,[1,3,8]],[.25,[20,70,190]],[.5,[20,190,210]],[.7,[240,220,40]],[.88,[245,120,30]],[1,[255,250,235]]], magma:[[0,[5,4,18]],[.3,[75,25,110]],[.58,[190,45,95]],[.8,[255,135,55]],[1,[255,245,180]]], ice:[[0,[2,12,25]],[.3,[10,75,120]],[.6,[45,190,210]],[.82,[180,240,245]],[1,[255,255,255]]], emerald:[[0,[2,15,10]],[.3,[0,90,60]],[.6,[20,190,110]],[.82,[180,235,70]],[1,[255,250,210]]]}, RAMP = ramps[scheme] || ramps.book;
    const bright = Math.max(.25, Math.min(1.75, Number(OF.hmBright) || 1));
    const ramp = scheme === "custom" ? (t => hmMix(t, hexRgb(OF.hmLo || "#010308"), hexRgb(OF.hmHi || "#fff5fa"))) : t => { for (let q = 1; q < RAMP.length; q++){ if (t <= RAMP[q][0]){ const a = RAMP[q-1], b = RAMP[q], u = (t - a[0])/(b[0] - a[0] || 1); return "rgb("+Math.round(a[1][0] + (b[1][0]-a[1][0])*u)+","+Math.round(a[1][1] + (b[1][1]-a[1][1])*u)+","+Math.round(a[1][2] + (b[1][2]-a[1][2])*u)+")"; } } return "rgb(255,250,235)"; };
    // 0) full-range base: traded volume by price of every candle on the chart (real data at any zoom: 50k..70k on a big timeframe). The exchange only lists resting orders close to the market, so this is what shows far levels; the book heat map is drawn on top of it
    const vpfOn = OF.vpf === true || (OF.vpf == null && tfSec >= 3600);   // the traded-volume-by-price base is ON by itself from 1H up (the book alone shows nothing far from price there); the settings can force it on / off
    if (this.domOn && vpfOn){ const d_ = this.data, nR = Math.max(20, Math.min(240, Math.round(PB/5))), key = d_.length+"|"+d_[d_.length-1].c+"|"+d_[d_.length-1].v+"|"+i0+"|"+i1+"|"+lo+"|"+hi+"|"+nR;
      if (!this._vp || this._vp.k !== key){ const vp = new Float64Array(nR), rh = (hi - lo)/nR || 1; for (let i = Math.max(0, i0); i <= Math.min(d_.length-1, i1); i++){ const k = d_[i], a0 = Math.max(0, Math.floor((k.l - lo)/rh)), a1 = Math.min(nR-1, Math.floor((k.h - lo)/rh)); if (a1 < a0) continue; const per = k.v/(a1 - a0 + 1); for (let r = a0; r <= a1; r++) vp[r] += per; } let m = 0; vp.forEach(v => { if (v > m) m = v; }); this._vp = {k:key, vp, m, rh}; }
      const V = this._vp; for (let r = 0; r < nR; r++){ const u = Math.pow(V.vp[r]/(V.m || 1), .6); if (u < .05) continue; const y0 = py(lo + (r + 1)*V.rh), y1 = py(lo + r*V.rh); c.fillStyle = hmRamp(u*.4); c.globalAlpha = .55 + .35*u; c.fillRect(gx0, y0, gw, Math.max(1, y1 - y0 + .5)); } c.globalAlpha = 1; }
    const fixedHm = (OF.hmm || "fix") === "fix" && span > 900000; if (this.domOn && fixedHm){ this.hmInit(); const firstHm = this.paintHeatCol(c, py, PB, tx, gx0, gx1, anchor - span*1.05, anchor + 60000); if (firstHm == null){ c.fillStyle = "#848e9c"; c.font = "10px sans-serif"; c.textAlign = "left"; c.fillText(Lg("No saved depth cells in this time window / price range","لا توجد خلايا عمق محفوظة في الفترة الزمنية أو النطاق السعري ده"), gx0, 26); } }
    if (this.domOn && this.secMs() > 600000 && (OF.hmm || "fix") === "fix" && !this.flowSpan){ const rec = this.hmRecorded(now), tfm = this.secMs(), cv = this.hmCover(now); if (cv && cv.gaps && rec >= tfm){ const z = n => String(n).padStart(2, "0"), dt = new Date(cv.oldest);
      c.save(); c.fillStyle = "#f0b90b"; c.font = "10px sans-serif"; c.textAlign = "left"; c.fillText(Lg("Book history has "+cv.gaps+" gap(s) ("+Math.round(cv.gapMs/60000)+" min with the app closed) · oldest "+z(dt.getDate())+"/"+z(dt.getMonth()+1)+" "+z(dt.getHours())+":"+z(dt.getMinutes()), "تاريخ الدفتر فيه "+cv.gaps+" فجوة ("+Math.round(cv.gapMs/60000)+" دقيقة والتطبيق مقفول) · الأقدم "+z(dt.getDate())+"/"+z(dt.getMonth()+1)+" "+z(dt.getHours())+":"+z(dt.getMinutes())), gx0, PB - 8); c.restore(); } if (rec < tfm){ const mins = Math.max(1, Math.round(rec/60000)), since = new Date(now - rec), hh = String(since.getHours()).padStart(2, "0")+":"+String(since.getMinutes()).padStart(2, "0");
      c.save(); c.fillStyle = "#848e9c"; c.font = "10px sans-serif"; c.textAlign = "left"; c.fillText(Lg("Recording since "+hh+" · "+mins+" min so far (this "+this.tf+" candle is longer)", "بيسجّل من "+hh+" · "+mins+" دقيقة لحد دلوقتي (شمعة "+this.tf+" أطول)"), gx0, PB - 8); c.restore(); } }
    if (this.domOn && !fixedHm) B.forEach((sn, i) => { const x0 = Math.max(gx0, tx(sn.t)), x1 = Math.min(gx1, i + 1 < B.length ? tx(B[i+1].t) : gx1), w = Math.max(1.2, x1 - x0); if (x1 < gx0) return;
      rows[i].forEach((v, k) => { const y = py(k*step); if (y < -rowH || y > PB + rowH) return; const rawT = Math.min(1, Math.pow(v.q/(hm || 1), .55)*(OF.dom || 1)), t = Math.min(1, Math.pow(rawT, 1/bright)); if (t < .04) return;
        c.globalAlpha = Math.max(.12, Math.min(1, (.08 + .9*t) * Math.min(1, bright)));
        c.fillStyle = scheme === "side" ? hexA(v.bid ? OF.color : OF.color2, .08 + .9*t) : scheme === "amber" ? "rgba(255,"+Math.round(190 + 65*t*t)+","+Math.round(30 + 210*t*t*t)+","+(.08 + .9*t).toFixed(2)+")" : ramp(t); c.fillRect(x0, y - rowH/2, w, rowH + .5); c.globalAlpha = 1; }); });
    // 1b) Bookmap-style depth histogram on the right edge: current resting size at every price row (bid colour below the mid, ask colour above)
    if (this.domOn && B.length){ const sn = B[B.length-1], R_ = sn._r; if (R_ && R_.size){ let mq = 0; R_.forEach(v => { if (v.q > mq) mq = v.q; }); const mw = gw*0.3;
      R_.forEach((v, k) => { const y = py(k*step); if (y < -rowH || y > PB + rowH) return; const w_ = Math.max(1, Math.pow(v.q/(mq || 1), .6)*mw); c.fillStyle = hexA(v.bid ? OF.color : OF.color2, .55); c.fillRect(gx1 - w_, y - rowH/2 + .5, w_, Math.max(1, rowH - 1)); }); } }
    // 2) mid-price trace (the line the heat map is read against)
    if (this.domOn && B.length > 1){ c.strokeStyle = "#eaecef"; c.lineWidth = 1.2; c.beginPath(); let st = false; B.forEach(sn => { if (!sn.bb || !sn.ba) return; const x = tx(sn.t); if (x < gx0) return; const y = py((sn.bb + sn.ba)/2); st ? c.lineTo(x, y) : (c.moveTo(x, y), st = true); }); c.stroke(); }
    // 2b) absorption: lots of volume traded at ONE price row without the price leaving it = the resting orders there soaked it up -> purple frame on the heat map
    const ab = new Map(); { const g = new Map(), w0 = now - Math.min(span, 45000); T_.forEach(x => { if (x.t < w0) return; const k = Math.round(x.p/step), o = g.get(k) || (g.set(k, {sum:0, n:0, buy:0, sell:0, t0:x.t}), g.get(k)); o.sum += x.q; o.n++; x.side === "Buy" ? o.buy += x.q : o.sell += x.q; if (x.t < o.t0) o.t0 = x.t; });
      const sums = [...g.values()].map(o => o.sum).sort((a, b) => a - b), med = sums.length ? sums[sums.length >> 1] : 0;
      g.forEach((o, k) => { if (o.n >= 4 && sums.length >= 4 && o.sum >= 3*Math.max(med, 1e-12)) ab.set(k, o); }); }
    if (this.domOn) ab.forEach((o, k) => { const y = py(k*step), x0 = Math.max(gx0, tx(o.t0)); if (y < -rowH || y > PB + rowH) return; c.strokeStyle = "#b57cff"; c.lineWidth = 1.6; c.fillStyle = "rgba(181,124,255,.16)"; c.fillRect(x0, y - rowH/2, gx1 - x0, rowH); c.strokeRect(x0, y - rowH/2, gx1 - x0, rowH);
      c.fillStyle = "#d9b8ff"; c.font = "bold 9px sans-serif"; c.textAlign = "left"; c.fillText("ABS " + (o.buy >= o.sell ? Lg("sellers absorb","البيع بيمتص") : Lg("buyers absorb","الشراء بيمتص")), x0 + 2, y - rowH/2 - 3); });
    // 2c) flashes: a big resting order that vanished. White = pulled (cancelled), purple = filled / absorbed by trades. Bright for 2.5 s, then a faint tick stays at that price and time
    if (this.domOn){ const nowT = now, FE = (this.flowE || []).filter(e => e.t >= now - span); let em = 0; FE.forEach(e => { if (e.q > em) em = e.q; });
      FE.forEach(e => { const X = tx(e.t), Y = py(e.p); if (X < gx0 - 4 || Y < -10 || Y > PB + 10) return; const age = (nowT - e.t)/1000, hot = age < 2.5, col = e.kind === "fill" ? "#b57cff" : "#ffffff", hh = Math.max(rowH, 3), ww = hot ? 16 + 20*Math.sqrt(e.q/(em || 1)) : 4;
        c.globalAlpha = hot ? Math.max(.25, 1 - age/2.5)*(.55 + .45*(Math.floor(age*6) % 2)) : .5; c.fillStyle = col; c.fillRect(X, Y - hh/2, ww, hh); if (hot){ c.strokeStyle = col; c.lineWidth = 1.2; c.strokeRect(X - 1, Y - hh/2 - 1, ww + 2, hh + 2); } c.globalAlpha = 1; }); }
    // 3) bubbles: one per print, size = quantity, buy = green / sell = red, they drift left as time passes and fade with age
    let qm = 0; T_.forEach(x => { if (x.q > qm) qm = x.q; }); const maxR = Math.min(22, Math.max(5, gw/9))*(OF.bsz || 1), top = [], mt = OF.min >= 2 ? 2 : 0, rk = {normal:0, smart:1, whale:2};   // in the column every print above 4% of the biggest one is drawn (the old default 'smart+' hid all normal prints, so no bubbles appeared); 'whale only' still filters
    if (this.bubOn) T_.forEach(x => { if (rk[x.tier || "normal"] < mt) return; if (x.q < qm*0.04) return; const X = tx(x.t), Y = py(x.p); if (X < gx0 - 4 || Y < -10 || Y > PB + 10) return; const age = (now - x.t)/span, r = Math.max(1.8, maxR*Math.pow(x.q/(qm || 1), .5)*Math.min(1, .35 + (now - x.t)/500)), col = x.side === "Buy" ? OF.color : OF.color2;
      c.globalAlpha = Math.max(.35, 1 - age*.65); c.fillStyle = hexA(col, Math.min(1, .5*(OF.bop || 1))); c.strokeStyle = col; c.lineWidth = 1; c.beginPath(); c.arc(X, Y, r, 0, 6.3); c.fill(); c.stroke(); if (ab.has(Math.round(x.p/step))){ c.strokeStyle = "#b57cff"; c.lineWidth = 2.2; c.beginPath(); c.arc(X, Y, r + 2.5, 0, 6.3); c.stroke(); } c.globalAlpha = 1; top.push([x.q, X, Y]); });
    c.font = "9px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "center"; c.fillStyle = "#cfd6dd";
    top.sort((a, b) => b[0] - a[0]).slice(0, 5).forEach(([q, X, Y]) => c.fillText(q >= 1000 ? (q/1000).toFixed(1)+"k" : q >= 10 ? q.toFixed(0) : q.toFixed(2), Math.max(gx0 + 12, Math.min(gx1 - 12, X)), Y - 10));
    const ly = py(this.data[this.data.length-1].c); c.strokeStyle = "#4aa3ff"; c.setLineDash([3,3]); c.beginPath(); c.moveTo(X0, ly + .5); c.lineTo(XE, ly + .5); c.stroke(); c.setLineDash([]);
    c.textAlign = "left"; c.fillStyle = "#848e9c"; c.font = "9px sans-serif"; const sp = span >= 86400000 ? Math.round(span/864000)/100+"d" : span >= 3600000 ? Math.round(span/360000)/10+"h" : span >= 60000 ? Math.round(span/60000*10)/10+"m" : Math.round(span/1000)+"s";
    { const full = Lg("ORDER FLOW · "+sp+" window (wheel = zoom)", "أوردر فلو · نافذة "+sp+" (العجلة = تكبير الوقت)"), mid = Lg("ORDER FLOW · "+sp, "أوردر فلو · "+sp), sht = Lg("OF · "+sp, "أوردر · "+sp), lg = this.domOn ? 100 : 0;   // narrow column: the title shrinks (full -> short -> tiny) and the pulled / filled key drops out before they run over each other
      const pick = [full, mid, sht].find(t => c.measureText(t).width + lg <= gw) || sht; c.fillText(pick, gx0, 10); this._ofKey = c.measureText(pick).width + lg <= gw + 2; }
    if (this.domOn && this._ofKey){ c.fillStyle = "#ffffff"; c.fillText("■ "+Lg("pulled","اتلغى"), gx1 - 96, 10); c.fillStyle = "#b57cff"; c.fillText("■ "+Lg("filled","اتنفذ"), gx1 - 46, 10); c.fillStyle = "#848e9c"; }
    if (this.domOn && B.length){ const sn = B[B.length-1], ps = sn.lv.map(x => x[0]); if (ps.length){ const yA = py(Math.max(...ps)), yB = py(Math.min(...ps)); c.fillStyle = "rgba(74,163,255,.07)"; c.fillRect(gx0, Math.min(yA, yB), gw, Math.max(2, Math.abs(yB - yA)));   // the price range the exchange book covers right now: outside of it the book has no orders to show (only the traded-volume base does)
        c.strokeStyle = "rgba(74,163,255,.35)"; c.setLineDash([2, 3]); c.beginPath(); c.moveTo(gx0, yA + .5); c.lineTo(gx1, yA + .5); c.moveTo(gx0, yB + .5); c.lineTo(gx1, yB + .5); c.stroke(); c.setLineDash([]); } }
    if (this.domOn && B.length){ const sn = B[B.length-1], ps = sn.lv.map(x => x[0]), mid = (sn.bb + sn.ba)/2; if (ps.length && mid){ const cov = (Math.max(...ps) - Math.min(...ps))/mid*100/2; c.fillStyle = "#6b7684"; c.fillText(cov > 0.95 ? Lg("book depth ±1 % (view cap)", "عمق الدفتر ±1% (سقف العرض)") : Lg("book depth ±"+cov.toFixed(2)+"% (exchange limit)", "عمق الدفتر ±"+cov.toFixed(2)+"% (حد البورصة)"), gx0, 36); } }
    if (this.domOn && vpfOn){ c.fillStyle = "#6b7684"; c.textAlign = "left"; c.fillText(Lg("▒ dim = estimated candle-volume profile (approx.) · bright = live/saved order book","▒ الخافت = توزيع تقديري لحجم الشموع (تقريبي) · الساطع = دفتر الأوامر الحي/المحفوظ"), gx0, 46); }
    if (this.domOn){ const bx = gx0, by = PB - 22, bw_ = Math.min(110, gw - 10); for (let q = 0; q < bw_; q++){ c.fillStyle = scheme === "side" ? hexA(OF.color, .15 + .85*(q/(bw_ - 1))) : scheme === "amber" ? "rgba(255,"+Math.round(190 + 65*(q/(bw_-1))**2)+","+Math.round(30 + 210*(q/(bw_-1))**3)+",1)" : ramp(q/(bw_ - 1)); c.fillRect(bx + q, by, 1.2, 6); } c.fillStyle = "#9aa4b2"; c.font = "8px sans-serif"; if (bw_ >= 84){ c.textAlign = "left"; c.fillText(Lg("small","صغير"), bx, by - 2); c.textAlign = "right"; c.fillText(Lg("big orders","أوامر كبيرة"), bx + bw_, by - 2); } else if (bw_ >= 44){ c.textAlign = "right"; c.fillText(Lg("big","كبير"), bx + bw_, by - 2); } c.textAlign = "left"; }   // narrow column: the two words would run over each other and out of the panel
    if (this.domOn && B.length < 2){ c.fillText(Lg("collecting the live book... (builds from now on)", "بيجمع الدفتر لايف... (بيتبني من دلوقتي)"), gx0, 26); }
    { const hb = Hub.last["book|"+this.sym], ht = Hub.last["trades|"+this.sym], er = (hb && hb.error) || (ht && ht.error); c.textAlign = "left"; c.font = "9px sans-serif"; c.fillStyle = er ? "#f6465d" : "#5e6673";
      c.fillText(er ? ("⚠ " + (hb && hb.error ? "book: " : "trades: ") + String(er).slice(0, 40)) : ("book " + (this.flowB || []).length + " · prints " + (this.flowT || []).length), gx0, PB - 6); }
    this._gaX = null; if (this.domOn && gw >= 230 && this.gaOn !== false) this.paintGauge(c, gx1, PB);
    if (this.readOn === true && this.domOn) this.paintRead(c, X0, XE, PB, py, now);   // FLOW READING (off by default): a short numbered reading of the last 2 minutes; needs a column >= 150 px and a plot >= 200 px
    c.restore();
    // sync card: in the empty space UNDER the order-flow column (next to the indicator panes) when there is room, else inside the column above the legend
    this._scX = null;
    if (this.syncOn && this.scOn !== false){ const room = this.H - 20 - PB - 6;
      if (room >= 96){ this.paintSyncCard(c, X0 + 4, XE - 3, PB, {top:PB + 3, h:room}); }
      else if (this.H >= 330 && gw >= 150){ const sx1 = this.domOn && gw >= 230 ? gx1 - 92 : gx1 - 2; this.paintSyncCard(c, gx0 + 2, sx1, PB); } }   // a small panel / narrow column: the card would sit on top of the heat map, so it stays off (the setting / a taller panel brings it back)   // the ✕ is drawn by the card itself (both layouts)
  },
  gaugeData(now){   // buy/sell pressure from REAL data only: aggressor volume of the last 2 min of prints, and bid vs ask size resting within 0.5 % of the mid (latest book snapshot)
    const W = 120000, T = (this.flowT || []).filter(x => x.t >= now - W); let b = 0, s = 0; T.forEach(x => { if (x.side === "Buy") b += x.q; else s += x.q; });
    const sn = this.flowB && this.flowB[this.flowB.length-1]; let bd = 0, ad = 0; if (sn && sn.bb && sn.ba){ const mid = (sn.bb + sn.ba)/2; sn.lv.forEach(([p, q]) => { if (Math.abs(p - mid)/mid > 0.005) return; if (p <= sn.bb) bd += q; else ad += q; }); }
    return {tr: b + s > 0 ? {buy:b, sell:s, n:T.length, v:(b - s)/(b + s)} : null, bk: bd + ad > 0 ? {bid:bd, ask:ad, v:(bd - ad)/(bd + ad)} : null};
  },
  paintOfX(c, x, y, key){   // small ✕ that hides an order-flow data box (gauge / sync card); hit area kept in this[key] for down()
    c.save(); c.fillStyle = "rgba(8,12,18,.85)"; c.fillRect(x, y, 13, 13); c.fillStyle = "#f6465d"; c.font = "bold 10px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("✕", x + 6.5, y + 7); c.restore();
    this[key] = {x, y, w:13, h:13};
  },
  paintGauge(c, gx1, PB){   // semicircle gauge (sell | buy) bottom-right of the order-flow column; needle = net aggressor pressure, bar below = book imbalance
    const OF = this.st.of, G = this.gaugeData(nowS()), R = 30, cx = gx1 - R - 14, cy = PB - 52;
    c.save(); c.fillStyle = "rgba(8,12,18,.72)"; c.fillRect(cx - R - 12, cy - R - 16, 2*R + 24, R + 62); c.textBaseline = "middle"; this.paintOfX(c, cx + R - 2, cy - R - 15, "_gaX");
    for (let k = 0; k < 40; k++){ const a0 = Math.PI + k/40*Math.PI, a1 = Math.PI + (k + 1)/40*Math.PI, t = k/39; c.strokeStyle = t < .5 ? hexA(OF.color2, .35 + .65*(1 - t*2)) : hexA(OF.color, .35 + .65*((t - .5)*2)); c.lineWidth = 7; c.beginPath(); c.arc(cx, cy, R - 4, a0, a1 + .02); c.stroke(); }
    const v = G.tr ? G.tr.v : 0, ang = Math.PI + (v + 1)/2*Math.PI; c.strokeStyle = G.tr ? "#fff" : "#6b7684"; c.lineWidth = 2; c.beginPath(); c.moveTo(cx, cy); c.lineTo(cx + Math.cos(ang)*(R - 8), cy + Math.sin(ang)*(R - 8)); c.stroke(); c.fillStyle = "#fff"; c.beginPath(); c.arc(cx, cy, 3, 0, 6.3); c.fill();
    c.font = "bold 10px sans-serif"; c.textAlign = "center"; c.fillStyle = G.tr ? (v >= 0 ? OF.color : OF.color2) : "#6b7684"; c.fillText(G.tr ? Math.round(100*G.tr.buy/(G.tr.buy + G.tr.sell))+"% "+Lg("buy","شراء") : Lg("no prints","مفيش صفقات"), cx, cy + 10);
    c.font = "8px sans-serif"; c.fillStyle = "#9aa4b2"; c.fillText(Lg("prints 2m","صفقات 2د")+(G.tr ? " · "+G.tr.n : ""), cx, cy + 20);
    const by = cy + 29, bw = 2*R, bx = cx - R; c.fillStyle = "#1b2027"; c.fillRect(bx, by, bw, 5); if (G.bk){ const f = G.bk.bid/(G.bk.bid + G.bk.ask); c.fillStyle = OF.color; c.fillRect(bx, by, bw*f, 5); c.fillStyle = OF.color2; c.fillRect(bx + bw*f, by, bw*(1 - f), 5); c.fillStyle = "#9aa4b2"; c.fillText(Lg("book bid ","دفتر شراء ")+Math.round(100*f)+"%", cx, by + 12); } else { c.fillStyle = "#6b7684"; c.fillText(Lg("book –","دفتر –"), cx, by + 12); }
    c.restore();
  },
  paintDiv(c, kind, series, X, Y, i0, i1, tag){   // divergence line between the two swing points, drawn on the indicator's own pane (green = bullish, red = bearish)
    if (!this.divOn || !series) return; const k = kind+":"+this.data.length+":"+(this.data.length ? this.data[this.data.length-1].c+"/"+this.data[this.data.length-1].v : 0)+":"+(kind === "rsi" ? this.st.rsi.len : kind === "macd" ? this.st.macd.fast+"-"+this.st.macd.slow+"-"+this.st.macd.sig : "");
    this._dv = this._dv || {}; if (!this._dv[kind] || this._dv[kind].k !== k) this._dv[kind] = {k, r:divFind(this.data, series, kind)};
    const lab = kind === "vol" ? "Vol" : kind.toUpperCase(); c.save(); c.font = "bold 9px sans-serif"; c.lineWidth = 1.6;
    this._dv[kind].r.filter(e => e.i2 >= i0 && e.i1 <= i1).forEach(e => { const up = e.side === "up", col = up ? "#0ecb81" : "#f6465d", x1 = X(e.i1), x2 = X(e.i2), y1 = Y(e.i1), y2 = Y(e.i2);
      c.strokeStyle = col; c.fillStyle = col; c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke(); [[x1,y1],[x2,y2]].forEach(([x,y]) => { c.beginPath(); c.arc(x, y, 2.4, 0, 6.3); c.fill(); });
      c.textAlign = "center"; c.fillText(lab+(up ? " ▲" : " ▼"), x2, up ? y2 - 5 : y2 + 11); });
    c.restore();
  },
  paintLv(c, py, PR){   // Daily / 4H / Weekly / Monthly open (solid) and the previous period's open (dashed); the previous close of a 24/7 market IS the new open, so it shares the label
    const L = this.lvD; if (!L) return; const defs = [["4H","#4aa3ff"],["D","#ffd54f"],["W","#ff9800"],["M","#ba68c8"]], dec = this.dec != null ? this.dec : 2; c.save(); c.font = "10px sans-serif"; c.textAlign = "right";
    defs.forEach(([k,col]) => { const p = L[k]; if (!p) return; [[p.cur.o, 1, k+" open"], [p.prev.o, 0, k+" prev"]].forEach(([v, solid, lab]) => { const y = py(v); if (!isFinite(y) || y < 0 || y > c.canvas.height) return;
      c.strokeStyle = col; c.globalAlpha = solid ? .85 : .55; c.lineWidth = 1; c.setLineDash(solid ? [] : [4,4]); c.beginPath(); c.moveTo(0, y+.5); c.lineTo(PR, y+.5); c.stroke(); c.setLineDash([]); c.globalAlpha = 1; c.fillStyle = col; c.fillText(lab+" "+Number(v).toFixed(v < 1 ? 5 : 2), PR-4, y-3); }); });
    c.restore();
  },
  llPick(k, t, px){   // which edge of the previous candle a timeframe shows: its high or its low. The TradingView script takes "whichever is nearer to the price", which makes the line JUMP from one edge to the other (the whole range of that timeframe: 200-300 USD on BTC 1H / 4H) every time the price ticks across the middle of the candle.
    // Here the choice has hysteresis: it changes only once the price is clearly (a fifth of the range) past the middle, and starts over when a new previous candle arrives.
    const S = this._llSide || (this._llSide = {}), key = t.ph+"|"+t.pl, o = S[k], r = t.ph - t.pl; let side;
    if (!o || o.key !== key || !(r > 0)) side = Math.abs(px - t.ph) < Math.abs(px - t.pl) ? "h" : "l";
    else { const pos = (px - t.pl)/r; side = o.side === "l" ? (pos > 0.7 ? "h" : "l") : (pos < 0.3 ? "l" : "h"); }
    S[k] = {key, side}; return side === "h" ? t.ph : t.pl; },
  paintLL(c, py, PR, i0, i1){   // "MTF Liquidity Levels & Targets" (port of the user's TradingView script): previous-candle high/low per timeframe, X77 EMA77/144 cross target, predictive target number, targets table
    const d = this.data, n = d.length, D = this.llD; if (n < 30) return; const bw = this.bw, last = d[n-1], px = last.c, sym = String(this.sym || "");
    const CFG = {len:30, maxATR:15, minP:70, maxP:170, mult:1.5}, f = v => v == null || !isFinite(v) ? "-" : Number(v).toFixed(v < 1 ? 5 : v < 10 ? 4 : v < 1000 ? 3 : 2);
    let atr = 0; { let tr = [], rma = 0; for (let i = 1; i < n; i++) tr.push(Math.max(d[i].h - d[i].l, Math.abs(d[i].h - d[i-1].c), Math.abs(d[i].l - d[i-1].c))); const L = 14; if (tr.length > L){ rma = tr.slice(0, L).reduce((a, b) => a + b, 0)/L; for (let i = L; i < tr.length; i++) rma = (rma*(L-1) + tr[i])/L; atr = rma; } }
    if (!atr) return; const xl = n - 1, x0 = this.x(xl), xe = x0 + CFG.len*bw; c.save(); c.font = "10px sans-serif"; c.textBaseline = "middle";
    const DEF = [["5M","#fff9c4","#14181f"],["15M","#ff9800","#14181f"],["1H","#4caf50","#ffffff"],["4H","#2196f3","#ffffff"],["D1","#f44336","#ffffff"],["W1","#b0bec5","#14181f"]], use = {};
    const tag = (x, y, txt, bg, fg) => { const w = c.measureText(txt).width + 8; c.fillStyle = bg; c.fillRect(x, y - 7, w, 14); c.fillStyle = fg; c.textAlign = "left"; c.fillText(txt, x + 4, y); };
    // 1) OHL: for each timeframe the previous candle's high or low, whichever is nearer to the price; hidden when farther than maxATR x ATR
    if (D) DEF.forEach(([k, bg, fg]) => { const t = D[k]; if (!t) return; const dh = Math.abs(px - t.ph), dl = Math.abs(px - t.pl), u = this.llPick(k, t, px); use[k] = u; if (Math.min(dh, dl) > atr*CFG.maxATR) return; const y = py(u); if (!isFinite(y) || y < -10 || y > this.PB + 10) return;
      c.strokeStyle = bg; c.lineWidth = k === "W1" ? 3 : 2; c.beginPath(); c.moveTo(x0, y); c.lineTo(Math.min(xe, PR), y); c.stroke(); if (xe < PR) tag(xe, y, f(u)+" | "+k, bg, fg); });
    // 2) X77: the last EMA77 / EMA144 cross -> target = the level inside [min..max pips] nearest to the entry (VWAP, EMA77, EMA144, 1H / 4H / D previous-candle level), else the middle of the range
    const ema = (L) => { const k = 2/(L+1), o = new Array(n); let e = d[0].c; for (let i = 0; i < n; i++){ e = i ? d[i].c*k + e*(1-k) : d[0].c; o[i] = e; } return o; }, e77 = ema(77), e144 = ema(144); let xi = -1, xd = 0; for (let i = n-1; i > 0; i--){ if (e77[i-1] <= e144[i-1] && e77[i] > e144[i]){ xi = i; xd = 1; break; } if (e77[i-1] >= e144[i-1] && e77[i] < e144[i]){ xi = i; xd = -1; break; } }
    let x77 = null; if (xi > 40){ const ent = d[xi].c, pip = /XAU/.test(sym) ? 0.1 : /NAS|US100/.test(sym) ? 0.25 : /BTC/.test(sym) ? 1 : /^Y:.*=X$/.test(sym) ? (/JPY/.test(sym) ? 0.01 : 0.0001) : Math.pow(10, Math.floor(Math.log10(ent)) - 3);
      const mn = ent + xd*CFG.minP*pip, mx = ent + xd*CFG.maxP*pip, inr = v => v != null && isFinite(v) && (xd > 0 ? v > mn && v < mx : v < mn && v > mx); let best = ent + xd*((CFG.minP + CFG.maxP)/2)*pip, bd = 1e18;
      [this.vwV && this.vwV[xi], e77[xi], e144[xi], use["1H"], use["4H"], use["D1"]].forEach(v => { if (inr(v)){ const dd = Math.abs(v - ent); if (dd < bd){ bd = dd; best = v; } } }); x77 = {t:best, dir:xd, ent};
      const y = py(best), rx = x0 + CFG.len*bw; if (isFinite(y) && y > -10 && y < this.PB + 10){ c.strokeStyle = "#ffd700"; c.lineWidth = 3; c.beginPath(); c.moveTo(x0, y); c.lineTo(Math.min(rx, PR), y); c.stroke();
        if (rx + 12*bw < PR){ const bh = Math.abs(py(best + atr*0.15) - py(best - atr*0.15)); c.fillStyle = "#ffd700"; c.strokeStyle = "#14181f"; c.lineWidth = 2; c.fillRect(rx - 2*bw, y - bh/2, 10*bw, bh); c.strokeRect(rx - 2*bw, y - bh/2, 10*bw, bh); c.fillStyle = "#ffd700"; c.font = "bold 12px sans-serif"; c.textAlign = "left"; c.fillText("X77 "+f(best), rx + 9*bw, y); c.font = "10px sans-serif"; } } }
    // 3) predictive target number above the last candle: price +/- 1.5 ATR in the direction of the average 3 / 5-bar momentum; gold when a previous-candle high/low sits between the price and the target, grey when the last candle goes against it
    const mom = ((px - d[n-4].c)/3 + (px - d[n-6].c)/5)/2, bull = (this._llBull == null || Math.abs(mom) > atr*0.08) ? (this._llBull = mom > 0) : this._llBull, tUp = px + atr*CFG.mult, tDn = px - atr*CFG.mult, cur = bull ? tUp : tDn; let cross = false;
    if (D) DEF.forEach(([k]) => { const t = D[k]; if (!t) return; if (bull ? (t.ph > px && t.ph <= tUp) : (t.pl < px && t.pl >= tDn)) cross = true; });
    { const col = cross ? "#ffb800" : (bull && last.c < last.o) || (!bull && last.c > last.o) ? "#9e9e9e" : bull ? "#00e676" : "#ff5252", y = py(last.h + atr*0.5); c.fillStyle = col; c.font = "bold 18px sans-serif"; c.textAlign = "center"; if (isFinite(y)) c.fillText(f(cur), x0, Math.max(12, y)); }
    // 4) targets table (bottom right of the plot): per timeframe close +/- 1.5 / 2 / 2.5 ATR of THAT timeframe, direction = its 3-bar momentum
    if (D && this.llTbl !== false){ const rows = [["5M","5M"],["15M","15M"],["1H","1H"],["4H","4H"],["D1","D1"]], rh = 16, tw = 176, tx = PR - tw - 8, th = rh*(rows.length + 2), ty = this.PB - th - 8; c.font = "10px sans-serif"; c.fillStyle = "rgba(27,31,43,.94)"; c.fillRect(tx, ty, tw, th); c.strokeStyle = "#4a505c"; c.lineWidth = 1; c.strokeRect(tx + .5, ty + .5, tw, th);
      c.fillStyle = "#4a505c"; c.fillRect(tx, ty, tw, rh); c.fillStyle = "#f5f7fa"; c.textAlign = "left"; c.fillText("TF", tx + 6, ty + rh/2); c.textAlign = "center"; c.fillText("Target", tx + tw/2, ty + rh/2); c.textAlign = "right"; c.fillText("Dir", tx + tw - 6, ty + rh/2);
      const M = {"5M":1.5, "15M":1.5, "1H":2, "4H":2, "D1":2.5}; rows.forEach(([k], i) => { const t = D[k], y = ty + rh*(i + 1) + rh/2; c.fillStyle = "#8a93a3"; c.textAlign = "left"; c.fillText(k, tx + 6, y); if (!t){ c.textAlign = "center"; c.fillText("n/a", tx + tw/2, y); return; } const up = t.mom > 0, col = up ? "#00e676" : "#ff5252"; c.fillStyle = col; c.textAlign = "center"; c.fillText(f(t.cl + (up ? t.atr : -t.atr)*M[k]), tx + tw/2, y); c.textAlign = "right"; c.fillText(up ? "UP" : "DN", tx + tw - 6, y); });
      const y = ty + rh*(rows.length + 1) + rh/2; c.fillStyle = "rgba(255,215,0,.15)"; c.fillRect(tx, ty + rh*(rows.length + 1), tw, rh); c.fillStyle = "#ffd700"; c.textAlign = "left"; c.fillText("X77", tx + 6, y); c.textAlign = "center"; c.fillText(x77 ? f(x77.t) : "None", tx + tw/2, y); c.textAlign = "right"; c.fillText(x77 ? (x77.dir > 0 ? "UP" : "DN") : "—", tx + tw - 6, y);
      { const bx = tx + tw - 16, by = ty - 17; c.fillStyle = "rgba(27,31,43,.92)"; c.fillRect(bx, by, 16, 15); c.fillStyle = "#f6465d"; c.textAlign = "center"; c.fillText("✕", bx + 8, by + 7.5); this._llX = {x:bx, y:by, w:16, h:15}; } }   // ✕ = hide the targets table
    else if (!D){ const err = this.llErr && Date.now() - this.llErr < 120000; c.font = "9px sans-serif"; c.fillStyle = err ? "#b08a3a" : "#6b7684"; c.textAlign = "right"; c.fillText(err ? "MTF LLT: waiting for the exchange (retrying)" : "MTF LLT: loading…", PR - 8, this.PB - 8); }   // small and quiet: it used to be a big sentence in the middle of the chart that never changed
    c.restore();
  },
  paintMt5(c, py, i0, i1){   // MT5-style pack seen on the user's phone chart: SMA ribbon (5 lines), Parabolic SAR (yellow diamonds), Bill Williams fractals (red arrow above a swing high, green arrow below a swing low)
    const d = this.data, n = d.length, S = this.st.mt5; if (n < 8) return; c.save();
    if (S.rib){ [[S.p1,"#4caf50",1],[S.p2,"#e040fb",1],[S.p3,"#2979ff",1.2],[S.p4,"#ff9800",1.4],[S.p5,"#f6465d",2]].forEach(([L, col, w]) => { L |= 0; if (L < 2 || n < L) return; c.strokeStyle = col; c.lineWidth = w; c.beginPath(); let sum = 0, f = true;
      const k_ = 2/(L+1); let e = null; for (let i = 0; i < n; i++){ sum += d[i].c; if (i >= L) sum -= d[i-L].c; e = e == null ? d[i].c : d[i].c*k_ + e*(1-k_); if (i < L-1 || i < i0 - 1 || i > i1 + 1) continue; const x = this.x(i), y = py(S.ema ? e : sum/L); f ? c.moveTo(x, y) : c.lineTo(x, y); f = false; } c.stroke(); }); }
    if (S.sar){ const P_ = psarOf(d, S.step, S.step, S.max); c.fillStyle = "#ffeb3b";   // same TradingView ta.sar rule as the stand-alone Parabolic SAR
      for (let i = Math.max(1, i0); i <= Math.min(n - 1, i1); i++){ if (P_.v[i] == null) continue; const x = this.x(i), y = py(P_.v[i]); c.beginPath(); c.moveTo(x, y - 3); c.lineTo(x + 3, y); c.lineTo(x, y + 3); c.lineTo(x - 3, y); c.closePath(); c.fill(); } }
    if (S.frc){ const k = Math.max(1, S.fr | 0); c.lineWidth = 1.4;
      for (let i = Math.max(k, i0); i <= Math.min(n - 1 - k, i1); i++){ let hi = true, lo = true; for (let j = 1; j <= k; j++){ if (!(d[i].h >= d[i-j].h && d[i].h > d[i+j].h)) hi = false; if (!(d[i].l <= d[i-j].l && d[i].l < d[i+j].l)) lo = false; }   // MT5 rule: strict vs the newer bars, >= vs the older ones
        const x = this.x(i); if (hi){ const y = py(d[i].h) - 6; c.strokeStyle = c.fillStyle = "#f6465d"; c.beginPath(); c.moveTo(x, y); c.lineTo(x, y - 12); c.stroke(); c.beginPath(); c.moveTo(x, y - 14); c.lineTo(x - 3.5, y - 8); c.lineTo(x + 3.5, y - 8); c.fill(); }
        if (lo){ const y = py(d[i].l) + 6; c.strokeStyle = c.fillStyle = "#0ecb81"; c.beginPath(); c.moveTo(x, y); c.lineTo(x, y + 12); c.stroke(); c.beginPath(); c.moveTo(x, y + 14); c.lineTo(x - 3.5, y + 8); c.lineTo(x + 3.5, y + 8); c.fill(); } } }
    c.restore();
  },
  paintDon(c, py, i0, i1){   // Donchian channels (highest / lowest CLOSE of the previous n bars) for three horizons + how many of the ensemble's channels are in an up / down breakout
    const cl = this.data.map(d => d.c), n_ = cl.length, cols = {20:"#81c784", 60:"#4aa3ff", 150:"#b57cff"};
    c.save(); c.lineWidth = 1;
    [20, 60, 150].forEach(L => { if (n_ < L + 2) return; c.strokeStyle = cols[L]; c.globalAlpha = .75; ["u","l"].forEach(k => { c.beginPath(); let f = true;
      for (let i = Math.max(i0, L); i <= i1; i++){ let v = k === "u" ? -Infinity : Infinity; for (let j = i-L; j < i; j++) v = k === "u" ? Math.max(v, cl[j]) : Math.min(v, cl[j]); const x = this.x(i), y = py(v); f ? c.moveTo(x,y) : c.lineTo(x,y); f = false; } c.stroke(); }); });
    const lbs = DON_LB.filter(L => n_ >= L + 10); let up = 0, dn = 0; lbs.forEach(L => { const s_ = donState(cl, L)[0]; if (s_ > 0) up++; else if (s_ < 0) dn++; });
    c.globalAlpha = 1; c.font = "bold 10px sans-serif"; c.fillStyle = up >= dn ? "#0ecb81" : "#f6465d"; c.fillText("Donchian "+(lbs.length ? (up >= dn ? "▲ "+up : "▼ "+dn)+"/"+lbs.length : "n/a")+"  (20/60/150)", 8, 36); c.restore();
  },
  paintMsb(c, py, i0, i1){   // MSB: market structure break lines + Order Block (Bu-/Be-OB) + Breaker / Mitigation Block (Bu-/Be-BB, -MB); see msbCalc
    const n = this.data.length; if (n < 20) return; const key = n+"|"+this.data[n-1].c+"|"+this.data[0].t; if (!this._msb || this._msb.k !== key){ let r = {zz:[], ev:[], boxes:[]}; try { r = msbCalc(this.data, 9, 0.33); } catch(e){} this._msb = {k:key, r}; }
    const R = this._msb.r, G = "#0ecb81", Rd = "#f6465d", xr = this.x(n - 1 + 10);
    c.save(); c.font = "10px sans-serif"; c.textBaseline = "middle";
    const live = {ob:{}, bb:{}}; R.boxes.forEach(B => { if (B.end < 0) (live[B.kind][B.bull] = live[B.kind][B.bull] || []).push(B); });
    const keep = new Set(); Object.values(live).forEach(o => Object.values(o).forEach(a => a.slice(-5).forEach(B => keep.add(B))));
    R.boxes.forEach(B => { if (B.end >= 0 || !keep.has(B)) return; const xa = this.x(B.i), y1 = py(B.hi), y2 = py(B.lo); if (this.x(n - 1) < 0 || xr < xa) return; const col = B.bull ? G : Rd;
      c.globalAlpha = B.kind === "ob" ? .22 : .14; c.fillStyle = col; c.fillRect(xa, y1, xr - xa, y2 - y1); c.globalAlpha = .9; c.strokeStyle = col; c.lineWidth = 1; c.strokeRect(xa + .5, y1 + .5, xr - xa, y2 - y1);
      c.fillStyle = col; c.textAlign = "right"; c.fillText(B.lbl, xr - 3, (y1 + y2)/2); });
    R.ev.forEach(E => { if (E.t < i0 - 400 || this.x(E.x0) > this.W) return; const col = E.bull ? G : Rd, y = py(E.y); c.globalAlpha = 1; c.strokeStyle = col; c.lineWidth = 2; c.beginPath(); c.moveTo(this.x(E.x0), y); c.lineTo(this.x(E.x1), y); c.stroke();
      c.fillStyle = col; c.font = "bold 10px sans-serif"; c.textAlign = "center"; c.fillText("MSB", this.x(E.xm), y + (E.bull ? -8 : 8)); });
    c.restore();
  },
  paintBB(c, py, dec, i0, i1){   // Bollinger bands (period / deviation from the BB+Stoch+OsMA indicator settings)
    const B = this.bsoV; if (!B) return; const line = (arr, col, w) => { c.strokeStyle = col; c.lineWidth = w; c.beginPath(); for (let i = i0; i <= i1; i++){ const x = this.x(i), y = py(arr[i]); i === i0 ? c.moveTo(x,y) : c.lineTo(x,y); } c.stroke(); };
    c.save(); c.globalAlpha = .07; c.fillStyle = "#26c6da"; c.beginPath(); for (let i = i0; i <= i1; i++){ const x = this.x(i), y = py(B.up[i]); i === i0 ? c.moveTo(x,y) : c.lineTo(x,y); } for (let i = i1; i >= i0; i--) c.lineTo(this.x(i), py(B.lo[i])); c.fill();
    c.globalAlpha = .85; line(B.up, "#26c6da", 1); line(B.lo, "#26c6da", 1); c.setLineDash([4,3]); line(B.mid, "#26c6da", 1); c.setLineDash([]); c.restore();
  },
  paintX(c, k, y0, h, i0, i1, PR){   // the three extra oscillator panes: zn = scalp zones (Stoch+RSI), bso = Bollinger + Stoch + OsMA, rm = RSI + MA with extreme levels
    const st = this.st[k], y = v => y0 + h - 2 - v/100*(h-4), L = (v, col, dash) => { c.strokeStyle = col; c.lineWidth = 1; c.setLineDash(dash || []); c.beginPath(); c.moveTo(0, y(v)+.5); c.lineTo(PR, y(v)+.5); c.stroke(); c.setLineDash([]); };
    const path = (arr, col, w, dash) => { c.strokeStyle = col; c.lineWidth = w; c.setLineDash(dash ? dash.split(",").map(Number) : []); c.beginPath(); for (let i = i0; i <= i1; i++){ const yy = y(arr[i]), x = this.x(i); i === i0 ? c.moveTo(x,yy) : c.lineTo(x,yy); } c.stroke(); c.setLineDash([]); };
    const mark = (i, up, txt) => { if (st.sg === false) return; const x = this.x(i), yy = up ? y0 + h - 8 : y0 + 9; c.fillStyle = up ? "#0ecb81" : "#f6465d"; c.font = "bold 9px sans-serif"; c.textAlign = "center"; c.fillText((up ? "▲ " : "▼ ")+txt, x, yy); c.textAlign = "left"; c.font = "10px ui-monospace,Menlo,Consolas,monospace"; };
    let title = "", labs = [];
    if (k === "zn"){ const Z = this.znV, hi = st.sell, hi2 = hi + 5, lo = st.buy, lo2 = lo - 5;
      c.fillStyle = "rgba(246,70,93,.07)"; c.fillRect(0, y(100), PR, y(hi2) - y(100)); c.fillStyle = "rgba(14,203,129,.07)"; c.fillRect(0, y(lo2), PR, y(0) - y(lo2));
      [[hi2,"#f6465d"],[hi,"#f6465d"],[50,"#8a94a3"],[lo,"#0ecb81"],[lo2,"#0ecb81"]].forEach(([v,col]) => L(v, col, v === 50 ? [] : [3,3]));
      c.globalAlpha = .18; c.fillStyle = st.color; c.beginPath(); c.moveTo(this.x(i0), y(50)); for (let i = i0; i <= i1; i++) c.lineTo(this.x(i), y(Z.k[i])); c.lineTo(this.x(i1), y(50)); c.fill(); c.globalAlpha = 1;
      { const cl = this.data.map(d => d.c), ea = (L) => { const kk = 2/(L+1); let e = cl[0]; return cl.map(v => (e = v*kk + e*(1-kk))); }, e1 = ea(12), e2 = ea(26), mc = e1.map((v, i) => v - e2[i]); let mx = 1e-12; for (let i = i0; i <= i1; i++) mx = Math.max(mx, Math.abs(mc[i]));   // MACD(12,26,1) as grey bars (signal period 1 = the MACD line itself), as in the MT5 pane
        const bw = Math.max(1, this.bw*0.5); for (let i = i0; i <= i1; i++){ const x = this.x(i), v = mc[i]/mx*(h/2 - 3), y5 = y(50); c.fillStyle = "rgba(160,168,180,.35)"; c.fillRect(x - bw/2, Math.min(y5, y5 - v), bw, Math.max(1, Math.abs(v))); } }
      path(Z.r, "rgba(181,124,255,.55)", 1); path(Z.d, st.color2, 1, "3,3"); path(Z.k, st.color, st.w);
      for (let i = Math.max(i0, 1); i <= i1; i++){ if (Z.k[i-1] >= hi && Z.k[i] < hi) mark(i, false, "SELL"); else if (Z.k[i-1] <= lo && Z.k[i] > lo) mark(i, true, "BUY"); }
      title = "Scalp zones · Stoch "+st.k+","+st.d+","+st.s+" · RSI "+st.rl+"  K "+(Z.k[Math.min(i1, Z.k.length-1)]||0).toFixed(1); labs = [[hi2,"Sell"],[50,"TP"],[lo,"Buy"]]; }
    else if (k === "rm"){ const R = this.rmV;
      [[st.hi,"#f6465d",[]],[90,"#7a3a44",[3,3]],[80,"#7a3a44",[3,3]],[70,"#3a424b",[3,3]],[50,"#1f252b",[]],[30,"#3a424b",[3,3]],[20,"#2f6b53",[3,3]],[10,"#2f6b53",[3,3]],[st.lo,"#0ecb81",[]]].forEach(([v,col,d]) => L(v, col, d));
      path(R.r, st.color, st.w); path(R.m, st.color2, st.w + .2); (R.ex || []).forEach(x => path(x.a, x.col, st.w));
      for (let i = Math.max(i0, 1); i <= i1; i++){ if (R.r[i-1] >= st.hi && R.r[i] < st.hi) mark(i, false, "SELL"); else if (R.r[i-1] <= st.lo && R.r[i] > st.lo) mark(i, true, "BUY"); }
      title = "RSI "+st.len+" + MA "+st.ma+((R.ex || []).length ? " / "+R.ex.map(x => x.n).join(" / ") : "")+" · extremes "+st.hi+" / "+st.lo+"  RSI "+(R.r[Math.min(i1, R.r.length-1)]||0).toFixed(1); labs = [[st.hi,String(st.hi)],[st.lo,String(st.lo)]]; }
    else if (k === "r2"){ const Q = this.r2V; if (!Q) { c.restore(); return; } const bw = Math.max(1, this.bw*0.5), UP = "#0ecb81", DN = "#f6465d", LV = 10;   // same colours as the candles
      for (let i = i0; i <= i1; i++){ const v = Q.osma[i]; if (!(v > 0)) continue; const x = this.x(i), hh = Math.min(100, v)/100*(h - 4); c.fillStyle = v <= LV ? UP : DN; c.globalAlpha = .8; c.fillRect(x - bw/2, y0 + h - 2 - hh, bw, Math.max(1, hh)); c.globalAlpha = 1; }   // OsMA bars on the same 0-100 scale as the RSI (like MT5: negative values fall below the pane and are not shown). Bar at/under the 10 line = up (green), above it = down (red)
      [[30,"#3a424b",[3,3]],[20,"#3a424b",[3,3]],[LV,"#8a94a3",[]],[5,"#3a424b",[3,3]]].forEach(([v,col,d]) => L(v, col, d));   // (the RSI(2) line itself is no longer drawn - bars only)
      for (let i = Math.max(i0, 1); i <= i1; i++){ const a = Q.osma[i-1], b = Q.osma[i]; if (a > LV && b > 0 && b <= LV) mark(i, true, ""); else if (a > 0 && a <= LV && b > LV) mark(i, false, ""); }
      title = "";   // no title / hit-rate text: bars, level lines and arrows only
      labs = [[30,"30"],[20,"20"],[LV,"10"],[5,"5"]]; }
    else { const B = this.bsoV; let mx = 1e-12; for (let i = i0; i <= i1; i++) mx = Math.max(mx, Math.abs(B.osma[i]));
      const yo = v => y0 + h/2 - v/mx*(h/2 - 3), bw = Math.max(1, this.bw*0.6);
      for (let i = i0; i <= i1; i++){ const v = B.osma[i], x = this.x(i); c.fillStyle = v >= 0 ? "rgba(14,203,129,.32)" : "rgba(246,70,93,.32)"; c.fillRect(x-bw/2, Math.min(yo(v), yo(0)), bw, Math.max(1, Math.abs(yo(v)-yo(0)))); }
      L(80, "#3a424b", [3,3]); L(50, "#1f252b"); L(20, "#3a424b", [3,3]); path(B.k, st.color, st.w); path(B.d, st.color2, st.w);
      for (let i = Math.max(i0, 1); i <= i1; i++){ if (B.k[i-1] >= 80 && B.k[i] < 80 && B.k[i] < B.d[i]) mark(i, false, "SELL"); else if (B.k[i-1] <= 20 && B.k[i] > 20 && B.k[i] > B.d[i]) mark(i, true, "BUY"); }
      title = "Bollinger "+st.bb+","+st.dev+" · Stoch "+st.k+","+st.d+","+st.s+" · OsMA "+st.fast+","+st.slow+","+st.sig; labs = [[80,"80"],[20,"20"]]; }
    c.restore(); c.fillStyle = "#848e9c"; c.font = "10px ui-monospace,Menlo,Consolas,monospace"; c.fillText(title, 6, y0+8); labs.forEach(([v,t]) => c.fillText(t, (this.W-this.axw)+5, y(v)+3));
  },
  paintSmt(c, py, dec, i0, i1){   // the correlated market drawn on THIS chart (rescaled) + SMT divergences between the two, marked swing to swing
    const D = this.smtD; if (!D || !D.length || !this.data.length){ if (this.smtName){ c.save(); c.font = "10px sans-serif"; c.fillStyle = "#ffd54f"; c.fillText("SMT: "+this.smtName, 8, 24); c.restore(); } return; } const mp = new Map(D.map(x => [x.t, x])), inv = !!this.smtInv, A = [], B = [];
    this.data.forEach((x, i) => { const q = mp.get(x.t); if (q){ A.push(Object.assign({i}, x)); B.push(q); } }); if (A.length < 40) return;
    const idx = new Map(A.map((x, k) => [x.i, k]));
    let mn = Infinity, mx = -Infinity, pmn = Infinity, pmx = -Infinity; for (let i = i0; i <= i1; i++){ const d = this.data[i]; if (!d) continue; mn = Math.min(mn, d.l); mx = Math.max(mx, d.h); const k = idx.get(i); if (k != null){ const v = inv ? -B[k].c : B[k].c; pmn = Math.min(pmn, v); pmx = Math.max(pmx, v); } }
    if (!isFinite(pmn) || pmx <= pmn) return; const sc = v => mn + (v - pmn)/(pmx - pmn)*(mx - mn), pv = (k, key) => sc(inv ? -(key === "h" ? B[k].l : B[k].h) : B[k][key] );
    c.save();   // (the dashed yellow line of the correlated market was removed on request; only the divergence marks are drawn)
    c.globalAlpha = 1; c.font = "10px sans-serif"; c.fillStyle = "#ffd54f"; c.fillText("SMT ⇄ "+(this.smtName || "")+(inv ? " (inverse)" : "")+"  ·  "+(this.smtD.length ? "" : ""), 8, 24);
    smtFind(A, B, inv).filter(e => A[e.i2].i >= i0 - 5).forEach(e => { const up = e.side === "up", col = up ? "#0ecb81" : "#f6465d", a1 = A[e.i1], a2 = A[e.i2], key = up ? "l" : "h";
      c.strokeStyle = col; c.lineWidth = 1.4; c.beginPath(); c.moveTo(this.x(a1.i), py(a1[key])); c.lineTo(this.x(a2.i), py(a2[key])); c.stroke();                       // the market that made the new extreme
      c.strokeStyle = "#ffd54f"; c.lineWidth = 1.4; c.beginPath(); c.moveTo(this.x(A[e.j1].i), py(pv(e.j1, key))); c.lineTo(this.x(A[e.j2].i), py(pv(e.j2, key))); c.stroke();   // ... and the one that refused
      const x = this.x(a2.i), y = py(a2[key]) + (up ? 16 : -16); c.fillStyle = "#0b0e11"; c.fillRect(x-17, y-8, 34, 14); c.strokeStyle = col; c.strokeRect(x-17, y-8, 34, 14); c.fillStyle = col; c.textAlign = "center"; c.fillText("SMT "+(up ? "▲" : "▼"), x, y+3); c.textAlign = "left"; });
    c.restore();
  },
  paintVp(c, py, dec, PR, PB, i0, i1){   // volume profile v3: ONE slim column on the right. length = traded volume, colour = delta (who won, stronger = more one-sided), thin heat strip on its left edge = resting limit orders (order book)
    const DEF = {v:3, mode:"vd", range:"vis", rowpx:3, wpct:10, lbl:0, book:1, walls:1};
    if (!this.st.vp || this.st.vp.v !== 3) this.st.vp = Object.assign({}, DEF);   // older wide layouts reset once
    const G = Object.assign({}, DEF, this.st.vp), n = this.data.length; if (!n) return;
    const a0 = G.range === "vis" ? Math.max(0, i0|0) : 0, a1 = G.range === "vis" ? Math.min(n-1, (i1 == null ? n-1 : i1)|0) : n-1, fpN = this.fp ? this.fp.size : 0;
    const k = [a0, a1, n, fpN, Math.floor(Date.now()/1500)].join(":");   // rebuild at most every 1.5 s or when the view / trades change (every tick was too heavy with several charts)
    if (!this._vp2 || this._vp2.k !== k){ let real = 0;
      const rows = this.data.slice(a0, a1 + 1).map(d => { const f = this.fp && this.fp.get(d.t);
        if (f && f.px && f.px.size){ let tb = 0; f.px.forEach(v => tb += v.b + v.s); if (tb > 0){ real++; const sc = (d.v || tb)/tb; return {l:d.l, h:d.h, pts:[...f.px].map(([p, v]) => [+p, (v.b + v.s)*sc, (v.b - v.s)*sc])}; } }
        const rg = d.h - d.l; return {l:d.l, h:d.h, v:d.v, tp:(d.h + d.l + d.c)/3, d:rg > 0 ? (2*(d.c - d.l)/rg - 1)*(d.v || 0) : 0}; });   // no trades: delta estimated from where the candle closed
      this._vp2 = {k, v:vpCalc2(rows, 60), f:vpCalc2(rows, 1200), real, cnt:rows.length}; }
    const vp = this._vp2.v, fn = this._vp2.f; if (!vp || !fn) return;
    const bw = Math.max(48, Math.min(170, (PR||this.W)*(Math.max(5, Math.min(30, +G.wpct || 10))/100))), x0 = PR - bw, buyC = this.st.of.color, sellC = this.st.of.color2, neu = TH.mut, SW = G.book ? 5 : 0;
    const binPx = Math.abs(py(fn.lo) - py(fn.lo + fn.st)), g = Math.max(1, Math.ceil(Math.max(1, +G.rowpx || 3)/Math.max(.01, binPx))), rs = fn.st*g;
    const rowsD = []; for (let i = 0; i < fn.bins.length; i += g){ let v = 0, dl = 0; for (let j = i; j < Math.min(fn.bins.length, i+g); j++){ v += fn.bins[j]; dl += fn.dl[j]; } rowsD.push({i, v, dl, n:Math.min(g, fn.bins.length-i)}); }
    const mx = Math.max(...rowsD.map(r => r.v), 1e-9), mxD = Math.max(...rowsD.map(r => Math.abs(r.dl)), 1e-9), pocR = rowsD.reduce((m, r) => r.v > m.v ? r : m, rowsD[0]), L = bw - SW - 2;
    c.save(); c.globalAlpha = .55; c.fillStyle = TH.bg || "#0b0e11"; c.fillRect(x0, 0, bw, PB); c.restore();   // quiet backdrop so the column reads as one piece
    c.font = "9px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "left";
    rowsD.forEach(r => { const y1 = py(fn.lo+(r.i+r.n)*fn.st), y0 = py(fn.lo+r.i*fn.st); if (y0 < 0 || y1 > PB || !(r.v > 0)) return;
      const rh = Math.max(1, y0-y1-(y0-y1 > 3 ? 1 : 0)), mp = fn.lo+(r.i+r.n/2)*fn.st, inVA = mp >= vp.val && mp <= vp.vah, dc = r.dl >= 0 ? buyC : sellC, imb = Math.abs(r.dl)/Math.max(1e-9, r.v);
      if (G.mode === "delta"){ const w = L*Math.abs(r.dl)/mxD; c.globalAlpha = .35 + .6*imb; c.fillStyle = dc; c.fillRect(PR - w, y1, w, rh); }
      else if (G.mode === "split"){ const w = L*r.v/mx, wb = w*Math.max(0, (r.v + r.dl)/2)/r.v; c.globalAlpha = inVA ? .7 : .45; c.fillStyle = buyC; c.fillRect(PR-w, y1, wb, rh); c.fillStyle = sellC; c.fillRect(PR-w+wb, y1, w-wb, rh); }
      else { const w = L*r.v/mx; c.globalAlpha = inVA ? .3 : .16; c.fillStyle = neu; c.fillRect(PR - w, y1, w, rh);   // length = volume, colour fills the part that was one-sided
        const wd = w*Math.min(1, .45 + imb); c.globalAlpha = Math.min(1, .5 + .6*imb); c.fillStyle = dc; c.fillRect(PR - wd, y1, wd, rh); }
      c.globalAlpha = 1; if (r === pocR){ c.fillStyle = "#f0b90b"; c.fillRect(PR - L*r.v/mx, y1, 2, rh); }
      if (G.lbl && rh >= 8){ const t = (r.dl >= 0 ? "+" : "−")+fmtV(Math.abs(r.dl)); c.fillStyle = "rgba(234,236,239,.85)"; c.fillText(t, x0 + SW + 3, y1 + rh/2 + 3); } });
    let bkTxt = ""; if (G.book && this.bkS && this.bkS.size){   // resting limit orders, smoothed per poll (flicker fades, lasting walls build): heat strip, brighter = more size
      const bk = this.bkN + "|" + fn.lo + "|" + rs; if (!this._bkB || this._bkB.k !== bk){ const B = new Map(); let pMin = Infinity, pMax = -Infinity;   // buckets only change with a new book snapshot or a new row grid
        this.bkS.forEach((o, p) => { const j = Math.floor((p - fn.lo)/rs); let e = B.get(j); if (!e){ e = {b:0, a:0, n:0}; B.set(j, e); } e[o.sd] += o.q; e.n = Math.max(e.n, o.n); if (p < pMin) pMin = p; if (p > pMax) pMax = p; });
        this._bkB = {k:bk, B, pMin, pMax}; } const B = this._bkB.B, pMin = this._bkB.pMin, pMax = this._bkB.pMax;
      const vis = [...B.entries()].map(([j, e]) => ({e, y0:py(fn.lo + j*rs), y1:py(fn.lo + (j+1)*rs)})).filter(q => q.y0 >= 0 && q.y1 <= PB), qs = vis.map(q => q.e.b + q.e.a).sort((a,b) => a-b);
      if (qs.length){ const mxB = qs[qs.length-1] || 1e-9, med = qs[Math.floor(qs.length/2)] || 1e-9, walls = [];
        vis.forEach(q => { const tq = q.e.b + q.e.a, col = q.e.b >= q.e.a ? buyC : sellC, rh = Math.max(1, q.y0 - q.y1); c.globalAlpha = .12 + .88*Math.sqrt(tq/mxB); c.fillStyle = col; c.fillRect(x0, q.y1, SW, rh);
          if (G.walls && tq >= 3*med && tq >= .25*mxB && q.e.n >= 5) walls.push({q, tq, col, rh}); });
        c.globalAlpha = 1; walls.sort((a,b) => b.tq - a.tq).slice(0, 5).forEach(({q, tq, col, rh}) => { const y = q.y1 + rh/2;   // big lasting wall: short tick into the column + size, nothing across the chart
          c.fillStyle = col; c.fillRect(x0 - 4, y - 1, SW + 10, 2); c.font = "bold 9px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "left"; c.fillText(fmtV(tq), x0 + SW + 8, y + 3); });
        const lp = this.data[n-1].c; bkTxt = " · ±"+(Math.max(lp - pMin, pMax - lp)/lp*100).toFixed(1)+"%"; } }
    [["POC",vp.poc,"#f0b90b"],["VAH",vp.vah,"#4aa3ff"],["VAL",vp.val,"#4aa3ff"]].forEach(([nm,p,col]) => { const y = py(p); if (y < 0 || y > PB) return;   // short marks on the column only
      c.globalAlpha = .8; c.strokeStyle = col; c.lineWidth = 1; c.setLineDash(nm === "POC" ? [] : [3,2]); c.beginPath(); c.moveTo(x0 - 6, y+.5); c.lineTo(PR, y+.5); c.stroke(); c.setLineDash([]);
      c.fillStyle = col; c.font = "9px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "right"; c.fillText(nm, x0 - 8, y + 3); c.globalAlpha = 1; });
    { const tb = fn.dl.reduce((a,b) => a+b, 0); c.font = "bold 10px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "right"; c.fillStyle = tb >= 0 ? buyC : sellC;
      c.fillText("Δ "+(tb >= 0 ? "+" : "−")+fmtV(Math.abs(tb))+(this._vp2.real ? "" : " ~")+bkTxt, PR-4, 12); }   // "~" = delta estimated from candles (no trades yet)
    c.textAlign = "left"; c.font = "11px ui-monospace,Menlo,Consolas,monospace";
  },
  ewCount(){   // newest impulse (1-5) + the corrective A-B-C that follows it, from the zigzag pivots; also a lone A-B-C when no impulse fits
    const k = this.data.length + ":" + (this.data.length ? this.data[this.data.length-1].c : 0) + ":" + this.tf; if (this._ew && this._ew.k === k) return this._ew.v;
    const z = harmZigzag(this.data, zzDev(this.data, 2.5, 0.001, 0.025), 3), out = []; let e = z.length;
    for (; e >= 6 && out.length < 2; e--){
      const w = z.slice(e-6, e), up = w[0].k === "L", s = up ? 1 : -1, P = w.map(q => q.p);
      const l1 = s*(P[1]-P[0]), l3 = s*(P[3]-P[2]), l5 = s*(P[5]-P[4]);
      const ok = l1 > 0 && l3 > 0 && l5 > 0 && s*(P[2]-P[0]) > 0 && s*(P[3]-P[1]) > 0 && s*(P[4]-P[1]) > 0 && s*(P[5]-P[3]) > 0 && !(l3 < l1 && l3 < l5);
      if (!ok) continue;
      const abc = z.slice(e, e+3).map((q,i) => ({i:q.i, p:q.p, txt:"ABC"[i], up:q.k === "H"}));
      out.push({up, pts:w.map((q,i) => ({i:q.i, p:q.p, txt:i ? String(i) : "", up:q.k === "H"})), abc, rec:out.length === 0}); e -= 4;
    }
    if (!out.length && z.length >= 4){ const w = z.slice(-4), s = w[0].k === "H" ? -1 : 1;   // A-B-C zigzag: C beyond A, B retraces less than 100% of A
      if (s*(w[1].p - w[0].p) > 0 && s*(w[2].p - w[0].p) > 0 && s*(w[3].p - w[1].p) > 0 && s*(w[3].p - w[2].p) < 0) out.push({up:s > 0, pts:[], abc:w.slice(1).map((q,i) => ({i:q.i, p:q.p, txt:"ABC"[i], up:q.k === "H"})), start:{i:w[0].i, p:w[0].p}, rec:true}); }
    this._ew = {k, v:out}; this._ewf = this.ewForming(z, out); return out;
  },
  ewForming(z, out){   // an impulse still being built (waves 1-4 so far) after the last finished count: pivots only, no forecast; returns {up, pts:[{i,p,txt}], next, broke} or null
    const top = out[0]; let base = -1; if (top){ if (top.abc.length < 3) return null; base = top.abc[2].i; }
    const q = z.filter(x => x.i >= base); if (q.length < 3) return null;
    const rule = (P, s) => P.length > 2 && s*(P[2]-P[0]) <= 0 ? Lg("wave 2 went past the start of wave 1", "الموجة 2 عدّت بداية الموجة 1") : P.length > 3 && s*(P[3]-P[1]) <= 0 ? Lg("wave 3 did not pass the end of wave 1", "الموجة 3 ما عدّتش نهاية الموجة 1") : P.length > 4 && s*(P[4]-P[1]) <= 0 ? Lg("wave 4 overlaps wave 1", "الموجة 4 داخلة في الموجة 1") : null;
    let broke = null;
    for (let m = Math.min(4, q.length-1); m >= 2; m--){
      const w = q.slice(-(m+1)), up = w[0].k === "L", s = up ? 1 : -1, P = w.map(x => x.p);
      if (s*(P[1]-P[0]) <= 0) continue;
      const r = rule(P, s); if (r){ if (!broke) broke = r; continue; }
      return {up, pts:w.map((x, j) => ({i:x.i, p:x.p, txt:j ? String(j) : "", up:x.k === "H"})), next:m+1, broke};
    }
    return null;
  },
  htfList(tf){   // six frames around this chart (owner 2026-10-19: "5 to 6 frames", option 3 = smaller ones too): up to two smaller, then the bigger ones; weekly and monthly are always there when bigger
    const L = ["1m","5m","15m","1H","4H","1D","1W","1M"], i = L.indexOf(tf); if (i < 0) return [];
    const smaller = L.slice(Math.max(0, i-2), i), bigger = L.slice(i+1);
    const pick = [...smaller, ...bigger.slice(0, 4)];
    for (let k = i-3; pick.length < 6 && k >= 0; k--) pick.unshift(L[k]);   // not enough bigger frames near the top: take the next smaller ones
    for (const x of bigger.slice(4)) if (pick.length < 6) pick.push(x);
    return [...new Set(pick)].slice(0, 6);
  },
  htfTrends(){   // [{tf, dir}] for the four bigger timeframes; each is fetched once per 5 min per symbol and shared by all charts
    if (!this.sym) return [];
    const store = HTF_CACHE;
    return this.htfList(this.tf).map(H => {
      const k = this.sym+"|"+H, e = store[k];
      if (!e || (!e.busy && Date.now() - e.t > 300000)){
        store[k] = {t:Date.now(), v:e ? e.v : null, busy:true};
        candlesTf(this.sym, H, true, 120).then(rows => { store[k] = {t:Date.now(), v:htfDir(rows, H), busy:false}; this.draw(); })
          .catch(() => { store[k] = {t:Date.now(), v:null, busy:false}; });
      }
      return store[k] && store[k].v;
    }).filter(Boolean);
  },
  htfNote(c, row){   // "15m ▲  1H ▼  4H ▲  1D ▲  1W ▲  1M ▲" under the indicator notes
    const T = this.htfTrends(); if (!T.length) return;
    this.indNote(c, row, T.map(t => t.tf+" "+(t.dir === "up" ? "▲" : t.dir === "down" ? "▼" : "–")).join("   ")+"  "+Lg("trend", "اتجاه"));
  },
  htfAgainst(up){   // true when most of the bigger timeframes with a known trend point the other way (weekly and monthly count as confirmation)
    const T = this.htfTrends().filter(t => t.dir !== "flat"); if (!T.length) return false;
    const opp = T.filter(t => (t.dir === "up") === (up === false)).length; return opp > T.length/2;
  },
  infoChip(c){   // one fold arrow for all indicator description text (owner 2026-10-19): hides labels only, never the lines / boxes / signals
    this._gChip = null; this._hidChip = null; if (!(this.ewOn || this.harmOn || this.gannOn) && !this.draws.some(d => d.hidden)) return;
    const open = this.infoOpen !== false, gx = this.PR - 22, gy = 4; c.save(); c.fillStyle = "rgba(11,14,17,.75)"; c.fillRect(gx, gy, 18, 14); c.fillStyle = "#9aa4b2"; c.font = "10px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText(open ? "▾" : "▸", gx + 9, gy + 7); c.restore();
    this._gChip = {x:gx, y:gy, w:18, h:14};
    const nh = this.draws.filter(d => d.hidden).length; this._hidChip = null;
    if (nh){ const txt = "◌ "+nh+" "+Lg("hidden: show all","مخفي: إظهار الكل"); c.font = "10px sans-serif"; const w = c.measureText(txt).width + 12, hx = gx - w - 6;
      c.save(); c.fillStyle = "rgba(11,14,17,.75)"; c.fillRect(hx, gy, w, 14); c.fillStyle = "#9aa4b2"; c.font = "10px sans-serif"; c.textAlign = "left"; c.textBaseline = "middle"; c.fillText(txt, hx + 6, gy + 7); c.restore();
      this._hidChip = {x:hx, y:gy, w, h:14}; }
  },
  indNote(c, row, txt){
    if (this.infoOpen === false || this.H < 340 || this.W < 520) return;   // description text folded; also hidden on a small chart (these grey "nothing found" lines would sit on the candles)   // small grey line under the price header: an indicator is ON but found nothing (so "nothing shows" is not mistaken for "broken")
    c.save(); c.font = "10px sans-serif"; c.textAlign = "left"; c.textBaseline = "alphabetic"; const w = c.measureText(txt).width + 10, y = 34 + row*15;
    c.globalAlpha = .7; c.fillStyle = "#000"; c.fillRect(6, y - 11, w, 14); c.globalAlpha = 1; c.fillStyle = "#9aa4b1"; c.fillText(txt, 11, y); c.restore();
  },
  paintEWforming(c, py){   // dashed line through the pivots of the impulse in progress + "forming: wave N next" (and the rule that cancelled a longer count)
    const f = this._ewf; if (!f) return; const col = f.up ? "#0ecb81" : "#f6465d";
    c.save(); c.globalAlpha = .8; c.strokeStyle = col; c.lineWidth = 1.2; c.setLineDash([5,4]); c.beginPath(); f.pts.forEach((q, i) => { const x = this.x(q.i), y = py(q.p); i ? c.lineTo(x, y) : c.moveTo(x, y); }); c.stroke(); c.setLineDash([]);
    c.font = "bold 11px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle"; f.pts.forEach(q => { if (!q.txt) return; const x = this.x(q.i), y = py(q.p), yy = q.up ? y - 13 : y + 13; c.fillStyle = "#0b0e11"; c.beginPath(); c.arc(x, yy, 8, 0, 6.3); c.fill(); c.strokeStyle = col; c.lineWidth = 1; c.stroke(); c.fillStyle = col; c.fillText(q.txt, x, yy + .5); });
    c.restore(); this.indNote(c, 2, Lg("Elliott forming: wave ", "إليوت بيتكوّن: الموجة ")+f.next+Lg(" next", " جاية")+(f.broke ? " · "+Lg("longer count dropped: ", "عدّ أطول اتلغى: ")+f.broke : ""));
  },
  paintEWauto(c, py, dec){
    const list = this.ewCount(); this.paintEWforming(c, py);
    if (!list.length){ this.indNote(c, 1, Lg("Elliott: no wave count on this timeframe yet", "إليوت: مفيش عد موجات على الفريم ده لسه")); return; } if (this.htfAgainst(list[0].up)) this.indNote(c, 3, Lg("Elliott count against the bigger trend", "عد إليوت عكس الاتجاه الأكبر")); const PR = this.PR, PB = this.PB; c.save(); c.beginPath(); c.rect(0,0,PR,PB); c.clip(); c.textAlign = "center"; c.textBaseline = "middle";
    list.forEach((w, n) => { const imp = w.pts.concat(w.abc.length ? [] : []), seq = (w.start ? [w.start] : []).concat(w.pts, w.abc); const col = w.up ? "#0ecb81" : "#f6465d", acol = "#b57cff";
      c.globalAlpha = n ? .45 : 1; c.lineWidth = n ? 1 : 1.6; c.strokeStyle = col; c.beginPath(); w.pts.forEach((q,i) => { const x = this.x(q.i), y = py(q.p); i ? c.lineTo(x,y) : c.moveTo(x,y); }); if (w.pts.length) c.stroke();
      if (w.abc.length){ c.strokeStyle = acol; c.setLineDash([4,3]); c.beginPath(); const first = w.pts.length ? w.pts[w.pts.length-1] : w.start; c.moveTo(this.x(first.i), py(first.p)); w.abc.forEach(q => c.lineTo(this.x(q.i), py(q.p))); c.stroke(); c.setLineDash([]); }
      c.font = "bold 11px sans-serif"; w.pts.concat(w.abc).forEach(q => { if (!q.txt) return; const x = this.x(q.i), y = py(q.p), ab = "ABC".includes(q.txt), cc = ab ? acol : col, yy = q.up ? y - 13 : y + 13;
        c.fillStyle = "#0b0e11"; c.beginPath(); c.arc(x, yy, 8, 0, 6.3); c.fill(); c.strokeStyle = cc; c.lineWidth = 1.2; c.stroke(); c.fillStyle = cc; c.fillText(q.txt, x, yy+.5); });
      if (n === 0 && w.pts.length > 1){   // OTE boxes (62-79% retracement of the impulse leg) where waves 2 / 4 / A end or are expected to end; the newest one runs to the right edge
        const P = w.pts, xe = this.x(this.data.length-1) + this.bw/2; c.save();
        for (let k = 0; k + 1 < P.length; k += 2){ const a0 = P[k].p, b0 = P[k+1].p, z1 = b0 - (b0 - a0)*0.618, z2 = b0 - (b0 - a0)*0.786, nxt = P[k+2], live = !nxt, x0 = this.x(P[k+1].i), x1 = nxt ? this.x(nxt.i) : Math.max(x0 + 24, xe), y1 = py(Math.max(z1, z2)), y2 = py(Math.min(z1, z2));
          let inZ = false; if (live) for (let j = P[k+1].i + 1; j < this.data.length && !inZ; j++){ const b = this.data[j]; inZ = b.l <= Math.max(z1, z2) && b.h >= Math.min(z1, z2); }   // confirmed bars after the impulse endpoint have traded into the zone
          if (!live || this.oteAlways || inZ){ c.globalAlpha = live ? .2 : .09; c.fillStyle = "#f0b90b"; c.fillRect(x0, y1, x1 - x0, Math.max(2, y2 - y1)); c.globalAlpha = live ? .75 : .35; c.strokeStyle = "#f0b90b"; c.lineWidth = 1; c.setLineDash([4,3]); c.strokeRect(Math.round(x0)+.5, Math.round(y1)+.5, x1 - x0, Math.max(2, y2 - y1)); c.setLineDash([]);
            if (live){ c.globalAlpha = .95; c.fillStyle = "#f0b90b"; c.font = "bold 9px sans-serif"; c.textAlign = "left"; c.fillText("OTE 62-79% · "+Lg("in zone", "داخل المنطقة"), x0 + 3, y1 - 3); } } }
        c.restore(); c.textAlign = "center"; }
      if (n === 0 && w.pts.length > 2){   // Fib retracement % on each corrective wave endpoint (2, 4, A)
        const P = w.pts; c.font = "bold 9px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "center";
        for (let k = 2; k < P.length; k += 2){   // P[0] = start, P[i] = end of wave i: even indices 2 and 4 end the corrective waves
          const imp = Math.abs(P[k-1].p - P[k-2].p);   // retracement of the impulse leg before it (wave 1 for wave 2, wave 3 for wave 4)
          const pct = imp > 0 ? Math.round(Math.abs(P[k].p - P[k-1].p) / imp * 1000) / 10 : null;
          if (pct === null || !isFinite(pct)) continue;
          const x = this.x(P[k].i), y = py(P[k].p), above = P[k].up; // corrective wave point — below the prior high (bull)
          c.globalAlpha = .85; c.fillStyle = "#cfd6dd";
          c.fillText(pct.toFixed(1)+"%", x, y + (above ? -22 : 22));
        }
        // A wave Fib (first abc point) when abc exists
        if (w.abc.length > 0 && w.pts.length >= 2){
          const lastImp = w.pts[w.pts.length-1], prevImp = w.pts[w.pts.length-2], A = w.abc[0];
          const rng = Math.abs(lastImp.p - prevImp.p);
          if (rng > 0){ const pct = Math.round(Math.abs(A.p - lastImp.p) / rng * 1000) / 10;
            if (isFinite(pct)){ const x = this.x(A.i), y = py(A.p); c.globalAlpha = .85; c.fillStyle = "#b57cff"; c.fillText(pct.toFixed(1)+"%", x, y + (A.up ? -22 : 22)); } }
        }
        c.textAlign = "center"; }
      if (n === 0 && w.pts.length){ const q = w.pts[1]; c.font = "9px sans-serif"; c.fillStyle = col; c.globalAlpha = .9; c.fillText("EW · "+this.tf+(w.up ? " ▲" : " ▼"), this.x(w.pts[0].i)+6, py(w.pts[0].p) + (w.up ? 14 : -14)); } });
    c.restore(); c.font = "11px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "left"; c.textBaseline = "alphabetic"; c.globalAlpha = 1;
  },
  paintHarm(c, py, dec){   // XABCD legs + ratio labels, PRZ box, and the pattern's own trade box (Entry / SL / TP) - separate from the scanner signal box
    const k = this.data.length + ":" + (this.data.length ? this.data[this.data.length-1].c : 0);
    if (!this._harm || this._harm.k !== k) this._harm = {k, list:harmFind(this.data, 5)};   // up to 5 patterns from the loaded bars (newest first)
    if (!this._harm.list.length){ this.indNote(c, 0, Lg("Harmonic: no XABCD pattern on this timeframe yet", "هارمونيك: مفيش نموذج XABCD على الفريم ده لسه")); return; } if (this.htfAgainst(this._harm.list[0].dir === "bull")) this.indNote(c, 3, Lg("Harmonic pattern against the bigger trend", "نمط هارمونيك عكس الاتجاه الأكبر"));
    const nm = ["X","A","B","C","D"], n = this.data.length, PRx = this.PR, F = v => Number(v).toFixed(dec), fs = "bold 10px ui-monospace,Menlo,Consolas,monospace";
    this._harm.list.forEach((h, q) => {
      // task 21: a pattern whose trade already ended (target hit or stop hit) is drawn muted (yellow, faded); older ended ones are hidden unless "show history" is on
      const endedQ = !!harmHit(h.plan, this.data, h.pts[h.pts.length-1].i);
      if (endedQ && q > 0 && !this.harmHist) return;
      const bull = h.dir === "bull", col = bull ? "#0ecb81" : "#f6465d", forming = h.state === "forming", P = h.pts.map(t => ({x:this.x(t.i), y:py(t.p), p:t.p})), m = P.length, bw = Math.max(this.bw, 4);
      c.save(); const A0 = (endedQ ? .4 : 1) * (q ? .55 : 1); c.globalAlpha = A0;
      if (!forming){ c.fillStyle = col; c.globalAlpha = A0*.12; [[0,1,2],[2,3,4]].forEach(t => { c.beginPath(); t.forEach((j,u) => u ? c.lineTo(P[j].x,P[j].y) : c.moveTo(P[j].x,P[j].y)); c.closePath(); c.fill(); }); }
      c.globalAlpha = A0; c.strokeStyle = col; c.lineWidth = 1.8; c.beginPath(); P.forEach((t,u) => u ? c.lineTo(t.x,t.y) : c.moveTo(t.x,t.y)); c.stroke();
      const xD = forming ? this.x(n-1) + 4*bw : P[4].x, yPm = py(h.prz.mid);
      if (forming){ c.setLineDash([5,4]); c.beginPath(); c.moveTo(P[3].x, P[3].y); c.lineTo(xD, yPm); c.stroke(); c.setLineDash([]); }
      const D = forming ? {x:xD, y:yPm, p:h.prz.mid} : P[4], pts = P.concat(forming ? [D] : []);
      c.lineWidth = 1; c.setLineDash([4,3]); c.globalAlpha = A0*.8; c.beginPath(); [[0,2],[1,3],[2,4],[0,4]].forEach(([a,b]) => { if (!pts[a] || !pts[b]) return; c.moveTo(pts[a].x,pts[a].y); c.lineTo(pts[b].x,pts[b].y); }); c.stroke(); c.setLineDash([]); c.globalAlpha = A0;
      c.font = fs; c.textAlign = "center"; c.fillStyle = col;
      pts.forEach((t,u) => { const hi = t.p >= Math.max((pts[Math.max(0,u-1)]||t).p, (pts[Math.min(pts.length-1,u+1)]||t).p); c.fillText(nm[u]+(forming && u === 4 ? "?" : ""), t.x, t.y + (hi ? -8 : 13)); });
      const ratio = (a, b, d_) => (Math.abs(pts[a].p - pts[b].p)/Math.abs(pts[d_[0]].p - pts[d_[1]].p)).toFixed(3), mid = (a, b) => [(pts[a].x+pts[b].x)/2, (pts[a].y+pts[b].y)/2];
      c.fillStyle = "#cfd6dd"; c.font = "9px ui-monospace,Menlo,Consolas,monospace";
      [[0,2,ratio(1,2,[0,1])],[1,3,ratio(2,3,[1,2])],[0,4,ratio(1,4,[0,1])],[2,4,ratio(3,4,[2,3])]].forEach(([a,b,tx]) => { if (!pts[a] || !pts[b]) return; const [mx,my] = mid(a,b); c.fillText(tx, mx, my - 3); });
      // PRZ box (Potential Reversal Zone)
      const z0 = Math.min(py(h.prz.lo), py(h.prz.hi)), zh = Math.max(6, Math.abs(py(h.prz.lo) - py(h.prz.hi))), zx = forming ? xD - 6*bw : D.x - 2*bw, zw = (forming ? 12 : 14)*bw;
      c.fillStyle = "rgba(255,193,7,.16)"; c.fillRect(zx, z0 - (zh < 8 ? (8-zh)/2 : 0), zw, Math.max(8, zh)); c.strokeStyle = "#ffc107"; c.setLineDash([4,3]); c.strokeRect(zx + .5, z0 - (zh < 8 ? (8-zh)/2 : 0) + .5, zw, Math.max(8, zh)); c.setLineDash([]);
      c.fillStyle = "#ffc107"; c.font = fs; c.textAlign = "left"; c.fillText("PRZ "+F(h.prz.lo)+(h.prz.hi - h.prz.lo > 1e-12 ? " – "+F(h.prz.hi) : ""), zx + 3, z0 - 5);
      // title
      c.fillStyle = col; c.fillText((bull ? "▲ " : "▼ ")+h.name+(forming ? " (forming)" : ""), Math.max(8, Math.min(PRx - 150, P[1].x)), Math.max(14, Math.min(P[0].y, P[1].y) - 18));
      // trade box (drawn only once price has reached the entry and while the trade is still open: no stop / last target touched since its point)
      const fromI = h.pts[h.pts.length-1].i, filled = harmFilled(h.plan, this.data, fromI), over = harmHit(h.plan, this.data, fromI), live = filled && !over, wait = !filled && !over;
      const pl = h.plan, bx = Math.min(PRx - 150, (forming ? xD : D.x) + 4*bw), bwid = Math.max(110, Math.min(150, PRx - bx - 4)), yE = py(pl.entry), yS = py(pl.stop), yT3 = py(pl.tps[2]);
      if (q === 0 && bwid > 60 && live){   // the trade box only for the newest open pattern, so older ones do not clutter the chart
        c.globalAlpha = A0; c.fillStyle = "rgba(14,203,129,.13)"; c.fillRect(bx, Math.min(yE, yT3), bwid, Math.abs(yT3 - yE)); c.fillStyle = "rgba(246,70,93,.15)"; c.fillRect(bx, Math.min(yE, yS), bwid, Math.abs(yS - yE));
        c.font = "bold 9px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "left";
        [[pl.entry,"#4aa3ff","ENTRY "+F(pl.entry)],[pl.stop,"#f6465d","SL "+F(pl.stop)],[pl.tps[0],"#0ecb81","TP1 "+F(pl.tps[0])+"  R:R "+pl.rr.toFixed(1)],[pl.tps[1],"#0ecb81","TP2 "+F(pl.tps[1])],[pl.tps[2],"#0ecb81","TP3 (A) "+F(pl.tps[2])]].forEach(([v,cl,tx]) => { const y = py(v); c.strokeStyle = cl; c.lineWidth = 1; c.beginPath(); c.moveTo(bx, y+.5); c.lineTo(bx+bwid, y+.5); c.stroke(); c.fillStyle = cl; c.fillText(tx, bx + 3, y - 3); });
        c.fillStyle = "#b57cff"; c.fillText(Lg("HARMONIC PLAN", "خطة الهارمونيك")+(forming ? " ("+Lg("pending", "معلّقة")+")" : ""), bx + 3, Math.min(yE, yT3, yS) - 12); }
      else if (q === 0 && wait){   // entry not reached yet: no box, only a dashed entry line and a small waiting label (same idea as the scanner's waiting label)
        const txt = "⏳ "+h.name+" "+(pl.dir === "long" ? "Long" : "Short")+" @ "+F(pl.entry)+"  SL "+F(pl.stop)+"  TP1 "+F(pl.tps[0])+"  R:R "+pl.rr.toFixed(1)+"  "+Lg("waiting", "انتظار");
        c.globalAlpha = A0; c.strokeStyle = "rgba(74,163,255,.7)"; c.setLineDash([5,4]); c.beginPath(); c.moveTo(forming ? xD : D.x, yE + .5); c.lineTo(PRx, yE + .5); c.stroke(); c.setLineDash([]);
        c.font = "10px sans-serif"; c.textAlign = "left"; const tw = c.measureText(txt).width + 12, tx0 = Math.max(4, Math.min(PRx - tw - 4, bx));
        c.fillStyle = "rgba(0,0,0,.65)"; c.fillRect(tx0, yE - 22, tw, 16); c.fillStyle = "#4aa3ff"; c.fillText(txt, tx0 + 6, yE - 10); }
      c.restore();
    });
    c.font = "11px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "left";
  },
  secMs(){ return (TFSEC[this.tf] || TFSEC[String(this.tf).toUpperCase()] || 3600)*1000; },
  t2i(t){
    const d = this.data, n = d.length; if (!n) return 0; const sm = this.secMs();
    if (t >= d[n-1].t) return n-1 + (t - d[n-1].t)/sm;
    let lo = 0, hi = n-1; while (lo < hi){ const m = (lo+hi+1) >> 1; if (d[m].t <= t) lo = m; else hi = m-1; }
    return lo + (t - d[lo].t)/sm;
  },
  i2t(i){
    const d = this.data, n = d.length; if (!n) return 0; const sm = this.secMs();
    if (i >= n-1) return d[n-1].t + (i-(n-1))*sm;
    const k = Math.max(0, Math.floor(i)); return d[k].t + (i-k)*sm;
  },
  tx(t){ return this.x(this.t2i(t)); },
  yp(p){ return this.PB - (p-this._lo)/(this._hi-this._lo)*this.PB; },
  py2p(y){ return this._lo + (this.PB-y)/this.PB*(this._hi-this._lo); },
  pt(e){ const r = this.cv.getBoundingClientRect(), x = (e.clientX-r.left)/this.S, y = (e.clientY-r.top)/this.S; return {x, y, t:this.i2t(this.idx(x)), p:this.py2p(y)}; },
  loadDraws(key){ this.drawKey = key; this.sel = null; this.creating = null; try { this.draws = JSON.parse(localStorage.getItem(key) || "[]"); } catch(e){ this.draws = []; } this.draw(); },
  saveDraws(){ if (!this.drawKey) return; try { localStorage.setItem(this.drawKey, JSON.stringify(this.draws)); } catch(e){} },
  setTool(t){ if (t !== "cur" && !this.drawingsVisible){ this.drawingsVisible = true; this.onDrawVis && this.onDrawVis(); }   // choosing a drawing tool while drawings are hidden shows them again: never draw something invisible
    this.tool = t; this.creating = null; if (this.onToolChange) this.onToolChange(t); this.cv.style.cursor = t === "cur" ? "" : "crosshair"; this.draw(); },
  cancelTool(){ if (this.creating){ this.draws = this.draws.filter(d => d !== this.creating); this.creating = null; } this.setTool("cur"); },
  ctxMenu(e){
    e.preventDefault(); document.querySelectorAll(".ctxm").forEach(m => m.remove());
    const q = this.pt(e); let target = null;
    if (this.drawingsVisible && q.x <= this.PR && q.y <= this.PB){ for (const d of this.draws.slice().reverse()){ if (this.hit(d, q.x, q.y)){ target = d; break; } } }
    const m = el("div","ctxm"); m.style.cssText = "position:fixed;z-index:2147483001;left:"+e.clientX+"px;top:"+e.clientY+"px";
    const item = (label, fn, danger) => { const b = el("button",null,esc(label)); if (danger) b.style.color = "#f6465d"; b.onclick = () => { fn(); m.remove(); }; m.append(b); };
    if (q.x <= this.PR && q.y <= this.PB && isFinite(q.p)){
      item(Lg("Horizontal line at ","خط أفقي عند ")+fmtP(q.p), () => { const d = {id:Date.now()+Math.random(), type:"hline", pts:[{t:q.t, p:q.p}]}; this.draws.push(d); this.sel = d; this.saveDraws(); this.draw(); });
      item(Lg("Copy price ","نسخ السعر ")+fmtP(q.p), () => ctxCopy(String(q.p))); item(Lg("Fit the view","ضبط العرض"), () => this.fit()); }
    if (target) item("🗑 "+T("cmDel"), () => { this.sel = target; this.deleteSel(); }, true);
    if (this.draws.length) item(T("cmAll")+" ("+this.draws.length+")", () => this.clearDraws());
    if (this.overlay || this.fibLv) item(T("cmOv"), () => { this.overlay = null; this.fibLv = null; this.draw(); });
    if (!m.children.length) item(T("cmNone"), () => {});
    document.body.append(m);
    const off = ev => { if (ev && m.contains(ev.target)) return; m.remove(); document.removeEventListener("pointerdown", off, true); }; setTimeout(() => document.addEventListener("pointerdown", off, true), 0);
  },
  deleteSel(){ if (this.sel){ this.draws = this.draws.filter(d => d !== this.sel); this.sel = null; this.saveDraws(); this.draw(); } },
  clearDraws(){ this.draws = []; this.sel = null; this.creating = null; this.saveDraws(); this.draw(); },
  avgRange(){ const r = this.data.slice(-14); return r.reduce((a,k) => a + (k.h-k.l), 0)/(r.length || 1) || 1; },
  handles(d){   // [{x,y,set(t,p)}] in canvas px
    const X = t => this.tx(t), Y = p => this.yp(p);
    if (d.type === "long" || d.type === "short"){
      return [{x:X(d.t0), y:Y(d.entry), set:(t,p) => { const dt = t-d.t0, dp = p-d.entry; d.t0 += dt; d.t1 += dt; d.entry += dp; d.stop += dp; d.tp += dp; }},
              {x:X(d.t1), y:Y(d.stop), set:(t,p) => { d.stop = p; d.t1 = Math.max(d.t0 + this.secMs()*2, t); }},
              {x:X(d.t1), y:Y(d.tp), set:(t,p) => { d.tp = p; d.t1 = Math.max(d.t0 + this.secMs()*2, t); }}];
    }
    if (d.type === "brush"){ // one handle per ~30 points (stroke can hold hundreds): drag a handle to edit that point
      const n = d.pts.length, step = Math.max(1, Math.ceil(n / 30)), out = [];
      for (let i = 0; i < n; i += step){ const q = d.pts[i]; out.push({x:X(q.t), y:Y(q.p), set:(t,p) => { q.t = t; q.p = p; }}); }
      return out;
    }
    return d.pts.map(q => ({x:X(q.t), y:Y(q.p), set:(t,p) => { q.t = t; q.p = p; }}));
  },
  hit(d, x, y){
    const hs = this.handles(d);
    for (let i = 0; i < hs.length; i++) if (Math.hypot(hs[i].x-x, hs[i].y-y) < 8) return {h:i};
    const cg = this.cgrip(d, hs); if (cg && Math.hypot(cg.x-x, cg.y-y) < 9) return {body:1};
    const seg = (x1,y1,x2,y2) => { const dx = x2-x1, dy = y2-y1, L = dx*dx+dy*dy || 1, u = Math.max(0, Math.min(1, ((x-x1)*dx+(y-y1)*dy)/L)); return Math.hypot(x1+u*dx-x, y1+u*dy-y) < 6; };
    if (d.type === "cross") return (Math.abs(hs[0].x - x) < 6 || Math.abs(hs[0].y - y) < 6) ? {body:1} : null;
    if (d.type === "ellipse"){ const cx = (hs[0].x+hs[1].x)/2, cy = (hs[0].y+hs[1].y)/2, rx = Math.abs(hs[0].x-hs[1].x)/2 + 4, ry = Math.abs(hs[0].y-hs[1].y)/2 + 4; return (((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1) ? {body:1} : null; }
    if (d.type === "triangle") return (this.inPoly(hs, x, y) || hs.some((h, i) => seg(h.x, h.y, hs[(i+1) % hs.length].x, hs[(i+1) % hs.length].y))) ? {body:1} : null;
    if (d.type === "pitchfork"){ if (hs.length < 3) return seg(hs[0].x,hs[0].y,hs[1].x,hs[1].y) ? {body:1} : null; return (this.pfLines(hs).some(l => seg(l[0],l[1],l[2],l[3])) || seg(hs[1].x,hs[1].y,hs[2].x,hs[2].y)) ? {body:1} : null; }
    if (d.type === "callout"){ const w = d._w || 60, h = d._h || 20; return ((x >= hs[1].x-2 && x <= hs[1].x+w && Math.abs(y-hs[1].y) < h/2+3) || seg(hs[0].x,hs[0].y,hs[1].x,hs[1].y)) ? {body:1} : null; }
    if (d.type === "plabel"){ const w = d._w || 50; return (x >= hs[0].x-2 && x <= hs[0].x+w+9 && Math.abs(y-hs[0].y) < 10) ? {body:1} : null; }
    if (d.type === "arrup" || d.type === "arrdn" || d.type === "flag") return Math.hypot(hs[0].x-x, hs[0].y + (d.type === "arrup" ? 11 : d.type === "arrdn" ? -11 : -13) - y) < 15 ? {body:1} : null;
    if (d.type === "hline") return Math.abs(hs[0].y - y) < 6 ? {body:1} : null;
    if (d.type === "rect"){ const x1 = Math.min(hs[0].x,hs[1].x), x2 = Math.max(hs[0].x,hs[1].x), y1 = Math.min(hs[0].y,hs[1].y), y2 = Math.max(hs[0].y,hs[1].y); return (x >= x1-4 && x <= x2+4 && y >= y1-4 && y <= y2+4) ? {body:1} : null; }
    if (d.type === "channel"){ const o = this.chanOff(d), y2a = this.yp(d.pts[0].p+o), y2b = this.yp(d.pts[1].p+o); return (seg(hs[0].x,hs[0].y,hs[1].x,hs[1].y) || seg(hs[0].x,y2a,hs[1].x,y2b)) ? {body:1} : null; }
    if (d.type === "text"){ const w = d._w || ((d.txt||"").length*6+10), h = d._h || 18; return (x >= hs[0].x-2 && x <= hs[0].x+w && Math.abs(y-hs[0].y) < h/2+3) ? {body:1} : null; }
    if (d.type === "vline") return Math.abs(hs[0].x - x) < 6 ? {body:1} : null;
    if (d.type === "brush"){ for (let i = 0; i + 1 < d.pts.length; i++){ if (seg(this.tx(d.pts[i].t), this.yp(d.pts[i].p), this.tx(d.pts[i+1].t), this.yp(d.pts[i+1].p))) return {body:1}; } return null; }
    if (d.type === "prange"){ const y1 = Math.min(hs[0].y, hs[1].y), y2 = Math.max(hs[0].y, hs[1].y); return (y >= y1-4 && y <= y2+4) ? {body:1} : null; }
    if (d.type === "drange"){ const x1 = Math.min(hs[0].x, hs[1].x), x2 = Math.max(hs[0].x, hs[1].x); return (x >= x1-4 && x <= x2+4) ? {body:1} : null; }
    if (d.type === "ray"){ const e = this.rayEnd(hs[0].x,hs[0].y,hs[1].x,hs[1].y); return seg(hs[0].x,hs[0].y,e.x,e.y) ? {body:1} : null; }
    if (d.type === "trend"){ const ea = d.extL ? this.rayEnd(hs[1].x,hs[1].y,hs[0].x,hs[0].y) : hs[0], eb = d.extR ? this.rayEnd(hs[0].x,hs[0].y,hs[1].x,hs[1].y) : hs[1]; return seg(ea.x,ea.y,eb.x,eb.y) ? {body:1} : null; }
    if (d.type === "arrow" || d.type === "measure") return seg(hs[0].x,hs[0].y,hs[1].x,hs[1].y) ? {body:1} : null;
    if (d.type === "wave"){ for (let i = 0; i < hs.length-1; i++) if (seg(hs[i].x,hs[i].y,hs[i+1].x,hs[i+1].y)) return {body:1}; return null; }
    if (d.type === "fib"){ const x0 = Math.min(hs[0].x, hs[1].x); if (x < x0-4) return null;
      for (const L of (d.lv || FIB_PRESETS.Retracement)){ if (Math.abs(this.yp(d.pts[1].p - (d.pts[1].p-d.pts[0].p)*L) - y) < 5) return {body:1}; } return null; }
    if (d.type === "long" || d.type === "short"){
      const xa = hs[0].x, xb = hs[1].x, ys = [hs[0].y, hs[1].y, hs[2].y], y1 = Math.min(...ys), y2 = Math.max(...ys);
      return (x >= Math.min(xa,xb) && x <= Math.max(xa,xb) && y >= y1 && y <= y2) ? {body:1} : null;
    }
    return null;
  },
  cgrip(d, hs){   // the centre grip of a selected drawing: grab it to move the whole drawing
    if (!hs || hs.length < 2 || ["brush","hline","vline","cross","text","plabel","arrup","arrdn","flag","prange","drange"].includes(d.type)) return null;
    if (d.type === "long" || d.type === "short") return {x:(hs[0].x + hs[1].x)/2, y:hs[0].y};
    return {x:hs.reduce((a,h) => a + h.x, 0)/hs.length, y:hs.reduce((a,h) => a + h.y, 0)/hs.length};
  },
  inPoly(hs, x, y){ let r = false; for (let i = 0, j = hs.length-1; i < hs.length; j = i++){ if ((hs[i].y > y) !== (hs[j].y > y) && x < (hs[j].x-hs[i].x)*(y-hs[i].y)/(hs[j].y-hs[i].y) + hs[i].x) r = !r; } return r; },
  pfLines(hs){   // Andrews pitchfork: median line from the pivot through the middle of B-C, and two parallels through B and C, all extended
    const A = hs[0], B = hs[1], C = hs[2], M = {x:(B.x + C.x)/2, y:(B.y + C.y)/2}, vx = M.x - A.x, vy = M.y - A.y; if (!vx && !vy) return [];
    return [[A, M], [B, {x:B.x + vx, y:B.y + vy}], [C, {x:C.x + vx, y:C.y + vy}]].map(([a, b]) => { const e = this.rayEnd(a.x, a.y, b.x, b.y); return [a.x, a.y, e.x, e.y]; });
  },
  chanOff(d){ const a = d.pts[0], b = d.pts[1], c = d.pts[2], dt = b.t-a.t || 1; return c.p - (a.p + (b.p-a.p)*(c.t-a.t)/dt); },
  toolDown(e){
    const q = this.pt(e); if (this.tool !== "cur" && (q.x > this.PR || q.y > this.PB || !this.data.length)){ const why = !this.data.length ? Lg("no candles loaded yet", "لا توجد شموع بعد") : q.x > this.PR ? Lg("click inside the candle area (this is the order-flow column / price axis)", "اضغط داخل منطقة الشموع (ده عمود الأوردر فلو / محور السعر)") : Lg("click in the price area (this is an indicator pane)", "اضغط في منطقة السعر (ده شريط مؤشر)"); this._hint = {t:Date.now(), s:Lg("Drawing: ", "الرسم: ")+why}; console.info("[XPIX] drawing click ignored: "+why+" x="+Math.round(q.x)+" PR="+Math.round(this.PR)+" y="+Math.round(q.y)+" PB="+Math.round(this.PB)); this.draw(); setTimeout(() => this.draw(), 3600); }
    if (q.x > this.PR || q.y > this.PB || !this.data.length) return false;
    const ac = this._autoChip; if (ac && q.x >= ac.x && q.x <= ac.x+ac.w && q.y >= ac.y && q.y <= ac.y+ac.h){ this.autoY(); this._autoChip = null; this.draw(); return true; }
    const hc = this._hidChip; if (hc && q.x >= hc.x && q.x <= hc.x+hc.w && q.y >= hc.y && q.y <= hc.y+hc.h){ this.draws.forEach(d => { delete d.hidden; }); this.saveDraws(); this.draw(); return true; }
    const gc = this._gChip; if (gc && q.x >= gc.x && q.x <= gc.x+gc.w && q.y >= gc.y && q.y <= gc.y+gc.h){ this.infoOpen = this.infoOpen === false; this.draw(); return true; }
    const ph = this._planH; if (this.tool === "cur" && this.overlay && this.overlay.plan && this.showSig && ph && Math.abs(q.x-ph.x) < 9 && Math.abs(q.y-ph.y) < 10){ this.planDrag = true; return true; }
    if (this.tool === "cur"){
      const order = this.drawingsVisible ? (this.sel ? [this.sel, ...this.draws.filter(d => d !== this.sel)] : this.draws.slice().reverse()) : [];
      for (const d of order){
        const h = this.hit(d, q.x, q.y); if (!h) continue;
        this.sel = d; this.drag = null;
        if (d.lock){ this.draw(); return true; }
        this.dragD = {d, h, last:q, changed:false}; this.draw(); return true;
      }
      if (this.sel){ this.sel = null; this.draw(); }
      return false;
    }
    const t = this.tool;
    if (this.creating){            // next point of a multi-click drawing
      const c = this.creating; c.pts[c.pts.length-1] = {t:q.t, p:q.p};
      const need = c.type === "wave" ? 6 : (c.type === "channel" || c.type === "triangle" || c.type === "pitchfork") ? 3 : 2;
      if (c.pts.length >= need){ this.creating = null; this.sel = c; this.saveDraws(); this.setTool("cur"); if (c.type === "callout") this.openEditor(c); }
      else c.pts.push({t:q.t, p:q.p});
      this.draw(); return true;
    }
    const id = Date.now() + Math.random();
    if (t === "vline" || t === "cross" || t === "plabel" || t === "arrup" || t === "arrdn" || t === "flag"){ const d = {id, type:t, pts:[{t:q.t, p:q.p}]}; this.draws.push(d); this.sel = d; this.saveDraws(); this.setTool("cur"); }
    else if (t === "brush"){ const d = {id, type:t, pts:[{t:q.t, p:q.p}]}; this.draws.push(d); this.creating = d; }
    else if (t === "hline"){ const d = {id, type:t, pts:[{t:q.t, p:q.p}]}; this.draws.push(d); this.sel = d; this.saveDraws(); this.setTool("cur"); }
    else if (t === "text"){ const d = {id, type:t, txt:"", pts:[{t:q.t, p:q.p}]}; this.draws.push(d); this.sel = d; this.setTool("cur"); this.draw(); this.openEditor(d); return true; }
    else if (t === "trend" || t === "info" || t === "extline" || t === "ellipse" || t === "triangle" || t === "pitchfork" || t === "callout" || t === "fib" || t === "wave" || t === "rect" || t === "channel" || t === "ray" || t === "arrow" || t === "measure" || t === "prange" || t === "drange"){ const d = {id, type:t === "info" || t === "extline" ? "trend" : t, pts:[{t:q.t, p:q.p}, {t:q.t, p:q.p}]}; if (t === "info") d.info = true; if (t === "extline"){ d.extL = true; d.extR = true; } if (t === "callout") d.txt = ""; if (t === "fib") d.lv = (FIB_PRESETS[this.fibPreset] || FIB_PRESETS.Retracement).slice(); this.draws.push(d); this.creating = d; }
    else if (t === "long" || t === "short"){
      const a = this.avgRange()*1.5, dir = t === "long" ? 1 : -1, d = {id, type:t, t0:q.t, t1:q.t + this.secMs()*25, entry:q.p, stop:q.p - dir*a, tp:q.p + dir*a*2};
      this.draws.push(d); this.sel = d; this.saveDraws(); this.setTool("cur");
    }
    this.draw(); return true;
  },
  toolMove(e){
    if (this.planDrag){ const q = this.pt(e), ph = this._planH; if (ph) this.planLen = Math.max(5, Math.min(2000, Math.round((q.x - ph.x0)/this.bw))); return true; }
    if (this.creating){ const q = this.pt(e), c = this.creating; if (c.type === "brush"){ if (e.buttons === 1){ const L = c.pts[c.pts.length-1]; if (Math.hypot(this.tx(q.t)-this.tx(L.t), this.yp(q.p)-this.yp(L.p)) >= 2) c.pts.push({t:q.t, p:q.p}); } return true; } c.pts[c.pts.length-1] = {t:q.t, p:q.p}; return true; }
    const dd = this.dragD; if (!dd) return false;
    const q = this.pt(e), d = dd.d; dd.changed = true;
    if (dd.h.h != null) this.handles(d)[dd.h.h].set(q.t, q.p);
    else {   // move the whole drawing
      const dt = q.t - dd.last.t, dp = q.p - dd.last.p;
      if (d.type === "long" || d.type === "short"){ d.t0 += dt; d.t1 += dt; d.entry += dp; d.stop += dp; d.tp += dp; }
      else d.pts.forEach(z => { z.t += dt; z.p += dp; });
    }
    dd.last = q; return true;
  },
  toolUp(e){ if (this.planDrag){ this.planDrag = false; this.onPlanLen && this.onPlanLen(this.planLen); } if (this.dragD){ if (this.dragD.changed) this.saveDraws(); this.dragD = null; }
    const c = this.creating;   // press, drag and release also draws a two-point tool (like TradingView): the release point is the end; a plain click keeps the click-click mode
    if (c && c.type !== "brush" && c.type !== "wave" && c.type !== "channel" && c.type !== "triangle" && c.type !== "pitchfork" && c.pts.length === 2 && Math.hypot(this.tx(c.pts[1].t) - this.tx(c.pts[0].t), this.yp(c.pts[1].p) - this.yp(c.pts[0].p)) > 8){
      const q = this.pt(e); c.pts[1] = {t:q.t, p:q.p}; this.creating = null; this.sel = c; this.saveDraws(); this.setTool("cur"); if (c.type === "callout") this.openEditor(c); this.draw(); } },
  nyMin(t){   // minutes since midnight in New York (DST-aware), cached per candle
    const m = this._ny || (this._ny = new Map()); let v = m.get(t); if (v != null) return v;
    if (!this._nyf) this._nyf = new Intl.DateTimeFormat("en-GB", {timeZone:"America/New_York", hour:"2-digit", minute:"2-digit", hour12:false});
    const parts = this._nyf.formatToParts(new Date(t)); v = (+parts.find(x => x.type === "hour").value % 24)*60 + (+parts.find(x => x.type === "minute").value);
    m.set(t, v); return v;
  },
  paintKZ(c, py, i0, i1, PB){
    if (this.secMs() > 3600*1000) return;           // sessions only make sense on 1H and lower
    // [name, start, end (>1440 = wraps past midnight), colour, isSession]  (New York time). Sessions = live boxes that freeze into
    // high / mid / low reference lines; kill zones = coloured bands.
    const Z = [["Asia", 19*60, 28*60, "#4aa3ff", 1], ["London", 3*60, 12*60, "#f0b90b", 1], ["New York", 8*60, 17*60, "#0ecb81", 1],
               ["Asia KZ", 20*60, 24*60, "#4aa3ff"], ["London Open KZ", 2*60, 5*60, "#f0b90b"], ["NY AM KZ", 7*60, 10*60, "#0ecb81"], ["NY PM KZ", 13.5*60, 16*60, "#b57cff"]];
    const d = this.data, step = this.bw, n = d.length, PR = this.PR, e9 = this.emaV && this.emaV[9], e21 = this.emaV && this.emaV[21];
    c.font = "bold 10px sans-serif"; c.textAlign = "left"; c.textBaseline = "top";
    const lo0 = Math.max(0, i0 - 120), hi0 = Math.min(n - 1, i1 + 60);
    Z.forEach(([name, a, b, col, isSes]) => {
      const segs = []; let start = -1;
      for (let i = lo0; i <= hi0; i++){
        const m = this.nyMin(d[i].t), inZ = (m >= a && m < b) || (b > 1440 && m < b - 1440);
        if (inZ && start < 0) start = i; else if (!inZ && start >= 0){ segs.push([start, i-1, false]); start = -1; }
      }
      if (start >= 0) segs.push([start, hi0, hi0 === n-1]);       // last flag = still running (live)
      segs.forEach(([s0, s1, live], si) => {
        let hi = -Infinity, lo = Infinity; for (let k = s0; k <= s1; k++){ hi = Math.max(hi, d[k].h); lo = Math.min(lo, d[k].l); }
        const x0 = this.x(s0) - step/2, x1 = this.x(s1) + step/2;
        c.globalAlpha = isSes ? .09 : .14; c.fillStyle = col; c.fillRect(x0, py(hi), x1-x0, Math.max(2, py(lo)-py(hi)));   // box = the price range the session actually travelled, not the full chart height
        c.strokeStyle = col; c.lineWidth = 1;
        if (isSes){
          const next = segs[si+1], xe = next ? this.x(next[0]) - step/2 : PR, mid = (hi+lo)/2;
          c.globalAlpha = live ? .75 : .35; c.strokeRect(Math.round(x0)+.5, Math.round(py(hi))+.5, x1-x0, Math.round(py(lo))-Math.round(py(hi)));   // the session box (live-tracking while open)
          // resting liquidity: the session high / low stay as levels until a LATER bar raids (trades through) them
          const raidAt = (lvl, up) => { for (let k = s1+1; k < n; k++){ if (up ? d[k].h > lvl : d[k].l < lvl) return k; } return -1; };
          const sesOf = k => { const m = this.nyMin(d[k].t); return m >= 3*60 && m < 8*60 ? "London" : m >= 8*60 && m < 17*60 ? "NY" : "Asia"; };
          c.setLineDash([5,3]);
          [[hi, true, "H"], [lo, false, "L"]].forEach(([lv, up, tag]) => {
            const rk = raidAt(lv, up), y = Math.round(py(lv))+.5, xr = rk >= 0 ? this.x(rk) : PR;
            c.globalAlpha = rk >= 0 ? .3 : .75; c.beginPath(); c.moveTo(x1, y); c.lineTo(Math.max(x1, xr), y); c.stroke();
            if (rk >= 0 && rk <= i1+1){          // flag the raid: diamond on the sweep bar + who raided what
              c.setLineDash([]); c.globalAlpha = 1; c.fillStyle = col; const rx = this.x(rk), ry = py(up ? d[rk].h : d[rk].l);
              c.beginPath(); c.moveTo(rx, ry-5); c.lineTo(rx+5, ry); c.lineTo(rx, ry+5); c.lineTo(rx-5, ry); c.closePath(); c.fill();
              c.font = "bold 9px sans-serif"; c.fillText(sesOf(rk)+" raids "+name+" "+tag, Math.min(rx+7, PR-96), ry + (up ? -12 : 4)); c.font = "bold 10px sans-serif"; c.setLineDash([5,3]);
            }
          });
          c.globalAlpha = .35; { const y = Math.round(py(mid))+.5; c.beginPath(); c.moveTo(x1, y); c.lineTo(Math.max(x1, xe), y); c.stroke(); }
          c.setLineDash([]);
          // rejection: wick beyond the session extreme, close back inside, EMA9/21 aligned with the reversal
          if (!live && e9 && e21){
            const stop = next ? next[0] : Math.min(n-1, s1 + 60);
            for (let k = s1+1; k <= stop && k < n; k++){
              if (d[k].h > hi && d[k].c < hi && e9[k] < e21[k]){ this.rejMark(c, this.x(k), py(d[k].h), -1, col); break; }
              if (d[k].l < lo && d[k].c > lo && e9[k] > e21[k]){ this.rejMark(c, this.x(k), py(d[k].l), 1, col); break; }
            }
          }
          c.globalAlpha = 1; c.fillStyle = col; if (x1-x0 > 30) c.fillText(name+(live ? " ●" : ""), x0+3, 14);
        } else {
          c.globalAlpha = .55; c.setLineDash([4,3]);
          [hi, lo].forEach(v => { const y = Math.round(py(v))+.5; c.beginPath(); c.moveTo(x0, y); c.lineTo(x1, y); c.stroke(); }); c.setLineDash([]);
          c.globalAlpha = 1; c.fillStyle = col; if (x1-x0 > 26) c.fillText(name, x0+3, 3);
        }
      });
    });
    c.globalAlpha = 1; c.textBaseline = "middle"; c.font = "11px ui-monospace,Menlo,Consolas,monospace";
  },
  rejMark(c, x, y, dir, col){   // dir +1 = bullish rejection (arrow up under the wick), -1 = bearish
    c.globalAlpha = 1; c.fillStyle = dir > 0 ? "#0ecb81" : "#f6465d"; const yy = y + (dir > 0 ? 12 : -12);
    c.beginPath(); c.moveTo(x, yy + (dir > 0 ? -8 : 8)); c.lineTo(x-5, yy + (dir > 0 ? 3 : -3)); c.lineTo(x+5, yy + (dir > 0 ? 3 : -3)); c.closePath(); c.fill();
    c.font = "bold 9px sans-serif"; c.textAlign = "center"; c.fillText("REJ", x, yy + (dir > 0 ? 8 : -12)); c.textAlign = "left"; c.font = "bold 10px sans-serif";
  },
  /* Kill Zone Sniper overlay (JOAT-style look): same rules as killzone_sniper_bull in modules/signals.py, mirrored for shorts.
     Inside the London (02-05) or NY AM (07-10) kill zone (New York time) a candle sweeps the 20-bar low (high), closes back
     inside with a displacement body >= 0.9 ATR14 and, with real volume, >= 1.5x its 20-bar average volume. Entry = that close,
     stop = the sweep wick, target = the 30-bar swing high (low), kept only when target >= 1.5R. Outcome = first of stop / target
     within 48 bars (stop counts first when both are in one candle). Drawn history only - not a backtest. */
  kzsCalc(){
    const d = this.data, n = d.length, key = n ? n+":"+d[n-1].t+":"+d[n-1].c+":"+this.tf : "";
    if (this._kzs && this._kzs.key === key) return this._kzs.list;
    const list = [];
    if (n > 60 && this.secMs() <= 3600*1000){
      const atr = new Array(n); let sum = 0; const tr = d.map((k, i) => i ? Math.max(k.h - k.l, Math.abs(k.h - d[i-1].c), Math.abs(k.l - d[i-1].c)) : k.h - k.l);
      for (let i = 0; i < n; i++){ sum += tr[i]; if (i >= 14) sum -= tr[i-14]; atr[i] = sum / Math.min(i+1, 14); }
      const volOk = d.filter(k => k.v > 0).length >= 0.9*n;
      const kzOf = t => { const m = this.nyMin(t); return m >= 120 && m < 300 ? "London" : m >= 420 && m < 600 ? "NY AM" : null; };
      for (let j = 30; j < n; j++){
        const k = d[j], kz = kzOf(k.t); if (!kz) continue;
        let lo = Infinity, hi = -Infinity, va = 0; for (let q = j-20; q < j; q++){ lo = Math.min(lo, d[q].l); hi = Math.max(hi, d[q].h); va += d[q].v; } va /= 20;
        const vr = volOk && va > 0 ? k.v / va : null; if (volOk && !(vr >= 1.5)) continue;
        let side = 0, lvl = 0;
        if (k.l < lo && k.c > lo && k.c > k.o && k.c - k.o >= 0.9*atr[j]){ side = 1; lvl = lo; }
        else if (k.h > hi && k.c < hi && k.c < k.o && k.o - k.c >= 0.9*atr[j]){ side = -1; lvl = hi; }
        if (!side) continue;
        const sl = side > 0 ? k.l : k.h; let tp = side > 0 ? -Infinity : Infinity;
        for (let q = Math.max(0, j-29); q <= j; q++) tp = side > 0 ? Math.max(tp, d[q].h) : Math.min(tp, d[q].l);
        const risk = (k.c - sl)*side, rr = risk > 0 ? (tp - k.c)*side / risk : 0; if (rr < 1.5) continue;
        let res = "open", end = Math.min(n-1, j+48);
        for (let q = j+1; q <= Math.min(n-1, j+48); q++){ if ((side > 0 ? d[q].l <= sl : d[q].h >= sl)){ res = "sl"; end = q; break; } if ((side > 0 ? d[q].h >= tp : d[q].l <= tp)){ res = "tp"; end = q; break; } }
        if (res === "open" && j+48 < n) res = "exp";
        list.push({j, side, kz, lvl, en:k.c, sl, tp, rr, vr, res, end});
      }
    }
    this._kzs = {key, list}; return list;
  },
  /* W.D. Gann time & price tools (visual; Gann has no peer-reviewed evidence - the weekly lab tests the time cycles against random):
     anchor = the most recent of the highest high / lowest low of the last `look` bars;
     time cycles = vertical lines at anchor + 30 / 45 / 60 / 90 / 120 / 144 / 180 / 360 bars (also into the future);
     Square of 9 = (sqrt(anchor price) +- k x deg/360 x 2)^2, k = 1..4;  fan = 1x1 / 1x2 / 2x1 lines, 1 unit = ATR14 per bar;
     cardinal dates (21 Mar / 21 Jun / 23 Sep / 21 Dec) on daily and higher bars. */
  syncStats(){ const done = (this.syncLog || []).filter(t => t.res != null), n = done.length; if (!n) return {n:0};
    return {n, win:Math.round(100*done.filter(t => t.res > 0).length/n), avg:Math.round(100*done.reduce((a, t) => a + t.res, 0)/n)/100, open:(this.syncLog || []).length - n}; },
  paintAstro(c, py, i0, i1, PB){   // moon phases, planetary aspects, retrograde shading, planetary price lines (Gann: 1 degree = 1 price unit x scale, repeating every 360)
    const d = this.data, n = d.length, A = this.st.astro, PR = this.PR, sec = this.secMs(); if (n < 2) return;
    const tL = d[Math.max(0, i0)].t, tR = d[n-1].t + Math.max(0, (PR - this.x(n-1))/this.bw)*sec, xT = t => this.x((t - d[0].t)/sec), G = Astro.GLYPH, span = tR - tL;
    const step0 = Math.max(3600e3, span/2500), step = 3600e3*2**Math.ceil(Math.log2(step0/3600e3)), dv = (a, b) => ((a - b + 540) % 360) - 180;   // power-of-two hours: the sample grid stays put while the chart redraws
    c.save(); c.textBaseline = "middle"; c.font = "11px sans-serif";
    // retrograde (geocentric longitude going backwards) shaded at the top
    if (A.retro && A.rp !== "sun" && A.rp !== "moon"){ let st = null, prev = Astro.lon(A.rp, tL - step); for (let t = Math.floor(tL/step)*step; t <= tR + step; t += step){ const v = Astro.lon(A.rp, t), r = dv(v, prev) < 0; prev = v;
        if (r && st == null) st = t; if ((!r || t > tR) && st != null){ const xa = xT(st), xb = xT(t); c.globalAlpha = .12; c.fillStyle = "#e056fd"; c.fillRect(xa, 0, Math.max(2, xb - xa), PB); c.globalAlpha = .9; c.fillStyle = "#e056fd"; c.font = "10px sans-serif"; c.fillText(G[A.rp]+" R", Math.max(2, xa + 2), PB - 30); st = null; } } }
    // moon phases: new = dark disc, full = bright disc (quarters optional)
    if (A.moon){ const targets = A.mq ? [0, 90, 180, 270] : [0, 180]; let prev = Astro.rev(Astro.lon("moon", tL - step) - Astro.lon("sun", tL - step)), ms = Math.min(step, 4*3600e3), ph = [];
      for (let t = Math.floor(tL/step)*step; t <= tR; t += ms){ const e = Astro.rev(Astro.lon("moon", t) - Astro.lon("sun", t)); targets.forEach(a => { const p0 = dv(prev, a), p1 = dv(e, a); if (p0 < 0 && p1 >= 0 && Math.abs(p1 - p0) < 90) ph.push([t, a]); }); prev = e; }
      const gapPx = ph.length > 1 ? Math.abs(xT(ph[1][0]) - xT(ph[0][0])) : 999, showLine = gapPx >= 25;
      ph.forEach(([t, a]) => { const x = xT(t); if (x < 0 || x > PR) return; if (gapPx < 9 && a !== 0) return; if (!showLine){ c.globalAlpha = 1; c.beginPath(); c.arc(x, 8, 4, 0, 6.3); if (a === 0){ c.fillStyle = "#0b0e11"; c.fill(); c.strokeStyle = "#c3c9d1"; c.stroke(); } else { c.fillStyle = "#f5f3d0"; c.fill(); } return; } c.globalAlpha = .25; c.strokeStyle = A.color2; c.setLineDash([2,4]); c.beginPath(); c.moveTo(x, 14); c.lineTo(x, PB); c.stroke(); c.setLineDash([]);
        c.globalAlpha = 1; c.beginPath(); c.arc(x, 8, 5, 0, 6.3); if (a === 0){ c.fillStyle = "#0b0e11"; c.fill(); c.strokeStyle = "#c3c9d1"; c.stroke(); } else if (a === 180){ c.fillStyle = "#f5f3d0"; c.fill(); } else { c.strokeStyle = "#c3c9d1"; c.stroke(); c.fillStyle = "#c3c9d1"; c.beginPath(); c.arc(x, 8, 5, a === 90 ? -Math.PI/2 : Math.PI/2, a === 90 ? Math.PI/2 : 1.5*Math.PI); c.fill(); } }); }
    // aspects between two bodies (geocentric or heliocentric): conjunction 0, sextile 60, square 90, trine 120, opposition 180
    if (A.asp && A.p1 !== A.p2){ const AS = A.aset === "all" ? [[0,"☌"],[60,"⚹"],[90,"□"],[120,"△"],[180,"☍"],[30,"⚺"],[45,"∠"],[135,"⚼"],[150,"⚻"]] : A.aset === "hard" ? [[0,"☌"],[90,"□"],[180,"☍"]] : [[0,"☌"],[60,"⚹"],[90,"□"],[120,"△"],[180,"☍"]];
      const sepAt = t => Math.abs(dv(Astro.lon(A.p1, t, A.ahel && A.p1 !== "moon"), Astro.lon(A.p2, t, A.ahel && A.p2 !== "moon"))), fast = A.p1 === "moon" || A.p2 === "moon", st2 = fast ? Math.min(step, 2*3600e3) : step;
      let prev = sepAt(tL - st2), k = 0; for (let t = Math.floor(tL/step)*step; t <= tR && k < 4000; t += st2, k++){ const v = sepAt(t);
        AS.forEach(([a, gl]) => { if ((prev - a)*(v - a) <= 0 && prev !== v){ const x = xT(t); if (x < 0 || x > PR) return; const hard = a % 90 === 0;
          c.globalAlpha = hard ? .7 : .45; c.strokeStyle = A.color; c.lineWidth = hard ? 1.4 : 1; c.setLineDash(hard ? [] : [4,3]); c.beginPath(); c.moveTo(x, 18); c.lineTo(x, PB); c.stroke(); c.setLineDash([]);
          c.globalAlpha = 1; c.fillStyle = A.color; c.font = "bold 11px sans-serif"; c.fillText(G[A.p1]+gl+G[A.p2], x + 3, 24); } }); prev = v; } }
    // planetary price lines: price = (longitude + 360 k) x scale (auto scale puts one 360 cycle near the price), plus harmonics (every 360/harm degrees)
    if (A.pl){ const last = d[n-1].c, scale = +A.scale > 0 ? +A.scale : 10**Math.round(Math.log10(Math.max(1e-9, last/720))), cyc = 360*scale, hm = Math.max(1, Math.min(12, A.harm|0 || 1)), lo = this._lo, hi = this._hi;
      const pts = []; for (let t = Math.floor(tL/step)*step; t <= tR; t += step*2**Math.max(0, Math.ceil(Math.log2(span/300/step)))) pts.push([t, Astro.lon(A.plp, t, A.plhel && A.plp !== "moon")]);
      for (let h = 0; h < hm; h++){ const off = h*360/hm*scale; for (let k = Math.floor((lo - off)/cyc) - 1; k <= Math.ceil((hi - off)/cyc) + 1; k++){
        c.strokeStyle = A.color; c.globalAlpha = h ? .35 : .75; c.lineWidth = h ? 1 : 1.5; c.setLineDash(h ? [5,4] : []); c.beginPath(); let started = false, lastLon = null;
        pts.forEach(([t, L]) => { const p = (L + 360*k)*scale + off, x = xT(t), y = py(p); if (lastLon != null && Math.abs(L - lastLon) > 180){ started = false; } lastLon = L; if (!started){ c.moveTo(x, y); started = true; } else c.lineTo(x, y); });
        c.stroke(); c.setLineDash([]); } }
      c.globalAlpha = .9; c.fillStyle = A.color; c.font = "9px sans-serif"; c.fillText(G[A.plp]+(A.plhel ? " helio" : " geo")+" · 1° = "+scale+" · "+Lg("lines every ","خط كل ")+(360/hm)+"°", 40, PB - 46); }
    c.globalAlpha = .75; c.fillStyle = "#9aa4b2"; c.font = "9px sans-serif"; c.fillText(Lg("Gann astro: visual only - no scientific evidence that planets move prices","جان الفلكي: عرض بصري بس - مفيش دليل علمي إن الكواكب بتحرك الأسعار"), 40, PB - 60);
    c.restore(); c.globalAlpha = 1; c.textBaseline = "middle"; c.font = "11px ui-monospace,Menlo,Consolas,monospace";
  },
  paintSyncMarks(c, py, i0, i1, PB){   // one small diamond per sync setup at its entry; filled = closed (colour = side), hollow = still open
    const d = this.data, n = d.length, S = this.st.sync; if (!n) return;
    (this.syncLog || []).forEach(t => { if (t.t < d[0].t) return; let lo = 0, hi = n - 1; while (lo < hi){ const m = (lo + hi + 1) >> 1; if (d[m].t <= t.t) lo = m; else hi = m - 1; }
      if (lo < i0 || lo > i1) return; const x = this.x(lo), y = py(t.en); if (y < 0 || y > PB) return; const col = t.dir > 0 ? S.color : S.color2, r = 5;
      c.beginPath(); c.moveTo(x, y - r); c.lineTo(x + r, y); c.lineTo(x, y + r); c.lineTo(x - r, y); c.closePath(); c.lineWidth = 1.5; c.strokeStyle = col; c.fillStyle = col;
      if (t.res != null){ c.globalAlpha = t.res > 0 ? .95 : .45; c.fill(); } else { c.globalAlpha = 1; c.stroke(); } c.globalAlpha = 1; });
  },
  paintRead(c, X0, XE, PB, py, now){   // FLOW READING: 2-4 plain sentences about what the book, the prints and the limit tracker did in the last 2 minutes, numbered, with the same numbers drawn on the heat map at the price they talk about. A description, never a forecast.
    const R = this._rd; if (!R) return;
    (R.zones || []).forEach(z => { const y1 = py(z.hi), y2 = py(z.lo), yy = Math.min(y1, y2), hh = Math.max(7, Math.abs(y1 - y2) + 4); if (yy > PB || yy + hh < 0) return;   // confluence zone: a gold bracket at the column's left edge, one dot per agreeing source
      c.save(); c.fillStyle = z.strength >= 3 ? "rgba(240,185,11,.95)" : "rgba(240,185,11,.55)"; c.fillRect(X0 + 5, yy, 3, hh); c.font = "bold 8px sans-serif"; c.textAlign = "left"; c.textBaseline = "middle"; c.fillText("●".repeat(z.strength), X0 + 11, yy + hh/2); c.restore(); });
    const w = XE - X0, ar = lang === "ar", lines = R.lines.slice(0, w >= 190 && PB >= 300 ? 4 : PB >= 220 ? 3 : PB >= 160 ? 2 : 1);   // small chart: fewer lines, the heat map stays readable
    if (w < 150 || PB < 200 || !lines.length) return;   // too small: the heat map matters more (the original port had this check inside its own comment, so it never ran)
    const G = this.st.of.color || "#0ecb81", Rd = this.st.of.color2 || "#f6465d", fs = 9, lh = 11;
    c.save(); c.font = fs+"px sans-serif"; c.textBaseline = "middle";
    const iso = t => ar ? t.replace(/[+\-]?[0-9A-Za-z][0-9A-Za-z.,%:+\-]*(?: +[A-Za-z][A-Za-z.\-]*)*/g, m => "\u2066"+m+"\u2069") : t;
    const wrap = t => { const out = [], words = t.split(" "), maxW = w - 26; let cur = ""; words.forEach(wd => { const tt = cur ? cur+" "+wd : wd; if (c.measureText(tt).width > maxW && cur){ out.push(cur); cur = wd; } else cur = tt; }); if (cur) out.push(cur); return out.slice(0, 3); };
    const rows = lines.map(l => ({l, ws:wrap(ar ? l.ar : l.en)})), H = 16 + rows.reduce((a, r) => a + r.ws.length*lh + 3, 0) + 4, y0 = 52;
    c.fillStyle = "rgba(8,12,18,.78)"; c.strokeStyle = "#2b3139"; c.lineWidth = 1; c.fillRect(X0 + 4, y0, w - 8, H); c.strokeRect(X0 + 4.5, y0 + .5, w - 9, H - 1);
    const tilt = R.tilt, tc = tilt.dir > 0 ? G : tilt.dir < 0 ? Rd : "#9aa4b2";
    c.font = "bold 9px sans-serif"; c.fillStyle = "#eaecef"; c.textAlign = ar ? "right" : "left"; c.fillText(ar ? "قراءة الأوردر فلو" : "FLOW READING", ar ? XE - 10 : X0 + 9, y0 + 8);
    c.font = "8px sans-serif"; c.fillStyle = tc; c.textAlign = ar ? "left" : "right"; c.fillText((ar ? tilt.label.ar : tilt.label.en), ar ? X0 + 9 : XE - 10, y0 + 8);
    let y = y0 + 18;
    rows.forEach((r, i) => { const col = r.l.side === "bid" ? G : r.l.side === "ask" ? Rd : r.l.sev >= 4 ? "#f0b90b" : "#c3c9d1";
      c.beginPath(); c.fillStyle = col; c.arc(ar ? XE - 14 : X0 + 14, y + 1, 6, 0, 6.3); c.fill(); c.fillStyle = "#0b0e11"; c.font = "bold 8px sans-serif"; c.textAlign = "center"; c.fillText(String(i + 1), ar ? XE - 14 : X0 + 14, y + 2);
      c.font = fs+"px sans-serif"; c.fillStyle = "#d5dbe2"; c.textAlign = ar ? "right" : "left";
      if (ar) c.direction = "rtl"; r.ws.forEach((t, k) => { c.fillText(iso(t), ar ? XE - 24 : X0 + 24, y + k*lh + 1); }); c.direction = "ltr"; y += r.ws.length*lh + 3;
      if (r.l.p != null){ const Y = py(r.l.p); if (Y > 0 && Y < PB){ c.strokeStyle = col; c.globalAlpha = .55; c.setLineDash([2, 3]); c.beginPath(); c.moveTo(X0 + 5, Y + .5); c.lineTo(XE - 3, Y + .5); c.stroke(); c.setLineDash([]); c.globalAlpha = 1;
        c.beginPath(); c.fillStyle = col; c.arc(XE - 9, Y, 6, 0, 6.3); c.fill(); c.fillStyle = "#0b0e11"; c.font = "bold 8px sans-serif"; c.textAlign = "center"; c.fillText(String(i + 1), XE - 9, Y + 1); } } });
    c.font = "8px sans-serif"; c.fillStyle = "#6b7684"; c.textAlign = ar ? "right" : "left"; c.fillText(ar ? "وصف لآخر دقيقتين، مش توقع" : "describes the last 2 min, not a forecast", ar ? XE - 10 : X0 + 9, y0 + H - 5);
    { const ZS = this.zlog ? ZoneLog.stats(this.zlog) : null; if (ZS && ZS.n){ const zt = ar ? "اختبار المناطق: "+ZS.n+" · لمست "+ZS.z.touch+" · ثبتت "+ZS.z.hold+"/"+(ZS.z.hold + ZS.z.brk)+" (كنترول "+ZS.c.hold+"/"+(ZS.c.hold + ZS.c.brk)+") · "+(ZS.pair >= 100 ? "t "+ZS.t : "مش دليل n<100") : "Zone test: "+ZS.n+" · touched "+ZS.z.touch+" · held "+ZS.z.hold+"/"+(ZS.z.hold + ZS.z.brk)+" (control "+ZS.c.hold+"/"+(ZS.c.hold + ZS.c.brk)+") · "+(ZS.pair >= 100 ? "t "+ZS.t : "not evidence n<100");
      c.fillStyle = "rgba(8,12,18,.78)"; c.fillRect(X0 + 4, y0 + H + 1, w - 8, 12); c.fillStyle = "#9aa4b2"; c.textAlign = ar ? "right" : "left"; if (ar) c.direction = "rtl"; c.fillText(iso(zt), ar ? XE - 10 : X0 + 9, y0 + H + 7, w - 16); c.direction = "ltr"; } }
    c.restore();
  },
  paintSyncCard(c, x0, x1, PB, area){   // card in the empty bottom corner of the order-flow column: the three lights, OI / funding, Gann agreement, recent setups + live forward-test stats
    const sy = this.sync, S = this.st.sync, w = x1 - x0; if (w < 120) return;
    const log = this.syncLog || [], st = this.syncStats(), px = this.data.length ? this.data[this.data.length - 1].c : null, G = S.color, R = S.color2, mono = "9px ui-monospace,Menlo,Consolas,monospace";
    const rows = [];   // [kind, ...] drawn top to bottom; height follows the content
    const stx = st.n ? "n "+st.n+" · "+st.win+"% · "+(st.avg > 0 ? "+" : "")+st.avg+"R" : Lg("no closed setups","مفيش صفقات مقفولة"), stc = !st.n ? "#6b7684" : st.n < 30 ? "#f0b90b" : st.avg > 0 ? "#0ecb81" : "#f6465d";
    c.save(); c.font = mono; const stw = c.measureText(stx).width + 10; c.restore(); const chip = w - stw - 12 > 110;   // stats chip in the header if it fits, else its own row
    rows.push(["lights"]); if (!chip) rows.push(["txt", stc, st.n ? "n "+st.n+" · "+Lg("win ","فوز ")+st.win+"% · "+Lg("avg ","متوسط ")+(st.avg > 0 ? "+" : "")+st.avg+"R"+(st.open ? " · "+st.open+Lg(" open"," مفتوحة") : "") : stx, "bold "]);
    if (sy && sy.dir) rows.push(["big", sy.dir > 0 ? G : R, sy.dir > 0 ? Lg("▲ ALL 3 BUY","▲ التلاتة شراء") : Lg("▼ ALL 3 SELL","▼ التلاتة بيع")]);
    else rows.push(["txt", "#6b7684", Lg("waiting for all three to agree","مستني التلاتة يتفقوا")]);
    if (this.gannOn && this._gannLive){ const gl = this._gannLive, ag = sy && sy.dir === gl.dir, ag2 = sy && sy.dir && !ag;
      rows.push(["txt", gl.dir > 0 ? G : R, (gl.dir > 0 ? "▲" : "▼")+" Gann "+(gl.dir > 0 ? Lg("BUY","شراء") : Lg("SELL","بيع"))+" "+fmtP(gl.en)+(ag ? Lg("  ✓ order flow agrees","  ✓ الأوردر فلو متفق") : ag2 ? Lg("  ✗ order flow against","  ✗ الأوردر فلو عكسه") : ""), "bold "]); }
    { const last = log[log.length - 1], cx = sy && sy.cx, side = sy && sy.dir ? sy.dir : last ? last.dir : 0, o = cx && cx.oi, fu = cx && cx.fund != null ? cx.fund : null;
      if (o || fu != null){ const of = side ? Ctx.oiFlag(cx, side > 0 ? "bullish" : "bearish") : {k:"na", txt:o ? Ctx.oiFlag(cx, "bullish").txt : ""}, ff = side ? Ctx.fundFlag(cx, side > 0 ? "bullish" : "bearish") : null, warn = of.k === "bad" || ff, col = warn ? "#f0b90b" : "#9aa4b2";
        if (o) rows.push(["txt", col, (warn ? "⚠ " : "")+"4h "+of.txt]);
        if (fu != null) rows.push(["txt", col, Lg("funding ","تمويل ")+(fu*100).toFixed(3)+"%"+(ff ? " · "+Lg(ff, ff === "crowded longs" ? "زحمة لونج" : "زحمة شورت") : "")]); }
      else rows.push(["txt", "#4a525c", Lg("OI / funding: loading or n/a","OI / تمويل: بيحمّل أو مش متاح")]); }
    const maxH = area ? area.h : Math.max(110, Math.min(PB*.55, 240)), base = 18 + 30 + 14 + 12;   // header + lights + recent title + footer
    let used = base + (rows.length - 1)*13; const room = Math.max(0, Math.min(5, Math.floor((maxH - used)/12)));
    const recent = room ? log.slice().sort((a, b) => b.t - a.t).slice(0, room) : []; used += recent.length ? 14 + recent.length*12 : 14;
    const h = Math.round(Math.min(used, maxH)), y0 = area ? area.top : PB - h - 30;   // under the column / above the heat-map legend + feed status line
    c.save(); c.fillStyle = "rgba(8,12,18,.9)"; c.strokeStyle = "#2b3139"; c.lineWidth = 1; c.fillRect(x0, y0, w, h); c.strokeRect(x0 + .5, y0 + .5, w - 1, h - 1);
    c.beginPath(); c.rect(x0 + 1, y0 + 1, w - 2, h - 2); c.clip(); c.textBaseline = "middle"; c.textAlign = "left";
    // Arabic lines: right-aligned rtl, every Latin / number token isolated so "+0.88R" or "4h" stay in one piece
    const tx = (t, x, y) => { if (lang !== "ar" || !/[\u0600-\u06FF]/.test(t)){ c.fillText(t, x, y); return; }
      c.save(); c.direction = "rtl"; c.textAlign = "right"; c.fillText(t.replace(/[+\-]?[0-9A-Za-z][0-9A-Za-z.,%:+\-]*(?: +[A-Za-z][A-Za-z.\-]*)*/g, m => "\u2066"+m+"\u2069"), x1 - 7, y); c.restore(); };
    // header: title left, live stats chip right
    c.fillStyle = "rgba(255,255,255,.04)"; c.fillRect(x0 + 1, y0 + 1, w - 2, 17); c.font = "bold 10px sans-serif"; c.fillStyle = "#eaecef"; tx(Lg("ORDER-FLOW SYNC","تزامن الأوردر فلو"), x0 + 7, y0 + 10); this.paintOfX(c, x0 + w - 16, y0 + 3, "_scX");   // ✕ on the card header, in the wide and in the narrow layout
    if (chip){ const cx0 = lang === "ar" ? x0 + 5 : x1 - stw - 20; c.font = mono; c.fillStyle = !st.n ? "#2b3139" : st.n < 30 ? "rgba(240,185,11,.18)" : st.avg > 0 ? "rgba(14,203,129,.2)" : "rgba(246,70,93,.2)"; c.fillRect(cx0, y0 + 3, stw, 13);
      c.fillStyle = stc; c.fillText(stx, cx0 + 5, y0 + 10); }
    let y = y0 + 18;
    rows.forEach(r => {
      if (r[0] === "lights"){ const lab = [Lg("Book","الدفتر"), Lg("Tape","الصفقات"), Lg("Limits","الليمت")], val = sy ? [sy.book, sy.tape, sy.lim] : [null, null, null], cw = (w - 14)/3;
        lab.forEach((l, i) => { const lx = x0 + 7 + i*cw, s_ = sy ? sy.L[i] : 0, col = s_ > 0 ? G : s_ < 0 ? R : "#4a525c", v = val[i];
          c.fillStyle = col; c.beginPath(); c.arc(lx + 5, y + 14, 4.5, 0, 6.3); c.fill(); if (s_){ c.globalAlpha = .25; c.beginPath(); c.arc(lx + 5, y + 14, 8, 0, 6.3); c.fill(); c.globalAlpha = 1; }
          c.font = "9px sans-serif"; c.fillStyle = "#9aa4b2"; c.fillText(l, lx + 14, y + 9); c.font = "bold 10px sans-serif"; c.fillStyle = s_ ? col : "#c3c9d1";
          c.fillText(v == null ? "–" : i < 2 ? (v > 0 ? "+" : "")+Math.round(v*100)+"%" : (v > 0 ? "+" : "")+v, lx + 14, y + 21); });
        y += 30; return; }
      c.fillStyle = r[1]; c.font = r[0] === "big" ? "bold 11px sans-serif" : (r[3] || "")+"9px sans-serif"; tx(r[2], x0 + 7, y + 6); y += 13; });
    // recent setups: time · side · entry · result (closed: R + tick, open: live R)
    c.strokeStyle = "#2b3139"; c.beginPath(); c.moveTo(x0 + 6, y + 2); c.lineTo(x1 - 6, y + 2); c.stroke();
    c.font = "8px sans-serif"; c.fillStyle = "#6b7684"; tx(Lg("RECENT SETUPS  ·  stop 1 ATR · target "+S.rr+"R","آخر الصفقات  ·  ستوب 1 ATR · هدف "+S.rr+"R"), x0 + 7, y + 9); y += 14;
    if (!recent.length && room){ c.font = "9px sans-serif"; c.fillStyle = "#4a525c"; tx(Lg("none yet - needs a live OKX book + tape","لسه مفيش - محتاج دفتر وصفقات OKX لايف"), x0 + 7, y + 5); }
    c.font = mono; recent.forEach(t => { const tm = new Date(t.t), hh = String(tm.getHours()).padStart(2, "0")+":"+String(tm.getMinutes()).padStart(2, "0"), up = t.dir > 0;
      c.fillStyle = "#6b7684"; c.fillText(hh, x0 + 7, y + 5); c.fillStyle = up ? G : R; c.fillText((up ? "▲ " : "▼ ")+fmtP(t.en), x0 + 42, y + 5);
      let rt, col; if (t.res != null){ rt = (t.res > 0 ? "+" : "")+t.res+"R "+(t.res > 0 ? "✓" : "✗"); col = t.res > 0 ? "#0ecb81" : "#f6465d"; }
      else { const r1 = Math.abs(t.en - t.sl) || 1e-9, lr = px == null ? null : Math.round((px - t.en)*t.dir/r1*100)/100; rt = "⏳ "+(lr == null ? "" : (lr > 0 ? "+" : "")+lr+"R"); col = "#f0b90b"; }
      c.textAlign = "right"; c.fillStyle = col; c.fillText(rt, x1 - 7, y + 5); c.textAlign = "left"; y += 12; });
    c.fillStyle = st.n >= 30 ? "#6b7684" : "#f0b90b"; c.font = "8px sans-serif";
    tx(st.n >= 30 ? Lg("live forward test in this browser, no costs","اختبار حي في المتصفح ده، من غير تكاليف") : Lg("under 30 setups = not evidence yet","أقل من 30 صفقة = مش دليل لسه"), x0 + 7, y0 + h - 7);
    c.restore();
  },
  paintLiq(c, py, i0, i1, PB){   // OKX liquidations: one bubble per candle and side at the size-weighted bankruptcy price; red = longs liquidated, green = shorts liquidated
    const d = this.data, n = d.length, G = this.st.liq, sec = this.secMs(); if (!n || !this.liqs.length) return;
    const g = new Map(); this.liqs.forEach(r => { if (r.t < d[0].t || r.t >= d[n-1].t + sec) return; let lo = 0, hi = n - 1; while (lo < hi){ const m = (lo + hi + 1) >> 1; if (d[m].t <= r.t) lo = m; else hi = m - 1; } const i = lo; if (i < i0 || i > i1) return;
      const k = i+"|"+r.side, o = g.get(k) || (g.set(k, {i, side:r.side, usd:0, pv:0}), g.get(k)); o.usd += r.usd; o.pv += r.p*r.usd; });
    const mn = +G.min || 0; c.save();
    g.forEach(o => { if (o.usd < mn || !o.usd) return; const y = py(o.pv/o.usd); if (y < 0 || y > PB) return;
      const x = this.x(o.i), r = Math.min(16, (3 + 2.2*Math.sqrt(o.usd/Math.max(mn, 1000)))*(+G.size || 1)), col = o.side === "L" ? G.color : G.color2;
      c.globalAlpha = .35; c.fillStyle = col; c.beginPath(); c.arc(x, y, r, 0, 6.3); c.fill(); c.globalAlpha = .9; c.strokeStyle = col; c.lineWidth = G.w || 1; c.stroke();
      if (o.usd >= 1e6){ c.beginPath(); c.arc(x, y, r + 3, 0, 6.3); c.stroke(); } });   // $1M+ = double ring
    c.restore(); c.globalAlpha = 1;
  },
  /* ===== GANN v3 (Se7s-style rules, own code) =====
     360 deg level = (sqrt(P/s) +- 2)^2 x s  (P = start price, s = spacing; Square of 9: one turn = +2 on the square root of the scaled price).
     Angles between 0 and 360: "averages" = equal steps (Se7s default; gold 3215.2 / s 100 -> 45 deg 3548.71 ... 360 deg 5883.31), "formula" = (sqrt(P/s) +- 2a/360)^2 x s.
     Shape n (1 circle .. 10 decagon) = main angles every 360/n deg, secondary angles halfway. Time levels every tsp bars from the start bar (+ offset).
     AUTO: on the source timeframe (1D by default, so every chart timeframe shows the same levels) it tries the major swing highs / lows as the start and
     spacings 1/2/2.5/5 x 10^k, counts later swing pivots that land on a level (+-0.25 ATR) and compares with the SAME grid shifted (chance);
     the best excess (z) wins; time spacing is chosen the same way. In-sample fit: it shows what price respected, it does not prove the future. */
  gannCycles(P, s, dir, lo, hi, min){ let base = P, c = 0; if (dir < 0) min = 1; while (c < 12){ c++; const r = Math.sqrt(base/s); base = (dir > 0 ? (r + 2)**2 : Math.max(0, r - 2)**2)*s; if (dir > 0 ? base >= hi : base <= lo) break; } return Math.max(min || 1, c); },
  gannGrid(P, s, dir, G){   // -> [{p, a, main, cyc}]
    const n = Math.max(1, Math.min(10, +G.shape || 4)), stepM = 360/n, stepS = stepM/2, out = [{p:P, a:0, main:true, cyc:0, d:dir}], cyc = Math.max(1, Math.min(12, +G.cycles || 1));
    let base = P;
    for (let c = 0; c < cyc; c++){ const r = Math.sqrt(base/s), L = (dir > 0 ? (r + 2)**2 : Math.max(0, r - 2)**2)*s;
      for (let a = (G.sec ? stepS : stepM); a <= 360 + 1e-9; a += (G.sec ? stepS : stepM)){ const main = Math.abs(a/stepM - Math.round(a/stepM)) < 1e-6;
        const p = (G.calc === "formula") ? (Math.max(0, r + dir*2*a/360))**2*s : base + (L - base)*a/360; out.push({p, a:a + 360*c, main, cyc:c, d:dir}); }
      base = L; }
    return out;
  },
  gannPivots(d, K){ const out = []; for (let i = K; i < d.length - K; i++){ let h = true, l = true; for (let j = i - K; j <= i + K; j++){ if (d[j].h > d[i].h) h = false; if (d[j].l < d[i].l) l = false; } if (h) out.push({i, p:d[i].h, k:1}); if (l) out.push({i, p:d[i].l, k:-1}); } return out; },
  gannFit(d, G){
    const n = d.length; if (n < 60) return null; const piv = this.gannPivots(d, 5); if (piv.length < 8) return null;
    let atr = 0; for (let i = 1; i < n; i++) atr += Math.max(d[i].h - d[i].l, Math.abs(d[i].h - d[i-1].c), Math.abs(d[i].l - d[i-1].c)); atr /= n - 1; const tol = .25*atr;
    // major swings = pivot that is the extreme of +-20 bars, in the first 85 % of the data (so later reactions can be counted)
    const W = Math.max(20, Math.round(n*.08)), isMajor = q => { for (let j = Math.max(0, q.i - W); j <= Math.min(n - 1, q.i + W); j++){ if (q.k > 0 ? d[j].h > q.p : d[j].l < q.p) return false; } return true; };
    let iH = 0, iL = 0; for (let i = 1; i < n; i++){ if (d[i].h > d[iH].h) iH = i; if (d[i].l < d[iL].l) iL = i; }
    const absH = {i:iH, p:d[iH].h, k:1}, absL = {i:iL, p:d[iL].l, k:-1};
    let major = piv.filter(q => q.i <= n*.9 && isMajor(q)); if (!major.some(q => q.i === iH && q.k > 0) && iH <= n*.9) major.push(absH); if (!major.some(q => q.i === iL && q.k < 0) && iL <= n*.9) major.push(absL);
    major.sort((a, b) => a.i - b.i); major = major.slice(-14);
    const anc = G.anc || "best"; if (anc === "high") major = [absH]; else if (anc === "low") major = [absL]; else if (anc === "last" && major.length) major = [major[major.length - 1]];
    const manualP = G.mode === "manual" && +G.start > 0, manualS = G.mode === "manual" && +G.spacing > 0;
    const starts = manualP ? [{i:Math.max(0, n - 1 - (G.tback|0)), p:+G.start, k:G.dir === "down" ? 1 : -1}] : major;
    if (!starts.length) return null; let best = null;
    const score = (lv, q0) => { const later = piv.filter(q => q.i > q0.i + 5); let h = 0; later.forEach(q => { if (lv.some(L => Math.abs(L.p - q.p) <= tol)) h++; }); return [h, later.length]; };
    starts.forEach(q0 => { const P = q0.p; (G.dir === "up" ? [1] : G.dir === "down" ? [-1] : [1, -1]).forEach(dir => {
      const sp = []; if (manualS) sp.push(+G.spacing); else { for (let k = -4; k <= 6; k++) [1, 2, 2.5, 5].forEach(m => { const s_ = m*10**k, R = 4*Math.sqrt(P*s_) + 4*s_; if (R >= .04*P && R <= 1.2*P) sp.push(s_); }); }
      const hiP = Math.max(...d.slice(q0.i).map(x => x.h)), loP = Math.min(...d.slice(q0.i).map(x => x.l));
      sp.forEach(s_ => { const lv = this.gannGrid(P, s_, dir, Object.assign({}, G, {sec:1, cycles:this.gannCycles(P, s_, dir, loP, hiP, 1)})); const [h, m] = score(lv, q0); if (m < 6) return;
        const gap = Math.abs(lv[lv.length - 1].p - P)/Math.max(1, lv.length - 1); let mu = 0; [.2, .4, .6, .8].forEach(f => { mu += score(lv.map(L => ({p:L.p + f*gap})), q0)[0]; }); mu /= 4;
        if (h < 4) return; const z = (h - mu)/Math.sqrt(mu + 1); if (!best || z > best.z) best = {i0:q0.i, t0:d[q0.i].t, P, s:s_, dir, z, hits:h, mu, m, gap}; }); }); });
    if (!best) return null;
    // time spacing: pivots within +-2 bars of start + k x tsp, against the same comb shifted
    const later = piv.filter(q => q.i > best.i0 + 5).map(q => q.i), tc = (+G.tsp > 0) ? [+G.tsp] : [30, 36, 40, 45, 60, 72, 90, 120, 144, 180];
    const hitsT = (tsp, off) => { let h = 0, m = 0; for (let t = best.i0 + tsp + off; t < n - 2; t += tsp){ m++; if (later.some(i => Math.abs(i - t) <= 2)) h++; } return [h, m]; };
    let bt = null; tc.forEach(tsp => { const [h, m] = hitsT(tsp, 0); if (m < 2) return; let mu = 0; [.25, .5, .75].forEach(f => mu += hitsT(tsp, Math.round(f*tsp))[0]); mu /= 3; const z = (h - mu)/Math.sqrt(mu + 1); if (!bt || z > bt.z) bt = {tsp, z, h, m}; });
    best.piv = piv; best.tolP = tol;
    best.tsp = bt ? bt.tsp : 90; best.tz = bt ? bt.z : 0; best.th = bt ? bt.h : 0; best.tm = bt ? bt.m : 0; best.atr = atr;
    const hiA = Math.max(...d.slice(best.i0).map(x => x.h)), loA = Math.min(...d.slice(best.i0).map(x => x.l)), Gc = Object.assign({}, G, {cycles:this.gannCycles(best.P, best.s, best.dir, loA, hiA, +G.cycles || 1)});
    best.levels = this.gannGrid(best.P, best.s, best.dir, Gc).map(L => Object.assign(L, {hits:piv.filter(q => q.i > best.i0 + 5 && Math.abs(q.p - L.p) <= tol).length}));
    if (G.dir === "both") best.levels = best.levels.concat(this.gannGrid(best.P, best.s, -best.dir, Object.assign({}, G, {cycles:this.gannCycles(best.P, best.s, -best.dir, loA, hiA, +G.cycles || 1)})).slice(1).map(L => Object.assign(L, {hits:piv.filter(q => q.i > best.i0 + 5 && Math.abs(q.p - L.p) <= tol).length})));
    return best;
  },
  gannCandles(src){   // -> {d, ms} for a timeframe ("auto" / "chart" = this chart); other timeframes fetched once per symbol for 15 min
    if (!src || src === "auto" || src === "chart") return {d:this.data, ms:this.secMs(), tf:this.tf};
    const MS = {"1m":6e4,"3m":18e4,"5m":3e5,"15m":9e5,"30m":18e5,"1H":36e5,"2H":72e5,"4H":144e5,"6H":216e5,"12H":432e5,"1D":864e5,"1W":6048e5,"1M":2592e6}, ms = MS[src] || 864e5;
    const C = this._gC = this._gC || {}, key = this.sym + "|" + src, c = C[key];
    if ((!c || Date.now() - c.t > 900000) && !(this._gBusy || {})[key]){ (this._gBusy = this._gBusy || {})[key] = true;
      okx("/market/candles?instId="+encodeURIComponent(this.sym)+"&bar="+(TF_OKX[src] || src)+"&limit=300").then(r => { C[key] = {t:Date.now(), ms, tf:src, d:r.map(x => ({t:+x[0], o:+x[1], h:+x[2], l:+x[3], c:+x[4], v:+x[5]})).reverse()}; this.draw(); })
        .catch(() => { C[key] = {t:Date.now(), ms, tf:src, d:null}; }).finally(() => { this._gBusy[key] = false; }); }
    return c && c.d ? {d:c.d, ms:c.ms, tf:src} : null;
  },
  gannSrc(){ return this.gannCandles(this.st.gann.src || "auto"); },
  gannClusters(G, curSrc, curF, tEnd){   // Gann grids of this timeframe + up to 3 higher ones; price levels / time levels that several timeframes share = clusters (weighted)
    const UP = {"1m":["5m","15m","1H"],"3m":["15m","1H","4H"],"5m":["15m","1H","4H"],"15m":["1H","4H","1D"],"30m":["1H","4H","1D"],"1H":["4H","1D","1W"],"2H":["4H","1D","1W"],"4H":["1D","1W","1M"],"6H":["1D","1W","1M"],"12H":["1D","1W","1M"],"1D":["1W","1M"],"1W":["1M"]};
    const cur = String(curSrc.tf || this.tf), curK = /^\d+[mhdw]$/i.test(cur) && !/m$/.test(cur) ? cur.toUpperCase() : cur, tfs = [[curK, curSrc, curF]];
    (UP[curK] || []).slice(0, Math.max(0, Math.min(3, G.mtfn|0 || 3))).forEach(tf => { const sr = this.gannCandles(tf), f = sr ? this.gannFitFor(sr, G) : null; if (f) tfs.push([tf, sr, f]); });
    const key = tfs.map(([tf, sr, f]) => tf + ":" + f.P + ":" + f.s + ":" + f.tsp + ":" + sr.d.length + ":" + sr.d[sr.d.length-1].t).join("|") + "|" + Math.round(tEnd/36e5);
    if (this._gCl && this._gCl.key === key) return this._gCl.v;
    const atr = curF.atr || 1, tolP = (+G.ctol || .35)*atr, P = [], T = [], ms0 = curSrc.ms;
    tfs.forEach(([tf, sr, f], ti) => { const wTF = 1 + .5*ti, sd = sr.d;
      f.levels.forEach(L => { const ring = L.a >= 360 && Math.abs(L.a % 360) < 1e-6; P.push({p:L.p, w:(L.main ? 2 : 1)*(ring ? 2 : 1)*wTF, tf}); });
      let H_ = -Infinity, L0 = Infinity; sd.forEach(k => { if (k.h > H_) H_ = k.h; if (k.l < L0) L0 = k.l; }); [[.5,2],[1/3,1],[2/3,1],[.25,1],[.75,1],[0,1.5],[1,1.5]].forEach(([fr, w]) => P.push({p:L0 + fr*(H_ - L0), w:w*wTF, tf}));
      const st = f.tsp*sr.ms, t1 = f.t0 + (G.toff|0)*sr.ms; for (let k = Math.ceil((sd[0].t - t1)/st); k < 600; k++){ if (!k) continue; const t = t1 + k*st; if (t > tEnd) break; T.push({t, h:Math.max((+G.ctolT || 3)*ms0, .5*sr.ms), w:(Math.abs(k*f.tsp) % 90 === 0 ? 2 : 1)*wTF, tf}); } });
    const group = (arr, val, tol) => { arr.sort((a, b) => val(a) - val(b)); const out = []; let g = null;
      arr.forEach(x => { if (g && val(x) - g.lo <= tol){ g.items.push(x); g.hi = val(x); } else { g = {lo:val(x), hi:val(x), items:[x]}; out.push(g); } });
      return out.map(g => { const w = g.items.reduce((a, x) => a + x.w, 0), tfsS = [...new Set(g.items.map(x => x.tf))]; return {lo:g.lo, hi:g.hi, c:g.items.reduce((a, x) => a + val(x)*x.w, 0)/w, score:Math.round(w*10)/10, tfs:tfsS}; }); };
    const minTF = Math.min(2, tfs.length), PC = group(P, x => x.p, tolP).filter(g => g.tfs.length >= minTF && g.score >= 4).sort((a, b) => b.score - a.score).slice(0, 8);
    // time: every level is a window (+- tolerance on this chart, at least half a bar of its own timeframe); overlapping windows of different timeframes merge
    T.sort((a, b) => (a.t - a.h) - (b.t - b.h)); const TC0 = []; let gT = null;
    T.forEach(x => { if (gT && x.t - x.h <= gT.hi){ gT.items.push(x); gT.hi = Math.max(gT.hi, x.t + x.h); } else { gT = {lo:x.t - x.h, hi:x.t + x.h, items:[x]}; TC0.push(gT); } });
    const TC = TC0.map(g => { const w = g.items.reduce((a, x) => a + x.w, 0); return {lo:g.lo, hi:g.hi, c:g.items.reduce((a, x) => a + x.t*x.w, 0)/w, score:Math.round(w*10)/10, tfs:[...new Set(g.items.map(x => x.tf))]}; })
      .filter(g => g.tfs.length >= minTF).sort((a, b) => a.c - b.c);
    const v = {PC, TC, tfs:tfs.map(x => x[0]), tolP}; this._gCl = {key, v}; return v;
  },
  gannTrades(src, F, G, t1st, step, ovr){   // replay of the zone rule over the source candles + the next zone; cached per data / settings
    const sd = src.d, n = sd.length, key = JSON.stringify([F.P, F.s, F.dir, F.tsp, sd.length, sd[n-1].t, sd[n-1].c, G.zw, G.sqr, G.shape, G.sec, t1st, step, ovr ? ovr.key : 0]);
    if (this._gT && this._gT.key === key) return this._gT.v;
    const atr = F.atr || (sd[n-1].h - sd[n-1].l), tol = .25*atr, zw = Math.max(1, G.zw|0 || 2);
    let ps = F.levels.map(L => L.p); if (G.sqr){ let H_ = -Infinity, L0 = Infinity; sd.forEach(k => { if (k.h > H_) H_ = k.h; if (k.l < L0) L0 = k.l; }); [0,.125,.25,1/3,.375,.5,.625,2/3,.75,.875,1].forEach(f => ps.push(L0 + f*(H_ - L0))); }
    if (ovr) ps = ovr.ps.slice();
    ps = [...new Set(ps.filter(p => p > 0).map(p => +p.toPrecision(10)))].sort((a, b) => a - b);
    const above = (p, minD) => ps.find(q => q > p + minD), below = (p, minD) => [...ps].reverse().find(q => q < p - minD);
    const list = []; const kMin = Math.ceil((sd[0].t - t1st)/step), kMax = Math.floor((sd[n-1].t - t1st)/step);
    const allW = ovr && ovr.times ? ovr.times.slice() : []; if (!(ovr && ovr.times)) for (let k = kMin; k <= kMax + 12; k++) allW.push({t:t1st + k*step, half:zw*src.ms});
    allW.sort((a, b) => a.t - b.t); const wins = allW.filter(w => w.t <= sd[n-1].t + w.half);
    const nextW = (t, skip) => { const f = allW.filter(w => w.t - w.half > t); return f[skip] || null; };   // Gann: time windows after the entry = when the move is due / over
    for (const W of wins){ const tk = W.t; let done = false;
      for (let i = 0; i < n && !done; i++){ if (Math.abs(sd[i].t - tk) > W.half) continue; const b = sd[i];
        for (const L of ps){ if (b.l > L + tol || b.h < L - tol) continue;
          let dir = 0; if (b.c > L + .1*atr && b.c > b.o && b.l <= L + tol) dir = 1; else if (b.c < L - .1*atr && b.c < b.o && b.h >= L - tol) dir = -1; if (!dir) continue;
          const en = b.c, sl = dir > 0 ? Math.min(b.l, L) - tol : Math.max(b.h, L) + tol, rk = Math.abs(en - sl); if (rk <= 0) continue;
          const tp1 = dir > 0 ? (above(en, rk) ?? en + 1.5*rk) : (below(en, rk) ?? en - 1.5*rk), tp2 = dir > 0 ? above(tp1, 0) : below(tp1, 0);
          // time: the next window after the entry = time target, the one after it = time stop (exit at the close if TP1 / stop not hit by then)
          const w1 = nextW(b.t, 0), w2 = nextW(b.t, 1), tT = w1 ? w1.t : b.t + step, tS = w2 ? w2.t + w2.half : b.t + 2*step;
          let res = null, tx = null, how = "";
          for (let j = i + 1; j < n; j++){ const q = sd[j]; if (q.t > tS){ res = Math.round(100*(sd[j - 1].c - en)*dir/rk)/100; tx = sd[j - 1].t; how = "time"; break; }
            if (dir > 0 ? q.l <= sl : q.h >= sl){ res = -1; tx = q.t; how = "stop"; break; } if (dir > 0 ? q.h >= tp1 : q.l <= tp1){ res = Math.round(100*Math.abs(tp1 - en)/rk)/100; tx = q.t; how = "tp"; break; } }
          list.push({t:b.t, dir, en, sl, tp1, tp2, res, tx, how, tT, tS, onTime:how === "tp" && w1 ? tx <= w1.t + w1.half : false, bars:tx ? Math.round((tx - b.t)/src.ms) : null, lo:b.l, hi:b.h, L}); done = true; break; } } }
    const closed = list.filter(x => x.res != null), nC = closed.length;
    const last = sd[n-1].c, kN = Math.max(kMax + 1, Math.ceil((sd[n-1].t - t1st)/step)), nw = ovr && ovr.times ? ovr.times.find(w => w.t > sd[n-1].t) : null;
    const next = {t:nw ? nw.t : t1st + kN*step, half:nw ? nw.half : zw*src.ms, lo:below(last, tol), hi:above(last, tol)};
    const tps = closed.filter(x => x.how === "tp");
    const v = {list, n:nC, win:nC ? Math.round(100*closed.filter(x => x.res > 0).length/nC) : 0, avg:nC ? Math.round(100*closed.reduce((a, x) => a + x.res, 0)/nC)/100 : 0, next, tol,
      onTime:tps.length ? Math.round(100*tps.filter(x => x.onTime).length/tps.length) : null, timeExits:closed.filter(x => x.how === "time").length, bars:nC ? Math.round(closed.reduce((a, x) => a + (x.bars || 0), 0)/nC) : null};
    this._gT = {key, v}; return v;
  },
  gannFitFor(src, G){ if (!src || !src.d || src.d.length < 60) return null; const key = JSON.stringify([this.sym, src.tf, src.d.length, src.d[src.d.length-1].t, G.mode, G.start, G.spacing, G.dir, G.shape, G.calc, G.cycles, G.sec, G.tsp, G.tback, G.anc]);
    const C = this._gF = this._gF || {}; if (!C[key]){ const ks = Object.keys(C); if (ks.length > 6) delete C[ks[0]]; C[key] = {f:this.gannFit(src.d, G)}; } return C[key].f; },
  paintGann(c, py, i0, i1, PB){
    const d = this.data, n = d.length, G = this.st.gann; if (n < 2) return;
    if (!G.v4){ Object.assign(G, {v4:1, src:"auto", htf:"auto", anc:"best", tq:"q", sqr:1, cbox:1, star:0, fan:0}); }
    if (!G.v5){ Object.assign(G, {v5:1, dir:"both", ext:1, cbox:0, tq:"off", fan:1}); }   // v5: grid both ways and across the whole history (past touches marked), geometry on the major range   // v3 -> v4: fit every timeframe by itself
    const src = this.gannSrc(), PR = this.PR;
    if (!src || !src.d){ c.save(); c.fillStyle = G.color; c.font = "10px sans-serif"; c.textBaseline = "top"; c.fillText(Lg("Gann: loading "+(G.src || "auto")+" candles…","جان: بيحمّل شموع "+(G.src || "auto")+"…"), 40, 4); c.restore(); return; }
    const F = this.gannFitFor(src, G); this._gFit = {f:F}; if (!F){ c.save(); c.fillStyle = G.color; c.font = "10px sans-serif"; c.textBaseline = "top"; c.fillText(Lg("Gann: not enough swings on "+(src.tf || "this chart")+" - load more history or pick a lower timeframe","جان: مفيش قمم وقيعان كفاية على "+(src.tf || "الشارت")+" - حمّل تاريخ أكتر أو اختار فريم أصغر"), 40, 4); c.restore(); return; }
    const sec = this.secMs(), xT = t => this.x((t - d[0].t)/sec), x0 = Math.max(0, Math.min(PR, xT(F.t0)));
    let t0 = F.t0; if (G.mode === "manual" && /^\d{4}-\d\d-\d\d$/.test(G.tdate || "")) t0 = Date.parse(G.tdate + "T00:00:00Z");
    c.save(); c.textBaseline = "middle"; c.font = "10px sans-serif";
    // the major range (highest high / lowest low on the source) - the frame for the square of the range, the Gann box geometry and the star
    const sd = src.d; let iH = 0, iL = 0; for (let i = 1; i < sd.length; i++){ if (sd[i].h > sd[iH].h) iH = i; if (sd[i].l < sd[iL].l) iL = i; }
    const RH = sd[iH].h, RL = sd[iL].l, RR = RH - RL, tA = Math.min(sd[iH].t, sd[iL].t), tB = Math.max(sd[iH].t, sd[iL].t), dur = Math.max(src.ms, tB - tA), upR = sd[iL].t < sd[iH].t;
    const tolP = F.tolP || (RR*.01), piv = F.piv || [];
    // price levels, drawn across the whole history; every past swing that reacted on a level gets a small ring (the check that the level worked)
    const visL = F.levels.map(L => ({L, y:py(L.p)})).filter(o => o.y >= -2 && o.y <= PB + 2 && o.L.p > 0).sort((a, b) => a.y - b.y), keepL = []; let lastY = -1e9, lastLbl = -1e9;
    visL.forEach(o => { const ring = o.L.a >= 360 && Math.abs(o.L.a % 360) < 1e-6; if (!ring && o.y - lastY < (o.L.main ? 6 : 14)) return; o.lbl = o.y - lastLbl >= 11; if (o.lbl) lastLbl = o.y; lastY = o.y; keepL.push(o); });
    keepL.forEach(({L, y, lbl}) => { const touch = piv.filter(q => Math.abs(q.p - L.p) <= tolP), strong = touch.length >= 2, col = L.main ? G.color : (G.color2 || "#f6465d");
      c.strokeStyle = col; c.globalAlpha = L.main ? (strong ? .95 : .65) : (strong ? .75 : .4); c.lineWidth = (L.main ? 1.4 : 1)*(G.w || 1)*(strong ? 1.4 : 1); c.setLineDash(L.main ? [] : [5,4]);
      c.beginPath(); c.moveTo(G.ext ? 0 : x0, y); c.lineTo(PR, y); c.stroke(); c.setLineDash([]);
      c.globalAlpha = .9; c.lineWidth = 1.2; touch.forEach(q => { const x = xT(sd[q.i].t); if (x < 0 || x > PR) return; c.beginPath(); c.arc(x, py(q.p), 3.5, 0, 6.3); c.stroke(); });
      const ring = L.a >= 360 && Math.abs(L.a % 360) < 1e-6 ? Math.round(L.a/360) : 0;   // 360 / 720 / 1080 ... = end of ring 1 / 2 / 3 (+2 on the square root per ring)
      if (ring){ c.globalAlpha = .9; c.strokeStyle = col; c.lineWidth = 2.6; c.beginPath(); c.moveTo(G.ext ? 0 : x0, y); c.lineTo(PR, y); c.stroke(); }
      if (G.lbl && lbl){ c.globalAlpha = .95; c.fillStyle = col; c.textAlign = "right"; c.fillText((L.d < 0 ? "-" : "")+Math.round(L.a)+"° = "+fmtP(L.p)+(ring ? "  "+Lg("ring ","حلقة ")+ring : "")+(touch.length ? "  ×"+touch.length : ""), PR - 6, y - 7); } });
    c.textAlign = "left";
    // time levels every tsp source bars from the start, forward AND backward over the history; a swing within +-2 bars of a level gets a small triangle
    const tsp = F.tsp, toff = G.toff|0, step = tsp*src.ms, tEnd = d[n-1].t + Math.max(60, (PR - this.x(n-1))/this.bw)*sec, t1st = t0 + toff*src.ms;
    if (G.tlv){ const kMin = Math.ceil((sd[0].t - t1st)/step); for (let k = kMin; k < 400; k++){ if (!k) continue; const t = t1st + k*step; if (t > tEnd) break; const x = xT(t); if (x < 0 || x > PR) continue; const big = Math.abs(k*tsp) % 90 === 0;
        const hit = piv.some(q => Math.abs(sd[q.i].t - t) <= 2*src.ms);
        c.strokeStyle = G.color; c.globalAlpha = big ? .6 : .28; c.lineWidth = big ? 1.3 : 1; c.setLineDash(big ? [] : [2,4]); c.beginPath(); c.moveTo(x, 0); c.lineTo(x, PB); c.stroke(); c.setLineDash([]);
        if (hit){ c.globalAlpha = .95; c.fillStyle = G.color; c.beginPath(); c.moveTo(x, PB - 2); c.lineTo(x - 4, PB - 9); c.lineTo(x + 4, PB - 9); c.closePath(); c.fill(); }
        if (G.lbl){ c.globalAlpha = .9; c.fillStyle = G.color; c.fillText((k > 0 ? "" : "-")+Math.abs(k*tsp)+"", x + 2, 8); } } }
    // long cycles for big timeframes (Gann's master cycles): 49 / 90 / 180 days, 1 / 2 / 3 / 5 / 7 / 10 / 20 / 30 years from the major high and the major low
    const lc = G.lcyc || "auto", lcOn = lc === "on" || (lc === "auto" && sec >= 864e5);
    if (lcOn){ const Y = 365.25*864e5, IV = [[49*864e5,"49d"],[90*864e5,"90d"],[180*864e5,"180d"],[Y,"1y"],[2*Y,"2y"],[3*Y,"3y"],[5*Y,"5y"],[7*Y,"7y"],[10*Y,"10y"],[20*Y,"20y"],[30*Y,"30y"]].filter(([v]) => v >= 3*sec);
      const anc = [[sd[iH].t, "H"], [sd[iL].t, "L"]], marks = [];
      const allLC = lc === "on"; anc.forEach(([ta, k]) => IV.forEach(([v, lb]) => { for (let m = 1; m <= (allLC ? 3 : 1); m++){ const t = ta + m*v; if (t > tEnd || (m > 1 && lb.endsWith("y") && v >= 10*Y)) break; marks.push({t, lb:(m > 1 ? m+"×" : "")+lb+" "+k, big:v >= Y}); if (v < Y) break; } }));
      marks.forEach(m => { m.conf = marks.some(o => o !== m && o.lb.slice(-1) !== m.lb.slice(-1) && Math.abs(o.t - m.t) <= Math.max(2*sec, .02*Math.min(Math.abs(m.t - sd[iH].t), Math.abs(m.t - sd[iL].t)))); });
      if (!allLC){ const keep = marks.filter(m => m.conf || /^(5|7|10|20|30)y/.test(m.lb)); marks.length = 0; keep.forEach(m => marks.push(m)); }
      marks.sort((a, b) => a.t - b.t); let lastX = -1e9, row = 0;
      marks.forEach(m => { const x = xT(m.t); if (x < 0 || x > PR) return; row = x - lastX < 70 ? (row + 1) % 4 : 0; lastX = x; m.ly = 22 + row*11; c.strokeStyle = "#ff9800"; c.globalAlpha = m.conf ? .95 : m.big ? .6 : .35; c.lineWidth = m.conf ? 2.2 : m.big ? 1.3 : 1; c.setLineDash(m.conf ? [] : [6,4]);
        c.beginPath(); c.moveTo(x, 0); c.lineTo(x, PB); c.stroke(); c.setLineDash([]); c.globalAlpha = .95; c.fillStyle = "#ff9800"; c.font = (m.conf ? "bold " : "")+"9px sans-serif"; c.fillText((m.conf ? "★ " : "")+m.lb, x + 3, m.ly); });
      c.font = "10px sans-serif"; }
    // Gann box on the major range (price high-low x its duration), repeated forward: diagonals 1x1 + 1x2 / 2x1 and the star inside it - so the geometry sits on the price
    const boxes = []; for (let k = 0; k < 6; k++){ const ta = tA + k*dur; if (ta > tEnd) break; boxes.push([ta, ta + dur]); }
    if (G.fan) boxes.forEach(([ta, tb], k) => { const xa = xT(ta), xb = xT(tb), yH = py(RH), yL = py(RL); if (xb < 0 || xa > PR) return;
      c.strokeStyle = G.color; c.globalAlpha = k ? .35 : .55; c.lineWidth = 1; c.strokeRect(xa, yH, xb - xa, yL - yH);
      [[0, 1, .8], [0, .5, .45], [0, 2, .45]].forEach(([_, m, al]) => { c.globalAlpha = al*(k ? .7 : 1); c.beginPath(); c.moveTo(xa, yL); c.lineTo(xa + (xb - xa)*Math.min(1, 1/m), yL - (yL - yH)*Math.min(1, m)); c.stroke();
        c.beginPath(); c.moveTo(xa, yH); c.lineTo(xa + (xb - xa)*Math.min(1, 1/m), yH + (yL - yH)*Math.min(1, m)); c.stroke(); });
      c.globalAlpha = .35; c.setLineDash([3,3]); c.beginPath(); c.moveTo((xa + xb)/2, yH); c.lineTo((xa + xb)/2, yL); c.moveTo(xa, (yH + yL)/2); c.lineTo(xb, (yH + yL)/2); c.stroke(); c.setLineDash([]); });
    if (G.star) boxes.slice(0, 3).forEach(([ta, tb], k) => { const sp = Math.max(3, Math.min(12, G.spts|0 || 8)), cxT = (ta + tb)/2, cp = (RH + RL)/2, V = [];
      for (let j = 0; j < sp; j++){ const a = Math.PI + j*2*Math.PI/sp; V.push([xT(cxT + dur/2*Math.cos(a)), py(cp + RR/2*Math.sin(a))]); }
      c.strokeStyle = G.starc || "#f0b90b"; c.globalAlpha = k ? .3 : .55; c.lineWidth = 1; c.beginPath(); c.ellipse(xT(cxT), py(cp), Math.abs(xT(tb) - xT(ta))/2, Math.abs(py(RL) - py(RH))/2, 0, 0, 6.3); c.stroke();
      const jump = sp >= 5 ? Math.floor((sp - 1)/2) : 1, seen = new Set(); for (let s0 = 0; s0 < sp; s0++){ if (seen.has(s0)) continue; c.beginPath(); let j = s0; c.moveTo(V[j][0], V[j][1]); do { seen.add(j); j = (j + jump) % sp; c.lineTo(V[j][0], V[j][1]); } while (j !== s0); c.stroke(); } });
    // GANN ZONE TRADES: at every time level (+- zw source bars) a candle that touches a price level and closes back away from it = confirmation (arrow);
    // entry = that close, stop = beyond the touch (0.25 ATR), TP1 / TP2 = the next Gann levels in the trade direction (min 1R). Replayed over the whole history
    // (ticks / crosses = past outcomes, stats on the chart) and followed live; the next zone is a thin box on the nearest level above (sell) and below (buy).
    let CL = null; if (G.mtf !== "off"){ CL = this.gannClusters(G, src, F, tEnd);
      CL.PC.forEach(g => { const ya = py(g.hi + CL.tolP*.3), yb = py(g.lo - CL.tolP*.3); if (yb < 0 || ya > PB) return; const a = Math.min(.35, .08 + g.score/60);
        c.globalAlpha = a; c.fillStyle = "#f0b90b"; c.fillRect(0, ya, PR, Math.max(2, yb - ya)); c.globalAlpha = .95; c.fillStyle = "#f0b90b"; c.font = "bold 9px sans-serif";
        c.fillText("★ "+g.tfs.length+" TF ("+g.tfs.join("·")+") "+fmtP(g.c)+" · "+Lg("score ","قوة ")+g.score, PR*.6, ya - 4); });
      CL.TC.forEach(g => { const xa = xT(g.lo), xb = xT(g.hi); if (xb < 0 || xa > PR) return; c.globalAlpha = Math.min(.3, .06 + g.score/50); c.fillStyle = "#f0b90b"; c.fillRect(xa, 0, Math.max(3, xb - xa), PB);
        c.globalAlpha = .95; c.fillStyle = "#f0b90b"; c.font = "bold 9px sans-serif"; c.fillText("★ "+g.tfs.join("·"), xa + 2, PB - 40); });
      c.font = "10px sans-serif"; }
    if (G.zone){ const ovr = CL && G.zsrc === "clusters" && CL.PC.length ? {key:CL.PC.map(g => g.c.toFixed(6)).join(",")+"|"+CL.TC.map(g => g.c).join(","), ps:CL.PC.map(g => g.c).concat(F.levels.filter(L => L.main).map(L => L.p).filter(p => !CL.PC.some(g => Math.abs(g.c - p) <= CL.tolP))),   // clusters first, this grid's main levels fill the gaps
        times:CL.TC.length ? CL.TC.map(g => ({t:(g.lo + g.hi)/2, half:Math.max((Math.max(1, G.zw|0 || 2))*src.ms, (g.hi - g.lo)/2)})) : null} : null;
      const T = this.gannTrades(src, F, G, t1st, step, ovr); T.cl = ovr ? CL.PC : null; const tf = src.tf || this.tf, ttype = sec <= 9e5 ? Lg("scalp","سكالب") : sec < 864e5 ? Lg("day trade","داي تريد") : Lg("swing","سوينج");
      T.list.forEach(tr => { const x = xT(tr.t), y = py(tr.en); if (x < -10 || x > PR + 10) return; const up = tr.dir > 0, col = up ? "#0ecb81" : "#f6465d", live = tr.res == null;
        c.globalAlpha = live ? 1 : .8; c.fillStyle = col; c.beginPath(); const ay = up ? py(tr.lo) + 14 : py(tr.hi) - 14; c.moveTo(x, ay + (up ? -8 : 8)); c.lineTo(x - 6, ay + (up ? 3 : -3)); c.lineTo(x + 6, ay + (up ? 3 : -3)); c.closePath(); c.fill();
        if (!live){ c.font = "bold 10px sans-serif"; c.fillStyle = tr.res > 0 ? "#0ecb81" : "#f6465d"; c.fillText((tr.res > 0 ? "✓" : "✗")+(tr.how === "time" ? "⌛" : tr.onTime ? "⏱" : ""), x - 3, ay + (up ? 14 : -12)); c.font = "10px sans-serif"; } });
      const L_ = T.list[T.list.length - 1];
      if (L_ && L_.res == null && d[n-1].t - L_.t <= 3*src.ms){ const id = "gann|"+this.sym+"|"+tf+"|"+L_.t, up = L_.dir > 0; this._gannLive = {dir:L_.dir, t:L_.t, en:L_.en};
        if (!(this._gAl || (this._gAl = new Set())).has(id)){ this._gAl.add(id); try { Alerts.add(id, "gann", this.sym, this.sym+" · Gann "+(up ? "BUY" : "SELL")+" · "+tf+" · "+Lg("entry ","دخول ")+fmtP(L_.en)+" · SL "+fmtP(L_.sl)+" · TP1 "+fmtP(L_.tp1)+" · ⏱ "+new Date(L_.tT).toISOString().slice(5, 16).replace("T"," ")+" · ⌛ "+new Date(L_.tS).toISOString().slice(5, 16).replace("T"," "), up ? "#0ecb81" : "#f6465d"); } catch(e){} } }
      else this._gannLive = null;
      if (L_ && L_.res == null){ const x = xT(L_.t), xe = PR - 4, up = L_.dir > 0, rk = Math.abs(L_.en - L_.sl);
        [[L_.en, "#4aa3ff", Lg("entry ","دخول ")], [L_.sl, "#f6465d", Lg("stop ","ستوب ")], [L_.tp1, "#0ecb81", "TP1 "], [L_.tp2, "#0ecb81", "TP2 "]].forEach(([p, col, lb]) => { if (p == null) return; const y = py(p); if (y < 0 || y > PB) return;
          c.strokeStyle = col; c.globalAlpha = .9; c.lineWidth = 1.4; c.setLineDash(lb === "TP2 " ? [5,4] : []); c.beginPath(); c.moveTo(x, y); c.lineTo(xe, y); c.stroke(); c.setLineDash([]);
          c.fillStyle = col; c.font = "bold 10px sans-serif"; c.textAlign = "right"; c.fillText(lb+fmtP(p)+(lb === "TP1 " || lb === "TP2 " ? "  "+(Math.abs(p - L_.en)/rk).toFixed(1)+"R" : ""), xe - 60, y - 7); c.textAlign = "left"; });
        [[L_.tT, "#4aa3ff", Lg("⏱ target time ","⏱ وقت الهدف ")], [L_.tS, "#f6465d", Lg("⌛ time stop ","⌛ ستوب زمني ")]].forEach(([t, col, lb]) => { if (!t) return; const xt = xT(t); if (xt < 0 || xt > PR) return;
          c.strokeStyle = col; c.globalAlpha = .85; c.lineWidth = 1.3; c.setLineDash([6,4]); c.beginPath(); c.moveTo(xt, py(Math.max(L_.tp1, L_.sl, L_.en)) - 20); c.lineTo(xt, py(Math.min(L_.tp1, L_.sl, L_.en)) + 20); c.stroke(); c.setLineDash([]);
          c.fillStyle = col; c.font = "bold 9px sans-serif"; c.fillText(lb+new Date(t).toISOString().slice(5, 16).replace("T"," "), xt + 3, py(Math.max(L_.tp1, L_.sl, L_.en)) - 24); });
        c.fillStyle = up ? "#0ecb81" : "#f6465d"; c.font = "bold 11px sans-serif"; c.fillText((up ? "▲ " : "▼ ")+Lg("Gann ","جان ")+(up ? Lg("BUY","شراء") : Lg("SELL","بيع"))+" · "+ttype+" · "+tf, x + 8, py(L_.en) + (up ? 16 : -14)); c.font = "10px sans-serif"; }
      // the next zones (not yet confirmed): thin boxes on the nearest level below (buy) and above (sell), +- zw source bars around the next time level
      const zw = Math.max(1, G.zw|0 || 2), nx = T.next; if (nx){ [[nx.lo, 1], [nx.hi, -1]].forEach(([p, dir]) => { if (p == null) return; const half = nx.half || zw*src.ms, cl = T.cl && T.cl.find(g => Math.abs(g.c - p) < 1e-9), xa = xT(nx.t - half), xb = xT(nx.t + half), ya = py((cl ? cl.hi : p) + T.tol), yb = py((cl ? cl.lo : p) - T.tol);
          const col = dir > 0 ? "#0ecb81" : "#f6465d"; c.globalAlpha = .16; c.fillStyle = col; c.fillRect(Math.min(xa, xb), ya, Math.max(3, Math.abs(xb - xa)), Math.max(2, yb - ya)); c.globalAlpha = .9; c.strokeStyle = col; c.setLineDash([4,3]); c.strokeRect(Math.min(xa, xb), ya, Math.max(3, Math.abs(xb - xa)), Math.max(2, yb - ya)); c.setLineDash([]);
          c.fillStyle = col; c.font = "bold 9px sans-serif"; c.fillText((cl ? "★ " : "")+(dir > 0 ? Lg("buy zone ","منطقة شراء ") : Lg("sell zone ","منطقة بيع "))+fmtP(p)+(cl ? " ("+cl.tfs.join("·")+")" : "")+" · "+new Date(nx.t).toISOString().slice(5, 16).replace("T"," "), Math.min(xa, xb), dir > 0 ? yb + 10 : ya - 8); c.font = "10px sans-serif"; }); }
      c.globalAlpha = .95; c.fillStyle = T.n >= 30 ? "#c3c9d1" : "#f0b90b"; c.font = "9px sans-serif";
      this.infoOpen !== false && c.fillText(Lg("Gann zone trades on this history: ","صفقات مناطق جان على التاريخ ده: ")+(T.n ? "n "+T.n+" · "+Lg("win ","فوز ")+T.win+"% · "+Lg("avg ","متوسط ")+(T.avg > 0 ? "+" : "")+T.avg+"R" : Lg("none yet","لسه مفيش"))+(T.n ? (T.onTime != null ? Lg(" · TP on time ","· الهدف في وقته ")+T.onTime+"%" : "")+" · "+Lg("time exits ","خروج بالزمن ")+T.timeExits+" · "+Lg("avg ","متوسط ")+T.bars+Lg(" bars"," شمعة") : "")+(T.n < 30 ? Lg(" · under 30 = not evidence"," · أقل من 30 = مش دليل") : "")+Lg(" · in-sample (the grid was fitted on the same data)"," · على نفس البيانات اللي الشبكة اتظبطت عليها"), 40, 50);
      // weekly lab, out of sample (fit on the first 60 %, traded on the last 40 %, vs random direction) for this timeframe
      const oo = (CFG.gannoos || {})[String(tf).toLowerCase()]; if (oo && oo.n){ const ev = oo.n >= 100 && oo.t > 3; c.fillStyle = ev ? "#0ecb81" : "#f0b90b";
        this.infoOpen !== false && c.fillText(Lg("Lab out of sample ("+tf+"): ","المعمل خارج العينة ("+tf+"): ")+"n "+oo.n+" · "+Lg("win ","فوز ")+oo.win+"% · "+Lg("avg ","متوسط ")+(oo.avg > 0 ? "+" : "")+oo.avg+"R · "+Lg("random ","عشوائي ")+(oo.rnd > 0 ? "+" : "")+oo.rnd+"R · t "+oo.t+(ev ? Lg(" · passes the bar"," · عدّى شرط الدليل") : Lg(" · not evidence (needs t>3, n≥100)"," · مش دليل (محتاج t>3 و n≥100)")), 40, 62); }
      c.font = "10px sans-serif"; }
    const HT = {"1m":"15m","3m":"1H","5m":"1H","15m":"4H","30m":"4H","1h":"1D","1H":"1D","2h":"1D","2H":"1D","4h":"1D","4H":"1D","6H":"1W","12H":"1W","1d":"1W","1D":"1W","1w":"1M","1W":"1M"};
    const cycT = (+G.shape || 4)*tsp*src.ms;   // one full 360-degree cycle in time = shape x time spacing
    // cycle boxes: where each 360-degree price cycle starts and ends, in price and in time
    if (G.cbox){ const ends = F.levels.filter(L => L.a > 0 && Math.abs(L.a % 360) < 1e-6 && L.d === F.dir).sort((a, b) => a.a - b.a); let base = F.P;
      ends.forEach((L, k) => { const ta = t0 + k*cycT, tb = t0 + (k + 1)*cycT, xa = xT(ta), xb = xT(tb), ya = py(base), yb = py(L.p);
        c.globalAlpha = .55; c.strokeStyle = G.color; c.setLineDash([6,4]); c.lineWidth = 1; c.strokeRect(Math.min(xa, xb), Math.min(ya, yb), Math.abs(xb - xa), Math.abs(yb - ya)); c.setLineDash([]);
        c.globalAlpha = .95; c.fillStyle = G.color; c.font = "bold 9px sans-serif"; c.fillText(Lg("cycle ","دورة ")+(k + 1)+Lg(" end ", " نهاية ")+new Date(tb).toISOString().slice(0, 10)+" · "+fmtP(L.p), Math.min(PR - 160, Math.max(4, xb - 150)), Math.min(ya, yb) - 8);
        base = L.p; }); c.font = "10px sans-serif"; }
    // time quarters / eighths / thirds of each cycle, or calendar 90-180-270-360 days from the start (anniversaries)
    if (G.tq && G.tq !== "off"){ const fr = G.tq === "e" ? [1,2,3,4,5,6,7,8].map(k => k/8) : G.tq === "t" ? [1/3, 2/3, 1] : [.25, .5, .75, 1];
      const marks = []; if (G.tq === "cal"){ for (let k = 1; k <= 24; k++) marks.push({t:t0 + k*90*864e5, lb:(k*90)+"d", big:k % 4 === 0}); }
      else for (let cyc = 0; cyc < 6; cyc++) fr.forEach(f => marks.push({t:t0 + (cyc + f)*cycT, lb:(cyc ? (cyc + 1)+"·" : "")+(G.tq === "t" ? Math.round(f*3)+"/3" : G.tq === "e" ? Math.round(f*8)+"/8" : Math.round(f*4)+"/4"), big:Math.abs(f - .5) < 1e-6 || f === 1}));
      marks.forEach(m => { if (m.t > tEnd) return; const x = xT(m.t); if (x < 0 || x > PR) return; c.strokeStyle = "#e056fd"; c.globalAlpha = m.big ? .8 : .45; c.lineWidth = m.big ? 1.5 : 1; c.setLineDash(m.big ? [] : [3,3]);
        c.beginPath(); c.moveTo(x, 0); c.lineTo(x, PB); c.stroke(); c.setLineDash([]); c.globalAlpha = .9; c.fillStyle = "#e056fd"; c.fillText(m.lb, x + 2, PB - 10); }); }
    // square of the range: eighths and thirds of the major range in price (50 % strongest), and its duration in eighths projected forward in time
    if (G.sqr){ [[0,1],[.125,0],[.25,1],[1/3,1],[.375,0],[.5,2],[.625,0],[2/3,1],[.75,1],[.875,0],[1,1]].forEach(([f, w]) => { const p = RL + f*RR, y = py(p); if (y < 0 || y > PB) return;
        const touch = piv.filter(q => Math.abs(q.p - p) <= tolP).length;
        c.strokeStyle = "#b57cff"; c.globalAlpha = w === 2 ? .85 : w ? .55 : .3; c.lineWidth = w === 2 ? 1.6 : 1; c.setLineDash(w ? [8,3] : [2,4]); c.beginPath(); c.moveTo(0, y); c.lineTo(PR, y); c.stroke(); c.setLineDash([]);
        if (w){ c.globalAlpha = .9; c.fillStyle = "#b57cff"; c.fillText((Math.round(f*1000)/10)+"% "+fmtP(p)+(touch ? " ×"+touch : ""), PR*.45, y - 7); } });
      for (let k = 1; k <= 16; k++){ const t = tB + k*dur/8; if (t > tEnd) break; const x = xT(t); if (x < 0 || x > PR) continue; const q = k % 2 === 0;
        c.strokeStyle = "#b57cff"; c.globalAlpha = k % 8 === 0 ? .8 : q ? .5 : .25; c.setLineDash(q ? [8,3] : [2,4]); c.beginPath(); c.moveTo(x, PB*.55); c.lineTo(x, PB); c.stroke(); c.setLineDash([]);
        if (q){ c.globalAlpha = .9; c.fillStyle = "#b57cff"; c.fillText((k/8)+"R", x + 2, PB - 22); } } }
    // higher-timeframe grid (same rules, its own fit) so the timeframes line up: thick faint lines tagged with the timeframe
    if (G.htf && G.htf !== "off"){ const htf = G.htf === "auto" ? (HT[this.tf] || HT[String(this.tf).toUpperCase()] || "1D") : G.htf, hs = htf !== src.tf ? this.gannCandles(htf) : null, HF = hs ? this.gannFitFor(hs, G) : null;
      if (HF) HF.levels.forEach(L => { if (!L.main) return; const y = py(L.p); if (y < 0 || y > PB) return; c.strokeStyle = G.color; c.globalAlpha = .22; c.lineWidth = 4; c.beginPath(); c.moveTo(0, y); c.lineTo(PR, y); c.stroke();
        c.globalAlpha = .85; c.fillStyle = G.color; c.font = "bold 9px sans-serif"; c.fillText("["+htf+"] "+Math.round(L.a)+"°", PR*.28, y - 7); c.font = "10px sans-serif"; }); }
    // start mark + summary
    c.globalAlpha = 1; c.fillStyle = G.color; c.beginPath(); c.arc(xT(t0), py(F.P), 4, 0, 6.3); c.fill();
    c.font = "bold 10px sans-serif"; c.textBaseline = "top"; const auto = G.mode !== "manual";
    if (this.infoOpen !== false) c.fillText("Gann "+(auto ? "AUTO" : "MANUAL")+" ("+(src.tf || "chart")+") · "+Lg("start ","بداية ")+fmtP(F.P)+(F.dir > 0 ? " ▲" : " ▼")+" "+new Date(t0).toISOString().slice(0, 10)+" · "+Lg("spacing ","تباعد ")+F.s+" · "+["","circle","line","triangle","square","pentagon","hexagon","heptagon","octagon","nonagon","decagon"][+G.shape || 4], 40, 24);
    c.font = "9px sans-serif"; c.fillStyle = "#9aa4b2";
    if (this.infoOpen !== false) c.fillText(Lg("price: ","السعر: ")+F.hits+"/"+F.m+Lg(" later swings on a level (chance ~"," قمة/قاع لاحقة على مستوى (الصدفة ~")+F.mu.toFixed(1)+", z "+F.z.toFixed(1)+") · "+Lg("time every ","الوقت كل ")+tsp+Lg(" bars: "," شمعة: ")+F.th+"/"+F.tm+" (z "+F.tz.toFixed(1)+")"+Lg(" · in-sample fit, not a forecast"," · مطابقة على الماضي، مش توقع"), 40, 37);
    c.restore(); c.globalAlpha = 1; c.textBaseline = "middle"; c.font = "11px ui-monospace,Menlo,Consolas,monospace";
  },
  paintKZS(c, py, i0, i1, PB){
    if (this.secMs() > 3600*1000){ c.globalAlpha = .8; c.fillStyle = TH.mut; c.font = "10px sans-serif"; c.textBaseline = "top"; c.fillText(Lg("Kill Zone Sniper: 1H and lower only","Kill Zone Sniper: فريم ساعة وأقل بس"), 40, PB - 16); c.globalAlpha = 1; return; }
    const L = this.kzsCalc(), step = this.bw, up = TH.up, dn = TH.dn, gold = "#f0b90b";
    c.save(); c.textBaseline = "middle";
    L.forEach(s => {
      if (s.end < i0 - 1 || s.j > i1 + 1) return;
      const xs = this.x(s.j), xe = this.x(s.res === "open" ? Math.min(this.data.length-1, s.j + 24) : s.end) + step/2, w = Math.max(step, xe - xs), ye = py(s.en), ys = py(s.sl), yt = py(s.tp);
      // projection: green box entry->target, red box entry->stop (JOAT-style), faded once the trade is finished
      const live = s.res === "open"; c.globalAlpha = live ? .2 : .1;
      c.fillStyle = up; c.fillRect(xs, Math.min(ye, yt), w, Math.abs(yt - ye)); c.fillStyle = dn; c.fillRect(xs, Math.min(ye, ys), w, Math.abs(ys - ye));
      c.globalAlpha = live ? .9 : .45; c.lineWidth = 1;
      [[ye, "#4aa3ff"], [ys, dn], [yt, up]].forEach(([y, col]) => { c.strokeStyle = col; c.beginPath(); c.moveTo(xs, Math.round(y)+.5); c.lineTo(xs + w, Math.round(y)+.5); c.stroke(); });
      // the swept pool: dashed gold line from 20 bars back to the sweep candle
      c.strokeStyle = gold; c.setLineDash([4,3]); c.beginPath(); const yl = Math.round(py(s.lvl))+.5; c.moveTo(this.x(Math.max(0, s.j-20)), yl); c.lineTo(xs, yl); c.stroke(); c.setLineDash([]);
      // sniper mark: crosshair on the sweep wick + label
      const wy = py(s.side > 0 ? this.data[s.j].l : this.data[s.j].h) + (s.side > 0 ? 10 : -10), col = s.side > 0 ? up : dn; c.globalAlpha = 1; c.strokeStyle = col; c.lineWidth = 1.5;
      c.beginPath(); c.arc(xs, wy, 5, 0, Math.PI*2); c.moveTo(xs-8, wy); c.lineTo(xs+8, wy); c.moveTo(xs, wy-8); c.lineTo(xs, wy+8); c.stroke(); c.lineWidth = 1;
      c.font = "bold 9px sans-serif"; c.fillStyle = col; c.textAlign = "center"; c.fillText("KZS "+(s.side > 0 ? "▲" : "▼"), xs, wy + (s.side > 0 ? 15 : -15)); c.textAlign = "left";
      if (w > 40){ c.font = "9px sans-serif"; c.fillStyle = TH.mut;
        const tag = {tp:"TP ✓", sl:"SL ✗", exp:Lg("expired","انتهت"), open:Lg("open","مفتوحة")}[s.res];
        c.fillText(s.kz+" · "+s.rr.toFixed(1)+"R · "+tag, xs + 3, yt + (s.side > 0 ? -7 : 7)); }
    });
    // dashboard: counts of what is drawn on this chart - not a win rate claim (small n, one symbol, one timeframe)
    const tp = L.filter(s => s.res === "tp").length, sl = L.filter(s => s.res === "sl").length, op = L.filter(s => s.res === "open" || s.res === "exp").length;
    const rows = [["Kill Zone Sniper", ""], [Lg("signals in history","إشارات في التاريخ"), L.length+""], ["TP / SL", tp+" / "+sl], [Lg("open / expired","مفتوحة / انتهت"), op+""]];
    if (L.length && L.length < 30) rows.push([Lg("n < 30: not evidence","أقل من 30: مش دليل"), ""]);
    if (this.kzsTbl !== false){ c.font = "10px sans-serif"; const bw = 168, bh = rows.length*14 + 6, bx = 40, by = PB - bh - 22;   // x 40 = right of the drawing toolbar
    { c.save(); c.fillStyle = "rgba(27,31,43,.92)"; c.fillRect(bx + bw - 15, by - 16, 16, 15); c.fillStyle = "#f6465d"; c.textAlign = "center"; c.textBaseline = "middle"; c.fillText("✕", bx + bw - 7, by - 8.5); c.restore(); this._kzsX = {x:bx + bw - 15, y:by - 16, w:16, h:15}; c.textAlign = "left"; }   // ✕ = hide this table
    c.globalAlpha = .85; c.fillStyle = TH.pane; c.fillRect(bx, by, bw, bh); c.globalAlpha = 1; c.strokeStyle = gold; c.strokeRect(bx+.5, by+.5, bw, bh);
    rows.forEach(([a, b], i) => { c.fillStyle = i ? TH.mut : gold; c.font = i ? "10px sans-serif" : "bold 10px sans-serif"; c.fillText(a, bx+6, by+10+i*14); c.textAlign = "right"; c.fillStyle = i ? TH.txt : gold; c.fillText(b, bx+bw-6, by+10+i*14); c.textAlign = "left"; }); }
    c.restore(); c.globalAlpha = 1; c.textBaseline = "middle"; c.font = "11px ui-monospace,Menlo,Consolas,monospace";
  },
  paintEW(c, py, ew, dec){   // Elliott signal: yellow box + wave polyline, same visual treatment as the session / kill-zone boxes
    if (!ew || !ew.pts || ew.pts.length < 2 || !this.data.length) return;
    const pts = ew.pts.map(([t,p]) => [this.tx(t), py(p), p]), n = this.data.length, xe = this.x(n-1) + this.bw/2, PR = this.PR, PB = this.PB;
    const ys = pts.map(q => q[1]), top = Math.min(...ys), bot = Math.max(...ys), x0 = pts[0][0] - this.bw/2, col = "#f0b90b";
    c.save(); c.beginPath(); c.rect(0,0,PR,PB); c.clip();
    c.globalAlpha = .12; c.fillStyle = col; c.fillRect(x0, top, xe-x0, bot-top);
    c.globalAlpha = .8; c.strokeStyle = col; c.lineWidth = 1.2; c.setLineDash([5,3]); c.strokeRect(Math.round(x0)+.5, Math.round(top)+.5, xe-x0, bot-top); c.setLineDash([]);
    c.lineWidth = 1.8; c.globalAlpha = 1; c.beginPath(); pts.forEach((q,i) => i ? c.lineTo(q[0],q[1]) : c.moveTo(q[0],q[1])); c.stroke();
    const labs = ew.kind === "ew5" ? ["0","1","2","3","4"] : ["0","1","2"];
    c.font = "bold 10px sans-serif"; c.textAlign = "center"; c.textBaseline = "middle";
    pts.forEach((q,i) => { c.fillStyle = col; c.beginPath(); c.arc(q[0],q[1],3,0,6.3); c.fill(); const above = i === 0 ? pts[1][1] > q[1] : pts[i-1][1] > q[1];
      c.fillStyle = col; c.fillText(labs[i] || "", q[0], q[1] + (above ? 10 : -10)); });
    [[ew.tgt, "Target", "#0ecb81"], [ew.inv, "Invalid", "#f6465d"]].forEach(([v, lab, lc]) => { if (!v) return; const y = py(v); if (y < 0 || y > PB) return;
      c.globalAlpha = .8; c.strokeStyle = lc; c.setLineDash([3,3]); c.beginPath(); c.moveTo(xe, y); c.lineTo(PR, y); c.stroke(); c.setLineDash([]); c.fillStyle = lc; c.textAlign = "right"; c.fillText(lab+" "+v.toFixed(dec), PR-3, y-7); });
    c.globalAlpha = 1; c.fillStyle = col; c.textAlign = "left"; c.fillText("Elliott · "+(ew.kind === "ew5" ? "Wave 5 start" : "Wave 3 start"), Math.max(2, x0+3), top-8);
    c.restore(); c.font = "11px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "left";
  },
  planSpan(){   // limited-length trade plan: starts at the bar where it was loaded, runs planLen bars (drag the handle to stretch it)
    const ov = this.overlay, d = this.data, n = d.length; if (ov && ov.t0 == null && n) ov.t0 = d[n-1].t;
    let i0 = n-1; if (ov && ov.t0 != null) while (i0 > 0 && d[i0].t > ov.t0) i0--;
    const x0 = Math.max(0, this.x(i0)), x1 = Math.max(x0 + 30, Math.min(this.PR, this.x(i0 + this.planLen)));
    return {x0, x1};
  },
  /* a plan is drawn in full only after price has touched its entry (since the setup was loaded); before that it is a small
     waiting label, so far-away setups do not clutter the chart */
  paintPending(c, py, pl, dec){
    const long_ = pl.tps && pl.tps[0] > pl.entry, yE = py(pl.entry), tp = pl.tps && pl.tps.length ? pl.tps[pl.tps.length-1] : pl.entry;
    const rr = Math.abs(tp-pl.entry)/(Math.abs(pl.entry-pl.stop) || 1), txt = "\u23F3 "+(long_ ? "Long" : "Short")+" @ "+pl.entry.toFixed(dec)+"  SL "+pl.stop.toFixed(dec)+"  TP "+tp.toFixed(dec)+"  R:R "+rr.toFixed(1)+"  waiting";
    c.save(); c.beginPath(); c.rect(0,0,this.PR,this.PB); c.clip();
    c.strokeStyle = "rgba(74,163,255,.7)"; c.setLineDash([5,4]); c.beginPath(); c.moveTo(0, yE); c.lineTo(this.PR, yE); c.stroke(); c.setLineDash([]);
    c.font = "11px sans-serif"; const bw = c.measureText(txt).width + 14, bx = Math.max(4, Math.min(this.PR - bw - 4, this.x(this.data.length-1) - bw / 2)), by = yE - 24;
    c.fillStyle = "rgba(0,0,0,.65)"; c.fillRect(bx, by, bw, 18); c.fillStyle = "#4aa3ff"; c.textAlign = "left"; c.fillText(txt, bx + 7, by + 13);
    c.restore();
  },
  paintJournal(c, py, dec){
    const d = this.data, tr = this.jtr; if (!tr || !tr.length || !d || !d.length) return;
    const last = d[d.length-1].t;
    c.save(); c.beginPath(); c.rect(0,0,this.PR,this.PB); c.clip();
    for (const t of tr){
      const x0 = this.tx(t.t0), x1 = this.tx(t.t1 || last);
      if (!(x1 >= 0) || x0 > this.PR) continue;
      const closed = t.status !== "open", long_ = t.dir === "bullish", w = Math.max(3, x1 - x0);
      const yE = py(t.entry), yS = py(t.sl), yT = py(t.tp1);
      c.globalAlpha = closed ? .28 : 1;
      c.fillStyle = "rgba(14,203,129,.16)"; c.fillRect(x0, Math.min(yE,yT), w, Math.abs(yE-yT));
      c.fillStyle = "rgba(246,70,93,.16)"; c.fillRect(x0, Math.min(yE,yS), w, Math.abs(yE-yS));
      c.lineWidth = 1;
      c.strokeStyle = "#4aa3ff"; c.beginPath(); c.moveTo(x0, yE); c.lineTo(x1, yE); c.stroke();
      c.strokeStyle = "#f6465d"; c.beginPath(); c.moveTo(x0, yS); c.lineTo(x1, yS); c.stroke();
      c.strokeStyle = "#0ecb81"; c.beginPath(); c.moveTo(x0, yT); c.lineTo(x1, yT); c.stroke();
      const lab = t.status === "tp" ? "TP ✓ "+(+t.r).toFixed(2)+"R" : t.status === "sl" ? "SL ✗ "+(+t.r).toFixed(2)+"R" : t.status === "nf" ? "no fill" : t.status === "exp" ? "expired" : "open";
      c.font = "10px sans-serif"; c.textAlign = "left"; c.fillStyle = closed ? "#848e9c" : (long_ ? "#0ecb81" : "#f6465d");
      c.fillText((long_ ? "Long" : "Short")+" · "+lab, Math.max(x0, 0) + 4, yE - 6);
      c.globalAlpha = 1;
    }
    c.restore();
  },
  paintSetupBox(c, py, pl, dec){
    const ov0 = this.overlay, t00 = ov0 && ov0.t0 != null ? ov0.t0 : -Infinity;
    if (!this.data.some(b => b.t >= t00 && b.l <= pl.entry && b.h >= pl.entry)) return this.paintPending(c, py, pl, dec);
    const n = this.data.length, sp = this.planSpan(), x0 = sp.x0, x1 = sp.x1, w = Math.max(30, x1 - x0), long_ = pl.tps && pl.tps[0] > pl.entry;
    const tp = pl.tps && pl.tps.length ? pl.tps[pl.tps.length-1] : pl.entry, yE = py(pl.entry), yS = py(pl.stop), yT = py(tp);
    c.save(); c.beginPath(); c.rect(0,0,this.PR,this.PB); c.clip();
    c.fillStyle = "rgba(14,203,129,.16)"; c.fillRect(x0, Math.min(yE,yT), w, Math.abs(yE-yT));
    c.fillStyle = "rgba(246,70,93,.16)"; c.fillRect(x0, Math.min(yE,yS), w, Math.abs(yE-yS));
    c.strokeStyle = "#4aa3ff"; c.beginPath(); c.moveTo(x0, yE); c.lineTo(x1, yE); c.stroke();
    (pl.tps||[]).forEach((v,i) => { const y = py(v); c.strokeStyle = "rgba(14,203,129,.8)"; c.setLineDash([4,3]); c.beginPath(); c.moveTo(x0,y); c.lineTo(x1,y); c.stroke(); c.setLineDash([]); c.fillStyle = "#0ecb81"; c.textAlign = "left"; c.fillText("TP"+(i+1)+" "+v.toFixed(dec), x0+4, y + (long_ ? 8 : -8)); });
    c.strokeStyle = "rgba(246,70,93,.9)"; c.beginPath(); c.moveTo(x0,yS); c.lineTo(x1,yS); c.stroke();
    c.fillStyle = "#f6465d"; c.fillText("SL "+pl.stop.toFixed(dec), x0+4, yS + (long_ ? 8 : -8));
    const rr = Math.abs(tp-pl.entry)/(Math.abs(pl.entry-pl.stop) || 1); c.fillStyle = "#4aa3ff"; c.fillText((long_ ? "Long" : "Short")+"  R:R "+rr.toFixed(1)+"  entry "+pl.entry.toFixed(dec), x0+4, yE - 7);
    c.restore();
    [[pl.entry,"Entry","#4aa3ff"],[pl.stop,"SL","#f6465d"]].concat((pl.tps||[]).map((v,i) => [v,"TP"+(i+1),"#0ecb81"])).forEach(([v,lab,col]) => { const y = py(v); if (y<0||y>this.PB) return; c.fillStyle = col; c.fillRect((this.W-this.axw)+1, y-7, this.axw-2, 14); c.fillStyle = "#000"; c.textAlign = "left"; c.fillText(lab+" "+v.toFixed(dec), (this.W-this.axw)+3, y); });
  },
  rayEnd(x0,y0,x1,y1){   // where a ray from (x0,y0) through (x1,y1) leaves the plot area
    const dx = x1-x0, dy = y1-y0; let s = Infinity;
    [[dx>0,(this.PR-x0)/dx],[dx<0,(0-x0)/dx],[dy>0,(this.PB-y0)/dy],[dy<0,(0-y0)/dy]].forEach(([ok,v]) => { if (ok && v > 0) s = Math.min(s, v); });
    if (!isFinite(s)) s = 1; return {x:x0+s*dx, y:y0+s*dy};
  },
  dbar(){   // TradingView-style bar above the selected drawing: colour, width, dash, lock, copy, front, delete
    if (!this.host) return; let bar = this.host.querySelector(".dbar");
    const d = this.sel && !this.creating && this.draws.includes(this.sel) ? this.sel : null;
    if (this.editor && this.editor.d !== d){ this.closeEditor(); }
    if (!d){ if (bar) bar.remove(); return; }
    if (!bar){ if (getComputedStyle(this.host).position === "static") this.host.style.position = "relative"; bar = document.createElement("div"); bar.className = "dbar"; this.host.append(bar); this.dbarBuild(bar); }
    const hs = this.handles(d), x = Math.max(4, Math.min(this.PR - 300, Math.min(...hs.map(h => h.x)))), y = Math.max(4, Math.min(...hs.map(h => h.y)) - 34);
    bar.style.left = x+"px"; bar.style.top = y+"px"; bar.style.display = "flex";
    bar.querySelectorAll("[data-col]").forEach(b => b.classList.toggle("on", b.dataset.col === (d.color || "")));
    bar.querySelectorAll("[data-w]").forEach(b => b.classList.toggle("on", +b.dataset.w === (d.w || 1.5)));
    bar.querySelector("[data-dash]").classList.toggle("on", d.ls ? d.ls !== "solid" : !!d.dash); bar.querySelector("[data-lock]").classList.toggle("on", !!d.lock);
  },
  dashOf(d){ return d.ls === "dot" ? [1.5, 3.5] : (d.ls === "dash" || (d.ls == null && d.dash)) ? [5, 4] : []; },   // line style: solid / dashed / dotted (old drawings only had dash on / off)
  fillOf(d, base, hexA, fallback){   // fill of a box-like drawing: the chosen fill colour + opacity, else the line colour at its usual tint
    if (d.fill){ const n = parseInt(d.fill.slice(1), 16), a = d.fo != null ? d.fo : (parseInt(hexA, 16) / 255 || .15); return "rgba("+((n >> 16) & 255)+","+((n >> 8) & 255)+","+(n & 255)+","+a+")"; }
    return d.color ? base + hexA : fallback; },
  closeEditor(){
    const ed = this.editor; if (!ed) return; this.editor = null; ed.box.remove();
    if (ed.d.type === "text" && !String(ed.d.txt || "").trim()){ this.draws = this.draws.filter(x => x !== ed.d); if (this.sel === ed.d) this.sel = null; }   // an empty note is not kept
    this.saveDraws(); this.draw();
  },
  openEditor(d){   // TradingView-style settings of one drawing, inside the chart (browser dialogs are blocked inside the page frame, so the old text box never opened)
    if (!this.host || !d) return; this.closeEditor();
    if (getComputedStyle(this.host).position === "static") this.host.style.position = "relative";
    const box = el("div", "dprop"), set = fn => { fn(d); this.saveDraws(); this.draw(); };
    this.editor = {d, box};
    const NAMES = {trend:Lg("Trend line","خط اتجاه"), hline:Lg("Horizontal line","خط أفقي"), vline:Lg("Vertical line","خط رأسي"), ray:Lg("Ray","شعاع"), arrow:Lg("Arrow","سهم"), rect:Lg("Rectangle","مستطيل"),
      channel:Lg("Channel","قناة"), text:Lg("Text note","ملاحظة نصية"), fib:Lg("Fibonacci","فيبوناتشي"), wave:Lg("Elliott wave","موجات إليوت"), measure:Lg("Measure","قياس"), prange:Lg("Price range","مدى سعر"),
      drange:Lg("Date range","مدى زمن"), brush:Lg("Brush","فرشاة"), ellipse:Lg("Ellipse","قطع ناقص"), triangle:Lg("Triangle","مثلث"), pitchfork:Lg("Andrews pitchfork","شوكة أندروز"), callout:Lg("Callout","تعليق"), plabel:Lg("Price label","علامة سعر"), arrup:Lg("Arrow up","سهم لأعلى"), arrdn:Lg("Arrow down","سهم لأسفل"), flag:Lg("Flag","علم"), cross:Lg("Cross line","خط متقاطع"), long:Lg("Long position","صفقة شراء"), short:Lg("Short position","صفقة بيع")};
    const head = el("div", "dph"); head.append(el("b", null, NAMES[d.type] || d.type)); const xb = el("button", null, "✕"); xb.title = Lg("close","إغلاق"); xb.onclick = () => this.closeEditor(); head.append(xb); box.append(head);
    const row = (label, ...kids) => { const r = el("div", "dpr"); r.append(el("span", null, label)); kids.forEach(k => r.append(k)); box.append(r); return r; };
    const color = (get, put, def) => { const ci = el("input"); ci.type = "color"; ci.value = get() || def; ci.oninput = () => set(() => put(ci.value)); return ci; };
    const PAL = ["#f0b90b", "#0ecb81", "#f6465d", "#4aa3ff", "#b57cff", "#ff9800", "#26c6da", "#eaecef", "#8a94a3"];
    if (d.type === "text" || d.type === "callout"){
      const ta = el("textarea"); ta.value = d.txt || ""; ta.placeholder = Lg("type your note here","اكتب ملاحظتك هنا"); ta.oninput = () => set(() => { d.txt = ta.value; });
      ta.onkeydown = e => { e.stopPropagation(); if (e.key === "Escape"){ this.closeEditor(); } };
      const wrap = el("div", "dpr"); wrap.style.display = "block"; wrap.append(ta); box.append(wrap); this.editor.ta = ta;
      const fs = el("select"); [10, 11, 12, 14, 16, 20, 26, 34].forEach(n => { const o = el("option", null, String(n)); o.value = n; fs.append(o); }); fs.value = String(d.fs || 11); fs.onchange = () => set(() => { d.fs = +fs.value; });
      row(Lg("Size","الحجم"), fs);
      row(Lg("Text colour","لون النص"), color(() => d.tc, v => { d.tc = v; }, "#eaecef"));
      const bg = el("input"); bg.type = "checkbox"; bg.checked = d.tb !== "none"; bg.onchange = () => set(() => { d.tb = bg.checked ? undefined : "none"; if (bg.checked) delete d.tb; });
      row(Lg("Background","الخلفية"), bg, color(() => (d.tb && d.tb !== "none" ? d.tb : ""), v => { d.tb = v; bg.checked = true; }, "#2b3139"));
      if (d.type === "callout") row(Lg("Line","الخط"), color(() => d.color, v => { d.color = v; }, "#f0b90b"));
    } else if (d.type !== "long" && d.type !== "short"){
      const pal = el("div"); pal.style.cssText = "display:flex;gap:4px;align-items:center;flex-wrap:wrap";
      PAL.forEach(c0 => { const b = el("button", "sw"); b.style.background = c0; b.title = c0; b.onclick = () => { set(() => { d.color = c0; }); ci.value = c0; pal.querySelectorAll(".sw").forEach(x => x.classList.toggle("on", x === b)); }; if (d.color === c0) b.classList.add("on"); pal.append(b); });
      const ci = color(() => d.color, v => { d.color = v; }, "#4aa3ff"); pal.append(ci); row(Lg("Line","الخط"), pal);
      const wsel = el("select"); [1, 1.5, 2, 3, 4, 5, 6].forEach(n => { const o = el("option", null, String(n)); o.value = n; wsel.append(o); }); wsel.value = String(d.w || 1.5);
      if (![...wsel.options].some(o => o.value === wsel.value)) wsel.value = "1.5"; wsel.onchange = () => set(() => { d.w = +wsel.value; });
      const seg = el("div", "seg"); [["solid", "──"], ["dash", "╌╌"], ["dot", "···"]].forEach(([k, ic]) => { const b = el("button", null, ic); b.title = k; const cur = d.ls || (d.dash ? "dash" : "solid");
        if (cur === k) b.classList.add("on"); b.onclick = () => { set(() => { d.ls = k; d.dash = k === "dash"; }); seg.querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b)); }; seg.append(b); });
      row(Lg("Width","السُمك"), wsel, seg);
      if (["rect", "channel", "prange", "drange", "ellipse", "triangle"].includes(d.type)){
        const op = el("input"); op.type = "range"; op.min = 0; op.max = 100; op.value = Math.round((d.fo != null ? d.fo : .15) * 100); op.oninput = () => set(() => { d.fo = op.value / 100; if (!d.fill) d.fill = d.color || ({rect:"#4aa3ff", channel:"#b57cff"}[d.type] || "#4aa3ff"); });
        row(Lg("Fill","التعبئة"), color(() => d.fill || d.color, v => { d.fill = v; if (d.fo == null) d.fo = .18; }, "#4aa3ff"), op);
      }
      if (d.type === "trend"){
        const l = el("input"); l.type = "checkbox"; l.checked = !!d.extL; l.onchange = () => set(() => { d.extL = l.checked; });
        const r = el("input"); r.type = "checkbox"; r.checked = !!d.extR; r.onchange = () => set(() => { d.extR = r.checked; });
        const ex = el("div"); ex.style.cssText = "display:flex;gap:4px;align-items:center;white-space:nowrap"; ex.append(l, el("span", null, Lg("left","يسار")), r, el("span", null, Lg("right","يمين")));
        ex.querySelectorAll("span").forEach(z => { z.style.minWidth = "0"; z.style.margin = "0 6px 0 0"; });
        row(Lg("Extend","تمديد"), ex);
      }
      if (["trend", "measure", "prange", "drange", "hline", "wave", "fib"].includes(d.type)){
        const lb = el("input"); lb.type = "checkbox"; lb.checked = !d.noLbl; lb.onchange = () => set(() => { d.noLbl = !lb.checked; });
        row(Lg("Labels","الأرقام"), lb);
      }
    } else {
      row("", el("span", null, Lg("Move the three handles to change entry, stop and target.","حرّك المقابض التلاتة لتغيير الدخول والوقف والهدف.")));
    }
    const foot = el("div", "dpf");
    const dup = el("button", null, Lg("Duplicate","نسخة")); dup.onclick = () => { const n = JSON.parse(JSON.stringify(d)), sh = this.secMs() * 3; n.id = Date.now() + Math.random(); (n.pts || []).forEach(q => { q.t += sh; }); if (n.t0 != null){ n.t0 += sh; n.t1 += sh; } this.draws.push(n); this.sel = n; this.closeEditor(); };
    const del = el("button", "bad", Lg("Delete","حذف")); del.onclick = () => { this.draws = this.draws.filter(x => x !== d); this.sel = null; this.editor = null; box.remove(); this.saveDraws(); this.draw(); };
    const ok = el("button", null, Lg("Done","تم")); ok.onclick = () => this.closeEditor(); foot.append(dup, del, ok); box.append(foot);
    box.addEventListener("pointerdown", e => e.stopPropagation());
    this.host.append(box);
    const hs = this.handles(d), xs = hs.map(h => h.x), ys = hs.map(h => h.y);
    const bw = 262, left = Math.max(4, Math.min(this.PR - bw - 4, Math.min(...xs))), top0 = Math.max(4, Math.min(...ys) + 34);
    box.style.left = left + "px"; box.style.top = Math.min(top0, Math.max(4, this.PB - box.offsetHeight - 4)) + "px";
    if ((d.type === "text" || d.type === "callout") && this.editor.ta) setTimeout(() => { try { this.editor.ta.focus(); this.editor.ta.select(); } catch(e){} }, 0);
  },
  dbarBuild(bar){
    const set = fn => { const d = this.sel; if (!d) return; fn(d); this.saveDraws(); this.draw(); };
    const add = (html, attrs, on) => { const b = document.createElement("button"); b.innerHTML = html; Object.entries(attrs).forEach(([k,v]) => b.setAttribute(k, v)); b.onpointerdown = e => { e.stopPropagation(); e.preventDefault(); on(); }; bar.append(b); };
    ["", "#f0b90b", "#0ecb81", "#f6465d", "#4aa3ff", "#b57cff", "#eaecef"].forEach(col => add('<i style="background:'+(col || "#8a94a3")+'"></i>', {"data-col":col, title:Lg("colour","لون")}, () => set(d => { if (col) d.color = col; else delete d.color; })));
    [1, 2, 3].forEach(w => add(String(w), {"data-w":w, title:Lg("width","سُمك")}, () => set(d => { d.w = w; })));
    add("⋯", {"data-dash":1, title:Lg("dashed","متقطع")}, () => set(d => { d.dash = !(d.ls ? d.ls === "dash" : d.dash); d.ls = d.dash ? "dash" : "solid"; }));
    add(Lg("Lock","قفل"), {"data-lock":1, title:Lg("lock: cannot be moved","قفل: ماينفعش يتحرك")}, () => set(d => { d.lock = !d.lock; }));
    add(Lg("Hide","إخفاء"), {"data-hide":1, title:Lg("hide (show again from the list: not yet)","إخفاء")}, () => set(d => { d.hidden = !d.hidden; this.sel = null; }));
    add("⚙", {title:Lg("settings: colour, line, fill, text","إعدادات: اللون والخط والتعبئة والنص")}, () => { const d = this.sel; if (d) this.openEditor(d); });
    add(Lg("Copy","نسخ"), {title:Lg("copy","نسخة")}, () => { const d = this.sel; if (!d) return; const n = JSON.parse(JSON.stringify(d)), sh = this.secMs()*3; n.id = Date.now() + Math.random();
      (n.pts || []).forEach(q => { q.t += sh; }); if (n.t0 != null){ n.t0 += sh; n.t1 += sh; } this.draws.push(n); this.sel = n; this.saveDraws(); this.draw(); });
    add(Lg("Front","للأمام"), {title:Lg("bring to front","للأمام")}, () => { const d = this.sel; if (!d) return; this.draws = this.draws.filter(x => x !== d).concat([d]); this.saveDraws(); this.draw(); });
    add(Lg("Delete","حذف"), {title:Lg("delete","حذف")}, () => { const d = this.sel; if (!d) return; this.draws = this.draws.filter(x => x !== d); this.sel = null; this.saveDraws(); this.draw(); });
  },
  paintSR(c, py, PB, dec){   // daily (dashed) / weekly (solid, thicker) support & resistance lines + a small tag at the right edge; only when the S/R button is on for this chart
    const o = this.srData; if (!this.srOn || !o) return; c.save(); c.font = "10px ui-monospace,Menlo,Consolas,monospace"; c.textAlign = "right"; c.textBaseline = "middle";
    [["W", o.W, 1.8, []], ["D", o.D, 1.1, [5, 4]]].forEach(([tf, lv, lw, dash]) => { if (tf === "D" && this.tf === "1W") return; (lv || []).slice(0, 8).forEach(l => { const y = Math.round(py(l.p)) + .5; if (y < 2 || y > PB - 2) return;
      const col = l.kind === "R" ? "#f6465d" : "#0ecb81"; c.globalAlpha = .35 + .13*l.strength; c.strokeStyle = col; c.lineWidth = lw; c.setLineDash(dash); c.beginPath(); c.moveTo(0, y); c.lineTo(this.PR, y); c.stroke(); c.setLineDash([]); c.globalAlpha = .95;
      const t = tf+" "+l.kind+" "+l.p.toFixed(dec)+" ×"+l.touches; c.fillStyle = "rgba(11,14,17,.7)"; const w = c.measureText(t).width + 6; c.fillRect(this.PR - w - 2, y - 7, w, 13); c.fillStyle = col; c.fillText(t, this.PR - 5, y); }); });
    c.restore(); },
  paintDraws(c, py, dec){
    if (!this.data.length || !this.drawingsVisible) return;
    c.save(); c.beginPath(); c.rect(0,0,this.PR,this.PB); c.clip(); c.lineWidth = 1.5; c.textBaseline = "middle";
    const DDOT = !!this.dots, dsd = Math.max(5, Math.min(7, Math.round(this.bw*0.25)+2)), sld0 = DDOT ? c.setLineDash : null;
    if (DDOT){ c.lineCap = "round"; c.setLineDash = () => sld0.call(c, [0.1, dsd]); }   // dot theme: every drawing stroke (solid or dashed) becomes a row of round dots
    const lab0 = (txt, x, y, col, bg) => { c.font = "10px sans-serif"; const w = c.measureText(txt).width + 6; c.fillStyle = bg || "rgba(11,14,17,.75)"; c.fillRect(x, y-7, w, 14); c.fillStyle = col; c.textAlign = "left"; c.fillText(txt, x+3, y); };
    this.draws.forEach(d => {
      if (d.hidden) return;   // hidden from the options bar: not drawn, not selectable
      const lab = d.noLbl && d.type !== "text" ? () => {} : lab0;
      const hs = this.handles(d), sel = d === this.sel;
      if (d.type === "brush"){
        c.strokeStyle = d.color || "#4aa3ff"; c.lineWidth = d.w || 2; c.lineJoin = "round"; c.lineCap = "round"; c.setLineDash(this.dashOf(d)); c.beginPath();
        d.pts.forEach((q,i) => { const x = this.tx(q.t), y = this.yp(q.p); i ? c.lineTo(x,y) : c.moveTo(x,y); }); c.stroke(); c.setLineDash([]);
      } else if (d.type === "prange"){
        const y1 = Math.min(hs[0].y, hs[1].y), y2 = Math.max(hs[0].y, hs[1].y), col = d.color || "#4aa3ff", p0 = d.pts[0].p, p1 = d.pts[1].p;
        c.fillStyle = this.fillOf(d, col, "1f", col+"1f"); c.fillRect(0, y1, this.PR, y2-y1); c.strokeStyle = col; c.lineWidth = d.w || 1; c.setLineDash(this.dashOf(d)); c.beginPath(); c.moveTo(0,y1+.5); c.lineTo(this.PR,y1+.5); c.moveTo(0,y2+.5); c.lineTo(this.PR,y2+.5); c.stroke(); c.setLineDash([]);
        const df = p1 - p0; lab((df>=0?"+":"")+df.toFixed(dec)+" ("+(df/p0*100).toFixed(2)+"%)", 6, (y1+y2)/2, col);
      } else if (d.type === "drange"){
        const x1 = Math.min(hs[0].x, hs[1].x), x2 = Math.max(hs[0].x, hs[1].x), col = d.color || "#4aa3ff", bars = Math.round(Math.abs(d.pts[1].t - d.pts[0].t)/this.secMs());
        c.fillStyle = this.fillOf(d, col, "1f", col+"1f"); c.fillRect(x1, 0, x2-x1, this.PB); c.strokeStyle = col; c.lineWidth = d.w || 1; c.setLineDash(this.dashOf(d)); c.beginPath(); c.moveTo(x1+.5,0); c.lineTo(x1+.5,this.PB); c.moveTo(x2+.5,0); c.lineTo(x2+.5,this.PB); c.stroke(); c.setLineDash([]);
        lab(bars+" "+Lg("bars","شمعة"), x1+4, 12, col);
      } else if (d.type === "hline"){
        const y = hs[0].y; c.strokeStyle = d.color || "#f0b90b"; c.lineWidth = d.w || 1.5; c.setLineDash(this.dashOf(d)); c.beginPath(); c.moveTo(0,y); c.lineTo(this.PR,y); c.stroke(); lab(d.pts[0].p.toFixed(dec), 4, y-9, "#f0b90b");
      } else if (d.type === "vline"){
        const x = hs[0].x; c.strokeStyle = d.color || "#eaecef"; c.lineWidth = d.w || 1.2; c.setLineDash(this.dashOf(d)); c.beginPath(); c.moveTo(x,0); c.lineTo(x,this.PB); c.stroke(); c.setLineDash([]);
      } else if (d.type === "ray" || d.type === "arrow"){
        const x0 = hs[0].x, y0 = hs[0].y, x1 = hs[1].x, y1 = hs[1].y, col = d.color || (d.type === "arrow" ? "#f0b90b" : "#4aa3ff"), dash = this.dashOf(d);
        const e = d.type === "ray" ? this.rayEnd(x0,y0,x1,y1) : {x:x1, y:y1};
        c.strokeStyle = col; c.lineWidth = d.w || 1.5; c.setLineDash(dash); c.beginPath(); c.moveTo(x0,y0); c.lineTo(e.x,e.y); c.stroke(); c.setLineDash([]);
        if (d.type === "arrow"){ const a = Math.atan2(y1-y0, x1-x0), L = 10; c.beginPath(); c.moveTo(x1,y1); c.lineTo(x1 - L*Math.cos(a-.4), y1 - L*Math.sin(a-.4)); c.moveTo(x1,y1); c.lineTo(x1 - L*Math.cos(a+.4), y1 - L*Math.sin(a+.4)); c.stroke(); }
      } else if (d.type === "measure"){
        const col = d.color || "#4aa3ff", p0 = d.pts[0], p1 = d.pts[1]; c.strokeStyle = col; c.lineWidth = d.w || 1.5; c.setLineDash([4,3]); c.beginPath(); c.moveTo(hs[0].x,hs[0].y); c.lineTo(hs[1].x,hs[1].y); c.stroke(); c.setLineDash([]);
        const df = p1.p - p0.p, bars = Math.round((p1.t - p0.t)/this.secMs()); lab((df>=0?"+":"")+df.toFixed(dec)+" ("+(df/p0.p*100).toFixed(2)+"%) · "+bars+" "+Lg("bars","شمعة"), (hs[0].x+hs[1].x)/2, (hs[0].y+hs[1].y)/2-10, col);
      } else if (d.type === "rect"){
        const x1 = Math.min(hs[0].x,hs[1].x), y1 = Math.min(hs[0].y,hs[1].y), w = Math.abs(hs[0].x-hs[1].x), h = Math.abs(hs[0].y-hs[1].y);
        const rc = d.color || "#4aa3ff"; c.fillStyle = this.fillOf(d, rc, "24", "rgba(74,163,255,.14)"); c.fillRect(x1,y1,w,h); c.strokeStyle = rc; c.lineWidth = d.w || 1.2; c.setLineDash(this.dashOf(d)); c.strokeRect(x1,y1,w,h); c.setLineDash([]);
      } else if (d.type === "channel"){
        const o = d.pts.length > 2 ? this.chanOff(d) : 0, ya = this.yp(d.pts[0].p+o), yb = this.yp(d.pts[1].p+o);
        const cc = d.color || "#b57cff"; c.fillStyle = this.fillOf(d, cc, "1f", "rgba(181,124,255,.12)"); c.beginPath(); c.moveTo(hs[0].x,hs[0].y); c.lineTo(hs[1].x,hs[1].y); c.lineTo(hs[1].x,yb); c.lineTo(hs[0].x,ya); c.closePath(); c.fill();
        c.strokeStyle = cc; c.lineWidth = d.w || 1.5; c.setLineDash(this.dashOf(d)); c.beginPath(); c.moveTo(hs[0].x,hs[0].y); c.lineTo(hs[1].x,hs[1].y); c.moveTo(hs[0].x,ya); c.lineTo(hs[1].x,yb); c.stroke();
        c.setLineDash([4,4]); c.lineWidth = 1; c.beginPath(); c.moveTo(hs[0].x,(hs[0].y+ya)/2); c.lineTo(hs[1].x,(hs[1].y+yb)/2); c.stroke(); c.setLineDash([]);
      } else if (d.type === "text"){
        const fs = d.fs || 11, lines = String(d.txt || (this.editor && this.editor.d === d ? " " : "Note")).split("\n"); c.font = fs+"px sans-serif"; c.textAlign = "left";
        const tw = Math.max(...lines.map(z => c.measureText(z).width)) + 10, th = lines.length*(fs+3) + 6, x0 = hs[0].x, y0 = hs[0].y - th/2; d._w = tw; d._h = th;
        if (d.tb !== "none"){ c.fillStyle = d.tb || "rgba(43,49,57,.9)"; c.fillRect(x0, y0, tw, th); }
        c.fillStyle = d.tc || "#eaecef"; lines.forEach((z, i) => c.fillText(z, x0 + 5, y0 + 3 + (fs+3)*i + (fs+3)/2));
      } else if (d.type === "trend"){
        c.strokeStyle = d.color || "#4aa3ff"; c.lineWidth = d.w || 1.5; c.setLineDash(this.dashOf(d)); c.beginPath();
        const ea = d.extL ? this.rayEnd(hs[1].x,hs[1].y,hs[0].x,hs[0].y) : hs[0], eb = d.extR ? this.rayEnd(hs[0].x,hs[0].y,hs[1].x,hs[1].y) : hs[1];
        c.moveTo(ea.x,ea.y); c.lineTo(eb.x,eb.y); c.stroke(); c.setLineDash([]);
        const dp = d.pts[1].p-d.pts[0].p, mx_ = (hs[0].x+hs[1].x)/2, my_ = (hs[0].y+hs[1].y)/2-10;
        if (d.info){ const bars = Math.round((d.pts[1].t-d.pts[0].t)/this.secMs()), ang = Math.atan2(hs[0].y-hs[1].y, Math.abs(hs[1].x-hs[0].x) || 1)*180/Math.PI; lab((dp>=0?"+":"")+dp.toFixed(dec)+" ("+(dp/d.pts[0].p*100).toFixed(2)+"%) · "+bars+" "+Lg("bars","شمعة")+" · "+ang.toFixed(0)+"°", mx_, my_, d.color || "#4aa3ff"); }
        else lab((dp>=0?"+":"")+(dp/d.pts[0].p*100).toFixed(2)+"%", mx_, my_, "#4aa3ff");
      } else if (d.type === "cross"){
        c.strokeStyle = d.color || "#eaecef"; c.lineWidth = d.w || 1; c.setLineDash(this.dashOf(d)); c.beginPath(); c.moveTo(0,hs[0].y); c.lineTo(this.PR,hs[0].y); c.moveTo(hs[0].x,0); c.lineTo(hs[0].x,this.PB); c.stroke(); c.setLineDash([]);
      } else if (d.type === "ellipse"){
        const ec = d.color || "#26c6da"; c.beginPath(); c.ellipse((hs[0].x+hs[1].x)/2, (hs[0].y+hs[1].y)/2, Math.max(1, Math.abs(hs[0].x-hs[1].x)/2), Math.max(1, Math.abs(hs[0].y-hs[1].y)/2), 0, 0, 6.2832);
        c.fillStyle = this.fillOf(d, ec, "24", "rgba(38,198,218,.14)"); c.fill(); c.strokeStyle = ec; c.lineWidth = d.w || 1.2; c.setLineDash(this.dashOf(d)); c.stroke(); c.setLineDash([]);
      } else if (d.type === "triangle"){
        const tg = d.color || "#ff9800"; c.beginPath(); hs.forEach((h, i) => i ? c.lineTo(h.x,h.y) : c.moveTo(h.x,h.y)); c.closePath();
        c.fillStyle = this.fillOf(d, tg, "24", "rgba(255,152,0,.14)"); c.fill(); c.strokeStyle = tg; c.lineWidth = d.w || 1.2; c.setLineDash(this.dashOf(d)); c.stroke(); c.setLineDash([]);
      } else if (d.type === "pitchfork"){
        const pc = d.color || "#b57cff"; c.strokeStyle = pc; c.lineWidth = d.w || 1.3; c.setLineDash(this.dashOf(d)); c.beginPath();
        if (hs.length < 3){ c.moveTo(hs[0].x,hs[0].y); c.lineTo(hs[1].x,hs[1].y); } else this.pfLines(hs).forEach(l => { c.moveTo(l[0],l[1]); c.lineTo(l[2],l[3]); });
        c.stroke(); if (hs.length > 2){ c.setLineDash([4,3]); c.lineWidth = 1; c.beginPath(); c.moveTo(hs[1].x,hs[1].y); c.lineTo(hs[2].x,hs[2].y); c.stroke(); } c.setLineDash([]);
      } else if (d.type === "callout"){
        const fs = d.fs || 11, lines = String(d.txt || (this.editor && this.editor.d === d ? " " : "Note")).split("\n"), cc = d.color || "#f0b90b"; c.font = fs+"px sans-serif"; c.textAlign = "left";
        const tw = Math.max(...lines.map(z => c.measureText(z).width)) + 12, th = lines.length*(fs+3) + 8, x0 = hs[1].x, y0 = hs[1].y - th/2; d._w = tw; d._h = th;
        c.strokeStyle = cc; c.lineWidth = d.w || 1.2; c.beginPath(); c.moveTo(hs[0].x,hs[0].y); c.lineTo(hs[0].x < x0 + tw/2 ? x0 : x0 + tw, hs[1].y); c.stroke();
        c.fillStyle = cc; c.beginPath(); c.arc(hs[0].x,hs[0].y,3,0,6.3); c.fill();
        if (d.tb !== "none"){ c.fillStyle = d.tb || "rgba(43,49,57,.95)"; c.fillRect(x0, y0, tw, th); } c.strokeRect(x0, y0, tw, th);
        c.fillStyle = d.tc || "#eaecef"; lines.forEach((z, i) => c.fillText(z, x0 + 6, y0 + 4 + (fs+3)*i + (fs+3)/2));
      } else if (d.type === "plabel"){
        const txt = d.pts[0].p.toFixed(dec), pc = d.color || "#4aa3ff"; c.font = "11px sans-serif"; const tw = c.measureText(txt).width + 12; d._w = tw + 7; const x = hs[0].x, y = hs[0].y;
        c.fillStyle = pc; c.beginPath(); c.moveTo(x,y); c.lineTo(x+7,y-9); c.lineTo(x+7+tw,y-9); c.lineTo(x+7+tw,y+9); c.lineTo(x+7,y+9); c.closePath(); c.fill(); c.fillStyle = "#0b0e11"; c.textAlign = "left"; c.fillText(txt, x+13, y);
      } else if (d.type === "arrup" || d.type === "arrdn"){
        const up = d.type === "arrup", ac = d.color || (up ? "#0ecb81" : "#f6465d"), x = hs[0].x, y = hs[0].y, sg = up ? 1 : -1;
        c.fillStyle = ac; c.beginPath(); c.moveTo(x,y); c.lineTo(x-8,y+sg*10); c.lineTo(x-3,y+sg*10); c.lineTo(x-3,y+sg*22); c.lineTo(x+3,y+sg*22); c.lineTo(x+3,y+sg*10); c.lineTo(x+8,y+sg*10); c.closePath(); c.fill();
      } else if (d.type === "flag"){
        const fc = d.color || "#f0b90b", x = hs[0].x, y = hs[0].y; c.strokeStyle = fc; c.lineWidth = d.w || 1.5; c.beginPath(); c.moveTo(x,y); c.lineTo(x,y-26); c.stroke();
        c.fillStyle = fc; c.beginPath(); c.moveTo(x,y-26); c.lineTo(x+16,y-21); c.lineTo(x,y-15); c.closePath(); c.fill();
      } else if (d.type === "wave"){
        const wc = d.color || "#f0b90b"; c.strokeStyle = wc; c.lineWidth = d.w || 1.5; c.setLineDash(this.dashOf(d)); c.beginPath(); hs.forEach((h,i) => i ? c.lineTo(h.x,h.y) : c.moveTo(h.x,h.y)); c.stroke(); c.setLineDash([]);
        hs.forEach((h,i) => { const up = i === 0 ? (hs[1] ? hs[1].y > h.y : true) : (hs[i-1].y > h.y); const lo = i % 2 === 0;
          c.fillStyle = wc; c.beginPath(); c.arc(h.x,h.y,3,0,6.3); c.fill(); lab(String(i), h.x-4, h.y + (up ? 10 : -10), wc); });
      } else if (d.type === "fib"){
        const a = d.pts[0], b = d.pts[1], xs = Math.min(hs[0].x, hs[1].x), cols = ["#848e9c","#f6465d","#ff9800","#0ecb81","#26c6da","#4aa3ff","#a855f7","#f0b90b"];
        (d.lv || FIB_PRESETS.Retracement).forEach((L,i) => {
          const pr = b.p - (b.p-a.p)*L, y = this.yp(pr); const col = d.color || (L < 0 ? "#0ecb81" : L > 1 ? "#f6465d" : cols[i % cols.length]); c.strokeStyle = col; c.lineWidth = d.w || 1; c.beginPath(); c.moveTo(xs,y); c.lineTo(this.PR,y); c.stroke();
          lab(L+"  "+pr.toFixed(dec), xs+3, y-8, col);
        });
        c.lineWidth = 1.5; c.strokeStyle = "rgba(234,236,239,.35)"; c.setLineDash([3,3]); c.beginPath(); c.moveTo(hs[0].x,hs[0].y); c.lineTo(hs[1].x,hs[1].y); c.stroke(); c.setLineDash([]);
      } else if (d.type === "long" || d.type === "short"){
        const xa = hs[0].x, xb = hs[1].x, yE = hs[0].y, yS = hs[1].y, yT = hs[2].y, w = Math.max(6, xb-xa), long_ = d.type === "long";
        c.fillStyle = "rgba(14,203,129,.18)"; c.fillRect(xa, Math.min(yE,yT), w, Math.abs(yE-yT));
        c.fillStyle = "rgba(246,70,93,.18)"; c.fillRect(xa, Math.min(yE,yS), w, Math.abs(yE-yS));
        c.strokeStyle = "#4aa3ff"; c.lineWidth = 1; c.beginPath(); c.moveTo(xa,yE); c.lineTo(xa+w,yE); c.stroke();
        const risk = Math.abs(d.entry-d.stop), rew = Math.abs(d.tp-d.entry), rr = risk ? rew/risk : 0, pc = v => (Math.abs(v-d.entry)/d.entry*100).toFixed(2)+"%";
        lab("TP "+d.tp.toFixed(dec)+" ("+pc(d.tp)+")", xa+4, yT + (long_ ? 9 : -9), "#0ecb81");
        lab("SL "+d.stop.toFixed(dec)+" ("+pc(d.stop)+")", xa+4, yS + (long_ ? -9 : 9), "#f6465d");
        lab((long_ ? "Long" : "Short")+"  R:R "+rr.toFixed(2), xa+4, yE + ((long_ ? yT : yS) < yE ? 9 : -9), "#4aa3ff");
        c.lineWidth = 1.5;
      }
      if (sel || (this.creating === d)){ hs.forEach(h => { c.fillStyle = "#fff"; c.strokeStyle = "#4aa3ff"; c.lineWidth = 1.5; c.beginPath(); c.arc(h.x,h.y,4.5,0,6.3); c.fill(); c.stroke(); });
        const cg = this.cgrip(d, hs); if (cg){ c.fillStyle = "#4aa3ff"; c.strokeStyle = "#fff"; c.lineWidth = 1.5; c.beginPath(); c.rect(cg.x-4.5, cg.y-4.5, 9, 9); c.fill(); c.stroke(); } }
    });
    if (DDOT) delete c.setLineDash; c.restore(); c.font = "11px ui-monospace,Menlo,Consolas,monospace"; c.lineWidth = 1; c.textBaseline = "middle";
  }
});

