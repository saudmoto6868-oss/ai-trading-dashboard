/* ---- TRADE CLASSES (owner 2026-11-06): trades sorted by style (Scalp / Day / Swing / Position), each style with its own
   timeframe stack (Elder triple screen: bias -> setup -> entry, same stacks as the Technical Office playbook, modules/office_kpi.py).
   Engine "S/R bounce": price at a support / resistance zone (pivot clusters with >= 2 touches, same as SR.compute) -> a bounce trade
   with a target in POINTS (Auto / 50 / 100 / 120 / 200 ...). The bounce size is MEASURED on this symbol's own candles, walk-forward
   (a level only counts after its pivot was confirmed, no future candles), so "it usually bounces ~100 points here" is a number with n,
   not a promise. Other schools (Elliott / ICT / classic) re-use the scanner's live setups, sorted into the same styles.
   Output joins the normal pipeline: Alerts.add -> Alerts widget, Setup Card, Ready, Signals, the live-setups strip and the journal
   (which then keeps the forward record). Information, not a proven edge: < 30 forward trades = not evidence. */
/* TCLASS-BEGIN pure engine (no DOM, no fetch): tests/test_tclass_js.py runs it with node on synthetic candles */
const TCE = {
  STYLES: {
    "Scalp":     {bias:"1H", setup:"15m", entry:"5m",  tfk:"5m",  hold:16, every:3*60e3,    want:400},
    "Day Trade": {bias:"4H", setup:"1H",  entry:"15m", tfk:"15m", hold:24, every:10*60e3,   want:400},
    "Swing":     {bias:"1W", setup:"1D",  entry:"4H",  tfk:"4h",  hold:20, every:60*60e3,   want:300},
    "Position":  {bias:"1M", setup:"1W",  entry:"1D",  tfk:"1d",  hold:16, every:4*3600e3,  want:200}
  },
  TARGETS: [0, 50, 100, 120, 200, 300, 500, 1000],   // 0 = Auto (the measured median bounce)
  // size of one "point" per market (editable in the widget): forex = pip, gold 0.1, silver / oil / stocks 0.01, indices 1, crypto by price
  pointSize(sym, px){
    sym = String(sym || ""); const b = sym.replace(/^(HL:xyz:|HL:|FH:|Y:)/, "").toUpperCase();
    if (/=X$/.test(b) || /^(EUR|GBP|AUD|NZD|USD|CAD|CHF|JPY)[_/]?(EUR|GBP|AUD|NZD|USD|CAD|CHF|JPY)/.test(b)) return /JPY/.test(b) ? 0.01 : 0.0001;
    if (/XAU|GOLD|^GC=F/.test(b)) return 0.1;
    if (/XAG|SILVER|^SI=F|^CL=F|^BZ=F|OIL|WTI|BRENT|^NG=F|NATGAS/.test(b)) return 0.01;
    if (/^\^|SP500|SPX|NAS|NDX|US30|DJI|DAX|DE30|UK100|JP225|NIKKEI|US500|USTEC/.test(b)) return 1;
    if (/^Y:/.test(sym) || /^HL:xyz:/.test(sym)) return 0.01;   // stocks / ETFs
    px = Math.abs(+px || 0); return px >= 1000 ? 1 : px >= 10 ? 0.01 : px >= 1 ? 0.001 : px >= 0.01 ? 0.00001 : 0.0000001;
  },
  atr(rows, n, upto){ upto = upto == null ? rows.length - 1 : upto; n = Math.min(n || 14, upto); if (n < 1) return 0; let s = 0;
    for (let i = upto - n + 1; i <= upto; i++) s += Math.max(rows[i].h - rows[i].l, Math.abs(rows[i].h - rows[i-1].c), Math.abs(rows[i].l - rows[i-1].c)); return s/n; },
  ema(vals, span){ const a = 2/(span + 1); let e = vals[0]; return vals.map(v => (e = a*v + (1 - a)*e)); },
  // bias of one timeframe, the same rule as modules/mtf.py tf_state: last two swing highs / lows (fractal k=3) + side of the 50-EMA
  bias(rows){
    if (!rows || rows.length < 60) return {available:false};
    const k = 3, hs = [], ls = []; for (let i = k; i < rows.length - k; i++){ let H = true, L = true; for (let j = i - k; j <= i + k; j++){ if (j === i) continue; if (rows[j].h >= rows[i].h) H = false; if (rows[j].l <= rows[i].l) L = false; } if (H) hs.push(rows[i].h); if (L) ls.push(rows[i].l); }
    const h2 = hs.slice(-2), l2 = ls.slice(-2); let trend = "range";
    if (h2.length === 2 && l2.length === 2){ if (h2[1] > h2[0] && l2[1] > l2[0]) trend = "up"; else if (h2[1] < h2[0] && l2[1] < l2[0]) trend = "down"; }
    const e = this.ema(rows.map(r => r.c), 50), px = rows[rows.length-1].c, side = px > e[e.length-1] ? "above" : "below";
    const sc = (trend === "up" ? 1 : trend === "down" ? -1 : 0) + (side === "above" ? 1 : -1);
    return {available:true, trend, ema:side, bias: sc > 0 ? "bull" : sc < 0 ? "bear" : "neutral", strength:Math.abs(sc)};
  },
  /* walk-forward bounce events: at bar i, levels = pivots CONFIRMED before i (pivot j is known at j+k). A long event = the bar's low
     touches a level from above (within tol) and the bar closes back above it; short = mirror. From that close we follow up to `hold`
     bars: mfe = best move in our favour BEFORE the stop (level -/+ stopAtr*ATR) is hit; a bar that touches the stop ends the event and
     its high / low is not counted (conservative). -> [{i, side, entry, stop, risk, mfe, stopped}] */
  events(rows, opt){
    opt = Object.assign({k:3, hold:16, stopAtr:0.6, tolAtr:0.35, start:30}, opt || {}); const n = rows.length, k = opt.k, out = [], piv = [];
    if (n < opt.start + 10) return out; let nextPiv = k, lastEv = -99;
    for (let i = opt.start; i < n - 1; i++){
      for (; nextPiv <= i - k - 1; nextPiv++){ const j = nextPiv; if (j < k || j + k >= n) continue; let H = true, L = true;
        for (let q = j - k; q <= j + k; q++){ if (q === j) continue; if (rows[q].h >= rows[j].h) H = false; if (rows[q].l <= rows[j].l) L = false; }
        if (H) piv.push(rows[j].h); if (L) piv.push(rows[j].l); }
      if (!piv.length || i - lastEv < 3) continue;
      const a = this.atr(rows, 14, i); if (!(a > 0)) continue; const tol = Math.max(a*opt.tolAtr, rows[i].c*0.0005), r = rows[i], p0 = rows[i-1];
      let best = null;
      for (const L of piv){
        if (p0.l > L + tol && r.l <= L + tol && r.l >= L - tol*2 && r.c > L){ const d = Math.abs(r.l - L); if (!best || d < best.d) best = {d, side:1, L}; }
        if (p0.h < L - tol && r.h >= L - tol && r.h <= L + tol*2 && r.c < L){ const d = Math.abs(r.h - L); if (!best || d < best.d) best = {d, side:-1, L}; }
      }
      if (!best) continue;
      const s = best.side, entry = r.c, stop = best.L - s*a*opt.stopAtr, risk = Math.abs(entry - stop); if (!(risk > 0)) continue;
      let mfe = 0, stopped = false;
      for (let q = i + 1; q < Math.min(n, i + 1 + opt.hold); q++){ const c = rows[q];
        if (s > 0 ? c.l <= stop : c.h >= stop){ stopped = true; break; }
        mfe = Math.max(mfe, s > 0 ? c.h - entry : entry - c.l); }
      out.push({i, side:s, level:best.L, entry, stop, risk, mfe, stopped}); lastEv = i;
    }
    return out;
  },
  // stats of those events for a target distance (price units): hit = the move reached the target before the stop
  stats(ev, target){
    const n = ev.length; if (!n) return {n:0};
    const m = ev.map(e => e.mfe).sort((a, b) => a - b), q = p => m[Math.min(n - 1, Math.floor(p*(n - 1)))];
    const hit = target > 0 ? ev.filter(e => e.mfe >= target).length : null;
    return {n, median:q(0.5), p25:q(0.25), p75:q(0.75), hit, hitPct: hit == null ? null : hit/n, medRisk: ev.map(e => e.risk).sort((a, b) => a - b)[Math.floor((n - 1)/2)]};
  },
  // a round number of points near x (for the Auto target): 1-2-2.5-5 steps
  nicePts(x){ if (!(x > 0)) return 0; const p = Math.pow(10, Math.floor(Math.log10(x))), f = x/p; return (f < 1.5 ? 1 : f < 2.25 ? 2 : f < 3.5 ? 2.5 : f < 7.5 ? 5 : 10)*p; },
  // a rejection candle at the level on the entry timeframe: the last CLOSED bar has a wick >= 45% of its range toward the level and closes in our favour
  rejection(rows, side){ if (!rows || rows.length < 3) return false; const c = rows[rows.length - 2], rg = c.h - c.l; if (!(rg > 0)) return false;
    return side > 0 ? (Math.min(c.o, c.c) - c.l)/rg >= 0.45 && c.c >= c.o - rg*0.1 : (c.h - Math.max(c.o, c.c))/rg >= 0.45 && c.c <= c.o + rg*0.1; },
  /* live candidates for one symbol + style. setupRows: candles of the setup tf; levels: SR.compute(setupRows); biasRows: higher tf; entryRows: lower tf (optional).
     targetPts: 0 = Auto. -> [{side, level, touches, entry, stop, tps, now, pts, ps, st, bias, rej, score, max, why[]}] */
  candidates(sym, setupRows, levels, biasRows, entryRows, o){
    o = Object.assign({targetPts:0, ps:0, hold:16, zoneAtr:0.5, nearAtr:1.5, stopAtr:0.6}, o || {});
    const n = setupRows ? setupRows.length : 0; if (n < 60 || !levels || !levels.length) return [];
    const px = setupRows[n-1].c, a = this.atr(setupRows, 14); if (!(a > 0)) return [];
    const ps = o.ps > 0 ? o.ps : this.pointSize(sym, px), ev = this.events(setupRows, {hold:o.hold, stopAtr:o.stopAtr}), b = this.bias(biasRows);
    const autoPts = Math.max(1, this.nicePts((this.stats(ev, 0).median || a)/ps));
    const tPts = o.targetPts > 0 ? o.targetPts : autoPts, T_ = tPts*ps, st = this.stats(ev, T_), out = [];
    const sideStats = s => this.stats(ev.filter(e => e.side === s), T_);
    [["S", 1], ["R", -1]].forEach(([kind, s]) => {
      const lv = levels.filter(x => x.kind === kind).sort((x, y) => Math.abs(x.p - px) - Math.abs(y.p - px))[0]; if (!lv) return;
      const dist = s > 0 ? px - lv.p : lv.p - px; if (dist < -a*0.25 || dist > a*o.nearAtr) return;   // broken through, or too far away
      const now = dist <= a*o.zoneAtr, entry = now ? px : lv.p + s*a*0.15, stop = lv.p - s*a*o.stopAtr, risk = Math.abs(entry - stop); if (!(risk > 0)) return;
      const opp = levels.filter(x => x.kind === (s > 0 ? "R" : "S") && s*(x.p - entry) > T_*1.2).sort((x, y) => Math.abs(x.p - entry) - Math.abs(y.p - entry))[0];
      const tps = [entry + s*T_, opp ? opp.p - s*a*0.1 : entry + s*T_*1.6];
      const rr = T_/risk, ss = sideStats(s), rej = this.rejection(entryRows, s), want = s > 0 ? "bull" : "bear";
      const agree = b.available ? (b.bias === want ? 1 : b.bias === "neutral" ? 0 : -1) : 0, why = [];
      let score = 0;
      if (lv.touches >= 3){ score++; why.push("level touched "+lv.touches+"x"); }
      if (now){ score++; why.push("price is at the zone now"); } else why.push("limit order at the zone");
      if (agree > 0){ score++; why.push("higher timeframe agrees ("+b.bias+")"); } else if (agree < 0) why.push("COUNTER-TREND: higher timeframe is "+b.bias);
      if (st.n >= 10 && st.hitPct >= 0.5){ score++; why.push("target reached in "+Math.round(st.hitPct*100)+"% of "+st.n+" past bounces"); }
      if (rr >= 1.5){ score++; why.push("R:R "+rr.toFixed(1)); }
      if (rej){ score++; why.push("rejection candle on the entry timeframe"); }
      out.push({side:s, level:lv.p, touches:lv.touches, entry, stop, tps, now, pts:tPts, autoPts, ps, rr, st, sideSt:ss, bias:b, agree, rej, score, max:6, why, atr:a});
    });
    return out;
  }
};
/* TCLASS-END */
const TC = {
  res:{}, busy:false, subs:new Set(), log:[], next:{},
  SCHOOLS: {
    bounce: null,   // the engine above
    elliott: ["موجة 3","اليوت"],
    ict: ["MSB-OB","OB","FVG","OTE","بريكر","يونيكورن","يهوذا","سيولة","CISD","Model 2022","CRT","Power of 3","KZ سنايبر","جلسات AMD","زومبي","SMT"],
    classic: ["اختراق","دعم/مقاومة","فيبو","VWAP","متوسطات","كسر ترند","دايفرجنس RSI","دايفرجنس MACD","Donchian","SMA 10/40","تيرتل 55","نطاق الافتتاح"]
  },
  styleOf(ttype){ return TCE.STYLES[ttype] ? ttype : "Day Trade"; },
  // card in the scanner's shape, so Alerts / Setup Card / Ready / Signals / strip / journal all read it unchanged
  card(sym, style, c, spark){
    const S = TCE.STYLES[style], long_ = c.side > 0, tag = Lg("Bounce ", "ارتداد ")+c.pts, ar = [
      (long_ ? "شراء من دعم " : "بيع من مقاومة ")+fmtP(c.level)+" (اتلمس "+c.touches+" مرات)",
      "الهدف "+c.pts+" نقطة ("+fmtP(c.tps[0])+") · الستوب "+fmtP(c.stop)+" · R:R "+c.rr.toFixed(1),
      c.st.n ? "تاريخيًا على "+S.setup+": متوسط الارتداد ~"+Math.round(c.st.median/c.ps)+" نقطة، والهدف اتضرب "+(c.st.hitPct == null ? "–" : Math.round(c.st.hitPct*100)+"%")+" من "+c.st.n+" مرة"+(c.st.n < 30 ? " (أقل من 30 = مش دليل)" : "") : "مفيش ارتدادات كفاية في التاريخ للقياس",
      "ترابط الفريمات: اتجاه "+S.bias+" ← إعداد "+S.setup+" ← دخول "+S.entry+": "+(c.agree > 0 ? "متوافق" : c.agree < 0 ? "عكس الاتجاه (حذر)" : "محايد"),
      c.now ? "السعر عند المنطقة دلوقتي" : "أمر معلّق عند المنطقة (السعر لسه ماوصلش)"];
    return {symbol:sym, direction:long_ ? "bullish" : "bearish", ttype:style, tfk:S.tfk, tfc:S.entry, score:c.score, max:c.max, src:"tclass",
      plan:{entry:c.entry, stop:c.stop, tps:c.tps}, zones:[{lo:Math.min(c.level, c.level - c.side*c.atr*0.15), hi:Math.max(c.level, c.level + c.side*c.atr*0.5), dir:long_ ? "bullish" : "bearish"}],
      tags:[[tag, "#f0b90b", "#000", "S/R bounce: "+c.why.join(" · ")], ["دعم/مقاومة", "#4aa3ff", "#000", "Support / resistance zone (pivot cluster)"]],
      spark, ana:{sig:ar}, why:c.why, level:c.level, touches:c.touches, pts:c.pts, ps:c.ps, hist:c.st};
  },
  /* Harmonic school: harmFind() (the chart's own detector, Gartley / Bat / Butterfly / Crab / Cypher, same rules as modules/harmonic.py) on the
     SAME setup-timeframe candles (no extra request). Kept: a completed pattern whose D is <= 12 bars old and not finished (stop / last target
     not touched), or a forming one (X-A-B-C, price heading for the PRZ). Plan = the detector's plan (entry D / PRZ mid, its stop, TP 0.382 / 0.618 AD). */
  harm(sym, style, rows, biasRows, spark, opt){
    if (typeof harmFind !== "function" || !rows || rows.length < 60) return [];
    const n = rows.length, px = rows[n-1].c, a = TCE.atr(rows, 14), b = TCE.bias(biasRows), ps = TCE.pointSize(sym, px), S = TCE.STYLES[style], out = [];
    harmFind(rows, 4).forEach(h => {
      const pl = h.plan, s = h.dir === "bull" ? 1 : -1, dI = h.pts[h.pts.length - 1].i;
      if (h.state === "done" && (n - 1 - dI > 12 || harmHit(pl, rows, dI))) return;
      const entry = pl.entry, stop = pl.stop, tps = pl.tps.slice(0, 2); if (!(Math.abs(entry - stop) > 0)) return;
      const near = Math.abs(px - entry) <= a*0.5, agree = b.available ? (b.bias === (s > 0 ? "bull" : "bear") ? 1 : b.bias === "neutral" ? 0 : -1) : 0, rr = Math.abs(tps[0] - entry)/Math.abs(entry - stop);
      const rej = TCE.rejection(rows, s), why = [], pts = Math.round(Math.abs(tps[0] - entry)/ps); let score = 0;
      if (h.state === "done"){ score++; why.push(h.name+" completed (D printed)"); } else why.push(h.name+" forming: limit order in the PRZ");
      if (near){ score++; why.push("price is at the zone now"); }
      if (agree > 0){ score++; why.push("higher timeframe agrees ("+b.bias+")"); } else if (agree < 0) why.push("COUNTER-TREND: higher timeframe is "+b.bias);
      if (rr >= 1.5){ score++; why.push("R:R "+rr.toFixed(1)); }
      if (rej){ score++; why.push("rejection candle at D"); }
      if (entry >= h.prz.lo - h.prz.pad - a*0.1 && entry <= h.prz.hi + h.prz.pad + a*0.1){ score++; why.push("D inside the PRZ"); }
      const long_ = s > 0, ar = [(long_ ? "شراء" : "بيع")+" من نموذج "+h.name+(h.state === "done" ? " مكتمل" : " بيتكوّن (أمر معلّق في منطقة الانعكاس PRZ)"),
        "الدخول "+fmtP(entry)+" · الستوب "+fmtP(stop)+" · الهدف "+fmtP(tps[0])+" ("+pts+" نقطة) · R:R "+rr.toFixed(1),
        "ترابط الفريمات: اتجاه "+S.bias+" ← إعداد "+S.setup+" ← دخول "+S.entry+": "+(agree > 0 ? "متوافق" : agree < 0 ? "عكس الاتجاه (حذر)" : "محايد"),
        "مفيش نسبة نجاح تاريخية للهارمونيك هنا لسه؛ السجل الفعلي في الجورنال (أقل من 30 = مش دليل)"];
      out.push({symbol:sym, direction:long_ ? "bullish" : "bearish", ttype:style, tfk:S.tfk, tfc:S.entry, score, max:6, src:"tclass", school:"harmonic",
        plan:{entry, stop, tps}, zones:[{lo:h.prz.lo, hi:h.prz.hi, dir:long_ ? "bullish" : "bearish"}],
        tags:[[Lg("Harmonic ","هارمونيك ")+h.name, "#b57cff", "#000", "Harmonic "+h.name+": "+why.join(" · ")]], spark, ana:{sig:ar}, why, pts, ps, level:entry, touches:0, hist:null});
    });
    return out;
  },
  async scanSym(sym, style, opt){
    const S = TCE.STYLES[style];
    const [setup, bias] = await Promise.all([candlesTf(sym, S.setup, true, S.want), candlesTf(sym, S.bias, true, 120).catch(() => [])]);
    const lv = SR.compute(setup); let cs = TCE.candidates(sym, setup, lv, bias, null, Object.assign({hold:S.hold}, opt));
    if (cs.length){ const en = await candlesTf(sym, S.entry, true, 60).catch(() => null); if (en) cs = TCE.candidates(sym, setup, lv, bias, en, Object.assign({hold:S.hold}, opt)); }
    const spark = setup.slice(-40).map(r => r.c), cards = cs.map(c => Object.assign(this.card(sym, style, c, spark), {school:"bounce"}));
    try { this.harm(sym, style, setup, bias, spark, opt).forEach(c => cards.push(c)); } catch(e){}
    return {t:Date.now(), n:setup.length, cards, raw:cs, bias:TCE.bias(bias)};
  },
  // one pass over the symbols of one style (sequential, small pause between symbols: OKX / Hyperliquid limits)
  async run(style, syms, opt, force){
    if (this.busy) return; const key = style; if (!force && Date.now() < (this.next[key] || 0)) return; this.busy = true;
    try {
      for (const s of syms){
        try { this.res[style+"|"+s] = await this.scanSym(s, style, opt); }
        catch(e){ this.res[style+"|"+s] = {t:Date.now(), err:String(e && e.message || e), cards:[]}; if (isRL(e)) break; }
        this.subs.forEach(f => f()); await new Promise(r => setTimeout(r, 350));
      }
      this.next[key] = Date.now() + TCE.STYLES[style].every;
    } finally { this.busy = false; this.subs.forEach(f => f()); }
  },
  // strong + at the zone now -> Alerts (that feeds the Setup Card, the strip, Ready, Signals and the journal); never replaces a stronger card of the same symbol / side / type
  push(cards, minPct){
    cards.forEach(c => { if (!c.plan || !c.why || 100*c.score/c.max < minPct || !(c.why.includes("price is at the zone now"))) return;
      const g = c.symbol+"|"+c.direction+"|"+c.ttype, old = Alerts.list.find(a => a.card && a.card.symbol+"|"+a.card.direction+"|"+a.card.ttype === g);
      if (old && old.card.src !== "tclass" && old.card.score/Math.max(1, old.card.max) >= c.score/c.max) return;
      const id = "tc|"+g+"|"+c.plan.stop.toPrecision(6), long_ = c.direction === "bullish";
      Alerts.add(id, "scan", c.symbol, c.symbol+" · "+(long_ ? "Long" : "Short")+" · "+ttTxt(c.ttype)+" · "+Lg("bounce ","ارتداد ")+c.pts+Lg(" pts"," نقطة"), long_ ? "#0ecb81" : "#f6465d", c); });
  },
  // forward record of this widget's trades from the journal (tag "Bounce N" / "ارتداد N"): the real test, per style
  record(style){ const L_ = (Journal.list || []).filter(t => (t.tags || []).some(g => /^(Bounce|ارتداد) \d/.test(g)) && (!style || t.ttype === style));
    const done = L_.filter(t => t.status === "tp" || t.status === "sl"), w = done.filter(t => t.status === "tp").length, R = done.reduce((s, t) => s + (t.r || 0), 0);
    return {n:L_.length, open:L_.filter(t => t.status === "open").length, done:done.length, win:w, avgR: done.length ? R/done.length : null}; }
};
Panel.prototype.build_tclass = function(){
  const S = this.state.tc = Object.assign({style:"Scalp", tgt:0, school:"bounce", uni:"chart", push:true, min:66, ps:{}}, this.state.tc || {});
  const tb = el("div","tb"), mk = (opts, key, num) => { const s = el("select"); opts.forEach(([v, l]) => s.append(Object.assign(el("option"), {value:String(v), textContent:l}))); s.value = String(S[key]);
    s.onpointerdown = e => e.stopPropagation(); s.onchange = () => { S[key] = num ? +s.value : s.value; Ws.save(); if (key !== "school") go(true); else draw(); }; return s; };
  const stSel = mk([["Scalp",Lg("Scalp","سكالب")],["Day Trade",Lg("Day trade","داي تريد")],["Swing",Lg("Swing","سوينج")],["Position",Lg("Position","بوزشن")]], "style");
  const tgSel = mk(TCE.TARGETS.map(v => [v, v ? v+Lg(" pts"," نقطة") : Lg("Auto (measured)","تلقائي (مقاس)")]), "tgt", true);
  const scSel = mk([["bounce",Lg("S/R bounce","ارتداد دعم/مقاومة")],["harmonic",Lg("Harmonic","هارمونيك")],["elliott",Lg("Elliott (scanner)","إليوت (السكانر)")],["ict",Lg("ICT / SMC (scanner)","ICT / SMC (السكانر)")],["classic",Lg("Classic (scanner)","كلاسيك (السكانر)")],["all",Lg("All schools","كل المدارس")]], "school");
  const unSel = mk([["chart",Lg("Chart symbol","رمز الشارت")],["watch",Lg("Watchlist (top 10)","الووتش ليست (أول 10)")]], "uni");
  const rf = el("button", null, "⟳"), pu = el("label"), pc = el("input"); rf.title = Lg("Scan now","افحص دلوقتي"); pc.type = "checkbox"; pc.checked = S.push !== false;
  pu.append(pc, document.createTextNode(Lg(" → Alerts"," ← التنبيهات"))); pu.title = Lg("Send strong trades (at the zone now, strength >= 4 of 6) to Alerts, the Setup Card and the top strip","ابعت الصفقات القوية (السعر عند المنطقة، قوة 4 من 6+) للتنبيهات وكارت الصفقة والشريط اللي فوق");
  [rf, pc].forEach(x => x.onpointerdown = e => e.stopPropagation()); pc.onchange = () => { S.push = pc.checked; Ws.save(); };
  tb.append(stSel, tgSel, scSel, unSel, rf, pu);
  const info = el("div","m"), box = el("div","rdy"), foot = el("div","m"); info.style.cssText = "font-size:11px;padding:2px 4px"; foot.style.cssText = "font-size:10px;padding:4px;line-height:1.4";
  this.body.append(tb, info, box, foot); this.body.style.overflow = "auto";
  const chartSym = () => { const ch = Ws.panels.find(p => p.type === "chart"); return ch ? ch.state.sym : SYMS[0]; };
  const syms = () => S.uni === "watch" ? SYMS.slice(0, 10) : [chartSym()];
  const own = () => S.school === "bounce" || S.school === "harmonic" || S.school === "all";
  const go = force => { if (own()) TC.run(S.style, syms(), {targetPts:S.tgt}, force); draw(); };
  rf.onclick = () => go(true);
  const draw = () => {
    const St = TCE.STYLES[S.style], fr = TC.record(S.style);
    info.innerHTML = '<b style="color:#f0b90b">'+esc(ttTxt(S.style))+'</b> · '+esc(Lg("bias","اتجاه"))+' <b>'+St.bias+'</b> → '+esc(Lg("setup","إعداد"))+' <b>'+St.setup+'</b> → '+esc(Lg("entry","دخول"))+' <b>'+St.entry+'</b>'
      +(TC.busy ? ' · <span style="color:#4aa3ff">'+esc(Lg("scanning…","بيفحص…"))+'</span>' : '');
    let rows = [];
    if (own()) syms().forEach(s => { const r = TC.res[S.style+"|"+s]; if (r) (r.cards || []).forEach(c => { if (S.school === "all" || (c.school || "bounce") === S.school) rows.push(c); }); });
    if (S.school !== "bounce" && S.school !== "harmonic"){ const want = S.school === "all" ? null : TC.SCHOOLS[S.school];
      readyList().filter(e => e.ttype === S.style && e.src !== "tclass" && (!want || (e.tags || []).some(t => want.includes(t[0])))).forEach(e => rows.push(e)); }
    rows.sort((a, b) => (b.score/b.max - a.score/a.max));
    const errs = syms().map(s => TC.res[S.style+"|"+s]).filter(r => r && r.err);
    if (!rows.length){ box.innerHTML = '<div class="err" style="color:#848e9c">'+esc(TC.busy ? Lg("scanning…","بيفحص…") : errs.length ? errs[0].err : (S.school === "harmonic" ? Lg("No active harmonic pattern on these symbols for this style.","مفيش نموذج هارمونيك شغال على الرموز دي للنوع ده.") : S.school === "bounce" ? Lg("No symbol is at a support / resistance zone right now for this style.","مفيش رمز عند منطقة دعم/مقاومة دلوقتي للنوع ده.") : Lg("No scanner setup of this school + style right now.","مفيش إعداد من المدرسة دي والنوع ده في السكانر دلوقتي.")))+'</div>'; }
    else {
      let h = '<table class="rdt"><tr><th>'+esc(T("symbol"))+'</th><th></th><th>'+esc(Lg("Level","المستوى"))+'</th><th>'+esc(Lg("Entry","الدخول"))+'</th><th>'+esc(T("stop"))+'</th><th>'+esc(Lg("Target","الهدف"))+'</th><th>R:R</th><th title="'+esc(Lg("Past bounces from a level on this symbol + setup timeframe (walk-forward): how often the move reached the target before the stop, out of n. Under 30 = not evidence.","الارتدادات اللي فاتت من مستوى على نفس الرمز والفريم (من غير بيانات مستقبلية): كام مرة الحركة وصلت للهدف قبل الستوب من n. أقل من 30 = مش دليل."))+'">'+esc(Lg("History","التاريخ"))+'</th><th>'+esc(T("rdStr"))+'</th></tr>';
      rows.slice(0, 60).forEach((e, i) => { const long_ = e.direction === "bullish", pct = Math.round(100*e.score/Math.max(1, e.max)), col = pct >= 67 ? "#0ecb81" : pct >= 50 ? "#f0b90b" : "#848e9c", pl = e.plan;
        const ps = e.ps || TCE.pointSize(e.symbol, pl.entry), pts = e.pts || Math.round(Math.abs(pl.tps[0] - pl.entry)/ps), r0 = Math.abs(pl.entry - pl.stop), hs = e.hist;
        h += '<tr data-i="'+i+'" style="cursor:pointer" title="'+esc((e.ana && e.ana.sig ? e.ana.sig : (e.tags || []).map(t => "["+t[0]+"] "+(t[3] || ""))).join("\n"))+'"><td><b>'+esc(e.symbol.replace(/-(USDT|USDC|SWAP)$/,""))+'</b> <span class="m">'+esc(e.tfc || e.tfk || "")+'</span></td>'
          +'<td style="color:'+(long_ ? "#0ecb81" : "#f6465d")+';font-weight:700">'+(long_ ? "▲ "+esc(T("long")) : "▼ "+esc(T("short")))+'</td>'
          +'<td class="m">'+(e.school === "harmonic" ? esc(tagTxt(e.tags[0][0])) : e.src === "tclass" ? esc(fmtP(e.level))+' <span title="'+esc(Lg("touches","لمسات"))+'">×'+(e.touches || "")+'</span>' : esc((e.tags || []).slice(0, 2).map(t => tagTxt(t[0])).join(" · ")))+'</td>'
          +'<td>'+fmtP(pl.entry)+'</td><td style="color:#f6465d">'+fmtP(pl.stop)+'</td><td style="color:#0ecb81">'+fmtP(pl.tps[0])+' <span class="m">('+pts+Lg(" pts"," ن")+')</span></td><td>'+(r0 ? (Math.abs(pl.tps[0] - pl.entry)/r0).toFixed(1) : "–")+'</td>'
          +'<td class="m">'+(hs && hs.n ? (hs.hitPct == null ? "–" : Math.round(hs.hitPct*100)+"%")+' n'+hs.n+(hs.n < 30 ? '*' : '')+' · ~'+Math.round(hs.median/ps)+Lg(" pts"," ن") : "–")+'</td>'
          +'<td><span class="bar"><i style="width:'+pct+'%;background:'+col+'"></i></span> '+pct+'%</td></tr>'; });
      box.innerHTML = h+'</table>';
      box.querySelectorAll("tr[data-i]").forEach(tr => tr.onclick = () => { const e = rows[+tr.dataset.i]; if (e) Ws.showOnChart(Object.assign({tfc: TFC_ALL[e.tfk] || "1H"}, e)); });
    }
    foot.innerHTML = esc(Lg("Forward record of these bounce trades (journal, ","السجل الفعلي لصفقات الارتداد دي (الجورنال، "))+esc(ttTxt(S.style))+'): <b>'+fr.done+'</b> '+esc(Lg("closed","مقفولة"))+' · '+fr.win+' TP · '+(fr.avgR == null ? "–" : (fr.avgR >= 0 ? "+" : "")+fr.avgR.toFixed(2)+"R")+' · '+fr.open+' '+esc(Lg("open","مفتوحة"))
      +(fr.done < 30 ? ' · <b style="color:#f0b90b">'+esc(Lg("under 30 = not evidence","أقل من 30 = مش دليل"))+'</b>' : '')
      +'<br>'+esc(Lg("* n under 30. Point size: forex = pip, gold 0.1, silver/oil/stocks 0.01, indices 1, crypto by price. The bounce size is measured on past candles of this symbol (no future data); it is information, not a promise. Harmonic = the chart's own detector on the setup timeframe; no historical hit rate for it yet.",
        "* n أقل من 30. حجم النقطة: الفوركس = بيب، الدهب 0.1، الفضة/البترول/الأسهم 0.01، المؤشرات 1، الكريبتو حسب السعر. حجم الارتداد مقاس على شموع الرمز اللي فاتت (من غير بيانات مستقبلية)؛ معلومة مش وعد. الهارمونيك = نفس كاشف الشارت على فريم الإعداد؛ لسه مفيش نسبة نجاح تاريخية ليه."));
    if (S.push !== false){ const all = []; Object.keys(TC.res).forEach(k => (TC.res[k].cards || []).forEach(c => all.push(c))); TC.push(all, S.min || 66); }
  };
  draw(); go(false); const iv = setInterval(() => go(false), 30000);
  TC.subs.add(draw); Alerts.subs.add(draw);
  this.unwatch = () => { clearInterval(iv); TC.subs.delete(draw); Alerts.subs.delete(draw); };
};
