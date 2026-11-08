/* World Monitor: Finnhub headlines + free RSS (BBC / Al Jazeera / Reuters ...), filtered by the news-widget switches */
const feedMsg = () => (CFG.feedStatus || []).join(" | ");
const worldItems = (wm = {eco:1, pol:1, geo:1, ar:1, en:1}) => {
  const tp = {economic:"eco", political:"pol", geopolitical:"geo"};
  return (CFG.news || []).map(n => Object.assign({topic:"economic", lang:"en"}, n)).concat(CFG.world || [])
    .filter(n => wm[tp[n.topic] || "eco"] && wm[n.lang === "ar" ? "ar" : "en"]).sort((a,b) => (b.ts || 0) - (a.ts || 0));
};
const SYM_RE = /^[A-Z0-9]{2,12}-[A-Z0-9]{2,6}(-SWAP|-\d{6}(-\d+(\.\d+)?-[CP])?)?$/;
const extraSyms = store.get(LS+"_syms", []).filter(x => SYM_RE.test(x) || /^HL:[a-z]+:[A-Z0-9]+$/.test(x));
extraSyms.forEach(x => { if (!SYMS.includes(x)) SYMS.push(x); });
// Long/Short + trade-type filters chosen above the scanner table (Streamlit side) apply to chart overlays and alert cards too
const FILT = Object.assign({side:"All", tt:"All", st:[], tf:"All", cls:"All"}, store.get(LS+"_filt", {}));
if (!Array.isArray(FILT.st)) FILT.st = [];
// strategy filter: id = the setup-tag label the scanner puts on a trade (Arabic key), label = what the user sees
const STRATS = [["موجة 3","Wave 3"],["اليوت","Elliott"],["MSB-OB","MSB + OB"],["OB","Order Block"],["FVG","FVG"],["OTE","OTE"],["بريكر","Breaker"],["يونيكورن","Unicorn"],["يهوذا","Judas"],["سيولة","Liquidity sweep"],["اختراق","Breakout"],["دعم/مقاومة","Support/Resistance"],["فيبو","Fibonacci"],["VWAP","VWAP"],["متوسطات","Moving averages"],["كسر ترند","Trendline break"],["CISD","Sweep + CISD"],["Model 2022","ICT Model 2022"],["زومبي","Zombie"],["SMT","SMT divergence"],["CRT","CRT (range sweep)"],["دايفرجنس RSI","RSI divergence"],["دايفرجنس MACD","MACD divergence"],["Donchian","Donchian ensemble"],["SMA 10/40","SMA 10/40 (hedge fund)"],["تيرتل 55","Donchian 55 (Turtle)"],["جلسات AMD","Session AMD"],["نطاق الافتتاح","Opening range"],["KZ سنايبر","Kill Zone Sniper"],["Power of 3","Power of Three"]];
/* strategy x timeframe TP1 hit-rates from the walk-forward backtest (modules/backtest_tf.py) */
function tfInfo(e){
  const T_ = CFG.tfstats && CFG.tfstats.stats; if (!T_) return null; const min = CFG.tfstats.min_n || 8, tf = e.tfk, best = CFG.tfstats.best || {};
  const tags = (e.tags || []).map(t => t[0]).filter(g => T_[g] && T_[g][tf] && T_[g][tf].n >= min);
  if (tags.length){ const hit = tags.reduce((s,g) => s + T_[g][tf].hit, 0)/tags.length, n = Math.min(...tags.map(g => T_[g][tf].n)); return {hit, n, isBest: tags.some(g => best[g] === tf), bestTf: best[tags[0]] || ""}; }
  const a = T_["*"] && T_["*"][tf]; return a && a.n >= min ? {hit:a.hit, n:a.n, isBest: best["*"] === tf, bestTf: best["*"] || ""} : null;
}
const wScore = e => { const r = e.score/Math.max(1,e.max), i = tfInfo(e); return i ? r*(0.75 + 0.5*i.hit) : r; };   // timeframes that historically hit TP1 more often rank higher
const tfTxt = e => { const i = tfInfo(e); return i ? "TP1 "+Math.round(100*i.hit)+"% · n"+i.n+(i.isBest ? " ★" : "") : ""; };
// a trade plan must point the way its direction says: long = stop < entry < targets, short = stop > entry > targets
const planOk = (pl, dir) => { if (!pl || !pl.tps || !pl.tps.length || !(pl.stop > 0) || !(pl.entry > 0)) return false;
  if (dir === "bullish") return pl.stop < pl.entry && pl.tps.every(t => t > pl.entry);
  if (dir === "bearish") return pl.stop > pl.entry && pl.tps.every(t => t < pl.entry);
  return true; };
