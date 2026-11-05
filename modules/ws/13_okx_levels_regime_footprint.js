/* OKX calls are shared: every panel asks for the same endpoints (open interest, positioning, funding), and OKX answers 429 when they
   all fire at once. One request per path is in flight or cached for a short time (rubik stats: 60 s, prices: 3 s); a 429 is reported
   as a rate limit instead of being retried in a loop. */
const OKX_CACHE = {};
// the rubik cooldown survives the workspace iframe being rebuilt (each rebuild used to re-hit OKX and reload the chart)
let OKX_COOL = 0; try { OKX_COOL = +(sessionStorage.getItem("okx_cool") || 0); } catch(e){}
const okxCoolSet = (t) => { OKX_COOL = t; try { sessionStorage.setItem("okx_cool", String(t)); } catch(e){} };
let OKX_RUB_DEAD = 0; try { OKX_RUB_DEAD = +(localStorage.getItem("okx_rub_dead") || 0); } catch(e){}   // OKX sends no CORS header on /rubik/ to this page: after one real failure the browser stops asking for 6 h (shared by all tabs)
let OKX_RUB_PROBE = null;   // the first /rubik/ request is a probe, the other coins wait for its answer instead of all firing (and failing) at once
const OKX_COOL_P = {}; let OKX_COOL_ALL = 0;   // global pause for candle requests after any 429   // per-path cooldown after a 429 (candles and other non-rubik paths)
function okx(path){
  if (/instId=Y%3A/i.test(path)) return yfOkx(path);
  if (/instId=HL%3A/i.test(path)) return hlOkx(path);
  const rub = /\/rubik\//.test(path);
  // Live order-book / trade snapshots are polled every 1.5 s by Hub. Do not reuse a 10 s cache entry for these endpoints.
  // Keep a short 1.2 s in-flight/repeat guard to coalesce overlapping requests without serving stale snapshots across polling ticks.
  const liveFlow = /\/market\/(?:books(?:-full)?|trades)\?/.test(path), ttl = rub ? 120000 : liveFlow ? 1200 : 10000, hit = OKX_CACHE[path];
  let shared = 0; try { shared = +(localStorage.getItem("okx_cool_all") || 0); } catch(e){}   // another tab of this browser hit the limit: this tab waits too (both tabs share one IP)
  if (shared > Date.now() + 20000) shared = 0;   // never trust a pause that is far in the future
  const liveTick = /\/market\/candles\?/.test(path) && /[?&]limit=(?:[1-9]|[1-3]\d|40)(?:&|$)/.test(path);   // the small refresh poll of an open chart (2 s loop): a healthy tab keeps it alive, only the big history loads wait for the other tab's pause
  const tickP = /\/market\/tickers\?/.test(path), cool = (liveFlow || tickP) ? (OKX_COOL_P[path] || 0) : Math.max(OKX_COOL_P[path] || 0, OKX_COOL_ALL, liveTick ? 0 : shared);   // the order book / tape / price-list polls are not held back by a candle 429 pause: only their own path's short pause applies
  if (!rub && Date.now() < cool) return Promise.reject(new Error("OKX rate limit: waiting before retry"));
  if (hit && Date.now() - hit.t < ttl) return hit.p;
  if (rub && Date.now() < OKX_COOL) return Promise.reject(new Error(Lg("OKX rate limit: paused for a few minutes","OKX: حد الطلبات، متوقف لدقايق")));
  if (rub && Date.now() < OKX_RUB_DEAD) return Promise.reject(new Error("OKX stats are blocked from the browser (CORS): skipped"));
  if (rub && OKX_RUB_PROBE) return OKX_RUB_PROBE.then(() => okx(path));
  if (rub){   // stats are slow-moving: reuse the last answer from this browser for 2 minutes, even after a refresh
    try { const st = JSON.parse(localStorage.getItem("okxc:"+path) || "null"); if (st && Date.now() - st.t < ttl){ OKX_CACHE[path] = {t: st.t, p: Promise.resolve(st.v)}; return OKX_CACHE[path].p; } } catch(e){}
  }
  const p = (async () => {
    let r;
    const ac = new AbortController(), tmo = setTimeout(() => ac.abort(), 15000);   // no answer in 15 s: give up, the polling loop tries again (a stuck request froze the chart until a refresh)
    try { r = await fetch(API + "/api/v5" + path, {cache:"no-store", signal:ac.signal}); clearTimeout(tmo); }
    catch(e){ clearTimeout(tmo); if (e && e.name === "AbortError") throw new Error("OKX timeout");   // CORS or network failure (the rubik stats send no CORS header to this page): pause the rubik family instead of retrying every symbol (owner's console, 2026-10-19)
      if (rub){ okxCoolSet(Date.now() + 600000); OKX_RUB_DEAD = Date.now() + 6*3600e3; try { localStorage.setItem("okx_rub_dead", String(OKX_RUB_DEAD)); } catch(e2){} }
      throw new Error("OKX blocked from this page (CORS / network): stats paused 10 min");
    }
    // one 429 pauses every candle request for a while: many timeframes and symbols were each retrying
    // the shared (cross-tab) pause is set once and never extended by repeated 429s (a blocked tab used to keep the other tab frozen), with jitter so two tabs do not retry together
    if (r.status === 429){ if (rub) okxCoolSet(Date.now() + 180000); else { OKX_COOL_P[path] = Date.now() + ((liveFlow || tickP) ? 4000 : 30000); const until = Date.now() + 8000 + Math.floor(Math.random()*7000); OKX_COOL_ALL = Math.max(OKX_COOL_ALL, until); try { if ((+(localStorage.getItem("okx_cool_all") || 0)) < Date.now()) localStorage.setItem("okx_cool_all", String(until)); } catch(e){} } throw new Error("OKX rate limit (429): wait a few minutes"); }
    if (!r.ok) throw new Error("HTTP "+r.status);
    const j = await r.json();
    if (j.code !== "0") throw new Error(j.msg || ("code "+j.code));
    if (rub) try { localStorage.setItem("okxc:"+path, JSON.stringify({t: Date.now(), v: j.data})); } catch(e){}
    return j.data;
  })();
  if (rub && !OKX_RUB_PROBE){ const pr = p.catch(() => {}).then(() => { if (OKX_RUB_PROBE === pr) OKX_RUB_PROBE = null; }); OKX_RUB_PROBE = pr; }
  OKX_CACHE[path] = {t: Date.now(), p};
  p.catch(() => { if (OKX_CACHE[path] && OKX_CACHE[path].p === p) delete OKX_CACHE[path]; });   // failed calls are not cached
  return p;
}
/* OKX public liquidation orders (no key) for a symbol's perpetual family -> [{t, p, side:"L"|"S", usd}] newest first, or null for non-OKX symbols.
   forced SELL = longs liquidated, forced BUY = shorts liquidated; USD = contracts x ctVal x bankruptcy price (linear) or contracts x ctVal (inverse). */
