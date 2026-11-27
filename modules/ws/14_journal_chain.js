/* ---------------- Trade journal: logs every scanner/alert trade, then follows it on OKX candles until TP1 or SL ---------------- */
const TFMS = {"1m":6e4, "5m":3e5, "15m":9e5, "1h":36e5, "4h":144e5, "1d":864e5};
const JBAR = {"1m":["1m",60000], "1H":["1H",3600000], "1D":["1D",86400000]};
const JEXP = {"5m":6*3600e3, "15m":12*3600e3, "4h":6*86400e3, "1m":12*3600e3, "13m":24*3600e3, "1h":3*86400e3, "2h":4*86400e3, "3h":5*86400e3, "6h":8*86400e3, "7h":9*86400e3, "8h":10*86400e3, "12h":14*86400e3, "1d":20*86400e3, "3d":40*86400e3, "1w":60*86400e3, "1mo":120*86400e3};
const TFC_ALL = {"1m":"1m","5m":"5m","13m":"13m","15m":"15m","4h":"4H","1h":"1H","2h":"2H","3h":"3H","6h":"6H","7h":"7H","8h":"8H","12h":"12H","1d":"1D","3d":"3D","1w":"1W","1mo":"1M"}, TFK_OPTS = [["1m","1m"],["5m","5m"],["13m","13m"],["15m","15m"],["1h","1h"],["2h","2h"],["3h","3h"],["4h","4h"],["6h","6h"],["7h","7h"],["8h","8h"],["12h","12h"],["1d","1d"],["3d","3d"],["1w","1w"],["1mo","1M"]];
/* Chain layers (docs/PIPELINE.md): the 5 institution-style layers the lab grades every signal by (modules/strategy_lab.py chain_layers) - htf: 100-bar trend on the trade side; loc: long in the lower third / short in the upper third of the 50-bar range;
   vol: bar volume >= 1.2x its 20-bar mean; reg: ATR% >= 0.8x its 100-bar median; time: London / New York hours (UTC 7-20; always on the daily). Grade A+++ = 5 layers, A+ = 4, A = 3, B = 2, C = 0-1.
   Recorded with every journal trade (info only: the first real lab run showed grades do NOT rank trades yet, so nothing is filtered by it) - live results then confirm or kill the lab's numbers. */