// timing layer: where is price NOW relative to a plan? -> {k: key, o: sort order}
function planTiming(e, p){
  const pl = e.plan; if (!pl || !(p > 0)) return {k:"tmNA", o:5};
  const long_ = e.direction === "bullish", risk = Math.abs(pl.entry - pl.stop), sgn = long_ ? 1 : -1; if (!risk) return {k:"tmNA", o:5};
  if (sgn*(p - pl.stop) <= 0) return {k:"tmStop", o:6};
  if (sgn*(p - pl.tps[0]) >= 0) return {k:"tmTp", o:7};
  const d = sgn*(p - pl.entry)/risk, prog = sgn*(p - pl.entry)/Math.abs(pl.tps[0] - pl.entry);
  if (Math.abs(d) <= 0.25) return {k:"tmNow", o:0};
  if (d < 0) return {k:"tmWait", o:1};
  return prog >= 0.5 ? {k:"tmLate", o:3} : {k:"tmRun", o:2};
}
// 'special mark' set-up: forex plan with a 30-50 pip stop and a 120+ pip target (forex only; a 'pip' on gold / indices / crypto is ambiguous, so they are never marked)
function pipSetup(e){
  const m = /^Y:([A-Z]{6})=X$/.exec(e.symbol || ""); if (!m || !e.plan) return null;
  const pip = m[1].endsWith("JPY") ? 0.01 : 0.0001, pl = e.plan, st = Math.abs(pl.entry - pl.stop)/pip, tp = Math.max(...pl.tps.map(t => Math.abs(t - pl.entry)))/pip;
  return st >= 30 && st <= 50 && tp >= 120 ? {st:Math.round(st), tp:Math.round(tp)} : null;
}
/* market class of a symbol, from the symbol alone (no fetch): used by the class filter of Ready / Signals / Alerts / Setup Card and by "Best of all" */
const CLS_LIST = ["Crypto","Metals","Oil & Gas","Indices","Forex","Stocks","Bonds","Options"];
function symClass(sym){
  sym = String(sym || ""); if (/-\d{6}-[\d.]+-[CP]$/.test(sym)) return "Options";
  if (/^HL:/.test(sym)) return hlCat(sym);
  if (/^FH:/.test(sym)) return /XAU|XAG|XPT|XCU/.test(sym) ? "Metals" : /SPX|NAS|US30|JP2|DE30|UK100/.test(sym) ? "Indices" : "Forex";
  if (/^Y:/.test(sym)){ const b = sym.slice(2); return /=X$/.test(b) ? "Forex" : /^\^/.test(b) ? "Indices" : /^(GC|SI|HG|PL|PA)=F$/.test(b) ? "Metals" : /^(CL|BZ|NG|HO)=F$/.test(b) ? "Oil & Gas" : /=F$/.test(b) ? "Other" : "Stocks"; }
  return "Crypto";
}
/* mini chart of a setup: last closes + entry / stop / TP1 (the scan sends e.spark); same idea as the old Scanner column */
function sparkSvg(e, W, H){ const v = (e && e.spark) || [], pl = e && e.plan; W = W || 72; H = H || 22; if (v.length < 2 || !pl) return "";
  const all = v.concat([pl.entry, pl.stop, pl.tps[0]]), lo = Math.min(...all), hi = Math.max(...all), y = p => (H-2-(p-lo)/((hi-lo)||1)*(H-4)).toFixed(1), pts = v.map((p, i) => (i*(W-1)/(v.length-1)).toFixed(1)+","+y(p)).join(" "), ln = (p, c, d) => '<line x1="0" x2="'+W+'" y1="'+y(p)+'" y2="'+y(p)+'" stroke="'+c+'" stroke-width=".8"'+(d ? ' stroke-dasharray="2 2"' : '')+'/>';
  return '<svg width="'+W+'" height="'+H+'" style="vertical-align:middle">'+ln(pl.tps[0], "#0ecb81", 1)+ln(pl.stop, "#f6465d", 1)+ln(pl.entry, "#4aa3ff", 0)+'<polyline points="'+pts+'" fill="none" stroke="'+(e.direction === "bullish" ? "#0ecb81" : "#f6465d")+'" stroke-width="1.2"/></svg>'; }
