/* V7 live SMC zones + research trade candidate (pure functions, browser + node). Research display only: nothing here is a recommendation, an order, or evidence of an edge.
   srZones      = confirmed swing highs/lows grouped into zones: prices sorted, a chain whose neighbours are within 0.30 ATR forms one zone; zones with >= 2 touches are kept;
                  support if the zone centre is below the last close else resistance; the `count` zones nearest the last close are returned.
   breakers     = order blocks (same definition as v7_live_extra.orderBlocks, evaluated on every BOS/CHoCH) that were MITIGATED by a close beyond their far side: the zone flips
                  (bull OB broken down -> bearish breaker, bear OB broken up -> bullish breaker) and stays until a later close beyond the new far side. Last 3.
   inverseFvg   = fair value gaps (3-bar gap >= 0.30 ATR, last 80 bars) that a later CLOSE passed through (bull gap: close below its low; bear gap: close above its high); the gap flips
                  (bull gap -> bearish inverse FVG) until a later close beyond the new far side. Last 4.
   tradeCandidate = direction of the last BOS/CHoCH; entry = nearest edge of the nearest unmitigated same-direction order block (or, if none, unfilled same-direction FVG) on the pullback side of
                  the last close; stop = far edge -/+ 0.15 ATR; targets = liquidity levels beyond the entry (prev NY-day high/low, EQH/EQL, confirmed swings) nearest first; TP1 must give R >= 2
                  (platform minimum), otherwise there is NO candidate and the reason is returned. */
(function (root) {
  const fin = Number.isFinite;
  function srZones(b, sw, atr, count) {
    if (!fin(atr) || !b.length) return [];
    const pts = sw.H.concat(sw.L).map(s => s.p).sort((a, c) => a - c), tol = 0.30 * atr, zones = []; let cur = [];
    pts.forEach(p => { if (cur.length && p - cur[cur.length - 1] > tol) { zones.push(cur); cur = []; } cur.push(p); }); if (cur.length) zones.push(cur);
    const last = b[b.length - 1].close;
    return zones.filter(z => z.length >= 2).map(z => { const c = z.reduce((s, x) => s + x, 0) / z.length; return { lo: z[0], hi: z[z.length - 1], mid: c, touches: z.length, kind: c < last ? 'support' : 'resistance' }; })
      .sort((p, q) => Math.abs(p.mid - last) - Math.abs(q.mid - last)).slice(0, count || 6);
  }
  function obOf(b, e) {
    let k = e.from, ext = e.dir === 'up' ? Infinity : -Infinity;
    for (let i = e.from; i <= e.i; i++) { if (e.dir === 'up' ? b[i].low < ext : b[i].high > ext) { ext = e.dir === 'up' ? b[i].low : b[i].high; k = i; } }
    for (let i = k; i >= Math.max(0, k - 5); i--) { if (e.dir === 'up' ? b[i].close < b[i].open : b[i].close > b[i].open) return i; }
    return -1;
  }
  function breakers(b, events) {
    const out = [];
    (events || []).forEach(e => {
      const j = obOf(b, e); if (j < 0) return; let m = -1;
      for (let i = e.i + 1; i < b.length; i++) { if (e.dir === 'up' ? b[i].close < b[j].low : b[i].close > b[j].high) { m = i; break; } }
      if (m < 0) return;
      const dir = e.dir === 'up' ? 'down' : 'up'; let dead = false;
      for (let i = m + 1; i < b.length; i++) { if (dir === 'down' ? b[i].close > b[j].high : b[i].close < b[j].low) { dead = true; break; } }
      if (!dead) out.push({ dir, i0: j, im: m, hi: b[j].high, lo: b[j].low });
    });
    return out.slice(-3);
  }
  function inverseFvg(b, atr) {
    const out = [], n = b.length; if (!fin(atr)) return out; const min = 0.30 * atr;
    for (let i = Math.max(2, n - 80); i < n; i++) {
      let g = null;
      if (b[i].low - b[i - 2].high >= min) g = { dir: 'bull', lo: b[i - 2].high, hi: b[i].low };
      else if (b[i - 2].low - b[i].high >= min) g = { dir: 'bear', lo: b[i].high, hi: b[i - 2].low };
      if (!g) continue;
      let m = -1; for (let j = i + 1; j < n; j++) { if (g.dir === 'bull' ? b[j].close < g.lo : b[j].close > g.hi) { m = j; break; } }
      if (m < 0) continue;
      const dir = g.dir === 'bull' ? 'bear' : 'bull'; let dead = false;
      for (let j = m + 1; j < n; j++) { if (dir === 'bear' ? b[j].close > g.hi : b[j].close < g.lo) { dead = true; break; } }
      if (!dead) out.push({ dir, i0: i - 2, im: m, lo: g.lo, hi: g.hi });
    }
    return out.slice(-4);
  }
  function tradeCandidate(b, atr, events, ob, fvg, levels) {
    if (!fin(atr) || !events || !events.length) return { cand: null, reason: 'no_structure' };
    const e = events[events.length - 1], long = e.dir === 'up', px = b[b.length - 1].close;
    const wantDir = long ? 'up' : 'down';
    let zone = (ob || []).filter(o => o.dir === wantDir && (long ? o.hi <= px : o.lo >= px)).sort((p, q) => Math.abs((long ? p.hi : p.lo) - px) - Math.abs((long ? q.hi : q.lo) - px))[0], src = 'OB';
    if (!zone) { zone = (fvg || []).filter(z => z.dir === (long ? 'bull' : 'bear') && (long ? z.hi <= px : z.lo >= px)).sort((p, q) => Math.abs((long ? p.hi : p.lo) - px) - Math.abs((long ? q.hi : q.lo) - px))[0]; src = 'FVG'; }
    if (!zone) return { cand: null, reason: 'no_zone', dir: wantDir };
    const entry = long ? zone.hi : zone.lo, sl = long ? zone.lo - 0.15 * atr : zone.hi + 0.15 * atr, risk = Math.abs(entry - sl);
    if (!(risk > 0)) return { cand: null, reason: 'no_risk', dir: wantDir };
    const tg = (levels || []).filter(p => fin(p) && (long ? p > entry : p < entry)).sort((p, q) => long ? p - q : q - p);
    const ok = tg.filter(p => Math.abs(p - entry) / risk >= 2);
    if (!ok.length) return { cand: null, reason: 'rr_below_2', dir: wantDir, entry, sl };
    return { cand: { dir: wantDir, src, entry, sl, tp1: ok[0], tp2: ok[1] == null ? null : ok[1], rr1: Math.abs(ok[0] - entry) / risk, rr2: ok[1] == null ? null : Math.abs(ok[1] - entry) / risk, zone: { lo: zone.lo, hi: zone.hi, i0: zone.i0 }, evIdx: e.i }, reason: 'ok', dir: wantDir };
  }
  const api = { srZones, breakers, inverseFvg, tradeCandidate };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.V7SMC = api;
})(typeof window !== 'undefined' ? window : globalThis);
