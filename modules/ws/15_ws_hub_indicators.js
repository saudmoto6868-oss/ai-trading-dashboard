/* ---------------- OKX WebSocket (live ticks; REST polling keeps running as a fallback) ---------------- */
const WSX = {
  conns:{}, subs:{},
  conn(kind){
    let c = this.conns[kind]; if (c) return c;
    c = this.conns[kind] = {ws:null, ready:false, kind};
    const open = () => {
      let ws; try { ws = new WebSocket(WSB + "/" + kind); } catch(e){ return setTimeout(open, 5000); }
      c.ws = ws;
      ws.onopen = () => { c.ready = true; Object.values(this.subs).filter(x => x.kind === kind).forEach(x => ws.send(JSON.stringify({op:"subscribe", args:[x.arg]})));
        c.ping = setInterval(() => { try{ ws.send("ping"); }catch(e){} }, 20000); };
      ws.onmessage = ev => {
        c.last = Date.now(); if (ev.data === "pong") return;
        let m; try { m = JSON.parse(ev.data); } catch(e){ return; }
        if (!m.arg || !m.data) return;
        const x = this.subs[JSON.stringify(m.arg)]; if (x) x.cbs.forEach(cb => { try{ cb(m.data); }catch(e){ console.error(e); } });
      };
      ws.onclose = () => { c.ready = false; clearInterval(c.ping); setTimeout(open, 3000); };
      ws.onerror = () => { try{ ws.close(); }catch(e){} };
    };
    open(); return c;
  },
  sub(kind, arg, cb){
    const c = this.conn(kind), key = JSON.stringify(arg);
    const x = this.subs[key] = this.subs[key] || {arg, kind, cbs:new Set()};
    x.cbs.add(cb);
    if (c.ready && x.cbs.size === 1) c.ws.send(JSON.stringify({op:"subscribe", args:[arg]}));
    return () => { x.cbs.delete(cb); if (!x.cbs.size){ delete this.subs[key]; if (c.ready) try{ c.ws.send(JSON.stringify({op:"unsubscribe", args:[arg]})); }catch(e){} } };
  }
};

/* ---------------- data hub (one poll per symbol/kind, shared by all widgets) ---------------- */
const SIG_IND = ["zn", "bso", "rm", "r2"];   // indicators that draw BUY/SELL marks today (more join this list as the new indicators are added)
const Lg = (a, b) => lang === "ar" ? b : a;
const CATL = {"Crypto":["Crypto","كريبتو"], "Forex":["Forex","فوركس"], "Metals":["Metals","معادن"], "Oil & Gas":["Oil & Gas","نفط وغاز"], "Commodities":["Commodities","سلع"], "Indices":["Indices","مؤشرات"], "Stocks":["Stocks","أسهم"], "Bonds":["Bonds","سندات"],
  "Options":["Options","خيارات"], "Meme coins":["Meme coins","عملات ميم"], "Egypt (EGX)":["Egypt (EGX)","مصر (EGX)"], "Saudi (Tadawul)":["Saudi (Tadawul)","السعودية (تداول)"]};