/* ---- Gann astro (optional overlay): planetary longitudes computed here, no outside service. Checked: new / full moons 2024-2026 within 0.06 deg,
   Jupiter-Saturn conjunction 2020-12-21 within 0.07 deg, Mercury retrograde April 2024, March 2024 equinox. No scientific evidence that planets move prices;
   the only studied effect (lunar phase, Dichev & Janes 2001) was small and inconsistent in later data - the weekly lab measures it on our markets. ---- */
/* Planetary positions (Paul Schlyter's method, ~1-2 arcmin for inner planets, <1 deg for Jupiter / Saturn without the great-inequality terms).
   lon(body, ms, helio) -> ecliptic longitude in degrees (equinox of date). Moon / Sun are geocentric only. */
const Astro = (() => {
  const R = Math.PI/180, rev = x => ((x % 360) + 360) % 360, DAY0 = Date.UTC(1999, 11, 31);
  const EL = {
    mercury: d => [48.3313+3.24587e-5*d, 7.0047+5e-8*d, 29.1241+1.01444e-5*d, .387098, .205635+5.59e-10*d, 168.6562+4.0923344368*d],
    venus:   d => [76.6799+2.4659e-5*d, 3.3946+2.75e-8*d, 54.891+1.38374e-5*d, .72333, .006773-1.302e-9*d, 48.0052+1.6021302244*d],
    mars:    d => [49.5574+2.11081e-5*d, 1.8497-1.78e-8*d, 286.5016+2.92961e-5*d, 1.523688, .093405+2.516e-9*d, 18.6021+.5240207766*d],
    jupiter: d => [100.4542+2.76854e-5*d, 1.303-1.557e-7*d, 273.8777+1.64505e-5*d, 5.20256, .048498+4.469e-9*d, 19.895+.0830853001*d],
    saturn:  d => [113.6634+2.3898e-5*d, 2.4886-1.081e-7*d, 339.3939+2.97661e-5*d, 9.55475, .055546-9.499e-9*d, 316.967+.0334442282*d],
    uranus:  d => [74.0005+1.3978e-5*d, .7733+1.9e-8*d, 96.6612+3.0565e-5*d, 19.18171-1.55e-8*d, .047318+7.45e-9*d, 142.5905+.011725806*d],
    neptune: d => [131.7806+3.0173e-5*d, 1.77-2.55e-7*d, 272.8461-6.027e-6*d, 30.05826+3.313e-8*d, .008606+2.15e-9*d, 260.2471+.005995147*d]};
  const kep = (M, e) => { let E = M + e*Math.sin(M)*(1 + e*Math.cos(M)); for (let k = 0; k < 6; k++) E = E - (E - e*Math.sin(E) - M)/(1 - e*Math.cos(E)); return E; };
  const sun = d => { const w = 282.9404 + 4.70935e-5*d, e = .016709 - 1.151e-9*d, M = rev(356.047 + .9856002585*d)*R, E = kep(M, e), xv = Math.cos(E) - e, yv = Math.sqrt(1 - e*e)*Math.sin(E);
    const v = Math.atan2(yv, xv)/R, r = Math.hypot(xv, yv), lon = rev(v + w); return {lon, r, x:r*Math.cos(lon*R), y:r*Math.sin(lon*R), M:M/R, w}; };
  const helio = (b, d) => { let [N, i, w, a, e, M] = EL[b](d); M = rev(M)*R; const E = kep(M, e), xv = a*(Math.cos(E) - e), yv = a*Math.sqrt(1 - e*e)*Math.sin(E), v = Math.atan2(yv, xv), r = Math.hypot(xv, yv);
    N *= R; i *= R; w *= R; const xh = r*(Math.cos(N)*Math.cos(v + w) - Math.sin(N)*Math.sin(v + w)*Math.cos(i)), yh = r*(Math.sin(N)*Math.cos(v + w) + Math.cos(N)*Math.sin(v + w)*Math.cos(i));
    return {x:xh, y:yh, lon:rev(Math.atan2(yh, xh)/R)}; };
  const moon = d => { const N = rev(125.1228 - .0529538083*d), i = 5.1454, w = rev(318.0634 + .1643573223*d), e = .0549, M = rev(115.3654 + 13.0649929509*d);
    const E = kep(M*R, e), xv = Math.cos(E) - e, yv = Math.sqrt(1 - e*e)*Math.sin(E), v = Math.atan2(yv, xv)/R;
    const Nr = N*R, ir = i*R, vw = (v + w)*R, x = Math.cos(Nr)*Math.cos(vw) - Math.sin(Nr)*Math.sin(vw)*Math.cos(ir), y = Math.sin(Nr)*Math.cos(vw) + Math.cos(Nr)*Math.sin(vw)*Math.cos(ir);
    let lon = Math.atan2(y, x)/R; const S = sun(d), Ms = S.M, Ls = rev(Ms + S.w), Lm = rev(M + w + N), D = Lm - Ls, F = Lm - N, s = a => Math.sin(a*R);
    lon += -1.274*s(M - 2*D) + .658*s(2*D) - .186*s(Ms) - .059*s(2*M - 2*D) - .057*s(M - 2*D + Ms) + .053*s(M + 2*D) + .046*s(2*D - Ms) + .041*s(M - Ms) - .035*s(D) - .031*s(M + Ms) - .015*s(2*F - 2*D) + .011*s(M - 4*D);
    return rev(lon); };
  const memo = new Map();   // the chart redraws often with the same times: remember each body / time / frame (capped)
  const lon = (b, ms, h) => { const k = b + (h ? "h" : "g") + Math.round(ms/6e4); let v = memo.get(k); if (v === undefined){ if (memo.size > 200000) memo.clear(); v = lon0(b, ms, h); memo.set(k, v); } return v; };
  const lon0 = (b, ms, h) => { const d = (ms - DAY0)/864e5; if (b === "moon") return moon(d); const S = sun(d); if (b === "sun") return h ? rev(S.lon + 180) : S.lon;   // helio "sun" = Earth
    const P = helio(b, d); return h ? P.lon : rev(Math.atan2(P.y + S.y, P.x + S.x)/R); };
  return {lon, rev, BODIES:["sun","moon","mercury","venus","mars","jupiter","saturn","uranus","neptune"], GLYPH:{sun:"☉",moon:"☽",mercury:"☿",venus:"♀",mars:"♂",jupiter:"♃",saturn:"♄",uranus:"♅",neptune:"♆"}};
})();
const LIQ_CT = {};
function liqFam(sym){ const fam = String(sym).split("-").slice(0, 2).join("-"); return /^(Y|HL|FH):/.test(sym) || !/^[A-Z0-9]+-(USDT|USDC|USD)$/.test(fam) ? null : fam; }
async function okxLiqs(sym){
  const fam = liqFam(sym); if (!fam) return null;
  if (!LIQ_CT[fam]){ const ins = await okx("/public/instruments?instType=SWAP&instFamily="+encodeURIComponent(fam)), m = {}; ins.forEach(x => m[x.instId] = {v:+x.ctVal || 0, inv:x.ctType === "inverse"}); LIQ_CT[fam] = m; }
  const d = await okx("/public/liquidation-orders?instType=SWAP&instFamily="+encodeURIComponent(fam)+"&state=filled&limit=100"), out = [];
  (d || []).forEach(g => { const c = LIQ_CT[fam][g.instId] || Object.values(LIQ_CT[fam])[0] || {v:0}; (g.details || []).forEach(x => { const p = +x.bkPx, q = +x.sz;
    out.push({t:+x.ts, p, side:x.side === "sell" ? "L" : "S", usd:c.inv ? q*c.v : q*c.v*p}); }); });
  return out.sort((a, b) => b.t - a.t);
}
async function syncClock(){ try { const t0 = Date.now(), r = await okx("/public/time"), t1 = Date.now(); if (r && r[0] && +r[0].ts > 0) SKEW = +r[0].ts + (t1-t0)/2 - t1; } catch(e){} }
syncClock(); setInterval(syncClock, 300000);
function aggBars(rows, n, unitMs){ const W = n*unitMs, out = []; rows.forEach(r => { const b = Math.floor(r.t/W)*W, l = out[out.length-1]; if (l && l.t === b){ l.h = Math.max(l.h, r.h); l.l = Math.min(l.l, r.l); l.c = r.c; l.v += r.v; l.n++; } else out.push({t:b, o:r.o, h:r.h, l:r.l, c:r.c, v:r.v, n:1}); }); return out; }
const parseRows = rows => rows.map(x => ({t:+x[0], o:+x[1], h:+x[2], l:+x[3], c:+x[4], v:+x[5]})).reverse();
/* Daily / weekly support & resistance from 1D and 1W candles (OKX history, no order book needed): swing pivots (3 bars each side) are clustered inside 0.6 ATR; touches = pivots in the cluster,
   strength 1-5 = touches weighted towards recent bars. A line above the last price is resistance, below is support. Computed in the browser, cached 1 h per symbol. NOT a signal: levels the market reacted at before. */
