"use strict";
const CFG = __CONFIG__;
/* blink diagnostics (console only, no UI): a page load line says whether Streamlit re-created this iframe; a long-task line says the main thread was blocked (>120 ms) */
try { const k = "xpix_loads", a = JSON.parse(localStorage.getItem(k) || "[]"); a.push(Date.now()); localStorage.setItem(k, JSON.stringify(a.slice(-20)));
  console.info("[XPIX] page load #" + a.length + (a.length > 1 ? " (" + Math.round((a[a.length-1] - a[a.length-2])/1000) + " s after the previous load)" : " (first)")); } catch(e){}
try { new PerformanceObserver(l => l.getEntries().forEach(e => { if (e.duration > 120) console.info("[XPIX] long task " + Math.round(e.duration) + " ms at t=" + Math.round(e.startTime/1000) + " s"); })).observe({entryTypes:["longtask"]}); } catch(e){}
const API = CFG.apiBase || "https://www.okx.com";
const WSB = CFG.wsBase || "wss://ws.okx.com/ws/v5";   // OKX retires WebSocket port 8443 on 2026-10-31: standard TLS port 443
const SYMS = CFG.symbols.slice();
const LS = "ai_ws_v5";
// Auto-Center is a per-tab choice: kept in sessionStorage, not in the shared state (other tabs and browsers were inheriting it)
const acGet = () => { try { return sessionStorage.getItem("ai_ac") !== "0"; } catch(e){ return true; } };   // ON unless this tab switched it off (owner 2026-11-05: the standard layout has centred charts)   // (it was OFF by default, a free chart like TradingView: with it on every live tick and data load re-centres the view on the latest candle and undoes a manual pan; the ⊙ button turns it off)
const acSet = v => { try { sessionStorage.setItem("ai_ac", v ? "1" : "0"); } catch(e){} };
/* ?ws_reset=1 on the page link = clear this browser's saved Workspace (layout, widget settings, drawings); the journal is kept */
try { const q = new URLSearchParams(window.parent.location.search); if (q.get("ws_reset") === "1"){
  Object.keys(localStorage).filter(k => k.startsWith(LS) && !/journal|_jset/i.test(k)).forEach(k => localStorage.removeItem(k));
  q.delete("ws_reset"); const u = window.parent.location.pathname + (q.toString() ? "?" + q : ""); window.parent.history.replaceState(null, "", u); } } catch(e){}
/* Live CFD quotes for forex / metals / indices / commodities: Finnhub's websocket with OANDA symbols. Runs only when the owner set
   FINNHUB_WS_TOKEN in Streamlit Secrets (the browser sees that key, so use a separate free key for it). [id, label, category, Yahoo twin]
   Whether every symbol streams on Finnhub's FREE plan is not verified - rows without ticks stay at "…". */
const FH_LIST = [["EUR_USD","EUR/USD","Forex","EURUSD=X"],["GBP_USD","GBP/USD","Forex","GBPUSD=X"],["USD_JPY","USD/JPY","Forex","USDJPY=X"],["AUD_USD","AUD/USD","Forex","AUDUSD=X"],["USD_CAD","USD/CAD","Forex","USDCAD=X"],["USD_CHF","USD/CHF","Forex","USDCHF=X"],["NZD_USD","NZD/USD","Forex","NZDUSD=X"],["EUR_GBP","EUR/GBP","Forex","EURGBP=X"],["EUR_JPY","EUR/JPY","Forex","EURJPY=X"],["GBP_JPY","GBP/JPY","Forex","GBPJPY=X"],
  ["XAU_USD","Gold XAU/USD","Metals","GC=F"],["XAG_USD","Silver XAG/USD","Metals","SI=F"],["XPT_USD","Platinum","Metals",""],["XCU_USD","Copper","Metals","HG=F"],
  ["SPX500_USD","S&P 500","Indices","^GSPC"],["NAS100_USD","Nasdaq 100","Indices","^NDX"],["US30_USD","Dow 30","Indices","^DJI"],["DE30_EUR","DAX","Indices","^GDAXI"],["UK100_GBP","FTSE 100","Indices","^FTSE"],["JP225_USD","Nikkei 225","Indices","^N225"],["HK33_HKD","Hang Seng","Indices","^HSI"],
  ["WTICO_USD","WTI crude","Oil & Gas","CL=F"],["BCO_USD","Brent crude","Oil & Gas","BZ=F"],["NATGAS_USD","Natural gas","Oil & Gas","NG=F"],["WHEAT_USD","Wheat","Commodities","ZW=F"],["CORN_USD","Corn","Commodities","ZC=F"],["SUGAR_USD","Sugar","Commodities","SB=F"]]
  .map(([id, label, cat, y]) => ({id:"FH:"+id, sym:"OANDA:"+id, label, cat, y:y ? "Y:"+y : ""}));
const FH_MAP = Object.fromEntries(FH_LIST.map(x => [x.id, x]));
const FH_HL = {"FH:EUR_USD":"EUR","FH:GBP_USD":"GBP","FH:USD_JPY":"JPY","FH:XAU_USD":"GOLD","FH:XAG_USD":"SILVER","FH:XPT_USD":"PLATINUM","FH:XCU_USD":"COPPER","FH:SPX500_USD":"SP500","FH:NAS100_USD":"XYZ100","FH:JP225_USD":"JP225","FH:WTICO_USD":"CL","FH:BCO_USD":"BRENTOIL","FH:NATGAS_USD":"NATGAS"};
const fhDup = id => FH_HL[id] && HL.q["HL:xyz:"+FH_HL[id]];   // same market already listed from Hyperliquid
// forex / CFD weekend: Friday 17:00 -> Sunday 17:00 New York time, OANDA sends no ticks
const fxClosed = () => { const p = new Intl.DateTimeFormat("en-US", {timeZone:"America/New_York", weekday:"short", hour:"numeric", hour12:false}).formatToParts(new Date()), d = p.find(x => x.type === "weekday").value, h = +p.find(x => x.type === "hour").value % 24;
  return d === "Sat" || (d === "Fri" && h >= 17) || (d === "Sun" && h < 17); };