const clsCounts = () => { const n = {}; try { readyList(true).forEach(e => { const c = symClass(e.symbol); n[c] = (n[c] || 0) + 1; }); } catch(e){} return n; };   // ready setups per class (before the class filter): what the scan really produced
const CLS_SELS = new Set(), clsBroadcast = () => { const n = clsCounts(); CLS_SELS.forEach(x => { if (!x.isConnected){ CLS_SELS.delete(x); return; } [...x.options].forEach(o => { if (CLS_LIST.includes(o.value)) o.textContent = catL(o.value) + " (" + (n[o.value] || 0) + ")"; }); x.value = FILT.cls || "All"; }); }; setInterval(() => { if (CLS_SELS.size) clsBroadcast(); }, 5000);   // every class select shows the one shared FILT.cls
const clsOk = sym => !FILT.cls || FILT.cls === "All" || FILT.cls === "__best" || symClass(sym) === FILT.cls;
const clsOptions = () => [["All", T("fAll")], ["__best", Lg("Best of all","الأفضل من الكل")]].concat(CLS_LIST.map(c => [c, catL(c)]));
function readyList(noCls){
  const seen = new Map();
  const put = (e, t) => { if (!e || !e.plan || !planOk(e.plan, e.direction) || !passFilters(e.direction, e.ttype, e.tags || []) || (FILT.tf !== "All" && e.tfk !== FILT.tf) || (!noCls && !clsOk(e.symbol))) return; const k = e.symbol+"|"+e.direction+"|"+e.ttype; const old = seen.get(k);
    if (!old || (e.score/e.max) > (old.score/old.max)) seen.set(k, Object.assign({}, e, {_t:t||0})); };
  (CFG.ready || []).forEach(e => put(e, 0)); Alerts.list.forEach(a => put(a.card, a.t));
  let out = [...seen.values()].sort((a,b) => (wScore(b) - wScore(a)) || (b._t - a._t));
  if (!noCls && FILT.cls === "__best"){ const n = {}; out = out.filter(e => { const c = symClass(e.symbol); n[c] = (n[c] || 0) + 1; return n[c] <= 2; }); }   // "Best of all": the 2 strongest ready setups of every class, a ranking over what is already scanned (no new fetch)
  return out;
}
function passFilters(dir, ttype, tags){
  if (tags && FILT.st.length && !tags.some(t => FILT.st.includes(t[0]))) return false;
  if (FILT.side === "Long" && dir !== "bullish") return false;
  if (FILT.side === "Short" && dir !== "bearish") return false;
  if (FILT.tt && FILT.tt !== "All" && ttype && ttype !== FILT.tt) return false;
  return true;
}
const TAG_EN = {"سيولة":"Liquidity","اختراق":"Breakout","دعم/مقاومة":"S/R","زومبي":"Zombie","موجة 3":"Wave 3","بريكر":"Breaker","يهوذا":"Judas","اليوت":"Elliott","يونيكورن":"Unicorn","فيبو":"Fib","متوسطات":"MAs","دايفرجنس RSI":"RSI Div","دايفرجنس MACD":"MACD Div","Donchian":"Donchian","جلسات AMD":"Session AMD","نطاق الافتتاح":"Opening range","KZ سنايبر":"KZ Sniper","Power of 3":"Power of 3"};
const TAG_TIP_EN = {"سيولة":"Liquidity: price swept a cluster of stops/old highs-lows — often a reversal or continuation trigger.","اختراق":"Breakout: price closed through a key level with momentum.","دعم/مقاومة":"Support/Resistance: price is reacting at a level that held before.","زومبي":"Zombie: weak, drifting move with fading volume — low conviction.","موجة 3":"Wave 3: Elliott impulse wave 3 — usually the strongest, longest leg.","بريكر":"Breaker block: a failed order block that flipped — retests are entries.","يهوذا":"Judas swing: a fake early-session move to grab liquidity before the real direction.","اليوت":"Elliott wave count supports this direction.","يونيكورن":"Unicorn: breaker block overlapping a fair-value gap — high-probability zone.","فيبو":"Fibonacci confluence: entry sits in a key retracement zone (0.5–0.79).","متوسطات":"Moving averages aligned with the trade direction.","MSB-OB":"Market-structure break + order block.","OB":"Order block: the last opposite candle before an impulsive move.","FVG":"Fair-value gap: an imbalance price tends to revisit.","OTE":"Optimal Trade Entry: 0.62–0.79 retracement of the swing.","SMT":"SMT divergence: two correlated markets disagree at a swing — one makes a new extreme, the other refuses (reversal footprint).","CRT":"Candle Range Theory: price swept one side of a higher-timeframe candle range and closed back inside — target the opposite side.","دايفرجنس RSI":"RSI regular divergence: price makes a new extreme but RSI does not — momentum is fading.","دايفرجنس MACD":"MACD regular divergence: price makes a new extreme but MACD does not — momentum is fading.","جلسات AMD":"Session AMD (ICT): the Asian range was swept in London and price closed back inside - distribution toward the opposite side of the range.","نطاق الافتتاح":"Opening-range breakout: fresh close beyond the first-15-minute range of the London / New York open.","KZ سنايبر":"Kill Zone Sniper: inside a London / NY kill zone a candle swept the last 20-bar low and closed back above with a displacement body (and volume where available).","Power of 3":"Power of Three: the day opened, price was manipulated below the daily open inside a kill zone, then rebounded with a displacement candle back above the open.","Donchian":"Donchian ensemble: several breakout channels (5-360 bars) agree on a trend and a fresh breakout just fired. Position size shrinks as volatility rises."};
const tagTip = t => lang === "ar" ? (t[3] || "") : (TAG_TIP_EN[t[0]] || t[3] || "");
const tagTxt = x => lang === "ar" ? x : (TAG_EN[x] || x);
const etaTxt = x => lang === "ar" || !x ? (x || "-") : String(x).replace("دقيقة","min").replace("ساعة","h").replace("يوم","d").replace("أسبوع","w");
const TT_AR = {"Scalp":"سكالب","Day Trade":"داي تريد","Swing":"سوينج","Position":"بوزشن"};
const ttTxt = x => lang === "ar" ? (TT_AR[x] || x) : x;