const catL = c => CATL[c] ? Lg(CATL[c][0], CATL[c][1]) : c;   // market-category names: the value stays English (used for filtering), the label follows the language
/* Logo of a symbol (same rules as modules/symbol_icon.py): coin icon, flag(s) for forex, country flag for an index, company icon for a stock, drawn badge for metals / energy; a coloured letter if the image fails */
const SI_CUR = {USD:"us",EUR:"eu",GBP:"gb",JPY:"jp",CHF:"ch",CAD:"ca",AUD:"au",NZD:"nz",CNH:"cn",CNY:"cn",KRW:"kr",MXN:"mx",TRY:"tr",INR:"in",BRL:"br",SAR:"sa",EGP:"eg",ZAR:"za",SEK:"se",NOK:"no",DKK:"dk",HKD:"hk",SGD:"sg",PLN:"pl",AED:"ae"};
const SI_METAL = {XAU:["Au","#f0b90b"],GOLD:["Au","#f0b90b"],GC:["Au","#f0b90b"],XAG:["Ag","#aab2bd"],SILVER:["Ag","#aab2bd"],SI:["Ag","#aab2bd"],XPT:["Pt","#8fa3b5"],PLATINUM:["Pt","#8fa3b5"],PL:["Pt","#8fa3b5"],XPD:["Pd","#9aa7b3"],PALLADIUM:["Pd","#9aa7b3"],PA:["Pd","#9aa7b3"],COPPER:["Cu","#b87333"],XCU:["Cu","#b87333"],HG:["Cu","#b87333"]};
const SI_ENERGY = new Set(["CL","WTI","BRENT","BZ","OIL","NG","NATGAS","USOIL","UKOIL","XTI","XBR","GAS"]);
const SI_INDEX = {SPX:"us",SP500:"us",US500:"us",GSPC:"us",NDX:"us",XYZ100:"us",US100:"us",IXIC:"us",DJI:"us",US30:"us",RUT:"us",VIX:"us",SPY:"us",QQQ:"us",IWM:"us",DIA:"us",DX:"us",DAX:"de",GER40:"de",GDAXI:"de",FTSE:"gb",UK100:"gb",HSI:"hk",N225:"jp",JP225:"jp",KR200:"kr",CAC40:"fr",FCHI:"fr",CASE30:"eg",TASI:"sa"};
const SI_STOCK = {AAPL:"apple.com",MSFT:"microsoft.com",NVDA:"nvidia.com",TSLA:"tesla.com",AMZN:"amazon.com",GOOGL:"google.com",GOOG:"google.com",META:"meta.com",AMD:"amd.com",INTC:"intel.com",MU:"micron.com",MRVL:"marvell.com",NET:"cloudflare.com",CRWD:"crowdstrike.com",MSTR:"strategy.com",COIN:"coinbase.com",MRNA:"modernatx.com",CRCL:"circle.com",NBIS:"nebius.com",CRWV:"coreweave.com",BE:"bloomenergy.com",SNDK:"sandisk.com",WDC:"westerndigital.com",AAOI:"ao-inc.com",LITE:"lumentum.com",SMSN:"samsung.com",SAMSUNG:"samsung.com",SKHX:"skhynix.com",SKHY:"skhynix.com",SKHYNIX:"skhynix.com",UNITREE:"unitree.com",CXMT:"cxmt.com",ZHIPU:"zhipuai.cn",NFLX:"netflix.com",PLTR:"palantir.com",HOOD:"robinhood.com",ORCL:"oracle.com",AVGO:"broadcom.com",TSM:"tsmc.com",BABA:"alibaba.com",UBER:"uber.com",DRAM:"roundhillinvestments.com",SOXL:"direxion.com",SOXS:"direxion.com",TLT:"ishares.com",SPCX:"spacex.com",EWY:"ishares.com",KORU:"direxion.com"};
function symIcon(sym, px){
  px = px || 14; sym = String(sym || "");
  const b = (sym.indexOf(":") >= 0 ? sym.split(":").pop() : sym).replace("=X", "").replace("=F", "").replace("^", "").split("-")[0].toUpperCase();
  const lt = b.slice(0, 1), col = "hsl(" + (Math.abs(b.split("").reduce((a, ch) => (a * 31 + ch.charCodeAt(0)) | 0, 7)) % 360) + ",55%,36%)";   // fixed lightness: the old hash could give a pale colour under the white letter = an "empty" icon
  const base = "display:inline-block;width:"+px+"px;height:"+px+"px;border-radius:50%;vertical-align:middle;margin-inline-end:5px;";
  const letter = "background:"+col+";color:#fff;font:700 "+Math.max(8, px - 7)+"px/"+px+"px sans-serif;text-align:center;";
  const img = (url, extra) => '<img src="'+url+'" alt="" loading="lazy" style="'+base+'object-fit:cover;'+(extra || "")+'" data-l="'+esc(lt)+'" data-st="'+esc(base+letter)+'" onerror="var s=document.createElement(\'span\');s.textContent=this.dataset.l;s.style.cssText=this.dataset.st;this.replaceWith(s)">';
  const badge = (t, c) => '<span style="'+base+'background:'+c+';color:#111;font:800 '+Math.max(8, Math.round(px*(t.length > 1 ? .5 : .62)))+'px/'+px+'px sans-serif;text-align:center">'+esc(t)+'</span>';
  let pair = b.length === 6 && SI_CUR[b.slice(0, 3)] && SI_CUR[b.slice(3)] ? [b.slice(0, 3), b.slice(3)] : null;
  if (!pair && /^HL:/.test(sym) && SI_CUR[b] && b !== "USD") pair = ["EUR","GBP","AUD","NZD"].includes(b) ? [b, "USD"] : ["USD", b];   // Hyperliquid names the pair by its non-dollar currency
  const isYH = /^(Y|HL):/.test(sym);
  if (SI_METAL[b]) return badge(SI_METAL[b][0], SI_METAL[b][1]);
  if (SI_ENERGY.has(b)) return badge("◆", "#f0b90b");
  if (SI_INDEX[b]) return img("https://flagcdn.com/w80/"+SI_INDEX[b]+".png");
  if (SI_STOCK[b]) return img("https://www.google.com/s2/favicons?domain="+SI_STOCK[b]+"&sz=64");
  if (pair && isYH){ const w = Math.round(px*1.5); return '<span style="display:inline-block;width:'+w+'px;height:'+px+'px;position:relative;vertical-align:middle;margin-inline-end:5px">'+img("https://flagcdn.com/w80/"+SI_CUR[pair[1]]+".png", "position:absolute;right:0;top:0;margin:0;")+img("https://flagcdn.com/w80/"+SI_CUR[pair[0]]+".png", "position:absolute;left:0;top:0;margin:0;box-shadow:0 0 0 1.5px #0b0e11;")+'</span>'; }
  if (isYH && SI_CUR[b]) return img("https://flagcdn.com/w80/"+SI_CUR[b]+".png");
  if (isYH) return badge(lt, "#4aa3ff");
  return img("https://cdn.jsdelivr.net/gh/spothq/cryptocurrency-icons@master/32/color/"+b.toLowerCase()+".png");
}
/* Item 23 (phase 1): read a trade explanation aloud with the browser's own speech engine (Web Speech API) - free, no key,
   nothing leaves the device. Arabic text uses an Arabic voice when the device has one (ar-EG preferred, then any ar-*). */