const FH = {q:{}, state:"off", ws:null, wait:5000,
  start(){ if (!CFG.fhToken || this.ws) return; let ws; try { ws = new WebSocket("wss://ws.finnhub.io?token="+encodeURIComponent(CFG.fhToken)); } catch(e){ this.state = "error"; return; }
    this.ws = ws; this.state = "connecting";
    ws.onopen = () => { this.state = "live"; this.wait = 5000; FH_LIST.forEach(x => ws.send(JSON.stringify({type:"subscribe", symbol:x.sym}))); };
    ws.onmessage = ev => { let m; try { m = JSON.parse(ev.data); } catch(e){ return; } if (m.type === "error"){ this.state = "error: "+(m.msg || ""); return; } if (m.type !== "trade" || !Array.isArray(m.data)) return;
      m.data.forEach(t => { const id = "FH:"+String(t.s || "").replace(/^OANDA:/, ""); if (FH_MAP[id] && +t.p > 0) this.q[id] = {last:+t.p, t:+t.t || Date.now()}; }); };
    ws.onclose = () => { this.ws = null; if (this.state !== "off"){ this.state = "reconnecting"; setTimeout(() => this.start(), this.wait); this.wait = Math.min(60000, this.wait*2); } };
    ws.onerror = () => { try { ws.close(); } catch(e){} }; },
  // change % reference = the previous daily close of the Yahoo twin when the page embedded it, otherwise unknown (no fake 0%)
  ref(x){ const D = x.y && YF[x.y] && YF[x.y]["1d"]; return D && D.length > 1 ? D[D.length-2][4] : 0; }
};
/* Hyperliquid (public API, no key, real time): the "xyz" builder dex lists TradFi perps - gold / silver / platinum / palladium /
   copper, WTI / Brent / gas / heating oil, S&P 500 / Nasdaq 100 / Nikkei / KOSPI, EUR / GBP / JPY, TLT and ~100 stocks.
   Ids are "HL:xyz:GOLD". These are PERPETUAL prices (track the market via an oracle; can differ slightly from spot / futures,
   and they trade 24/7 including when the underlying market is closed). Live mids from the allMids websocket; prev-day price,
   volume and the market list from metaAndAssetCtxs every 30 s (also the fallback when the socket is down). */
const HL_API = CFG.hlApi || "https://api.hyperliquid.xyz", HL_DEX = "xyz";
const HL_CAT = {GOLD:"Metals",SILVER:"Metals",PLATINUM:"Metals",PALLADIUM:"Metals",COPPER:"Metals",CL:"Oil & Gas",BRENTOIL:"Oil & Gas",NATGAS:"Oil & Gas",HO:"Oil & Gas",
  SP500:"Indices",XYZ100:"Indices",JP225:"Indices",KR200:"Indices",EUR:"Forex",GBP:"Forex",JPY:"Forex",AUD:"Forex",CAD:"Forex",CHF:"Forex",TLT:"Bonds"};
const HL_LBL = {GOLD:"Gold",SILVER:"Silver",PLATINUM:"Platinum",PALLADIUM:"Palladium",COPPER:"Copper",CL:"WTI crude",BRENTOIL:"Brent crude",NATGAS:"Natural gas",HO:"Heating oil",
  SP500:"S&P 500",XYZ100:"Nasdaq 100 (XYZ100)",JP225:"Nikkei 225",KR200:"KOSPI 200",EUR:"EUR/USD",GBP:"GBP/USD",JPY:"USD/JPY",AUD:"AUD/USD",CAD:"USD/CAD",CHF:"USD/CHF",TLT:"US 20Y+ bonds (TLT)"};