const Chain = {
  layers(d, dir, tf, tms){ const L = d && d.length; if (!L || L < 120 || !dir) return null; const i = L - 1, c = d.map(x => x.c), tr = d.map((x, j) => j ? Math.max(x.h - x.l, Math.abs(x.h - d[j-1].c), Math.abs(x.l - d[j-1].c)) : x.h - x.l), at = tr.map((_, j) => { let q = 0, m = 0; for (let k = Math.max(0, j - 13); k <= j; k++){ q += tr[k]; m++; } return q/m; }), natr = at.map((v, j) => c[j] > 0 ? v/c[j] : NaN);
    let h = -Infinity, l = Infinity; for (let j = Math.max(0, i - 49); j <= i; j++){ if (d[j].h > h) h = d[j].h; if (d[j].l < l) l = d[j].l; } const pos = h > l ? (c[i] - l)/(h - l) : .5;
    let vs = 0, vn = 0; for (let j = Math.max(0, i - 20); j < i; j++){ vs += +d[j].v || 0; vn++; } const rv = vn && vs > 0 ? (+d[i].v || 0)/(vs/vn) : 0;
    const r0 = natr.slice(Math.max(0, i - 100), i).filter(v => v > 0).sort((a, b) => a - b), med = r0.length ? (r0.length % 2 ? r0[(r0.length - 1)/2] : (r0[r0.length/2 - 1] + r0[r0.length/2])/2) : 0;
    const hr = new Date(tms || Date.now()).getUTCHours(), daily = /^1d$/i.test(tf || "");
    const o = {htf:Math.sign(c[i] - c[i - 100]) === dir, loc:dir > 0 ? pos <= 1/3 : pos >= 2/3, vol:rv >= 1.2, reg:med > 0 ? natr[i]/med >= .8 : true, time:daily || (hr >= 7 && hr < 20)};
    const n = ["htf", "loc", "vol", "reg", "time"].filter(k => o[k]).length; o.g = n === 5 ? "A+++" : n === 4 ? "A+" : n === 3 ? "A" : n === 2 ? "B" : "C"; return o; },
  tag(rec){ candlesTf(rec.symbol, TFC_ALL[rec.tfk] || "1H", true, 200).then(rows => { const o = Chain.layers(rows, rec.dir === "bullish" ? 1 : -1, rec.tfk, rec.t0); if (o){ rec.chain = o; Journal.save(); } }).catch(() => {}); }   // async: the trade is logged at once, the layers are added when the candles arrive
};
/* the journal trade on this symbol at this entry, only if it FILLED (price reached the entry). Only a filled journal trade may draw a trade box */
function journalFill(sym, entry){ return (Journal.list || []).find(t => t.symbol === sym && t.fill !== false && Math.abs(t.entry - entry) <= 0.0005*Math.abs(entry)) || null; }
const Journal = {
  list: store.get(LS+"_journal", []), subs: new Set(), busy: false,
  cfg: Object.assign({min:50, rr:1}, store.get(LS+"_jset", {}) || {}),   // what gets LOGGED: weak (< min % strength) or poor-payoff (< rr R:R) setups are not recorded, so they cannot drag the win rate down
  px(sym){ const t = Hub.last["tickers|all"]; return t && !t.error && t[sym] ? t[sym].last : null; },
  save(){ this.list = this.list.slice(-1500); store.set(LS+"_journal", this.list); this.pushServer(); this.subs.forEach(f => f()); },
  // one journal: every new or changed trade goes to the server store (trade_journal.py) through the journal bridge; localStorage stays as this browser's cache
  pushServer(){
    let br = null; try { for (const f of Array.from(window.parent.frames)){ try { if (f.__xpixJournal){ br = f.__xpixJournal; break; } } catch(e){} } } catch(e){}
    if (!br) return; this._sent = this._sent || {};
    for (const t of this.list){
      const sig = [t.status, t.fill, t.r, t.t1, t.reason || "", (t.exits || []).length].join("|"); if (this._sent[t.id] === sig) continue; this._sent[t.id] = sig;
      br.push({id:t.id, symbol:t.symbol, dir:t.dir, tfk:t.tfk, ttype:t.ttype, entry:t.entry, sl:t.sl, tp1:t.tp1, tp2:t.tp2 || null, tp3:t.tp3 || null, rr:t.rr, score:t.score, max:t.max, tags:t.tags || [], ctx:t.ctx || null, t0:t.t0, t1:t.t1 || null, status:t.status, fill:t.fill !== false, r:t.r || 0, exits:t.exits || [], reason:t.reason || ""});
    }
  },
  ingest(){
    let added = 0; const pool = [];
    (CFG.ready || []).forEach(e => pool.push(e)); Alerts.list.forEach(a => a.card && pool.push(a.card));
    pool.slice(0, 12).forEach(e => e && e.symbol && Ctx.get(e.symbol));   // warm the live-context cache for the newest setups
    pool.forEach(e => {
      if (!e || !e.plan || !planOk(e.plan, e.direction)) return;
      const key = e.symbol+"|"+e.direction+"|"+e.ttype, en = e.plan.entry;
      if (100*e.score/Math.max(1, e.max) < this.cfg.min) return; { const r0 = Math.abs(en - e.plan.stop); if (!r0 || Math.abs(e.plan.tps[0] - en)/r0 < this.cfg.rr) return; }
      const cd = (JEXP[e.tfk] || 3*86400e3)/6;   // cool-down per setup: the same symbol|side|type is not re-logged every time price drifts, even after the first one closed
      if (this.list.some(t => t.key === key && (t.status === "open" || Math.abs(t.entry-en)/en < 0.0005 || Date.now() - t.t0 < cd))) return;
      const rec = {id:key+"|"+Date.now(), key, symbol:e.symbol, dir:e.direction, tfk:e.tfk, ttype:e.ttype, entry:en, sl:e.plan.stop, tp1:e.plan.tps[0], tp2:e.plan.tps[1] || null, tp3:e.plan.tps[2] || null,
        rr: Math.abs(e.plan.tps[0]-en)/Math.max(1e-12, Math.abs(en-e.plan.stop)), riskPct:0.25, score:e.score, max:e.max, pct:Math.round(100*e.score/Math.max(1,e.max)), tags:(e.tags||[]).map(t => t[0]).slice(0,4), t0:Date.now(), status:"open", ctx:Object.assign(Ctx.snapshot(e.symbol, e.direction), {schools: e.j ? {verdict:e.j.verdict, score:e.j.score, pct:e.j.pct, pros:e.j.pros.map(p => [p[0], p[1]]), cons:e.j.cons.map(p => [p[0], p[1]]), vetoes:e.j.vetoes.map(p => p[0]), second:e.j.second.map(p => p[0])} : null, snap: e.ctxSnap || null}), fill:(() => { const p0 = this.px(e.symbol); return p0 ? Math.abs(en - p0)/p0 <= 0.0002 : false; })()}; this.list.push(rec); Chain.tag(rec);   // fill:false = the plan entry is away from the price, the trade only counts once price really touches it (old records have no field = filled)
      added++;
    });
    if (added) this.save();
  },
  async track(){
    if (this.busy) return; const open = this.list.filter(t => t.status === "open"); if (!open.length) return; this.busy = true; let changed = false;
    try {
      const bySym = {}; open.forEach(t => (bySym[t.symbol] = bySym[t.symbol] || []).push(t));
      for (const sym of Object.keys(bySym)){
        const trs = bySym[sym], oldest = Math.min(...trs.map(t => t.t0)), age = Date.now() - oldest, bar = age < 4.5*3600e3 ? JBAR["1m"] : age < 12*86400e3 ? JBAR["1H"] : JBAR["1D"];
        let rows; try { rows = (await okx("/market/candles?instId="+encodeURIComponent(sym)+"&bar="+bar[0]+"&limit=300")).map(r => ({t:+r[0], h:+r[2], l:+r[3], c:+r[4]})).reverse(); } catch(e){ continue; }
        trs.forEach(tr => {
          const long_ = tr.dir === "bullish"; if (rows.length){ tr.last = rows[rows.length-1].c; changed = true; }
          for (const c of rows){
            if (c.t + bar[1] <= tr.t0) continue;
            let fc = false;   // fill candle: the target in the same candle could have printed BEFORE the fill, so only the stop counts there
            if (tr.fill === false){   // entry not touched yet: a move to the stop or the target WITHOUT touching the entry was never a trade
              if (c.l <= tr.entry && tr.entry <= c.h){ tr.fill = true; fc = true; changed = true; }
              else { const away = long_ ? (c.l > tr.entry ? c.h >= tr.tp1 : c.h < tr.entry && c.l <= tr.sl) : (c.h < tr.entry ? c.l <= tr.tp1 : c.l > tr.entry && c.h >= tr.sl); if (away){ tr.status = "nf"; tr.r = 0; tr.t1 = c.t + bar[1]; changed = true; break; } continue; } }
            // partial exits: each target books 1/n of the trade at its own R (n = 1, 2 or 3 targets); the stop books the units still open at -1R; status stays "open" until the last unit is closed
            tr.exits = tr.exits || []; const n = tr.tp3 ? 3 : tr.tp2 ? 2 : 1, risk = Math.abs(tr.entry - tr.sl) || 1e-12, sumR = () => tr.exits.reduce((a, e) => a + e.r, 0), booked = new Set(tr.exits.map(e => e.level));
            const beOn = booked.has("tp1"), slPx = beOn ? tr.entry : tr.sl;   // after TP1 the stop moves to the entry (breakeven): the rest of the trade cannot lose
            const sl = long_ ? c.l <= slPx : c.h >= slPx;
            if (sl){ const tpN = tr.exits.filter(e => e.level !== "sl").length; tr.exits.push({level:"sl", t:c.t + bar[1], price:slPx, r: beOn ? 0 : -(n - tpN)/n}); tr.status = "sl"; tr.r = sumR(); tr.t1 = c.t + bar[1]; changed = true; break; }   // same candle touches both: count the stop (conservative)
            if (!fc) for (const [lvl, px] of [["tp1", tr.tp1], ["tp2", tr.tp2], ["tp3", tr.tp3]]){ if (!px || booked.has(lvl)) continue; if (long_ ? c.h >= px : c.l <= px){ booked.add(lvl); tr.exits.push({level:lvl, t:c.t + bar[1], price:px, r:Math.abs(px - tr.entry)/risk/n}); changed = true; } }   // the fill candle cannot book a target (the target may have printed before the fill)
            tr.r = sumR();
            if (tr.exits.filter(e => e.level !== "sl").length >= n){ tr.status = "tp"; tr.t1 = c.t + bar[1]; changed = true; break; }
          }
          // max hold: 24 bars of the trade's timeframe, then it closes at the R already booked
          if (tr.status === "open" && Date.now() - tr.t0 > Math.min(JEXP[tr.tfk] || 3*86400e3, 24 * (TFMS[tr.tfk] || 36e5))){ tr.status = tr.fill === false ? "nf" : "exp"; tr.r = tr.fill === false ? 0 : (tr.exits || []).reduce((a, e) => a + e.r, 0); tr.t1 = Date.now(); changed = true; }
        });
      }
    } finally { this.busy = false; }
    if (changed) this.save();
  },
  /* POST-MORTEM of a stopped trade (pure, from the saved record): warnings already on at entry, what the wider-stop test says, one next step. */
  postmortem(tr){
    if (!tr || tr.status !== "sl") return null;
    const long_ = tr.dir === "bullish", c = tr.ctx || {}, why = [], wider = [];
    if (c.of === "against") why.push([Lg("Order flow was against the trade at entry","الأوردر فلو كان ضد الصفقة وقت الدخول"), 1]);
    if (c.news) why.push([Lg("News was active on the symbol at entry","كان هناك خبر نشط على الرمز وقت الدخول"), 1]);
    if (c.fund === (long_ ? "crowded longs" : "crowded shorts")) why.push([Lg("Funding was crowded on the trade side","التمويل كان مزدحم في اتجاه الصفقة"), 1]);
    if (c.oi && (long_ ? ["shorts","closing"] : ["longs","cover"]).includes(c.oi)) why.push([Lg("Open interest did not back the trade","الـOI ما كانش داعم للصفقة"), 1]);
    if (tr.score != null && tr.max && 100*tr.score/tr.max < 70) why.push([Lg("Setup score was weak (under 70%)","سكور الإعداد كان ضعيف (أقل من 70%)"), 1]);
    const r = tr.stk && tr.stk.r; if (r) [1.25, 1.5, 2, 3].forEach(k => { if (r[k] > 0) wider.push(k); });
    if (wider.length) why.push([Lg("A wider stop ("+wider[0]+"× risk) would have reached the target","ستوب أوسع ("+wider[0]+"× الخطر) كان هيوصل للهدف"), 0]);
    const warns = why.filter(w => w[1]).length;
    const next = warns ? Lg("Skip or wait: "+warns+" warning(s) were already on at entry","تجنّب الدخول أو انتظر: كان هناك "+warns+" تحذير وقت الدخول")
      : wider.length ? Lg("Stop too tight for this setup: test the wider stop on more trades","الستوب ضيّق على الإعداد ده: جرّب الستوب الأوسع على صفقات أكتر")
      : Lg("Entry came early: wait for a confirming close before entering","الدخول كان بدري: استنى إغلاق تأكيد قبل الدخول");
    if (!why.length) why.push([Lg("No warning was recorded at entry","لم يُسجَّل أي تحذير وقت الدخول"), 0]);
    return {why: why.map(w => w[0]), next, warns};
  },
  /* STOP TEST on YOUR trades (owner 2026-11-03: "most trades hit the stop and then reach the target"). For every finished trade, replay the candles after the entry with the SAME target and a stop k x the original risk
     (k = 1 is the real stop). Shows how many stopped trades did reach the target later, and what a wider stop would have done to the average R. Mark-to-close at the end of the trade's life when neither was hit. A tiny sample proves nothing (n < 30). */
  KS: [1, 1.25, 1.5, 2, 3],
  simOne(tr, rows, bm){
    const long_ = tr.dir === "bullish", risk = Math.abs(tr.entry - tr.sl), rr = tr.rr || Math.abs(tr.tp1 - tr.entry)/risk; if (!(risk > 0) || !(rr > 0)) return null; const end = tr.t0 + (JEXP[tr.tfk] || 3*86400e3);
    const bars = rows.filter(c => c.t + bm > tr.t0 && c.t < end); if (!bars.length || rows[0].t > tr.t0 + bm) return null;   // the candle history must reach back to the entry
    const full = Date.now() >= end;   // false = the trade's life is not over yet: counted "so far" (a later recovery would be missed) and replayed again later
    const adv = bars.map(c => long_ ? (tr.entry - c.l)/risk : (c.h - tr.entry)/risk); let ti = -1; for (let i = 1; i < bars.length; i++){ if (long_ ? bars[i].h >= tr.tp1 : bars[i].l <= tr.tp1){ ti = i; break; } }   // the entry candle only counts for the stop (like the tracker)
    const lastC = bars[bars.length-1].c, mtm = (long_ ? lastC - tr.entry : tr.entry - lastC)/risk, out = {};
    this.KS.forEach(k => { let js = -1; for (let i = 0; i < adv.length; i++){ if (adv[i] >= k - 1e-9){ js = i; break; } } out[k] = js >= 0 && (ti < 0 || js <= ti) ? -k : ti >= 0 ? rr : Math.max(-k, Math.min(rr, mtm)); });
    let j1 = -1; for (let i = 0; i < adv.length; i++){ if (adv[i] >= 1 - 1e-9){ j1 = i; break; } }
    return {r:out, rr, full, rec:j1 >= 0 && (ti < 0 || j1 < ti) ? (ti >= 0 ? 1 : 0) : null, mae:ti >= 0 ? Math.max(...adv.slice(0, ti + 1)) : null}; },
  async simStops(){
    if (this._sim) return; const todo = this.list.filter(t => (t.status === "sl" || t.status === "tp" || t.status === "exp") && t.fill !== false && (!t.stk || !t.stk.full) && t.entry && t.sl && t.tp1 && (!t._stkT || Date.now() - t._stkT > 3600e3)); if (!todo.length) return; this._sim = true; let ch = false;
    try { const bySym = {}; todo.forEach(t => (bySym[t.symbol] = bySym[t.symbol] || []).push(t));
      for (const sym of Object.keys(bySym)){ const trs = bySym[sym], age = Date.now() - Math.min(...trs.map(t => t.t0)), bar = age < 4.5*3600e3 ? JBAR["1m"] : age < 12*86400e3 ? JBAR["1H"] : JBAR["1D"];
        let rows; try { rows = (await okx("/market/candles?instId="+encodeURIComponent(sym)+"&bar="+bar[0]+"&limit=300")).map(r => ({t:+r[0], h:+r[2], l:+r[3], c:+r[4]})).reverse(); } catch(e){ continue; }
        trs.forEach(tr => { tr._stkT = Date.now(); const o = this.simOne(tr, rows, bar[1]); if (o){ const prev = JSON.stringify(tr.stk || null); tr.stk = o; if (JSON.stringify(o) !== prev) ch = true; } }); } } finally { this._sim = false; }
    if (ch) this.save(); },
  stopTable(list){   // rows per stop distance + the "stopped, then reached the target" share, from the trades that have a replay
    const S = list.filter(t => t.stk); if (!S.length) return null; const n = S.length, rr = S.reduce((a, t) => a + t.stk.rr, 0)/n;
    const rows = this.KS.map(k => { const v = S.map(t => t.stk.r[k]); return {k, n, win:100*v.filter((x, i) => x >= S[i].stk.rr - 1e-9).length/n, avg:v.reduce((a, b) => a + b, 0)/n}; });
    const st = S.filter(t => t.stk.rec != null), rec = st.filter(t => t.stk.rec === 1).length, mae = S.map(t => t.stk.mae).filter(x => x != null).sort((a, b) => a - b), q = f => mae.length ? mae[Math.min(mae.length - 1, Math.floor(f*mae.length))] : null;
    return {n, full:S.filter(t => t.stk.full).length, rows, stopped:st.length, rec, mae:{n:mae.length, p50:q(.5), p75:q(.75), p90:q(.9)}}; },
  stats(minPct, since){
    const L = this.list.filter(t => t.pct >= minPct && t.t0 >= since), closed = L.filter(t => t.status === "tp" || t.status === "sl").sort((a,b) => a.t1 - b.t1), W = closed.filter(t => t.status === "tp");
    const gp = W.reduce((a,t) => a + t.r, 0), gl = closed.length - W.length; let eq = 0, peak = 0, dd = 0; const curve = closed.map(t => { eq += t.r; peak = Math.max(peak, eq); dd = Math.max(dd, peak - eq); return {t:t.t1, v:eq}; });
    return {all:L, closed, wins:W.length, losses:gl, open:L.filter(t => t.status === "open").length, exp:L.filter(t => t.status === "exp").length, nf:L.filter(t => t.status === "nf").length,
      wr: closed.length ? 100*W.length/closed.length : 0, net: eq, avg: closed.length ? eq/closed.length : 0, pf: gl ? gp/gl : (gp ? Infinity : 0),
      best: closed.length ? Math.max(...closed.map(t => t.r)) : 0, worst: closed.length ? Math.min(...closed.map(t => t.r)) : 0, dd, curve};
  }
};
setTimeout(() => { Journal.ingest(); Journal.track(); Journal.simStops(); }, 1500);
setInterval(() => { Journal.ingest(); Journal.track(); Journal.simStops(); }, 30000);
Alerts.subs.add(() => Journal.ingest());
const RegimeCtx = {   // market regime of a setup's symbol on its own timeframe (candles via candlesTf, 5-minute cache); the Setup Card shows it as information, never as a pass / fail
  c:{},
  get(sym, tf){ const k = sym+"|"+tf, h = this.c[k]; if (h && (h.busy || Date.now() - h.t < 300000)) return h;
    const o = this.c[k] = {t:h ? h.t : 0, v:h ? h.v : null, busy:true};
    candlesTf(sym, tf, true, 200).then(rows => { this.c[k] = {t:Date.now(), v:Regime.of(rows), busy:false}; Setup.subs.forEach(f => f()); }).catch(() => { this.c[k] = {t:Date.now(), v:null, busy:false}; });
    return o; }
};
const Setup = {sel:null, subs:new Set(), pick(e){ this.sel = e; this.subs.forEach(f => f()); }};   // the setup shown by the Setup Card widget (clicked chip / newest alert / best live setup)
function setupHtml(e){
  const ar = lang === "ar", long_ = e.direction === "bullish", col = long_ ? "#0ecb81" : "#f6465d", pl = e.plan || null, a = e.ana || null, pct = Math.round(100*e.score/Math.max(1, e.max));
  let rr = null; try { const r0 = Math.abs(pl.entry - pl.stop); rr = r0 ? Math.abs(pl.tps[0] - pl.entry)/r0 : null; } catch(x){}
  const H = t => '<div style="margin-top:9px;font-weight:700;color:#f0b90b">'+esc(t)+'</div>', li = arr => '<ul dir="rtl" style="margin:3px 0;padding-inline-start:16px;text-align:right;line-height:1.55">'+arr.map(x => '<li>'+esc(x)+'</li>').join("")+'</ul>';
  let h = '<div style="padding:8px 10px;font-size:12px;line-height:1.5"><div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap"><b style="font-size:15px">'+esc(e.symbol.replace(/-(USDT|USDC|SWAP)$/,""))+'</b><span style="color:'+col+';font-weight:700">'+(long_ ? "▲ "+Lg("BUY","شراء") : "▼ "+Lg("SELL","بيع"))+'</span><span class="m">'+esc(ttTxt(e.ttype))+' · '+esc(e.tfk || "")+'</span><span style="margin-inline-start:auto;font-weight:700;color:'+(pct >= 70 ? col : "#eaecef")+'">'+e.score+'/'+e.max+' · '+pct+'%</span></div>';
  if (e.q != null && e.q > 0) h += '<div class="m" style="margin-top:2px">'+esc(Lg("Evidence quality","جودة الأدلة"))+': <b style="color:#eaecef">'+e.q+'/100</b>'+((e.qwhy || []).length ? ' · '+esc(e.qwhy.join(" · ")) : "")+'</div>';
  { const c = Ctx.cache[e.symbol]; if ((!c || Date.now() - c.t > 60000) && !Ctx.busy[e.symbol] && !/^(Y|FH):/.test(e.symbol)) Ctx.get(e.symbol).then(r => { if (r && r !== c) Setup.subs.forEach(f => f()); });   // re-draw only when a NEW snapshot arrived: a busy / Yahoo symbol resolved at once and looped draw -> get -> draw in microtasks (froze the page)
    const R = (Ws.radar && Ws.radar.d[e.symbol]) || null, fr = R && !R.err ? (R.verdict === "up" ? (long_ ? "ok" : "bad") : R.verdict === "down" ? (long_ ? "bad" : "ok") : "mid") : "na";
    const ofv = Ctx.ofVerdict(c, e.direction), ses = Ctx.session(), nw = Ctx.news(e.symbol), fu = Ctx.fundFlag(c, e.direction), ic = k => ({ok:'<b class="g">✓</b>', bad:'<b class="rd">✗</b>', mid:'<b class="m">~</b>', na:'<b class="m">–</b>'})[k];
    const rows = [[fr, Lg("Daily trend (radar)","الترند اليومي (الرادار)"), R && !R.err ? R.verdict : Lg("open the radar","افتح الرادار")],
      [e.q >= 50 ? "ok" : e.q ? "mid" : "na", Lg("Lab evidence","أدلة المعمل"), e.q ? e.q+"/100" : "–"],
      [ofv === "agree" ? "ok" : ofv === "against" ? "bad" : ofv === "mixed" ? "mid" : "na", Lg("Order book + tape now","دفتر الأوامر والصفقات الآن"), c && c.of ? "book "+(c.of.book == null ? "–" : Math.round(c.of.book*100)+"%")+" · Δ2m "+(c.of.delta == null ? "–" : Math.round(c.of.delta*100)+"%") : "…"],
      [/KZ/.test(ses) ? "ok" : "mid", Lg("Time (NY session)","الوقت (جلسة نيويورك)"), ses],
      (() => { const rg = RegimeCtx.get(e.symbol, TFC_ALL[e.tfk] || "1H"), v = rg && rg.v; return [v && v.regime ? "mid" : "na", Lg("Market regime (now, this timeframe)","حالة السوق (الآن، نفس الإطار الزمني)"), v && v.regime ? v.regime.toUpperCase()+(v.adx != null ? " · ADX "+Math.round(v.adx) : "") : (rg && rg.busy ? "…" : "–")]; })(),
      [nw ? "bad" : "ok", Lg("High-impact news ±1h","خبر قوي خلال ساعة"), nw ? nw.country+" "+nw.title : Lg("none","لا يوجد")],
      [fu ? "bad" : (c && c.fund != null ? "ok" : "na"), Lg("Funding (crowding)","التمويل (الزحمة)"), c && c.fund != null ? (c.fund*100).toFixed(3)+"%"+(fu ? " · "+fu : "") : "–"],
      (() => { const o = Ctx.oiFlag(c, e.direction); return [o.k, Lg("Open interest 4h (OKX)","العقود المفتوحة 4س (OKX)"), o.txt]; })()];
    h += '<div style="margin-top:6px;border:1px solid var(--line);border-radius:4px;padding:4px 6px"><div class="m" style="font-size:10px;margin-bottom:2px">'+esc(Lg("Checklist (playbook)","قائمة التحقق (الخطة)"))+'</div>'+rows.map(([k, l, v]) => '<div style="display:flex;gap:6px;font-size:11px">'+ic(k)+'<span style="flex:1">'+esc(l)+'</span><span class="m">'+esc(String(v))+'</span></div>').join("")+'</div>'; }
  if ((e.tags || []).length) h += '<div style="margin-top:5px">'+e.tags.slice(0,6).map(t => '<span style="display:inline-block;padding:0 6px;margin:0 3px 3px 0;border-radius:3px;font-size:10px;font-weight:700;background:'+esc(t[1])+';color:'+esc(t[2])+'" title="'+esc(tagTip(t))+'">'+esc(tagTxt(t[0]))+'</span>').join("")+'</div>';
  if ((e.lab || []).length){   // backtest beside the signal (owner 2026-11-20): weekly-lab row per detector, net of cost; never a promise
    const f = v => v == null ? "–" : (v >= 0 ? "+" : "")+Number(v).toFixed(2), vc = {edge:["#0ecb81", Lg("passed the lab gate","عدّى بوابة المعمل")], "too few":["#848e9c", Lg("too few (not evidence)","عدد قليل (ليس دليلًا)")], loses:["#f6465d", Lg("loses after cost","خسران بعد التكلفة")], "positive, not proven":["#f0b90b", Lg("positive, not proven","موجب، غير مثبت")]};
    h += H(Lg("Backtest beside the signal (weekly lab, net of cost)","الباك تيست جنب الإشارة (المعمل الأسبوعي، بعد التكلفة)"))
      +'<table class="rdt"><tr><th>'+esc(Lg("detector","المؤشر"))+'</th><th>TF</th><th>n</th><th>'+esc(Lg("net R","صافي R"))+'</th><th>t</th><th>IS / OOS</th><th></th></tr>'
      +e.lab.map(r => { const v = vc[r.verdict] || ["#848e9c", r.verdict]; return '<tr><td>'+esc(r.key)+'</td><td>'+esc(r.tf)+'</td><td>'+r.n+'</td><td style="color:'+(r.net > 0 ? "#0ecb81" : "#f6465d")+'">'+f(r.net)+'</td><td>'+f(r.t)+'</td><td>'+f(r.is)+' / '+f(r.oos)+'</td><td style="color:'+v[0]+'">'+esc(v[1])+'</td></tr>'; }).join("")+'</table>';
  }
  if (pl) h += H(Lg("Trade plan","خطة الصفقة"))+'<div style="display:grid;grid-template-columns:auto 1fr;gap:2px 10px"><span class="m">'+Lg("Entry","دخول")+'</span><b>'+fmtP(pl.entry)+'</b><span class="m">'+Lg("Stop","وقف")+'</span><b style="color:#f6465d">'+fmtP(pl.stop)+'</b>'+pl.tps.map((v, i) => '<span class="m">'+Lg("Target ","هدف ")+(i+1)+'</span><b style="color:#0ecb81">'+fmtP(v)+'</b>').join("")+(rr ? '<span class="m">R:R</span><b>1 : '+rr.toFixed(1)+'</b>' : "")+'</div>';
  if (e.eta) h += '<div class="m" style="margin-top:3px">'+esc(typeof e.eta === "string" ? e.eta : "")+'</div>';
  if (a){ h += H(Lg("Conditions met (why the setup opened)","الشروط اللي اتحققت (ليه السيت اب اتفتح)"))+li(a.sig || []);
    if (a.ctx && a.ctx.length) h += H(Lg("Context: daily bias / premium-discount / kill zone","السياق: تحيز اليوم / بريميوم-ديسكاونت / الكيل زون"))+li(a.ctx);
    if (a.against) h += '<div dir="rtl" style="margin-top:7px;color:#f6465d;text-align:right">'+esc(a.against)+'</div>';
    if (a.htf && a.htf.length) h += H(Lg("Higher timeframes","الفريمات الأعلى"))+li(a.htf);
    if (a.mtf && a.mtf.length) h += H(Lg("Weekly / Daily / 4H framework","إطار الأسبوعي / اليومي / 4 ساعات"))+li(a.mtf);
    if (a.scen && a.scen.length) h += H(Lg("Scenarios","السيناريوهات"))+li(a.scen); }
  else h += '<div class="m" style="margin-top:8px">'+esc(Lg("No stored analysis for this older setup; it fills in after the next scan.","لا يوجد تحليل محفوظ لهذا الإعداد القديم؛ سيظهر بعد المسح التالي."))+'</div>';
  return h+'<div class="m" style="margin-top:9px;font-size:10px">'+esc(Lg("Evidence ranking, not a proven win rate. Not financial advice.","ترتيب بالأدلة وليس نسبة نجاح مثبتة. وليست نصيحة مالية."))+'</div></div>';
}