const Voice = {
  ok: typeof window !== "undefined" && "speechSynthesis" in window,
  voice(isAr){ const v = this.ok ? speechSynthesis.getVoices() : []; return isAr ? (v.find(x => /^ar-EG/i.test(x.lang)) || v.find(x => /^ar/i.test(x.lang))) : (v.find(x => /^en-US/i.test(x.lang)) || v.find(x => /^en/i.test(x.lang))); },
  clean(t){ return String(t || "").replace(/[★☆▲▼●◐✓✗↗⚡•·🔊⏹]/gu, " ").replace(/\bTP(\d)/g, "T P $1").replace(/\bSL\b/g, "S L").replace(/\s+/g, " ").trim(); },
  speak(text, btn){ if (!this.ok) return false; if (speechSynthesis.speaking){ speechSynthesis.cancel(); if (btn) btn.textContent = "🔊"; return true; }
    const t = this.clean(text), isAr = /[\u0600-\u06FF]/.test(t), u = new SpeechSynthesisUtterance(t), v = this.voice(isAr);
    u.lang = v ? v.lang : (isAr ? "ar-EG" : "en-US"); if (v) u.voice = v; u.rate = isAr ? 0.95 : 1;
    if (btn){ btn.textContent = "⏹"; u.onend = u.onerror = () => { btn.textContent = "🔊"; }; }
    speechSynthesis.speak(u); return true; },
  button(getText){ const b = el("button", null, "🔊"); b.title = this.ok ? Lg("Read this aloud (tap again to stop)", "اقرا الكلام ده بصوت (اضغط تاني للإيقاف)") : Lg("This browser has no speech engine", "المتصفح ده مفيهوش قارئ صوتي");
    b.disabled = !this.ok; b.onpointerdown = e => e.stopPropagation(); b.onclick = e => { e.stopPropagation(); this.speak(getText(), b); }; return b; }
};
if (Voice.ok) try { speechSynthesis.getVoices(); speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices(); } catch(e){}
const smtPeers = sym => { const b = sym.split("-SWAP")[0].split("-").slice(0,2).join("-"), o = []; (CFG.smt || []).forEach(([a, c, inv]) => { if (a === b) o.push([c, !!inv]); else if (c === b) o.push([a, !!inv]); }); return o; };
function smtFind(A, B, inv){   // swing-by-swing divergence between two aligned candle arrays; returns [{i1,i2,side,j1,j2}] (side up = bullish)
  const n = A.length, out = []; if (n < 40) return out; const rg = A.slice(-14).reduce((a, x) => a + (x.h - x.l), 0)/14 || 1e-9, rgB = B.slice(-14).reduce((a, x) => a + (x.h - x.l), 0)/14 || 1e-9;
  const bl = i => inv ? -B[i].h : B[i].l, bh = i => inv ? -B[i].l : B[i].h;
  const pv = (key) => { const r = []; for (let i = 3; i < n-3; i++){ let ok = true; for (let k = i-3; k <= i+3 && ok; k++) if (k !== i && (key === "l" ? A[k].l < A[i].l : A[k].h > A[i].h)) ok = false; if (ok) r.push(i); } return r; };
  const wmin = (f, i) => { let m = Infinity, j = i; for (let k = Math.max(0, i-3); k <= Math.min(n-1, i+3); k++) if (f(k) < m){ m = f(k); j = k; } return [m, j]; };
  const wmax = (f, i) => { let m = -Infinity, j = i; for (let k = Math.max(0, i-3); k <= Math.min(n-1, i+3); k++) if (f(k) > m){ m = f(k); j = k; } return [m, j]; };
  const L = pv("l"); for (let q = 1; q < L.length; q++){ const i1 = L[q-1], i2 = L[q]; if (i2 - i1 < 5 || i2 - i1 > 60 || A[i2].l >= A[i1].l - 0.1*rg) continue; if (Math.min(...A.slice(i1+1, i2).map(x => x.l)) <= A[i2].l) continue;
    const [b1, j1] = wmin(bl, i1), [b2, j2] = wmin(bl, i2); if (b2 >= b1 + 0.1*rgB) out.push({i1, i2, side:"up", j1, j2}); }
  const H = pv("h"); for (let q = 1; q < H.length; q++){ const i1 = H[q-1], i2 = H[q]; if (i2 - i1 < 5 || i2 - i1 > 60 || A[i2].h <= A[i1].h + 0.1*rg) continue; if (Math.max(...A.slice(i1+1, i2).map(x => x.h)) >= A[i2].h) continue;
    const [b1, j1] = wmax(bh, i1), [b2, j2] = wmax(bh, i2); if (b2 <= b1 - 0.1*rgB) out.push({i1, i2, side:"dn", j1, j2}); }
  return out;
}
const DON_LB = [5,10,20,30,60,90,150,250,360];
/* regular divergences between price swings and an oscillator / volume (same rules as modules/signals.py: fractal pivots n=3, 5-60 bars apart, clean pair, 0.1 ATR beyond the previous swing).
   kind "rsi": oscillator must differ by >= 2 points and start below 45 (bull) / above 55 (bear); "macd": >= 0.03 ATR, MACD line below / above 0; "vol": the 5-bar average volume at the second swing is <= 80% of the first (momentum fading) */