const SR = {
  cache:{}, busy:{},
  compute(rows, k){ k = k || 3; const n = rows.length; if (n < 2*k + 5) return []; const cp = rows[n-1].c;
    let atr = 0, m = Math.min(14, n-1); for (let i = n-m; i < n; i++) atr += Math.max(rows[i].h - rows[i].l, Math.abs(rows[i].h - rows[i-1].c), Math.abs(rows[i].l - rows[i-1].c)); atr /= m; const tol = Math.max(atr*0.6, cp*0.002);
    const pv = []; for (let i = k; i < n-k; i++){ let hh = true, ll = true; for (let j = i-k; j <= i+k; j++){ if (j === i) continue; if (rows[j].h >= rows[i].h) hh = false; if (rows[j].l <= rows[i].l) ll = false; } const w = 0.5 + 0.5*i/n; if (hh) pv.push({p:rows[i].h, w, i}); if (ll) pv.push({p:rows[i].l, w, i}); }
    pv.sort((a, b) => a.p - b.p); const cl = []; pv.forEach(q => { const c = cl[cl.length-1]; if (c && q.p - c.max <= tol){ c.s += q.p; c.n++; c.w += q.w; c.max = q.p; c.last = Math.max(c.last, q.i); } else cl.push({s:q.p, n:1, w:q.w, max:q.p, last:q.i}); });
    return cl.filter(c => c.n >= 2).map(c => { const p = c.s/c.n; return {p, touches:c.n, strength:Math.max(1, Math.min(5, Math.round(c.w*1.1))), kind:p > cp ? "R" : "S", dist:(p-cp)/cp*100, lastBar:rows[c.last].t}; }).sort((a, b) => Math.abs(a.dist) - Math.abs(b.dist)); },
  async load(sym){ const hit = this.cache[sym]; if (hit && Date.now() - hit.t < 3600000) return hit; if (this.busy[sym]) return this.busy[sym];
    const p = (async () => { try { const [d, w] = await Promise.all([candlesTf(sym, "1D", true, 200).catch(() => []), candlesTf(sym, "1W", true, 120).catch(() => [])]);
        const o = {t:Date.now(), D:this.compute(d), W:this.compute(w), nD:d.length, nW:w.length}; if (d.length || w.length) this.cache[sym] = o; return o; } finally { delete this.busy[sym]; } })();
    this.busy[sym] = p; return p; },
  top(lv, n){ const R = lv.filter(x => x.kind === "R").slice(0, n), S = lv.filter(x => x.kind === "S").slice(0, n); return R.concat(S); }
};
/* REGIME-BEGIN market regime of the latest candle (same definitions and numbers as modules/regime.py; tests/test_regime_js_parity.py runs both on the same candles) */
const Regime = {
  wilder(x, n){ const o = new Array(x.length).fill(NaN); if (x.length <= n) return o; let s = 0, k = 0; for (let i = 1; i <= n; i++){ if (x[i] === x[i]) { s += x[i]; k++; } } o[n] = k ? s/k : NaN; for (let i = n+1; i < x.length; i++) o[i] = (o[i-1]*(n-1) + x[i])/n; return o; },
  atrAdx(d, n = 14){ const L = d.length, tr = new Array(L), pdm = new Array(L), mdm = new Array(L);
    for (let i = 0; i < L; i++){ const pc = i ? d[i-1].c : d[0].c, up = i ? d[i].h - d[i-1].h : 0, dn = i ? d[i-1].l - d[i].l : 0; tr[i] = Math.max(d[i].h - d[i].l, Math.abs(d[i].h - pc), Math.abs(d[i].l - pc)); pdm[i] = (up > dn && up > 0) ? up : 0; mdm[i] = (dn > up && dn > 0) ? dn : 0; }
    const atr = Regime.wilder(tr, n), ps = Regime.wilder(pdm, n), ms = Regime.wilder(mdm, n), dx = new Array(L).fill(NaN);
    for (let i = 0; i < L; i++){ const pdi = 100*ps[i]/atr[i], mdi = 100*ms[i]/atr[i], v = 100*Math.abs(pdi - mdi)/(pdi + mdi); dx[i] = isFinite(v) ? v : NaN; }
    const adx = new Array(L).fill(NaN); let f = dx.findIndex(v => v === v); if (f >= 0 && f + n < L){ let s = 0; for (let i = f; i < f + n; i++) s += dx[i]; adx[f+n-1] = s/n; for (let i = f + n; i < L; i++) adx[i] = (adx[i-1]*(n-1) + dx[i])/n; }
    return {atr, adx}; },
  of(d){   // -> {regime, adx, atrRatio, bbPct, volPct, retZ}; regime = null with fewer than 60 candles
    if (!d || d.length < 60) return {regime:null}; const LOOK = 100, L = d.length, {atr, adx} = Regime.atrAdx(d), c = d.map(x => x.c), tail = (a, n) => a.slice(Math.max(0, a.length - n)), fin = a => a.filter(v => v === v);
    const med = a => { const b = a.slice().sort((x, y) => x - y), m = b.length >> 1; return b.length % 2 ? b[m] : (b[m-1] + b[m])/2; };
    const aw = fin(tail(atr, LOOK)), atrRatio = aw.length && med(aw) > 0 ? atr[L-1]/med(aw) : null;
    const bbw = c.map((_, i) => { if (i < 19) return NaN; let m = 0; for (let j = i-19; j <= i; j++) m += c[j]; m /= 20; let v = 0; for (let j = i-19; j <= i; j++) v += (c[j]-m)*(c[j]-m); return 4*Math.sqrt(v/20)/m; });
    const bw = fin(tail(bbw, LOOK)), bbPct = bw.length > 10 && bbw[L-1] === bbw[L-1] ? bw.filter(v => v < bbw[L-1]).length/bw.length*100 : null;
    const r5 = c.map((v, i) => i >= 5 ? v/c[i-5] - 1 : NaN), z = fin(tail(r5, LOOK)); let retZ = null; if (z.length > 10 && r5[L-1] === r5[L-1]){ const m = z.reduce((a, b) => a + b, 0)/z.length, sd = Math.sqrt(z.reduce((a, b) => a + (b-m)*(b-m), 0)/z.length); if (sd > 0) retZ = (r5[L-1] - m)/sd; }
    let volPct = null; { const v = tail(d.map(x => +x.v || 0), LOOK), sum = v.reduce((a, b) => a + b, 0), nz = v.filter(x => x !== 0).length; if (sum > 0 && nz > v.length*0.5){ const last = v[v.length-1]; volPct = (v.filter(x => x < last).length + v.filter(x => x <= last).length)/2/v.length*100; } }
    const x = adx[L-1]; let g;
    if (retZ !== null && retZ < -2) g = "Crash"; else if (atrRatio !== null && atrRatio > 1.5) g = "Hi-Vol"; else if (bbPct !== null && bbPct < 20) g = "Squeeze"; else if (volPct !== null && volPct < 20) g = "Thin";
    else if (x === x && x > 25) g = "Trend"; else if (x === x && x < 20 && atrRatio !== null && atrRatio < 1) g = "Chop"; else g = "Mixed";
    return {regime:g, adx:x === x ? x : null, atrRatio, bbPct, volPct, retZ}; },
  cache:{k:"", v:null},
  now(d){ if (!d || !d.length) return null; const l = d[d.length-1], k = d.length+"|"+l.t+"|"+l.c+"|"+l.h+"|"+l.l; if (Regime.cache.k !== k) Regime.cache = {k, v:Regime.of(d)}; return Regime.cache.v; },
  col:{Trend:"#4aa3ff", Chop:"#848e9c", "Hi-Vol":"#f0b90b", Crash:"#f6465d", Squeeze:"#b57cff", Thin:"#6b7684"}
};
/* REGIME-END */
const FP_BARS = 12, FP_PAGES = 120;   // footprint: how many newest candles get real per-price volume (was 3), and the cap of history-trades calls to fill them (was 40)
/* FPS-BEGIN persistent footprint store: prints summed per 1-minute x price, kept in this browser (IndexedDB) for FPS.KEEP, plus the time ranges (from, to] that are KNOWN to be complete.
   A candle of any timeframe >= 1m is rebuilt from the minutes; a candle outside the known ranges says "partial" instead of looking complete. Pure functions are tested in node (tests/test_footprint_store.py). */