const hlBase = id => String(id).replace(/^HL:/, "").split(":").pop(), hlCoin = id => String(id).replace(/^HL:/, "");
const hlCat = id => HL_CAT[hlBase(id)] || "Stocks", hlLabel = id => HL_LBL[hlBase(id)] || hlBase(id);
const HL = {q:{}, list:[], state:"off", ws:null, wait:3000, t:0, tr:{}, trSub:new Set(),
  /* one shared path for every /info call: identical calls share a short cache and one in-flight request, and a 429 stops ALL calls for a while (Retry-After, capped) instead of every widget retrying */
  cache:new Map(), inflight:new Map(), cool:0,
  async post(body, ttl){ const key = JSON.stringify(body), now = Date.now();   // ttl = how long an identical answer is reused (default 1.5 s; the candle polls pass more)
    if (now < this.cool) throw new Error("Hyperliquid rate limit: waiting before retry");
    const hit = this.cache.get(key); if (hit && now - hit.t < (ttl || 1500)) return hit.v;
    if (this.inflight.has(key)) return this.inflight.get(key);
    const p = (async () => { try { const r = await fetch(HL_API+"/info", {method:"POST", headers:{"Content-Type":"application/json"}, body:key});
        if (r.status === 429){ const ra = +r.headers.get("Retry-After") || 0, wait = Math.min(60000, Math.max(15000, ra*1000)); this.cool = Date.now() + wait + Math.random()*2000; throw new Error("Hyperliquid HTTP 429"); }
        if (!r.ok) throw new Error("Hyperliquid HTTP "+r.status);
        const v = await r.json(); this.cache.set(key, {t:Date.now(), v}); return v; } finally { this.inflight.delete(key); } })();
    this.inflight.set(key, p); return p; },
  /* trades: the REST recentTrades call gives only the last ~10 prints (~20 s on gold), so the footprint / tape stayed almost empty.
     A "trades" subscription on the same socket keeps a rolling buffer (newest first, like OKX) of every print since the chart opened (2026-10-22). */
  trSend(coin){ try { this.ws && this.ws.send(JSON.stringify({method:"subscribe", subscription:{type:"trades", coin}})); } catch(e){} },
  trPush(x){ if (!x || !x.coin) return; const b = this.tr[x.coin] = this.tr[x.coin] || {ids:new Set(), rows:[]}, id = String(x.tid || x.hash || x.time);
    if (b.ids.has(id)) return; b.ids.add(id); b.rows.push({tradeId:id, ts:String(x.time), px:String(x.px), sz:String(x.sz), side:x.side === "B" ? "buy" : "sell"});
    if (b.rows.length > 600){ b.rows.sort((p, q) => +q.ts - +p.ts); b.rows.length = 400; b.ids = new Set(b.rows.map(r => r.tradeId)); } },
  async trades(coin){ if (!this.trSub.has(coin)){ this.trSub.add(coin); this.start(); this.trSend(coin); }
    const b = this.tr[coin], sd = this.seedT = this.seedT || {}; if ((!b || b.rows.length < 10) && Date.now() - (sd[coin] || 0) > 4000){ sd[coin] = Date.now(); const t = await this.post({type:"recentTrades", coin}); (t || []).forEach(x => this.trPush(x)); }   // REST seed at most every 4 s per coin (it costs ~20 of the 1200 request weight per minute; the socket fills the buffer on its own)   // seed / socket down: REST
    return (this.tr[coin] || {rows:[]}).rows.slice().sort((p, q) => +q.ts - +p.ts).slice(0, 300); },
  async ctx(){ const [meta, ctxs] = await this.post({type:"metaAndAssetCtxs", dex:HL_DEX}); const L = [];
    (meta.universe || []).forEach((u, i) => { const c = ctxs[i] || {}, id = "HL:"+u.name, px = +(c.midPx || c.markPx), vol = +c.dayNtlVlm || 0, oi = +c.openInterest || 0;
      if (u.isDelisted || !(px > 0) || (!vol && !oi)) return;
      const o = this.q[id] = Object.assign(this.q[id] || {}, {open:+c.prevDayPx || 0, vol}); if (!o.last || !this.ws) o.last = px; L.push({id, vol, cat:hlCat(id)}); });
    this.list = L; this.t = Date.now(); },
  start(){ if (this.on) return; this.on = true; this.state = "connecting";
    const poll = async () => { try { await this.ctx(); if (this.state !== "live") this.state = "rest"; } catch(e){ this.state = "error: "+(e.message || e); } setTimeout(poll, this.ws ? 30000 : 8000); };
    poll(); this.sock(); },
  sock(){ let ws; try { ws = new WebSocket(HL_API.replace(/^http/, "ws")+"/ws"); } catch(e){ return; }
    ws.onopen = () => { this.ws = ws; this.state = "live"; this.wait = 3000; ws.send(JSON.stringify({method:"subscribe", subscription:{type:"allMids", dex:HL_DEX}})); this.trSub.forEach(c => this.trSend(c)); this.ping = setInterval(() => { try { ws.send(JSON.stringify({method:"ping"})); } catch(e){} }, 30000); };
    ws.onmessage = ev => { let m; try { m = JSON.parse(ev.data); } catch(e){ return; }
      if (m.channel === "trades" && Array.isArray(m.data)){ m.data.forEach(x => this.trPush(x)); return; }
      const mids = m.channel === "allMids" && m.data && m.data.mids; if (!mids) return;
      Object.entries(mids).forEach(([k, v]) => { const id = "HL:"+k; if (this.q[id] && +v > 0) this.q[id].last = +v; }); };
    ws.onclose = () => { this.ws = null; clearInterval(this.ping); if (this.state === "live") this.state = "rest"; setTimeout(() => this.sock(), this.wait); this.wait = Math.min(60000, this.wait*2); };
    ws.onerror = () => { try { ws.close(); } catch(e){} }; }
};
// OKX timeframe -> Hyperliquid candle interval (bars Hyperliquid does not have -> clear error)
const HL_IV = {"1m":"1m","3m":"3m","5m":"5m","15m":"15m","30m":"30m","1H":"1h","2H":"2h","4H":"4h","8H":"8h","12Hutc":"12h","1D":"1d","1Dutc":"1d","3Dutc":"3d","1W":"1w","1Wutc":"1w","1M":"1M","1Mutc":"1M"};
const HL_MS = {"1m":6e4,"3m":18e4,"5m":3e5,"15m":9e5,"30m":18e5,"1h":36e5,"2h":72e5,"4h":144e5,"8h":288e5,"12h":432e5,"1d":864e5,"3d":2592e5,"1w":6048e5,"1M":2592e6};
/* Hyperliquid's l2Book answers only 20 levels a side (gold: about +-2 USD = +-0.05 %), so the order-flow heat map was a thin strip. l2Book also takes nSigFigs (5, 4, 3 = ticks of 10x each, still 20 levels a side), so the book is
   STITCHED: the native 20 levels, then the coarser ladders only BEYOND the finer one's edge (one coarse tick skipped, so nothing is counted twice), each coarse level spread over its range in fine steps (size / parts) so the
   heat map is continuous. Gold: about +-2000 USD with the nSigFigs 2 ladder (the sub-levels are <= 1 USD apart so the map has no stripes). Coarse ladders are reused for 4 s (weight 2 each). Answers in OKX's shape like the native call. */
