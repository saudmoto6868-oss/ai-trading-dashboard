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
  /* ---- indicators + session levels + user rules (pure; used by the VWAP / MA / session schools and "My strategies") ---- */
  sma(v, n){ const o = new Array(v.length).fill(NaN); let s = 0; for (let i = 0; i < v.length; i++){ s += v[i]; if (i >= n) s -= v[i-n]; if (i >= n - 1) o[i] = s/n; } return o; },
  rsi(v, n){ n = n || 14; const o = new Array(v.length).fill(NaN); let g = 0, l = 0; for (let i = 1; i < v.length; i++){ const d = v[i] - v[i-1], up = Math.max(d, 0), dn = Math.max(-d, 0);
      if (i <= n){ g += up; l += dn; if (i === n){ g /= n; l /= n; o[i] = l ? 100 - 100/(1 + g/l) : 100; } } else { g = (g*(n-1) + up)/n; l = (l*(n-1) + dn)/n; o[i] = l ? 100 - 100/(1 + g/l) : 100; } } return o; },
  // VWAP anchored at each UTC day start (crypto / perpetuals trade 24h) with +-1 / +-2 standard-deviation bands; no volume -> equal weights
  // anchor "rth" = the US cash open 09:30 New York (indices / stocks): the session id is the New York date of (time - 9h30)
  nyOff(t){ const k = Math.floor(t/864e5); this._ny = this._ny || {}; if (this._ny[k] != null) return this._ny[k];
    let off = -5*3600e3; try { const f = new Intl.DateTimeFormat("en-US", {timeZone:"America/New_York", hour:"2-digit", hour12:false}).formatToParts(new Date(k*864e5 + 12*3600e3)), h = +f.find(x => x.type === "hour").value % 24; off = (h - 12)*3600e3; } catch(e){}
    return (this._ny[k] = off); },
  sessId(t, anchor){ return anchor === "rth" ? Math.floor((t + this.nyOff(t) - 9.5*3600e3)/864e5) : Math.floor(t/864e5); },
  vwapSession(rows, anchor){ const n = rows.length, vw = new Array(n), sd = new Array(n); let day = null, pv = 0, vv = 0, p2 = 0;
    for (let i = 0; i < n; i++){ const r = rows[i], d = this.sessId(r.t || 0, anchor); if (d !== day){ day = d; pv = 0; vv = 0; p2 = 0; }
      const tp = (r.h + r.l + r.c)/3, v = r.v > 0 ? r.v : 1; pv += tp*v; vv += v; p2 += tp*tp*v; vw[i] = pv/vv; sd[i] = Math.sqrt(Math.max(0, p2/vv - vw[i]*vw[i])); }
    return {vw, sd}; },
  // previous UTC day high / low, today's open, this week's open (Monday 00:00 UTC), from intraday rows -> {pdh, pdl, dopen, wopen} (null when not enough days)
  dayLevels(rows){ const n = rows.length; if (!n || !rows[0].t) return {}; const days = new Map(); rows.forEach(r => { const d = Math.floor(r.t/864e5), x = days.get(d); if (!x) days.set(d, {o:r.o, h:r.h, l:r.l}); else { x.h = Math.max(x.h, r.h); x.l = Math.min(x.l, r.l); } });
    const ks = [...days.keys()].sort((a, b) => a - b), today = ks[ks.length-1], prev = ks.length > 1 ? days.get(ks[ks.length-2]) : null, wk = d => Math.floor((d + 3)/7);   // epoch day 0 = Thursday -> +3 makes weeks start on Monday
    const w0 = ks.find(d => wk(d) === wk(today)); return {pdh:prev ? prev.h : null, pdl:prev ? prev.l : null, dopen:days.get(today).o, wopen:w0 != null ? days.get(w0).o : null}; },
  indicators(rows, anchor){ const c = rows.map(r => r.c), v = this.vwapSession(rows, anchor), L = this.dayLevels(rows);
    const I = {close:c, open:rows.map(r => r.o), high:rows.map(r => r.h), low:rows.map(r => r.l), ema9:this.ema(c, 9), ema21:this.ema(c, 21), ema50:this.ema(c, 50), ema200:this.ema(c, 200),
      sma20:this.sma(c, 20), sma50:this.sma(c, 50), rsi14:this.rsi(c, 14), vwap:v.vw, vwapU1:v.vw.map((x, i) => x + v.sd[i]), vwapL1:v.vw.map((x, i) => x - v.sd[i]),
      vwapU2:v.vw.map((x, i) => x + 2*v.sd[i]), vwapL2:v.vw.map((x, i) => x - 2*v.sd[i])};
    ["pdh","pdl","dopen","wopen"].forEach(k => { I[k] = L[k] == null ? null : c.map(() => L[k]); }); return I; },
  RULE_SRC: ["close","open","high","low","ema9","ema21","ema50","ema200","sma20","sma50","vwap","vwapU1","vwapL1","vwapU2","vwapL2","rsi14","pdh","pdl","dopen","wopen"],
  // one user rule on the last closed state (index i): {a, op: ">" "<" "xa" (crosses above) "xb" (crosses below), b: indicator or "value", v: number, off: points added to b}
  rule(r, I, i, ps){ const get = (k, j) => k === "value" ? +r.v : (I[k] && I[k][j] != null ? I[k][j] : NaN), off = (+r.off || 0)*(ps || 1);
    const A = get(r.a, i), B = get(r.b, i) + off, A0 = get(r.a, i - 1), B0 = get(r.b, i - 1) + off; if (!(A === A) || !(B === B)) return false;
    return r.op === ">" ? A > B : r.op === "<" ? A < B : r.op === "xa" ? A0 <= B0 && A > B : r.op === "xb" ? A0 >= B0 && A < B : false; },
  rulesOk(rules, I, i, ps){ return !!(rules && rules.length) && rules.every(r => this.rule(r, I, i, ps)); },
  /* ---- deliberation (pure): every idea gets a case FOR, a case AGAINST, hard stops, a second look, then a verdict ---- */
  swings(rows, k){ k = k || 3; const out = []; for (let i = k; i < rows.length - k; i++){ let H = true, L = true; for (let j = i - k; j <= i + k; j++){ if (j === i) continue; if (rows[j].h >= rows[i].h) H = false; if (rows[j].l <= rows[i].l) L = false; } if (H) out.push({i, p:rows[i].h, k:"H"}); if (L) out.push({i, p:rows[i].l, k:"L"}); } return out; },
  // break of structure in the last `fresh` bars: a close beyond the newest confirmed swing high / low that no earlier close had broken.
  // BOS = with the previous swing trend, MSS (market structure shift) = against it. -> [{side, level, i, kind}]
  structure(rows, fresh){ fresh = fresh || 6; const n = rows.length, sw = this.swings(rows, 3), out = []; if (n < 40) return out;
    [["H", 1], ["L", -1]].forEach(([k, s]) => { const L = sw.filter(x => x.k === k); if (L.length < 2) return; const q = L[L.length - 1], prev = L[L.length - 2];
      let brk = -1; for (let i = q.i + 4; i < n; i++){ if (s > 0 ? rows[i].c > q.p : rows[i].c < q.p){ brk = i; break; } }
      if (brk < 0 || n - 1 - brk > fresh) return; const wasTrend = s > 0 ? q.p > prev.p : q.p < prev.p;
      out.push({side:s, level:q.p, i:brk, kind: wasTrend ? "BOS" : "MSS"}); });
    return out; },
  // volume profile nodes: POC, value-area edges and high-volume nodes (local peaks >= 1.3x the average bin) -> [{p, src}]
  vpNodes(vp){ if (!vp || !vp.bins) return []; const b = vp.bins, avg = b.reduce((a, x) => a + x, 0)/b.length, mid = i => vp.lo + (i + .5)*vp.st, out = [{p:vp.poc, src:"POC"}, {p:vp.vah, src:"VAH"}, {p:vp.val, src:"VAL"}];
    for (let i = 1; i < b.length - 1; i++) if (b[i] >= b[i-1] && b[i] >= b[i+1] && b[i] >= avg*1.3 && Math.abs(mid(i) - vp.poc) > vp.st*1.5) out.push({p:mid(i), src:"HVN"});
    return out; },
  // the first level of the OTHER side between the entry and the target (price must get through it first) -> {p, src} or null
  obstacle(entry, target, side, levels, atr){ let best = null;
    (levels || []).forEach(l => { const d = side*(l.p - entry); if (d > atr*0.25 && side*(target - l.p) > 0 && (!best || d < side*(best.p - entry))) best = l; }); return best; },
  /* idea = {det, side, entry, stop, tps:[t1, t2], now, level}; c = context (all numbers from the candles / journal, see TC.judgeAll).
     -> {pros:[[w, en, ar]], cons:[[w, en, ar]], vetoes:[[en, ar]], second:[[en, ar]], score, pct, verdict TAKE|WAIT|SKIP, plan, rr, pts} */
  judge(idea, c){
    const s = idea.side, pros = [], cons = [], vetoes = [], second = [], P = (w, en, ar) => pros.push([w, en, ar]), C = (w, en, ar) => cons.push([w, en, ar]);
    const entry = idea.entry, stop = idea.stop, risk = Math.abs(entry - stop) || 1e-12, tps = idea.tps.slice(), want = s > 0 ? "bull" : "bear", ps = c.ps || 1, pt = x => Math.round(Math.abs(x)/ps);
    // second look at the target: an opposite level before it -> cut the target just before that level, keep it only if R:R still >= 1.5
    const ob = this.obstacle(entry, tps[0], s, c.levels, c.atr); let blocked = false;
    if (ob){ const cut = ob.p - s*c.atr*0.1, rrCut = Math.abs(cut - entry)/risk;
      if (rrCut >= 1.5){ second.push(["Target cut from "+pt(tps[0] - entry)+" to "+pt(cut - entry)+" pts: "+ob.src+" at "+ob.p.toPrecision(6)+" stands in the way", "الهدف اتقص من "+pt(tps[0] - entry)+" لـ"+pt(cut - entry)+" نقطة: فيه "+ob.src+" عند "+ob.p.toPrecision(6)+" في السكة"]); tps[0] = cut; if (s*(tps[1] - cut) <= 0) tps[1] = ob.p + s*c.atr*0.3; }
      else { blocked = true; C(2, ob.src+" at "+ob.p.toPrecision(6)+" before the target; cutting the target leaves R:R "+rrCut.toFixed(1), "فيه "+ob.src+" عند "+ob.p.toPrecision(6)+" قبل الهدف؛ لو قصيت الهدف الـR:R يبقى "+rrCut.toFixed(1)); } }
    if (s*(tps[1] - tps[0]) <= 0) tps[1] = tps[0] + s*Math.abs(tps[0] - entry)*0.6;
    const rr = Math.abs(tps[0] - entry)/risk;
    // case FOR
    if (c.bias && c.bias.available && c.bias.bias === want) P(2, "Bias timeframe "+c.tf.bias+" agrees ("+c.bias.bias+")", "فريم الاتجاه "+c.tf.bias+" موافق ("+c.bias.bias+")");
    if (c.setupB && c.setupB.available && c.setupB.bias === want) P(1, "Setup timeframe "+c.tf.setup+" trend agrees", "ترند فريم الإعداد "+c.tf.setup+" موافق");
    if (c.trig) P(1.5, "Entry timeframe "+c.tf.entry+" trigger: "+c.trig, "إشارة على فريم الدخول "+c.tf.entry+": "+c.trig);
    if (c.confl && c.confl.length) P(Math.min(3, c.confl.length), "Other schools at the same zone: "+c.confl.join(", "), "مدارس تانية في نفس المنطقة: "+c.confl.join("، "));
    if (c.vpAt) P(1, "Volume-profile node at the entry ("+c.vpAt+")", "نقطة فوليوم بروفايل عند الدخول ("+c.vpAt+")");
    if (c.hist && c.hist.n >= 10 && c.hist.hitPct >= 0.55) P(1.5, "Past bounces here reached this target "+Math.round(c.hist.hitPct*100)+"% of "+c.hist.n, "الارتدادات اللي فاتت هنا وصلت للهدف ده "+Math.round(c.hist.hitPct*100)+"% من "+c.hist.n+" مرة");
    if (rr >= 2 && !blocked) P(1, "R:R "+rr.toFixed(1), "R:R "+rr.toFixed(1));
    if (c.jr && c.jr.done >= 10 && c.jr.avgR > 0) P(1, "This idea type is positive in your journal ("+c.jr.done+" trades, "+c.jr.avgR.toFixed(2)+"R)", "النوع ده كسبان في الجورنال بتاعك ("+c.jr.done+" صفقة، "+c.jr.avgR.toFixed(2)+"R)");
    if (c.scalp && c.ses && c.ses !== "off-KZ" && /KZ/.test(c.ses)) P(0.5, "Inside a kill zone ("+c.ses+")", "جوه كيل زون ("+c.ses+")");
    // case AGAINST
    if (c.bias && c.bias.available && c.bias.bias !== want && c.bias.bias !== "neutral") C(2.5, "Bias timeframe "+c.tf.bias+" is against ("+c.bias.bias+")", "فريم الاتجاه "+c.tf.bias+" ضدك ("+c.bias.bias+")");
    if (!c.bias || !c.bias.available) C(0.5, "No bias timeframe data ("+c.tf.bias+")", "مفيش بيانات لفريم الاتجاه ("+c.tf.bias+")");
    if (c.setupB && c.setupB.available && c.setupB.bias !== want && c.setupB.bias !== "neutral") C(1, "Setup timeframe trend is against", "ترند فريم الإعداد ضدك");
    if (!c.trig) C(0.5, "No trigger yet on the entry timeframe "+c.tf.entry, "لسه مفيش إشارة على فريم الدخول "+c.tf.entry);
    if (rr < 1.5) C(1.5, "R:R only "+rr.toFixed(1), "الـR:R "+rr.toFixed(1)+" بس");
    if (c.late) C(1.5, "Late: price already went "+Math.round(c.late*100)+"% of the way to the target", "متأخر: السعر مشي "+Math.round(c.late*100)+"% من المسافة للهدف");
    if (c.hist && c.hist.n >= 10 && c.hist.hitPct < 0.4) C(1.5, "Past bounces reached this target only "+Math.round(c.hist.hitPct*100)+"% of "+c.hist.n, "الارتدادات اللي فاتت وصلت للهدف ده "+Math.round(c.hist.hitPct*100)+"% بس من "+c.hist.n);
    if (c.hist && c.hist.n >= 10 && c.hist.p75 > 0 && Math.abs(tps[0] - entry) > c.hist.p75) C(1, "Target is bigger than 3 of 4 past moves on "+c.tf.setup+" ("+pt(c.hist.p75)+" pts)", "الهدف أكبر من 3 من كل 4 حركات فاتت على "+c.tf.setup+" ("+pt(c.hist.p75)+" نقطة)");
    if (!c.hist || c.hist.n < 10) C(0.5, "Too little history to measure ("+((c.hist && c.hist.n) || 0)+" past cases)", "تاريخ قليل للقياس ("+((c.hist && c.hist.n) || 0)+" حالة)");
    if (c.regime === "chop") C(1, "Market regime: chop (moves die quickly)", "حالة السوق: تذبذب (الحركات بتموت بسرعة)");
    if (c.regime === "hivol" || c.regime === "crash") C(1, "Market regime: "+c.regime+" (stops get hit by noise)", "حالة السوق: "+c.regime+" (الستوب بيتضرب من الضوضاء)");
    if (c.classOpen >= 2) C(1, c.classOpen+" open trades already in the same class and direction", "فيه "+c.classOpen+" صفقات مفتوحة في نفس الفئة والاتجاه");
    if (c.jr && c.jr.done >= 10 && c.jr.avgR < 0) C(1.5, "This idea type loses in your journal ("+c.jr.done+" trades, "+c.jr.avgR.toFixed(2)+"R)", "النوع ده خسران في الجورنال بتاعك ("+c.jr.done+" صفقة، "+c.jr.avgR.toFixed(2)+"R)");
    if (c.scalp && c.ses === "off-KZ") C(0.5, "Scalp outside the kill zones", "سكالب برة الكيل زون");
    // hard stops
    if (c.news) vetoes.push(["High-impact news within the hour: "+c.news, "خبر قوي خلال ساعة: "+c.news]);
    if (c.openSame) vetoes.push(["You already have this trade open (journal)", "الصفقة دي مفتوحة عندك أصلًا (الجورنال)"]);
    if (c.openOpp) vetoes.push(["An OPPOSITE trade on this symbol is open", "فيه صفقة عكسها مفتوحة على نفس الرمز"]);
    if (rr < 1) vetoes.push(["R:R below 1", "R:R أقل من 1"]);
    const sum = a => a.reduce((t, x) => t + x[0], 0), score = Math.round((sum(pros) - sum(cons))*10)/10;
    let verdict = vetoes.length ? "SKIP" : score >= 3 && rr >= 1.5 ? (idea.now ? "TAKE" : "WAIT") : score >= 1 ? "WAIT" : "SKIP";
    const worst = cons.slice().sort((a, b) => b[0] - a[0])[0];
    if (verdict === "TAKE" && worst && worst[0] >= 2){ verdict = "WAIT"; second.push(["Downgraded to WAIT: the strongest objection is heavy ("+worst[1]+")", "نزلت لـ«استنى»: أقوى اعتراض تقيل ("+worst[2]+")"]); }
    if (verdict === "WAIT" && !idea.now) second.push(["Limit order at "+entry.toPrecision(6)+": price has not reached the zone", "أمر معلّق عند "+entry.toPrecision(6)+": السعر لسه ماوصلش للمنطقة"]);
    const pct = Math.max(0, Math.min(100, Math.round((score + 4)/12*100)));
    // A+ (Academy checklist): a TAKE with the higher timeframe behind it, a trigger on the entry timeframe, >= 2 independent confirmations,
    // R:R >= 2 with a clear path to the target, and no regime / journal objection -> grade A+; other TAKE = A, WAIT = B, SKIP = C
    const conf = (c.confl ? c.confl.length : 0) + (c.vpAt ? 1 : 0) + (c.hist && c.hist.n >= 10 && c.hist.hitPct >= 0.55 ? 1 : 0) + (c.setupB && c.setupB.available && c.setupB.bias === want ? 1 : 0);
    const aplus = verdict === "TAKE" && !!(c.bias && c.bias.available && c.bias.bias === want) && !!c.trig && conf >= (["elliott","harmonic","smt"].includes(idea.det) ? 3 : 2) && rr >= 2 && !ob && score >= 5 && !c.regime_bad && !(c.jr && c.jr.done >= 10 && c.jr.avgR < 0);
    const grade = aplus ? "A+" : verdict === "TAKE" ? "A" : verdict === "WAIT" ? "B" : "C";
    return {pros, cons, vetoes, second, score, pct, verdict, grade, conf, plan:{entry, stop, tps}, rr, pts:pt(tps[0] - entry), blocked: blocked ? ob : null};
  },
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
const TC_VR = {TAKE:2, WAIT:1, SKIP:0};
const TC = {
  res:{}, busy:false, prog:"", subs:new Set(), next:{},
  // the schools ("detectors"); the English name is the stable key used in journal tags ("TC <name>")
  DETS: [["bounce","S/R bounce","ارتداد دعم/مقاومة"], ["vp","Volume profile","فوليوم بروفايل"], ["struct","Breakout / BOS / MSS","اختراق / كسر هيكل"], ["smt","SMT","SMT"],
         ["elliott","Elliott","إليوت"], ["harmonic","Harmonic","هارمونيك"], ["scanner","Scanner setups","إعدادات السكانر"],
         ["vwap","VWAP","VWAP"], ["ma","Moving averages","المتوسطات"], ["session","Session levels","مستويات الجلسة"], ["custom","My strategies","استراتيجياتي"]],
  // "My strategies": the owner's own rules (saved in this browser). The first one is the owner's Nasdaq idea, UNTESTED: long only when price is >= 25 points under the session VWAP.
  CUSTOM_DEFAULT: [{id:"nqvwap", name:"Nasdaq VWAP stretch (long only)", side:"long", sym:"XYZ100|NAS|NDX|NQ|US100|USTEC", stop:1, on:true, rules:[{a:"close", op:"<", b:"vwap", off:-25}], note:"owner idea, not backtested"}],
  customs(){ const v = store.get(LS+"_tc_custom", null); return Array.isArray(v) ? v : this.CUSTOM_DEFAULT.map(x => JSON.parse(JSON.stringify(x))); },
  saveCustoms(v){ store.set(LS+"_tc_custom", v); this.next = {}; },
  detName(k){ const d = this.DETS.find(x => x[0] === k); return d ? Lg(d[1], d[2]) : k; },
  detKey(k){ const d = this.DETS.find(x => x[0] === k); return "TC "+(d ? d[1] : k); },
  // SMT partner when the server list (CFG.smt) has none: Hyperliquid TradFi pairs
  PEERS: {"HL:xyz:GOLD":["HL:xyz:SILVER",false], "HL:xyz:SILVER":["HL:xyz:GOLD",false], "HL:xyz:SP500":["HL:xyz:XYZ100",false], "HL:xyz:XYZ100":["HL:xyz:SP500",false],
          "HL:xyz:CL":["HL:xyz:BRENTOIL",false], "HL:xyz:BRENTOIL":["HL:xyz:CL",false], "HL:xyz:EUR":["HL:xyz:GBP",false], "HL:xyz:GBP":["HL:xyz:EUR",false]},
  peer(sym){ let o = []; try { o = smtPeers(sym); } catch(e){} return o.length ? o[0] : (this.PEERS[sym] || null); },
  /* the three timeframes of the style. A missing timeframe does not drop the symbol: bias falls back to the setup frame (marked), entry to the setup frame */
  async stack(sym, style){
    const S = TCE.STYLES[style], notes = [], setup = await candlesTf(sym, S.setup, true, S.want);
    if (!setup || setup.length < 60) throw new Error(Lg("not enough "+S.setup+" candles ("+(setup ? setup.length : 0)+")", "شموع "+S.setup+" مش كفاية ("+(setup ? setup.length : 0)+")"));
    let bias = await candlesTf(sym, S.bias, true, 120).catch(() => null), biasFallback = false, entry = await candlesTf(sym, S.entry, true, 80).catch(() => null);
    if (!bias || bias.length < 60){ notes.push(Lg("no "+S.bias+" candles: bias not counted", "مفيش شموع "+S.bias+": الاتجاه مش محسوب")); bias = setup; biasFallback = true; }
    if (!entry || entry.length < 20){ notes.push(Lg("no "+S.entry+" candles: trigger read on "+S.setup, "مفيش شموع "+S.entry+": الإشارة من "+S.setup)); entry = setup; }
    return {setup, bias, entry, biasFallback, notes};
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
  /* every school proposes ideas on the setup timeframe; all share the target in points (user's or Auto = median measured move) */
  ideas(sym, style, st, opt){
    const S = TCE.STYLES[style], R = st.setup, n = R.length, px = R[n-1].c, a = TCE.atr(R, 14), ps = TCE.pointSize(sym, px), on = k => !opt.dets || !opt.dets.length || opt.dets.includes(k), out = [];
    const ev = TCE.events(R, {hold:S.hold}), auto = Math.max(1, TCE.nicePts((TCE.stats(ev, 0).median || a)/ps)), tPts = opt.targetPts > 0 ? opt.targetPts : auto, T_ = tPts*ps;
    const lv = SR.compute(R), vp = vpCalc(R.slice(-200), 60), nodes = TCE.vpNodes(vp);
    const mk = (det, side, entry, stop, now, level, label, own) => { if (!(entry > 0) || !(Math.abs(entry - stop) > 0) || (side > 0 ? stop >= entry : stop <= entry)) return;
      const tps = own && !(opt.targetPts > 0) && own.length ? [own[0], own[1] != null ? own[1] : own[0] + side*Math.abs(own[0] - entry)*0.6] : [entry + side*T_, entry + side*T_*1.6];
      if (side*(tps[0] - entry) <= 0) return; out.push({det, label, side, entry, stop, now, level, tps}); };
    if (on("bounce")) TCE.candidates(sym, R, lv, st.bias, st.entry, {targetPts:tPts, ps, hold:S.hold}).forEach(c =>
      mk("bounce", c.side, c.entry, c.stop, c.now, c.level, Lg("Bounce from ","ارتداد من ")+(c.side > 0 ? Lg("support ","دعم ") : Lg("resistance ","مقاومة "))+fmtP(c.level)+" ×"+c.touches));
    if (on("vp")) [1, -1].forEach(sd => { const nd = nodes.filter(x => sd*(px - x.p) >= -a*0.25 && sd*(px - x.p) <= a*1.5).sort((x, y) => Math.abs(x.p - px) - Math.abs(y.p - px))[0]; if (!nd) return;
      const now = Math.abs(px - nd.p) <= a*0.5; mk("vp", sd, now ? px : nd.p + sd*a*0.1, nd.p - sd*a*0.7, now, nd.p, "VP "+nd.src+" "+fmtP(nd.p)); });
    if (on("struct")) TCE.structure(R, 6).forEach(b => { const d = b.side*(px - b.level), now = d >= -a*0.3 && d <= a*0.8;
      mk("struct", b.side, now ? px : b.level + b.side*a*0.1, b.level - b.side*a, now, b.level, b.kind+" "+(b.side > 0 ? "▲" : "▼")+" "+fmtP(b.level)+(now ? "" : Lg(" (retest)"," (ريتست)"))); });
    if (on("smt") && st.peer && st.peer.length > 40){ const m = new Map(st.peer.map(r => [r.t, r])), A = [], B = []; R.forEach(r => { const q = m.get(r.t); if (q){ A.push(r); B.push(q); } });
      try { smtFind(A, B, st.peerInv).filter(x => x.i2 >= A.length - 8).slice(-1).forEach(x => { const sd = x.side === "up" ? 1 : -1, ex = sd > 0 ? A[x.i2].l : A[x.i2].h;
        mk("smt", sd, px, ex - sd*a*0.3, true, ex, "SMT "+Lg("vs ","مع ")+String(st.peerSym).replace(/^HL:xyz:|^Y:/, "")); }); } catch(e){} }
    if (on("elliott")) try { const o = {data:R, tf:S.setup, ewForming:CandleChart.prototype.ewForming}, list = CandleChart.prototype.ewCount.call(o), f = o._ewf;
      if (f && (f.next === 3 || f.next === 5) && !f.broke){ const sd = f.up ? 1 : -1, P = f.pts.map(q => q.p), stp = f.next === 3 ? P[0] : P[1];
        mk("elliott", sd, px, stp - sd*a*0.2, true, P[P.length-1], Lg("Elliott: wave "+f.next+" next","إليوت: الموجة "+f.next+" جاية")); }
      const top = list && list[0]; if (top && top.pts.length === 6 && (!top.abc || !top.abc.length) && n - 1 - top.pts[5].i <= 10){ const sd = top.up ? -1 : 1, ext = top.pts[5].p;
        mk("elliott", sd, px, ext - sd*a*0.3, true, ext, Lg("Elliott: 5 waves done → A-B-C","إليوت: 5 موجات خلصت ← A-B-C")); } } catch(e){}
    if (on("harmonic")) try { this.harm(sym, style, R, st.bias, [], {}).forEach(h => mk("harmonic", h.direction === "bullish" ? 1 : -1, h.plan.entry, h.plan.stop, h.why.includes("price is at the zone now"), h.plan.entry, tagTxt(h.tags[0][0]), h.plan.tps)); } catch(e){}
    if (on("scanner")) readyList(true).filter(e => e.symbol === sym && e.ttype === style && e.src !== "tclass").forEach(e =>
      mk("scanner", e.direction === "bullish" ? 1 : -1, e.plan.entry, e.plan.stop, Math.abs(px - e.plan.entry) <= a*0.5, e.plan.entry, Lg("Scanner: ","السكانر: ")+(e.tags || []).slice(0, 3).map(t => tagTxt(t[0])).join(" · "), e.plan.tps));
    const I_ = TCE.indicators(R), li = n - 1, intraday = style === "Scalp" || style === "Day Trade";
    /* VWAP school (owner options): side long / short / both; anchor UTC day or the 09:30 New York cash open; stretch measured in sigma, points or ATR;
       optional "wait for the reclaim" (a close back over the previous bar's high / under its low) and the 10:00-11:30 New York window (sources: fades fail in
       9:30-10:00 and on trend days). Target = the VWAP, stop 1 ATR beyond the extreme. Untested: the journal keeps the record. */
    if (on("vwap") && intraday){ const V = Object.assign({side:"both", anchor:"auto", mode:"sigma", k:2, trig:true, win:false}, opt.vw || {});
      const idx = /^(HL:xyz:(SP500|XYZ100|JP225|KR200)|Y:\^|FH:(SPX|NAS|US30))/.test(sym) || symClass(sym) === "Stocks", anchor = V.anchor === "auto" ? (idx ? "rth" : "utc") : V.anchor;
      const IV = anchor === "utc" ? I_ : TCE.indicators(R, anchor), vw = IV.vwap[li], sdv = (IV.vwapU2[li] - vw)/2, dist = V.mode === "points" ? V.k*ps : V.mode === "atr" ? V.k*a : V.k*sdv;
      let inWin = true; if (V.win){ try { const f = new Intl.DateTimeFormat("en-GB", {timeZone:"America/New_York", hour:"2-digit", minute:"2-digit", hour12:false}).formatToParts(new Date(R[li].t)), m = (+f.find(x => x.type === "hour").value % 24)*60 + +f.find(x => x.type === "minute").value; inWin = m >= 600 && m <= 690; } catch(e){} }
      const E = st.entry, eL = E.length - 1, recl = sd => E.length > 2 && (sd > 0 ? E[eL].c > E[eL-1].h : E[eL].c < E[eL-1].l);
      const tag = (V.mode === "points" ? V.k+Lg(" pts"," نقطة") : V.mode === "atr" ? V.k+" ATR" : V.k+"σ")+(anchor === "rth" ? " · NY 09:30" : "");
      if (sdv > 0 && inWin){
        [[1, "long"], [-1, "short"]].forEach(([sd, nm]) => { if (V.side !== "both" && V.side !== nm) return;
          if (sd*(vw - px) < dist) return;   // not stretched enough from the VWAP
          const ext = sd > 0 ? Math.min(...R.slice(-3).map(r => r.l)) : Math.max(...R.slice(-3).map(r => r.h)), ok = !V.trig || recl(sd);
          mk("vwap", sd, px, ext - sd*a, ok, vw, (sd > 0 ? Lg("Under VWAP by ","تحت الـVWAP بـ") : Lg("Over VWAP by ","فوق الـVWAP بـ"))+tag+(ok ? "" : Lg(" (wait for the reclaim)"," (استنى الريكليم)")), [vw, vw + sd*sdv]); });
        if (V.mode === "sigma"){ const e = IV.ema21, up = e[li] > e[li-5], dn = e[li] < e[li-5];
          if (V.side !== "short" && up && px > vw && R[li].l <= vw + a*0.2 && px - vw <= a*0.6) mk("vwap", 1, px, vw - a*0.6, true, vw, Lg("Pullback to VWAP in an uptrend","رجوع لـVWAP في ترند صاعد"));
          if (V.side !== "long" && dn && px < vw && R[li].h >= vw - a*0.2 && vw - px <= a*0.6) mk("vwap", -1, px, vw + a*0.6, true, vw, Lg("Pullback to VWAP in a downtrend","رجوع لـVWAP في ترند هابط")); } } }
    if (on("ma") && n > 60){ const e9 = I_.ema9, e21 = I_.ema21, e50 = I_.ema50, e200 = I_.ema200, lo5 = Math.min(...R.slice(-5).map(r => r.l)), hi5 = Math.max(...R.slice(-5).map(r => r.h));
      for (let k = li; k > li - 3; k--){
        if (e9[k-1] <= e21[k-1] && e9[k] > e21[k] && px > e200[li]){ mk("ma", 1, px, lo5 - a*0.2, true, e21[li], Lg("EMA 9/21 cross up, above EMA200","تقاطع EMA 9/21 لفوق، فوق EMA200")); break; }
        if (e9[k-1] >= e21[k-1] && e9[k] < e21[k] && px < e200[li]){ mk("ma", -1, px, hi5 + a*0.2, true, e21[li], Lg("EMA 9/21 cross down, below EMA200","تقاطع EMA 9/21 لتحت، تحت EMA200")); break; } }
      if (n > 220) for (let k = li; k > li - 5; k--){
        if (e50[k-1] <= e200[k-1] && e50[k] > e200[k]){ mk("ma", 1, px, px - 2*a, true, e200[li], Lg("Golden cross 50/200","التقاطع الذهبي 50/200")); break; }
        if (e50[k-1] >= e200[k-1] && e50[k] < e200[k]){ mk("ma", -1, px, px + 2*a, true, e200[li], Lg("Death cross 50/200","تقاطع الموت 50/200")); break; } } }
    if (on("session") && intraday) [["pdh","PDH"], ["pdl","PDL"], ["dopen",Lg("daily open","افتتاح اليوم")], ["wopen",Lg("weekly open","افتتاح الأسبوع")]].forEach(([k, nm]) => {
      const L = I_[k] && I_[k][li]; if (L == null) return; const d = px - L;
      if (Math.abs(d) <= a*0.5){ const sd = d >= 0 ? 1 : -1; mk("session", sd, px, L - sd*a*0.6, true, L, Lg("At ","عند ")+nm+" "+fmtP(L)); }   // above the level = it holds as support, below = resistance
      if ((k === "pdh" && R[li].c > L && R[li-1].c <= L) || (k === "pdl" && R[li].c < L && R[li-1].c >= L)){ const sd = k === "pdh" ? 1 : -1; mk("session", sd, px, L - sd*a*0.8, true, L, Lg("Break of ","كسر ")+nm+" "+fmtP(L)); } });
    if (on("custom")) this.customs().forEach(cs => { if (cs.on === false) return; let okSym = true; try { okSym = !cs.sym || new RegExp(cs.sym, "i").test(sym); } catch(e){ okSym = false; } if (!okSym) return;
      const sd = cs.side === "short" ? -1 : 1; if (TCE.rulesOk(cs.rules, I_, li, ps)) mk("custom", sd, px, px - sd*a*(+cs.stop || 1), true, px, "★ "+cs.name); });
    return {ideas:out, ctx:{px, a, ps, tPts, auto, ev, lv, nodes}};
  },
  // the case for / against of every idea, with the live context (journal, news, regime, open trades)
  judgeAll(sym, style, st, I){
    const S = TCE.STYLES[style], R = st.setup, X = I.ctx, bias = st.biasFallback ? {available:false} : TCE.bias(st.bias), setupB = TCE.bias(R);
    let reg = null; try { reg = (Regime.of(R) || {}).regime || null; } catch(e){}
    let nw = null, ses = ""; try { nw = Ctx.news(sym); ses = Ctx.session(); } catch(e){}
    const open = (Journal.list || []).filter(t => t.status === "open"), cls = symClass(sym), entStruct = st.entry === R ? [] : TCE.structure(st.entry, 3);
    const levels = X.lv.map(l => ({p:l.p, src:l.kind === "R" ? Lg("resistance","مقاومة") : Lg("support","دعم")})).concat(X.nodes.map(x => ({p:x.p, src:"VP "+x.src})));
    return I.ideas.map(idea => { const s = idea.side, dir = s > 0 ? "bullish" : "bearish", T_ = Math.abs(idea.tps[0] - idea.entry), hist = TCE.stats(X.ev.filter(e => e.side === s), T_);
      const tS = entStruct.find(b => b.side === s), tR = TCE.rejection(st.entry, s), trig = tS ? tS.kind+" "+S.entry : tR ? Lg("rejection candle","شمعة رفض") : "";
      const confl = [...new Set(I.ideas.filter(o => o !== idea && o.side === s && o.det !== idea.det && Math.abs(o.entry - idea.entry) <= X.a).map(o => this.detName(o.det)))];
      const vn = X.nodes.find(x => Math.abs(x.p - idea.entry) <= X.a*0.3), late = idea.now && idea.level != null ? Math.max(0, s*(X.px - idea.level))/Math.max(1e-12, Math.abs(idea.tps[0] - idea.level)) : 0;
      const c = {tf:{bias:S.bias, setup:S.setup, entry:S.entry}, ps:X.ps, atr:X.a, levels, bias, setupB, trig, confl, vpAt:vn ? vn.src : "", hist, late:late > 0.4 ? late : 0, regime:reg, regime_bad:reg === "chop" || reg === "hivol" || reg === "crash",
        news:nw ? (nw.country+" "+(nw.title || "")) : "", openSame:open.some(t => t.symbol === sym && t.dir === dir), openOpp:open.some(t => t.symbol === sym && t.dir !== dir),
        classOpen:open.filter(t => t.symbol !== sym && symClass(t.symbol) === cls && t.dir === dir).length, jr:this.record(style, idea.det), scalp:style === "Scalp", ses};
      return Object.assign({}, idea, {j:TCE.judge(idea, c), hist}); });
  },
  async scanSym(sym, style, opt){
    const st = await this.stack(sym, style), S = TCE.STYLES[style], pr = this.peer(sym);
    if (pr && (!opt.dets || !opt.dets.length || opt.dets.includes("smt"))){ try { st.peer = await candlesTf(pr[0], S.setup, true, S.want); st.peerSym = pr[0]; st.peerInv = !!pr[1]; } catch(e){ st.notes.push(Lg("SMT partner "+pr[0]+" not available", "شريك الـSMT "+pr[0]+" مش متاح")); } }
    const I = this.ideas(sym, style, st, opt), J = this.judgeAll(sym, style, st, I).sort((x, y) => (TC_VR[y.j.verdict] - TC_VR[x.j.verdict]) || (y.j.score - x.j.score));
    return {t:Date.now(), n:st.setup.length, notes:st.notes, ideas:J, spark:st.setup.slice(-40).map(r => r.c), px:I.ctx.px, autoPts:I.ctx.auto, tPts:I.ctx.tPts, ps:I.ctx.ps};
  },
  async run(style, syms, opt, force){
    if (this.busy) return; if (!force && Date.now() < (this.next[style] || 0)) return; this.busy = true;
    try { for (let k = 0; k < syms.length; k++){ const s = syms[k]; this.prog = (k + 1)+"/"+syms.length+" "+s.replace(/^HL:xyz:|^Y:|-USDT.*$/g, ""); this.subs.forEach(f => f());
        try { this.res[style+"|"+s] = await this.scanSym(s, style, opt); }
        catch(e){ this.res[style+"|"+s] = {t:Date.now(), err:String(e && e.message || e), ideas:[]}; if (isRL(e)){ this.prog = T("busy"); break; } }
        await new Promise(r => setTimeout(r, 300)); }
      this.next[style] = Date.now() + TCE.STYLES[style].every;
    } finally { this.busy = false; if (this.prog.indexOf("/") > 0) this.prog = ""; this.subs.forEach(f => f()); }
  },
  // an idea as a card in the scanner's shape: Alerts / Setup Card / Ready / Signals / strip / journal read it unchanged
  card(sym, style, x, r){
    const S = TCE.STYLES[style], j = x.j, long_ = x.side > 0, V = {TAKE:"ادخل", WAIT:"استنى", SKIP:"ماتدخلش"};
    const ar = ["القرار: "+V[j.verdict]+" · الدرجة "+j.grade+" · "+x.label+" · النتيجة "+j.score, "ترابط الفريمات: "+S.bias+" ← "+S.setup+" ← "+S.entry]
      .concat(j.pros.map(p => "✔ "+p[2]), j.cons.map(p => "✘ "+p[2]), j.vetoes.map(p => "⛔ "+p[1]), j.second.map(p => "↻ "+p[1]));
    return {symbol:sym, direction:long_ ? "bullish" : "bearish", ttype:style, tfk:S.tfk, tfc:S.entry, score:Math.round(j.pct/10), max:10, src:"tclass", det:x.det, verdict:j.verdict,
      plan:{entry:j.plan.entry, stop:j.plan.stop, tps:j.plan.tps}, zones:[{lo:Math.min(x.entry, x.stop), hi:Math.max(x.entry, x.stop), dir:long_ ? "bullish" : "bearish"}],
      tags:[[this.detKey(x.det), "#f0b90b", "#000", x.label], [j.pts+Lg(" pts"," نقطة"), "#4aa3ff", "#000", "target in points"]].concat(j.grade === "A+" ? [["A+", "#f0b90b", "#000", "A+ setup: higher timeframe + trigger + 2 confirmations + R:R >= 2 + clear path"]] : []), spark:r.spark, ana:{sig:ar}, j, pts:j.pts, ps:r.ps, label:x.label};
  },
  // TAKE + price at the zone -> Alerts (never replaces a stronger card of the same symbol / side / type)
  push(style){ Object.keys(this.res).filter(k => k.startsWith(style+"|")).forEach(k => { const r = this.res[k], x = r.ideas && r.ideas[0]; if (!x || x.j.verdict !== "TAKE" || !x.now) return;
      const sym = k.slice(style.length + 1), c = this.card(sym, style, x, r), g = c.symbol+"|"+c.direction+"|"+c.ttype, old = Alerts.list.find(a => a.card && a.card.symbol+"|"+a.card.direction+"|"+a.card.ttype === g);
      if (old && old.card.src !== "tclass" && old.card.score/Math.max(1, old.card.max) >= c.score/c.max) return;
      Alerts.add("tc|"+g+"|"+c.plan.stop.toPrecision(6), "scan", sym, sym+" · "+(c.direction === "bullish" ? "Long" : "Short")+" · "+ttTxt(style)+" · "+x.label+" · "+c.pts+Lg(" pts"," نقطة"), c.direction === "bullish" ? "#0ecb81" : "#f6465d", c); }); },
  // VWAP school options popover (side, anchor, distance, reclaim, window) + the owner's Nasdaq preset
  vwPanel(anchorEl, S, onChange){ const old = document.getElementById("tcVw"); if (old){ old.remove(); return; }
    const m = el("div"); m.id = "tcVw"; m.dir = lang === "ar" ? "rtl" : "ltr"; m.style.cssText = "position:fixed;z-index:99999;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px;font-size:13px;box-shadow:0 10px 30px rgba(0,0,0,.5);display:grid;gap:6px;max-width:96vw";
    m.onpointerdown = ev => ev.stopPropagation(); const V = S.vw, row = (lbl, node) => { const r = el("label"); r.style.cssText = "display:flex;gap:8px;align-items:center;justify-content:space-between"; r.append(document.createTextNode(lbl), node); m.append(r); };
    const sl = (opts, k) => { const x = el("select"); opts.forEach(([v, l]) => x.append(Object.assign(el("option"), {value:String(v), textContent:l}))); x.value = String(V[k]); x.onchange = () => { V[k] = x.value; onChange(); }; return x; };
    row(Lg("Side","الاتجاه"), sl([["both",Lg("Long + short","شراء + بيع")],["long",Lg("Long only","شراء بس")],["short",Lg("Short only","بيع بس")]], "side"));
    row(Lg("VWAP starts at","الـVWAP يبدأ من"), sl([["auto",Lg("Auto (indices NY 09:30, else UTC)","تلقائي (المؤشرات 9:30 نيويورك، الباقي UTC)")],["rth",Lg("NY cash open 09:30","افتتاح نيويورك 9:30")],["utc",Lg("UTC day","يوم UTC")]], "anchor"));
    row(Lg("Distance in","المسافة بـ"), sl([["sigma","σ"],["points",Lg("points","نقاط")],["atr","ATR"]], "mode"));
    const kk = el("input"); kk.type = "number"; kk.step = "any"; kk.value = V.k; kk.style.width = "80px"; kk.onchange = () => { V.k = +kk.value || 2; onChange(); }; row(Lg("At least","على الأقل"), kk);
    const ck = k => { const x = el("input"); x.type = "checkbox"; x.checked = !!V[k]; x.onchange = () => { V[k] = x.checked; onChange(); }; return x; };
    row(Lg("Wait for the reclaim candle","استنى شمعة الريكليم"), ck("trig")); row(Lg("Only 10:00-11:30 New York","بس 10:00-11:30 نيويورك"), ck("win"));
    const pre = el("button", null, esc(Lg("Preset: Nasdaq long, 25 pts, NY 09:30, reclaim, 10-11:30","جاهز: ناسداك شراء، 25 نقطة، 9:30 نيويورك، ريكليم، 10-11:30")));
    pre.onclick = () => { Object.assign(V, {side:"long", anchor:"rth", mode:"points", k:25, trig:true, win:true}); m.remove(); onChange(); }; m.append(pre);
    m.append(el("div", "m", esc(Lg("Untested: the sources show vendor / forum numbers only; the journal keeps the real record.","مش متجربة: المصادر فيها أرقام بياعين ومنتديات بس؛ الجورنال بيسجل الحقيقي."))));
    document.body.append(m); const r = anchorEl.getBoundingClientRect(); m.style.top = (r.bottom + 4)+"px"; m.style.left = Math.max(6, Math.min(r.left, innerWidth - m.offsetWidth - 6))+"px";
    setTimeout(() => document.addEventListener("pointerdown", function h(ev){ if (!m.contains(ev.target) && ev.target !== anchorEl){ m.remove(); document.removeEventListener("pointerdown", h, true); } }, true), 0); },
  // next kill zone / session (New York time, the same clock as Ctx.session) -> {name, in}
  nextSession(){ try { const f = new Intl.DateTimeFormat("en-GB", {timeZone:"America/New_York", hour:"2-digit", minute:"2-digit", hour12:false}).formatToParts(new Date()), m = (+f.find(x => x.type === "hour").value % 24)*60 + +f.find(x => x.type === "minute").value;
      const L = [["London KZ", 120], ["NY AM KZ", 420], ["NY PM KZ", 810], ["Asia", 1200]].map(([nm, st]) => [nm, (st - m + 1440) % 1440]).sort((a, b) => a[1] - b[1])[0], h = Math.floor(L[1]/60), mm = L[1] % 60;
      return {name:L[0], in:(h ? h+"h " : "")+mm+"m"}; } catch(e){ return null; } },
  // "My strategies" editor: name, side, symbols (regex), stop in ATR, rules [a op b (+/- points)]; saved in this browser
  editor(anchor, onSave){
    const old = document.getElementById("tcEd"); if (old){ old.remove(); return; }
    const m = el("div"); m.id = "tcEd"; m.dir = lang === "ar" ? "rtl" : "ltr"; m.style.cssText = "position:fixed;z-index:99999;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 12px;font-size:13px;box-shadow:0 14px 40px rgba(0,0,0,.55);width:min(560px,96vw);max-height:80vh;overflow:auto";
    m.onpointerdown = e => e.stopPropagation(); let list = this.customs(), cur = null;
    const SRC = TCE.RULE_SRC, OPS = [[">", ">"], ["<", "<"], ["xa", Lg("crosses above","يقطع لفوق")], ["xb", Lg("crosses below","يقطع لتحت")]];
    const sel = (opts, v) => { const s = el("select"); opts.forEach(o => { const [k, l] = Array.isArray(o) ? o : [o, o]; s.append(Object.assign(el("option"), {value:k, textContent:l})); }); s.value = v; return s; };
    const paint = () => { m.innerHTML = '<b style="color:#f0b90b">★ '+esc(Lg("My strategies","استراتيجياتي"))+'</b> <span class="m" style="font-size:11px">'+esc(Lg("judged by the same engine (case for / against, second look); untested until the journal has 30+ trades","بتتحكم بنفس المحرك (ليه أدخل / ليه لأ، مراجعة تانية)؛ مش مجربة لحد ما الجورنال يبقى فيه 30+ صفقة"))+'</span>';
      list.forEach((cs, i) => { const r = el("div"); r.style.cssText = "display:flex;gap:6px;align-items:center;margin-top:6px"; const on = el("input"); on.type = "checkbox"; on.checked = cs.on !== false; on.onchange = () => { cs.on = on.checked; this.saveCustoms(list); onSave(); };
        const t = el("span", null, esc(cs.name)+' <span class="m" style="font-size:11px">'+(cs.side === "short" ? "▼" : "▲")+" "+esc((cs.rules || []).map(x => x.a+" "+x.op+" "+(x.b === "value" ? x.v : x.b)+(+x.off ? (x.off > 0 ? " +" : " ")+x.off+"pt" : "")).join(" & "))+'</span>'); t.style.flex = "1";
        const ed = el("button", null, "✎"), del = el("button", null, "✕"); ed.onclick = () => { cur = JSON.parse(JSON.stringify(cs)); cur._i = i; form(); }; del.onclick = () => { list.splice(i, 1); this.saveCustoms(list); onSave(); paint(); };
        r.append(on, t, ed, del); m.append(r); });
      const nb = el("button", null, "＋ "+Lg("New strategy","استراتيجية جديدة")); nb.style.marginTop = "8px"; nb.onclick = () => { cur = {id:"c"+Date.now(), name:"", side:"long", sym:"", stop:1, on:true, rules:[{a:"close", op:">", b:"ema21", off:0}]}; form(); }; m.append(nb); };
    const form = () => { paint(); const f = el("div"); f.style.cssText = "margin-top:8px;border-top:1px solid var(--line);padding-top:8px;display:grid;gap:6px";
      const nm = el("input"); nm.placeholder = Lg("Name","الاسم"); nm.value = cur.name; const sd = sel([["long", Lg("Long","شراء")], ["short", Lg("Short","بيع")]], cur.side);
      const sy = el("input"); sy.placeholder = Lg("Symbols (optional, e.g. XYZ100|NQ)","الرموز (اختياري، مثلًا XYZ100|NQ)"); sy.value = cur.sym || ""; const stp = el("input"); stp.type = "number"; stp.step = "0.1"; stp.value = cur.stop || 1; stp.title = Lg("Stop in ATR","الستوب بالـATR"); stp.style.width = "70px";
      const r1 = el("div"); r1.style.cssText = "display:flex;gap:6px;flex-wrap:wrap"; r1.append(nm, sd, sy, document.createTextNode(Lg("stop ATR ","ستوب ATR ")), stp); f.append(r1);
      const rbox = el("div"); f.append(rbox);
      const rules = () => { rbox.innerHTML = ""; cur.rules.forEach((ru, k) => { const rw = el("div"); rw.style.cssText = "display:flex;gap:4px;flex-wrap:wrap;align-items:center;margin:2px 0";
          const A = sel(SRC, ru.a), O = sel(OPS, ru.op), B = sel(SRC.concat([["value", Lg("number","رقم")]]), ru.b), V = el("input"), OF = el("input"), X = el("button", null, "✕");
          V.type = "number"; V.step = "any"; V.value = ru.v != null ? ru.v : ""; V.style.width = "70px"; V.hidden = ru.b !== "value"; OF.type = "number"; OF.step = "any"; OF.value = ru.off || 0; OF.style.width = "70px"; OF.title = Lg("+/- points added to the right side","+/- نقاط على الطرف اليمين");
          A.onchange = () => ru.a = A.value; O.onchange = () => ru.op = O.value; B.onchange = () => { ru.b = B.value; V.hidden = ru.b !== "value"; }; V.oninput = () => ru.v = +V.value; OF.oninput = () => ru.off = +OF.value; X.onclick = () => { cur.rules.splice(k, 1); rules(); };
          rw.append(A, O, B, V, document.createTextNode(Lg(" ± pts "," ± نقاط ")), OF, X); rbox.append(rw); }); };
      rules();
      const add = el("button", null, "＋ "+Lg("rule","شرط")), sv = el("button", null, "💾 "+Lg("Save","احفظ")), cn = el("button", null, Lg("Cancel","إلغاء"));
      add.onclick = () => { cur.rules.push({a:"close", op:"<", b:"vwap", off:0}); rules(); };
      sv.onclick = () => { cur.name = nm.value.trim() || Lg("My strategy","استراتيجيتي"); cur.side = sd.value; cur.sym = sy.value.trim(); cur.stop = +stp.value || 1; if (cur.sym){ try { new RegExp(cur.sym); } catch(e){ alert(Lg("Symbols: not a valid pattern","الرموز: صيغة غلط")); return; } }
        if (!cur.rules.length){ alert(Lg("Add at least one rule","ضيف شرط واحد على الأقل")); return; } const i = cur._i; delete cur._i; if (i != null) list[i] = cur; else list.push(cur); this.saveCustoms(list); cur = null; onSave(); paint(); };
      cn.onclick = () => { cur = null; paint(); };
      const r3 = el("div"); r3.style.cssText = "display:flex;gap:6px"; r3.append(add, sv, cn); f.append(r3); m.append(f); };
    paint(); document.body.append(m); const r = anchor.getBoundingClientRect(); m.style.top = Math.min(r.bottom + 4, innerHeight - 100)+"px"; m.style.left = Math.max(6, Math.min(r.left, innerWidth - m.offsetWidth - 6))+"px";
    setTimeout(() => document.addEventListener("pointerdown", function h(ev){ if (!m.contains(ev.target) && ev.target !== anchor){ m.remove(); document.removeEventListener("pointerdown", h, true); } }, true), 0);
  },
  // forward record from the journal for one style (+ one school): the real test
  record(style, det){ const key = det ? this.detKey(det) : null, L_ = (Journal.list || []).filter(t => (t.tags || []).some(g => key ? g === key : /^TC /.test(g)) && (!style || t.ttype === style));
    const done = L_.filter(t => t.status === "tp" || t.status === "sl"), w = done.filter(t => t.status === "tp").length, R = done.reduce((s, t) => s + (t.r || 0), 0);
    return {n:L_.length, open:L_.filter(t => t.status === "open").length, done:done.length, win:w, avgR: done.length ? R/done.length : null}; }
};
Panel.prototype.build_tclass = function(){
  const S = this.state.tc = Object.assign({style:"Scalp", tgt:0, uni:"watch", cls:"All", max:20, show:"tw", dir:"both", dets:TC.DETS.map(d => d[0]), push:true}, this.state.tc || {});
  if (!Array.isArray(S.dets) || S.detsV !== 2){ S.dets = TC.DETS.map(d => d[0]); S.detsV = 2; }   // v2 added VWAP / MA / session / my strategies: switched on for saved layouts too
  if (!document.getElementById("tcCss")){ const st = el("style"); st.id = "tcCss"; st.textContent =
    ".tcw .tb{display:flex;flex-wrap:wrap;gap:4px;align-items:center}.tcw .tb select,.tcw .tb button{font-size:12px}"
    +".tcw .sum{font-size:12px;padding:5px 6px;margin:4px 0;border:1px solid var(--line);border-radius:6px;line-height:1.5}"
    +".tcw .cd{border:1px solid var(--line);border-inline-start:4px solid var(--vc);border-radius:7px;padding:7px 9px;margin:6px 2px;cursor:pointer;font-size:12px;line-height:1.5;background:color-mix(in srgb,var(--vc) 6%,transparent)}"
    +".tcw .cd:hover{background:color-mix(in srgb,var(--vc) 13%,transparent)}.tcw .hd{display:flex;flex-wrap:wrap;align-items:center;gap:7px}.tcw .vb{font-weight:800;font-size:11px;padding:1px 8px;border-radius:4px;background:var(--vc);color:#0b0e11}"
    +".tcw .ch{font-size:11px;padding:0 6px;border-radius:3px;background:rgba(240,185,11,.15);color:#f0b90b;font-weight:700}.tcw .stk{font:11px ui-monospace,Menlo,Consolas,monospace;color:var(--mut)}"
    +".tcw .two{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:4px}@media (max-width:520px){.tcw .two{grid-template-columns:1fr}}.tcw ul{margin:2px 0;padding-inline-start:16px}"
    +".tcw .g{color:#0ecb81}.tcw .r{color:#f6465d}.tcw .b{color:#4aa3ff}.tcw .ru{margin-top:4px;font-size:11px;color:var(--mut)}.tcw details summary{cursor:pointer;color:var(--mut);font-size:11px}";
    document.head.append(st); }
  this.body.classList.add("tcw"); this.body.style.overflow = "auto";
  const ar = lang === "ar", tb = el("div","tb"), stop_ = x => { x.onpointerdown = e => e.stopPropagation(); return x; };
  const mk = (opts, key, num, title) => { const s = stop_(el("select")); opts.forEach(([v, l]) => s.append(Object.assign(el("option"), {value:String(v), textContent:l}))); s.value = String(S[key]); s.title = title || "";
    s.onchange = () => { S[key] = num ? +s.value : s.value; Ws.save(); (key === "show" || key === "dir") ? draw() : go(true); }; return s; };
  tb.append(
    mk([["Scalp",Lg("Scalp · 1H→15m→5m","سكالب · 1H←15m←5m")],["Day Trade",Lg("Day · 4H→1H→15m","داي · 4H←1H←15m")],["Swing",Lg("Swing · 1W→1D→4H","سوينج · 1W←1D←4H")],["Position",Lg("Position · 1M→1W→1D","بوزشن · 1M←1W←1D")]], "style", false, Lg("Style = timeframe stack (bias → setup → entry)","النوع = ترابط الفريمات (اتجاه ← إعداد ← دخول)")),
    mk(TCE.TARGETS.map(v => [v, v ? v+Lg(" pts"," نقطة") : Lg("Target: Auto","الهدف: تلقائي")]), "tgt", true, Lg("Target in points (Auto = the measured median move)","الهدف بالنقاط (تلقائي = متوسط الحركة المقاسة)")),
    mk([["chart",Lg("Chart symbol","رمز الشارت")],["watch",Lg("Watchlist","الووتش ليست")]], "uni"),
    mk([["All",Lg("All classes","كل الفئات")]].concat(CLS_LIST.map(c => [c, catL(c)])), "cls"),
    mk([[5,"5"],[10,"10"],[20,"20"],[40,"40"]].map(([v, l]) => [v, Lg("max ","أقصى ")+l]), "max", true, Lg("How many symbols to study","كام رمز يتدرس")),
    mk([["aplus",Lg("Show: A+ only","اعرض: A+ بس")],["take",Lg("Show: TAKE","اعرض: ادخل")],["tw",Lg("Show: TAKE + WAIT","اعرض: ادخل + استنى")],["all",Lg("Show: all (with rejected)","اعرض: الكل (مع المرفوض)")]], "show"),
    mk([["both",Lg("Long + short","شراء + بيع")],["long",Lg("Long only","شراء بس")],["short",Lg("Short only","بيع بس")]], "dir"));
  const schB = stop_(el("button")), schTxt = () => { schB.textContent = Lg("Schools: ","المدارس: ")+(S.dets.length === TC.DETS.length ? Lg("all","الكل") : S.dets.length)+" ▾"; }; schTxt();
  schB.onclick = e => { e.stopPropagation(); const old = document.getElementById("tcSch"); if (old){ old.remove(); return; }
    const m = el("div"); m.id = "tcSch"; m.style.cssText = "position:fixed;z-index:99999;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:13px;box-shadow:0 10px 30px rgba(0,0,0,.5)";
    TC.DETS.forEach(([k, en, a_]) => { const l = el("label"); l.style.cssText = "display:flex;gap:6px;align-items:center;padding:2px 0;cursor:pointer"; const c = el("input"); c.type = "checkbox"; c.checked = S.dets.includes(k);
      c.onchange = () => { S.dets = c.checked ? [...new Set(S.dets.concat([k]))] : S.dets.filter(x => x !== k); Ws.save(); schTxt(); go(true); }; l.append(c, document.createTextNode(Lg(en, a_))); m.append(l); });
    document.body.append(m); const r = schB.getBoundingClientRect(); m.style.top = (r.bottom + 4)+"px"; m.style.left = Math.max(6, Math.min(r.left, innerWidth - m.offsetWidth - 6))+"px";
    setTimeout(() => document.addEventListener("pointerdown", function h(ev){ if (!m.contains(ev.target)){ m.remove(); document.removeEventListener("pointerdown", h, true); } }, true), 0); };
  const rf = stop_(el("button", null, "⟳ "+Lg("Study now","ادرس دلوقتي"))), pu = el("label"), pc = stop_(el("input")); pc.type = "checkbox"; pc.checked = S.push !== false;
  pu.append(pc, document.createTextNode(Lg(" → Alerts"," ← التنبيهات"))); pu.title = Lg("Send TAKE trades (price at the zone) to Alerts, the Setup Card, the top strip and the journal","ابعت صفقات «ادخل» (السعر عند المنطقة) للتنبيهات وكارت الصفقة والشريط والجورنال");
  pc.onchange = () => { S.push = pc.checked; Ws.save(); };
  const myB = stop_(el("button", null, "★ "+Lg("My strategies","استراتيجياتي"))); myB.title = Lg("Add your own rules (e.g. price 25 points under VWAP, EMA cross ...): they are judged like every other school","ضيف قواعدك (مثلًا السعر تحت الـVWAP بـ25 نقطة، تقاطع متوسطات ...): بتتحكم عليها زي أي مدرسة");
  myB.onclick = e => { e.stopPropagation(); TC.editor(myB, () => go(true)); };
  const vwB = stop_(el("button", null, "VWAP ⚙")); vwB.title = Lg("VWAP school options: long / short / both, anchor, distance, reclaim, time window","إعدادات مدرسة الـVWAP: شراء / بيع / الاتنين، البداية، المسافة، الريكليم، وقت الجلسة");
  vwB.onclick = e => { e.stopPropagation(); TC.vwPanel(vwB, S, () => { Ws.save(); go(true); }); };
  tb.append(schB, vwB, myB, rf, pu);
  const sum = el("div","sum"), box = el("div"); this.body.append(tb, sum, box);
  const chartSym = () => { const ch = Ws.panels.find(p => p.type === "chart"); return ch ? ch.state.sym : SYMS[0]; };
  const syms = () => (S.uni === "watch" ? SYMS.slice() : [chartSym()]).filter(s => S.cls === "All" || symClass(s) === S.cls).slice(0, S.max || 20);
  S.vw = Object.assign({side:"both", anchor:"auto", mode:"sigma", k:2, trig:true, win:false}, S.vw || {});
  const go = force => { TC.run(S.style, syms(), {targetPts:S.tgt, dets:S.dets, vw:S.vw}, force); draw(); };
  rf.onclick = () => go(true);
  const VC = {TAKE:"#0ecb81", WAIT:"#f0b90b", SKIP:"#848e9c"}, VT = {TAKE:Lg("TAKE","ادخل"), WAIT:Lg("WAIT","استنى"), SKIP:Lg("SKIP","ماتدخلش")}, L2 = x => ar ? x[2] : x[1], L1 = x => ar ? x[1] : x[0];
  const dirOk = x => S.dir === "both" || (S.dir === "long" ? x.side > 0 : x.side < 0), showOk = (v, g) => S.show === "all" || (S.show === "aplus" ? g === "A+" : v === "TAKE" || (S.show === "tw" && v === "WAIT"));
  const cardHtml = (sym, r, x, i, alt) => { const j = x.j, St = TCE.STYLES[S.style], long_ = x.side > 0, pl = j.plan, ok = b => b ? '<b class="g">✓</b>' : '<b class="r">✗</b>';
    const bOk = j.pros.some(p => /^Bias/.test(p[1])), bBad = j.cons.some(p => /^Bias timeframe/.test(p[1])), sOk = j.pros.some(p => /^Setup/.test(p[1])), eOk = j.pros.some(p => /^Entry/.test(p[1]));
    const li = (a, f) => a.length ? '<ul>'+a.map(f).join("")+'</ul>' : '<div class="m">–</div>';
    return '<div class="cd" data-s="'+esc(sym)+'" data-i="'+i+'" style="--vc:'+VC[j.verdict]+'"><div class="hd"><span class="vb">'+VT[j.verdict]+'</span>'+(j.grade === "A+" ? '<span class="vb" style="background:linear-gradient(135deg,#f0b90b,#ffe08a);box-shadow:0 0 8px #f0b90b">A+</span>' : '<span class="m" style="font-weight:800">'+j.grade+'</span>')+'<b style="font-size:14px">'+esc(sym.replace(/^HL:xyz:|^Y:|-USDT.*$/g, ""))+'</b>'
      +'<b style="color:'+(long_ ? "#0ecb81" : "#f6465d")+'">'+(long_ ? "▲ "+esc(T("long")) : "▼ "+esc(T("short")))+'</b><span class="ch">'+esc(x.label)+'</span><span class="m">'+esc(Lg("score ","النتيجة "))+j.score+' · '+j.pct+'%</span></div>'
      +'<div class="stk">'+St.bias+' '+(bOk ? ok(1) : bBad ? ok(0) : '<b class="m">~</b>')+' → '+St.setup+' '+(sOk ? ok(1) : '<b class="m">~</b>')+' → '+St.entry+' '+(eOk ? ok(1) : '<b class="m">~</b>')+'</div>'
      +'<div>'+esc(Lg("Entry ","دخول "))+'<b>'+fmtP(pl.entry)+'</b> · '+esc(Lg("Stop ","ستوب "))+'<b class="r">'+fmtP(pl.stop)+'</b> · '+esc(Lg("Target ","هدف "))+'<b class="g">'+fmtP(pl.tps[0])+'</b> ('+j.pts+Lg(" pts"," نقطة")+') · R:R <b>'+j.rr.toFixed(1)+'</b>'+(j.blocked ? ' <b class="r">⚠ '+esc(Lg("blocked by ","مسدود بـ"))+esc(j.blocked.src)+'</b>' : "")+(x.now ? "" : ' · <span class="b">'+esc(Lg("limit","أمر معلّق"))+'</span>')+'</div>'
      +(j.vetoes.length ? '<div class="r"><b>⛔ '+j.vetoes.map(v => esc(L1(v))).join(" · ")+'</b></div>' : "")
      +'<div class="two"><div><b class="g">✔ '+esc(Lg("Why take it","ليه أدخل"))+'</b>'+li(j.pros, p => '<li>'+esc(L2(p))+' <span class="m">+'+p[0]+'</span></li>')+'</div>'
      +'<div><b class="r">✘ '+esc(Lg("Why NOT take it","ليه ماادخلش"))+'</b>'+li(j.cons, p => '<li>'+esc(L2(p))+' <span class="m">−'+p[0]+'</span></li>')+'</div></div>'
      +(j.second.length ? '<div class="b">↻ '+esc(Lg("Second look: ","مراجعة تانية: "))+j.second.map(v => esc(L1(v))).join(" · ")+'</div>' : "")
      +(alt ? '<div class="ru">'+esc(Lg("Compared with: ","اتقارنت بـ: "))+alt+'</div>' : "")+'</div>'; };
  const draw = () => {
    const keys = syms(), res = keys.map(s => [s, TC.res[S.style+"|"+s]]).filter(([, r]) => r), St = TCE.STYLES[S.style], fr = TC.record(S.style);
    let nI = 0, nAp = 0, cnt = {TAKE:0, WAIT:0, SKIP:0}; const why = {}, errs = [], notes = [];
    res.forEach(([s, r]) => { if (r.err){ errs.push(s.replace(/^HL:xyz:|^Y:/, "")+": "+r.err); return; } (r.notes || []).forEach(n => notes.push(s.replace(/^HL:xyz:|^Y:|-USDT.*$/g, "")+": "+n));
      r.ideas.forEach(x => { nI++; cnt[x.j.verdict]++; if (x.j.grade === "A+") nAp++; if (x.j.verdict !== "TAKE"){ const w = x.j.vetoes[0] ? L1(x.j.vetoes[0]) : (x.j.cons.slice().sort((a, b) => b[0] - a[0])[0] || [0, "", ""]); const t = typeof w === "string" ? w : L2(w); if (t){ const k = t.replace(/\s*\(.*$/, "").replace(/\b\d[\d.,]*\b(?![A-Za-z])/g, "#").slice(0, 50).trim(); why[k] = (why[k] || 0) + 1; } } }); });
    const top = Object.entries(why).sort((a, b) => b[1] - a[1]).slice(0, 4);
    const open = (Journal.list || []).filter(t => t.status === "open");
    sum.innerHTML = '<b style="color:#f0b90b">'+esc(ttTxt(S.style))+'</b> · '+St.bias+' → '+St.setup+' → '+St.entry+' · '+esc(Lg("target ","الهدف "))+(S.tgt ? S.tgt+Lg(" pts"," نقطة") : Lg("Auto","تلقائي"))
      +(TC.busy ? ' · <b class="b">'+esc(Lg("studying ","بيدرس "))+esc(TC.prog)+'</b>' : '')
      +'<br>'+esc(Lg("Studied ","اتدرس "))+res.length+'/'+keys.length+' '+esc(Lg("symbols","رمز"))+' · '+nI+' '+esc(Lg("ideas","فكرة"))+' · <b class="g">'+cnt.TAKE+' '+VT.TAKE+'</b> · <b style="color:#f0b90b">'+cnt.WAIT+' '+VT.WAIT+'</b> · <span class="m">'+cnt.SKIP+' '+VT.SKIP+'</span> · <b style="color:#f0b90b">A+ '+nAp+'</b>'
      +' · '+esc(Lg("open trades in the journal: ","صفقات مفتوحة في الجورنال: "))+open.length
      +(top.length ? '<br><span class="m">'+esc(Lg("Most common reasons not to enter: ","أكتر أسباب الرفض: "))+top.map(([k, n]) => esc(k)+" ("+n+")").join(" · ")+'</span>' : "")
      +(errs.length ? '<br><span class="r">'+esc(errs.slice(0, 3).join(" · "))+(errs.length > 3 ? " +"+(errs.length - 3) : "")+'</span>' : "")
      +(notes.length ? '<br><span class="m" title="'+esc(notes.join("\n"))+'">ⓘ '+esc(notes.slice(0, 2).join(" · "))+(notes.length > 2 ? " +"+(notes.length - 2) : "")+'</span>' : "")
      +'<br><span class="m">'+esc(Lg("Forward record (journal): ","السجل الفعلي (الجورنال): "))+fr.done+' '+esc(Lg("closed","مقفولة"))+' · '+fr.win+' TP · '+(fr.avgR == null ? "–" : (fr.avgR >= 0 ? "+" : "")+fr.avgR.toFixed(2)+"R")+(fr.done < 30 ? ' · '+esc(Lg("under 30 = not evidence","أقل من 30 = مش دليل")) : "")+'</span>';
    // best idea per symbol (after the side filter), then rank across symbols
    const list = []; res.forEach(([s, r]) => { const ids = (r.ideas || []).filter(dirOk); if (!ids.length) return; list.push([s, r, ids]); });
    list.sort((a, b) => (TC_VR[b[2][0].j.verdict] - TC_VR[a[2][0].j.verdict]) || (b[2][0].j.score - a[2][0].j.score));
    const bo = list.find(([, , ids]) => ids[0].j.verdict !== "SKIP");
    if (bo) sum.innerHTML += '<br>🏆 '+esc(Lg("Best of all now: ","الأفضل من الكل دلوقتي: "))+'<b>'+esc(bo[0].replace(/^HL:xyz:|^Y:|-USDT.*$/g, ""))+' '+(bo[2][0].side > 0 ? "▲" : "▼")+' '+esc(bo[2][0].label)+'</b> ('+VT[bo[2][0].j.verdict]+', '+bo[2][0].j.score+')';
    { const ns = TC.nextSession(), cand = list.filter(([, , ids]) => ids[0].j.verdict !== "SKIP" && ["session","vwap","struct","bounce","vp"].includes(ids[0].det)).slice(0, 5);
      if (ns && (S.style === "Scalp" || S.style === "Day Trade")) sum.innerHTML += '<br>⏰ '+esc(Lg("Next session: ","الجلسة الجاية: "))+'<b>'+esc(ns.name)+'</b> '+esc(Lg("in ","بعد "))+ns.in
        +(cand.length ? ' · '+esc(Lg("candidates before it: ","المرشحين قبلها: "))+cand.map(([s_, , ids]) => esc(s_.replace(/^HL:xyz:|^Y:|-USDT.*$/g, ""))+" "+(ids[0].side > 0 ? "▲" : "▼")+" "+esc(ids[0].label)).join(" · ") : ""); }
    { const lb = TC.DETS.map(d => [d, TC.record(S.style, d[0])]).filter(([, r]) => r.done > 0).sort((x, y) => (y[1].avgR || 0) - (x[1].avgR || 0));
      sum.innerHTML += '<br><span class="m">📚 '+esc(Lg("Schools in your journal (","المدارس في الجورنال ("))+esc(ttTxt(S.style))+'): '+(lb.length ? lb.map(([d, r]) => esc(Lg(d[1], d[2]))+" "+r.done+" · "+Math.round(100*r.win/r.done)+"% · "+(r.avgR >= 0 ? "+" : "")+r.avgR.toFixed(2)+"R").join(" | ")
        +esc(Lg(" — the engine adds / removes weight from a school after 10 closed trades; under 30 = not evidence"," — المحرك بيزوّد / يقلل وزن المدرسة بعد 10 صفقات مقفولة؛ أقل من 30 = مش دليل")) : esc(Lg("no closed trades yet","لسه مفيش صفقات مقفولة")))+'</span>'; }
    let h = "", shown = 0;
    list.forEach(([s, r, ids]) => { const x = ids[0]; if (!showOk(x.j.verdict, x.j.grade)) return; shown++;
      const others = ids.slice(1, 4).map(o => esc(o.label)+" ("+VT[o.j.verdict]+", "+o.j.score+")").join(" · ");
      h += cardHtml(s, r, x, 0, others ? others+esc(Lg(" — lower score after the same checks"," — نتيجتهم أقل بعد نفس الفحص")) : "");
      if (ids.length > 1 && S.show === "all") h += '<details style="margin:0 4px 6px"><summary>'+esc(Lg("All ideas on ","كل الأفكار على "))+esc(s)+' ('+ids.length+')</summary>'+ids.slice(1).map((o, k) => cardHtml(s, r, o, k + 1, "")).join("")+'</details>'; });
    if (!shown) h = '<div class="err" style="color:#848e9c;padding:10px">'+esc(TC.busy ? Lg("studying…","بيدرس…") : !res.length ? Lg("Press “Study now”.","اضغط «ادرس دلوقتي».") : S.show === "take" ? Lg("Nothing passed as TAKE. Switch Show to TAKE + WAIT or all to see why.","مفيش حاجة عدّت «ادخل». غيّر العرض لـ«ادخل + استنى» أو «الكل» عشان تشوف ليه.") : Lg("No idea passed. Switch Show to all to see the rejected ones and why.","مفيش فكرة عدّت. غيّر العرض لـ«الكل» عشان تشوف المرفوض وليه."))+'</div>';
    box.innerHTML = h;
    box.querySelectorAll(".cd").forEach(d => d.onclick = () => { const s = d.dataset.s, r = TC.res[S.style+"|"+s]; if (!r) return; const ids = r.ideas.filter(dirOk), x = ids[+d.dataset.i]; if (x) Ws.showOnChart(TC.card(s, S.style, x, r)); });
    if (S.push !== false) TC.push(S.style);
  };
  draw(); go(false); const iv = setInterval(() => go(false), 30000);
  TC.subs.add(draw); Journal.subs.add(draw);
  this.unwatch = () => { clearInterval(iv); TC.subs.delete(draw); Journal.subs.delete(draw); };
};