/* Live context checklist (the schools that cannot be backtested here): order book + time & sales (live), time of day,
   fundamental (high-impact news, funding). One snapshot per symbol, cached 60 s. Journal stores the snapshot with every logged
   trade, so the journal measures over time whether "order flow agreed" / session / news actually change the result. */
const Ctx = {
  cache:{}, busy:{},
  session(t){ const f = new Intl.DateTimeFormat("en-GB", {timeZone:"America/New_York", hour:"2-digit", minute:"2-digit", hour12:false}).formatToParts(new Date(t || Date.now())),
      m = (+f.find(x => x.type === "hour").value % 24)*60 + +f.find(x => x.type === "minute").value;
    return m >= 120 && m < 300 ? "London KZ" : m >= 420 && m < 600 ? "NY AM KZ" : m >= 810 && m < 960 ? "NY PM KZ" : m >= 1200 || m < 120 ? "Asia" : "off-KZ"; },
  news(sym, t){ const now = t || Date.now(), cur = ["USD"].concat((/^(?:FH:|Y:)?([A-Z]{3})_?([A-Z]{3})/.exec(String(sym).replace("HL:xyz:","")) || []).slice(1));
    const hit = (CFG.cal || []).filter(e => e.impact === "High" && e.ts >= now - 30*60e3 && e.ts <= now + 60*60e3 && cur.includes(e.country)); return hit.length ? hit[0] : null; },
  async get(sym){
    // many setups / scanner symbols call this at once: each symbol is refreshed at most every 5 min, and the OKX open-interest call is skipped during a rate-limit pause
    const c = this.cache[sym]; if ((c && Date.now() - c.t < 300000) || this.busy[sym] || /^(Y|FH):/.test(sym)) return c; this.busy[sym] = true;
    const out = {t:Date.now(), of:null, fund:null};
    try {
      const [bk, tr] = await Promise.all([okx("/market/books?instId="+encodeURIComponent(sym)+"&sz=400").catch(() => null), okx("/market/trades?instId="+encodeURIComponent(sym)+"&limit=100").catch(() => null)]);
      let bi = null, de = null;
      if (bk && bk[0] && bk[0].bids && bk[0].bids.length && bk[0].asks.length){ const b0 = +bk[0].bids[0][0], a0 = +bk[0].asks[0][0], mid = (b0 + a0)/2; let bd = 0, ad = 0;
        bk[0].bids.forEach(x => { if ((mid - +x[0])/mid <= .005) bd += +x[1]; }); bk[0].asks.forEach(x => { if ((+x[0] - mid)/mid <= .005) ad += +x[1]; }); if (bd + ad > 0) bi = (bd - ad)/(bd + ad); }
      if (tr && tr.length){ const t0 = Math.max(...tr.map(x => +x.ts)) - 120000; let b = 0, s_ = 0; tr.forEach(x => { if (+x.ts < t0) return; x.side === "buy" ? b += +x.sz : s_ += +x.sz; }); if (b + s_ > 0) de = (b - s_)/(b + s_); }
      out.of = {book:bi, delta:de};
      if (!/^HL:/.test(sym)){ const base = sym.split("-")[0], rubOk = Date.now() >= OKX_COOL;
        const [f, oiH, cd] = await Promise.all([okx("/public/funding-rate?instId="+base+"-USDT-SWAP").catch(() => null),
          rubOk ? okx("/rubik/stat/contracts/open-interest-volume?ccy="+base+"&period=1H").catch(() => null) : null, okx("/market/candles?instId="+base+"-USDT-SWAP&bar=1H&limit=6").catch(() => null)]);
        if (f && f[0]) out.fund = +f[0].fundingRate;
        if (oiH && oiH.length > 4 && cd && cd.length > 4){ const oi4 = (+oiH[0][1]/+oiH[4][1] - 1)*100, p4 = (+cd[0][4]/+cd[4][4] - 1)*100;
          out.oi = {oi4, p4, read: p4 >= 0 && oi4 >= 0 ? "longs" : p4 >= 0 ? "cover" : oi4 >= 0 ? "shorts" : "closing"}; } }
    } catch(e){}
    this.cache[sym] = out; this.busy[sym] = false; return out; },
  // verdicts for one side: "agree" / "against" / "mixed" / "n/a"
  ofVerdict(c, dir){ const o = c && c.of; if (!o || (o.book == null && o.delta == null)) return "n/a"; const d = dir === "bullish" ? 1 : -1, v = [o.book, o.delta].filter(x => x != null).map(x => Math.sign(x)*(Math.abs(x) >= .1 ? 1 : 0)*d);
    return v.every(x => x > 0) ? "agree" : v.every(x => x < 0) ? "against" : "mixed"; },
  fundFlag(c, dir){ const f = c && c.fund; if (f == null) return null; return dir === "bullish" && f > .0005 ? "crowded longs" : dir === "bearish" && f < -.0005 ? "crowded shorts" : null; },
  // price x open interest over 4 h vs the trade side: new longs back a long, short covering is a weak rise, new shorts / longs closing push down
  oiFlag(c, dir){ const o = c && c.oi; if (!o) return {k:"na", txt:"–"}; const L_ = dir === "bullish", r = o.read;
    const txt = (o.oi4 > 0 ? "+" : "")+o.oi4.toFixed(1)+"% OI · "+({longs:Lg("new longs","لونجات جديدة"), cover:Lg("short covering","تغطية شورت"), shorts:Lg("new shorts","شورتات جديدة"), closing:Lg("longs closing","لونجات بتقفل")})[r];
    const k = L_ ? (r === "longs" ? "ok" : r === "cover" ? "mid" : "bad") : (r === "shorts" ? "ok" : r === "closing" ? "mid" : "bad"); return {k, txt, read:r}; },
  snapshot(sym, dir){ const c = this.cache[sym]; return {of:this.ofVerdict(c, dir), ses:this.session(), news:!!this.news(sym), fund:this.fundFlag(c, dir), oi:this.oiFlag(c, dir).read || null}; }
};
const Alerts = {
  list: store.get(LS+"_alerts", []).filter(a => a.kind === "scan" && a.card), subs: new Set(),
  add(id, kind, sym, text, color, card){
    { const old = this.list.find(a => a.id === id); if (old){ if (card && card.ana && !(old.card && old.card.ana)){ old.card = card; store.set(LS+"_alerts", this.list); this.subs.forEach(f => f()); } return; } }   // an older stored copy without the Arabic analysis gets it filled in
    if (card){ const g = card.symbol+"|"+card.direction+"|"+card.ttype; this.list = this.list.filter(a => !(a.card && a.card.symbol+"|"+a.card.direction+"|"+a.card.ttype === g)); }
    this.list.unshift({id, t:Date.now(), kind, sym, text, color, card}); this.list = this.list.slice(0, 200);
    store.set(LS+"_alerts", this.list); this.subs.forEach(f => f());
  },
  clear(){ this.list = []; store.set(LS+"_alerts", this.list); this.subs.forEach(f => f()); }
};
(CFG.alerts || []).forEach(a => {
  const bull = a.direction === "bullish";
  Alerts.add(a.id, "scan", a.symbol, a.symbol+" · "+(bull ? "Long" : "Short")+" · "+a.score+"/"+a.max, bull ? "#0ecb81" : "#f6465d", a);
});