async function hlWideBook(coin){
  const NS = [5, 4, 3, 2], CL = HL.coarse = HL.coarse || {};   // a coarse ladder that times out / is rate-limited falls back to its last good copy (< 2 min old): without it the snapshot had NO far walls and the map showed a black stripe until the next good one
  const rs = await Promise.all([HL.post({type:"l2Book", coin}), ...NS.map(async n => { const k = coin+"|"+n; try { const v = await HL.post({type:"l2Book", coin, nSigFigs:n}, 4000); if (v && v.levels) CL[k] = {t:Date.now(), v}; return v; } catch(e){ const c = CL[k]; return c && Date.now() - c.t < 120000 ? c.v : null; } })]);
  const base = rs[0], lv0 = (base && base.levels) || [[], []];
  const side = si => { const out = (lv0[si] || []).map(x => ({p:+x.px, q:+x.sz, n:+x.n || 0})); let fine = Infinity; for (let i = 1; i < out.length; i++){ const d = Math.abs(out[i].p - out[i-1].p); if (d > 1e-12 && d < fine) fine = d; }
    let edge = out.length ? out[out.length-1].p : null; if (edge == null) return out;
    for (const r of rs.slice(1)){ const L = ((r && r.levels && r.levels[si]) || []).map(x => ({p:+x.px, q:+x.sz, n:+x.n || 0})); if (L.length < 2) continue; const T = Math.abs(L[1].p - L[0].p); if (!(T > 0)) continue;
      const parts = isFinite(fine) ? Math.min(120, Math.max(1, Math.round(T/fine))) : 1, sub = T/parts;
      L.forEach(x => { for (let j = 0; j < parts; j++){ const pp = x.p + (j - (parts-1)/2)*sub*(si === 0 ? -1 : 1); if (si === 0 ? !(pp < edge) : !(pp > edge)) continue; out.push({p:+pp.toFixed(10), q:x.q/parts, n:Math.round(x.n/parts)}); } });   // cut per SUB-level at the finer ladder's edge: no coarse tick is thrown away, so there is no empty band at the junction of two ladders
      out.sort((u, v) => si === 0 ? v.p - u.p : u.p - v.p); edge = out[out.length-1].p; }
    return out; };
  const f = a => a.map(x => [String(x.p), String(x.q), "0", String(x.n || 0)]);
  return [{bids:f(side(0)), asks:f(side(1)), ts:String((base && base.time) || Date.now())}];
}
async function hlOkx(path){   // answers the OKX REST paths the widgets use, in OKX's shape, from Hyperliquid
  const q = new URLSearchParams(path.split("?")[1] || ""), id = q.get("instId"), coin = hlCoin(id);
  if (/\/market\/(history-)?candles/.test(path)){ const iv = HL_IV[q.get("bar")]; if (!iv) throw new Error("timeframe "+q.get("bar")+" not available on Hyperliquid");
    await clockReady(); const lim = Math.min(+q.get("limit") || 100, 1000), end = Math.floor(q.get("after") ? +q.get("after") - 1 : nowS()), start = Math.floor(end - lim*HL_MS[iv]);   // nowS() = the exchange's time (PC clock + measured skew): a PC clock that is hours behind used to ask Hyperliquid for OLD candles (owner 2026-11-05: gold charts ~90 below the live price)
    const poll = lim <= 5 && !q.get("after"), rows = await HL.post({type:"candleSnapshot", req:{coin, interval:iv, startTime:poll ? Math.floor(start/HL_MS[iv])*HL_MS[iv] : start, endTime:poll ? Math.floor(end/5000)*5000 : end}}, poll ? 5000 : 0);   // the live poll (3 bars): its time window is rounded so charts on the same symbol and timeframe send ONE identical request, reused for 5 s (a candle poll costs ~20 of Hyperliquid's 1200 request weight per minute)
    return (rows || []).map(k => [String(k.t), String(k.o), String(k.h), String(k.l), String(k.c), String(k.v), "0", "0", "1"]).reverse(); }
  if (/\/market\/ticker/.test(path)){ if (!HL.t) await HL.ctx(); const x = HL.q[id]; if (!x) throw new Error("unknown Hyperliquid market "+coin); return [{instId:id, last:String(x.last), open24h:String(x.open || x.last), vol24h:String(x.vol || 0)}]; }
  if (/\/market\/books/.test(path)){ const wide = /books-full/.test(path) || +q.get("sz") >= 100; if (wide) return hlWideBook(coin);
    const b = await HL.post({type:"l2Book", coin}), lv = (b && b.levels) || [[], []], f = a => a.map(x => [String(x.px), String(x.sz), "0", String(x.n || 0)]);
    return [{bids:f(lv[0] || []), asks:f(lv[1] || []), ts:String(b.time || Date.now())}]; }
  if (/\/market\/trades/.test(path)) return HL.trades(coin);   // newest first, like OKX (the old REST-only version returned oldest first and only ~10 prints)
  throw new Error("not available for Hyperliquid markets");
}
const TFSEC = {"5s":5,"15s":15,"30s":30,"1m":60,"5m":300,"15m":900,"30m":1800,"13m":780,"1H":3600,"2H":7200,"3H":10800,"4H":14400,"6H":21600,"7H":25200,"8H":28800,"12H":43200,"1D":86400,"3D":259200,"1W":604800,"1M":2592000};
/* OKX bar sizes: 2H is native; 6H / 12H / 3D / 1M use its UTC variants; 13m, 3H, 7H and 8H do not exist on OKX, so they are built from 1m / 1H candles (buckets aligned to the UTC epoch) */
const TF_OKX = {"2H":"2H","6H":"6Hutc","12H":"12Hutc","3D":"3Dutc","1M":"1Mutc"}, TF_AGG = {"13m":["1m",13],"3H":["1H",3],"7H":["1H",7],"8H":["1H",8]};
const okxBar = tf => TF_OKX[tf] || tf;
// the PC clock can be minutes off; candle times come from OKX, so the countdown uses OKX server time (offset measured against /public/time)
let SKEW = 0; const nowS = () => Math.round(Date.now() + SKEW);   // always a whole millisecond: Hyperliquid answers HTTP 422 to a fractional startTime / endTime
const HM_RAMP = [[0,[1,3,8]],[.1,[12,26,110]],[.2,[22,72,205]],[.32,[0,158,230]],[.43,[0,200,170]],[.54,[60,205,70]],[.65,[190,225,40]],[.75,[250,205,30]],[.84,[250,130,25]],[.92,[235,45,50]],[.97,[225,60,200]],[1,[255,245,250]]];   // many distinct bands: navy > blue > sky > teal > green > lime > yellow > orange > red > magenta > white
const hmRamp = t => { for (let q = 1; q < HM_RAMP.length; q++){ if (t <= HM_RAMP[q][0]){ const a = HM_RAMP[q-1], b = HM_RAMP[q], u = (t - a[0])/(b[0] - a[0] || 1); return "rgb("+Math.round(a[1][0] + (b[1][0]-a[1][0])*u)+","+Math.round(a[1][1] + (b[1][1]-a[1][1])*u)+","+Math.round(a[1][2] + (b[1][2]-a[1][2])*u)+")"; } } return "rgb(255,250,235)"; };
const hexRgb = h => [parseInt(h.slice(1,3),16), parseInt(h.slice(3,5),16), parseInt(h.slice(5,7),16)];   // "#rrggbb" -> [r,g,b]
const hmMix = (t, lo, hi) => "rgb("+Math.round(lo[0] + (hi[0]-lo[0])*t)+","+Math.round(lo[1] + (hi[1]-lo[1])*t)+","+Math.round(lo[2] + (hi[2]-lo[2])*t)+")";   // custom heat-map ramp: two colours (added 2026-10-19)
const candleRem = (lastT, tf) => { const ms = (TFSEC[tf] || 3600)*1000; let e = nowS() - lastT; if (e < 0) e = 0; return e < ms ? ms - e : ms - (e % ms); };   // ms until the next candle opens
const hexA = (h, a) => { const n = parseInt(h.slice(1), 16); return "rgba("+(n>>16&255)+","+(n>>8&255)+","+(n&255)+","+a+")"; };
const HARM_TOL = 0.10;   // ratio tolerance: 6 % found almost nothing on live-like bars (60 random walks: 1 chart); 10 % still needs a clean X-A-B-C-D shape. Chart only: the lab's Python finder keeps TOL 0.06 until the lab is moved.
const HARM_RULES = {
  "Gartley":{b:[.618,.618],c:[.382,.886],d:[.786,.786]}, "Bat":{b:[.382,.5],c:[.382,.886],d:[.886,.886]},
  "Butterfly":{b:[.786,.786],c:[.382,.886],d:[1.272,1.618]}, "Crab":{b:[.382,.618],c:[.382,.886],d:[1.618,1.618]},
  "Cypher":{b:[.382,.618],cx:[1.13,1.414],d:[.786,.786]}};
