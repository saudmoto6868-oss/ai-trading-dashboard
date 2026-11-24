/* LEDGER-BEGIN (owner 2026-11-24): every chart strategy's NEW plan goes to the server signal ledger (modules/signal_ledger.py) through the
   journal bridge, each strategy under its own name, with a snapshot of order flow / bigger timeframes / regime at that moment.
   FORWARD ONLY: a plan is sent when it appears on the newest candles, never the strategy's replayed history (patterns that are confirmed
   later - harmonics, pivots - would look better than they were). The server replays the candles afterwards and explains each trade.
   Sources here: Kill Zone Sniper (kzs), 2.6 (s26), Gann zones (gann), Harmonic (harmonic). The server scanner records itself (main.py). */
const Ledger = {
  seen: new Set(), wait: [],
  bridge(){ try { for (const f of Array.from(window.parent.frames)){ try { if (f.__xpixJournal) return f.__xpixJournal; } catch(e){} } } catch(e){} return null; },
  tf(tf){ return tf === "1M" ? "1mo" : String(tf || "").toLowerCase(); },
  add(s){   // -> true when queued for the server (once per plan per page)
    if (!s || !s.symbol || !(s.entry > 0) || !(s.sl > 0) || !Array.isArray(s.tps)) return false;
    const tps = s.tps.map(Number).filter(v => isFinite(v) && v > 0); if (!tps.length || s.sl === s.entry) return false;
    const k = [s.src, s.sub || "", s.symbol, s.tf, s.dir, s.t0, (+s.entry).toPrecision(8)].join("|"); if (this.seen.has(k)) return false; this.seen.add(k);
    let h = 0; for (let i = 0; i < k.length; i++) h = (h*31 + k.charCodeAt(i)) | 0;
    this.wait.push(Object.assign({}, s, {tps, id:"sig:"+(h >>> 0).toString(36)+":"+k.length, kind:"sig"})); if (this.wait.length > 300) this.wait.splice(0, this.wait.length - 300);
    this.flush(); return true; },
  flush(){ const br = this.bridge(); if (!br) return; while (this.wait.length) br.push(this.wait.shift()); }
};
setInterval(() => Ledger.flush(), 15000);   // the bridge may appear after the first plans (Streamlit reruns)
Object.assign(CandleChart.prototype, {
  ofCtx(dir){   // what the chart showed when the plan appeared: order flow of the last candle (real trades or candle-shape estimate), CVD direction, bigger timeframes, regime
    const d = this.data, n = d.length, out = {}; if (!n) return out; const k = d[n-1], m = this.fp && this.fp.get(k.t), rg = k.h - k.l, up = dir === "long";
    let bp; if (m && m.b + m.s > 0){ bp = m.b/(m.b + m.s); out.of_real = true; } else { bp = rg > 0 ? (k.c - k.l)/rg : .5; out.of_real = false; }
    out.delta_pct = Math.round(bp*100); out.of = bp >= .55 ? (up ? "with" : "against") : bp <= .45 ? (up ? "against" : "with") : "neutral";
    try { const cv = this.cvdSeries(Math.max(0, n - 20), n - 1); if (cv.length > 1){ const r = cv[cv.length-1].cum - cv[0].cum; out.cvd = (r >= 0) === up ? "with" : "against"; out.cvd_real = cv.filter(p => p.real).length; } } catch(e){}
    try { const T = this.htfTrends().filter(t => t.dir !== "flat" && t.dir && (TFSEC[t.tf] || 0) > (TFSEC[this.tf] || 0)); if (T.length){ const w = T.filter(t => (t.dir === "up") === up).length; out.htf = w > T.length/2 ? "with" : w < T.length/2 ? "against" : "mixed"; out.htf_n = T.length; } } catch(e){}
    try { const r = Regime.now(d); if (r && r.regime) out.regime = r.regime; } catch(e){}
    return out; },
  ledgerAdd(o){   // o = {src, sub, tBar (open time of the signal candle), dir, entry, sl, tps, tf?, ms?, why?}
    if (!this.sym || !this.data.length || !(o.tBar > 0)) return false; const ms = o.ms || this.secMs();
    return Ledger.add({src:o.src, sub:o.sub || "", symbol:this.sym, tf:Ledger.tf(o.tf || this.tf), dir:o.dir, entry:+o.entry, sl:+o.sl, tps:o.tps, t0:o.tBar + ms, ctx:this.ofCtx(o.dir), why:o.why || []}); }
});
{ const P = CandleChart.prototype, wrap = (fn, after) => { const f = P[fn]; if (typeof f !== "function") return; P[fn] = function(...a){ const r = f.apply(this, a); try { after.call(this, r, a); } catch(e){} return r; }; };
  const fresh = (ch, j) => j >= ch.data.length - 3 && j <= ch.data.length - 2;   // written on one of the two newest CLOSED candles (the forming candle can still change its mind)
  wrap("kzsCalc", function(L){ (L || []).forEach(s => { if (!fresh(this, s.j)) return; this.ledgerAdd({src:"kzs", sub:s.kz || "", tBar:this.data[s.j].t, dir:s.side > 0 ? "long" : "short", entry:s.en, sl:s.sl, tps:[s.tp]}); }); });
  wrap("paintS26", function(){ const R = this._s26 && this._s26.r; (R || []).forEach(p => { if (p.known == null || !fresh(this, p.known)) return;
    this.ledgerAdd({src:"2.6", sub:p.kind || "", tBar:this.data[p.known].t, dir:p.side === "BUY" ? "long" : "short", entry:p.entry, sl:p.stop, tps:[p.tp1, p.tp2]}); }); });
  wrap("gannTrades", function(T, a){ const src = a[0] || {}, sd = src.d || this.data, ms = src.ms || this.secMs(); if (!sd.length || !T || !T.list) return;
    T.list.forEach(tr => { if (!(tr.t >= sd[Math.max(0, sd.length - 3)].t && tr.t <= sd[Math.max(0, sd.length - 2)].t)) return; this.ledgerAdd({src:"gann", sub:"zone", tBar:tr.t, ms, tf:src.tf, dir:tr.dir > 0 ? "long" : "short", entry:tr.en, sl:tr.sl, tps:[tr.tp1, tr.tp2]}); }); });
  wrap("paintHarm", function(){ const H = this._harm, n = this.data.length; if (!H || !H.list) return;
    H.list.forEach(h => { if (h.state === "forming" || !h.plan || !h.pts || !h.pts[4] || h.pts[4].i < n - 3) return;   // a finished XABCD whose D is on the newest candles
      this.ledgerAdd({src:"harmonic", sub:h.name || "", tBar:this.data[n-1].t, dir:h.dir === "bull" ? "long" : "short", entry:h.plan.entry, sl:h.plan.stop, tps:h.plan.tps}); }); });
}
/* LEDGER-END */