function divFind(d, osc, kind){
  const n = d.length, out = []; if (n < 40 || !osc) return out;
  const rg = i => { let a = 0, c = 0; for (let k = Math.max(0, i-13); k <= i; k++){ a += d[k].h - d[k].l; c++; } return a/c || 1e-9; };
  const val = kind === "vol" ? i => { let a = 0, c = 0; for (let k = Math.max(0, i-2); k <= Math.min(n-1, i+2); k++){ a += d[k].v || 0; c++; } return a/c; } : i => osc[i];
  const piv = key => { const r = []; for (let i = 3; i < n-3; i++){ let ok = true; for (let k = i-3; k <= i+3 && ok; k++) if (k !== i && (key === "l" ? d[k].l < d[i].l : d[k].h > d[i].h)) ok = false; if (ok) r.push(i); } return r; };
  const L = piv("l"), H = piv("h");
  for (let q = 1; q < L.length; q++){ const i1 = L[q-1], i2 = L[q]; if (i2 - i1 < 5 || i2 - i1 > 60 || d[i2].l >= d[i1].l - 0.1*rg(i2)) continue; let lo = Infinity; for (let k = i1+1; k < i2; k++) lo = Math.min(lo, d[k].l); if (lo <= d[i2].l) continue;
    const o1 = val(i1), o2 = val(i2), thr = kind === "rsi" ? 2 : kind === "macd" ? 0.03*rg(i2) : 0;
    const ok = kind === "vol" ? o1 > 0 && o2 <= 0.8*o1 : (o2 - o1 >= thr && o1 < (kind === "rsi" ? 45 : 0)); if (ok) out.push({i1, i2, side:"up"}); }
  for (let q = 1; q < H.length; q++){ const i1 = H[q-1], i2 = H[q]; if (i2 - i1 < 5 || i2 - i1 > 60 || d[i2].h <= d[i1].h + 0.1*rg(i2)) continue; let hi = -Infinity; for (let k = i1+1; k < i2; k++) hi = Math.max(hi, d[k].h); if (hi >= d[i2].h) continue;
    const o1 = val(i1), o2 = val(i2), thr = kind === "rsi" ? 2 : kind === "macd" ? 0.03*rg(i2) : 0;
    const ok = kind === "vol" ? o1 > 0 && o2 <= 0.8*o1 : (o1 - o2 >= thr && o1 > (kind === "rsi" ? 55 : 0)); if (ok) out.push({i1, i2, side:"dn"}); }
  return out;
}
function donState(c, n){ let st = 0, age = 0; for (let i = n; i < c.length; i++){ let hi = -Infinity, lo = Infinity; for (let j = i-n; j < i; j++){ if (c[j] > hi) hi = c[j]; if (c[j] < lo) lo = c[j]; } const nw = c[i] > hi ? 1 : c[i] < lo ? -1 : st; age = nw !== st ? 0 : age + 1; st = nw; } return [st, age]; }
function amdPhase(d){   // ICT Power of 3 on the last candles: Accumulation (tight range) -> Manipulation (sweep of the range extreme + close back inside) -> Distribution (expansion beyond the range)
  const n = d.length; if (n < 30) return {phase:"?"};
  const atr = d.slice(-30, -1).reduce((a, x) => a + (x.h - x.l), 0)/29 || 1e-12, base = d.slice(-26, -4), hi = Math.max(...base.map(x => x.h)), lo = Math.min(...base.map(x => x.l)), rec = d.slice(-4), last = d[n-1];
  const sLo = rec.some(x => x.l < lo - 0.1*atr) && last.c > lo, sHi = rec.some(x => x.h > hi + 0.1*atr) && last.c < hi;
  if (sLo && !sHi) return {phase:"M", dir:"up"}; if (sHi && !sLo) return {phase:"M", dir:"dn"};
  const mv = last.c - d[n-7].c; if (Math.abs(mv) >= 2.5*atr && (last.c > hi || last.c < lo)) return {phase:"D", dir:mv > 0 ? "up" : "dn"};
  const r12 = d.slice(-12); if (Math.max(...r12.map(x => x.h)) - Math.min(...r12.map(x => x.l)) <= 3.5*atr) return {phase:"A"};
  return {phase:"-"};
}
const Hub = {
  subs:{}, last:{}, timers:{}, an:{},
  sub(kind, sym, cb){
    const key = kind+"|"+sym;
    (this.subs[key] = this.subs[key] || new Set()).add(cb);
    if (this.last[key]) cb(this.last[key]);
    if (!this.timers[key]) this.start(key, kind, sym);
    return () => { const s = this.subs[key]; s.delete(cb); if (!s.size){ clearTimeout(this.timers[key]); delete this.timers[key]; delete this.last[key]; if (kind === "trades") delete this.an[sym]; } };
  },
  tkKeep(m, AS){   // last good price per symbol (also kept in this browser): a failed / rate-limited OKX ticker call shows the previous number with a 'delayed' marker instead of an empty row
    if (!this.tkGood){ this.tkGood = {}; try { this.tkGood = JSON.parse(localStorage.getItem(LS+"_tk") || "{}") || {}; } catch(e){} }
    const now = Date.now(), G = this.tkGood; let n = 0;
    AS.forEach(s => { const x = m[s]; if (x && x.last > 0){ G[s] = {last:x.last, open:x.open || 0, hi:x.hi || 0, lo:x.lo || 0, t:now}; n++; } else { const g = G[s]; if (g && now - g.t < 86400000) m[s] = Object.assign({}, g, {stale:1}); } });
    if (n && now - (this.tkSaved || 0) > 30000){ this.tkSaved = now; try { const o = {}; AS.forEach(s => { if (G[s]) o[s] = G[s]; }); localStorage.setItem(LS+"_tk", JSON.stringify(o)); } catch(e){} }
    return m; },
  kick(key){ if (this.busy && this.busy[key]) return; clearTimeout(this.timers[key]); this.tickFns && this.tickFns[key] && this.tickFns[key](); },
  start(key, kind, sym){
    const every = kind === "tickers" ? 3000 : 1500;
    const tick = async () => {
      if (!this.subs[key] || !this.subs[key].size) return;
      (this.busy = this.busy || {})[key] = true;
      try {
        let payload;
        if (/^Y:/.test(sym) && (kind === "book" || kind === "trades")){ payload = {error:"no order book / tape for this market (Yahoo feed)"}; }
        else if (kind === "book"){
          let d; try { d = (await okx("/market/books-full?instId="+encodeURIComponent(sym)+"&sz=2000"))[0]; if (!d || !d.bids || d.bids.length < 5) throw 0; } catch(e){ d = (await okx("/market/books?instId="+encodeURIComponent(sym)+"&sz=400"))[0]; }   // up to 2000 levels a side = the widest band OKX's REST book gives; falls back to 400
          const bb = d.bids.map(x=>({p:+x[0],q:+x[1]})), aa = d.asks.map(x=>({p:+x[0],q:+x[1]}));
          payload = { bids:bb.slice(0,50), asks:aa.slice(0,50), deep:{bids:bb, asks:aa} };   // every other panel keeps the nearest 50 levels; the order-flow heat map gets the full 400 so it fills the chart top to bottom
        } else if (kind === "trades"){
          const d = await okx("/market/trades?instId="+encodeURIComponent(sym)+"&limit=100");
          { const mx = d.length ? Math.max(...d.map(x => +x.ts || 0)) : 0; if (mx > 0 && Math.abs(mx - nowS()) > 60000) SKEW = Math.round(mx - Date.now()); }   // PC clock wrong and /public/time failed: take the exchange time from the prints
          payload = this.analyze(sym, d.map(x=>({id:x.tradeId, t:+x.ts, p:+x.px, q:+x.sz, side:x.side==="buy"?"Buy":"Sell"})).reverse());
        } else if (kind === "tickers"){
          const AS = SYMS.concat([...(Hub.extra || [])]), types = ["SPOT"], optU = [...new Set(AS.filter(s => /-\d{6}-[\d.]+-[CP]$/.test(s)).map(s => s.split("-").slice(0,2).join("-")))]; if (AS.some(s => /-SWAP$/.test(s))) types.push("SWAP"); if (AS.some(s => /-\d{6}$/.test(s))) types.push("FUTURES");
          const m = {}; Object.entries(HL.q).forEach(([k, x]) => { if (x.last) m[k] = {last:x.last, open:x.open || 0, live:1}; }); FH_LIST.forEach(x => { const q = FH.q[x.id]; if (q) m[x.id] = {last:q.last, open:FH.ref(x), live:1}; }); (await Promise.all(types.map(t => okx("/market/tickers?instType="+t).catch(() => [])).concat(optU.map(u => okx("/market/tickers?instType=OPTION&uly="+u).catch(() => []))))).forEach(d => d.forEach(x => m[x.instId] = {last:+x.last, open:+x.open24h, bid:+x.bidPx || 0, ask:+x.askPx || 0, hi:+x.high24h || 0, lo:+x.low24h || 0})); Object.keys(YF).forEach(y => { const D = YF[y], h = D["1h"] || D["1d"] || [], d = D["1d"] || h; if (h.length) m[y] = {last:h[h.length-1][4], open:(d.length > 1 ? d[d.length-2][4] : d[0][1])}; });
          payload = this.tkKeep(m, AS);
        }
        this.last[key] = payload; (this.fails = this.fails || {})[key] = 0; setStatus(true);
        this.subs[key] && this.subs[key].forEach(cb => { try{ cb(payload); }catch(e){ console.error(e);} });
      } catch(e){ this.fails = this.fails || {}; this.fails[key] = (this.fails[key] || 0) + 1;
        if (this.last[key] && this.fails[key] < 8) { /* keep showing the last good book / tape for ~12 s of failures instead of replacing the panel with an error */ }
        else { setStatus(false); this.subs[key] && this.subs[key].forEach(cb => { try{ cb({error:String(e.message||e)}); }catch(_){} }); } }
      this.busy[key] = false; clearTimeout(this.timers[key]);
      if (this.subs[key] && this.subs[key].size) this.timers[key] = setTimeout(tick, every);
    };
    (this.tickFns = this.tickFns || {})[key] = tick;
    this.timers[key] = setTimeout(tick, 0);
  },
  /* tape analysis: new-print flags, SMART/WHALE tiers, absorption, stats */
  analyze(sym, rows){
    const st = this.an[sym] = this.an[sym] || {seen:new Set(), first:true};
    const med = median(rows.map(r=>r.q)) || 1e-12;
    rows.forEach(r => {
      r.isNew = !st.first && !st.seen.has(r.id);
      r.tier = r.q >= settings.smart*2.5*med ? "whale" : r.q >= settings.smart*med ? "smart" : "normal";
      r.absorb = false; r.adir = "";
      r.notional = r.p*r.q;
    });
    rows.forEach(r => st.seen.add(r.id));
    if (st.seen.size > 800) st.seen = new Set(rows.map(r=>r.id));
    st.first = false;
    // absorption: heavy volume at ONE price while the window barely moved
    if (rows.length >= 10){
      const ps = rows.map(r=>r.p), lo = Math.min(...ps), hi = Math.max(...ps), mid = median(ps);
      if (mid > 0 && (hi-lo)/mid*100 <= 0.05){
        const lv = {};
        rows.forEach(r => { const o = lv[r.p] = lv[r.p] || {sum:0,n:0,buy:0,sell:0}; o.sum += r.q; o.n++; r.side==="Buy" ? o.buy += r.q : o.sell += r.q; });
        const m2 = median(Object.values(lv).map(o=>o.sum)) || 1e-12;
        rows.forEach(r => { const o = lv[r.p]; if (o.sum >= settings.absorb*m2 && o.n >= 4){ r.absorb = true; r.adir = o.buy >= o.sell ? "sellers" : "buyers"; } });
      }
    }
    const buy = rows.filter(r=>r.side==="Buy").reduce((a,r)=>a+r.q,0), sell = rows.filter(r=>r.side==="Sell").reduce((a,r)=>a+r.q,0);
    const span = rows.length ? (rows[rows.length-1].t - rows[0].t)/1000 : 0;
    const hits = {}; rows.filter(r=>r.isNew).forEach(r => hits[r.p] = r.side);
    st.map = st.map || new Map(); st.buf = st.buf || [];
    st.buf.forEach(b => b.isNew = false);
    rows.forEach(r => { const o = st.map.get(r.id); if (o){ o.tier = r.tier; o.absorb = r.absorb; o.adir = r.adir; o.isNew = r.isNew; } else { st.map.set(r.id, r); st.buf.push(r); } });
    if (st.buf.length > 3000){ st.buf.splice(0, 600).forEach(b => st.map.delete(b.id)); }
    const ab = new Set(rows.filter(r=>r.absorb).map(r=>r.p));
    return { rows, all: st.buf, hits, ab, abDir: (rows.find(r=>r.absorb)||{}).adir || "",
             stats:{ pace: span>0 ? rows.length/span : rows.length, buyPct: buy+sell ? 100*buy/(buy+sell) : 50, delta: buy-sell } };
  }
};