const harmIn = (v, r) => v >= r[0]*(1-HARM_TOL) && v <= r[1]*(1+HARM_TOL);
function harmCheck(X, A, B, C, D){   // mirrors modules/harmonic.py
  const xa = Math.abs(A-X), ab = Math.abs(A-B); if (xa <= 0 || ab <= 0) return null;
  const sg = A > X ? 1 : -1; if (!(sg*(B-X) > 0 && sg*(A-B) > 0)) return null;
  const b = ab/xa, cab = Math.abs(C-B)/ab;
  for (const [name, r] of Object.entries(HARM_RULES)){
    if (!harmIn(b, r.b)) continue;
    if (name === "Cypher"){ if (!(sg*(C-A) > 0)) continue; const xc = Math.abs(C-X); if (!harmIn(xc/xa, r.cx) || !harmIn(Math.abs(C-D)/xc, r.d)) continue; }
    else { if (!(sg*(A-C) > 0 && sg*(C-B) > 0) || !harmIn(cab, r.c)) continue; if (!harmIn(Math.abs(A-D)/xa, r.d) || sg*(D-C) >= 0) continue; }
    return name;
  }
  return null;
}
function harmZigzag(d, dev, n){
  const piv = [];
  for (let i = n; i < d.length-n; i++){
    let mh = -Infinity, ml = Infinity; for (let k = i-n; k <= i+n; k++){ if (d[k].h > mh) mh = d[k].h; if (d[k].l < ml) ml = d[k].l; }
    if (d[i].h >= mh) piv.push({i, p:d[i].h, k:"H"}); else if (d[i].l <= ml) piv.push({i, p:d[i].l, k:"L"});
  }
  const out = [];
  for (const q of piv){
    const L = out[out.length-1];
    if (L && L.k === q.k){ if ((q.k === "H" && q.p > L.p) || (q.k === "L" && q.p < L.p)) out[out.length-1] = q; continue; }
    if (L && Math.abs(q.p-L.p)/L.p < dev) continue;
    out.push(q);
  }
  return out;
}
/* Harmonic patterns (Carney / Pesavento ratio definitions: Gartley, Bat, Butterfly, Crab, Cypher). A "completed" pattern has its D pivot; a "forming" one has X-A-B-C confirmed and projects the
   Potential Reversal Zone (PRZ) where D should print. PRZ = the XA-retracement level (or range) intersected with the BC projection range of the pattern; plan = entry at D / PRZ, stop beyond X
   (Gartley / Bat / Cypher) or beyond the PRZ (Butterfly / Crab), targets at 0.382 / 0.618 of the A-D leg and at A. These stop / target conventions are common practice, not a fixed standard. */
const HARM_BC = {"Gartley":[1.13,1.618], "Bat":[1.618,2.618], "Butterfly":[1.618,2.24], "Crab":[2.24,3.618]};
function harmPrz(name, X, A, B, C){
  const sg = A > X ? 1 : -1, xa = Math.abs(A-X), r = HARM_RULES[name];
  if (name === "Cypher"){ const xc = Math.abs(C-X), l = C - sg*r.d[0]*xc; return {lo:Math.min(l, l), hi:Math.max(l, l), mid:l, pad:.03*xa}; }
  let l1 = A - sg*r.d[0]*xa, l2 = A - sg*r.d[1]*xa; if (r.d[0] === r.d[1]){ l1 += .03*xa*sg; l2 -= .03*xa*sg; }   // single ratio -> +-3% of XA band
  let lo = Math.min(l1, l2), hi = Math.max(l1, l2); const bc = HARM_BC[name];
  if (bc){ const q1 = C - sg*bc[0]*Math.abs(C-B), q2 = C - sg*bc[1]*Math.abs(C-B), plo = Math.min(q1, q2), phi = Math.max(q1, q2), olo = Math.max(lo, plo), ohi = Math.min(hi, phi); if (olo <= ohi){ lo = olo; hi = ohi; } }
  return {lo, hi, mid:(lo+hi)/2, pad:0};
}
function harmPlan(name, X, A, C, D, prz){   // D = price where the trade is taken (D pivot, or the PRZ mid for a forming pattern)
  const sg = A > X ? 1 : -1, xa = Math.abs(A-X), far = sg > 0 ? Math.min(D, prz.lo) : Math.max(D, prz.hi);
  const stop = (name === "Butterfly" || name === "Crab") ? far - sg*0.1*xa : X - sg*0.02*xa, ad = Math.abs(A-D);
  const tps = [D + sg*0.382*ad, D + sg*0.618*ad, A], risk = Math.abs(D-stop) || 1e-9;
  return {dir:sg > 0 ? "long" : "short", entry:D, stop, tps, rr:Math.abs(tps[0]-D)/risk};
}
function harmFilled(pl, d, from){   // true once price has traded at the entry since the pattern point; no fill = no trade, so no box
  for (let j = from; j < d.length; j++){ const b = d[j]; if (b.l <= pl.entry && b.h >= pl.entry) return true; }
  return false;
}
function harmHit(pl, d, from){   // true once a bar after the trade point touched the stop or the last target (the trade is over)
  const long_ = pl.dir === "long", lo = pl.stop, tp = pl.tps[2];
  for (let j = from + 1; j < d.length; j++){ const b = d[j]; if (long_ ? (b.l <= lo || b.h >= tp) : (b.h >= lo || b.l <= tp)) return true; }
  return false;
}
/* zigzag swing size from the market's own volatility: k x the average bar range (% of price) over the last 200 bars, clamped.
   A fixed % (was 1.2 % harmonic, 0.6 % Elliott) found nothing on calm markets / small timeframes (gold 5m bars move ~0.05 %). */
function zzDev(d, k, lo, hi){ const n = d.length, m = Math.min(200, n); if (!m) return lo; let s = 0;
  for (let i = n - m; i < n; i++){ const b = d[i]; s += (b.h - b.l)/(b.c || 1); }
  return Math.max(lo, Math.min(hi, k*s/m)); }