const FPS = {
  MIN: 60000, KEEP: 72*3600000, DB: "xpix_fp", off: false,
  pad: t => String(Math.max(0, Math.floor(t))).padStart(13, "0"),
  join(cov, a, b){ if (!(b > a)) return cov.slice(); let na = a, nb = b; const out = [];   // add (a, b] to a sorted list of ranges; ranges that touch merge
    cov.forEach(([x, y]) => { if (y < na || x > nb) out.push([x, y]); else { na = Math.min(na, x); nb = Math.max(nb, y); } }); out.push([na, nb]); return out.sort((p, q) => p[0] - q[0]); },
  span(cov, t){ return cov.find(([x, y]) => t > x && t <= y) || null; },   // the known range that holds a print time, or null
  has(cov, a, b){ return cov.some(([x, y]) => x <= a && y >= b); },       // is the whole stretch a..b inside one known range
  group(trades){ const g = new Map(); trades.forEach(([t, p, q, side]) => { const k = Math.floor(t/FPS.MIN)*FPS.MIN; let m = g.get(k); if (!m) g.set(k, m = new Map()); let o = m.get(p); if (!o) m.set(p, o = [0, 0]); o[side === "Buy" ? 0 : 1] += q; }); return g; },
  flat(m){ const a = []; m.forEach(([b, s], p) => a.push(p, b, s)); return a; },                       // one minute -> [price, buy, sell, price, buy, sell...]
  merge(old, m){ const g = new Map(); if (old) for (let i = 0; i + 2 < old.length; i += 3) g.set(old[i], [old[i+1], old[i+2]]); m.forEach(([b, s], p) => { const o = g.get(p); if (o) g.set(p, [o[0] + b, o[1] + s]); else g.set(p, [b, s]); }); return FPS.flat(g); },
  fold(mins, ch, ms, cov, now){   // stored minutes -> the candles of the chart (ms = candle length in ms, >= 60000); each candle gets .part when it is not wholly inside a known range
    const d = ch.data; if (!d.length || ms < FPS.MIN) return 0; let n = 0; const ks = [...mins.keys()].sort((a, b) => a - b); let i = 0;
    ks.forEach(k => { if (k < d[0].t) return; while (i + 1 < d.length && d[i+1].t <= k) i++; const key = d[i].t; let m = ch.fp.get(key); if (!m){ m = {px:new Map(), b:0, s:0}; ch.fp.set(key, m); }
      const a = mins.get(k); for (let j = 0; j + 2 < a.length; j += 3){ let o = m.px.get(a[j]); if (!o) m.px.set(a[j], o = {b:0, s:0}); o.b += a[j+1]; o.s += a[j+2]; m.b += a[j+1]; m.s += a[j+2]; } n++; });
    FPS.mark(ch, ms, cov, now); return n; },
  mark(ch, ms, cov, now){ ch.fp.forEach((m, key) => { const b = Math.min(key + ms, now || key + ms); m.part = b > key ? !FPS.has(cov, key, b) : false; }); },   // a candle that starts after the verified end (just opened) is not flagged: nothing is missing from it yet
  cover(items, now, tol){   // items = [[bucket start, bucket length]] of recorded book history: where it starts, how many holes (> tol ms with nothing recorded) it has, and where the unbroken run that ends now begins
    const a = items.slice().sort((x, y) => x[0] - y[0]); if (!a.length) return {oldest:0, runFrom:0, gaps:0, gapMs:0}; let gaps = 0, gapMs = 0, run = a[0][0];
    for (let i = 1; i < a.length; i++){ const hole = a[i][0] - (a[i-1][0] + a[i-1][1]); if (hole > tol){ gaps++; gapMs += hole; run = a[i][0]; } }
    const tail = now - (a[a.length-1][0] + a[a.length-1][1]); if (tail > tol){ gaps++; gapMs += tail; run = 0; }   // nothing recorded lately: there is no unbroken run up to now
    return {oldest:a[0][0], runFrom:run, gaps, gapMs}; },
  hmMerge(H, o, cut){   // saved book history o = {step, b:{t:{w, m, c:[[row, size]]}}} into the live one H = {step, b:Map}; same grid only; a cell keeps the larger size. returns buckets touched
    if (!o || !o.step || !o.b) return 0; if (!H.step || !H.b.size) H.step = o.step; if (H.step !== o.step) return 0; let n = 0;
    Object.keys(o.b).forEach(k => { const t = +k; if (t < cut) return; const x = o.b[k], cur = H.b.get(t);
      if (!cur){ H.b.set(t, {w:x.w, m:x.m, c:new Map(x.c)}); n++; return; }
      let ch = false; x.c.forEach(([r, q]) => { const v = cur.c.get(r); if (v == null || q > v){ cur.c.set(r, q); ch = true; } }); if (ch) n++; });
    return n; },
  async getHm(sym){ const db = FPS.off ? null : await FPS.open(); if (!db) return null;
    return new Promise(res => { try { let out = null; const tx = db.transaction("m", "readonly"); tx.objectStore("m").get("hm|"+sym).onsuccess = e => { out = e.target.result || null; }; tx.oncomplete = () => { db.close(); res(out); }; tx.onerror = tx.onabort = () => { db.close(); res(null); }; } catch(e){ res(null); } }); },
  async putHm(sym, obj){ const db = FPS.off ? null : await FPS.open(); if (!db) return false;
    return new Promise(res => { try { const tx = db.transaction("m", "readwrite"); tx.objectStore("m").put(obj, "hm|"+sym); tx.oncomplete = () => { db.close(); res(true); }; tx.onerror = tx.onabort = () => { db.close(); res(false); }; } catch(e){ res(false); } }); },
  since(cov){ return cov.length ? cov[cov.length-1][0] : 0; },
  open(){ return new Promise(res => { try { const rq = indexedDB.open(FPS.DB, 1); rq.onupgradeneeded = () => rq.result.createObjectStore("m"); rq.onsuccess = () => res(rq.result); rq.onerror = () => res(null); rq.onblocked = () => res(null); } catch(e){ res(null); } }); },
  async pull(base, sym, a, b){   // the always-on recorder (CFG.fpServer, recorder/footprint_recorder.py): {cov, mins} of the minutes it heard, or null
    try { const r = await fetch(base+"/fp?sym="+encodeURIComponent(sym)+"&from="+Math.floor(a)+"&to="+Math.floor(b)); if (!r.ok) return null; const j = await r.json(); return j && Array.isArray(j.cov) && j.mins && typeof j.mins === "object" ? j : null; } catch(e){ return null; } },
  async adopt(sym, j){   // the recorder is authoritative for whole minutes inside the ranges it listened: replace them in the store and mark those ranges known (edge minutes it only heard in part are left as they are)
    const db = FPS.off ? null : await FPS.open(); if (!db) return false;
    return new Promise(res => { try { const tx = db.transaction("m", "readwrite"), st = tx.objectStore("m"), ck = "cov|"+sym;
        st.get(ck).onsuccess = e => { let cov = e.target.result || [];
          j.cov.forEach(([a, b]) => { const A = Math.ceil(a/FPS.MIN)*FPS.MIN, B = Math.floor(b/FPS.MIN)*FPS.MIN; if (!(B > A)) return;
            st.delete(IDBKeyRange.bound(sym+"|"+FPS.pad(A), sym+"|"+FPS.pad(B - FPS.MIN)));
            Object.keys(j.mins).forEach(k => { const m = +k; if (m >= A && m < B && Array.isArray(j.mins[k])) st.put(j.mins[k].map(Number), sym+"|"+FPS.pad(m)); });
            cov = FPS.join(cov, A, B); });
          const lo = Date.now() - FPS.KEEP; st.put(cov.filter(r => r[1] > lo).map(r => [Math.max(r[0], lo), r[1]]), ck); };
        tx.oncomplete = () => { db.close(); res(true); }; tx.onerror = tx.onabort = () => { db.close(); res(false); }; } catch(e){ res(false); } }); },
  async loadSrv(sym, from){   // the store, topped up from the recorder when one is configured (one request per chart open; minutes only, so skipped for sub-minute charts by the caller)
    let o = await FPS.load(sym, from); if (!CFG.fpServer) return o;
    const j = await FPS.pull(CFG.fpServer, sym, from, Date.now()); if (j && j.cov.length && await FPS.adopt(sym, j)) o = await FPS.load(sym, from); return o; },
  async load(sym, from){   // {cov, mins} or null when IndexedDB is not usable
    const db = FPS.off ? null : await FPS.open(); if (!db) return null;
    return new Promise(res => { try { const tx = db.transaction("m", "readonly"), st = tx.objectStore("m"), mins = new Map(); let cov = [];
        st.get("cov|"+sym).onsuccess = e => { cov = e.target.result || []; };
        st.openCursor(IDBKeyRange.bound(sym+"|"+FPS.pad(from), sym+"|"+FPS.pad(9e12))).onsuccess = e => { const c = e.target.result; if (c){ mins.set(+String(c.key).split("|").pop(), c.value); c.continue(); } };
        tx.oncomplete = () => { db.close(); res({cov, mins}); }; tx.onerror = tx.onabort = () => { db.close(); res(null); }; } catch(e){ res(null); } }); },
  async commit(sym, trades, from, to){   // store the prints in (from, to] that no earlier commit (this tab, another tab, another panel) already holds, then mark (from, to] known. true on success
    const db = FPS.off ? null : await FPS.open(); if (!db) return false;
    return new Promise(res => { try { const tx = db.transaction("m", "readwrite"), st = tx.objectStore("m"), ck = "cov|"+sym;
        st.get(ck).onsuccess = e => { const cov = e.target.result || [], keep = trades.filter(x => x[0] > from && x[0] <= to && !FPS.span(cov, x[0])), g = FPS.group(keep), ks = [...g.keys()]; let left = ks.length;
          const fin = () => { const lo = Date.now() - FPS.KEEP; st.put(FPS.join(cov, from, to).filter(r => r[1] > lo).map(r => [Math.max(r[0], lo), r[1]]), ck); st.delete(IDBKeyRange.bound(sym+"|"+FPS.pad(0), sym+"|"+FPS.pad(lo - FPS.MIN))); };
          if (!left) return fin(); ks.forEach(k => { const key = sym+"|"+FPS.pad(k); st.get(key).onsuccess = ev => { st.put(FPS.merge(ev.target.result, g.get(k)), key); if (!--left) fin(); }; }); };
        tx.oncomplete = () => { db.close(); res(true); }; tx.onerror = tx.onabort = () => { db.close(); FPS.off = true; res(false); }; } catch(e){ res(false); } }); }   // a full disk / blocked store switches recording off for this page: the footprint still works from memory
};
/* FPS-END */
const CandleCache = {   // last 300 candles per symbol + timeframe in this browser: a new tab / refresh paints at once, the live request then replaces them (max 16 entries, quota errors ignored)
  key(sym, tf){ return LS+"_cc|"+sym+"|"+tf; },
  get(sym, tf){ try { const o = JSON.parse(localStorage.getItem(this.key(sym, tf)) || "null"); if (!o || !o.r || o.r.length < 20 || Date.now() - o.t > 7*86400000) return null; return o.r.map(a => ({t:a[0], o:a[1], h:a[2], l:a[3], c:a[4], v:a[5]})); } catch(e){ return null; } },
  put(sym, tf, rows){ try { if (!rows || rows.length < 20) return; const k = this.key(sym, tf), idx = JSON.parse(localStorage.getItem(LS+"_cci") || "[]").filter(x => x !== k); idx.push(k);
      while (idx.length > 16){ localStorage.removeItem(idx.shift()); }
      localStorage.setItem(k, JSON.stringify({t:Date.now(), r:rows.slice(-300).map(x => [x.t, x.o, x.h, x.l, x.c, x.v || 0])})); localStorage.setItem(LS+"_cci", JSON.stringify(idx)); } catch(e){} }
};
async function candlesTf(sym, tf, first, want){   // -> candles oldest..newest for any chart timeframe (native, UTC variant, or aggregated); `want` = how many bars the first load should aim for
  const ag = TF_AGG[tf] || (tf === "6H" && /^(HL|Y):/.test(sym) ? ["1H", 6] : null);   // Hyperliquid / Yahoo have no 6h bar (gold, oil, indices, FX, stocks on 6H threw 'timeframe 6Hutc not available'): build it from 1H
  if (!ag){   // native timeframe: task 55, the first load also walks back in history until `want` candles (same loop as the aggregated ones)
    let nat = parseRows(await okx("/market/candles?instId="+encodeURIComponent(sym)+"&bar="+okxBar(tf)+"&limit="+(first ? 300 : 3)));
    if (first === true){ const need = want || 120; let guard = 0; while (nat.length < need && guard++ < 8 && nat.length){ let more; try { more = parseRows(await okx("/market/history-candles?instId="+encodeURIComponent(sym)+"&bar="+okxBar(tf)+"&after="+nat[0].t+"&limit=100")); } catch(e){ break; } if (!more.length) break; nat = more.concat(nat); } }
    return nat;
  }
  const [bb, n] = ag, unit = TFSEC[bb]*1000; let base = parseRows(await okx("/market/candles?instId="+encodeURIComponent(sym)+"&bar="+bb+"&limit="+(first ? 300 : 100)));
  if (first === true){ const need = (want || 120)*n; let guard = 0; while (base.length < need && guard++ < 8){ let more; try { more = parseRows(await okx("/market/history-candles?instId="+encodeURIComponent(sym)+"&bar="+bb+"&after="+base[0].t+"&limit=100")); } catch(e){ break; } if (!more.length) break; base = more.concat(base); } }
  const out = aggBars(base, n, unit); if (out.length) out.shift();   // the oldest bucket is usually incomplete
  return out.map(({n:_n, ...r}) => r);
}
const isRL = e => /rate limit|429/i.test(String(e && e.message || e || ""));   // a rate limit is a pause, not a failure
const hlPoll = tf => { const s = TFSEC[tf] || 60; return s >= 86400 ? 45000 : s >= 14400 ? 30000 : s >= 3600 ? 20000 : s >= 900 ? 10000 : 6000; };   // Hyperliquid candle poll period by timeframe: a daily candle does not need a 6 s poll (weight limit ~1200 / min per IP)
const ageTxt = ms => { const m = Math.round(ms/60000); return m < 90 ? m+Lg(" min", " دقيقة") : m < 2880 ? Math.round(m/60)+Lg(" h", " ساعة") : Math.round(m/1440)+Lg(" days", " يوم"); };
const offTxt = (sym, e) => isRL(e) ? T("busy") : (/^HL:/.test(String(sym || "")) ? T("offlineHL") : T("offline"));   // the text says WHICH venue and whether it is only a pause
const LLC = new Map();   // symbol -> {t, v, p}: shared MTF LLT candles (see llKick)
async function llFetch(sym){
  const c = LLC.get(sym), now = Date.now(); if (c && c.p) return c.p; if (c && c.v && now - c.t < (/^HL:/.test(sym) ? 90000 : 25000)) return c.v;   // Hyperliquid: 6 candle requests per refresh, so refresh every 90 s (the levels only change when a candle closes)
  const bars = {"5M":"5m", "15M":"15m", "1H":"1H", "4H":"4H", "D1":"1Dutc", "W1":"1Wutc"}, rec = {t:now, v:c ? c.v : null, p:null};
  rec.p = (async () => { const o = {}; let hard = 0;
    for (const [k, b] of Object.entries(bars)){
      try { const r = parseRows(await okx("/market/candles?instId="+encodeURIComponent(sym)+"&bar="+b+"&limit=40")), m = r.length; if (m < 18) continue;
        const tr = []; for (let i = 1; i < m; i++) tr.push(Math.max(r[i].h - r[i].l, Math.abs(r[i].h - r[i-1].c), Math.abs(r[i].l - r[i-1].c))); let a = tr.slice(0, 14).reduce((x, y) => x + y, 0)/14; for (let i = 14; i < tr.length; i++) a = (a*13 + tr[i])/14;
        o[k] = {ph:r[m-2].h, pl:r[m-2].l, cl:r[m-1].c, atr:a, mom:(r[m-1].c - r[m-4].c)/3}; } catch(e){ if (isRL(e)) break; if (++hard >= 3) break; }   // a rate limit stops the set (the page-wide pause is already running); keep what came
      await new Promise(r => setTimeout(r, 150)); }
    return Object.keys(o).length >= 3 ? o : null; })();
  LLC.set(sym, rec); let v = null; try { v = await rec.p; } finally { LLC.set(sym, {t:Date.now(), v:v || rec.v, p:null}); } return v; }   // null = this round failed (the cache still holds the last good set)
function setStatus(ok){ const d = document.getElementById("dot"); if (!d) return; d.className = ok ? "ok" : "bad"; d.title = ok ? T("live") : T("offline"); }

