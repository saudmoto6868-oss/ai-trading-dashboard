/* V7 live CFX tools, batch 1 (pure functions, browser + node). Research display only: nothing here is a signal, an order, or evidence of an edge.
   Every definition is also written in tests/test_v7_cfx.py (independent Python) and the two must agree.
   obAll        = order blocks as in v7_live_extra.orderBlocks but ALL of the last 6 (mitigated ones keep the bar `mit` of the first later close beyond the far side, else -1);
                  volPct = 100 * volume(OB candle) / sum(volume from the OB candle to the break bar) - an ESTIMATE from candle volume.
   sweeps       = a bar whose wick passes a liquidity level but whose close is back inside (high > p and close < p for a high; low < p and close > p for a low); first such bar per level,
                  scanning from `from`; a close beyond the level first consumes it (no sweep). Last 8.
   cisd         = change in state of delivery: a run of >= 2 same-colour candles, then within 10 bars the first close beyond the OPEN of the run's first candle (bearish run -> close above = up;
                  bullish run -> close below = down). Line from the run's first candle to the confirming bar at that open price. Last 6.
   cisdHtf      = the same on higher-timeframe bars built from the candles (bucket = floor(time / htfSec), the forming bucket dropped), mapped back to the first candle of each bucket.
   trendLine    = trend up: line through the last two swing lows if the second is higher; trend down: last two swing highs if the second is lower.
   pools        = liquidity pools: swing highs (lows) chained within 0.10 ATR with >= 2 touches that no later bar has taken out (high above the pool top / low below the pool bottom). Last 8.
   fibLevels    = on the last impulse (last swing high vs low, same as OTE): retracements .236 .382 .5 .618 .705 .786 and extension targets 1.272 1.618 beyond the impulse extreme.
   divergences  = regular divergence between consecutive swings on a supplied series (RSI / MACD): bearish = higher swing high with a lower series value; bullish = lower swing low with a
                  higher series value; swings at most `maxGap` bars apart. Last 4.
   trackCandidate = paper tracking of a research trade candidate on the candles after `t0`: pending until price trades back to the entry (long: low <= entry, short: high >= entry), then from the
                  NEXT bar: stop first if both in one bar, else TP1; pending expires after 48 bars, open times out after 96 bars. Measurement only, never an order. */