const YF = CFG.yf || {}, YF_BAR = {"15m":"15m","1H":"1h","4H":"4h","1D":"1d"};
function yfOkx(path){   // markets OKX does not list (forex / indices / EGX / Tadawul): candles were embedded by the server from Yahoo Finance, answered here in OKX's shape (newest first)
  const q = new URLSearchParams(path.split("?")[1] || ""), sym = q.get("instId"), D = YF[sym];
  if (/\/history-candles/.test(path)) return [];
  if (!D) throw new Error("no data for "+sym+" (Yahoo feed)");
  if (/\/market\/ticker/.test(path)){ const h = D["1h"] || D["1d"] || [], d = D["1d"] || h; if (!h.length) throw new Error("no data"); const l = h[h.length-1][4], pv = d.length > 1 ? d[d.length-2][4] : d[0][1]; return [{instId:sym, last:String(l), open24h:String(pv), vol24h:"0"}]; }
  if (/\/market\/candles/.test(path)){ const k = YF_BAR[q.get("bar")]; if (!k || !D[k]) throw new Error("timeframe "+q.get("bar")+" not available for this market (15m / 1H / 4H / 1D only)"); const lim = +q.get("limit") || 100; return D[k].slice(-lim).reverse().map(r => [String(r[0]), String(r[1]), String(r[2]), String(r[3]), String(r[4]), String(r[5]), "0", "0", "1"]); }
  throw new Error("not available for this market (Yahoo feed)");
}