const HTF_CACHE = {};   // "SYMBOL|TF" -> {t, v, busy}: shared by every chart
function htfDir(rows, tf){   // EMA50 trend of one timeframe's candles: up / down when price and the EMA agree with a 10-bar slope, else flat
  if (!rows || rows.length < 60) return null; const k = 2/51; let e = rows[0].c; const ema = [];
  rows.forEach(r => { e = r.c*k + e*(1-k); ema.push(e); }); const n = rows.length - 1, c = rows[n].c, slope = ema[n] - ema[n-10];
  return {tf, dir: c > ema[n] && slope > 0 ? "up" : c < ema[n] && slope < 0 ? "down" : "flat"};
}
function harmFind(d, maxN){   // newest-first list of {name, dir, state:"done"|"forming", pts:[{i,p}] (5 for done, 4 for forming), prz, plan}
  const z = harmZigzag(d, zzDev(d, 4, 0.002, 0.04), 3), res = [], n = d.length; if (z.length < 4 || !n) return res; const last = d[n-1].c;
  for (let e = z.length; e >= 5 && res.length < maxN; e--){
    const w = z.slice(e-5, e), nm = harmCheck(w[0].p, w[1].p, w[2].p, w[3].p, w[4].p); if (!nm) continue;
    const prz = harmPrz(nm, w[0].p, w[1].p, w[2].p, w[3].p);
    res.push({name:nm, dir:w[1].p > w[0].p ? "bull" : "bear", state:"done", pts:w.map(q => ({i:q.i, p:q.p})), prz, plan:harmPlan(nm, w[0].p, w[1].p, w[3].p, w[4].p, prz)});
  }
  const w = z.slice(-4), X = w[0].p, A = w[1].p, B = w[2].p, C = w[3].p, sg = A > X ? 1 : -1;   // forming: X-A-B-C confirmed, price heading for D
  if (sg*(B-X) > 0 && sg*(A-B) > 0 && sg*(A-C) > 0 && sg*(C-B) > 0 && n-1 - w[3].i <= 60){
    const xa = Math.abs(A-X), ab = Math.abs(A-B), b = ab/xa, cab = Math.abs(C-B)/ab;
    for (const [nm, r] of Object.entries(HARM_RULES)){
      if (!harmIn(b, r.b)) continue; if (nm === "Cypher"){ if (!(sg*(C-A) > 0) || !harmIn(Math.abs(C-X)/xa, r.cx)) continue; } else if (!harmIn(cab, r.c)) continue;
      const prz = harmPrz(nm, X, A, B, C), tgtSide = sg > 0 ? last >= prz.lo - .1*xa : last <= prz.hi + .1*xa;   // price has not blown through the zone
      if (tgtSide && (sg > 0 ? last < C : last > C)){ res.unshift({name:nm, dir:sg > 0 ? "bull" : "bear", state:"forming", pts:w.map(q => ({i:q.i, p:q.p})), prz, plan:harmPlan(nm, X, A, C, prz.mid, prz)}); break; }
    }
  }
  return res.slice(0, maxN);
}
/* Volume profile: rows [{h,l,v}] -> POC / value area (70%) / bins. Volume of each candle is spread across the price bins it touched. */
function vpCalc(rows, nb){
  nb = nb || 60; if (!rows.length) return null; const hasD = rows.some(r => r.d != null);
  let lo = Infinity, hi = -Infinity; rows.forEach(r => { if (r.l < lo) lo = r.l; if (r.h > hi) hi = r.h; });
  if (!(hi > lo)) return null; const st = (hi-lo)/nb, bins = new Array(nb).fill(0), dl = new Array(nb).fill(0);
  rows.forEach(r => { const a = Math.min(nb-1, Math.max(0, Math.floor((r.l-lo)/st))), b = Math.min(nb-1, Math.max(0, Math.floor((r.h-lo)/st))), v = (r.v || 0) / (b-a+1), dd = (r.d || 0) / (b-a+1); for (let i = a; i <= b; i++){ bins[i] += v; dl[i] += dd; } });
  let pi = 0; bins.forEach((v,i) => { if (v > bins[pi]) pi = i; });
  const tot = bins.reduce((a,b) => a+b, 0); let acc = bins[pi], a = pi, b = pi;
  while (acc < tot*0.7 && (a > 0 || b < nb-1)){ const up = b < nb-1 ? bins[b+1] : -1, dn = a > 0 ? bins[a-1] : -1; if (up >= dn){ b++; acc += bins[b]; } else { a--; acc += bins[a]; } }
  const mid = i => lo + (i+.5)*st;
  return {poc:mid(pi), vah:lo+(b+1)*st, val:lo+a*st, lo, hi, st, bins, dl, hasD, max:bins[pi]};
}
// volume profile v2: rows {l,h,v,d,tp} spread as a triangle peaked at the typical price (H+L+C)/3 (closer to where trading happened than an even
// spread), or rows {pts:[[price, vol, delta]...]} = real trades by price (live footprint) scaled to the candle volume
function vpCalc2(rows, nb){
  if (!rows.length) return null; let lo = Infinity, hi = -Infinity; rows.forEach(r => { if (r.l < lo) lo = r.l; if (r.h > hi) hi = r.h; });
  if (!(hi > lo)) return null; const st = (hi-lo)/nb, bins = new Float64Array(nb), dl = new Float64Array(nb), at = p => Math.min(nb-1, Math.max(0, Math.floor((p-lo)/st)));
  rows.forEach(r => { if (r.pts){ r.pts.forEach(([p, v, d]) => { const i = at(p); bins[i] += v; dl[i] += d; }); return; }
    const a = at(r.l), b = at(r.h), span = Math.max(1e-12, r.h - r.l); let ws = 0; const w = [];
    for (let i = a; i <= b; i++){ const m = lo + (i+.5)*st, x = 1 - Math.abs(m - r.tp)/span; w.push(Math.max(.25, x)); ws += w[w.length-1]; }
    for (let i = a; i <= b; i++){ const f = w[i-a]/ws; bins[i] += (r.v || 0)*f; dl[i] += (r.d || 0)*f; } });
  let pi = 0; for (let i = 1; i < nb; i++) if (bins[i] > bins[pi]) pi = i;
  let tot = 0; for (let i = 0; i < nb; i++) tot += bins[i]; let acc = bins[pi], a = pi, b = pi;
  while (acc < tot*0.7 && (a > 0 || b < nb-1)){ const up = b < nb-1 ? bins[b+1] : -1, dn = a > 0 ? bins[a-1] : -1; if (up >= dn){ b++; acc += bins[b]; } else { a--; acc += bins[a]; } }
  return {poc:lo + (pi+.5)*st, vah:lo+(b+1)*st, val:lo+a*st, lo, hi, st, bins:[...bins], dl:[...dl], max:bins[pi], pi};
}
/* per-indicator notes: what it is and how to read it (shown with the ⓘ button in the Indicators menu) */
const IND_HELP = {
  ma:["Moving averages (SMA / EMA / WMA, up to 7 lines). Fast lines (9-21) follow price; slow ones (50-200) show the swing trend. Price above a line = bullish bias, below = bearish; a fast line crossing a slow one = momentum shift. EMA reacts fastest, SMA is smoothest, WMA weights recent bars more.","المتوسطات المتحركة (SMA / EMA / WMA، لحد 7 خطوط). الفترات القصيرة (9-21) بتتبع السعر؛ الطويلة (50-200) اتجاه السوينج. السعر فوق الخط = تحيز صاعد، تحته = هابط؛ تقاطع خط سريع مع بطيء = تحول زخم. EMA أسرع رد فعل، SMA أنعم، WMA بيوزن الشموع الأحدث أكتر."],
  vwap:["VWAP: average price weighted by volume. Above = buyers in control, below = sellers. Institutions use it as a fair-value line.","VWAP: متوسط السعر موزون بالحجم. فوقه = المشترين مسيطرين، تحته = البائعين. خط القيمة العادلة للمؤسسات."],
  sig:["Scanner signal: BUY/SELL arrow on the signal candle with the plan (Entry blue, SL red, TP green). Past journal signals for this symbol also show as arrows (green ✓ hit TP, red ✗ hit SL). Drag the plan handle to resize the lines.","إشارة السكانر: سهم شراء/بيع على شمعة الإشارة مع الخطة (دخول أزرق، ستوب أحمر، أهداف خضرا). إشارات الجورنال السابقة للرمز بتظهر كأسهم (✓ ضرب الهدف، ✗ ضرب الستوب). اسحب مقبض الخطة لتغيير الطول."],
  flow:["Classic order-flow lines: a coloured level where heavy absorption or a sweep (liquidity grab) just happened. Price often reacts there again.","خطوط تدفق الأوامر: مستوى ملوّن فيه امتصاص قوي أو سحب سيولة. السعر غالباً بيتفاعل معاه تاني."],
  mk:["BUY/SELL markers from absorption: ▲ = buyers absorbed selling (bounce candidate), ▼ = sellers absorbed buying. The line is the level, the dotted target is 1.5×ATR.","علامات شراء/بيع من الامتصاص: ▲ المشترين امتصوا البيع، ▼ البائعين امتصوا الشراء. الخط هو المستوى والهدف 1.5×ATR."],
  volume:["Volume bars under price, coloured by real delta (buy minus sell) when trades are flowing. Big green = aggressive buying, big red = aggressive selling; a big bar with a tiny candle = absorption.","أعمدة الفوليوم ملوّنة بالدلتا الحقيقية (شراء − بيع). أخضر كبير = شراء عدواني، أحمر كبير = بيع عدواني؛ عمود كبير مع شمعة صغيرة = امتصاص."],
  rsi:["RSI: momentum 0–100. Above 70 = overbought, below 30 = oversold. Divergence (price makes a new high, RSI doesn't) warns of reversal.","RSI: الزخم من 0 لـ100. فوق 70 تشبع شرائي، تحت 30 تشبع بيعي. الدايفرجنس (سعر قمة جديدة وRSI لأ) تحذير انعكاس."],
  macd:["MACD: trend momentum. Line crossing above the signal line = bullish; histogram growing = momentum building. Best used with the trend, not against it.","MACD: زخم الاتجاه. تقاطع الخط فوق السيجنال = صاعد؛ الهيستوجرام بيكبر = الزخم بيزيد. الأفضل مع الاتجاه مش ضده."],
  vp:["Volume Profile (right side): volume per price row. POC = most traded price (magnet), VAH/VAL = 70% value area. Each row splits green (buy) / red (sell) with its delta; thin rows between thick ones are gaps — price tends to move fast through them.","بروفايل الحجم (يمين): الحجم لكل مستوى سعر. POC أكتر سعر اتداول (مغناطيس)، VAH/VAL منطقة القيمة 70%. كل صف أخضر (شراء)/أحمر (بيع) مع الدلتا؛ الصفوف الرفيعة بين سميكة = فجوات والسعر بيعدي فيها بسرعة."],
  bvd:["Breakout Volume Delta: when price closes through a swing high/low it labels who was stronger inside the breakout bar (▲ BUY n% / ▼ SELL n% / ⚠ weak). '~' means estimated from the candle, no live trades yet.","Breakout Volume Delta: لما السعر يكسر قمة/قاع بيكتب مين كان الأقوى جوه شمعة الكسر. '~' = تقدير من الشمعة."],
  ew:["Elliott waves (auto): the last confirmed swing pivots are numbered 1-2-3-4-5 when they obey the impulse rules (wave 2 never beyond the start, wave 3 never the shortest, wave 4 never overlaps wave 1) and A-B-C after it. Wave 3 is usually the strongest; after 5 expect a correction. Labels carry the timeframe — a count on 5m is a small wave inside the 1H one.","موجات إليوت (تلقائي): آخر قمم وقيعان مؤكدة بتتسمّى 1-2-3-4-5 لو بتحترم قواعد الموجة الدافعة (الموجة 2 ما تتخطاش البداية، الموجة 3 مش الأقصر، الموجة 4 ما تلمسش منطقة الموجة 1) وبعدها A-B-C. الموجة 3 غالباً الأقوى؛ بعد 5 توقع تصحيح. الرقم بيتكتب مع التايم فريم."],
  harm:["Harmonic patterns (Gartley/Bat/Butterfly/Crab/Cypher): X-A-B-C-D legs with Fibonacci ratios. The D point is the potential reversal zone; confirm with a candle before entering.","الهارمونيك: أرجل X-A-B-C-D بنسب فيبوناتشي. نقطة D منطقة انعكاس محتملة؛ أكّد بشمعة قبل الدخول."],
  kz:["Kill zones: Asia/London/New York session boxes. Highs/lows of finished sessions are liquidity that price often raids. Most reliable setups appear in London and NY.","كيل زون: صناديق آسيا/لندن/نيويورك. قمم وقيعان الجلسات المنتهية سيولة السعر بيسحبها. أقوى السيناريوهات في لندن ونيويورك."],
  fp:["Footprint: sell × buy volume at each price inside each candle. Imbalances (one side far bigger) show who is pushing; big numbers at the extremes = absorption.","فوتبرنت: حجم البيع × الشراء لكل سعر جوه الشمعة. عدم التوازن بيوضح مين بيدفع؛ أرقام كبيرة عند الأطراف = امتصاص."],
  delta:["Delta per candle: buy volume minus sell volume. Positive = buyers aggressive. Price rising on falling delta = weak move.","دلتا كل شمعة: شراء − بيع. موجبة = مشترين عدوانيين. سعر طالع ودلتا نازلة = حركة ضعيفة."],
  bub:["Bubbles: big prints (smart/whale) sized by volume, green buy / red sell. Clusters at a level = real interest there.","فقاعات: صفقات كبيرة (سمارت/حوت) بحجم الحجم، أخضر شراء/أحمر بيع. تجمّع عند مستوى = اهتمام حقيقي."],
  dot:["Dots: ◆ sweep (liquidity grabbed) and ⊗ absorption (heavy volume, price barely moves). Number ×n = repeats collapsed into one.","نقط: ◆ سحب سيولة و⊗ امتصاص. ×n = تكرارات اتجمعت في علامة واحدة."],
  dom:["Depth heat-map: resting limit orders (bid/ask) over time. Bright bands = big walls; vanishing walls = spoofing or filled orders.","خريطة العمق: الأوامر المعلقة بمرور الوقت. أشرطة ساطعة = جدران كبيرة؛ اختفاؤها = سحب أو تنفيذ."],
  adx:["ADX / DMI (Wilder, 14): ADX (gold) measures trend STRENGTH, not direction: above 25 = trending, below 20 = range. +DI (green) above -DI (red) = buyers lead, below = sellers lead. A rising ADX with +DI on top = strong up-trend.","ADX / DMI (وايلدر 14): الـ ADX (دهبي) بيقيس قوة الترند مش اتجاهه: فوق 25 = فيه ترند، تحت 20 = رينج. +DI (أخضر) فوق -DI (أحمر) = المشترين ماسكين، تحته = البايعين. ADX طالع و+DI فوق = ترند صاعد قوي."],
  cci:["CCI (20): how far the typical price is from its average, in units of mean deviation. Above +100 = unusually strong (momentum or overbought), below -100 = unusually weak. Crossing back inside ±100 often marks the end of the push.","CCI (20): السعر بعيد قد إيه عن متوسطه. فوق +100 = قوة غير عادية (زخم أو تشبع شراء)، تحت -100 = ضعف غير عادي. الرجوع جوه ±100 غالباً نهاية الموجة."],
  psar:["Parabolic SAR (0.02 / 0.2): dots under the candles = up-trend (green), above = down-trend (red). When price touches the dots they flip sides - a trailing-stop and trend-flip tool. Weak in sideways markets.","Parabolic SAR (0.02 / 0.2): نقط تحت الشموع = ترند صاعد (أخضر)، فوق = هابط (أحمر). لما السعر يلمس النقط بتقلب الناحية التانية - أداة وقف متحرك وتغيّر ترند. ضعيف في السوق العرضي."],
  dot3:["Depth of Trade: one switch for bubbles + depth heat-map + dots + BUY/SELL markers. ⚙ opens colours and sizes.","Depth of Trade: مفتاح واحد للفقاعات + خريطة العمق + النقط + علامات الشراء/البيع. ⚙ للألوان والأحجام."],
};
/* Chart modes = indicator bundles (ids of the Indicators menu). Everything not listed is switched off, except display options. */
const CHART_MODES = [
  {id:"clean", en:"Clean", ar:"نظيف", on:["ma","volume","sig"], ma:[9,21], tipEn:"Candles, EMA 9/21, volume and scanner signals only.", tipAr:"شموع + EMA 9/21 + فوليوم + إشارات السكانر بس."},
  {id:"kzs", en:"Kill Zone Sniper", ar:"قناص الكيل زون", on:["ma","kz","kzs","volume","sig"], ma:[9,21], tipEn:"Sessions + kill zones, the Kill Zone Sniper overlay, EMA 9/21 (the REJ filter), volume, signals. Intraday (1H and lower).", tipAr:"الجلسات + الكيل زون + قناص الكيل زون + EMA 9/21 + فوليوم + إشارات. للانترادي (ساعة وأقل)."},
  {id:"smc", en:"ICT / SMC", ar:"ICT / SMC", on:["ma","kz","lv","ll","smt","sig","volume"], ma:[9,21], tipEn:"Liquidity view: sessions, open levels, XPIX MTF liquidity levels, SMT, signals.", tipAr:"عرض السيولة: الجلسات، مستويات الفتح، مستويات XPIX، SMT، الإشارات."},
  {id:"flow", en:"Order flow", ar:"أوردر فلو", on:["vwap","dcol","bub","dot","dom","mk","delta","vp","volume","sig"], tipEn:"Order-flow column, bubbles, dots, depth, delta, volume profile, VWAP.", tipAr:"عمود الأوردر فلو، الفقاعات، النقط، العمق، الدلتا، بروفايل الفوليوم، VWAP."},
  {id:"swing", en:"Swing", ar:"سوينج", on:["ma","don","lv","ll","rsi","adx","sig","volume"], ma:[21,50], tipEn:"EMA 21/50, Donchian ensemble, open levels, XPIX levels, RSI, ADX (trend strength). Best on 4H / 1D.", tipAr:"EMA 21/50، Donchian، مستويات الفتح، مستويات XPIX، RSI، ADX (قوة الترند). أحسن على 4 ساعات / يومي."},
  {id:"mt5", en:"MT5", ar:"MT5", on:["mt5","r2","volume","sig"], tipEn:"The MT5 phone layout: MA ribbon + SAR + fractals and the RSI(2) + OsMA window.", tipAr:"شكل شارت MT5: ريبون المتوسطات + SAR + فراكتال ونافذة RSI(2) + OsMA."},
];
const indHelp = id => { const v = IND_HELP[id]; return v ? v[lang === "ar" ? 1 : 0] : ""; };
const VP_TFS = [["5m","5m"],["15m","15m"],["1H","1H"],["4H","4H"],["1D","1D"]];
const FIB_PRESETS = {
  "Retracement":[0,0.236,0.382,0.5,0.618,0.786,1],
  "Fibo POP":[0,0.5,0.559,0.669,0.786,1],
  "Fib Monkey Strategy":[-0.99,-0.66,-0.33,0.03,0.63,0.78,0.99],
  "Fib Target Prices":[0,0.5,1,-1,-2,-2.5,-3,-4],
  "SNR (Support & Resistance)":[2.64,2.6,2.56,2.47,1.55,1,0,-0.21,-0.255,-0.29],
  "CRT (Candle Range Theory)":[2.64,2.6,2.56,1.55,1.47,1,0,-0.21,-0.255,-0.29,-0.4],
  "OTE (Optimal Trade Entry)":[0,0.5,0.62,0.705,0.79,1],
  "Zone Gold & Silver":[0,0.232,0.25,0.688,0.718,0.786,0.804,0.822,1],
  "Premium / Discount":[0,0.5,1],
  "Fib retracement (earn every day)":[2.64,2.6,2.56,1.55,1.47,1,0,-0.21,-0.255,-0.3,-0.39]
};
const TFS = [["5s","5s"],["15s","15s"],["30s","30s"],["1m","1m"],["5m","5m"],["13m","13m"],["15m","15m"],["30m","30m"],["1H","1h"],["2H","2h"],["3H","3h"],["4H","4h"],["6H","6h"],["7H","7h"],["8H","8h"],["12H","12h"],["1D","1d"],["3D","3d"],["1W","1w"],["1M","1M"]];