/* Wilder ADX / DMI (TradingView ta.dmi): TR, +DM, -DM smoothed with RMA(len); DX = 100*|+DI - -DI| / (+DI + -DI); ADX = RMA(DX, len) */
const adxOf = (d, L) => { const n = d.length, rma = a => { const o = new Array(a.length).fill(null); let r = 0; for (let i = 0; i < a.length; i++){ if (i < L){ r += a[i]; if (i === L-1) o[i] = r = r/L; } else o[i] = r = (r*(L-1) + a[i])/L; } return o; };
  const tr = [], pd = [], md = []; d.forEach((k, i) => { if (!i){ tr.push(k.h - k.l); pd.push(0); md.push(0); return; } const p = d[i-1], up = k.h - p.h, dn = p.l - k.l;
    tr.push(Math.max(k.h - k.l, Math.abs(k.h - p.c), Math.abs(k.l - p.c))); pd.push(up > dn && up > 0 ? up : 0); md.push(dn > up && dn > 0 ? dn : 0); });
  const at = rma(tr), sp = rma(pd), sm = rma(md), pdi = at.map((a, i) => a ? 100*sp[i]/a : null), mdi = at.map((a, i) => a ? 100*sm[i]/a : null);
  const dx = pdi.map((v, i) => v == null ? null : (v + mdi[i]) ? 100*Math.abs(v - mdi[i])/(v + mdi[i]) : 0), f = dx.findIndex(v => v != null), adx = new Array(n).fill(null);
  if (f >= 0){ let r = 0; for (let i = f; i < n; i++){ const j = i - f; if (j < L){ r += dx[i]; if (j === L-1) adx[i] = r = r/L; } else adx[i] = r = (r*(L-1) + dx[i])/L; } }
  return {adx, pdi, mdi}; };