(function (root) {
  const fin = Number.isFinite;
  function obOf(b, e) {
    let k = e.from, ext = e.dir === 'up' ? Infinity : -Infinity;
    for (let i = e.from; i <= e.i; i++) { if (e.dir === 'up' ? b[i].low < ext : b[i].high > ext) { ext = e.dir === 'up' ? b[i].low : b[i].high; k = i; } }
    for (let i = k; i >= Math.max(0, k - 5); i--) { if (e.dir === 'up' ? b[i].close < b[i].open : b[i].close > b[i].open) return i; }
    return -1;
  }
  function obAll(b, events) {
    const out = [];
    (events || []).forEach(e => {
      const j = obOf(b, e); if (j < 0) return; let mit = -1;
      for (let i = e.i + 1; i < b.length; i++) { if (e.dir === 'up' ? b[i].close < b[j].low : b[i].close > b[j].high) { mit = i; break; } }
      let s = 0; for (let i = j; i <= e.i; i++) s += +b[i].volume || 0;
      out.push({ dir: e.dir, i0: j, hi: b[j].high, lo: b[j].low, mit, type: e.type, volPct: s > 0 ? 100 * (+b[j].volume || 0) / s : null });
    });
    return out.slice(-6);
  }
  function sweeps(b, levels) {
    const out = [];
    (levels || []).forEach(L => {
      for (let i = Math.max(0, L.from); i < b.length; i++) {
        if (L.side === 'high') { if (b[i].high > L.p && b[i].close < L.p) { out.push({ i, kind: L.kind, p: L.p, side: 'high' }); break; } if (b[i].close > L.p) break; }
        else { if (b[i].low < L.p && b[i].close > L.p) { out.push({ i, kind: L.kind, p: L.p, side: 'low' }); break; } if (b[i].close < L.p) break; }
      }
    });
    return out.sort((p, q) => p.i - q.i).slice(-8);
  }
  function cisd(b) {
    const out = [], n = b.length; let i = 0;
    while (i < n) {
      const col = b[i].close < b[i].open ? -1 : b[i].close > b[i].open ? 1 : 0; if (!col) { i++; continue; }
      let j = i; while (j + 1 < n && (b[j + 1].close < b[j + 1].open ? -1 : b[j + 1].close > b[j + 1].open ? 1 : 0) === col) j++;
      if (j - i + 1 >= 2) { const lv = b[i].open; for (let k = j + 1; k <= Math.min(n - 1, j + 10); k++) { if (col < 0 ? b[k].close > lv : b[k].close < lv) { out.push({ dir: col < 0 ? 'up' : 'down', i0: i, i1: k, level: lv }); break; } } }
      i = j + 1;
    }
    return out.slice(-6);
  }
  function aggregate(b, sec) {
    const out = []; let key = null;
    b.forEach((x, i) => { const k = Math.floor(x.time / sec); if (k !== key) { key = k; out.push({ time: k * sec, open: x.open, high: x.high, low: x.low, close: x.close, first: i }); } else { const a = out[out.length - 1]; a.high = Math.max(a.high, x.high); a.low = Math.min(a.low, x.low); a.close = x.close; } });
    return out;
  }
  function cisdHtf(b, htfSec) {
    const ag = aggregate(b, htfSec); ag.pop(); if (ag.length < 4) return [];
    return cisd(ag).map(e => ({ dir: e.dir, i0: ag[e.i0].first, i1: ag[e.i1].first, level: e.level }));
  }
  function trendLine(sw, trend) {
    const a = trend === 'up' ? sw.L : trend === 'down' ? sw.H : null; if (!a || a.length < 2) return null;
    const p = a[a.length - 2], q = a[a.length - 1]; if (trend === 'up' ? !(q.p > p.p) : !(q.p < p.p)) return null;
    return { dir: trend, i1: p.i, p1: p.p, i2: q.i, p2: q.p };
  }
  function pools(b, sw, atr) {
    if (!fin(atr)) return []; const tol = 0.10 * atr, out = [];
    [['high', sw.H], ['low', sw.L]].forEach(([kind, arr]) => {
      const s = arr.slice().sort((x, y) => x.p - y.p); let cur = [];
      const flush = () => { if (cur.length >= 2) {
        const top = Math.max(...cur.map(x => x.p)), bot = Math.min(...cur.map(x => x.p)), last = Math.max(...cur.map(x => x.i)); let swept = false;
        for (let i = last + 1; i < b.length; i++) { if (kind === 'high' ? b[i].high > top : b[i].low < bot) { swept = true; break; } }
        if (!swept) out.push({ kind, p: cur.reduce((u, x) => u + x.p, 0) / cur.length, touches: cur.length, iLast: last, i0: Math.min(...cur.map(x => x.i)) }); } cur = []; };
      s.forEach(x => { if (cur.length && x.p - cur[cur.length - 1].p > tol) flush(); cur.push(x); }); flush();
    });
    return out.sort((x, y) => x.iLast - y.iLast).slice(-8);
  }
  function fibLevels(sw) {
    const h = sw.H[sw.H.length - 1], l = sw.L[sw.L.length - 1]; if (!h || !l) return null; const r = h.p - l.p; if (!(r > 0)) return null;
    const up = h.i > l.i, R = [0.236, 0.382, 0.5, 0.618, 0.705, 0.786], E = [1.272, 1.618];
    return { dir: up ? 'up' : 'down', hi: h.p, lo: l.p, i0: Math.min(h.i, l.i), retr: R.map(k => ({ k, p: up ? h.p - k * r : l.p + k * r })), ext: E.map(k => ({ k, p: up ? h.p + (k - 1) * r : l.p - (k - 1) * r })) };
  }
  function divergences(sw, ser, maxGap) {
    const out = [];
    for (let k = 1; k < sw.H.length; k++) { const a = sw.H[k - 1], c = sw.H[k]; if (c.i - a.i <= maxGap && fin(ser[a.i]) && fin(ser[c.i]) && c.p > a.p && ser[c.i] < ser[a.i]) out.push({ dir: 'bear', i1: a.i, i2: c.i, p1: a.p, p2: c.p }); }
    for (let k = 1; k < sw.L.length; k++) { const a = sw.L[k - 1], c = sw.L[k]; if (c.i - a.i <= maxGap && fin(ser[a.i]) && fin(ser[c.i]) && c.p < a.p && ser[c.i] > ser[a.i]) out.push({ dir: 'bull', i1: a.i, i2: c.i, p1: a.p, p2: c.p }); }
    return out.sort((x, y) => x.i2 - y.i2).slice(-4);
  }
  function trackCandidate(b, c, t0) {
    const long = c.dir === 'up'; let st = 'pending', iFill = -1, iEnd = -1, cnt = 0, oc = 0;
    for (let k = 0; k < b.length; k++) {
      if (b[k].time <= t0) continue; cnt++;
      if (st === 'pending') {
        if (long ? b[k].low <= c.entry : b[k].high >= c.entry) { st = 'open'; iFill = k; oc = 0; continue; }
        if (cnt > 48) { st = 'expired'; iEnd = k; break; } continue;
      }
      oc++;
      if (long ? b[k].low <= c.sl : b[k].high >= c.sl) { st = 'sl'; iEnd = k; break; }
      if (long ? b[k].high >= c.tp1 : b[k].low <= c.tp1) { st = 'tp1'; iEnd = k; break; }
      if (oc > 96) { st = 'timeout'; iEnd = k; break; }
    }
    return { status: st, iFill, iEnd, R: st === 'tp1' ? c.rr1 : st === 'sl' ? -1 : null };
  }
  const api = { obAll, sweeps, cisd, cisdHtf, trendLine, pools, fibLevels, divergences, trackCandidate, aggregate };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.V7CFX = api;
})(typeof window !== 'undefined' ? window : globalThis);