/* CCI (Lambert): (typical price - SMA(tp, n)) / (0.015 * mean absolute deviation) */
const cciOf = (d, L) => { const tp = d.map(k => (k.h + k.l + k.c)/3); return tp.map((v, i) => { if (i < L-1) return null; let s = 0; for (let j = i-L+1; j <= i; j++) s += tp[j]; const m = s/L; let md = 0; for (let j = i-L+1; j <= i; j++) md += Math.abs(tp[j] - m); md /= L; return md ? (v - m)/(0.015*md) : 0; }); };
/* Parabolic SAR, port of TradingView's ta.sar (Pine reference implementation): on a flip the SAR starts at the
   prior extreme point or this bar's own high/low, whichever is further, so a fresh dot never sits inside the candle. */
const psarOf = (d, start, inc, max) => { const n = d.length, v = new Array(n).fill(null), u = new Array(n).fill(null); if (n < 2) return {v, up:u};
  let res, mm, acc, below;
  for (let i = 1; i < n; i++){ let first = false;
    if (i === 1){ below = d[1].c > d[0].c; mm = below ? d[1].h : d[1].l; res = below ? d[0].l : d[0].h; first = true; acc = start; }
    res = res + acc*(mm - res);
    if (below){ if (res > d[i].l){ first = true; below = false; res = Math.max(d[i].h, mm); mm = d[i].l; acc = start; } }
    else if (res < d[i].h){ first = true; below = true; res = Math.min(d[i].l, mm); mm = d[i].h; acc = start; }
    if (!first){ if (below){ if (d[i].h > mm){ mm = d[i].h; acc = Math.min(acc + inc, max); } } else if (d[i].l < mm){ mm = d[i].l; acc = Math.min(acc + inc, max); } }
    if (below){ res = Math.min(res, d[i-1].l); if (i > 1) res = Math.min(res, d[i-2].l); } else { res = Math.max(res, d[i-1].h); if (i > 1) res = Math.max(res, d[i-2].h); }
    v[i] = res; u[i] = below; }
  return {v, up:u}; };
const smaOf = (a, n) => { let s = 0; return a.map((v, i) => { s += v; if (i >= n) s -= a[i-n]; return i >= n-1 ? s/n : s/(i+1); }); };
let CHART_S = 1;   // chart size from the header − / + control (1 = theme size); every chart lays itself out in units of this
const MA_TYPES = ["SMA","EMA","WMA"], MA_MAX = 7, MA_COLS = ["#f0b90b","#4aa3ff","#b57cff","#ff9800","#0ecb81","#f6465d","#26c6da"];
const maOf = (a, n, type) => {   // one moving average of a series: null before the first full window (SMA / WMA), EMA starts on the first bar
  if (type === "WMA"){ const den = n*(n+1)/2; return a.map((_, i) => { if (i < n-1) return null; let s = 0; for (let k = 0; k < n; k++) s += a[i-k]*(n-k); return s/den; }); }
  if (type === "SMA"){ let s = 0; return a.map((v, i) => { s += v; if (i >= n) s -= a[i-n]; return i >= n-1 ? s/n : null; }); }
  const k = 2/(n+1); let e = null; return a.map(v => (e = e == null ? v : v*k + e*(1-k)));
};
const stochK = (d, k, slow) => smaOf(d.map((x, i) => { if (i < k-1) return 50; let hh = -Infinity, ll = Infinity; for (let j = i-k+1; j <= i; j++){ hh = Math.max(hh, d[j].h); ll = Math.min(ll, d[j].l); } return hh > ll ? (x.c - ll)/(hh - ll)*100 : 50; }), slow);
const rsiOf = (cl, L) => { let ag = 0, al = 0; return cl.map((v, i) => { if (!i) return 50; const d = v - cl[i-1], g = Math.max(d, 0), l = Math.max(-d, 0); if (i <= L){ ag += g/L; al += l/L; } else { ag = (ag*(L-1) + g)/L; al = (al*(L-1) + l)/L; } return i < L ? 50 : al === 0 ? 100 : 100 - 100/(1 + ag/al); }); };
